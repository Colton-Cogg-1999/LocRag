# LocRAG · What a fuzzy-match cutoff hides

A translation memory (TM) stores earlier translations as bilingual examples. A localization tool using a 75% fuzzy-match cutoff can hide a useful phrase because the rest of its sentence has changed. LocRAG looks for that phrase by meaning when lexical matching falls below the cutoff.

**The cutoff hid reusable terminology. Simply showing the three closest fuzzy matches recovered much of its value.** LocRAG found terms those matches missed. On the held-out English→Spanish panel, the selective router had five fewer terminology passes and five more accuracy passes than unthresholded fuzzy retrieval. The paired estimates leave the overall advantage uncertain.

## A phrase worth recovering

In a medical packaging description, the best fuzzy match scored **41.67%**. The three closest lexical matches contained lists of tablet counts. GPT-6.2 Astra rendered “Starter pack” as *Envase de inicio* both without memory and with those matches. One semantic example cleared LocRAG’s threshold. With it, Astra used *Envase de iniciación*, the wording documented in two separate TM entries. All three translations passed the source-accuracy check. This is the kind of change a localizer cares about even when the meaning is already correct. [Case and counterexample](docs/selective-router-results.md#two-cases)

## From pilot to policy test

In the corrected Spanish medical pilot, all 300 sources fell below the fuzzy cutoff. Semantic search surfaced candidates on **85**. The automated auditor judged the top match fully or partly reusable on **66**. That established that the fallback could find useful material. It left a practical question open: how often would lifting the fuzzy cutoff achieve the same thing? [Corrected pilot results](results/runs/2026-11-16/emea-router/report.md)

The final study compared three policies on the same **480** English sources from OPUS medical text and software interfaces. GPT-6.2 Astra translated each source under each policy, using the same prompt template. The production LocRAG router accepts fuzzy examples at 75% or above, then falls back to semantic examples with cosine similarity of at least 0.80 if the best fuzzy match falls short. It translates without examples when neither route qualifies.

### Where the fuzzy cutoff hid every suggestion

| Outcome | No memory | Three closest fuzzy matches | Selective LocRAG |
|---|---:|---:|---:|
| Used the documented Spanish wording | 113/152 (74.3%) | 123/152 (80.9%) | 118/152 (77.6%) |
| Preserved source meaning | 158/160 (98.8%) | 149/160 (93.1%) | 154/160 (96.3%) |

All 160 below-cutoff sources counted toward accuracy. On 152, two independent historical entries supported a wording convention before scoring began. GPT-6.2 Sol graded anonymous translations separately for consistency and accuracy. Human post-editing time and client acceptance remain unmeasured.

LocRAG supplied semantic examples on **82** sources and abstained on **78**. Relative to no memory, it fixed eight terminology inconsistencies and introduced three. Both translations passed accuracy on all eleven changes. On four other sources the judge flagged a new meaning error. Compared with unthresholded fuzzy retrieval, LocRAG’s consistency difference was **−3.3 percentage points** (95% interval −8.4 to +1.4) and its accuracy difference was **+3.1 points** (−1.2 to +7.5). [Full results across six fuzzy bands](docs/selective-router-results.md) · [Prompts and selected examples](experiments/selective-router/panel.jsonl) · [Translations and judge evidence](results/selective-router/outputs.jsonl)

### Why score terminology separately?

An earlier experiment always supplied three semantic examples, even on sources where LocRAG would abstain. On 21 below-cutoff Gemma segments, semantic context fixed the terminology and both versions passed accuracy. The reference-free CometKiwi score registered a gain above the study’s noise threshold on only **two**. The archived multilingual benchmark and a second translator provide additional comparisons. [Consistency and QE analysis](docs/consistency-results.md) · [Multilingual benchmark](docs/v2-results.md) · [Always-on Astra replication](docs/frontier.md)

## Reproduce the headline table

From a checkout with Python 3.12+ and uv, rebuild the report from recorded outputs without API credentials:

```bash
uv sync --locked
uv run python -m locrag.study.selective_router summarize
uv run pytest -q
```

The below-cutoff table corresponds to `groups.low` in the [numerical summary](results/selective-router/summary.json). The [protocol](experiments/selective-router/protocol.md) describes route replay, the frozen judges’ instructions and fresh inference.

## Try the router

Configure the providers in a local `.env` using `.env.example`. Supply your own TM as JSONL with `src` and `tgt` fields, then run:

```bash
uv run python -m locrag.pipeline "Open the settings window." \
  --tm path/to/memory.jsonl --target de \
  --domain "software interface localization" --json
```

The CLI supports Spanish, German and Simplified Chinese and returns the route, the examples supplied and the translation. The historical Spanish demo lets readers inspect recorded examples offline. [Architecture](docs/architecture.md) · [Demo setup](docs/reproduction.md) · [Historical routing audit](results/audit/report.md)

## Data and license

Code is licensed under MIT. The medical and software corpora have their own terms. Saved evaluation artifacts include excerpts from each. The OPUS corpus citation is Jörg Tiedemann, *Parallel Data, Tools and Interfaces in OPUS*, LREC 2012. [OPUS EMEA](https://opus.nlpl.eu/legacy/EMEA.php) · [OPUS KDE4](https://opus.nlpl.eu/legacy/KDE4.php)
