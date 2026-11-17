"""Unblind the LLM-judge scores (Claude Opus 5.5, in-session, reference-guided MQM-lite) and compare with metrics."""
import json, sys
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

D = "results/study/test-v1/llm_judge"
SEV = {"minor": 1, "major": 5, "critical": 10}
SYS = ["tm_as_is", "hybrid_ctx", "zero_shot", "nmt_deepl"]
BANDS = ["100", "95-99", "85-94", "75-84", "50-74", "<50"]
key = json.load(open(f"{D}/key.json"))
rows = {}
for l in open("results/study/test-v1/rows_analysis.jsonl"):
    r = json.loads(l)
    if r["condition"] in SYS:
        rows[(r["row_id"], r["condition"])] = r
rec = []  # one per (row, system)
for l in open(f"{D}/scores.jsonl"):
    s = json.loads(l)
    k = key[s["item"]]
    pts = sum(SEV[e[1]] for e in s["errors"])
    worst = max([SEV[e[1]] for e in s["errors"]], default=0)
    for sysname in k[s["cand"]]:
        r = rows[(k["row_id"], sysname)]
        q = r["qe"]
        rec.append(dict(item=s["item"], row_id=k["row_id"], sys=sysname, band=r["band"], corpus=r["corpus"],
                        score=s["score"], mqm=pts, worst=worst, kiwi=q.get("cometkiwi22"),
                        comet=q.get("comet22"), chrf=q.get("chrf"), errors=s["errors"], mt=r["translation"]))
json.dump(rec, open(f"{D}/unblinded.json", "w"), ensure_ascii=False, indent=0)
rng = np.random.default_rng(7)
def ci(x):
    x = np.asarray(x, float); b = [rng.choice(x, len(x)).mean() for _ in range(5000)]
    return np.percentile(b, [2.5, 97.5])

by = defaultdict(dict)
for r in rec: by[r["row_id"]][r["sys"]] = r
print("## Per system (n=72 rows each)\n")
print("| system | mean score | mean MQM pts (lower better) | rows with major+ error | rows with critical error |")
print("|---|---:|---:|---:|---:|")
for s in SYS:
    xs = [v[s] for v in by.values()]
    print(f"| {s} | {np.mean([x['score'] for x in xs]):.1f} | {np.mean([x['mqm'] for x in xs]):.2f} | "
          f"{sum(x['worst']>=5 for x in xs)} | {sum(x['worst']>=10 for x in xs)} |")
print("\n## Mean judge score by band\n")
print("| band | n | " + " | ".join(SYS) + " | hybrid − TM [95% CI] | hybrid W/T/L vs TM |")
print("|---|---:|" + "---:|" * (len(SYS) + 2))
for b in BANDS + ["all"]:
    vs = [v for v in by.values() if b == "all" or v["tm_as_is"]["band"] == b]
    d = [v["hybrid_ctx"]["score"] - v["tm_as_is"]["score"] for v in vs]
    lo, hi = ci(d)
    w = sum(x > 0 for x in d); t = sum(x == 0 for x in d); L = sum(x < 0 for x in d)
    print(f"| {b} | {len(vs)} | " + " | ".join(f"{np.mean([v[s]['score'] for v in vs]):.1f}" for s in SYS)
          + f" | {np.mean(d):+.1f} [{lo:+.1f}, {hi:+.1f}] | {w}/{t}/{L} |")
print("\n## Pairwise vs hybrid_ctx (judge score), all bands\n")
for s in ("tm_as_is", "zero_shot", "nmt_deepl"):
    d = [v["hybrid_ctx"]["score"] - v[s]["score"] for v in by.values()]
    lo, hi = ci(d)
    print(f"- hybrid − {s}: {np.mean(d):+.1f} [{lo:+.1f}, {hi:+.1f}]; W/T/L {sum(x>0 for x in d)}/{sum(x==0 for x in d)}/{sum(x<0 for x in d)}")
print("\n## Agreement of metrics with the judge (Spearman over row×system)\n")
for m in ("kiwi", "comet", "chrf"):
    xs = [r for r in rec if r[m] is not None]
    print(f"- {m}: rho={spearmanr([r[m] for r in xs], [r['score'] for r in xs])[0]:.2f} (n={len(xs)})")
print("\n## Do metrics flag the outputs the judge found major/critical errors in?\n")
from locrag.study.stats import auc
for label, pool in (("all systems", rec), ("generated only (hybrid, zero-shot, DeepL)", [r for r in rec if r["sys"] != "tm_as_is"])):
    print(f"**{label}**\n")
    print("| metric | AUC: clean > major/critical | flagged errors that score above the clean median |")
    print("|---|---:|---:|")
    for m in ("kiwi", "comet", "chrf"):
        xs = [r for r in pool if r[m] is not None]
        bad = [r[m] for r in xs if r["worst"] >= 5]; ok = [r[m] for r in xs if r["worst"] == 0]
        if not bad or not ok: continue
        a = auc(bad + ok, [0]*len(bad) + [1]*len(ok))
        med = float(np.median(ok))
        print(f"| {m} | {a:.2f} | {sum(b > med for b in bad)}/{len(bad)} |")
    print()
gen = [r for r in rec if r["sys"] != "tm_as_is" and r["worst"] >= 5]
print("## Major/critical errors in generated outputs, with metric scores\n")
for r in sorted(gen, key=lambda r: -(r["kiwi"] or 0)):
    e = "; ".join(f"{x[1]}: {x[2]}" for x in r["errors"] if SEV[x[1]] >= 5)
    print(f"- {r['row_id']} {r['sys']} band {r['band']}: Kiwi {r['kiwi']:.3f}, COMET {r['comet']:.3f}, chrF {r['chrf']:.0f} | {e}")
