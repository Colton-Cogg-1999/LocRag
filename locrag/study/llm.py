"""OpenRouter chat client for the study: usage/cost/provider logging, retries, full-record cache, Batch API.

Every call returns an `LLMResult` that records what was actually served (provider, model snapshot), token
usage, provider-reported cost and latency. The cache stores the full record, so cached replays keep their
original accounting (`cached=True` marks the replay; cost is not charged twice in run accounting).

`replicate` is part of the cache key: replicate=1 requests an independent second generation of an identical
prompt (used to measure the provider/generation noise floor).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import httpx

from common import env  # noqa: F401  (loads .env)
from locrag.study.config import ROOT

BASE_URL = os.environ.get("L10N_STUDY_BASE_URL", "https://openrouter.ai/api/v1")
CACHE_PATH = ROOT / ".cache" / "study_llm.sqlite"
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    model_requested: str
    model_served: str = ""
    provider: str = ""
    finish_reason: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0
    generation_id: str = ""
    attempts: int = 1
    cached: bool = False
    via_batch: bool = False
    raw_usage: dict = field(default_factory=dict)

    def accounting(self) -> dict:
        d = asdict(self)
        d.pop("text")
        d.pop("raw_usage")
        return d


def request_body(messages: list[dict], *, model: str, temperature: float = 0.0, max_tokens: int = 512,
                 seed: int | None = None, reasoning_effort: str | None = None, provider: dict | None = None,
                 response_format: dict | None = None) -> dict:
    body: dict = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    if seed is not None:
        body["seed"] = seed
    if reasoning_effort:
        body["reasoning"] = {"effort": reasoning_effort}
    if provider:
        body["provider"] = provider
    if response_format:
        body["response_format"] = response_format
    return body


def cache_key(body: dict, replicate: int = 0) -> str:
    return hashlib.sha256(json.dumps([BASE_URL, body, replicate], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def parse_completion(d: dict, model: str, latency: float = 0.0, attempts: int = 1) -> LLMResult:
    if not d.get("choices"):
        raise LLMError(f"No choices in response: {str(d)[:300]}")
    choice = d["choices"][0]
    text = (choice.get("message") or {}).get("content") or ""
    u = d.get("usage") or {}
    meta = d.get("openrouter_metadata") or {}
    served = d.get("model") or ""
    for ep in (meta.get("endpoints") or {}).get("available") or []:
        if ep.get("selected"):
            served = ep.get("model") or served
    return LLMResult(
        text=text.strip(), model_requested=model, model_served=served, provider=d.get("provider") or "",
        finish_reason=choice.get("finish_reason") or "", prompt_tokens=int(u.get("prompt_tokens") or 0),
        completion_tokens=int(u.get("completion_tokens") or 0),
        reasoning_tokens=int((u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0),
        cached_tokens=int((u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0),
        cost_usd=float(u.get("cost") or 0.0), latency_s=round(latency, 3), generation_id=d.get("id") or "",
        attempts=attempts, raw_usage=u)


class Client:
    def __init__(self, cache_path: Path = CACHE_PATH, api_key: str | None = None, max_attempts: int = 8):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
        self.cache_path = cache_path
        self.max_attempts = max_attempts
        self._lock = threading.Lock()
        self._db: sqlite3.Connection | None = None
        self._http: httpx.Client | None = None

    # ---------------------------------------------------------------- cache
    def _conn(self) -> sqlite3.Connection:
        if self._db is None:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self.cache_path, check_same_thread=False)
            self._db.execute("CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT, created REAL)")
        return self._db

    def cache_get(self, key: str) -> LLMResult | None:
        with self._lock:
            row = self._conn().execute("SELECT v FROM cache WHERE k=?", (key,)).fetchone()
        if not row:
            return None
        res = LLMResult(**json.loads(row[0]))
        res.cached = True
        return res

    def cache_put(self, key: str, res: LLMResult) -> None:
        rec = asdict(res)
        rec["cached"] = False
        with self._lock:
            self._conn().execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
                                 (key, json.dumps(rec, ensure_ascii=False), time.time()))
            self._conn().commit()

    # ---------------------------------------------------------------- http
    def _client(self) -> httpx.Client:
        if self._http is None:
            if not self.api_key:
                raise LLMError("OPENROUTER_API_KEY is not set")
            self._http = httpx.Client(base_url=BASE_URL, timeout=httpx.Timeout(180.0, connect=20.0),
                                      headers={"Authorization": f"Bearer {self.api_key}",
                                               "X-OpenRouter-Metadata": "enabled",
                                               "X-Title": "locrag-study"})
        return self._http

    def _post_with_retry(self, path: str, payload: dict) -> tuple[dict, int, float]:
        last = ""
        for attempt in range(1, self.max_attempts + 1):
            started = time.perf_counter()
            try:
                r = self._client().post(path, json=payload)
                elapsed = time.perf_counter() - started
                if r.status_code in RETRY_STATUS:
                    last = f"HTTP {r.status_code}: {r.text[:200]}"
                elif r.status_code >= 400:
                    raise LLMError(f"HTTP {r.status_code}: {r.text[:500]}")
                else:
                    d = r.json()
                    if isinstance(d, dict) and d.get("error"):
                        code = (d["error"] or {}).get("code")
                        last = f"provider error {code}: {str(d['error'])[:200]}"
                        if code not in RETRY_STATUS and code is not None and int(code) < 500:
                            raise LLMError(last)
                    else:
                        return d, attempt, elapsed
            except (httpx.TransportError, json.JSONDecodeError) as exc:
                last = f"{type(exc).__name__}: {exc}"
            time.sleep(min(60.0, 2 ** attempt) * (0.5 + random.random()))
        raise LLMError(f"Gave up after {self.max_attempts} attempts: {last}")

    def complete(self, messages: list[dict], *, model: str, temperature: float = 0.0, max_tokens: int = 512,
                 seed: int | None = None, reasoning_effort: str | None = None, provider: dict | None = None,
                 response_format: dict | None = None, replicate: int = 0, use_cache: bool = True,
                 require_text: bool = True) -> LLMResult:
        body = request_body(messages, model=model, temperature=temperature, max_tokens=max_tokens, seed=seed,
                            reasoning_effort=reasoning_effort, provider=provider, response_format=response_format)
        key = cache_key(body, replicate)
        if use_cache and (hit := self.cache_get(key)):
            return hit
        res = None
        for empty_try in range(3):
            d, attempts, elapsed = self._post_with_retry("/chat/completions", body)
            res = parse_completion(d, model, elapsed, attempts)
            if res.text or not require_text:
                break
            time.sleep(2 * (empty_try + 1))
        if require_text and not res.text:
            raise LLMError(f"Empty completion (finish_reason={res.finish_reason})")
        if use_cache:
            self.cache_put(key, res)
        return res

    def credits_remaining(self) -> float | None:
        """Account balance in USD from OpenRouter (None if unavailable)."""
        try:
            r = self._client().get("/credits")
            d = r.json().get("data") or {}
            return float(d["total_credits"]) - float(d["total_usage"])
        except Exception:
            return None

    # ---------------------------------------------------------------- Batch API (async, ~50% price)
    def batch_submit(self, model: str, requests: list[tuple[str, dict]], provider: dict | None = None) -> str:
        """requests: [(custom_id, body)] where body has no "model". Returns the batch id."""
        payload: dict = {"endpoint": "/v1/chat/completions", "model": model}
        if provider:
            payload["provider"] = provider
        payload["completion_window"] = "24h"
        payload["requests"] = [{"custom_id": cid, "body": {k: v for k, v in b.items() if k != "model"}}
                               for cid, b in requests]  # key order matters: requests last
        d, _, _ = self._post_with_retry("/batches", payload)
        if not d.get("id"):
            raise LLMError(f"Batch submit returned no id: {str(d)[:300]}")
        return d["id"]

    def batch_get(self, batch_id: str) -> dict:
        r = self._client().get(f"/batches/{batch_id}")
        if r.status_code >= 400:
            raise LLMError(f"Batch status HTTP {r.status_code}: {r.text[:300]}")
        return r.json()

    def batch_wait(self, batch_id: str, poll_s: float = 30.0, timeout_s: float = 26 * 3600, log=print) -> dict:
        started = time.time()
        while True:
            d = self.batch_get(batch_id)
            status = d.get("status")
            if status in ("completed", "failed", "expired", "cancelled"):
                return d
            if time.time() - started > timeout_s:
                raise LLMError(f"Batch {batch_id} still {status} after {timeout_s}s")
            log(f"  batch {batch_id}: {status} {d.get('request_counts') or ''}")
            time.sleep(poll_s)

    @staticmethod
    def batch_results(d: dict, model: str) -> dict[str, LLMResult | str]:
        """custom_id → LLMResult, or an error string."""
        out: dict[str, LLMResult | str] = {}
        for item in d.get("results") or []:
            cid = item.get("custom_id")
            resp = item.get("response") or {}
            body = resp.get("body") if isinstance(resp, dict) else None
            if body and body.get("choices"):
                res = parse_completion(body, model)
                res.via_batch = True
                out[cid] = res
            else:
                out[cid] = json.dumps(item.get("error") or resp or item)[:500]
        return out
