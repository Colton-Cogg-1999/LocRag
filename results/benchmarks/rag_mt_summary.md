# Experiment B — RAG-MT on held-out EMEA (200 segments, k=3, MT: openai/gpt-5.4-mini, retrieval: openrouter:baai/bge-m3)

chrF++ (BLEU in parentheses). 'leverage' = top-1 TM target used as-is, no LLM.

| fuzzy band | n | zero-shot | +fuzzy ≥75% (CAT) | +fuzzy top-k | +semantic | +hybrid (RRF) | tiered (fuzzy≥85 else semantic) | leverage fuzzy | leverage semantic | shared examples |
|---|---|---|---|---|---|---|---|---|---|---|
| 95-99 | 40 | 71.2 (51.0) | 92.9 (89.0) | 92.2 (87.7) | 92.1 (87.5) | 91.8 (87.3) | 92.9 (89.0) | 92.0 (87.9) | 93.1 (89.5) | 1.57/3 |
| 85-94 | 40 | 74.3 (55.1) | 89.2 (80.2) | 87.3 (76.5) | 87.2 (76.5) | 88.2 (78.5) | 89.2 (80.2) | 77.6 (63.3) | 77.3 (62.8) | 1.55/3 |
| 75-84 | 40 | 71.2 (51.9) | 82.2 (69.3) | 82.9 (70.9) | 82.6 (71.0) | 82.3 (70.1) | 82.6 (71.0) | 69.7 (53.0) | 70.0 (55.9) | 1.32/3 |
| 50-74 | 40 | 75.6 (59.6) | 75.6 (59.6) | 79.7 (67.1) | 81.3 (68.1) | 78.3 (65.3) | 81.3 (68.1) | 52.5 (34.9) | 48.8 (25.8) | 0.72/3 |
| <50 | 40 | 67.1 (48.0) | 67.1 (48.0) | 67.0 (46.0) | 68.3 (48.6) | 69.6 (49.5) | 68.3 (48.6) | 26.5 (6.8) | 30.3 (6.0) | 0.38/3 |
| ALL | 200 | 71.7 (52.8) | 82.8 (72.2) | 83.0 (72.0) | 83.5 (72.8) | 83.2 (73.0) | 84.1 (73.9) | 67.2 (55.9) | 67.3 (53.4) | 1.11/3 |

Paired sentence-level chrF++ (margin 0.5) with exact sign test:

- semantic_vs_fuzzy_topk: {'semantic>fuzzy': 50, 'fuzzy>semantic': 42, 'tie': 108, 'sign_test_p': 0.4657}
- semantic_vs_fuzzy_cat75: {'semantic>fuzzy_cat75': 55, 'fuzzy_cat75>semantic': 44, 'tie': 101, 'sign_test_p': 0.3149}
- semantic_vs_zero_shot: {'semantic>zero_shot': 129, 'zero_shot>semantic': 38, 'tie': 33, 'sign_test_p': 0.0}
- tiered_vs_fuzzy_cat75: {'tiered>fuzzy_cat75': 47, 'fuzzy_cat75>tiered': 29, 'tie': 124, 'sign_test_p': 0.0505}