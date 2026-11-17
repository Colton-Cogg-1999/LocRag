# LocRAG 2.0 run report: `dev-smoke`

Rows: **48**. Conditions: zero_shot, fuzzy_ctx, hybrid_ctx, nmt_deepl, semantic_ctx, structured_ctx, tm_as_is, zero_shot_repeat. Metrics: cometkiwi22, metricx24_qe, comet22, chrf.
Primary metric: CometKiwi-22 (reference-free QE, 0–1, higher is better; Δ reported ×100). Robustness: MetricX-24-hybrid-large QE mode (lower is better; Δ sign-flipped so + = better).

**Noise floor ε** (q=0.9 of |ΔKiwi| between two independent zero-shot generations that differ): 0.0289 (differing regenerations n=6 of 48). A row is *meaningfully improved* when ΔKiwi ≥ ε and MetricX also improves (symmetrically for degraded).

## A. TM recovery (H1)

Denominator: held-out rows with a valid reuse classification. *Any reuse* = at least one TM unit shown under B/C/D with a Sonnet label in {full, partial, terminology, style_convention} **and** (except style) a cited target span found verbatim in the TM translation. *Substantive* = the same, restricted to full/partial. *Semantic-only* = the semantic top-k holds such material while the fuzzy top-k holds none. *Misleading* = at least one shown unit labelled misleading; *risk* = at least one unit with content that would be wrong if copied.

### EMEA/es

| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 50.0% | 100.0% | 2/0/0/0 |
| 95-99 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 50.0% | 100.0% | 1/1/0/0 |
| 85-94 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 50.0% | 1/1/0/0 |
| 75-84 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 1/1/0/0 |
| 50-74 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 0/2/0/0 |
| <50 | 2 | 50.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 0.0% | 100.0% | 0/1/1/0 |
| below75 | 4 | 75.0% | 100.0% [51.0, 100.0] | 75.0% [30.1, 95.4] | 0.0% | 0.0% | 100.0% | 0/3/1/0 |
| all | 12 | 91.7% | 100.0% [75.8, 100.0] | 91.7% [64.6, 98.5] | 0.0% | 16.7% | 91.7% | 5/6/1/0 |

### KDE4/all

| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 6 | 100.0% | 100.0% [61.0, 100.0] | 100.0% [61.0, 100.0] | 0.0% | 0.0% | 100.0% | 6/0/0/0 |
| 95-99 | 6 | 100.0% | 83.3% [43.6, 97.0] | 83.3% [43.6, 97.0] | 0.0% | 16.7% | 100.0% | 3/2/0/0 |
| 85-94 | 6 | 100.0% | 100.0% [61.0, 100.0] | 100.0% [61.0, 100.0] | 0.0% | 66.7% | 100.0% | 0/6/0/0 |
| 75-84 | 6 | 50.0% | 100.0% [61.0, 100.0] | 100.0% [61.0, 100.0] | 0.0% | 0.0% | 100.0% | 0/6/0/0 |
| 50-74 | 6 | 0.0% | 100.0% [61.0, 100.0] | 50.0% [18.8, 81.2] | 0.0% | 33.3% | 100.0% | 0/3/3/0 |
| <50 | 6 | 50.0% | 100.0% [61.0, 100.0] | 50.0% [18.8, 81.2] | 0.0% | 50.0% | 100.0% | 0/3/2/1 |
| below75 | 12 | 25.0% | 100.0% [75.8, 100.0] | 50.0% [25.4, 74.6] | 0.0% | 41.7% | 100.0% | 0/6/5/1 |
| all | 36 | 66.7% | 97.2% [85.8, 99.5] | 80.6% [65.0, 90.2] | 0.0% | 27.8% | 100.0% | 9/20/5/1 |

### KDE4/de

| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 2/0/0/0 |
| 95-99 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 1/1/0/0 |
| 85-94 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 50.0% | 100.0% | 0/2/0/0 |
| 75-84 | 2 | 50.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 0/2/0/0 |
| 50-74 | 2 | 0.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 0.0% | 100.0% | 0/1/1/0 |
| <50 | 2 | 50.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 0/1/1/0 |
| below75 | 4 | 25.0% | 100.0% [51.0, 100.0] | 50.0% [15.0, 85.0] | 0.0% | 25.0% | 100.0% | 0/2/2/0 |
| all | 12 | 66.7% | 100.0% [75.8, 100.0] | 83.3% [55.2, 95.3] | 0.0% | 16.7% | 100.0% | 3/7/2/0 |

### KDE4/es

| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 2/0/0/0 |
| 95-99 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 1/1/0/0 |
| 85-94 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 50.0% | 100.0% | 0/2/0/0 |
| 75-84 | 2 | 50.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 0/2/0/0 |
| 50-74 | 2 | 0.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 0/1/1/0 |
| <50 | 2 | 50.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 0/1/0/1 |
| below75 | 4 | 25.0% | 100.0% [51.0, 100.0] | 50.0% [15.0, 85.0] | 0.0% | 50.0% | 100.0% | 0/2/1/1 |
| all | 12 | 66.7% | 100.0% [75.8, 100.0] | 83.3% [55.2, 95.3] | 0.0% | 25.0% | 100.0% | 3/7/1/1 |

### KDE4/zh_CN

| band | n | cos ≥ floor | any reuse [95% CI] | substantive [95% CI] | substantive, semantic-only | misleading | risk | best label (full/partial/term/style) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 2/0/0/0 |
| 95-99 | 2 | 100.0% | 50.0% [9.4, 90.5] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 1/0/0/0 |
| 85-94 | 2 | 100.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 100.0% | 100.0% | 0/2/0/0 |
| 75-84 | 2 | 50.0% | 100.0% [34.2, 100.0] | 100.0% [34.2, 100.0] | 0.0% | 0.0% | 100.0% | 0/2/0/0 |
| 50-74 | 2 | 0.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 0/1/1/0 |
| <50 | 2 | 50.0% | 100.0% [34.2, 100.0] | 50.0% [9.4, 90.5] | 0.0% | 50.0% | 100.0% | 0/1/1/0 |
| below75 | 4 | 25.0% | 100.0% [51.0, 100.0] | 50.0% [15.0, 85.0] | 0.0% | 50.0% | 100.0% | 0/2/2/0 |
| all | 12 | 66.7% | 91.7% [64.6, 98.5] | 75.0% [46.8, 91.1] | 0.0% | 41.7% | 100.0% | 3/6/2/0 |

Below-75 recovery re-weighted to each corpus's natural 50–74 / <50 mix:

- EMEA/es: any reuse 100.0%, substantive 66.7%
- KDE4/all: any reuse 100.0%, substantive 50.0%
- KDE4/de: any reuse 100.0%, substantive 50.0%
- KDE4/es: any reuse 100.0%, substantive 50.0%
- KDE4/zh_CN: any reuse 100.0%, substantive 50.0%

## B. Translation quality vs zero-shot (H2)

Paired ΔKiwi ×100 with 95% bootstrap CI (clustered by source when languages are pooled), Wilcoxon p (Holm-adjusted within each block), and the shares of rows meaningfully improved or degraded.

### EMEA/es|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 12 | 0.8605 | – | – | – | – | – | – |
| fuzzy_ctx | 12 | 0.8601 | -0.03 [-0.8, 1.0] | +0.12 [-0.14, 0.51] | 0.492 | 16.7% | 8.3% | 0.0% |
| semantic_ctx | 12 | 0.8603 | -0.02 [-0.8, 1.0] | +0.11 [-0.15, 0.51] | – | 41.7% | 8.3% | 0.0% |
| hybrid_ctx | 12 | 0.8611 | +0.06 [-0.7, 1.0] | +0.15 [-0.15, 0.57] | – | 25.0% | 8.3% | 0.0% |
| structured_ctx | 12 | 0.8573 | -0.32 [-1.2, 0.7] | -0.02 [-0.35, 0.44] | – | 25.0% | 8.3% | 0.0% |
| nmt_deepl | 12 | 0.8659 | +0.54 [0.1, 1.1] | +0.42 [-0.00, 1.00] | – | 25.0% | 0.0% | 0.0% |
| tm_as_is | 12 | 0.7417 | -11.88 [-17.9, -6.3] | -3.32 [-4.99, -1.85] | 0.000977 | 0.0% | 0.0% | 66.7% |

### EMEA/es|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 4 | 0.8622 | – | – | – | – | – | – |
| fuzzy_ctx | 4 | 0.8724 | +1.02 [-0.3, 3.3] | +0.51 [-0.05, 1.56] | – | 25.0% | 25.0% | 0.0% |
| semantic_ctx | 4 | 0.8733 | +1.11 [0.0, 3.3] | +0.52 [0.00, 1.56] | – | 75.0% | 25.0% | 0.0% |
| hybrid_ctx | 4 | 0.8721 | +0.99 [-0.3, 3.2] | +0.51 [-0.05, 1.58] | – | 50.0% | 25.0% | 0.0% |
| structured_ctx | 4 | 0.8721 | +0.99 [-0.3, 3.2] | +0.51 [-0.05, 1.58] | – | 50.0% | 25.0% | 0.0% |
| nmt_deepl | 4 | 0.8747 | +1.25 [0.3, 2.2] | +1.09 [-0.16, 2.34] | – | 0.0% | 0.0% | 0.0% |
| tm_as_is | 4 | 0.6795 | -18.27 [-28.7, -6.5] | -5.68 [-9.21, -2.06] | – | 0.0% | 0.0% | 75.0% |

### KDE4/all|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 36 | 0.8281 | – | – | – | – | – | – |
| fuzzy_ctx | 36 | 0.8144 | -1.37 [-2.6, -0.4] | -0.23 [-0.65, 0.07] | 0.24 | 19.4% | 2.8% | 11.1% |
| semantic_ctx | 36 | 0.8123 | -1.58 [-3.6, -0.2] | -0.36 [-0.93, 0.00] | 0.284 | 30.6% | 2.8% | 13.9% |
| hybrid_ctx | 36 | 0.8150 | -1.31 [-2.4, -0.4] | -0.26 [-0.68, 0.03] | 0.251 | 22.2% | 2.8% | 11.1% |
| structured_ctx | 36 | 0.8223 | -0.58 [-2.4, 1.2] | -0.28 [-0.69, -0.00] | 0.284 | 22.2% | 8.3% | 13.9% |
| nmt_deepl | 36 | 0.8335 | +0.54 [-0.7, 2.2] | +0.09 [-0.03, 0.23] | 0.595 | 13.9% | 5.6% | 5.6% |
| tm_as_is | 36 | 0.5647 | -26.35 [-35.8, -17.0] | -3.12 [-4.43, -1.94] | 4.37e-09 | 0.0% | 0.0% | 77.8% |

### KDE4/all|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 12 | 0.8468 | – | – | – | – | – | – |
| fuzzy_ctx | 12 | 0.8425 | -0.43 [-0.9, 0.0] | +0.08 [-0.01, 0.21] | – | 25.0% | 0.0% | 0.0% |
| semantic_ctx | 12 | 0.8425 | -0.43 [-0.9, -0.1] | -0.06 [-0.15, -0.00] | – | 50.0% | 0.0% | 8.3% |
| hybrid_ctx | 12 | 0.8397 | -0.71 [-1.1, -0.2] | -0.01 [-0.15, 0.09] | – | 33.3% | 0.0% | 0.0% |
| structured_ctx | 12 | 0.8412 | -0.56 [-2.1, 0.5] | -0.17 [-0.34, -0.04] | – | 33.3% | 0.0% | 8.3% |
| nmt_deepl | 12 | 0.8366 | -1.03 [-2.1, 0.1] | +0.16 [0.02, 0.33] | 0.465 | 8.3% | 0.0% | 8.3% |
| tm_as_is | 12 | 0.4199 | -42.70 [-52.2, -33.2] | -5.94 [-8.57, -3.74] | 0.000977 | 0.0% | 0.0% | 100.0% |

### KDE4/de|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 12 | 0.8072 | – | – | – | – | – | – |
| fuzzy_ctx | 12 | 0.8180 | +1.08 [-0.8, 4.3] | +0.17 [-0.02, 0.43] | 1 | 8.3% | 8.3% | 0.0% |
| semantic_ctx | 12 | 0.8112 | +0.40 [-2.1, 4.1] | +0.08 [-0.08, 0.34] | – | 25.0% | 8.3% | 16.7% |
| hybrid_ctx | 12 | 0.8168 | +0.97 [-0.8, 4.1] | +0.07 [-0.14, 0.35] | 0.967 | 16.7% | 8.3% | 0.0% |
| structured_ctx | 12 | 0.8172 | +1.01 [-2.1, 5.8] | +0.03 [-0.20, 0.33] | – | 25.0% | 8.3% | 8.3% |
| nmt_deepl | 12 | 0.8257 | +1.85 [-0.1, 5.4] | +0.17 [-0.03, 0.44] | 1 | 8.3% | 8.3% | 0.0% |
| tm_as_is | 12 | 0.5419 | -26.53 [-37.6, -15.3] | -2.03 [-3.79, -0.59] | 0.00586 | 0.0% | 0.0% | 75.0% |

### KDE4/de|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 4 | 0.8393 | – | – | – | – | – | – |
| fuzzy_ctx | 4 | 0.8358 | -0.35 [-1.2, 0.5] | +0.13 [-0.04, 0.46] | – | 0.0% | 0.0% | 0.0% |
| semantic_ctx | 4 | 0.8269 | -1.24 [-2.5, 0.0] | -0.04 [-0.09, 0.00] | – | 50.0% | 0.0% | 25.0% |
| hybrid_ctx | 4 | 0.8279 | -1.14 [-1.6, -0.4] | -0.15 [-0.46, 0.02] | – | 25.0% | 0.0% | 0.0% |
| structured_ctx | 4 | 0.8346 | -0.47 [-1.6, 0.2] | -0.19 [-0.55, 0.00] | – | 50.0% | 0.0% | 0.0% |
| nmt_deepl | 4 | 0.8408 | +0.15 [-0.4, 1.0] | +0.25 [0.06, 0.50] | – | 0.0% | 0.0% | 0.0% |
| tm_as_is | 4 | 0.4068 | -43.25 [-51.6, -34.9] | -4.99 [-7.62, -2.13] | – | 0.0% | 0.0% | 100.0% |

### KDE4/es|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 12 | 0.8528 | – | – | – | – | – | – |
| fuzzy_ctx | 12 | 0.8124 | -4.04 [-7.6, -1.2] | -0.68 [-1.78, 0.05] | 0.0176 | 16.7% | 0.0% | 25.0% |
| semantic_ctx | 12 | 0.8104 | -4.23 [-9.3, -0.5] | -0.98 [-2.50, -0.05] | – | 33.3% | 0.0% | 16.7% |
| hybrid_ctx | 12 | 0.8116 | -4.12 [-7.7, -1.3] | -0.70 [-1.79, 0.03] | 0.0195 | 16.7% | 0.0% | 25.0% |
| structured_ctx | 12 | 0.8184 | -3.44 [-7.2, -0.6] | -0.74 [-1.82, -0.02] | – | 25.0% | 0.0% | 16.7% |
| nmt_deepl | 12 | 0.8397 | -1.31 [-3.0, 0.4] | +0.20 [-0.00, 0.49] | 0.131 | 16.7% | 8.3% | 16.7% |
| tm_as_is | 12 | 0.5722 | -28.06 [-38.1, -17.9] | -4.45 [-7.47, -1.94] | 0.00195 | 0.0% | 0.0% | 91.7% |

### KDE4/es|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 4 | 0.8644 | – | – | – | – | – | – |
| fuzzy_ctx | 4 | 0.8537 | -1.06 [-1.9, -0.3] | +0.09 [-0.04, 0.29] | – | 0.0% | 0.0% | 0.0% |
| semantic_ctx | 4 | 0.8636 | -0.08 [-0.3, 0.1] | -0.14 [-0.38, 0.00] | – | 50.0% | 0.0% | 0.0% |
| hybrid_ctx | 4 | 0.8507 | -1.36 [-2.8, -0.3] | +0.07 [-0.03, 0.21] | – | 0.0% | 0.0% | 0.0% |
| structured_ctx | 4 | 0.8605 | -0.39 [-1.1, 0.1] | -0.13 [-0.38, 0.01] | – | 25.0% | 0.0% | 0.0% |
| nmt_deepl | 4 | 0.8289 | -3.55 [-6.4, -0.7] | +0.18 [-0.06, 0.62] | – | 0.0% | 0.0% | 25.0% |
| tm_as_is | 4 | 0.4346 | -42.98 [-53.9, -32.1] | -8.53 [-14.65, -3.34] | – | 0.0% | 0.0% | 100.0% |

### KDE4/zh_CN|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 12 | 0.8244 | – | – | – | – | – | – |
| fuzzy_ctx | 12 | 0.8129 | -1.15 [-4.0, 0.8] | -0.18 [-0.56, 0.06] | – | 33.3% | 0.0% | 8.3% |
| semantic_ctx | 12 | 0.8152 | -0.92 [-3.8, 0.9] | -0.18 [-0.57, 0.06] | – | 33.3% | 0.0% | 8.3% |
| hybrid_ctx | 12 | 0.8166 | -0.78 [-3.7, 1.1] | -0.16 [-0.55, 0.09] | – | 33.3% | 0.0% | 8.3% |
| structured_ctx | 12 | 0.8312 | +0.68 [-1.3, 3.2] | -0.13 [-0.30, -0.00] | 0.922 | 16.7% | 16.7% | 16.7% |
| nmt_deepl | 12 | 0.8350 | +1.07 [-0.1, 2.8] | -0.11 [-0.26, 0.02] | 0.129 | 16.7% | 0.0% | 0.0% |
| tm_as_is | 12 | 0.5799 | -24.45 [-35.1, -13.6] | -2.88 [-4.63, -1.24] | 0.00439 | 0.0% | 0.0% | 66.7% |

### KDE4/zh_CN|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 4 | 0.8368 | – | – | – | – | – | – |
| fuzzy_ctx | 4 | 0.8380 | +0.12 [0.0, 0.4] | +0.01 [0.00, 0.04] | – | 75.0% | 0.0% | 0.0% |
| semantic_ctx | 4 | 0.8372 | +0.04 [-0.2, 0.4] | +0.01 [-0.01, 0.04] | – | 50.0% | 0.0% | 0.0% |
| hybrid_ctx | 4 | 0.8404 | +0.36 [0.0, 1.1] | +0.04 [0.00, 0.12] | – | 75.0% | 0.0% | 0.0% |
| structured_ctx | 4 | 0.8284 | -0.84 [-3.4, 1.1] | -0.20 [-0.47, -0.02] | – | 25.0% | 0.0% | 25.0% |
| nmt_deepl | 4 | 0.8400 | +0.32 [-0.0, 0.7] | +0.05 [-0.01, 0.11] | – | 25.0% | 0.0% | 0.0% |
| tm_as_is | 4 | 0.4182 | -41.86 [-51.0, -32.7] | -4.29 [-6.07, -1.95] | – | 0.0% | 0.0% | 100.0% |

### ALL|all

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 48 | 0.8362 | – | – | – | – | – | – |
| fuzzy_ctx | 48 | 0.8259 | -1.04 [-2.0, -0.3] | -0.14 [-0.47, 0.11] | 0.174 | 18.8% | 4.2% | 8.3% |
| semantic_ctx | 48 | 0.8243 | -1.19 [-2.7, -0.1] | -0.24 [-0.69, 0.06] | 0.21 | 33.3% | 4.2% | 10.4% |
| hybrid_ctx | 48 | 0.8265 | -0.97 [-1.8, -0.2] | -0.16 [-0.49, 0.10] | 0.21 | 22.9% | 4.2% | 8.3% |
| structured_ctx | 48 | 0.8310 | -0.52 [-1.9, 0.8] | -0.22 [-0.54, 0.03] | 0.174 | 22.9% | 8.3% | 10.4% |
| nmt_deepl | 48 | 0.8416 | +0.54 [-0.4, 1.8] | +0.17 [0.02, 0.35] | 0.232 | 16.7% | 4.2% | 4.2% |
| tm_as_is | 48 | 0.6089 | -22.73 [-30.3, -15.0] | -3.17 [-4.21, -2.23] | 3.75e-12 | 0.0% | 0.0% | 75.0% |

### ALL|below75

| condition | n | mean Kiwi | ΔKiwi ×100 [CI] | ΔMetricX [CI] | p (Holm) | identical | improved | degraded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 16 | 0.8507 | – | – | – | – | – | – |
| fuzzy_ctx | 16 | 0.8500 | -0.07 [-0.6, 0.9] | +0.19 [-0.00, 0.48] | 1 | 25.0% | 6.2% | 0.0% |
| semantic_ctx | 16 | 0.8502 | -0.04 [-0.6, 0.9] | +0.09 [-0.10, 0.38] | – | 56.2% | 6.2% | 6.2% |
| hybrid_ctx | 16 | 0.8478 | -0.29 [-0.8, 0.8] | +0.12 [-0.09, 0.43] | 1 | 37.5% | 6.2% | 0.0% |
| structured_ctx | 16 | 0.8489 | -0.18 [-1.3, 1.0] | -0.00 [-0.24, 0.34] | 1 | 37.5% | 6.2% | 6.2% |
| nmt_deepl | 16 | 0.8461 | -0.46 [-1.4, 0.8] | +0.39 [0.05, 0.85] | 1 | 6.2% | 0.0% | 6.2% |
| tm_as_is | 16 | 0.4848 | -36.59 [-45.1, -24.1] | -5.87 [-7.99, -4.01] | 0.000153 | 0.0% | 0.0% | 93.8% |

## C. Quality change by fuzzy band

Mean ΔKiwi ×100 vs zero-shot (n in parentheses; * = 95% CI excludes 0).

### EMEA/es

| band | fuzzy_ctx | semantic_ctx | hybrid_ctx | structured_ctx | nmt_deepl | tm_as_is |
|---|---:|---:|---:|---:|---:|---:|
| 100 | -0.0 (2) | +0.0 (2) | +0.0 (2) | -1.2* (2) | +0.8 (2) | -4.5* (2) |
| 95-99 | -0.8* (2) | -0.9* (2) | -0.3* (2) | -1.2* (2) | -0.0 (2) | -10.1* (2) |
| 85-94 | -1.5* (2) | -1.5* (2) | -1.5* (2) | -1.5* (2) | -0.0 (2) | -7.0* (2) |
| 75-84 | +0.0 (2) | +0.0 (2) | +0.1* (2) | -0.1 (2) | -0.0 (2) | -13.1* (2) |
| 50-74 | +2.0 (2) | +2.2 (2) | +2.0 (2) | +2.0 (2) | +1.5* (2) | -7.9* (2) |
| <50 | +0.0 (2) | +0.0 (2) | +0.0 (2) | +0.0 (2) | +1.0* (2) | -28.7* (2) |

### KDE4/all

| band | fuzzy_ctx | semantic_ctx | hybrid_ctx | structured_ctx | nmt_deepl | tm_as_is |
|---|---:|---:|---:|---:|---:|---:|
| 100 | +0.3* (6) | +0.4* (6) | +0.4* (6) | +0.3* (6) | +0.0* (6) | -11.2* (6) |
| 95-99 | -1.3* (6) | -1.3* (6) | -1.3* (6) | -1.8* (6) | +0.4 (6) | -10.7* (6) |
| 85-94 | -3.5* (6) | -5.3 (6) | -3.1* (6) | -4.1* (6) | +0.4* (6) | -20.7* (6) |
| 75-84 | -2.8* (6) | -2.3 (6) | -2.3 (6) | +3.2 (6) | +4.4* (6) | -30.0* (6) |
| 50-74 | -0.9* (6) | -0.1 (6) | -1.0* (6) | -0.1 (6) | -0.8 (6) | -42.6* (6) |
| <50 | +0.0 (6) | -0.7* (6) | -0.5 (6) | -1.1 (6) | -1.2* (6) | -42.8* (6) |

### KDE4/de

| band | fuzzy_ctx | semantic_ctx | hybrid_ctx | structured_ctx | nmt_deepl | tm_as_is |
|---|---:|---:|---:|---:|---:|---:|
| 100 | +0.2 (2) | +0.2 (2) | +0.2 (2) | +0.2 (2) | +0.1* (2) | -9.2* (2) |
| 95-99 | -0.3* (2) | -0.3* (2) | -0.3* (2) | -0.2* (2) | +0.5 (2) | -5.6* (2) |
| 85-94 | -1.4 (2) | -3.7 (2) | -0.5 (2) | -5.0* (2) | -0.1* (2) | -33.8* (2) |
| 75-84 | +8.7 (2) | +8.7 (2) | +8.7 (2) | +12.0 (2) | +10.4 (2) | -24.1 (2) |
| 50-74 | -1.1* (2) | +0.0 (2) | -0.8 (2) | +0.0 (2) | -0.4* (2) | -42.2* (2) |
| <50 | +0.4 (2) | -2.5* (2) | -1.5* (2) | -0.9 (2) | +0.7* (2) | -44.3* (2) |

### KDE4/es

| band | fuzzy_ctx | semantic_ctx | hybrid_ctx | structured_ctx | nmt_deepl | tm_as_is |
|---|---:|---:|---:|---:|---:|---:|
| 100 | -0.0 (2) | +0.1 (2) | +0.1 (2) | +0.1 (2) | -0.1 (2) | -16.4* (2) |
| 95-99 | -2.9* (2) | -2.9* (2) | -2.9* (2) | -2.6* (2) | +1.6 (2) | -5.0* (2) |
| 85-94 | -10.9* (2) | -14.2* (2) | -10.9* (2) | -9.0* (2) | -0.0 (2) | -23.7* (2) |
| 75-84 | -8.3 (2) | -8.3 (2) | -8.3 (2) | -8.3 (2) | -2.3 (2) | -37.4* (2) |
| 50-74 | -1.5* (2) | -0.2 (2) | -2.1* (2) | -0.1 (2) | -2.5 (2) | -42.4* (2) |
| <50 | -0.6 (2) | +0.1 (2) | -0.6 (2) | -0.7 (2) | -4.6* (2) | -43.5* (2) |

### KDE4/zh_CN

| band | fuzzy_ctx | semantic_ctx | hybrid_ctx | structured_ctx | nmt_deepl | tm_as_is |
|---|---:|---:|---:|---:|---:|---:|
| 100 | +0.8* (2) | +0.8* (2) | +0.8* (2) | +0.8* (2) | +0.1 (2) | -8.1 (2) |
| 95-99 | -0.9 (2) | -0.9 (2) | -0.9 (2) | -2.5* (2) | -0.9 (2) | -21.6* (2) |
| 85-94 | +1.8 (2) | +1.8 (2) | +2.0* (2) | +1.6 (2) | +1.3* (2) | -4.7* (2) |
| 75-84 | -8.9* (2) | -7.3 (2) | -7.3 (2) | +5.9 (2) | +5.2* (2) | -28.6* (2) |
| 50-74 | +0.0 (2) | -0.2 (2) | +0.0 (2) | -0.2 (2) | +0.4 (2) | -43.3* (2) |
| <50 | +0.2 (2) | +0.2 (2) | +0.7 (2) | -1.5 (2) | +0.2 (2) | -40.5* (2) |

### Crossover (H3)

τ\* = lowest best-fuzzy score where an isotonic fit of QE(TM-as-is) − QE(alternative) reaches ≥ 0. Best τ = threshold maximising mean QE of the pipeline 'TM-as-is if fuzzy ≥ τ, else alternative' (τ = 100 ≈ never use raw TM below exact matches).

Computed under the primary QE metric and, as a cross-check against QE preferring MT-style output over human TM translations, under reference-based COMET-22 and chrF (references are independent human translations; rows whose reference also occurs as a TM target are not excluded here).

| metric | stratum | alternative | τ* [95% CI] | best pipeline τ | bands where context beats zero-shot (CI > 0) |
|---|---|---|---|---:|---|
| cometkiwi22 | KDE4/all | nmt_deepl | never [100, 100] | 97 | fuzzy_ctx: 100; semantic_ctx: 100; hybrid_ctx: 100; structured_ctx: 100 |
| cometkiwi22 | KDE4/all | zero_shot | never [100, 100] | 97 |  |
| cometkiwi22 | KDE4/all | hybrid_ctx | never [100, 100] | 97 |  |
| cometkiwi22 | KDE4/all | structured_ctx | never [100, 100] | 97 |  |
| comet22 | KDE4/all | nmt_deepl | never [80, 100] | 76 | fuzzy_ctx: 100, 85-94, 50-74; semantic_ctx: 85-94; hybrid_ctx: 85-94; structured_ctx: 95-99, 85-94 |
| comet22 | KDE4/all | zero_shot | never [80, 100] | 76 |  |
| comet22 | KDE4/all | hybrid_ctx | never [84, 100] | 91 |  |
| comet22 | KDE4/all | structured_ctx | never [80, 100] | 91 |  |
| chrf | KDE4/all | nmt_deepl | 75.0 [75, 86] | 76 | fuzzy_ctx: 100, 95-99, 85-94, 75-84, 50-74; semantic_ctx: 100, 95-99, 85-94; hybrid_ctx: 100, 95-99, 85-94; structured_ctx: 85-94 |
| chrf | KDE4/all | zero_shot | 75.0 [75, 86] | 76 |  |
| chrf | KDE4/all | hybrid_ctx | 85.71 [75, 100] | 81 |  |
| chrf | KDE4/all | structured_ctx | 75.0 [75, 100] | 76 |  |

## D. Failure analysis

### Heuristic detectors (counts of rows)

| condition | n | number mismatch | negation mismatch | output contains TM-induced n-grams |
|---|---:|---:|---:|---:|
| zero_shot | 48 | 0 | 1 | 0 |
| fuzzy_ctx | 48 | 0 | 0 | 26 |
| hybrid_ctx | 48 | 0 | 0 | 29 |
| nmt_deepl | 48 | 0 | 1 | 0 |
| semantic_ctx | 48 | 0 | 0 | 29 |
| structured_ctx | 48 | 0 | 1 | 31 |
| tm_as_is | 48 | 10 | 1 | 0 |

### ΔKiwi by best verified reuse label of the context shown

- **fuzzy_ctx:** full n=14 Δ=-0.4 (↑0 ↓1); partial n=26 Δ=-1.5 (↑3 ↓6); terminology n=4 Δ=-0.7 (↑0 ↓0); style_convention n=3 Δ=+0.2 (↑0 ↓0); misleading n=1 Δ=-2.3 (↑0 ↓0)
- **semantic_ctx:** full n=14 Δ=-0.4 (↑0 ↓1); partial n=20 Δ=-2.2 (↑3 ↓4); terminology n=12 Δ=-0.4 (↑0 ↓1); misleading n=2 Δ=-1.1 (↑0 ↓0)
- **hybrid_ctx:** full n=14 Δ=-0.3 (↑0 ↓1); partial n=22 Δ=-1.6 (↑3 ↓4); terminology n=9 Δ=-0.6 (↑0 ↓1); style_convention n=2 Δ=+0.2 (↑0 ↓0); misleading n=1 Δ=-2.3 (↑0 ↓0)
- **structured_ctx:** full n=14 Δ=-0.7 (↑0 ↓1); partial n=22 Δ=-0.3 (↑4 ↓3); terminology n=9 Δ=-0.5 (↑0 ↓1); style_convention n=2 Δ=-0.2 (↑0 ↓0); misleading n=1 Δ=-3.3 (↑0 ↓1)

### Structured-context extractor

- Rows 48, parse failures 0, empty context (→ identical to zero-shot prompt) 0.
- Span items 146; verbatim-valid 143 (97.9%); failure reasons {'target_in_historical': 3}.
- Independent audit: 224 items in 48 rows; mapping correct 89.3%, applies to new source 86.6%; verbatim-valid but not applicable: 20.

### Does retrieval confidence predict benefit?

AUC for predicting a meaningful improvement (ΔKiwi ≥ ε):

- **hybrid_ctx** (n=48, positives=3): fuzzy_best 0.46, cos_best 0.59, verified_label_rank 0.48, zero_shot_qe_low 0.90
- **structured_ctx** (n=48, positives=4): fuzzy_best 0.45, cos_best 0.62, verified_label_rank 0.48, zero_shot_qe_low 0.94
- **semantic_ctx** (n=48, positives=3): fuzzy_best 0.46, cos_best 0.59, verified_label_rank 0.50, zero_shot_qe_low 0.90

### Descriptive regression of ΔKiwi on row features

- **hybrid_ctx** (n=48): fuzzy_best/100 +0.055 [-0.120, +0.335]; cos_best -0.155 [-0.961, +0.294]; verified_reusable -0.006 [-0.046, +0.195]; misleading_shown -0.009 [-0.048, +0.164]; log_src_words +0.005 [-0.036, +0.121]; term_density +0.069 [-0.009, +0.239]; prompt_ktokens +0.043 [-0.465, +0.580]; zero_shot_qe -0.300 [-1.098, -0.028]; is_KDE4 -0.021 [-0.090, +0.004]
- **structured_ctx** (n=48): fuzzy_best/100 -0.011 [-0.209, +0.204]; cos_best -0.019 [-0.736, +0.455]; verified_reusable +0.005 [-0.043, +0.300]; misleading_shown +0.033 [-0.007, +0.300]; log_src_words +0.009 [-0.033, +0.132]; term_density +0.047 [-0.041, +0.150]; prompt_ktokens -0.197 [-1.188, +0.291]; zero_shot_qe -0.561 [-1.270, -0.068]; is_KDE4 -0.024 [-0.079, +0.006]

## E. Cost–benefit

| condition | $/row | extra $/row vs zero-shot | prompt tokens/row | latency s/row | net meaningful improvement | extra $ per net improvement |
|---|---:|---:|---:|---:|---:|---:|
| fuzzy_ctx | 0.000065 | 0.000031 | 310 | 1.13 | -4.2% | – |
| semantic_ctx | 0.000059 | 0.000025 | 308 | 1.11 | -6.2% | – |
| hybrid_ctx | 0.000056 | 0.000022 | 310 | 1.06 | -4.2% | – |
| structured_ctx | 0.000260 | 0.000226 | 265 | 1.03 | -2.1% | – |
| nmt_deepl | 0.000000 | -0.000034 | 0 | 0.05 | 0.0% | – |

Measured spend for this run: **$0.6177** (generation $0.0242, auditor $0.5935). DeepL characters billed: 3,337.

## F. Reliability

- Errors per condition: {'zero_shot': 0, 'fuzzy_ctx': 0, 'hybrid_ctx': 0, 'nmt_deepl': 0, 'semantic_ctx': 0, 'structured_ctx': 0, 'tm_as_is': 0, 'zero_shot_repeat': 0}.
- QE coverage (scored rows): {'cometkiwi22': 384, 'metricx24_qe': 384, 'comet22': 384, 'chrf': 384}.
- QE bias checks: {"corr_kiwi_length_ratio_zs_nmt": -0.007711583512894366, "band100_mean_kiwi_tm_as_is": 0.7675836607813835, "band100_mean_kiwi_zero_shot": 0.8630652129650116, "band100_mean_kiwi_nmt_deepl": 0.8654422163963318, "segment_sign_agreement_kiwi_metricx": 0.7081545064377682}.

QE validity probes (controlled corruptions of zero-shot outputs; share where QE scored the corruption lower):

| probe | n | Kiwi lower | Kiwi drop ≥ ε | mean ΔKiwi ×100 | MetricX lower |
|---|---:|---:|---:|---:|---:|
| number_change | 12 | 100.0% | 16.7% | -1.4 | 83.3% |
| drop_end | 40 | 100.0% | 100.0% | -28.6 | 100.0% |
| untranslated | 46 | 97.8% | 97.8% | -52.6 | 100.0% |
| append_unrelated | 48 | 97.9% | 97.9% | -21.5 | 97.9% |
| negation_removed | 15 | 100.0% | 93.3% | -12.6 | 100.0% |
| tm_swap | 8 | 100.0% | 100.0% | -32.6 | 100.0% |

Limitations: QE is a learned estimate, not human judgment; reuse labels are automated (Sonnet + verbatim check); corpus translations proxy approved client TMs; there are no document IDs; one translator model.
