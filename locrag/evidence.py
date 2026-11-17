"""Rebuild audited evidence from committed outputs. No models, keys or corpus downloads.

    python -m locrag.evidence [--output results/audit]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from math import comb, sqrt
from pathlib import Path

import numpy as np
from sacrebleu.metrics import CHRF

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(wins, losses) + 1)) / 2**n) if n else 1.0


def wilson(successes: int, n: int) -> list[float]:
    if not n:
        return [0.0, 1.0]
    z = 1.959963984540054
    p = successes / n
    center = (p + z*z / (2*n)) / (1 + z*z/n)
    radius = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return [round(center-radius, 4), round(center+radius, 4)]


def paired_mean_ci(deltas: list[float], seed: int = 2026, samples: int = 2000) -> dict:
    """Exploratory percentile bootstrap over segments, not documents or corpus chrF."""
    values = np.asarray(deltas, dtype=float)
    if not len(values):
        return {"mean": None, "ci95": None, "n": 0}
    rng = np.random.default_rng(seed)
    means = np.mean(rng.choice(values, size=(samples, len(values)), replace=True), axis=1)
    return {"mean": round(float(values.mean()), 4),
            "ci95": [round(float(x), 4) for x in np.quantile(means, [.025, .975])], "n": len(values)}


def summarize(rows: list[dict]) -> dict:
    counts = Counter(r["loc_pairwise"] for r in rows)
    valid = [r for r in rows if r["loc_pairwise"] in ("rag", "zero_shot", "tie")]
    score = CHRF(word_order=2)
    refs = [[r["ref"] for r in rows]]
    return {
        "n": len(rows), "localization": dict(counts),
        "generic": dict(Counter(r["pairwise"] for r in rows)),
        "reuse": dict(Counter(r["reuse"].get("reuse", "error") for r in rows)),
        "sign_test_p": sign_test(counts["rag"], counts["zero_shot"]),
        "accuracy": {"zero_shot": sum(r["loc_zs_accurate"] for r in valid),
                     "rag": sum(r["loc_rag_accurate"] for r in valid), "valid_n": len(valid)},
        "consistency": {"zero_shot": sum(r["zs_consistent"] for r in valid),
                        "rag": sum(r["rag_consistent"] for r in valid), "valid_n": len(valid)},
        "accuracy_delta": paired_mean_ci([int(r["loc_rag_accurate"])-int(r["loc_zs_accurate"]) for r in valid]),
        "chrf_corpus": {key: round(score.corpus_score([r[key] for r in rows], refs).score, 4)
                        for key in ("zero_shot", "rag")} if rows and all(r.get("ref") for r in rows) else None,
        "sentence_chrf_delta": paired_mean_ci([r["chrf_rag"]-r["chrf_zero_shot"] for r in rows
                                                if "chrf_rag" in r]),
    }


def build_evidence(root: Path = ROOT) -> dict:
    paths = [root / "results/router/rows.jsonl", root / "results/benchmarks/probes_rows.json",
             root / "results/benchmarks/rag_mt_outputs.jsonl"]
    rows = read_rows(paths[0])
    real = [r for r in rows if r["set"] == "real"]
    routed = [r for r in real if r["route"] == "semantic"]
    reusable = sum(r["reuse"].get("reuse") in ("full", "partial") for r in routed)
    probes = json.loads(paths[1].read_text())
    probe_metrics = {}
    for name in sorted({r["retriever"] for r in probes}):
        probe_metrics[name] = {}
        for category in ("edit", "paraphrase", "restructure"):
            subset = [r for r in probes if r["retriever"] == name and r["cat"] == category]
            hits = sum(r["rank"] == 1 for r in subset)
            probe_metrics[name][category] = {"n": len(subset), "hits_at_1": hits,
                                             "recall_at_1": hits / len(subset)}
    mt = read_rows(paths[2])
    metric = CHRF(word_order=2)
    mt_metrics = {}
    for band in ("95-99", "85-94", "75-84", "50-74", "<50", "ALL"):
        subset = mt if band == "ALL" else [r for r in mt if r["band"] == band]
        mt_metrics[band] = {"n": len(subset), "chrf": {
            condition: round(metric.corpus_score([r["hyp"][condition] for r in subset],
                                                  [[r["tgt"] for r in subset]]).score, 1)
            for condition in mt[0]["hyp"]}}
    return {
        "schema_version": 1, "status": "historical exploratory evidence; not a fresh validation",
        "provenance": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "metric_signature": str(metric.get_signature()),
        "coverage": {"real_n": len(real), "passing_n": len(routed), "reusable_passing_n": reusable,
                     "passing_rate_ci95": wilson(len(routed), len(real)),
                     "reusable_rate_ci95": wilson(reusable, len(real))},
        "routed_subset": summarize(routed), "all_real_original_treatment": summarize(real),
        "risk_original_treatment": summarize([r for r in rows if r["set"] == "risk"]),
        "no_route_changed_outputs": sum(r["route"] == "none" and r["rag"] != r["zero_shot"] for r in real),
        "retrieval": probe_metrics, "mt_by_band": mt_metrics,
        "limitations": [
            "The original evaluation always supplied at least one semantic example, even for route=none.",
            "The 85 passing real segments are a selected subset, not an independent validation set.",
            "Thresholds were chosen after exploratory analysis; frozen validation is still required.",
            "Generic and localization judgments use one model with different rubrics, not independent judges.",
            "The corpus acts as a proxy for approved client translations; corpus entries can contain errors.",
            "No dedicated, human-verified polarity labels support a 40/40 polarity-safety claim.",
            "Intervals resample segments and do not account for document dependence or judge error.",
        ],
    }


def render_report(e: dict) -> str:
    c, s = e["coverage"], e["routed_subset"]
    lines = ["# Audited historical evidence", "", e["status"], "",
             "Generated with `python -m locrag.evidence`; no inference is performed.", "",
             f"- Similarity threshold passed: **{c['passing_n']}/{c['real_n']}**.",
             f"- Passing candidate judged reusable: **{c['reusable_passing_n']}/{c['real_n']}** overall, "
             f"or **{c['reusable_passing_n']}/{c['passing_n']}** among passing candidates.",
             f"- Localization preference in the passing subset: **{s['localization'].get('rag',0)} wins / "
             f"{s['localization'].get('tie',0)} ties / {s['localization'].get('zero_shot',0)} losses**; "
             f"two-sided exact sign test p={s['sign_test_p']:.6g} (ties excluded).",
             f"- Accuracy judgments: **{s['accuracy']['zero_shot']} → {s['accuracy']['rag']}**. "
             "Accuracy equivalence has not been established.",
             f"- Corpus chrF++: **{s['chrf_corpus']['zero_shot']:.1f} → {s['chrf_corpus']['rag']:.1f}**.",
             f"- Paired mean sentence chrF++ change: **{s['sentence_chrf_delta']['mean']:.2f}**, "
             f"exploratory 95% bootstrap interval **{s['sentence_chrf_delta']['ci95']}**. "
             "This interval describes mean sentence scores, not corpus chrF++.",
             f"- **{e['no_route_changed_outputs']}** original no-route rows have different RAG and zero-shot outputs.",
             "", "## Translation experiment (original 200-segment study)", "",
             "| Fuzzy band | n | Zero-shot | Thresholded fuzzy | Semantic | Tiered (post hoc) |",
             "|---|---:|---:|---:|---:|---:|"]
    for band, row in e["mt_by_band"].items():
        v = row["chrf"]
        lines.append(f"| {band} | {row['n']} | {v['zero_shot']} | {v['fuzzy_cat75']} | {v['semantic']} | {v['tiered']} |")
    lines += ["", "## Interpretation limits", "", *[f"- {x}" for x in e["limitations"]], "",
              "Source SHA-256 hashes, all summaries, and metric signature are in `summary.json`.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "results/audit")
    args = ap.parse_args()
    evidence = build_evidence()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
    (args.output / "report.md").write_text(render_report(evidence), encoding="utf-8")
    print(f"Rebuilt evidence in {args.output}")


if __name__ == "__main__":
    main()
