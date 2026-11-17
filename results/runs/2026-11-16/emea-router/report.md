# Project 2: semantic retrieval where fuzzy matching fails (< 75%)

TM: 20,000 EMEA units (en→es). MT: **openai/gpt-5.4-mini**, k ≤ 3. Retrieval: **openrouter:baai/bge-m3**. Judge (blind A/B): **anthropic/claude-sonnet-5.5**. Semantic route used when top similarity ≥ 80.

Baseline = what happens today when the best fuzzy match is below threshold: the CAT/TMS offers nothing, so the LLM translates with no TM context (zero-shot).

## Headline

* Real new segments with fuzzy < 75%: **300**. Semantic search found a candidate ≥ 80 for **85 (28%)**; the judge rated the top match reusable (full/partial) for **66** of them.
Policy: **router**. Risk probes deliberately force semantic context. Two rubrics from the same judge model: **localization rubric** (sees the TM entry; accuracy first, then reuse of approved terminology/phrasing) and **generic rubric** (no TM entry; accuracy then general fluency).

| set | n | top match reusable? | **loc judge:** RAG wins / tie / zero-shot wins | accurate: zero-shot → RAG | consistent w/ approved TM: zero-shot → RAG | generic judge: RAG / tie / zero-shot | chrF++ vs human ref | chrF++ vs approved TM translation |
|---|---|---|---|---|---|---|---|---|
| real, fuzzy < 75%, routed to semantic | 85 | 3 full + 63 partial | **50** / 26 / 9 | 83 → **82** | 31 → **75** | 25 / 28 / 32 | 71.7 → **74.8** | 43.4 → 51.6 |
| real, fuzzy < 75%, all decisions including declines | 300 | 3 full + 151 partial | **50** / 241 / 9 | 297 → **296** | 195 → **239** | 25 / 243 / 32 | 71.8 → **72.5** | 33.7 → 36.1 |
| constructed rewordings | 80 | 53 full + 25 partial | **56** / 13 / 11 | 79 → **71** | 11 → **67** | 24 / 15 / 41 | n/a (no reference) | 53.4 → 71.5 |
| **risk:** negated rewordings forced through RAG | 40 | 0 full + 39 partial | **35** / 4 / 1 | 39 → **39** | 7 → **39** | 6 / 6 / 28 | n/a (no reference) | 65.1 → 81.3 |

## Where does semantic retrieval stop helping? (real set, by top-1 similarity)

| top-1 similarity | n | reusable (full+partial) | loc judge: RAG / tie / zero-shot | accurate: zero-shot → RAG | chrF++ zero-shot → RAG |
|---|---|---|---|---|---|
| 90–100 | 17 | 17 | 12 / 4 / 1 | 16 → 15 | 67.1 → 75.8 |
| 85–90 | 17 | 12 | 10 / 5 / 2 | 17 → 17 | 72.9 → 70.6 |
| 80–85 | 51 | 37 | 28 / 17 / 6 | 50 → 50 | 72.5 → 75.8 |
| 75–80 | 70 | 45 | 0 / 70 / 0 | 70 → 70 | 70.6 → 70.6 |
| 0–75 | 145 | 43 | 0 / 145 / 0 | 144 → 144 | 72.4 → 72.4 |

## Fuzzy band of the real set

| best fuzzy | n | routed to semantic | loc judge: RAG / tie / zero-shot |
|---|---|---|---|
| 50–75% | 59 | 37 | 26 / 31 / 2 |
| 30–50% | 127 | 36 | 17 / 105 / 5 |
| 0–30% | 114 | 12 | 7 / 105 / 2 |