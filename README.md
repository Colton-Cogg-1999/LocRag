# LocRAG: Semantic Search for Localization Workflows

**When translation-memory fuzzy matching finds nothing usable, semantic search often can.**
LocRAG is a TM lookup router for LLM-based translation workflows: it keeps classic CAT-style fuzzy
matching where it works, and falls back to semantic retrieval (RAG) below the fuzzy threshold, feeding
previously approved translations into the LLM prompt instead of translating from scratch.

```
new segment ─► fuzzy TM lookup ─► best match ≥ 75% ─► CAT path: fuzzy matches → LLM context → translation
                               └─► best match < 75% ─► semantic search ─► similarity ≥ 80 ─► RAG: matches → LLM context
                                                                       └─► nothing close ──► zero-shot (flag for review)
```

Below a ~75% fuzzy score, CAT tools show the translator nothing, and the segment is billed as "no match".
But a reworded sentence, a new product strength or a reordered clause can have a perfectly reusable
approved translation that edit distance cannot see.

## Results

Evaluated on the EU medicines corpus EMEA (en→es): a 20,000-unit translation memory, 300 real new
segments whose best fuzzy match is below 75%, and controlled reworded/negated variants of TM entries.
Full write-up: [`RESULTS.md`](RESULTS.md).

| finding | evidence |
|---|---|
| Fuzzy matching can't find reworded content; semantic search can | correct TM entry ranked first: fuzzy **25–53%**, semantic **95–100%** (3 embedding models); **0%** of reworded variants reach the 75% CAT threshold |
| Below 75%, semantic retrieval yields better translations based on previous translations | on segments where semantic search found a match, a blind judge preferred the RAG translation **50 : 13** (p ≈ 3×10⁻⁶); consistency with approved TM **36 → 77 / 85**; accuracy unchanged; chrF++ vs human reference **71.5 → 74.5** |
| Strongest in the 50–74% band (thrown away by CAT tools today) | RAG preferred **38 : 7** |
| It's a fallback, not a replacement | above 85% fuzzy, fuzzy matching is as good or better; across all bands semantic vs fuzzy is not significant (p = 0.31) |

Example (real segment, `results/router/examples.md`):

| | |
|---|---|
| new segment | Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets. |
| best fuzzy match | 67%: *CoAprovel 150 mg/ 12.5 mg tablets.* → CAT shows nothing |
| semantic match (sim 92) | *Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 25 mg film-coated tablets.* → *Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 25 mg, comprimidos recubiertos con película.* |
| zero-shot (today) | Irbesartán hidroclorotiazida Winthrop 300 mg/12,5 mg comprimidos. |
| **LocRAG** | **Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos.** (identical to the human reference) |

## Quickstart

```bash
uv sync
cp .env.example .env              # paste an OpenRouter key (or point at any OpenAI-compatible endpoint)
uv run python -m common.check     # one tiny call per configured model

./scripts/download_emea.sh        # OPUS EMEA en-es corpus → data/raw/EMEA
uv run python -m locrag.prepare_data   # builds data/tm/EMEA/{tm,test}.jsonl (20k-unit TM + held-out test set)

uv run python -m locrag.pipeline "Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets."
```

The pipeline prints the best fuzzy match, the route taken, the TM examples used, and the translation
(plus the zero-shot translation for comparison when fuzzy matching failed).

### Experiments

| command | what it measures | output |
|---|---|---|
| `uv run python -m locrag.exp_router` | the router on 300 real below-threshold segments + reworded and negated probes; blind A/B judging (localization rubric and generic rubric) | `results/router/` |
| `uv run python -m locrag.exp_retrieval` | retrieval only: fuzzy vs 3 embedding models vs hybrid on 160 hand-written probes | `results/benchmarks/probes_*` |
| `uv run python -m locrag.exp_rag_mt` | RAG-MT quality across all fuzzy bands (zero-shot, CAT fuzzy ≥75%, fuzzy top-k, semantic, hybrid, tiered) | `results/benchmarks/rag_mt_*` |

All LLM calls are cached on disk (`.cache/`), so re-running is free.

## Configuration (`.env`)

| variable | default | role |
|---|---|---|
| `OPENROUTER_API_KEY` | (blank) | blank → local OpenAI-compatible server at `http://127.0.0.1:8081/v1` |
| `L10N_MT_MODEL` | `openai/gpt-5.4-mini` | translation model |
| `L10N_JUDGE_MODEL` | `anthropic/claude-sonnet-5.5` | blind A/B judge in experiments |
| `L10N_RETRIEVAL_MODEL` | `openrouter:baai/bge-m3` | embeddings (`openrouter:` prefix = hosted, otherwise local sentence-transformers) |
| `L10N_FUZZY_THRESHOLD` | `75` | CAT minimum match threshold |
| `L10N_SEMANTIC_MIN_SIM` | `80` | minimum cosine × 100 for a semantic match to be used |

## Layout

```
locrag/
  pipeline.py       TMRouter: fuzzy → semantic → LLM; CLI
  retrievers.py     CAT-style fuzzy (word-level Levenshtein), semantic (embeddings), hybrid (RRF)
  prepare_data.py   TM + stratified test set from OPUS EMEA
  exp_router.py     main evaluation (below-threshold segments)
  exp_retrieval.py  retrieval probes      probes_emea.yaml  40 TM units × 4 hand-written variants
  exp_rag_mt.py     RAG-MT across fuzzy bands
common/             OpenAI-compatible client with disk cache, embeddings, .env loader
results/            all outputs referenced in RESULTS.md
```

## Data

EMEA parallel corpus from OPUS: J. Tiedemann, *Parallel Data, Tools and Interfaces in OPUS*, LREC 2012.
The corpus is downloaded by `scripts/download_emea.sh` and not redistributed here; result files contain
short excerpts for illustration.

## License

MIT
