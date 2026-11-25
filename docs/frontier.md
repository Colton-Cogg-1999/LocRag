# Frontier replication · English to Spanish

**Question.** Does adding semantic retrieval to a strong lexical baseline improve below-cutoff English→Spanish translation when a frontier model sees the same examples as the earlier Gemma system?

Every retrieval arm here used a fixed set of examples. For the subsequent test of the selective policy across all six fuzzy bands, see the [production-router comparison](selective-router-results.md).

## Results

Across 100 paired segments, GPT-6.2 Sol consistently preferred hybrid on **3** and fuzzy on **4** for source meaning. Of the **87 ties**, 50 were character-identical and 37 were different translations judged equally accurate in both orders. The remaining **6** received different verdicts when the order was reversed. Net hybrid wins (wins minus losses divided by all segments) were **−1 percentage point**, with a paired, stratified bootstrap 95% interval of **[−6, +4]**. This panel resolves only fairly large differences in meaning preference. [Recorded summary](../results/frontier/summary.json)

| Examples shown to Astra | Mean chrF | EMEA medical (50) | KDE4 software (50) | Matched Gemma mean chrF |
|---|---:|---:|---:|---:|
| None | 76.06 | 76.61 | 75.51 | 73.63 |
| Random | 76.11 | 76.99 | 75.23 | — |
| Fuzzy | 76.74 | 76.21 | 77.26 | 77.61 |
| Semantic | 78.30 | 76.49 | 80.10 | 77.55 |
| Hybrid | 78.16 | 76.89 | 79.43 | 78.75 |

Random examples shifted mean segment chrF by **+0.05** relative to zero-shot [−1.12, +1.14]. Fuzzy retrieval gained **+0.62** over random [−0.84, +2.12]. Hybrid gained **+1.42** over fuzzy [−0.01, +2.93]. Intervals are pointwise, from 10,000 paired bootstrap resamples within the four sampling strata. Software strings account for most of the observed reference gain from semantic or hybrid context. The two domain columns are descriptive. The original Gemma run had four comparable arms. Cross-model scores reflect their respective generation settings.

### Follow-up analysis of the no-memory baseline

With the 75% cutoff enforced, every source in this panel would receive no TM suggestion. The saved zero-shot translation represents that policy for this experiment. Compared with that output on the same source, fuzzy context gained **+0.68** chrF [−0.78, +2.17], semantic context **+2.23** [+0.17, +4.49], and hybrid context **+2.10** [+0.40, +3.79]. These paired intervals were added after inspecting the run, using the same stratified bootstrap. The judge evaluated hybrid versus fuzzy only. For semantic versus zero-shot the descriptive mean difference was +4.59 chrF in KDE4 and −0.13 in EMEA.

### Three decisions behind the averages

- **Equivalent wording.** For “Host name used to generate the message ID,” fuzzy and hybrid both used *nombre del servidor*. One spelled out *identificador* and the other used *id.*. The judge accepted both in either order. [Translations and judgments](../results/frontier/rows/Keb459d31f97f-es.json)
- **Terminology the judge preferred.** For “sows and gilts,” fuzzy produced *cerdas adultas y nulíparas*. Hybrid produced *cerdas reproductoras y futuras reproductoras*. Both orders favored fuzzy for preserving the distinction in the source. The corpus reference also uses *adultas y nulíparas*. [Translations and judgments](../results/frontier/rows/Eab944dfd7377-es.json)
- **A reference match that merits human review.** For the JIS function’s “half-width argument,” hybrid wrote *argumento de media anchura*, matching the reference exactly. Fuzzy wrote *argumento de ancho medio*. The judge preferred hybrid in both orders without seeing the reference. This is a concrete string a bilingual software reviewer can check for an important ambiguity versus an acceptable synonym. [Translations and judgments](../results/frontier/rows/K6cbdfa706c51-es.json)

**Run accounting.** The published rows contain 490 unique Astra translations and 100 Sol judgments. Ten translation slots reused identical prompts. Successful requests amount to $1.69 at uncached standard rates. A checkout-directory rename interrupted the local ledger during seven calls. Their reservations bring the conservative run total to $2.07. Actual billing may be lower. The API reported the model aliases recorded in the row files.

## Protocol

**Design.** The frozen panel contains 25 previously tested sources from each combination of domain (EMEA medical text, KDE4 software) and best fuzzy band (<50, 50–74). Selection uses seed 20261124 and source identifiers before reading model outputs or references. Each stratum has equal weight. Reusing v2 sources supports a matched model replication. Generalization to unseen documents remains open. [Frozen inputs](../experiments/frontier/panel.jsonl)

| Arm | Evidence given to GPT-6.2 Astra |
|---|---|
| Zero-shot | Source and domain |
| Random | Three same-domain TM pairs, with English word counts matched position by position to fuzzy top-3; excludes the entries selected by any retrieval arm |
| Fuzzy | Three highest word-level fuzzy matches |
| Semantic | Three BGE-M3 nearest neighbors |
| Hybrid | Three entries from reciprocal-rank fusion of lexical and semantic neighbors |

The translator receives the v2 prompt, low reasoning effort, and one source per call. The three retrieved lists are frozen. The random arm controls for domain examples and approximate source length. Identical prompts reuse a single completion. The run records the served model and token usage. Sampling variability across generations is outside the scope of this panel.

**Primary contrast.** Compare hybrid and fuzzy on source meaning. Identical strings count as ties. For every changed pair, GPT-6.2 Sol sees the English source, domain and anonymous Spanish candidates in both orders. It cites evidence for a preference. Report hybrid wins, fuzzy wins, ties and order disagreements across all 100 rows. Order disagreements remain a separate outcome. Both models are from the same family. Bilingual human ratings would provide an independent check.

**Secondary endpoint.** Report mean segment chrF for all five conditions against the held-out corpus translation, plus a paired, stratified 95% bootstrap interval for hybrid minus fuzzy. Random versus zero-shot estimates the effect of showing in-domain examples. Fuzzy versus random estimates the incremental effect of lexical relevance. chrF measures reference agreement. A favorable score alone cannot establish meaning preservation or editing time saved.

## Matched historical baseline

The original Gemma translations on these exact 100 sources scored **73.63** mean segment chrF for zero-shot, **77.61** for fuzzy, **77.55** for semantic and **78.75** for hybrid. The historical run omitted random context. These are descriptive scores for the balanced Spanish panel. The larger multilingual comparison uses a different mix of segments. [Recorded baseline](../results/frontier/historical.json)

## Reproduction

The published panel suffices to run the five arms. Rebuilding the panel itself requires the prepared v2 data and frozen retrieval candidates described in the [v2 reproduction guide](v2-reproduction.md).

```bash
uv sync --locked
uv run python -m locrag.study.retriever_comparison   # offline, historical data
uv run python -m locrag.study.frontier baseline      # offline, matched historical scores
uv run python -m locrag.study.frontier pilot         # paid, four panel rows
uv run python -m locrag.study.frontier run           # paid, resumes pilot
uv run python -m locrag.study.frontier summarize     # offline, requires all 100 outputs
```

For paid stages, supply `OPENAI_API_KEY` in the local project environment. The runner contacts the direct OpenAI endpoint. It checks both model IDs before translation and uses the standard service tier. A local SQLite ledger at `.cache/frontier.sqlite` persists prompt hashes, usage and budget reservations. Preserve it across restarts. The study cap is $80 using uncached token rates, leaving $20 of the proposed budget available. Failed or interrupted requests retain their upper-bound reservations. The pilot covers one source in each stratum and carries forward into the full run. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

Each completed row is written under `results/frontier/rows/`. A complete run writes `results/frontier/summary.json`. To regenerate the frozen inputs after v2 preparation and retrieval, run `uv run python -m locrag.study.frontier_panel`.
