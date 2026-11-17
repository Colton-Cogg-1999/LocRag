# Audited historical evidence

historical exploratory evidence; not a fresh validation

Generated with `python -m locrag.evidence`; no inference is performed.

- Similarity threshold passed: **85/300**.
- Passing candidate judged reusable: **65/300** overall, or **65/85** among passing candidates.
- Localization preference in the passing subset: **50 wins / 22 ties / 13 losses**; two-sided exact sign test p=3.01595e-06 (ties excluded).
- Accuracy judgments: **84 → 82**. Accuracy equivalence has not been established.
- Corpus chrF++: **71.5 → 74.5**.
- Paired mean sentence chrF++ change: **3.90**, exploratory 95% bootstrap interval **[0.927, 7.2827]**. This interval describes mean sentence scores, not corpus chrF++.
- **168** original no-route rows have different RAG and zero-shot outputs.

## Translation experiment (original 200-segment study)

| Fuzzy band | n | Zero-shot | Thresholded fuzzy | Semantic | Tiered (post hoc) |
|---|---:|---:|---:|---:|---:|
| 95-99 | 40 | 71.2 | 92.9 | 92.1 | 92.9 |
| 85-94 | 40 | 74.3 | 89.2 | 87.2 | 89.2 |
| 75-84 | 40 | 71.2 | 82.2 | 82.6 | 82.6 |
| 50-74 | 40 | 75.6 | 75.6 | 81.3 | 81.3 |
| <50 | 40 | 67.1 | 67.1 | 68.3 | 68.3 |
| ALL | 200 | 71.7 | 82.8 | 83.5 | 84.1 |

## Interpretation limits

- The original evaluation always supplied at least one semantic example, even for route=none.
- The 85 passing real segments are a selected subset, not an independent validation set.
- Thresholds were chosen after exploratory analysis; frozen validation is still required.
- Generic and localization judgments use one model with different rubrics, not independent judges.
- The corpus acts as a proxy for approved client translations; corpus entries can contain errors.
- No dedicated, human-verified polarity labels support a 40/40 polarity-safety claim.
- Intervals resample segments and do not account for document dependence or judge error.

Source SHA-256 hashes, all summaries, and metric signature are in `summary.json`.
