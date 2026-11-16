"""Experiment A — controlled retrieval probes: fuzzy vs semantic vs hybrid.

  uv run python -m locrag.exp_retrieval

Metrics per probe category (edit / paraphrase / restructure):
  R@1, R@5, MRR@10       is the right TM unit found, and how high?
  surfaced@75            would a CAT tool even SHOW it? (fuzzy score >= 75%, the usual minimum
                         match threshold). Semantic retrieval has no such cliff.
Negation probes: does the retriever's score tell "same meaning" apart from "same words,
opposite meaning"? (AUC of gold-score: paraphrase/restructure vs negation; 0.5 = blind,
< 0.5 = actively prefers the wrong-meaning segment.)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import yaml

from common.embed import EXTRA_RETRIEVAL_MODELS, RETRIEVAL_MODEL
from locrag.retrievers import FuzzyRetriever, HybridRetriever, SemanticRetriever, cat_fuzzy

ROOT = Path(__file__).resolve().parent.parent
CATS = ["edit", "paraphrase", "restructure", "negation"]


def load_tm(corpus="EMEA"):
    return [json.loads(l) for l in (ROOT / "data" / "tm" / corpus / "tm.jsonl").open(encoding="utf-8")]


def auc(pos: list[float], neg: list[float]) -> float:
    """P(score(pos) > score(neg)), ties count half."""
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def main():
    tm = load_tm()
    id2idx = {r["id"]: i for i, r in enumerate(tm)}
    probes = yaml.safe_load((ROOT / "locrag" / "probes_emea.yaml").read_text(encoding="utf-8"))

    fuzzy = FuzzyRetriever(tm)
    sems = []
    for m in [RETRIEVAL_MODEL, *EXTRA_RETRIEVAL_MODELS]:
        pre = "query: " if "e5" in m.lower() and not m.startswith("openrouter:") else ""  # local e5 needs prefixes
        print(f"embedding TM with {m} ...", flush=True)
        sems.append(SemanticRetriever(tm, m, query_prefix=pre, doc_prefix=pre))
    retrievers = {"fuzzy": fuzzy, **{s.name: s for s in sems},
                  f"hybrid({sems[0].name.split(':')[-1]})": HybridRetriever(fuzzy, sems[0])}

    # gold = the original unit + its near-duplicates in the TM (>= 90% fuzzy to the original)
    gold = {}
    for p in probes:
        oi = id2idx[p["tm"]]
        dup = {h.idx for h in fuzzy.search(tm[oi]["src"], k=30) if h.score >= 90}
        gold[p["tm"]] = dup | {oi}

    queries = [(p["tm"], c, p[c]) for p in probes for c in CATS]
    # batch-encode queries per semantic model, then search
    qvecs = {s.name: s.encode_queries([q for _, _, q in queries]) for s in sems}

    rows = []
    for qi, (tid, cat, q) in enumerate(queries):
        g = gold[tid]
        oi = id2idx[tid]
        for name, r in retrievers.items():
            if isinstance(r, SemanticRetriever):
                hits = r.search_vec(qvecs[r.name][qi], k=10)
            elif isinstance(r, HybridRetriever):
                f_hits = fuzzy.search(q, k=20)
                s_hits = sems[0].search_vec(qvecs[sems[0].name][qi], k=20)
                hits = r.fuse(f_hits, s_hits, k=10)
            else:
                hits = r.search(q, k=10)
            rank = next((k + 1 for k, h in enumerate(hits) if h.idx in g), None)
            # retriever's own score for the ORIGINAL unit (for the negation analysis)
            if isinstance(r, SemanticRetriever):
                gold_score = float(r.mat[oi] @ qvecs[r.name][qi]) * 100
            else:
                gold_score = cat_fuzzy(q, tm[oi]["src"])
            rows.append({"tm": tid, "cat": cat, "retriever": name, "rank": rank,
                         "gold_score": round(gold_score, 1),
                         "fuzzy_to_gold": round(cat_fuzzy(q, tm[oi]["src"]), 1),
                         "top1": hits[0].src if hits else None})

    # ---- aggregate
    names = list(retrievers)
    summary = {}
    for name in names:
        summary[name] = {}
        for cat in CATS[:3]:
            rr = [r for r in rows if r["retriever"] == name and r["cat"] == cat]
            ranks = [r["rank"] for r in rr]
            summary[name][cat] = {
                "R@1": np.mean([x == 1 for x in ranks]).round(3),
                "R@5": np.mean([x is not None and x <= 5 for x in ranks]).round(3),
                "MRR@10": np.mean([1 / x if x else 0 for x in ranks]).round(3),
            }
        pos = [r["gold_score"] for r in rows if r["retriever"] == name and r["cat"] in ("paraphrase", "restructure")]
        neg = [r["gold_score"] for r in rows if r["retriever"] == name and r["cat"] == "negation"]
        summary[name]["meaning_AUC"] = round(auc(pos, neg), 3)
        summary[name]["mean_score"] = {c: round(float(np.mean([r["gold_score"] for r in rows
                                                               if r["retriever"] == name and r["cat"] == c])), 1)
                                       for c in CATS}

    # CAT visibility: fraction of probes whose gold has fuzzy >= 75 (a CAT tool would show it at all)
    surfaced = {c: round(float(np.mean([r["fuzzy_to_gold"] >= 75 for r in rows
                                        if r["retriever"] == "fuzzy" and r["cat"] == c])), 3) for c in CATS}

    out = ROOT / "results" / "benchmarks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "probes_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    res = {"n_items": len(probes), "summary": summary, "cat_surfaced_at_75": surfaced}
    (out / "probes_summary.json").write_text(json.dumps(res, indent=2, default=float))

    md = ["# Experiment A: retrieval probes (EMEA TM, 20k units, 40 items × 4 variants)", "",
          "| retriever | edit R@1 | paraphrase R@1 | paraphrase R@5 | restructure R@1 | restructure R@5 | meaning AUC |",
          "|---|---|---|---|---|---|---|"]
    for n in names:
        s = summary[n]
        md.append(f"| {n} | {s['edit']['R@1']:.2f} | {s['paraphrase']['R@1']:.2f} | {s['paraphrase']['R@5']:.2f} | "
                  f"{s['restructure']['R@1']:.2f} | {s['restructure']['R@5']:.2f} | {s['meaning_AUC']:.2f} |")
    md += ["", "Fraction of probes where the correct TM unit scores ≥75% fuzzy (i.e. a CAT tool would display it at all):",
           "", "| edit | paraphrase | restructure | negation |", "|---|---|---|---|",
           f"| {surfaced['edit']:.2f} | {surfaced['paraphrase']:.2f} | {surfaced['restructure']:.2f} | {surfaced['negation']:.2f} |",
           "", "Mean retriever score of the original unit, by probe type:", ""]
    for n in names:
        md.append(f"- **{n}**: {summary[n]['mean_score']}")
    (out / "probes_summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
