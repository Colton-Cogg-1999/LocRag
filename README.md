# LocRAG · When does translation memory help?

A localizer translating “Host name used to generate the message ID” might write *nombre del host* or *nombre del servidor*. A translation memory (TM) can show which wording appeared in earlier work. How much does it matter whether the examples come from lexical matching or semantic search?

## Frontier experiment

We translated the same 100 English medical and software segments into Spanish using GPT-6.2 Astra under five conditions. Giving the model three random examples from the same domain controls for the effect of seeing localized text. All 100 segments fell below the 75% fuzzy-match cutoff.

| Context | Mean segment chrF |
|---|---:|
| None | 76.06 |
| Three random, length-matched examples | 76.11 |
| Three lexical matches (fuzzy) | 76.74 |
| Three semantic matches (BGE-M3) | 78.30 |
| Three matches from the combined rankings (hybrid) | 78.16 |

**Did hybrid retrieval improve meaning over fuzzy retrieval?** A blinded GPT-6.2 Sol judge evaluated every changed pair in both orders. Hybrid won **3**, fuzzy won **4**, **87** tied and **6** changed verdict with order. Fifty pairs produced identical text. The net hybrid preference was **−1 percentage point** [95% interval −6, +4]. Hybrid scored **+1.42 chrF** over fuzzy [−0.01, +2.93]. Most of the observed gain in reference agreement came from software strings. The study uses model judgments on a balanced Spanish panel. [Protocol, results and worked examples](docs/frontier.md) · [Rebuildable numerical summary](results/frontier/summary.json)

## Earlier multilingual experiment

| Comparison | Result |
|---|---|
| Translate without examples vs supply the three closest fuzzy matches, even below the usual 75% cutoff | On 2,140 below-cutoff segments, fuzzy context gained 5.0 chrF points against corpus references. Reference-free CometKiwi fell by 0.52 points on a 100-point scale. |
| Replace fuzzy search with BGE-M3 semantic search or fuse the two rankings | All three methods gained roughly five chrF points over zero-shot below the cutoff. Hybrid retrieved a different ordered list from fuzzy on 2,040 segments. The translations differed on 933. |
| Extract reusable spans first or show the retrieved examples directly | Across the full v2 test, structured extraction gained 7.7 chrF over zero-shot. Direct hybrid context gained 10.4 and used fewer API dollars. |

![Share of segments with different retrieved examples and different translations, by domain and language](results/retriever-comparison/retrieval-and-translation.png)

### Does hybrid beat the fuzzy baseline?

Both systems used Gemma 4 31B, the same translation prompt, and three examples. The table gives the **paired difference, hybrid minus fuzzy**, on the below-cutoff subset of the band-stratified test. Confidence intervals use 10,000 bootstrap resamples of English source IDs, keeping each KDE source’s target languages together.

| Metric | Paired segments | Mean difference | 95% interval |
|---|---:|---:|---:|
| chrF | 2,140 | +0.07 | [−0.32, +0.45] |
| COMET-22 × 100 | 510 | +0.03 | [−0.19, +0.25] |
| CometKiwi × 100 | 2,140 | −0.003 | [−0.11, +0.11] |

The average differences are small and each interval spans zero. On the host-name example above, fuzzy context produced *Nombre del host usado para generar el ID del mensaje.* Hybrid produced *Nombre del servidor usado para generar el id. del mensaje.* chrF favored hybrid (83.2 vs 78.0), while CometKiwi favored fuzzy (0.868 vs 0.854). The corpus reference and a reference-free evaluator reward different features here. A bilingual reviewer could tell us which wording fits the interface.

**Limits.** The full v2 test contains 4,229 segment–language pairs from OPUS medical text and KDE interfaces. Band quotas affect pooled averages, sentence-level splits can share document conventions, and corpus references can contain errors. The earlier blinded 72-row judge study included hybrid, zero-shot, raw TM and DeepL. The frontier replication above directly compares fuzzy and hybrid context.

Rebuild the comparison and figure offline with `uv run python -m locrag.study.retriever_comparison`. [Machine-readable results](results/retriever-comparison/summary.json) · [Full study and error analysis](docs/v2-results.md) · [Original exploratory study](results/runs/2026-11-16/README.md)

## What's implemented

The v2 study lives in `locrag/study/` and runs as `python -m locrag.study`. It covers exact word-level fuzzy matching, band-stratified held-out sampling with leakage checks, a resumable cached OpenRouter client with provider and cost logging, a DeepL control, a blinded QE scorer in its own environment (`qe/`), the Sonnet reuse and extractor auditor with a credit guard, and paired bootstrap, crossover and failure analyses. See the [v2 reproduction guide](docs/v2-reproduction.md).

The Python pipeline combines fuzzy matching, semantic retrieval, and translation. It supports Spanish, German, and Simplified Chinese, and reports which route it used and which examples it supplied. Empty memories and rejected matches fall back to translation without examples.

The v1 evaluation code prepares matched language splits, runs the four approaches, and saves translations and judgments for inspection. The multilingual runs used GPT-5.4-mini for translation, Claude Sonnet 5.5 for judging, and BGE-M3 for embeddings. A/B presentation order was randomized. Tests cover routing and evidence reconstruction; GitHub Actions runs the offline checks.

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
