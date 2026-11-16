# Results

Corpus: OPUS EMEA (EU medicines documentation), en→es. Translation memory: 20,000 units. All models via
OpenRouter: translation **GPT-5.4 mini**, embeddings **BGE-M3** (plus text-embedding-3-large and
Qwen3-embedding-8B for comparison), blind judge **Claude Sonnet 5.5**. Raw outputs in `results/`.

## 1. Router: semantic retrieval below the fuzzy threshold (`locrag/exp_router.py`, `results/router/`)

Router: best fuzzy match ≥ 75% → CAT path; below 75% → semantic search; matches with similarity ≥ 80 go into
the LLM prompt. Baseline = today's behaviour below the threshold: no TM context (zero-shot).

Two blind A/B judges (order randomised): a **localization rubric** (sees the approved TM entry; accuracy first, then
reuse of approved terminology/phrasing) and a **generic rubric** (no TM entry; accuracy, then fluency).

| set | n | top match reusable | loc judge: RAG / tie / zero-shot | accurate: zero-shot → RAG | consistent with approved TM: zero-shot → RAG | generic judge: RAG / tie / zero-shot | chrF++ vs human ref |
|---|---|---|---|---|---|---|---|
| real segments, fuzzy < 75%, routed to semantic | 85 | 3 full + 62 partial | **50 / 22 / 13** | 84 → 82 | **36 → 77** | 30 / 30 / 25 | **71.5 → 74.5** |
| real segments, fuzzy < 75%, all | 300 | 3 full + 151 partial | 147 / 117 / 36 | 286 → 290 | 157 → 271 | 90 / 113 / 97 | 71.9 → 73.2 |
| reworded TM entries (fuzzy shows 0%) | 80 | 53 full + 25 partial | 60 / 7 / 13 | 79 → 73 | 14 → 73 | 12 / 12 / 56 | n/a |
| negated TM entries, forced through RAG | 40 | 39 partial | 34 / 2 / 4 | 40 → 38 | 4 → 38 | 8 / 4 / 28 | n/a |

**Findings**
* Of 300 real new segments below 75% fuzzy, semantic search found a candidate (≥ 80) for **85 (28%)**, judged
  reusable for **65**. On those, the localization judge preferred RAG **50 : 13 (sign test p ≈ 3×10⁻⁶)**,
  consistency with approved translations rose **36 → 77 of 85**, accuracy was unchanged, and chrF++ against the
  human reference rose **71.5 → 74.5** (paired p ≈ 0.06).
* In the **50–74% fuzzy band**, which CAT tools discard, RAG was preferred **38 : 7** (p ≈ 3×10⁻⁶).
* The generic judge sees no difference (30 : 25): RAG's gain is consistency with previously approved translations,
  which is what a localization workflow wants, not generic fluency.
* **Risk:** with near-identical *opposite-meaning* TM examples in context, the MT model still preserved polarity in
  **40/40** cases; 1–2 outputs picked up unrelated wording from the example. On reworded sentences, approved phrasing
  occasionally doesn't fit (12/80 judged less accurate by at least one judge vs 1/80 zero-shot).

## 2. Retrieval probes (`locrag/exp_retrieval.py`, `results/benchmarks/probes_summary.md`)

40 TM units × 4 hand-written variants: *edit* (small change), *paraphrase*, *restructure*, *negation*.
R@1 = correct unit (or a ≥ 90% duplicate) ranked first.

| retriever | edit R@1 | paraphrase R@1 | paraphrase R@5 | restructure R@1 |
|---|---|---|---|---|
| fuzzy (CAT-style, word-level Levenshtein) | **1.00** | 0.25 | 0.38 | 0.53 |
| semantic: BGE-M3 | 0.97 | **0.97** | 1.00 | **1.00** |
| semantic: text-embedding-3-large | 0.97 | 0.95 | 1.00 | 1.00 |
| semantic: Qwen3-embedding-8B | 0.97 | 0.95 | 1.00 | 1.00 |

Share of probes whose correct unit reaches **75% fuzzy** (i.e. a CAT tool would display it): edit 100%,
**paraphrase 0%, restructure 0%**. Neither fuzzy nor embedding scores separate "same meaning" from "same words,
opposite meaning" (fuzzy ranks the negated sentence higher; embeddings are at chance), so retrieval is not verification.

## 3. RAG-MT across all fuzzy bands (`locrag/exp_rag_mt.py`, `results/benchmarks/rag_mt_summary.md`)

200 held-out segments, 40 per fuzzy band, k = 3 examples, chrF++ vs human reference.

| fuzzy band | zero-shot | fuzzy ≥ 75% (CAT) | fuzzy top-3 | semantic top-3 | tiered (fuzzy if ≥ 85%, else semantic) |
|---|---|---|---|---|---|
| 95–99 | 71.2 | **92.9** | 92.2 | 92.1 | **92.9** |
| 85–94 | 74.3 | **89.2** | 87.3 | 87.2 | **89.2** |
| 75–84 | 71.2 | 82.2 | 82.9 | 82.6 | 82.6 |
| 50–74 | 75.6 | 75.6 (nothing shown) | 79.7 | **81.3** | **81.3** |
| < 50 | 67.1 | 67.1 (nothing shown) | 67.0 | 68.3 | 68.3 |
| all | 71.7 | 82.8 | 83.0 | 83.5 | **84.1** |

* Any TM context vs none: +11 chrF++ (p < 0.001).
* Semantic vs CAT fuzzy over all bands: not significant (p = 0.31). Fuzzy is as good or better above 85%.
* Tiered routing scores best overall (84.1; vs CAT fuzzy 47 : 29 paired wins, p = 0.05). The 85% cut-off was chosen
  after seeing per-band results, so confirm on a fresh split.

**Conclusion:** use semantic retrieval as the fallback below the fuzzy threshold, not as a replacement for fuzzy matching.
