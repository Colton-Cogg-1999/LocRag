"""Independent auditor stage (claude-sonnet-5.5; never the translator):

  reuse            per-row classification of every TM unit shown to the translator under B/C/D
  extraction       semantic faithfulness of the structured-context extractor (sample)
  mqm              MQM error spans for single translations (sample; diagnostic, never a preference judgment)

The auditor never receives the held-out reference. For MQM it receives only (source, translation): no
condition, TM context or system identity. Requests run through the async Batch API when configured (≈50%
price) and are cached under the same keys a sync call would use, so batch and sync replays are equivalent.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from locrag.study.config import write_json
from locrag.study.context import contains, parse_json_object
from locrag.study.data import load_tm, read_jsonl
from locrag.study.generate import JsonlStore
from locrag.study.llm import LLMResult, cache_key, request_body
from locrag.study.prompts import (REUSE_LABELS, extraction_audit_messages, mqm_messages, reuse_messages)

REUSABLE = {"full", "partial", "terminology", "style_convention"}


class Auditor:
    def __init__(self, cfg: dict, run_dir: Path, client, log=print):
        self.cfg, self.run_dir, self.client, self.log = cfg, run_dir, client, log
        a = cfg["auditor"]
        self.model, self.max_tokens, self.use_batch = a["model"], a["max_tokens"], a.get("use_batch_api", False)
        self.effort = a.get("reasoning_effort", "minimal")
        # measured sync cost per request on dev-v1 (Sonnet 5.5, minimal reasoning), padded ~10%
        self.est_cost = {"reuse": 0.0070, "extraction_audit": 0.0053, "mqm": 0.0040}
        self.reserve_usd = 1.50

    def _body(self, messages):
        return request_body(messages, model=self.model, temperature=0.0, max_tokens=self.max_tokens,
                            reasoning_effort=self.effort)

    def run(self, task: str, requests: list[tuple[str, list[dict]]], batch: bool | None = None) -> dict[str, LLMResult | str]:
        """requests: [(custom_id, messages)] → custom_id → LLMResult (or error string)."""
        results: dict[str, LLMResult | str] = {}
        todo = []
        for cid, msgs in requests:
            hit = self.client.cache_get(cache_key(self._body(msgs)))
            if hit:
                results[cid] = hit
            else:
                todo.append((cid, msgs))
        self.log(f"{task}: {len(requests)} requests, {len(todo)} uncached")
        if not todo:
            return results
        est = len(todo) * self.est_cost.get(task, 0.008)
        remaining = self.client.credits_remaining()
        if remaining is not None and remaining - est < self.reserve_usd:
            raise RuntimeError(f"{task}: estimated ${est:.2f} would leave ${remaining - est:.2f} of ${remaining:.2f} "
                               f"credit (reserve ${self.reserve_usd:.2f}). Reduce the sample or add credit.")
        self.log(f"{task}: est. ${est:.2f}; balance ${remaining if remaining is not None else float('nan'):.2f}")
        use_batch = self.use_batch if batch is None else batch
        if use_batch and len(todo) >= 20:
            results.update(self._run_batch(task, todo))
        else:
            from concurrent.futures import ThreadPoolExecutor
            def one(item):
                cid, msgs = item
                b = self._body(msgs)
                try:
                    return cid, self.client.complete(b["messages"], model=self.model, temperature=0.0,
                                                     max_tokens=self.max_tokens, reasoning_effort=self.effort)
                except Exception as exc:
                    return cid, f"{type(exc).__name__}: {exc}"[:300]
            with ThreadPoolExecutor(max_workers=6) as ex:
                for cid, res in ex.map(one, todo):
                    results[cid] = res
        return results

    def _run_batch(self, task: str, todo: list[tuple[str, list[dict]]]) -> dict[str, LLMResult | str]:
        state_path = self.run_dir / f"batch_{task}.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        ids = sorted(cid for cid, _ in todo)
        fingerprint = hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]
        by_cid = dict(todo)
        if state.get("fingerprint") != fingerprint or state.get("status") in ("failed", "expired", "cancelled"):
            bid = self.client.batch_submit(self.model, [(cid, self._body(m)) for cid, m in todo])
            state = {"batch_id": bid, "fingerprint": fingerprint, "n": len(todo), "status": "submitted"}
            write_json(state_path, state)
            self.log(f"{task}: submitted batch {bid} ({len(todo)} requests)")
        d = self.client.batch_wait(state["batch_id"], log=self.log)
        state["status"] = d.get("status")
        state["usage"] = d.get("usage")
        write_json(state_path, state)
        out = self.client.batch_results(d, self.model)
        for cid, res in out.items():
            if isinstance(res, LLMResult) and res.text and cid in by_cid:
                self.client.cache_put(cache_key(self._body(by_cid[cid])), res)
        missing = [cid for cid in by_cid if cid not in out]
        for cid in missing:
            out[cid] = "missing from batch results"
        return out

    # ---------------------------------------------------------------- reuse classification
    def reuse(self, rows: list[dict], cands: dict, data_dir: Path, k: int) -> None:
        store = JsonlStore(self.run_dir / "reuse.jsonl", key=("row_id",))
        todo = [r for r in rows if not store.has(r["row_id"])]
        tms: dict = {}
        reqs, meta = [], {}
        for row in todo:
            tm = tms.setdefault((row["corpus"], row["lang"]), load_tm(data_dir, row["corpus"], row["lang"]))
            c = cands[row["src_id"]]
            union: list[int] = []
            for key in ("fuzzy", "semantic", "hybrid"):
                for i in c[key][:k]:
                    if i not in union:
                        union.append(i)
            pairs = [(tm[i]["src"], tm[i]["tgt"]) for i in union]
            domain = self.cfg["corpora"][row["corpus"]]["domain"]
            reqs.append((row["row_id"], reuse_messages(row["src"], row["lang"], domain, pairs)))
            meta[row["row_id"]] = (row, union, pairs)
        results = self.run("reuse", reqs)
        msgs_by_cid = dict(reqs)
        for cid, res in results.items():
            row, union, pairs = meta[cid]
            rec = self._parse_reuse(row, union, pairs, res, cands[row["src_id"]])
            if rec["error"] and rec["error"].startswith("parse") and isinstance(res, LLMResult):
                # one repair attempt: ask for exactly one object per pair
                repair = msgs_by_cid[cid] + [
                    {"role": "assistant", "content": res.text},
                    {"role": "user", "content": f"Reply again with JSON only, containing exactly {len(union)} objects "
                                                f"in \"pairs\", one per historical pair, ids 1..{len(union)}."}]
                try:
                    res2 = self.client.complete(repair, model=self.model, temperature=0.0, max_tokens=self.max_tokens,
                                                reasoning_effort=self.effort)
                    rec2 = self._parse_reuse(row, union, pairs, res2, cands[row["src_id"]])
                    rec2["repaired"] = True
                    a1, a2 = rec["accounting"] or {}, rec2["accounting"] or {}
                    rec2["accounting"] = {**a2, "cost_usd": a1.get("cost_usd", 0) + a2.get("cost_usd", 0)}
                    rec = rec2
                except Exception as exc:
                    rec["error"] += f"; repair failed: {exc}"[:200]
            store.add(rec)

    def _parse_reuse(self, row, union, pairs, res, cand) -> dict:
        rec = {"row_id": row["row_id"], "auditor": self.model, "tm_idx": union, "labels": [], "error": None,
               "accounting": res.accounting() if isinstance(res, LLMResult) else None}
        if not isinstance(res, LLMResult):
            rec["error"] = res
            return rec
        try:
            parsed = parse_json_object(res.text).get("pairs")
            if not isinstance(parsed, list) or len(parsed) != len(union):
                raise ValueError(f"expected {len(union)} pair labels, got {len(parsed) if isinstance(parsed, list) else 'none'}")
            for i, (tm_idx, (hs, ht), p) in enumerate(zip(union, pairs, parsed)):
                label = p.get("label")
                if label not in REUSE_LABELS:
                    raise ValueError(f"invalid label {label!r}")
                ev = [e for e in (p.get("evidence") or []) if isinstance(e, dict)]
                ev_ok = [contains(ht, e.get("target_span", "")) and contains(row["src"], e.get("new_source_span", ""))
                         for e in ev]
                verified = label in REUSABLE and (label == "style_convention" or any(ev_ok))
                rec["labels"].append({"tm_idx": tm_idx, "label": label, "risk": bool(p.get("risk")),
                                      "note": str(p.get("note", ""))[:300], "evidence": ev, "evidence_verbatim": ev_ok,
                                      "verified_reusable": verified,
                                      "fuzzy": cand["candidates"][str(tm_idx)]["fuzzy"],
                                      "cos": cand["candidates"][str(tm_idx)]["cos"]})
        except (ValueError, json.JSONDecodeError, AttributeError) as exc:
            rec["error"] = f"parse: {exc}"[:300]
            rec["raw"] = res.text[:2000]
            rec["labels"] = []
        return rec

    # ---------------------------------------------------------------- extractor faithfulness audit
    def extraction_audit(self, rows: list[dict], data_dir: Path, sample: int, seed: int) -> None:
        store = JsonlStore(self.run_dir / "extraction_audit.jsonl", key=("row_id",))
        ex = {r["row_id"]: r for r in read_jsonl(self.run_dir / "extractions.jsonl")}
        by_id = {r["row_id"]: r for r in rows}
        eligible = sorted(rid for rid, e in ex.items() if rid in by_id and e.get("items"))
        random.Random(seed).shuffle(eligible)
        chosen = [rid for rid in eligible[:sample] if not store.has(rid)]
        tms: dict = {}
        reqs, meta = [], {}
        for rid in chosen:
            row, e = by_id[rid], ex[rid]
            tm = tms.setdefault((row["corpus"], row["lang"]), load_tm(data_dir, row["corpus"], row["lang"]))
            pairs = [(tm[i]["src"], tm[i]["tgt"]) for i in e["candidate_tm_idx"]]
            items = [{k: v for k, v in it.items() if k in ("kind", "pair", "source", "target", "new_source_span", "note")}
                     for it in e["items"]]
            reqs.append((rid, extraction_audit_messages(row["src"], row["lang"], pairs, items)))
            meta[rid] = e["items"]
        for cid, res in self.run("extraction_audit", reqs).items():
            rec = {"row_id": cid, "auditor": self.model, "items": [], "error": None,
                   "accounting": res.accounting() if isinstance(res, LLMResult) else None}
            try:
                if not isinstance(res, LLMResult):
                    raise ValueError(res)
                judged = parse_json_object(res.text).get("items") or []
                for it, j in zip(meta[cid], judged):
                    rec["items"].append({**{k: it.get(k) for k in ("kind", "ok", "reason", "source", "target", "note")},
                                         "mapping_correct": bool(j.get("mapping_correct")),
                                         "applies": bool(j.get("applies")), "audit_note": str(j.get("note", ""))[:300]})
                if len(judged) != len(meta[cid]):
                    rec["error"] = f"judged {len(judged)} of {len(meta[cid])} items"
            except (ValueError, json.JSONDecodeError, AttributeError) as exc:
                rec["error"] = str(exc)[:300]
            store.add(rec)

    # ---------------------------------------------------------------- MQM (single translations, blinded)
    def mqm(self, items: list[dict]) -> None:
        """items: [{"item_id", "src", "hyp", "lang", "domain"}] — item_id is an opaque hash of (src, hyp)."""
        store = JsonlStore(self.run_dir / "mqm.jsonl", key=("item_id",))
        todo = [it for it in items if not store.has(it["item_id"])]
        reqs = [(it["item_id"], mqm_messages(it["src"], it["hyp"], it["lang"], it["domain"])) for it in todo]
        for cid, res in self.run("mqm", reqs).items():
            rec = {"item_id": cid, "auditor": self.model, "errors": [], "error": None,
                   "accounting": res.accounting() if isinstance(res, LLMResult) else None}
            try:
                if not isinstance(res, LLMResult):
                    raise ValueError(res)
                errs = parse_json_object(res.text).get("errors") or []
                rec["errors"] = [{k: str(e.get(k, ""))[:300] for k in ("span", "category", "severity", "note")}
                                 for e in errs if isinstance(e, dict)]
            except (ValueError, json.JSONDecodeError, AttributeError) as exc:
                rec["error"] = str(exc)[:300]
            store.add(rec)
