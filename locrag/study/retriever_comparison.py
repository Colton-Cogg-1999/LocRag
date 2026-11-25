"""Rebuild the below-cutoff Gemma comparison from the public, frozen run."""
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from locrag.study.config import RESULTS_DIR, ROOT, write_json
from locrag.study.data import read_jsonl
from locrag.study.stats import bootstrap_mean_ci


def main():
    groups = defaultdict(dict)
    for r in read_jsonl(RESULTS_DIR / "test-v1" / "rows_analysis.jsonl"):
        if r["band"] in ("50-74", "<50") and r["condition"] in ("hybrid_ctx", "fuzzy_ctx"):
            if r["error"] or r["condition"] in groups[r["row_id"]]:
                raise ValueError(f"Incomplete or duplicate output for {r['row_id']}")
            groups[r["row_id"]][r["condition"]] = r
    pairs = [(g["hybrid_ctx"], g["fuzzy_ctx"]) for _, g in sorted(groups.items())]
    strata = sorted({(h["corpus"], h["lang"]) for h, f in pairs})
    summaries = {}
    for corpus, lang in [("All", "all"), *strata]:
        subset = [(h, f) for h, f in pairs if corpus == "All" or (h["corpus"], h["lang"]) == (corpus, lang)]
        counts = Counter()
        for h, f in subset:
            same_tm = [e["tm_id"] for e in h["retrieved"]] == [e["tm_id"] for e in f["retrieved"]]
            same_text = h["translation"] == f["translation"]
            counts[("same" if same_tm else "different") + "_tm_" + ("same" if same_text else "different") + "_text"] += 1
        metrics = {}
        for metric, scale in [("chrf", 1), ("cometkiwi22", 100), ("comet22", 100)]:
            scored = [(h, f) for h, f in subset if all(r["qe"].get(metric) is not None for r in (h, f))]
            metrics[metric] = bootstrap_mean_ci(
                [(h["qe"][metric] - f["qe"][metric]) * scale for h, f in scored],
                clusters=[h["src_id"] for h, f in scored],
            )
        summaries[f"{corpus}/{lang}"] = dict(rows=len(subset), counts=dict(counts), hybrid_minus_fuzzy=metrics)
    out = ROOT / "results" / "retriever-comparison"
    write_json(out / "summary.json", summaries)
    fig, ax = plt.subplots(figsize=(8, 3.5), layout="constrained")
    y = np.arange(len(strata))
    for offset, kind, label, color in [(-.17, "tm", "Top-3 list changed", "#326b93"),
                                       (.17, "text", "Translation changed", "#ad582c")]:
        rates = []
        for corpus, lang in strata:
            s = summaries[f"{corpus}/{lang}"]
            rates.append(100 * sum(n for key, n in s["counts"].items() if
                         (key.startswith("different_tm") if kind == "tm" else key.endswith("different_text"))) / s["rows"])
        bars = ax.barh(y + offset, rates, height=.30, label=label, color=color)
        ax.bar_label(bars, fmt="%.0f%%", padding=3)
    ax.set(yticks=y, yticklabels=[f"{c} · en → {l}" for c, l in strata], xlim=(0, 112),
           xlabel="Share of matched segments below the 75% fuzzy cutoff", title="Switching from fuzzy to hybrid retrieval")
    ax.invert_yaxis()
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.21), ncols=2, frameon=False)
    ax.spines[["right", "top"]].set_visible(False)
    fig.savefig(out / "retrieval-and-translation.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
