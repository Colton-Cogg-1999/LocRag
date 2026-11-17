# Experiment B — RAG-MT on held-out EMEA (200 segments, k=3, MT: openai/gpt-5.4-mini, retrieval: openrouter:baai/bge-m3)

chrF++ (BLEU in parentheses). 'leverage' = top-1 TM target used as-is, no LLM.

| fuzzy band | n | zero-shot | +fuzzy ≥75% (CAT) | +fuzzy top-k | +semantic | +hybrid (RRF) | tiered (fuzzy≥85 else semantic) | leverage fuzzy | leverage semantic | shared examples |
|---|---|---|---|---|---|---|---|---|---|---|
| 95-99 | 40 | 70.1 (49.5) | 93.0 (89.4) | 92.1 (87.9) | 90.2 (84.8) | 91.9 (87.9) | 93.0 (89.4) | 92.0 (87.9) | 93.1 (89.5) | 1.57/3 |
| 85-94 | 40 | 74.3 (54.1) | 88.7 (80.0) | 87.5 (76.7) | 88.0 (77.7) | 87.7 (77.9) | 88.7 (80.0) | 77.6 (63.3) | 77.3 (62.8) | 1.55/3 |
| 75-84 | 40 | 71.1 (52.5) | 82.8 (69.9) | 83.6 (71.9) | 83.0 (73.0) | 81.6 (69.3) | 83.0 (73.0) | 69.7 (53.0) | 70.0 (55.9) | 1.32/3 |
| 50-74 | 40 | 74.8 (58.9) | 76.0 (58.5) | 78.4 (65.4) | 79.9 (66.2) | 79.4 (67.2) | 79.9 (66.2) | 52.5 (34.9) | 49.0 (26.2) | 0.72/3 |
| <50 | 40 | 68.1 (48.5) | 68.2 (49.3) | 66.6 (47.7) | 67.3 (46.6) | 71.2 (52.5) | 67.3 (46.6) | 26.5 (6.8) | 30.3 (6.0) | 0.38/3 |
| ALL | 200 | 71.4 (52.2) | 83.1 (72.3) | 82.9 (72.6) | 82.7 (72.2) | 83.6 (73.5) | 83.7 (73.5) | 67.2 (55.9) | 67.3 (53.5) | 1.11/3 |

Paired sentence-level chrF++ (margin 0.5) with exact sign test:

- semantic_vs_fuzzy_topk: {'semantic>fuzzy': 49, 'fuzzy>semantic': 51, 'tie': 100, 'sign_test_p': 0.9204}
- semantic_vs_fuzzy_cat75: {'semantic>fuzzy_cat75': 51, 'fuzzy_cat75>semantic': 53, 'tie': 96, 'sign_test_p': 0.9219}
- semantic_vs_zero_shot: {'semantic>zero_shot': 124, 'zero_shot>semantic': 40, 'tie': 36, 'sign_test_p': 0.0}
- tiered_vs_fuzzy_cat75: {'tiered>fuzzy_cat75': 43, 'fuzzy_cat75>tiered': 36, 'tie': 121, 'sign_test_p': 0.4999}