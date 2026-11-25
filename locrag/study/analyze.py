"""Analysis and reporting for a study run. Reads only stage outputs; makes no model calls.

Writes into the run directory:
  rows_analysis.jsonl   one record per (row, condition): retrieval, reuse, prompt/context, output, QE, ΔQE, cost
  summary.json          every number in the report
  report.md             sections A–F
  examples.md           largest improvements/degradations with full context
  human_eval/           blinded stratified sample (items.csv) + separate key (key.csv)
"""
from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from locrag.study import features as F
from locrag.study import stats as S
from locrag.study.config import write_json
from locrag.study.data import load_heldout, load_references, load_tm, read_jsonl
from locrag.study.config import DATA_DIR
from locrag.study.generate import latest_outputs
from locrag.study.qe_bridge import attach_scores, item_id
from locrag.study.retrieval import load_candidates

BANDS = ["100", "95-99", "85-94", "75-84", "50-74", "<50"]
CONTEXT = ["fuzzy_ctx", "semantic_ctx", "hybrid_ctx", "structured_ctx", "draft_ctx"]
COMPARE = CONTEXT + ["nmt_deepl", "tm_as_is"]
LABEL_RANK = {"full": 0, "partial": 1, "terminology": 2, "style_convention": 3, "none": 4, "misleading": 5}
PRIMARY, ROBUST = "cometkiwi22", "metricx24_qe"
ORIENT = {"cometkiwi22": 1.0, "metricx24_qe": -1.0, "comet22": 1.0, "chrf": 1.0, "metricx24_ref": -1.0}
CANDIDATES = DATA_DIR / "candidates.jsonl"


# ------------------------------------------------------------------------------------------- loading
class Run:
    def __init__(self, run_dir: Path, rows: list[dict], cfg: dict):
        self.dir, self.cfg = run_dir, cfg
        self.rows = {r["row_id"]: r for r in rows}
        self.out = {k: v for k, v in latest_outputs(run_dir / "translations.jsonl").items() if k[0] in self.rows}
        self.refs = load_references(DATA_DIR)
        self.cands = load_candidates(CANDIDATES)
        sources = {rid: r["src"] for rid, r in self.rows.items()}
        metrics = [m for m in ("cometkiwi22", "metricx24_qe", "comet22", "metricx24_ref")
                   if (run_dir / "qe" / f"{m}.jsonl").exists()] + ["chrf"]
        self.metrics = metrics
        self.scores = attach_scores(run_dir, list(self.out.values()), sources, self.refs, metrics)
        self.reuse = {r["row_id"]: r for r in read_jsonl(run_dir / "reuse.jsonl")}
        self.extr = {r["row_id"]: r for r in read_jsonl(run_dir / "extractions.jsonl")}
        self.extr_audit = read_jsonl(run_dir / "extraction_audit.jsonl")
        self.mqm = {r["item_id"]: r for r in read_jsonl(run_dir / "mqm.jsonl")}
        self.conditions = sorted({c for _, c in self.out}, key=lambda c: (c not in ("zero_shot",), c))
        self._tms: dict = {}

    def tm(self, corpus, lang):
        if (corpus, lang) not in self._tms:
            self._tms[(corpus, lang)] = load_tm(DATA_DIR, corpus, lang)
        return self._tms[(corpus, lang)]

    def good(self, rid: str, cond: str, metric: str) -> float | None:
        v = self.scores.get((rid, cond), {}).get(metric)
        return None if v is None else ORIENT[metric] * v

    def delta(self, rid: str, cond: str, metric: str, base: str = "zero_shot") -> float | None:
        a, b = self.good(rid, cond, metric), self.good(rid, base, metric)
        return None if a is None or b is None else a - b

    def best_label(self, rid: str, cond: str | None = None) -> str | None:
        """Most valuable verified label among TM units shown under `cond` (or any of B/C/D)."""
        rec = self.reuse.get(rid)
        if not rec or rec.get("error"):
            return None
        shown = None
        if cond:
            o = self.out.get((rid, cond))
            shown = set(o.get("candidate_tm_idx") or []) if o else set()
        labels = [l for l in rec["labels"] if shown is None or l["tm_idx"] in shown]
        if not labels:
            return "none"
        if any(l["verified_reusable"] for l in labels):
            return min((l["label"] for l in labels if l["verified_reusable"]), key=LABEL_RANK.get)
        return "misleading" if any(l["label"] == "misleading" for l in labels) else "none"

    def any_misleading(self, rid: str, cond: str | None = None) -> bool | None:
        rec = self.reuse.get(rid)
        if not rec or rec.get("error"):
            return None
        shown = None
        if cond and (o := self.out.get((rid, cond))):
            shown = set(o.get("candidate_tm_idx") or [])
        return any((l["label"] == "misleading" or l["risk"]) for l in rec["labels"] if shown is None or l["tm_idx"] in shown)


def strata(run: Run) -> dict[str, list[str]]:
    by: dict[str, list[str]] = defaultdict(list)
    for rid, r in run.rows.items():
        by[f"{r['corpus']}/{r['lang']}"].append(rid)
        by["ALL"].append(rid)
        if r["corpus"] == "KDE4":
            by["KDE4/all"].append(rid)
    return dict(sorted(by.items(), key=lambda kv: (kv[0] == "ALL", kv[0])))


# ------------------------------------------------------------------------------------------- noise floor
def noise_floor(run: Run, q: float) -> dict:
    """ε = q-quantile of |ΔKiwi| between two independent zero-shot generations of the SAME prompt, computed over
    pairs whose outputs differ: the QE movement produced by an equally valid alternative wording. (Including the
    many identical regenerations would make ε ≈ 0 and reflect output stability, not QE sensitivity.)"""
    pairs = [(rid, run.out.get((rid, "zero_shot")), run.out.get((rid, "zero_shot_repeat"))) for rid in run.rows]
    pairs = [(rid, a, b) for rid, a, b in pairs if a and b and a.get("translation") and b.get("translation")]
    differ = [rid for rid, a, b in pairs if a["translation"] != b["translation"]]
    d_all = np.abs([x for rid, _, _ in pairs if (x := run.delta(rid, "zero_shot_repeat", PRIMARY)) is not None])
    d = np.abs([x for rid in differ if (x := run.delta(rid, "zero_shot_repeat", PRIMARY)) is not None])
    dm = np.abs([x for rid in differ if (x := run.delta(rid, "zero_shot_repeat", ROBUST)) is not None])
    if not len(d):
        return {"n_pairs": len(pairs), "n_differing": 0, "eps": None}
    return {"n_pairs": len(pairs), "n_differing": len(differ), "share_identical": 1 - len(differ) / max(1, len(pairs)),
            "eps": float(np.quantile(d, q)), "quantile": q, "definition": "quantile of |ΔKiwi| over differing regenerations",
            "abs_delta_quantiles_differing": {str(p): float(np.quantile(d, p)) for p in (0.5, 0.75, 0.9, 0.95)},
            "eps_including_identical": float(np.quantile(d_all, q)) if len(d_all) else None,
            "metricx_eps": float(np.quantile(dm, q)) if len(dm) else None}


# ------------------------------------------------------------------------------------------- A. recovery
def recovery(run: Run) -> dict:
    floor = run.cfg["retrieval"]["semantic_floor"]
    k = run.cfg["retrieval"]["k"]
    out = {}
    for name, rids in strata(run).items():
        table = {}
        for band in BANDS + ["below75", "all"]:
            sel = [r for r in rids if (band == "all" or (band == "below75" and run.rows[r]["fuzzy_best"] < 75)
                                       or run.rows[r]["band"] == band)]
            sel = [r for r in sel if r in run.reuse and not run.reuse[r].get("error")]
            if not sel:
                continue
            n = len(sel)
            cov = sum(run.cands[run.rows[r]["src_id"]]["cos_best"] >= floor for r in sel)

            def units(r, key):
                return set(run.cands[run.rows[r]["src_id"]][key][:k])

            def has(r, pool=None, substantive=False):
                return any(l["verified_reusable"] and (not substantive or l["label"] in ("full", "partial"))
                           and (pool is None or l["tm_idx"] in pool) for l in run.reuse[r]["labels"])
            ver = sum(has(r) for r in sel)
            sub = sum(has(r, substantive=True) for r in sel)
            ver_by = {key: sum(has(r, units(r, key)) for r in sel) for key in ("fuzzy", "semantic", "hybrid")}
            sub_by = {key: sum(has(r, units(r, key), True) for r in sel) for key in ("fuzzy", "semantic", "hybrid")}
            # semantic-only: semantic top-k holds verified material while the fuzzy top-k holds none
            sem_only = sum(has(r, units(r, "semantic")) and not has(r, units(r, "fuzzy")) for r in sel)
            sub_sem_only = sum(has(r, units(r, "semantic"), True) and not has(r, units(r, "fuzzy"), True) for r in sel)
            best = Counter(run.best_label(r) for r in sel)
            mis = sum(any(l["label"] == "misleading" for l in run.reuse[r]["labels"]) for r in sel)
            risk = sum(any(l["risk"] for l in run.reuse[r]["labels"]) for r in sel)
            table[band] = {"n": n, "semantic_coverage": cov, "semantic_coverage_ci": S.wilson(cov, n),
                           "verified_reusable": ver, "verified_reusable_ci": S.wilson(ver, n),
                           "substantive_reusable": sub, "substantive_reusable_ci": S.wilson(sub, n),
                           "verified_by_retriever": ver_by, "substantive_by_retriever": sub_by,
                           "verified_semantic_only": sem_only, "substantive_semantic_only": sub_sem_only,
                           "best_label": dict(best), "rows_with_misleading_candidate": mis,
                           "rows_with_risk_flag": risk,
                           "labeled_candidates_verbatim_fail": sum(
                               1 for r in sel for l in run.reuse[r]["labels"]
                               if l["label"] in ("full", "partial", "terminology") and not l["verified_reusable"])}
        out[name] = table
    return out


def population_weighted_below75(run: Run, rec: dict) -> dict:
    """Below-75 recovery rate re-weighted to the pool's natural 50-74 / <50 mix (per corpus)."""
    out = {}
    for corpus in run.cfg["corpora"]:
        man = json.loads((DATA_DIR / corpus / "manifest.json").read_text())
        nat = man["pool_natural_band_counts"]
        w = {b: nat.get(b, 0) for b in ("50-74", "<50")}
        tot = sum(w.values()) or 1
        for name, table in rec.items():
            if not name.startswith(corpus + "/"):
                continue
            if all(b in table for b in w):
                rate = sum(w[b] / tot * table[b]["verified_reusable"] / table[b]["n"] for b in w)
                srate = sum(w[b] / tot * table[b]["substantive_reusable"] / table[b]["n"] for b in w)
                out[name] = {"weighted_rate": rate, "weighted_substantive_rate": srate, "weights": {b: w[b] / tot for b in w}}
    return out


# ------------------------------------------------------------------------------------------- B/C. quality
REF_METRICS = ("comet22", "chrf")


def compare(run: Run, rids: list[str], cond: str, eps: float | None, B: int, metric: str = PRIMARY) -> dict:
    ids, d, agree, clusters = [], [], [], []
    for r in rids:
        x = run.delta(r, cond, metric)
        if x is None:
            continue
        ids.append(r)
        d.append(x)
        y = run.delta(r, cond, ROBUST) if metric == PRIMARY else None
        agree.append(0.0 if y is None else y)
        clusters.append(run.rows[r]["src_id"])
    if not d:
        return {"n": 0}
    multi_lang = len({run.rows[r]["lang"] for r in ids}) > 1
    res = S.paired_summary(d, clusters if multi_lang else None, B=B, eps=eps,
                           agree=agree if metric == PRIMARY and ROBUST in run.metrics else None)
    rob = [run.delta(r, cond, ROBUST) for r in ids]
    rob = [x for x in rob if x is not None]
    if rob and metric == PRIMARY:
        res["robust_mean"] = float(np.mean(rob))
        res["robust_ci"] = S.bootstrap_mean_ci(rob, B=B)["ci"]
        res["sign_agreement"] = float(np.mean([np.sign(a) == np.sign(b) for a, b in zip(d, agree) if a != 0 and b != 0])) \
            if any(a != 0 and b != 0 for a, b in zip(d, agree)) else None
    return res


def quality(run: Run, eps: float | None, B: int) -> dict:
    out = {}
    for name, rids in strata(run).items():
        for subset in ("all", "below75"):
            sel = rids if subset == "all" else [r for r in rids if run.rows[r]["fuzzy_best"] < 75]
            block = {"absolute": {}, "vs_zero_shot": {}}
            for cond in [c for c in run.conditions if c != "zero_shot_repeat"]:
                vals = [run.good(r, cond, PRIMARY) for r in sel]
                vals = [v for v in vals if v is not None]
                if vals:
                    block["absolute"][cond] = {"mean": float(np.mean(vals)), "n": len(vals)}
            pvals = {}
            for cond in [c for c in COMPARE if c in run.conditions]:
                res = compare(run, sel, cond, eps, B)
                block["vs_zero_shot"][cond] = res
                pvals[cond] = res.get("p")
            for cond, padj in S.holm(pvals).items():
                block["vs_zero_shot"][cond]["p_holm"] = padj
            clean = [r for r in sel if not run.refs[r].get("ref_in_tm_targets")]
            for m in REF_METRICS:
                if m in run.metrics:
                    block[f"secondary_{m}"] = {c: compare(run, sel, c, None, B, metric=m)
                                               for c in COMPARE if c in run.conditions}
                    # leakage check: drop rows whose reference also occurs as a TM target
                    block[f"secondary_{m}_clean"] = {c: compare(run, clean, c, None, B, metric=m)
                                                     for c in COMPARE if c in run.conditions}
            out[f"{name}|{subset}"] = block
    return out


def by_band(run: Run, eps: float | None, B: int, metric: str = PRIMARY) -> dict:
    out = {}
    for name, rids in strata(run).items():
        if name == "ALL":
            continue
        out[name] = {band: {cond: compare(run, [r for r in rids if run.rows[r]["band"] == band], cond,
                                          eps if metric == PRIMARY else None, B, metric=metric)
                            for cond in COMPARE if cond in run.conditions} for band in BANDS}
    return out


def crossover_analysis(run: Run, B: int, metric: str = PRIMARY) -> dict:
    """H3: where raw TM stops beating NMT / zero-shot LLM, and the best 'TM ≥ τ else X' pipeline thresholds."""
    out = {}
    for name, rids in strata(run).items():
        if name in ("ALL",):
            continue
        res = {}
        for alt in ("nmt_deepl", "zero_shot", "hybrid_ctx", "structured_ctx", "draft_ctx"):
            sel = [r for r in rids if run.good(r, "tm_as_is", metric) is not None and run.good(r, alt, metric) is not None]
            if len(sel) < 20:
                continue
            x = [run.rows[r]["fuzzy_best"] for r in sel]
            t = [run.good(r, "tm_as_is", metric) for r in sel]
            a = [run.good(r, alt, metric) for r in sel]
            sweep = S.threshold_sweep(x, t, a, B=B)
            best = max(sweep, key=lambda s: s["mean"])
            res[alt] = {"crossover": S.crossover_ci(x, np.subtract(t, a), B=min(B, 1000)),
                        "best_tau": best["tau"], "best_mean": best["mean"],
                        "never_tm_mean": sweep[-1]["mean"] if sweep[-1]["tau"] == 100 else None,
                        "sweep": sweep}
        # where does LLM+TM context start beating zero-shot? per band: CI lower bound > 0
        res["context_helps_bands"] = {cond: [b for b in BANDS if (c := compare(run, [r for r in rids if run.rows[r]["band"] == b], cond, None, B, metric=metric)).get("ci") and c["ci"][0] > 0]
                                      for cond in CONTEXT if cond in run.conditions}
        out[name] = res
    return out


# ------------------------------------------------------------------------------------------- D. failures
def failure_analysis(run: Run, eps: float | None) -> dict:
    det = {}
    for cond in [c for c in run.conditions if c != "zero_shot_repeat"]:
        num = neg = induced = n = 0
        for rid, r in run.rows.items():
            o = run.out.get((rid, cond))
            if not o or not o.get("translation"):
                continue
            n += 1
            hyp = o["translation"]
            num += F.number_mismatch(r["src"], hyp)
            neg += F.negation_mismatch(r["src"], hyp, r["lang"])
            z = run.out.get((rid, "zero_shot"), {}).get("translation") or ""
            tm = run.tm(r["corpus"], r["lang"])
            induced += F.tm_induced_ngrams(hyp, z, [tm[i]["tgt"] for i in (o.get("candidate_tm_idx") or [])], r["lang"]) > 0 \
                if cond in CONTEXT else 0
        det[cond] = {"n": n, "number_mismatch": num, "negation_mismatch": neg, "rows_with_tm_induced_ngrams": induced}
    # degradation vs reuse label of the shown context
    by_label = {}
    for cond in [c for c in CONTEXT if c in run.conditions]:
        groups = defaultdict(list)
        for rid in run.rows:
            d = run.delta(rid, cond, PRIMARY)
            lab = run.best_label(rid, cond if cond != "structured_ctx" else "hybrid_ctx")
            if d is not None and lab is not None:
                groups[lab].append(d)
        by_label[cond] = {lab: {"n": len(v), "mean_delta": float(np.mean(v)),
                                "degraded": int(sum(x <= -(eps or 0) for x in v)) if eps else None,
                                "improved": int(sum(x >= (eps or 0) for x in v)) if eps else None}
                          for lab, v in sorted(groups.items(), key=lambda kv: LABEL_RANK.get(kv[0], 9))}
    # extractor faithfulness (verbatim) and semantic audit
    items = [it for e in run.extr.values() for it in (e.get("items") or []) if it.get("kind") in ("terms", "phrases")]
    reasons = Counter(r for it in items if not it["ok"] for r in it["reason"].split(","))
    audit_items = [it for a in run.extr_audit for it in a.get("items", [])]
    extractor = {
        "rows": len(run.extr), "parse_errors": sum(bool(e.get("error")) for e in run.extr.values()),
        "empty_context_rows": sum(not e.get("context_block") for e in run.extr.values()),
        "span_items": len(items), "span_items_verbatim_ok": sum(it["ok"] for it in items),
        "failure_reasons": dict(reasons),
        "audit": {"rows": len(run.extr_audit), "items": len(audit_items),
                  "mapping_correct": sum(i["mapping_correct"] for i in audit_items),
                  "applies": sum(i["applies"] for i in audit_items),
                  "by_kind": {k: {"n": len(v), "mapping_correct": sum(i["mapping_correct"] for i in v),
                                  "applies": sum(i["applies"] for i in v)}
                              for k, v in _group(audit_items, "kind").items()},
                  "verbatim_ok_but_not_applies": sum(1 for i in audit_items if i.get("ok") and not i["applies"]
                                                      and i.get("kind") in ("terms", "phrases"))}}
    # predictors of benefit (hybrid & structured): AUC for meaningful improvement
    pred = {}
    for cond in [c for c in ("hybrid_ctx", "structured_ctx", "draft_ctx", "semantic_ctx") if c in run.conditions]:
        ys, xs = [], defaultdict(list)
        for rid, r in run.rows.items():
            d = run.delta(rid, cond, PRIMARY)
            if d is None or eps is None:
                continue
            c = run.cands[r["src_id"]]
            lab = run.best_label(rid, "hybrid_ctx" if cond in ("structured_ctx", "draft_ctx") else cond)
            ys.append(d >= eps)
            xs["fuzzy_best"].append(r["fuzzy_best"])
            xs["cos_best"].append(c["cos_best"])
            xs["verified_label_rank"].append(-(LABEL_RANK.get(lab, 5) if lab else 5))
            xs["zero_shot_qe_low"].append(-(run.good(rid, "zero_shot", PRIMARY) or 0))
        pred[cond] = {"n": len(ys), "positives": int(sum(ys)),
                      "auc": {k: S.auc(v, ys) for k, v in xs.items()}}
    return {"detectors": det, "delta_by_reuse_label": by_label, "extractor": extractor, "benefit_predictors": pred}


def _group(items, key):
    g = defaultdict(list)
    for i in items:
        g[i.get(key)].append(i)
    return g


def regression(run: Run, td: F.TermDensity, B: int) -> dict:
    out = {}
    for cond in [c for c in ("hybrid_ctx", "structured_ctx", "draft_ctx") if c in run.conditions]:
        X, y, cl = [], [], []
        for rid, r in run.rows.items():
            d = run.delta(rid, cond, PRIMARY)
            o = run.out.get((rid, cond))
            base = run.good(rid, "zero_shot", PRIMARY)
            if d is None or base is None or not o:
                continue
            c = run.cands[r["src_id"]]
            lab = run.best_label(rid, "hybrid_ctx")
            X.append([r["fuzzy_best"] / 100, c["cos_best"], float(lab in ("full", "partial", "terminology")),
                      float(bool(run.any_misleading(rid, "hybrid_ctx"))), np.log(len(r["src"].split())),
                      td.density(r["src"], r["corpus"]), (o.get("accounting") or {}).get("prompt_tokens", 0) / 1000,
                      base, float(r["corpus"] == "KDE4")])
            y.append(d)
            cl.append(r["src_id"])
        if len(y) > 30:
            names = ["fuzzy_best/100", "cos_best", "verified_reusable", "misleading_shown", "log_src_words",
                     "term_density", "prompt_ktokens", "zero_shot_qe", "is_KDE4"]
            out[cond] = {"n": len(y), "coefficients": S.ols(np.asarray(X), np.asarray(y), names, B=min(B, 2000), clusters=cl),
                         "note": "Descriptive OLS of ΔQE on row features; zero_shot_qe coefficient partly reflects regression to the mean."}
    return out


# ------------------------------------------------------------------------------------------- QE probes
PROBES = ("number_change", "drop_end", "untranslated", "append_unrelated", "negation_removed", "tm_swap")


def make_probes(rows: dict, outs: dict, cands: dict, tm_lookup, seed: int, per_probe: int = 150) -> list[dict]:
    """Controlled corruptions of zero-shot outputs; returned as extra (row_id, probe, hyp) items to score."""
    rng = random.Random(seed)
    zs = [(rid, o["translation"]) for (rid, c), o in sorted(outs.items()) if c == "zero_shot" and o.get("translation")]
    by_lang = defaultdict(list)
    for rid, h in zs:
        by_lang[rows[rid]["lang"]].append(h)
    items = []
    rng.shuffle(zs)
    count = Counter()
    for rid, hyp in zs:
        r = rows[rid]
        cand = {}
        if re.search(r"\d", hyp):
            cand["number_change"] = re.sub(r"\d+", lambda m: str(int(m.group()) + 1 if len(m.group()) < 6 else 7), hyp, count=1)
        toks = hyp.split() if r["lang"] != "zh_CN" else list(hyp)
        if len(toks) >= 6:
            keep = toks[: max(1, int(len(toks) * 0.65))]
            cand["drop_end"] = (" " if r["lang"] != "zh_CN" else "").join(keep)
        cand["untranslated"] = r["src"]
        others = [h for h in by_lang[r["lang"]] if h != hyp]
        if others:
            cand["append_unrelated"] = hyp + (" " if r["lang"] != "zh_CN" else "") + rng.choice(others)
        if F.has_negation(hyp, r["lang"]):
            cand["negation_removed"] = F.NEGATION[r["lang"]].sub("", hyp, count=1).replace("  ", " ").strip()
        if r["band"] == "<50":
            idx = cands[r["src_id"]]["semantic"][0]
            cand["tm_swap"] = tm_lookup(r["corpus"], r["lang"])[idx]["tgt"]
        for probe, ph in cand.items():
            if count[probe] < per_probe and ph and ph != hyp:
                count[probe] += 1
                items.append({"row_id": rid, "probe": probe, "translation": ph, "condition": f"probe:{probe}"})
    return items


def probe_results(run: Run, eps: float | None) -> dict:
    path = run.dir / "probes.jsonl"
    if not path.exists():
        return {}
    probes = read_jsonl(path)
    sources = {rid: r["src"] for rid, r in run.rows.items()}
    tables = {m: {r["id"]: r["score"] for r in read_jsonl(run.dir / "qe" / f"{m}.jsonl")} for m in (PRIMARY, ROBUST)
              if (run.dir / "qe" / f"{m}.jsonl").exists()}
    out = {}
    for probe in PROBES:
        ps = [p for p in probes if p["probe"] == probe]
        res = {"n": len(ps)}
        for m, t in tables.items():
            ds = []
            for p in ps:
                base = run.out.get((p["row_id"], "zero_shot"), {}).get("translation")
                a, b = t.get(item_id(sources[p["row_id"]], p["translation"])), t.get(item_id(sources[p["row_id"]], base or ""))
                if a is not None and b is not None:
                    ds.append(ORIENT[m] * (a - b))
            if ds:
                res[m] = {"mean_delta": float(np.mean(ds)), "share_lower": float(np.mean(np.asarray(ds) < 0)),
                          "share_drop_ge_eps": float(np.mean(np.asarray(ds) <= -eps)) if (eps and m == PRIMARY) else None}
        out[probe] = res
    return out


# ------------------------------------------------------------------------------------------- E. cost
def cost_report(run_dir: Path, rows: list[dict], cfg: dict) -> dict:
    out = latest_outputs(run_dir / "translations.jsonl")
    ids = {r["row_id"] for r in rows}
    per = defaultdict(lambda: {"rows": 0, "cost_usd": 0.0, "fresh_cost_usd": 0.0, "prompt_tokens": 0,
                               "completion_tokens": 0, "latency_s": 0.0, "errors": 0, "chars_billed": 0})
    for (rid, cond), o in out.items():
        if rid not in ids:
            continue
        p = per[cond]
        p["rows"] += 1
        p["errors"] += bool(o.get("error"))
        a = o.get("accounting") or {}
        p["cost_usd"] += a.get("cost_usd", 0.0) or 0.0
        p["fresh_cost_usd"] += 0.0 if a.get("cached") else (a.get("cost_usd", 0.0) or 0.0)
        p["prompt_tokens"] += a.get("prompt_tokens", 0) or 0
        p["completion_tokens"] += a.get("completion_tokens", 0) or 0
        p["latency_s"] += a.get("latency_s", 0.0) or 0.0
        p["chars_billed"] += a.get("chars_billed", 0) or 0
    ext = [e for e in read_jsonl(run_dir / "extractions.jsonl") if e["row_id"] in ids]
    per["extractor"] = {"rows": len(ext), "cost_usd": sum(c.get("cost_usd", 0) for e in ext for c in e.get("calls", [])),
                        "prompt_tokens": sum(c.get("prompt_tokens", 0) for e in ext for c in e.get("calls", [])),
                        "completion_tokens": sum(c.get("completion_tokens", 0) for e in ext for c in e.get("calls", [])),
                        "latency_s": sum(c.get("latency_s", 0) for e in ext for c in e.get("calls", []))}
    aud = {}
    for name in ("reuse", "extraction_audit", "mqm"):
        recs = read_jsonl(run_dir / f"{name}.jsonl")
        accs = [r["accounting"] for r in recs if r.get("accounting")]
        aud[name] = {"calls": len(accs), "cost_usd": sum(a.get("cost_usd", 0) for a in accs),
                     "prompt_tokens": sum(a.get("prompt_tokens", 0) for a in accs),
                     "completion_tokens": sum(a.get("completion_tokens", 0) for a in accs),
                     "via_batch": sum(bool(a.get("via_batch")) for a in accs)}
    for name in ("reuse", "extraction_audit", "mqm"):
        st = run_dir / f"batch_{name}.json"
        if st.exists():
            aud[name]["batch_usage"] = json.loads(st.read_text()).get("usage")
    n = len(ids)
    gen_total = sum(v["cost_usd"] for v in per.values())
    aud_total = sum(v["cost_usd"] for v in aud.values())
    test_rows = len(load_heldout(DATA_DIR, "test"))
    return {"rows": n, "generation": {k: dict(v) for k, v in per.items()}, "auditor": aud,
            "total_usd": gen_total + aud_total,
            "per_row_usd": {"generation": gen_total / max(1, n), "auditor": aud_total / max(1, n)},
            "projection_to_test_usd": {"rows": test_rows, "generation": gen_total / max(1, n) * test_rows,
                                       "auditor_reuse": aud.get("reuse", {}).get("cost_usd", 0) / max(1, n) * test_rows,
                                       "note": "Linear projection from this run's measured cost per row; noise-floor "
                                               "replicates and audit samples are fixed-size on test."}}


def cost_benefit(run: Run, qual: dict, costs: dict) -> dict:
    gen = costs["generation"]
    rows = max(1, costs["rows"])
    base = gen.get("zero_shot", {}).get("cost_usd", 0.0) / rows
    out = {}
    q = qual.get("ALL|all", {}).get("vs_zero_shot", {})
    for cond in CONTEXT + ["nmt_deepl"]:
        if cond not in gen:
            continue
        c = gen[cond]["cost_usd"] / rows + (gen["extractor"]["cost_usd"] / rows if cond == "structured_ctx" else 0.0)
        res = q.get(cond, {})
        net = res.get("net_share")
        out[cond] = {"usd_per_row": c, "extra_usd_per_row_vs_zero_shot": c - base,
                     "mean_prompt_tokens": gen[cond]["prompt_tokens"] / max(1, gen[cond]["rows"]),
                     "mean_latency_s": gen[cond].get("latency_s", 0) / max(1, gen[cond]["rows"]),
                     "net_meaningful_improvement_share": net,
                     "extra_usd_per_net_improvement": (c - base) / net if net and net > 0 else None}
    return out


# ------------------------------------------------------------------------------------------- outputs
def rows_analysis(run: Run, td: F.TermDensity) -> list[dict]:
    recs = []
    for (rid, cond), o in sorted(run.out.items()):
        r = run.rows[rid]
        c = run.cands[r["src_id"]]
        shown = o.get("candidate_tm_idx") or []
        reuse = {l["tm_idx"]: l for l in (run.reuse.get(rid, {}).get("labels") or [])}
        tm = run.tm(r["corpus"], r["lang"])
        recs.append({
            "row_id": rid, "src_id": r["src_id"], "corpus": r["corpus"], "lang": r["lang"], "split": r["split"],
            "src": r["src"], "band": r["band"], "fuzzy_best": r["fuzzy_best"], "cos_best": c["cos_best"],
            "src_words": len(r["src"].split()), "term_density": round(td.density(r["src"], r["corpus"]), 4),
            "condition": cond, "system": o.get("system"), "model": o.get("model"),
            "template_version": o.get("template_version"), "messages_sha": o.get("messages_sha"),
            "context_block": o.get("context_block"),
            "retrieved": [{"tm_id": tm[i]["tm_id"], "fuzzy": c["candidates"][str(i)]["fuzzy"],
                           "cos": c["candidates"][str(i)]["cos"], "reuse_label": reuse.get(i, {}).get("label"),
                           "verified_reusable": reuse.get(i, {}).get("verified_reusable")} for i in shown],
            "translation": o.get("translation"),
            "qe": run.scores.get((rid, cond), {}),
            "delta_vs_zero_shot": {m: run.delta(rid, cond, m) for m in run.metrics} if cond != "zero_shot" else None,
            "accounting": o.get("accounting"), "error": o.get("error"),
        })
    return recs


def mqm_sample(run_dir: Path, rows: list[dict], cfg: dict) -> list[dict]:
    """Blinded MQM items: per condition, half the largest |ΔQE| rows and half random rows (seeded)."""
    run = Run(run_dir, rows, cfg)
    per = cfg["auditor"]["mqm_sample_per_condition"]
    rng = random.Random(cfg["seed"])
    items = {}
    for cond in ["zero_shot", "hybrid_ctx", "structured_ctx", "draft_ctx", "fuzzy_ctx", "semantic_ctx", "nmt_deepl"]:
        rids = [rid for rid in run.rows if run.out.get((rid, cond), {}).get("translation")]
        scored = sorted((r for r in rids if run.delta(r, cond, PRIMARY) is not None),
                        key=lambda r: -abs(run.delta(r, cond, PRIMARY)))
        chosen = scored[: per // 2] if cond != "zero_shot" else []
        rest = [r for r in rids if r not in chosen]
        rng.shuffle(rest)
        chosen += rest[: per - len(chosen)]
        for rid in chosen:
            r, hyp = run.rows[rid], run.out[(rid, cond)]["translation"]
            iid = item_id(r["src"], hyp)
            items[iid] = {"item_id": iid, "src": r["src"], "hyp": hyp, "lang": r["lang"],
                          "domain": cfg["corpora"][r["corpus"]]["domain"]}
    return list(items.values())


def mqm_summary(run: Run) -> dict:
    if not run.mqm:
        return {}
    w = {"minor": 1, "major": 5, "critical": 10}
    out = {}
    for cond in run.conditions:
        pen, crit, n, cats = [], 0, 0, Counter()
        for rid, r in run.rows.items():
            o = run.out.get((rid, cond))
            if not o or not o.get("translation"):
                continue
            m = run.mqm.get(item_id(r["src"], o["translation"]))
            if not m or m.get("error"):
                continue
            n += 1
            pen.append(sum(w.get(e["severity"], 1) for e in m["errors"]))
            crit += any(e["severity"] in ("major", "critical") for e in m["errors"])
            cats.update(e["category"] for e in m["errors"])
        if n:
            out[cond] = {"n": n, "mean_penalty": float(np.mean(pen)), "rows_with_major_or_critical": crit,
                         "categories": dict(cats.most_common(8))}
    return out


def human_eval_export(run: Run, out_dir: Path, per_cell: int = 4) -> int:
    rng = random.Random(run.cfg["seed"] + 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    items, key = [], []
    cells = defaultdict(list)
    for rid, r in run.rows.items():
        cells[(r["corpus"], r["lang"], r["band"])].append(rid)
    for cell in sorted(cells):
        rids = sorted(cells[cell])
        rng.shuffle(rids)
        for rid in rids[:per_cell]:
            r = run.rows[rid]
            outs = {c: run.out.get((rid, c), {}).get("translation") for c in ("zero_shot", "hybrid_ctx", "structured_ctx", "draft_ctx", "nmt_deepl")}
            distinct = {}
            for c, h in outs.items():
                if h:
                    distinct.setdefault(h, []).append(c)
            hyps = list(distinct.items())
            rng.shuffle(hyps)
            for n, (h, conds) in enumerate(hyps):
                iid = item_id(r["src"], h)
                items.append({"item_id": iid, "segment_id": r["src_id"], "lang": r["lang"], "source": r["src"],
                              "translation": h, "option": chr(65 + n), "accuracy_0_100": "", "terminology_0_100": "",
                              "errors": "", "comments": ""})
                key.append({"item_id": iid, "row_id": rid, "band": r["band"], "conditions": "|".join(conds)})
    for name, rows in (("items.csv", items), ("key.csv", key)):
        with (out_dir / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    (out_dir / "README.md").write_text(
        "# Blinded human evaluation sample\n\nGive reviewers `items.csv` only. `key.csv` maps items to conditions "
        "and must stay with the analyst. Options are shuffled per segment; identical outputs from different "
        "conditions appear once. Score accuracy and terminology independently (0–100) and list errors "
        "(negation, numbers/units, omission, addition, terminology, fluency).\n", encoding="utf-8")
    return len(items)


# ------------------------------------------------------------------------------------------- report
def analyze(run_dir: Path, rows: list[dict], cfg: dict, log=print, noise_from: str | None = None) -> dict:
    run = Run(run_dir, rows, cfg)
    B = cfg["stats"]["bootstrap"]
    nf = noise_floor(run, cfg["qe"]["noise_floor_quantile"])
    if noise_from:
        frozen = json.loads((run_dir.parent / noise_from / "summary.json").read_text())["noise_floor"]
        nf = {**frozen, "source_run": noise_from, "this_run": nf}
    eps = nf.get("eps")
    log(f"noise floor ε = {eps}")
    td = F.TermDensity({c: [t["src"] for t in run.tm(c, cfg["corpora"][c]["targets"][0])] for c in cfg["corpora"]})
    rec = recovery(run)
    qual = quality(run, eps, B)
    band = by_band(run, eps, B)
    band_ref = {m: by_band(run, None, B, m) for m in REF_METRICS if m in run.metrics}
    cross = {m: crossover_analysis(run, B, m) for m in (PRIMARY, "comet22", "chrf") if m in run.metrics}
    fail = failure_analysis(run, eps)
    reg = regression(run, td, B)
    costs = cost_report(run_dir, rows, cfg)
    summary = {
        "run": run_dir.name, "n_rows": len(run.rows), "conditions": run.conditions, "metrics": run.metrics,
        "noise_floor": nf, "recovery": rec, "recovery_population_weighted_below75": population_weighted_below75(run, rec),
        "quality": qual, "by_band": band, "by_band_reference": band_ref, "crossover": cross, "failures": fail, "regression": reg,
        "qe_probes": probe_results(run, eps), "mqm": mqm_summary(run), "cost": costs,
        "cost_benefit": cost_benefit(run, qual, costs),
        "errors": {c: sum(1 for (rid, cc), o in run.out.items() if cc == c and o.get("error")) for c in run.conditions},
        "qe_coverage": {m: sum(1 for v in run.scores.values() if m in v) for m in run.metrics},
        "qe_bias": qe_bias(run),
    }
    write_json(run_dir / "summary.json", summary)
    with (run_dir / "rows_analysis.jsonl").open("w", encoding="utf-8") as f:
        for r in rows_analysis(run, td):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (run_dir / "examples.md").write_text(examples_md(run), encoding="utf-8")
    n_he = human_eval_export(run, run_dir / "human_eval")
    (run_dir / "report.md").write_text(render(summary, cfg), encoding="utf-8")
    log(f"wrote report.md, summary.json, rows_analysis.jsonl, examples.md, human_eval/ ({n_he} items)")
    return summary


def qe_bias(run: Run) -> dict:
    out = {}
    lr, q = [], []
    for (rid, cond), s in run.scores.items():
        o = run.out[(rid, cond)]
        if PRIMARY in s and cond in ("zero_shot", "nmt_deepl"):
            lr.append(F.length_ratio(run.rows[rid]["src"], o["translation"]))
            q.append(s[PRIMARY])
    if len(q) > 10:
        out["corr_kiwi_length_ratio_zs_nmt"] = float(np.corrcoef(lr, q)[0, 1])
    for band in ("100",):
        sel = [rid for rid, r in run.rows.items() if r["band"] == band]
        for cond in ("tm_as_is", "zero_shot", "nmt_deepl"):
            v = [run.good(r, cond, PRIMARY) for r in sel]
            v = [x for x in v if x is not None]
            if v:
                out[f"band100_mean_kiwi_{cond}"] = float(np.mean(v))
    # do the two QE metrics agree on condition-vs-zero-shot direction at segment level?
    agree = []
    for (rid, cond) in run.scores:
        if cond in COMPARE:
            a, b = run.delta(rid, cond, PRIMARY), run.delta(rid, cond, ROBUST)
            if a and b:
                agree.append(np.sign(a) == np.sign(b))
    if agree:
        out["segment_sign_agreement_kiwi_metricx"] = float(np.mean(agree))
    return out


def examples_md(run: Run, n: int = 6) -> str:
    lines = ["# Examples: largest QE changes vs zero-shot", "",
             "Selected by CometKiwi Δ. QE is a model estimate; these are pointers for manual inspection, not verdicts.", ""]
    for cond in [c for c in ("hybrid_ctx", "structured_ctx", "draft_ctx", "semantic_ctx", "fuzzy_ctx") if c in run.conditions]:
        scored = [(run.delta(rid, cond, PRIMARY), rid) for rid in run.rows]
        scored = sorted((x for x in scored if x[0] is not None), key=lambda x: x[0])
        for title, picks in (("Degradations", scored[:n]), ("Improvements", scored[::-1][:n])):
            lines += [f"## {cond}: {title}", ""]
            for d, rid in picks:
                r, o = run.rows[rid], run.out[(rid, cond)]
                z = run.out.get((rid, "zero_shot"), {}).get("translation")
                labels = run.reuse.get(rid, {}).get("labels") or []
                lab = {l["tm_idx"]: l["label"] for l in labels}
                tm = run.tm(r["corpus"], r["lang"])
                lines += [f"### {rid} ({r['corpus']}/{r['lang']}, band {r['band']}, fuzzy {r['fuzzy_best']:.0f}) ΔKiwi {d:+.3f}", "",
                          f"- **Source:** {r['src']}", f"- **Zero-shot:** {z}", f"- **{cond}:** {o['translation']}",
                          f"- **Reference (not shown to any system or evaluator):** {run.refs[rid]['ref']}"]
                for i in o.get("candidate_tm_idx") or []:
                    lines.append(f"- TM [{lab.get(i, '?')}]: {tm[i]['src']} → {tm[i]['tgt']}")
                if cond == "structured_ctx" and o.get("context_block"):
                    lines += ["", "```", o["context_block"], "```"]
                lines.append("")
    return "\n".join(lines)


def _pct(x, n):
    return f"{100 * x / n:.1f}%" if n else "–"


def _ci(ci, scale=100, nd=1):
    return f"[{ci[0] * scale:.{nd}f}, {ci[1] * scale:.{nd}f}]" if ci else ""


REF_SCALE = {"comet22": 100, "chrf": 1}  # COMET-22 is 0–1 (report ×100); chrF is already 0–100


def render_reference(s: dict) -> list[str]:
    """Section H: the same comparisons under reference-based metrics (independent human references)."""
    if not any(f"secondary_{m}" in b for b in s["quality"].values() for m in REF_METRICS):
        return []
    L = ["## H. Reference-based cross-check", "",
         "Paired Δ vs zero-shot under reference-based metrics (COMET-22 ×100; chrF points), 95% bootstrap CI. "
         "*clean* drops rows whose reference also occurs verbatim as a TM target (possible leakage via retrieval). "
         "On the test split COMET-22 covers a stratified subsample; chrF covers every row.", ""]
    for key, block in s["quality"].items():
        ms = [m for m in REF_METRICS if f"secondary_{m}" in block]
        if not ms:
            continue
        head = " | ".join(f"Δ{m} [CI] | n | Δ{m} clean [CI]" for m in ms)
        L += [f"### {key}", "", f"| condition | {head} |", "|---|" + "---:|---:|---:|" * len(ms)]
        for cond in COMPARE:
            cells = []
            for m in ms:
                sc = REF_SCALE[m]
                for variant in ("", "_clean"):
                    r = block[f"secondary_{m}{variant}"].get(cond) or {}
                    if not r.get("n"):
                        cells += ["–"] if variant else ["–", "0"]
                        continue
                    cell = f"{sc * r['mean']:+.2f} {_ci(r['ci'], sc)}"
                    cells += [cell, str(r["n"])] if not variant else [f"{cell} (n={r['n']})"]
            if any(c not in ("–", "0") for c in cells):
                L.append(f"| {cond} | " + " | ".join(cells) + " |")
        L.append("")
    for m, strata_ in (s.get("by_band_reference") or {}).items():
        sc = REF_SCALE[m]
        L += [f"### Δ{m} by fuzzy band", "", "(n in parentheses; * = 95% CI excludes 0)", ""]
        for name, bands in strata_.items():
            conds = [c for c in COMPARE if any(bands[b].get(c, {}).get("n") for b in BANDS)]
            L += [f"**{name}**", "", "| band | " + " | ".join(conds) + " |", "|---|" + "---:|" * len(conds)]
            for b in BANDS:
                cells = []
                for c in conds:
                    r = bands[b].get(c, {})
                    if not r.get("n"):
                        cells.append("–")
                        continue
                    sig = "*" if r["ci"] and (r["ci"][0] > 0 or r["ci"][1] < 0) else ""
                    cells.append(f"{sc * r['mean']:+.1f}{sig} ({r['n']})")
                L.append(f"| {b} | " + " | ".join(cells) + " |")
            L.append("")
    return L


def render(s: dict, cfg: dict) -> str:
    nf = s["noise_floor"]
    eps = nf.get("eps")
    L = [f"# LocRAG 2.0 run report: `{s['run']}`", "",
         f"Rows: **{s['n_rows']}**. Conditions: {', '.join(s['conditions'])}. Metrics: {', '.join(s['metrics'])}.",
         f"Primary metric: CometKiwi-22 (reference-free QE, 0–1, higher is better; Δ reported ×100). "
         + ("Robustness: MetricX-24-hybrid-large QE mode (lower is better; Δ sign-flipped so + = better)."
            if ROBUST in s["metrics"] else "Reference-based cross-checks: COMET-22 and chrF (section H)."), "",
         f"**Noise floor ε** (q={nf.get('quantile')} of |ΔKiwi| between two independent zero-shot generations that differ): "
         f"{'%.4f' % eps if eps is not None else 'n/a'} (differing regenerations n={nf.get('n_differing')} of {nf.get('n_pairs')}"
         f"{', frozen from ' + nf['source_run'] if nf.get('source_run') else ''}). "
         + ("A row is *meaningfully improved* when ΔKiwi ≥ ε and MetricX also improves (symmetrically for degraded)."
          if ROBUST in s["metrics"] else
          "A row is *meaningfully improved* when ΔKiwi ≥ ε (symmetrically for degraded). MetricX was not run on this "
          "split (single-QE-model decision); Kiwi/MetricX agreement is reported on the development run only."), ""]
    # A
    L += ["## A. TM recovery (H1)", "",
          "Denominator: held-out rows with a valid reuse classification. *Any reuse* = at least one TM unit shown "
          "under B/C/D with a Sonnet label in {full, partial, terminology, style_convention} **and** (except style) a cited "
          "target span found verbatim in the TM translation. *Substantive* = the same, restricted to full/partial. "
          "*Semantic-only* = the semantic top-k holds such material while the fuzzy top-k holds none. "
          "*Misleading* = at least one shown unit labelled misleading; *risk* = at least one unit with content that would "
          "be wrong if copied.", ""]
    for name, table in s["recovery"].items():
        if name == "ALL":
            continue
        L += [f"### {name}", "", "| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for band, t in table.items():
            b = t["best_label"]
            L.append(f"| {band} | {t['n']} | {_pct(t['semantic_coverage'], t['n'])} | {_pct(t['verified_reusable'], t['n'])} "
                     f"{_ci(t['verified_reusable_ci'])} | {_pct(t['substantive_reusable'], t['n'])} {_ci(t['substantive_reusable_ci'])} | "
                     f"{_pct(t['substantive_semantic_only'], t['n'])} | {_pct(t['rows_with_misleading_candidate'], t['n'])} | "
                     f"{_pct(t['rows_with_risk_flag'], t['n'])} | "
                     f"{b.get('full', 0)}/{b.get('partial', 0)}/{b.get('terminology', 0)}/{b.get('style_convention', 0)} |")
        L.append("")
    if s["recovery_population_weighted_below75"]:
        L += ["Below-75 recovery re-weighted to each corpus's natural 50–74 / <50 mix:", ""]
        L += [f"- {k}: any reuse {100 * v['weighted_rate']:.1f}%, substantive {100 * v['weighted_substantive_rate']:.1f}%"
              for k, v in s["recovery_population_weighted_below75"].items()]
        L.append("")
    # B
    L += ["## B. Translation quality vs zero-shot (H2)", "",
          "Paired ΔKiwi ×100 with 95% bootstrap CI (clustered by source when languages are pooled), Wilcoxon p "
          "(Holm-adjusted within each block), and the shares of rows meaningfully improved or degraded.", ""]
    for key, block in s["quality"].items():
        if not block["vs_zero_shot"]:
            continue
        L += [f"### {key}", "", "| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        zs = block["absolute"].get("zero_shot", {})
        L.append(f"| zero_shot | {zs.get('n', 0)} | {zs.get('mean', 0):.4f} | – | – | – | – | – | – |")
        for cond, r in block["vs_zero_shot"].items():
            if not r.get("n"):
                continue
            L.append(f"| {cond} | {r['n']} | {block['absolute'].get(cond, {}).get('mean', float('nan')):.4f} | "
                     f"{100 * r['mean']:+.2f} {_ci(r['ci'])} | "
                     f"{('%+.2f ' % r['robust_mean'] + _ci(r.get('robust_ci'), 1, 2)) if r.get('robust_mean') is not None else '–'} | "
                     f"{'%.3g' % r['p_holm'] if r.get('p_holm') is not None else '–'} | {_pct(r['share_identical'] * r['n'], r['n'])} | "
                     f"{_pct(r.get('improved', 0), r['n']) if eps else '–'} | {_pct(r.get('degraded', 0), r['n']) if eps else '–'} |")
        L.append("")
    # C
    L += ["## C. Quality change by fuzzy band", "", "Mean ΔKiwi ×100 vs zero-shot (n in parentheses; * = 95% CI excludes 0).", ""]
    for name, bands in s["by_band"].items():
        conds = [c for c in COMPARE if any(bands[b].get(c, {}).get("n") for b in BANDS)]
        L += [f"### {name}", "", "| band | " + " | ".join(conds) + " |", "|---|" + "---:|" * len(conds)]
        for b in BANDS:
            cells = []
            for c in conds:
                r = bands[b].get(c, {})
                if not r.get("n"):
                    cells.append("–")
                    continue
                star = "*" if r.get("ci") and (r["ci"][0] > 0 or r["ci"][1] < 0) else ""
                cells.append(f"{100 * r['mean']:+.1f}{star} ({r['n']})")
            L.append(f"| {b} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["### Crossover (H3)", "",
          "τ\\* = lowest best-fuzzy score where an isotonic fit of QE(TM-as-is) − QE(alternative) reaches ≥ 0. "
          "Best τ = threshold maximising mean QE of the pipeline 'TM-as-is if fuzzy ≥ τ, else alternative' "
          "(τ = 100 ≈ never use raw TM below exact matches).", "",
          "Computed under the primary QE metric and, as a cross-check against QE preferring MT-style output over human "
          "TM translations, under reference-based COMET-22 and chrF (references are independent human translations; "
          "rows whose reference also occurs as a TM target are not excluded here).", "",
          "| metric | stratum | alternative | τ* [95% CI] | best pipeline τ | bands where context beats zero-shot (CI > 0) |",
          "|---|---|---|---|---:|---|"]
    for metric, by_stratum in s["crossover"].items():
        for name, res in by_stratum.items():
            helps = "; ".join(f"{k}: {', '.join(v)}" for k, v in res.get("context_helps_bands", {}).items() if v) or "none"
            for n_alt, alt in enumerate(a for a in ("nmt_deepl", "zero_shot", "hybrid_ctx", "structured_ctx", "draft_ctx") if a in res):
                c = res[alt]["crossover"]
                L.append(f"| {metric} | {name} | {alt} | {c['tau'] if c['tau'] is not None else 'never'} "
                         f"{_ci(c['ci'], 1, 0) if c.get('ci') else ''} | {res[alt]['best_tau']} | {helps if n_alt == 0 else ''} |")
    L.append("")
    # D
    f = s["failures"]
    L += ["## D. Failure analysis", "", "### Heuristic detectors (counts of rows)", "",
          "| condition | n | number mismatch | negation mismatch | output contains TM-induced n-grams |", "|---|---:|---:|---:|---:|"]
    for cond, d in f["detectors"].items():
        L.append(f"| {cond} | {d['n']} | {d['number_mismatch']} | {d['negation_mismatch']} | {d['rows_with_tm_induced_ngrams']} |")
    L += ["", "### ΔKiwi by best verified reuse label of the context shown", ""]
    for cond, labs in f["delta_by_reuse_label"].items():
        L.append(f"- **{cond}:** " + "; ".join(f"{lab} n={v['n']} Δ={100 * v['mean_delta']:+.1f}"
                                                  + (f" (↑{v['improved']} ↓{v['degraded']})" if v.get("improved") is not None else "")
                                                  for lab, v in labs.items()))
    e = f["extractor"]
    a = e["audit"]
    L += ["", "### Structured-context extractor", "",
          f"- Rows {e['rows']}, parse failures {e['parse_errors']}, empty context (→ identical to zero-shot prompt) {e['empty_context_rows']}.",
          f"- Span items {e['span_items']}; verbatim-valid {e['span_items_verbatim_ok']} "
          f"({_pct(e['span_items_verbatim_ok'], e['span_items'])}); failure reasons {e['failure_reasons']}.",
          f"- Independent audit: {a['items']} items in {a['rows']} rows; mapping correct {_pct(a['mapping_correct'], a['items'])}, "
          f"applies to new source {_pct(a['applies'], a['items'])}; verbatim-valid but not applicable: {a['verbatim_ok_but_not_applies']}.", ""]
    L += ["### Does retrieval confidence predict benefit?", "", "AUC for predicting a meaningful improvement (ΔKiwi ≥ ε):", ""]
    for cond, p in f["benefit_predictors"].items():
        L.append(f"- **{cond}** (n={p['n']}, positives={p['positives']}): " +
                 ", ".join(f"{k} {v:.2f}" if v is not None else f"{k} –" for k, v in p["auc"].items()))
    if s["regression"]:
        L += ["", "### Descriptive regression of ΔKiwi on row features", ""]
        for cond, r in s["regression"].items():
            L.append(f"- **{cond}** (n={r['n']}): " + "; ".join(f"{c['term']} {c['coef']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}]"
                                                              for c in r["coefficients"][1:]))
        L.append("")
    if s["mqm"]:
        L += ["### MQM spans (Sonnet, blinded single-translation annotation; sampled, diagnostic)", "",
              "| condition | n | mean penalty | rows with major/critical | top categories |", "|---|---:|---:|---:|---|"]
        for cond, m in s["mqm"].items():
            L.append(f"| {cond} | {m['n']} | {m['mean_penalty']:.2f} | {m['rows_with_major_or_critical']} | {m['categories']} |")
        L.append("")
    # E
    L += ["## E. Cost–benefit", "", "| condition | $/row | extra $/row vs zero-shot | prompt tokens/row | latency s/row | net meaningful improvement | extra $ per net improvement |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    for cond, c in s["cost_benefit"].items():
        L.append(f"| {cond} | {c['usd_per_row']:.6f} | {c['extra_usd_per_row_vs_zero_shot']:.6f} | {c['mean_prompt_tokens']:.0f} | "
                 f"{c['mean_latency_s']:.2f} | {'%.1f%%' % (100 * c['net_meaningful_improvement_share']) if c['net_meaningful_improvement_share'] is not None else '–'} | "
                 f"{'$%.4f' % c['extra_usd_per_net_improvement'] if c['extra_usd_per_net_improvement'] else '–'} |")
    co = s["cost"]
    L += ["", f"Measured spend for this run: **${co['total_usd']:.4f}** (generation ${sum(v['cost_usd'] for v in co['generation'].values()):.4f}, "
          f"auditor ${sum(v['cost_usd'] for v in co['auditor'].values()):.4f}). DeepL characters billed: "
          f"{co['generation'].get('nmt_deepl', {}).get('chars_billed', 0):,}.", ""]
    # F
    L += render_reference(s)
    L += ["## F. Reliability", "", f"- Errors per condition: {s['errors']}.", f"- QE coverage (scored rows): {s['qe_coverage']}.",
          f"- QE bias checks: {json.dumps(s['qe_bias'])}."]
    if s["qe_probes"]:
        L += ["", "QE validity probes (controlled corruptions of zero-shot outputs; share where QE scored the corruption lower):", "",
              "| probe | n | Kiwi lower | Kiwi drop ≥ ε | mean ΔKiwi ×100 | MetricX lower |", "|---|---:|---:|---:|---:|---:|"]
        for p, r in s["qe_probes"].items():
            k, m = r.get(PRIMARY, {}), r.get(ROBUST, {})
            L.append(f"| {p} | {r['n']} | {_pct(k.get('share_lower', 0) * r['n'], r['n']) if k else '–'} | "
                     f"{_pct((k.get('share_drop_ge_eps') or 0) * r['n'], r['n']) if k.get('share_drop_ge_eps') is not None else '–'} | "
                     f"{100 * k.get('mean_delta', 0):+.1f} | {_pct(m.get('share_lower', 0) * r['n'], r['n']) if m else '–'} |")
    L += ["", "Limitations: QE is a learned estimate, not human judgment; reuse labels are automated (Sonnet + verbatim "
          "check); corpus translations proxy approved client TMs; there are no document IDs; one translator model.", ""]
    return "\n".join(L)
