"""Paired statistics for the study. Deterministic given the seed."""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as sps

from locrag.evidence import wilson  # noqa: F401  (re-exported)


def bootstrap_mean_ci(values, clusters=None, B: int = 10000, seed: int = 2026, alpha: float = 0.05) -> dict:
    """Percentile bootstrap CI of the mean. With `clusters`, resamples whole clusters (e.g. one English
    source shared by three target languages) so dependent rows are not treated as independent."""
    v = np.asarray(values, dtype=float)
    n = len(v)
    if n == 0:
        return {"mean": None, "ci": None, "n": 0}
    rng = np.random.default_rng(seed)
    if clusters is None:
        idx = rng.integers(0, n, size=(B, n))
        means = v[idx].mean(axis=1)
    else:
        labels, inv = np.unique(np.asarray(clusters), return_inverse=True)
        sums = np.bincount(inv, weights=v, minlength=len(labels))
        counts = np.bincount(inv, minlength=len(labels)).astype(float)
        pick = rng.integers(0, len(labels), size=(B, len(labels)))
        means = sums[pick].sum(axis=1) / counts[pick].sum(axis=1)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return {"mean": float(v.mean()), "ci": [float(lo), float(hi)], "n": int(n)}


def wilcoxon_p(deltas) -> dict:
    d = np.asarray(deltas, dtype=float)
    nz = d[d != 0]
    if len(nz) < 10:
        return {"p": None, "n_nonzero": int(len(nz))}
    res = sps.wilcoxon(nz, zero_method="wilcox", alternative="two-sided")
    return {"p": float(res.pvalue), "n_nonzero": int(len(nz))}


def holm(pvals: dict) -> dict:
    """Holm–Bonferroni adjusted p-values for a family {name: p}; None p-values are passed through."""
    items = sorted(((p, k) for k, p in pvals.items() if p is not None))
    m, out, running = len(items), {k: None for k in pvals}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def paired_summary(deltas, clusters=None, B: int = 10000, seed: int = 2026, eps: float | None = None,
                   agree=None) -> dict:
    """Mean Δ with CI and Wilcoxon p; with eps, shares of meaningfully improved/degraded rows.
    `agree` (optional, same length): robustness-metric Δ oriented so that >0 means better; a row counts as
    meaningfully improved only if the primary Δ ≥ eps AND the robustness metric also improves."""
    d = np.asarray(deltas, dtype=float)
    out = {**bootstrap_mean_ci(d, clusters, B, seed), **wilcoxon_p(d)}
    out["share_identical"] = float(np.mean(d == 0)) if len(d) else None
    if eps is not None and len(d):
        up, down = d >= eps, d <= -eps
        if agree is not None:  # robustness metric must agree in direction
            a = np.asarray(agree, dtype=float)
            up, down = up & (a > 0), down & (a < 0)
        out.update(eps=eps, improved=int(up.sum()), degraded=int(down.sum()),
                   improved_share=float(up.mean()), degraded_share=float(down.mean()),
                   net_share=float(up.mean() - down.mean()))
    return out


def isotonic_increasing(x, y) -> tuple[np.ndarray, np.ndarray]:
    """Pool-adjacent-violators fit of y on x (non-decreasing). Returns (sorted x, fitted y)."""
    order = np.argsort(x, kind="stable")
    xs, ys = np.asarray(x, float)[order], np.asarray(y, float)[order]
    blocks = [[v, 1.0] for v in ys]  # [mean, weight]
    merged: list[list[float]] = []
    for b in blocks:
        merged.append(b)
        while len(merged) > 1 and merged[-2][0] > merged[-1][0]:
            m2, w2 = merged.pop()
            m1, w1 = merged.pop()
            merged.append([(m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2])
    fit = np.concatenate([np.full(int(w), m) for m, w in merged])
    return xs, fit


def crossover(x, d) -> float | None:
    """Smallest x at which the isotonic (non-decreasing) fit of d(x) reaches ≥ 0, i.e. where system 1 stops
    losing to system 2 as similarity rises. None if it never does."""
    if len(x) < 5:
        return None
    xs, fit = isotonic_increasing(x, d)
    hit = np.nonzero(fit >= 0)[0]
    return float(xs[hit[0]]) if len(hit) else None


def crossover_ci(x, d, B: int = 2000, seed: int = 2026) -> dict:
    x, d = np.asarray(x, float), np.asarray(d, float)
    point = crossover(x, d)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        c = crossover(x[i], d[i])
        boots.append(np.inf if c is None else c)
    boots = np.asarray(boots)
    finite = boots[np.isfinite(boots)]
    return {"tau": point, "n": int(len(x)), "share_boot_never": float(np.mean(~np.isfinite(boots))),
            "ci": [float(np.quantile(finite, .025)), float(np.quantile(finite, .975))] if len(finite) > 20 else None}


def threshold_sweep(fuzzy, score_tm, score_alt, taus=range(50, 101), B: int = 2000, seed: int = 2026) -> list[dict]:
    """Mean score of the pipeline 'use TM-as-is if fuzzy ≥ τ else alternative' for each τ."""
    f, t, a = (np.asarray(v, float) for v in (fuzzy, score_tm, score_alt))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(f), size=(B, len(f)))
    out = []
    for tau in taus:
        s = np.where(f >= tau, t, a)
        means = s[idx].mean(axis=1)
        out.append({"tau": tau, "mean": float(s.mean()), "ci": [float(np.quantile(means, .025)), float(np.quantile(means, .975))],
                    "share_tm": float(np.mean(f >= tau))})
    return out


def auc(scores, labels) -> float | None:
    """Mann–Whitney AUC of `scores` for binary `labels` (ties count half)."""
    s, y = np.asarray(scores, float), np.asarray(labels, bool)
    pos, neg = s[y], s[~y]
    if not len(pos) or not len(neg):
        return None
    ranks = sps.rankdata(np.concatenate([pos, neg]))
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def ols(X: np.ndarray, y: np.ndarray, names: list[str], B: int = 2000, seed: int = 2026,
        clusters=None) -> list[dict]:
    """OLS coefficients with (cluster) bootstrap CIs. Descriptive association, not causal effects."""
    X1 = np.column_stack([np.ones(len(y)), X])
    beta = np.linalg.lstsq(X1, y, rcond=None)[0]
    rng = np.random.default_rng(seed)
    boots = []
    if clusters is None:
        for _ in range(B):
            i = rng.integers(0, len(y), len(y))
            boots.append(np.linalg.lstsq(X1[i], y[i], rcond=None)[0])
    else:
        labels, inv = np.unique(np.asarray(clusters), return_inverse=True)
        members = [np.nonzero(inv == g)[0] for g in range(len(labels))]
        for _ in range(B):
            i = np.concatenate([members[g] for g in rng.integers(0, len(labels), len(labels))])
            boots.append(np.linalg.lstsq(X1[i], y[i], rcond=None)[0])
    boots = np.asarray(boots)
    return [{"term": n, "coef": float(b), "ci": [float(np.quantile(boots[:, j], .025)), float(np.quantile(boots[:, j], .975))]}
            for j, (n, b) in enumerate(zip(["intercept", *names], beta))]


def fmt(x, nd=3) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:+.{nd}f}" if isinstance(x, float) else str(x)
