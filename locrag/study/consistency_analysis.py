"""Replay cross-band accuracy, consistency and paired uncertainty from frozen annotations."""
import json
from collections import Counter

import numpy as np

from locrag.study.config import RESULTS_DIR, write_json
from locrag.study.consistency_panel import ARMS, BANDS, DIR, OUT, SEED
from locrag.study.data import read_jsonl

GROUPS = {"low": BANDS[:2], "middle": BANDS[2:4], "high": BANDS[4:]}
PAIRS = (("semantic_ctx", "fuzzy_ctx"), ("semantic_ctx", "zero_shot"), ("fuzzy_ctx", "zero_shot"))


def decoded(p):
    return {arm: p["verdicts"][letter]["passed"] for arm, letter in p["labels"].items()}


def assemble():
    sources = {r["row_id"]: r for r in read_jsonl(DIR / "sources.jsonl")}
    inputs = {(r["model"], r["row_id"]): r["outputs"] for r in read_jsonl(DIR / "translations.jsonl")}
    frozen = {r["row_id"]: r for r in read_jsonl(OUT / "conventions.jsonl")}
    if sources.keys() != frozen.keys():
        raise ValueError("Missing convention decisions")
    rows, reliability, seen = [], Counter(), set()
    calls = {r["call"]["request_hash"]: r["call"] for r in frozen.values()}
    for grade in read_jsonl(OUT / "grades.jsonl"):
        key = (grade["model"], grade["row_id"])
        if key in seen:
            raise ValueError(f"Duplicate {key}")
        seen.add(key)
        model, i = key
        r = sources[i]
        row = {"id": i, "model": model, "band": r["band"], "corpus": r["corpus"], "eligible": frozen[i]["eligible"]}
        assert ("consistency" in grade["evaluations"]) == row["eligible"]
        for task, passes in grade["evaluations"].items():
            first = decoded(passes[0])
            assert first.keys() == set(ARMS)
            assert len(set(inputs[key].values())) == len(passes[0]["verdicts"])
            row[task] = first
            for p in passes:
                calls[p["call"]["request_hash"]] = p["call"]
            if len(passes) == 2:
                second = decoded(passes[1])
                # Count an identical translation only once for this source.
                unique = {text: arm for arm, text in inputs[key].items()}
                reliability[task + "_rows"] += 1
                reliability[task + "_candidates"] += len(unique)
                reliability[task + "_agree"] += sum(first[a] == second[a] for a in unique.values())
        rows.append(row)
    if inputs.keys() != seen or len(rows) != 580:
        raise ValueError("Incomplete grading")
    return rows, dict(reliability), calls


def estimate(rows, seed=SEED):
    eligible = np.asarray([r["eligible"] for r in rows])
    acc = np.asarray([[r["accuracy"][a] for a in ARMS] for r in rows], dtype=int)
    con = np.asarray([[r.get("consistency", {}).get(a, False) for a in ARMS] for r in rows], dtype=int)
    n = len(rows)
    n_conv = int(eligible.sum())
    rng = np.random.default_rng(seed)
    strata = sorted({(r["corpus"], r["band"]) for r in rows})
    strata_draws = []
    for corpus, band in strata:
        idx = [i for i,r in enumerate(rows) if r["corpus"] == corpus and r["band"] == band]
        strata_draws.append(rng.choice(idx, size=(10000, len(idx))))
    draws = np.concatenate(strata_draws, axis=1)
    den = eligible[draws].sum(axis=1)
    out = {"n": n, "eligible": n_conv, "arms": {}, "paired": {}}
    samples = {}
    for j, arm in enumerate(ARMS):
        out["arms"][arm] = {"consistent": int(con[:, j].sum()), "accurate": int(acc[:, j].sum())}
    for after, before in PAIRS:
        a, b = ARMS.index(after), ARMS.index(before)
        diff = con[:, a] - con[:, b]
        # Ineligible rows contribute zero to both arm numerators.
        con_boot = diff[draws].sum(axis=1) / np.where(den > 0, den, np.nan)
        acc_diff = acc[:, a] - acc[:, b]
        acc_boot = acc_diff[draws].mean(axis=1)
        tag = after + "_minus_" + before
        both_accurate = (acc[:, a] == 1) & (acc[:, b] == 1)
        out["paired"][tag] = {
            "consistency_pp": float(100 * diff.sum() / n_conv) if n_conv else None,
            "consistency_ci95": (100 * np.nanquantile(con_boot, [.025, .975])).tolist() if n_conv else None,
            "accuracy_pp": float(100 * acc_diff.mean()),
            "accuracy_ci95": (100 * np.quantile(acc_boot, [.025, .975])).tolist(),
            "con_fixes": int((diff == 1).sum()), "con_losses": int((diff == -1).sum()),
            "con_fixes_both_accurate": int(((diff == 1) & both_accurate).sum()),
            "con_losses_both_accurate": int(((diff == -1) & both_accurate).sum()),
            "meaning_errors_introduced": int((acc_diff == -1).sum()),
            "meaning_errors_fixed": int((acc_diff == 1).sum()),
        }
        samples[tag] = con_boot
    return out, samples


def qe_on_consistency_fixes(rows):
    """Exploratory: did archived reference-free QE detect accuracy-preserving fixes?"""
    archive = RESULTS_DIR / "test-v1"
    eps = json.loads((archive / "summary.json").read_text())["noise_floor"]["eps"]
    subset = [r for r in rows if r["model"] == "Gemma" and r["band"] in GROUPS["low"] and r["eligible"]]
    ids = {r["id"] for r in subset}
    qe = {(r["row_id"], r["condition"]): r["qe"]["cometkiwi22"]
          for r in read_jsonl(archive / "rows_analysis.jsonl") if r["row_id"] in ids and r["condition"] in ARMS}
    out = {"archived_epsilon": eps}
    for before in ("zero_shot", "fuzzy_ctx"):
        deltas = [qe[r["id"], "semantic_ctx"] - qe[r["id"], before] for r in subset
                  if r["accuracy"][before] and r["accuracy"]["semantic_ctx"]
                  and not r["consistency"][before] and r["consistency"]["semantic_ctx"]]
        out["semantic_ctx_minus_" + before] = {
            "fixes": len(deltas), "up": sum(d >= eps for d in deltas),
            "within_noise_floor": sum(abs(d) < eps for d in deltas), "down": sum(d <= -eps for d in deltas),
        }
    return out


def main():
    rows, reliability, calls = assemble()
    summary = {"models": {}, "reversal_agreement": reliability,
               "unique_calls": len(calls), "cost_upper_usd_completed": sum(c["cost_upper_usd"] for c in calls.values())}
    for model in ("Gemma", "Astra"):
        sub = [r for r in rows if r["model"] == model]
        out, distributions = {}, {}
        for key, bands in {"all": BANDS, **GROUPS, **{b: (b,) for b in BANDS}}.items():
            part = [r for r in sub if r["band"] in bands]
            if part:
                out[key], boot = estimate(part, seed=SEED + int(key == "high"))
                distributions[key] = boot["semantic_ctx_minus_fuzzy_ctx"]
        if "high" in out:
            delta = distributions["low"] - distributions["high"]
            tag = "semantic_ctx_minus_fuzzy_ctx"
            point = out["low"]["paired"][tag]["consistency_pp"] - out["high"]["paired"][tag]["consistency_pp"]
            out["low_minus_high_semantic_advantage"] = {"pp": point, "ci95": (100 * np.nanquantile(delta,[.025,.975])).tolist()}
        out["low_by_domain"] = {
            corpus: estimate([r for r in sub if r["band"] in GROUPS["low"] and r["corpus"] == corpus])[0]
            for corpus in sorted({r["corpus"] for r in sub})
        }
        summary["models"][model] = out
    summary["exploratory_qe_on_low_band_fixes"] = qe_on_consistency_fixes(rows)
    write_json(OUT / "summary.json", summary)


if __name__ == "__main__":
    main()
