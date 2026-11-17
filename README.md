# LocRAG

A translation memory—a collection of previously translated text—can contain useful translations even when fuzzy matching doesn't return a usable match. LocRAG uses semantic search to find that work and give it to a translation model as context, helping it reuse established terminology and phrasing.

I built this around a gap in translation-memory reuse: a sentence gets rewritten, its fuzzy score drops, and a relevant past translation falls below the matching cutoff. The wording has changed, but parts of the earlier translation may still be useful. LocRAG searches by meaning to recover those examples.

## What the experiments showed

**Semantic search recovered reusable translations below the fuzzy-matching cutoff. Using retrieved examples also produced more preferred translations than zero-shot translation in Spanish, German, and Simplified Chinese, with stronger terminology consistency.**

### Recovering translations that fuzzy matching missed

The most direct test used a 20,000-entry English-to-Spanish medical translation memory and 300 real sentences whose best fuzzy matches scored below the configured 75% cutoff.

Semantic search found candidates above its similarity threshold for **85 of those 300 sentences**. Of those, **66 were judged fully or partly reusable**: 3 full matches and 63 partial matches. In other words, roughly **22% of sentences that fell below the fuzzy cutoff still had useful translation material recoverable from the memory**.

That reuse could be a term, a phrase, or a sentence structure; it didn't require copying an entire translation. For those 85 sentences, supplying retrieved context increased terminology/phrasing consistency ratings from **31 to 75**. Across all 300 sentences, the selective system recorded **50 wins, 9 losses, and 241 ties** against translation without memory under the localization rubric.

This is the main result: semantic search makes more of an existing translation memory usable. The fuzzy and semantic comparisons help measure how much additional material can be recovered and whether it helps the translation.

### Using the recovered context to translate

In a separate test, I translated a shared set of 300 English software-localization sentences into Spanish, German, and Simplified Chinese, using a 5,000-entry translation memory for each language. The experiment compared four approaches: no memory, fuzzy matching only, always supplying semantic examples, and a selective system that tries fuzzy matching before semantic search.

Here is **always-on semantic RAG versus zero-shot translation**—the same translation model working without memory examples:

| Target language | RAG preferred | Zero-shot preferred | Tie |
|---|---:|---:|---:|
| Spanish | 103 | 49 | 148 |
| German | 110 | 52 | 138 |
| Simplified Chinese | 97 | 51 | 152 |
| **Total** | **310** | **152** | **438** |

RAG won **67% of comparisons with a clear winner**. Across all 900 cases, it won 34%, lost 17%, and tied 49%. The evaluator considered preservation of meaning first, then appropriate reuse of terminology and phrasing from the memory. All reuse, consistency, and preference results here are automated judgments, not human ratings.

### Adding semantic search to an existing matching workflow

The selective system keeps ordinary fuzzy matching as the first step. When its score falls below 75%, it searches by meaning and uses examples only if they clear a separate similarity threshold.

Adding that semantic fallback to the fuzzy-only system produced these results:

| Target language | Better with fallback | Worse with fallback | Tie |
|---|---:|---:|---:|
| Spanish | 14 | 8 | 278 |
| German | 20 | 3 | 277 |
| Simplified Chinese | 8 | 6 | 286 |

Fallback was used on 43 of the 300 English inputs. Fuzzy matching handled 22, and the remaining 235 received no memory examples, which explains most of the ties. German showed the clearest added benefit; the smaller Spanish and Chinese differences are less conclusive.

### What the results don't establish

More consistent wording doesn't guarantee more accurate meaning. Always-on semantic RAG introduced 61 meaning errors and fixed 59 across the three languages. In the medical experiment, a separate rubric that didn't reward memory consistency preferred RAG 25 times and zero-shot 32 times. Retrieved examples can also pull a translation toward details that don't belong in the new sentence.

This is evidence for a useful localization assistant, with human review still needed. It doesn't establish a general accuracy improvement or that semantic search should replace fuzzy matching. The experiments cover software and medical text, all with English source sentences. The medical reruns use previously studied inputs.

The [full results report](results/runs/2026-11-16/README.md) includes the remaining comparisons, failure cases, and links to raw outputs. The [multilingual summary](results/multilingual/validation-v1/summary.json) contains the numbers behind the tables above.

## What's implemented

The Python pipeline combines fuzzy matching, semantic retrieval, and translation. It supports Spanish, German, and Simplified Chinese, and reports which route it used and which examples it supplied. Empty memories and rejected matches fall back to translation without examples.

The evaluation code prepares matched language splits, runs the four approaches, and saves translations and judgments for inspection. The multilingual runs used GPT-5.4-mini for translation, Claude Sonnet 5.5 for judging, and BGE-M3 for embeddings. A/B presentation order was randomized. Tests cover routing and evidence reconstruction; GitHub Actions runs the offline checks.

An earlier experiment supplied semantic context even when its route label said `none`. That is fixed in the current pipeline and completed reruns. The [audit](results/audit/report.md) documents the issue, and the original outputs remain available so the correction can be traced.

## Run it

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
cp .env.example .env
```

Add your provider credentials to `.env`. Supply a translation memory as JSONL, with `src` and `tgt` fields on each line:

```json
{"src": "Open the file.", "tgt": "Öffnen Sie die Datei."}
```

Then translate a segment:

```bash
uv run python -m locrag.pipeline "Open the settings window." \
  --tm path/to/memory.jsonl --target de \
  --domain "software interface localization" --json
```

Supported targets are `es`, `de`, and `zh_CN`. For local embeddings, install the optional dependencies with `uv sync --extra local`.

To run the tests and rebuild the saved results summary without making model calls:

```bash
uv run pytest -q
uv run python scripts/summarize_run.py
```

The [reproduction guide](docs/reproduction.md) covers the original experiments, and the [multilingual protocol](docs/multilingual.md) covers data preparation and the three-language evaluation. The [architecture notes](docs/architecture.md) explain the code structure.

To browse saved examples from the original archived Spanish study, an optional local demo needs no API key:

```bash
uv run python -m locrag.demo
python -m http.server 8000 --bind 127.0.0.1 --directory demo/dist
```

Open http://127.0.0.1:8000. The completed results linked above cover the newer runs.

## Data and license

Code is licensed under MIT. Translation data comes from [OPUS EMEA](https://opus.nlpl.eu/legacy/EMEA.php) and [OPUS KDE4](https://opus.nlpl.eu/legacy/KDE4.php), credited to their contributors. The code license does not cover the corpora. Downloaded datasets are excluded from the repository; saved results contain excerpts used in the evaluation.

OPUS citation: Jörg Tiedemann, *Parallel Data, Tools and Interfaces in OPUS*, LREC 2012.
