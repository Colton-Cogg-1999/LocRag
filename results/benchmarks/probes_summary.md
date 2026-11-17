# Experiment A: retrieval probes (EMEA TM, 20k units, 40 items × 4 variants)

> Historical exploratory result. The hybrid meaning-AUC column uses the fuzzy-score proxy in the original evaluator, not the fusion score. Gold near-duplicates are accepted by fuzzy similarity and are not individually verified meaning equivalents. See [architecture notes](../../docs/architecture.md).

| retriever | edit R@1 | paraphrase R@1 | paraphrase R@5 | restructure R@1 | restructure R@5 | meaning AUC |
|---|---|---|---|---|---|---|
| fuzzy | 1.00 | 0.25 | 0.38 | 0.53 | 0.62 | 0.01 |
| semantic:bge-m3 | 0.97 | 0.97 | 1.00 | 1.00 | 1.00 | 0.63 |
| semantic:text-embedding-3-large | 0.97 | 0.95 | 1.00 | 1.00 | 1.00 | 0.49 |
| semantic:qwen3-embedding-8b | 0.97 | 0.95 | 1.00 | 1.00 | 1.00 | 0.59 |
| hybrid(bge-m3) | 1.00 | 0.45 | 0.90 | 0.68 | 0.97 | 0.01 |

Fraction of probes where the correct TM unit scores ≥75% fuzzy (i.e. a CAT tool would display it at all):

| edit | paraphrase | restructure | negation |
|---|---|---|---|
| 1.00 | 0.00 | 0.00 | 0.82 |

Mean retriever score of the original unit, by probe type:

- **fuzzy**: {'edit': 93.2, 'paraphrase': 22.8, 'restructure': 32.5, 'negation': 84.3}
- **semantic:bge-m3**: {'edit': 94.4, 'paraphrase': 86.8, 'restructure': 97.3, 'negation': 89.5}
- **semantic:text-embedding-3-large**: {'edit': 92.1, 'paraphrase': 80.6, 'restructure': 92.9, 'negation': 87.5}
- **semantic:qwen3-embedding-8b**: {'edit': 94.2, 'paraphrase': 89.2, 'restructure': 96.7, 'negation': 91.8}
- **hybrid(bge-m3)**: {'edit': 93.2, 'paraphrase': 22.8, 'restructure': 32.5, 'negation': 84.3}
