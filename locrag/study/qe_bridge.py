"""Blinded hand-off to the isolated QE environment (qe/).

Each unique (source, hypothesis) pair becomes one item with an opaque id = sha256(src ⟂ hyp). Items are
shuffled with a fixed seed and written with ONLY {id, src, mt} (+ ref for reference-based metrics), so the
scorer cannot see the condition, retrieved TM, prompt, translation system or row identity. Identical outputs
from different conditions receive identical scores by construction.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
from pathlib import Path

from sacrebleu.metrics import CHRF

from locrag.study.config import ROOT
from locrag.study.data import read_jsonl

QE_PROJECT = ROOT / "qe"
QE_METRICS = ("cometkiwi22", "metricx24_qe")
REF_METRICS = ("comet22",)


def item_id(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:20]


def export_items(outputs: list[dict], sources: dict[str, str], refs: dict[str, dict] | None, path: Path,
                 seed: int) -> int:
    """outputs: generation records with row_id + translation; sources: row_id → src."""
    items = {}
    for o in outputs:
        hyp = o.get("translation")
        if not hyp:
            continue
        src = sources[o["row_id"]]
        if refs is None:
            items[item_id(src, hyp)] = {"id": item_id(src, hyp), "src": src, "mt": hyp}
        else:
            ref = refs[o["row_id"]]["ref"]
            items[item_id(src, hyp, ref)] = {"id": item_id(src, hyp, ref), "src": src, "mt": hyp, "ref": ref}
    rows = sorted(items.values(), key=lambda r: r["id"])
    random.Random(seed).shuffle(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return len(rows)


def run_scorer(metric: str, inp: Path, out: Path, batch_size: int = 16, log=print) -> None:
    cmd = ["uv", "run", "--project", str(QE_PROJECT), "python", "-m", "locrag_qe.score", "--metric", metric,
           "--input", str(inp), "--output", str(out), "--batch-size", str(batch_size)]
    log(" ".join(cmd))
    env = {**os.environ, "TOKENIZERS_PARALLELISM": "false"}  # .env (incl. HF_TOKEN) already loaded into os.environ
    subprocess.run(cmd, check=True, env=env, cwd=ROOT)


def load_scores(path: Path) -> dict[str, float]:
    return {r["id"]: float(r["score"]) for r in read_jsonl(path)}


def score_run(run_dir: Path, outputs: list[dict], sources: dict[str, str], refs: dict[str, dict],
              metrics: list[str], seed: int, log=print) -> None:
    qdir = run_dir / "qe"
    for metric in metrics:
        if metric == "chrf":
            continue
        uses_ref = metric in REF_METRICS or metric.endswith("_ref")
        inp = qdir / f"in_{'ref' if uses_ref else 'qe'}.jsonl"
        n = export_items(outputs, sources, refs if uses_ref else None, inp, seed)
        log(f"{metric}: {n} unique items")
        run_scorer(metric, inp, qdir / f"{metric}.jsonl", log=log)


def chrf_scores(outputs: list[dict], refs: dict[str, dict]) -> dict[tuple, float]:
    """Sentence chrF (character n-grams only, word_order=0) per (row_id, condition)."""
    m = CHRF(word_order=0)
    return {(o["row_id"], o["condition"]): m.sentence_score(o["translation"], [refs[o["row_id"]]["ref"]]).score
            for o in outputs if o.get("translation")}


def attach_scores(run_dir: Path, outputs: list[dict], sources: dict[str, str], refs: dict[str, dict],
                  metrics: list[str]) -> dict[tuple, dict]:
    """(row_id, condition) → {metric: score}. Missing scores are absent, never imputed."""
    tables = {m: load_scores(run_dir / "qe" / f"{m}.jsonl") for m in metrics if m != "chrf"}
    chrf = chrf_scores(outputs, refs) if "chrf" in metrics else {}
    out = {}
    for o in outputs:
        hyp = o.get("translation")
        if not hyp:
            continue
        src = sources[o["row_id"]]
        rec = {}
        for m, t in tables.items():
            key = item_id(src, hyp, refs[o["row_id"]]["ref"]) if (m in REF_METRICS or m.endswith("_ref")) else item_id(src, hyp)
            if key in t:
                rec[m] = t[key]
        if (o["row_id"], o["condition"]) in chrf:
            rec["chrf"] = chrf[(o["row_id"], o["condition"])]
        out[(o["row_id"], o["condition"])] = rec
    return out
