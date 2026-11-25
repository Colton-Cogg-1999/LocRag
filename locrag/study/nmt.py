"""DeepL API client: the production-NMT control. Context-free by design (no glossary, no TM).

Uses `model_type=latency_optimized` (DeepL's classic NMT models) so the control stays a conventional NMT
system rather than DeepL's newer LLM-based model; the model type DeepL reports is logged per call.
Responses are cached in SQLite so re-runs do not consume the 500k-character free quota again.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import threading
import time
from pathlib import Path

import httpx

from common import env  # noqa: F401
from locrag.study.config import ROOT

CACHE_PATH = ROOT / ".cache" / "study_deepl.sqlite"


class DeepLError(RuntimeError):
    pass


class DeepL:
    def __init__(self, api_key: str | None = None, model_type: str = "latency_optimized",
                 cache_path: Path = CACHE_PATH):
        self.api_key = (api_key or os.environ.get("DEEPL_API_KEY", "")).strip()
        self.model_type = model_type
        self.base = "https://api-free.deepl.com/v2" if self.api_key.endswith(":fx") else "https://api.deepl.com/v2"
        self._db = None
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(cache_path, check_same_thread=False)
            self._db.execute("CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT)")
        self._lock = threading.Lock()

    def _key(self, text: str, target: str) -> str:
        return hashlib.sha256(json.dumps([text, target, self.model_type]).encode()).hexdigest()

    def _headers(self) -> dict:
        if not self.api_key:
            raise DeepLError("DEEPL_API_KEY is not set in .env")
        return {"Authorization": f"DeepL-Auth-Key {self.api_key}"}

    def usage(self) -> dict:
        r = httpx.get(f"{self.base}/usage", headers=self._headers(), timeout=30)
        r.raise_for_status()
        return r.json()

    def translate(self, texts: list[str], target: str, batch: int = 40) -> list[dict]:
        """Returns [{"text", "cached", "chars_billed", "latency_s", "model_type_used"}] in input order."""
        out: list[dict | None] = [None] * len(texts)
        todo = []
        for i, t in enumerate(texts):
            row = None
            if self._db is not None:
                with self._lock:
                    row = self._db.execute("SELECT v FROM cache WHERE k=?", (self._key(t, target),)).fetchone()
            if row:
                out[i] = {**json.loads(row[0]), "cached": True}
            else:
                todo.append(i)
        for start in range(0, len(todo), batch):
            idx = todo[start:start + batch]
            payload = {"text": [texts[i] for i in idx], "source_lang": "EN", "target_lang": target,
                       "model_type": self.model_type}
            res, elapsed = self._post(payload)
            trs = res.get("translations") or []
            if len(trs) != len(idx):
                raise DeepLError("DeepL returned a different number of translations")
            for i, tr in zip(idx, trs):
                rec = {"text": tr["text"], "chars_billed": len(texts[i]), "latency_s": round(elapsed / len(idx), 3),
                       "model_type_used": tr.get("model_type_used") or res.get("model_type_used") or self.model_type}
                out[i] = {**rec, "cached": False}
                if self._db is not None:
                    with self._lock:
                        self._db.execute("INSERT OR REPLACE INTO cache VALUES (?, ?)",
                                         (self._key(texts[i], target), json.dumps(rec, ensure_ascii=False)))
                        self._db.commit()
        return out  # type: ignore[return-value]

    def _post(self, payload: dict) -> tuple[dict, float]:
        last = ""
        for attempt in range(1, 8):
            started = time.perf_counter()
            try:
                r = httpx.post(f"{self.base}/translate", headers=self._headers(), json=payload, timeout=60)
                if r.status_code in (429, 500, 502, 503, 504, 529):
                    last = f"HTTP {r.status_code}"
                elif r.status_code == 456:
                    raise DeepLError("DeepL quota exceeded (HTTP 456)")
                elif r.status_code >= 400:
                    raise DeepLError(f"HTTP {r.status_code}: {r.text[:300]}")
                else:
                    return r.json(), time.perf_counter() - started
            except httpx.TransportError as exc:
                last = str(exc)
            time.sleep(min(60, 2 ** attempt) * (0.5 + random.random()))
        raise DeepLError(f"Gave up: {last}")
