"""Plot the preregistered comparisons from the archived numerical summary."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from locrag.study.consistency_panel import OUT


def main():
    results = json.loads((OUT / "summary.json").read_text())["models"]["Gemma"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.7), sharey=True, layout="constrained")
    for ax, measure, title in zip(axes, ["consistency", "accuracy"], ["Convention followed", "Meaning preserved"]):
        ax.axvline(0, color="#8a9298", lw=1)
        for y, group in enumerate(("high", "middle", "low")):
            for baseline, offset, color, label in [
                ("zero_shot", .13, "#27617a", "Semantic vs no TM"),
                ("fuzzy_ctx", -.13, "#aa512d", "Semantic vs fuzzy"),
            ]:
                pair = results[group]["paired"]["semantic_ctx_minus_" + baseline]
                point = pair[measure + "_pp"]
                lo, hi = pair[measure + "_ci95"]
                ax.errorbar(point, y + offset, xerr=[[point - lo], [hi - point]], color=color,
                            marker="o", ms=6, capsize=3, lw=2, label=label if y == 0 else None)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.grid(axis="x", alpha=.15)
        ax.set_xlabel("Paired difference (percentage points)")
        ax.spines[["right", "top"]].set_visible(False)
    axes[0].set_yticks([0, 1, 2], ["95–100", "75–94", "Below 75"])
    axes[0].set_ylabel("Best fuzzy score")
    axes[0].set_ylim(-.55, 2.55)
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.1, -.23), ncols=2, frameon=False)
    fig.savefig(OUT / "paired-effects.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
