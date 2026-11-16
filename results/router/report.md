# Project 2: semantic retrieval where fuzzy matching fails (< 75%)

TM: 20,000 EMEA units (en→es). MT: **openai/gpt-5.4-mini**, k ≤ 3. Retrieval: **openrouter:baai/bge-m3**. Judge (blind A/B): **anthropic/claude-sonnet-5.5**. Semantic route used when top similarity ≥ 80.

Baseline = what happens today when the best fuzzy match is below threshold: the CAT/TMS offers nothing, so the LLM translates with no TM context (zero-shot).

## Headline

* Real new segments with fuzzy < 75%: **300**. Semantic search found a candidate ≥ 80 for **85 (28%)**; the judge rated the top match reusable (full/partial) for **65** of them.
Two blind judges: **localization rubric** (sees the approved TM entry; accuracy first, then reuse of approved terminology/phrasing) and **generic rubric** (no TM entry; accuracy then general fluency).

| set | n | top match reusable? | **loc judge:** RAG wins / tie / zero-shot wins | accurate: zero-shot → RAG | consistent w/ approved TM: zero-shot → RAG | generic judge: RAG / tie / zero-shot | chrF++ vs human ref | chrF++ vs approved TM translation |
|---|---|---|---|---|---|---|---|---|
| real, fuzzy < 75%, routed to semantic | 85 | 3 full + 62 partial | **50** / 22 / 13 | 84 → **82** | 36 → **77** | 30 / 30 / 25 | 71.5 → **74.5** | 43.6 → 50.8 |
| real, fuzzy < 75%, all (incl. weak semantic hits) | 300 | 3 full + 151 partial | **147** / 117 / 36 | 286 → **290** | 157 → **271** | 90 / 113 / 97 | 71.9 → **73.2** | 33.8 → 37.9 |
| constructed rewordings (fuzzy shows 0%) | 80 | 53 full + 25 partial | **60** / 7 / 13 | 79 → **73** | 14 → **73** | 12 / 12 / 56 | n/a (no reference) | 53.4 → 72.1 |
| **risk:** negated rewordings forced through RAG | 40 | 0 full + 39 partial | **34** / 2 / 4 | 40 → **38** | 4 → **38** | 8 / 4 / 28 | n/a (no reference) | 63.1 → 82.3 |

## Where does semantic retrieval stop helping? (real set, by top-1 similarity)

| top-1 similarity | n | reusable (full+partial) | loc judge: RAG / tie / zero-shot | accurate: zero-shot → RAG | chrF++ zero-shot → RAG |
|---|---|---|---|---|---|
| 90–100 | 17 | 17 | 13 / 3 / 1 | 17 → 17 | 68.8 → 75.1 |
| 85–90 | 17 | 12 | 12 / 3 / 2 | 17 → 16 | 70.5 → 71.5 |
| 80–85 | 51 | 36 | 25 / 16 / 10 | 50 → 49 | 72.5 → 75.2 |
| 75–80 | 70 | 45 | 38 / 22 / 10 | 69 → 69 | 69.9 → 71.5 |
| 0–75 | 145 | 44 | 59 / 73 / 13 | 133 → 139 | 73.0 → 73.5 |

## Fuzzy band of the real set

| best fuzzy | n | routed to semantic | loc judge: RAG / tie / zero-shot |
|---|---|---|---|
| 50–75% | 59 | 37 | 38 / 14 / 7 |
| 30–50% | 127 | 36 | 52 / 59 / 16 |
| 0–30% | 114 | 12 | 57 / 44 / 13 |