# Architecture and decisions

`TMRouter.route()` produces a decision and exact examples. The CLI, corrected router evaluation and multilingual conditions consume this shared implementation.

| Module | Boundary |
|---|---|
| `retrievers.py` | Ranked hits without translation or evaluation policy |
| `pipeline.py` | Validated thresholds, routing, language/domain prompts, translation |
| `common/` | Provider calls, normalized embeddings, local caches |
| `evidence.py` | Deterministic aggregation; no inference imports |
| `multilingual.py` | Shared-source preparation and explicit new model runs |
| `demo/` | Static recorded evidence; no credentials or backend |

Embeddings load lazily. Strong fuzzy matches need no embedding download or call. Retrieval errors propagate rather than being disguised as no-match decisions. Empty translation responses and malformed judgments are rejected.

## Decisions

**Exact vector search:** a normalized matrix keeps a 5k/20k-entry experiment inspectable. Million-entry performance is not claimed. Larger indexes need measured latency/recall comparisons before approximate search is introduced.

**Fuzzy prefilter:** character similarity selects 100 candidates before word-level scoring. The new audit compares this with exhaustive scoring on all 300 KDE4 test queries. It missed 26 maxima but crossed no 75% decision boundaries in this sample; this does not prove it never changes decisions elsewhere.

**Separate outcomes:** relevant retrieval, accurate translation and client wording are different questions. Corpus translations proxy approved client memory and can contain errors.

**Conservative replay:** the demo preserves original outputs. Selective replay only uses recorded real-segment routes and substitutes saved zero-shot outputs for declines. It generates no new judgments and offers no arbitrary threshold counterfactuals.

**Shared multilingual sources:** English-source retrieval is common across targets. The experiment tests translation effects in Spanish, German and Simplified Chinese, not Chinese/German-source search.

## Limits

Provider aliases can change. A cache supports repeat inspection, not a guarantee of identical fresh inference. New manifests record code/data hashes, model IDs and parameters. Provider billing/token accounting is not instrumented; durations can include cache hits.

Original retrieval gold sets accept fuzzy near-duplicates without verified meaning-equivalence labels. The historical hybrid “meaning AUC” column uses a fuzzy-score proxy, not the fusion score; do not interpret it as an independently measured hybrid discrimination score.

KDE4 Moses exports lack document IDs. Numeric/placeholder grouping reduces overlap but does not establish document separation or eliminate semantic near-duplicates. The multilingual inference runs are complete; human review remains outstanding.
