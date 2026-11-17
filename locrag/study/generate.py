"""Generation stage: LLM conditions (A–E, A′), DeepL NMT control (N) and TM-as-is leverage (T).

Resumable: outputs are appended to JSONL keyed by (row_id, condition); completed keys are skipped on rerun.
Identical prompts (e.g. structured_ctx with an empty extraction == zero_shot) execute ONCE and are shared,
so equivalent conditions can never differ because of concurrent independent generations.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from common.llm import clean_translation
from locrag.study.config import text_sha
from locrag.study.context import extract
from locrag.study.data import load_tm, read_jsonl
from locrag.study.prompts import (TEMPLATE_VERSION, draft_context_block, raw_context_block, translation_messages)
from locrag.study.retrieval import condition_candidates

LLM_CONDITIONS = ("zero_shot", "fuzzy_ctx", "semantic_ctx", "hybrid_ctx", "structured_ctx", "draft_ctx")
_QUOTES = {('"', '"'), ("“", "”"), ("«", "»"), ("„", "“"), ("「", "」"), ("'", "'")}
_LABEL = re.compile(r"^\s*(Translation|Traducción|Übersetzung|译文|翻译|Spanish|German|Simplified Chinese|"
                    r"Español|Deutsch|中文|简体中文)\s*[:：]\s*", re.IGNORECASE)


class JsonlStore:
    """Append-only JSONL with a (row_id, condition) key; thread-safe."""

    def __init__(self, path: Path, key=("row_id", "condition")):
        self.path, self.key = path, key
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.done = {tuple(r[k] for k in key) for r in read_jsonl(path)}

    def has(self, *key) -> bool:
        return tuple(key) in self.done

    def add(self, rec: dict) -> None:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)
            self.done.add(tuple(rec[k] for k in self.key))


def clean_output(text: str, src: str) -> str:
    out = clean_translation(text)
    out = _LABEL.sub("", out).strip()
    if len(out) >= 2 and (out[0], out[-1]) in _QUOTES and not (src.strip()[:1] in "\"'“«"):
        out = out[1:-1].strip()
    return out


def messages_sha(messages: list[dict]) -> str:
    return hashlib.sha256(json.dumps(messages, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]


def noise_subset(rows: list[dict], n: int, seed: int) -> set[str]:
    """Deterministic band-stratified subset of row_ids (hash order within each corpus/band stratum)."""
    if n >= len(rows):
        return {r["row_id"] for r in rows}
    strata: dict[tuple, list[dict]] = {}
    for r in rows:
        strata.setdefault((r["corpus"], r["band"]), []).append(r)
    order = {k: sorted(v, key=lambda r: hashlib.sha256(f"{seed}:{r['row_id']}".encode()).hexdigest())
             for k, v in strata.items()}
    picked, i = [], 0
    while len(picked) < n:
        for k in sorted(order):
            if i < len(order[k]) and len(picked) < n:
                picked.append(order[k][i]["row_id"])
        i += 1
    return set(picked)


class Generator:
    def __init__(self, cfg: dict, data_dir: Path, run_dir: Path, client, candidates: dict, log=print):
        self.cfg, self.data_dir, self.run_dir, self.client, self.cands, self.log = cfg, data_dir, run_dir, client, candidates, log
        self.k = cfg["retrieval"]["k"]
        self._tms: dict[tuple, list[dict]] = {}
        self.extractions = JsonlStore(run_dir / "extractions.jsonl", key=("row_id",))
        self.outputs = JsonlStore(run_dir / "translations.jsonl")
        self.prompts = JsonlStore(run_dir / "prompts.jsonl", key=("messages_sha",))

    def tm(self, corpus: str, lang: str) -> list[dict]:
        if (corpus, lang) not in self._tms:
            self._tms[(corpus, lang)] = load_tm(self.data_dir, corpus, lang)
        return self._tms[(corpus, lang)]

    def pairs(self, row: dict, condition: str) -> tuple[list[int], list[tuple[str, str]]]:
        idx = condition_candidates(self.cands[row["src_id"]], condition, self.k)
        tm = self.tm(row["corpus"], row["lang"])
        return idx, [(tm[i]["src"], tm[i]["tgt"]) for i in idx]

    def domain(self, row: dict) -> str:
        return self.cfg["corpora"][row["corpus"]]["domain"]

    # ------------------------------------------------------------ extraction (condition E, step 1)
    def run_extractions(self, rows: list[dict], workers: int) -> None:
        todo = [r for r in rows if not self.extractions.has(r["row_id"])]
        self.log(f"extractor: {len(todo)} to run ({len(rows) - len(todo)} done)")

        def one(row):
            idx, pairs = self.pairs(row, "structured_ctx")
            try:
                ex = extract(self.client, self.cfg, row["src"], row["lang"], pairs)
            except Exception as exc:  # provider failure: record, keep going
                ex = {"error": f"{type(exc).__name__}: {exc}"[:300], "context_block": None, "calls": []}
            self.extractions.add({"row_id": row["row_id"], "candidate_tm_idx": idx, **ex})

        self._pool(todo, one, workers, "extract")

    # ------------------------------------------------------------ LLM translation
    def _context(self, row: dict, condition: str, extractions: dict) -> tuple[list[int], str, str | None]:
        """(candidate idx, context_block, error) for a condition."""
        if condition in ("zero_shot", "zero_shot_repeat"):
            return [], "", None
        if condition == "structured_ctx":
            ex = extractions.get(row["row_id"])
            if ex is None or ex.get("context_block") is None:
                return ex.get("candidate_tm_idx", []) if ex else [], "", "extraction missing or failed"
            return ex["candidate_tm_idx"], ex["context_block"], None
        idx, pairs = self.pairs(row, condition)
        if condition == "draft_ctx":
            return idx, draft_context_block(pairs, row["lang"]), None
        return idx, raw_context_block(pairs, row["lang"]), None

    def run_translations(self, rows: list[dict], conditions: list[str], noise_ids: set[str], workers: int) -> None:
        tcfg = self.cfg["translation"]
        extractions = {r["row_id"]: r for r in read_jsonl(self.run_dir / "extractions.jsonl")}
        jobs: dict[tuple, dict] = {}  # (messages_sha, replicate) → job with all (row, condition) users
        for row in rows:
            conds = list(conditions) + (["zero_shot_repeat"] if row["row_id"] in noise_ids else [])
            for cond in conds:
                if self.outputs.has(row["row_id"], cond):
                    continue
                idx, block, err = self._context(row, cond, extractions)
                if err:
                    self.outputs.add(self._record(row, cond, idx, block, None, None, error=err))
                    continue
                msgs = translation_messages(row["src"], row["lang"], self.domain(row), block)
                replicate = 1 if cond == "zero_shot_repeat" else 0
                key = (messages_sha(msgs), replicate)
                jobs.setdefault(key, {"messages": msgs, "replicate": replicate, "users": []})["users"].append(
                    (row, cond, idx, block))
        self.log(f"translation: {len(jobs)} unique prompts for "
                 f"{sum(len(j['users']) for j in jobs.values())} (row, condition) outputs")

        def one(item):
            (sha, replicate), job = item
            if not self.prompts.has(sha):
                self.prompts.add({"messages_sha": sha, "messages": job["messages"]})
            try:
                res = self.client.complete(job["messages"], model=tcfg["model"], temperature=tcfg["temperature"],
                                           max_tokens=tcfg["max_tokens"], seed=tcfg.get("seed"),
                                           reasoning_effort=tcfg.get("reasoning_effort"),
                                           provider=tcfg.get("provider"), replicate=replicate)
                err = None
            except Exception as exc:
                res, err = None, f"{type(exc).__name__}: {exc}"[:300]
            for n, (row, cond, idx, block) in enumerate(job["users"]):
                self.outputs.add(self._record(row, cond, idx, block, sha, res, error=err, shared=n > 0))

        self._pool(list(jobs.items()), one, workers, "translate")

    def _record(self, row, cond, idx, block, sha, res, error=None, shared=False) -> dict:
        tcfg = self.cfg["translation"]
        rec = {"row_id": row["row_id"], "src_id": row["src_id"], "corpus": row["corpus"], "lang": row["lang"],
               "band": row["band"], "split": row["split"], "condition": cond, "system": "llm",
               "candidate_tm_idx": idx, "context_block": block, "context_chars": len(block or ""),
               "template_version": TEMPLATE_VERSION, "messages_sha": sha,
               "model": tcfg["model"], "params": {k: tcfg.get(k) for k in ("temperature", "max_tokens", "seed",
                                                                          "reasoning_effort", "provider")},
               "translation": None, "raw_output": None, "accounting": None, "shared_generation": shared,
               "error": error}
        if res is not None:
            rec["raw_output"] = res.text
            rec["translation"] = clean_output(res.text, row["src"]) or None
            acc = res.accounting()
            if shared:  # the generation is attributed once; shared users carry zero marginal cost
                acc = {**acc, "cost_usd": 0.0, "shared": True}
            rec["accounting"] = acc
            if res.finish_reason == "length":
                rec["error"] = "truncated (finish_reason=length)"
            if not rec["translation"]:
                rec["error"] = rec["error"] or "empty translation after cleaning"
        return rec

    # ------------------------------------------------------------ non-LLM systems
    def run_tm_as_is(self, rows: list[dict]) -> None:
        for row in rows:
            if self.outputs.has(row["row_id"], "tm_as_is"):
                continue
            c = self.cands[row["src_id"]]
            top = c["fuzzy"][0]
            tgt = self.tm(row["corpus"], row["lang"])[top]["tgt"]
            self.outputs.add({"row_id": row["row_id"], "src_id": row["src_id"], "corpus": row["corpus"],
                              "lang": row["lang"], "band": row["band"], "split": row["split"],
                              "condition": "tm_as_is", "system": "tm", "candidate_tm_idx": [top],
                              "tm_fuzzy": c["candidates"][str(top)]["fuzzy"], "translation": tgt,
                              "context_block": "", "context_chars": 0, "accounting": {"cost_usd": 0.0}, "error": None})

    def run_nmt(self, rows: list[dict], deepl) -> None:
        targets = self.cfg["nmt"]["targets"]
        for lang in sorted({r["lang"] for r in rows}):
            todo = [r for r in rows if r["lang"] == lang and not self.outputs.has(r["row_id"], "nmt_deepl")]
            if not todo:
                continue
            self.log(f"DeepL {lang}: {len(todo)} segments, {sum(len(r['src']) for r in todo):,} chars")
            try:
                outs = deepl.translate([r["src"] for r in todo], targets[lang])
            except Exception as exc:
                self.log(f"DeepL failed for {lang}: {exc}")
                raise
            for row, o in zip(todo, outs):
                self.outputs.add({"row_id": row["row_id"], "src_id": row["src_id"], "corpus": row["corpus"],
                                  "lang": row["lang"], "band": row["band"], "split": row["split"],
                                  "condition": "nmt_deepl", "system": "nmt", "candidate_tm_idx": [],
                                  "translation": o["text"], "context_block": "", "context_chars": 0,
                                  "model": f"deepl:{o.get('model_type_used')}",
                                  "accounting": {"cost_usd": 0.0, "chars_billed": 0 if o["cached"] else o["chars_billed"],
                                                 "latency_s": o["latency_s"], "cached": o["cached"]},
                                  "error": None})

    # ------------------------------------------------------------
    def _pool(self, items, fn, workers, label):
        if not items:
            return
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(fn, it) for it in items]
            for f in as_completed(futures):
                f.result()
                done += 1
                if done % 50 == 0 or done == len(items):
                    self.log(f"  {label}: {done}/{len(items)}")


def latest_outputs(path: Path) -> dict[tuple, dict]:
    """Last record per (row_id, condition)."""
    out = {}
    for r in read_jsonl(path):
        out[(r["row_id"], r["condition"])] = r
    return out


__all__ = ["Generator", "JsonlStore", "LLM_CONDITIONS", "clean_output", "latest_outputs", "noise_subset", "text_sha"]
