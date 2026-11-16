"""Experiment B — does better retrieval give better translations? (RAG-MT on held-out EMEA)

  uv run python -m locrag.exp_rag_mt [--per-band 20] [--k 3]

Conditions: zero-shot | fuzzy top-k | semantic top-k | hybrid top-k.
Fuzzy is given its best shot: always k examples, no 75% cut-off (a real CAT tool would hide most).
Also reports raw leverage: chrF of the top-1 retrieved TM target vs the reference (no LLM).
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from sacrebleu.metrics import BLEU, CHRF

from common.llm import MT_MODEL, chat, clean_translation, describe
from locrag.retrievers import FuzzyRetriever, HybridRetriever, SemanticRetriever

ROOT = Path(__file__).resolve().parent.parent
BAND_ORDER = ["95-99", "85-94", "75-84", "50-74", "<50"]
SYSTEM = ("You are a professional English-to-Spanish translator for EU medicinal product information "
          "(SmPC and package leaflets). Follow the terminology and phrasing of the translation memory "
          "examples when they are relevant. Output only the Spanish translation of the final sentence.")


def prompt(src: str, examples) -> str:
    parts = []
    if examples:
        parts.append("Translation memory examples:")
        for h in examples:
            parts.append(f"EN: {h.src}\nES: {h.tgt}")
        parts.append("")
    parts.append(f"Translate:\nEN: {src}\nES:")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-band", type=int, default=20)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()

    d = ROOT / "data" / "tm" / "EMEA"
    tm = [json.loads(l) for l in (d / "tm.jsonl").open(encoding="utf-8")]
    test_all = [json.loads(l) for l in (d / "test.jsonl").open(encoding="utf-8")]
    test = [t for b in BAND_ORDER for t in [x for x in test_all if x["band"] == b][: a.per_band]]

    fuzzy = FuzzyRetriever(tm)
    sem = SemanticRetriever(tm)
    hyb = HybridRetriever(fuzzy, sem)
    qv = sem.encode_queries([t["src"] for t in test])

    jobs = []
    for i, t in enumerate(test):
        f_hits = fuzzy.search(t["src"], k=20)
        s_hits = sem.search_vec(qv[i], k=20)
        ret = {"zero_shot": [], "fuzzy": f_hits[: a.k], "semantic": s_hits[: a.k],
               "fuzzy_cat75": [h for h in f_hits[: a.k] if h.score >= 75],  # what a CAT tool would actually show
               "hybrid": hyb.fuse(f_hits, s_hits, a.k)}
        t["leverage"] = {"fuzzy": f_hits[0].tgt, "semantic": s_hits[0].tgt}
        t["top_fuzzy_score"] = f_hits[0].score
        t["overlap_fuzzy_semantic"] = len({h.idx for h in ret["fuzzy"]} & {h.idx for h in ret["semantic"]})
        for cond, ex in ret.items():
            jobs.append((i, cond, prompt(t["src"], ex)))

    print(describe())
    print(f"{len(test)} segments × 5 conditions = {len(jobs)} LLM calls (cached ones are free)")
    done = [0]

    def run(job):
        i, cond, p = job
        out = clean_translation(chat(p, system=SYSTEM, max_tokens=300, model=MT_MODEL))
        done[0] += 1
        if done[0] % 20 == 0:
            print(f"  {done[0]}/{len(jobs)}", flush=True)
        return i, cond, out

    with ThreadPoolExecutor(a.workers) as ex:
        for i, cond, out in ex.map(run, jobs):
            test[i].setdefault("hyp", {})[cond] = out

    # tiered policy (no extra calls): trust the CAT fuzzy match when it is strong, else semantic retrieval
    for t in test:
        t["hyp"]["tiered"] = t["hyp"]["fuzzy_cat75"] if t["top_fuzzy_score"] >= 85 else t["hyp"]["semantic"]

    chrf, bleu = CHRF(word_order=2), BLEU()
    conds = ["zero_shot", "fuzzy_cat75", "fuzzy", "semantic", "hybrid", "tiered"]

    def corpus_scores(items, key):
        hyps = [key(t) for t in items]
        refs = [[t["tgt"] for t in items]]
        return round(chrf.corpus_score(hyps, refs).score, 1), round(bleu.corpus_score(hyps, refs).score, 1)

    table = {}
    for band in BAND_ORDER + ["ALL"]:
        items = test if band == "ALL" else [t for t in test if t["band"] == band]
        row = {c: corpus_scores(items, lambda t, c=c: t["hyp"][c]) for c in conds}
        row["leverage_fuzzy"] = corpus_scores(items, lambda t: t["leverage"]["fuzzy"])
        row["leverage_semantic"] = corpus_scores(items, lambda t: t["leverage"]["semantic"])
        row["n"] = len(items)
        row["mean_overlap"] = round(float(np.mean([t["overlap_fuzzy_semantic"] for t in items])), 2)
        table[band] = row

    # paired sentence-level wins: semantic vs fuzzy
    s_chrf = lambda h, r: chrf.sentence_score(h, [r]).score
    from math import comb

    def paired(x, y):
        w = {f"{x}>{y}": 0, f"{y}>{x}": 0, "tie": 0}
        for t in test:
            a_, b_ = s_chrf(t["hyp"][x], t["tgt"]), s_chrf(t["hyp"][y], t["tgt"])
            w[f"{x}>{y}" if a_ > b_ + 0.5 else f"{y}>{x}" if b_ > a_ + 0.5 else "tie"] += 1
        k, m = w[f"{x}>{y}"], w[f"{x}>{y}"] + w[f"{y}>{x}"]
        # two-sided exact sign test
        tail = sum(comb(m, i) for i in range(0, min(k, m - k) + 1)) / 2 ** m if m else 1.0
        w["sign_test_p"] = round(min(1.0, 2 * tail), 4)
        return w

    wins = {"semantic_vs_fuzzy_topk": paired("semantic", "fuzzy"),
            "semantic_vs_fuzzy_cat75": paired("semantic", "fuzzy_cat75"),
            "semantic_vs_zero_shot": paired("semantic", "zero_shot"),
            "tiered_vs_fuzzy_cat75": paired("tiered", "fuzzy_cat75")}

    out = ROOT / "results" / "benchmarks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rag_mt_outputs.jsonl").write_text("\n".join(json.dumps(t, ensure_ascii=False) for t in test))
    (out / "rag_mt_summary.json").write_text(json.dumps({"table": table, "paired": wins}, indent=2))

    md = [f"# Experiment B — RAG-MT on held-out EMEA ({len(test)} segments, k={a.k}, MT: {MT_MODEL}, retrieval: {sem.model})", "",
          "chrF++ (BLEU in parentheses). 'leverage' = top-1 TM target used as-is, no LLM.", "",
          "| fuzzy band | n | zero-shot | +fuzzy ≥75% (CAT) | +fuzzy top-k | +semantic | +hybrid (RRF) | tiered (fuzzy≥85 else semantic) | leverage fuzzy | leverage semantic | shared examples |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x: f"{x[0]} ({x[1]})"
    for band, r in table.items():
        md.append(f"| {band} | {r['n']} | {f(r['zero_shot'])} | {f(r['fuzzy_cat75'])} | {f(r['fuzzy'])} | {f(r['semantic'])} | {f(r['hybrid'])} | {f(r['tiered'])} | "
                  f"{f(r['leverage_fuzzy'])} | {f(r['leverage_semantic'])} | {r['mean_overlap']}/{a.k} |")
    md += ["", "Paired sentence-level chrF++ (margin 0.5) with exact sign test:", ""] + [f"- {k}: {v}" for k, v in wins.items()]
    (out / "rag_mt_summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
