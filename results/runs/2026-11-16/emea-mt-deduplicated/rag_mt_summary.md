# Experiment B — RAG-MT on held-out EMEA (200 segments, k=3, MT: openai/gpt-5.4-mini, retrieval: openrouter:baai/bge-m3)

chrF++ (BLEU in parentheses). 'leverage' = top-1 TM target used as-is, no LLM.

| fuzzy band | n | zero-shot | +fuzzy ≥75% (CAT) | +fuzzy top-k | +semantic | +hybrid (RRF) | tiered (fuzzy≥85 else semantic) | leverage fuzzy | leverage semantic | shared examples |
|---|---|---|---|---|---|---|---|---|---|---|
| 95-99 | 40 | 70.1 (49.5) | 92.9 (89.2) | 92.2 (88.1) | 91.3 (86.5) | 92.0 (88.0) | 92.9 (89.2) | 92.0 (87.9) | 93.1 (89.5) | 1.57/3 |
| 85-94 | 40 | 74.3 (54.1) | 88.7 (80.0) | 87.8 (77.1) | 88.1 (77.7) | 88.0 (78.3) | 88.7 (80.0) | 77.6 (63.3) | 77.3 (62.8) | 1.55/3 |
| 75-84 | 40 | 71.1 (52.5) | 82.8 (69.9) | 83.9 (72.7) | 83.0 (72.6) | 81.6 (68.9) | 83.0 (72.6) | 69.7 (53.0) | 70.0 (55.9) | 1.32/3 |
| 50-74 | 40 | 76.2 (59.0) | 76.2 (59.0) | 78.7 (65.6) | 79.8 (66.1) | 79.1 (66.7) | 79.8 (66.1) | 52.5 (34.9) | 49.0 (26.2) | 0.72/3 |
| <50 | 40 | 68.7 (49.7) | 68.7 (49.7) | 66.7 (47.9) | 67.3 (46.6) | 71.2 (52.5) | 67.3 (46.6) | 26.5 (6.8) | 30.3 (6.0) | 0.38/3 |
| ALL | 200 | 71.7 (52.5) | 83.2 (72.4) | 83.1 (72.9) | 83.0 (72.2) | 83.6 (73.5) | 83.6 (73.4) | 67.2 (55.9) | 67.3 (53.5) | 1.11/3 |

Paired sentence-level chrF++ (margin 0.5) with exact sign test:

- semantic_vs_fuzzy_topk: {'semantic>fuzzy': 44, 'fuzzy>semantic': 48, 'tie': 108, 'sign_test_p': 0.7547}
- semantic_vs_fuzzy_cat75: {'semantic>fuzzy_cat75': 49, 'fuzzy_cat75>semantic': 53, 'tie': 98, 'sign_test_p': 0.7666}
- semantic_vs_zero_shot: {'semantic>zero_shot': 122, 'zero_shot>semantic': 44, 'tie': 34, 'sign_test_p': 0.0}
- tiered_vs_fuzzy_cat75: {'tiered>fuzzy_cat75': 40, 'fuzzy_cat75>tiered': 37, 'tie': 123, 'sign_test_p': 0.8199}