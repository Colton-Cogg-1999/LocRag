# Fuzzy Matching vs. Semantic Search in Localization Workflows

*An exploratory, comparative study of translation-memory retrieval for LLM-based machine translation
(EMEA corpus, English → Spanish).*

## Summary

Translation-memory (TM) lookup in CAT tools relies on fuzzy matching, an edit-distance score between the
new sentence and stored sentences. Below a match threshold, usually 75%, the tool shows the translator
nothing. This project tests what that threshold leaves out. It compares fuzzy matching with
embedding-based semantic search, first as retrievers and then as sources of in-context examples for an LLM
translator.

Main observations:

1. **Fuzzy matching does not recover reworded content.** On 160 controlled probes, the correct TM entry was
   ranked first in 25% (paraphrase) and 53% (restructured) of cases by fuzzy matching, against 95–100% for
   three embedding models. None of the paraphrased or restructured probes reached the 75% CAT threshold.
2. **Above about 85% fuzzy, semantic search adds nothing.** Translation quality with fuzzy-retrieved examples
   was equal to or better than with semantic examples. Over all bands the two did not differ significantly (p = 0.31).
3. **Below the threshold, semantic retrieval is measurably useful in some cases.** Of 300 real segments with no
   fuzzy match ≥ 75%, semantic search found a candidate (cosine ≥ 0.80) for 85 (28%). On those 85, a blind
   judge preferred translations that used the retrieved examples over zero-shot translations 50 : 13
   (p ≈ 3×10⁻⁶). Consistency with previously approved translations rose from 36 to 77 of 85, and accuracy did
   not change.
4. **The gain is consistency, not general quality.** A second judge that did not see the TM entry found no
   difference (30 : 25). chrF++ against the human reference rose 71.5 → 74.5, which is not significant at
   α = 0.05 (p ≈ 0.06).
5. **Neither retriever can tell same meaning from same words with opposite meaning.** In a stress test, the
   translation model still preserved polarity in 40/40 cases.

Taken together, the results suggest that semantic search complements fuzzy matching below the threshold
and does not replace it. All results come from one language pair, one domain and LLM judges (see
[Limitations](#limitations)).

## Research questions

* **RQ1 (retrieval).** How often does fuzzy matching find a TM entry that means the same thing as the new
  sentence but is worded differently, and how does embedding search compare?
* **RQ2 (translation, all bands).** When retrieved TM entries are given to an LLM as examples, how does
  translation quality depend on the retriever and on the fuzzy-match band of the segment?
* **RQ3 (translation, below threshold).** For real segments where a CAT tool shows no match, does adding
  semantically retrieved examples improve on the current baseline, which is zero-shot translation?
* **RQ4 (risk).** Do near-identical TM entries with the opposite meaning (for example, a negated sentence)
  mislead the retriever or the translator?

## Data and setup

| | |
|---|---|
| Corpus | OPUS **EMEA** (European Medicines Agency documents), en→es |
| Translation memory | 20,000 aligned units; held-out test segments drawn from the rest of the corpus, stratified by best fuzzy score |
| Fuzzy matcher | CAT-style word-level Levenshtein similarity (0–100) |
| Embeddings | **BGE-M3** (primary); text-embedding-3-large and Qwen3-embedding-8B for comparison |
| Hybrid | reciprocal-rank fusion of fuzzy and BGE-M3 rankings |
| Translator | **GPT-5.4 mini**, k ≤ 3 TM examples in the prompt |
| Judge | **Claude Sonnet 5.5**, blind A/B with randomized order |
| Metrics | Recall@k; chrF++ (and BLEU) against the human reference; judge preferences; paired exact sign tests |

All model calls went through OpenRouter and are cached on disk, so every number below can be reproduced from
the cache.

## Experiment 1: Retrieval probes (RQ1, RQ4)

**Method.** 40 TM units were each rewritten by hand in four ways: a small **edit**, a **paraphrase**, a
**restructure** (clauses reordered), and a **negation** (same words, opposite meaning). Each variant was used
as a query against the full 20k-unit TM. R@1 counts a hit if the original unit, or a ≥ 90% duplicate of it, is
ranked first. *Meaning AUC* is the probability that the retriever scores a same-meaning variant above the
negated one: 0.5 means it cannot tell them apart, and values below 0.5 mean it prefers the wrong meaning.

| retriever | edit R@1 | paraphrase R@1 | paraphrase R@5 | restructure R@1 | restructure R@5 | meaning AUC |
|---|---|---|---|---|---|---|
| fuzzy (word-level Levenshtein) | **1.00** | 0.25 | 0.38 | 0.53 | 0.62 | 0.01 |
| semantic: BGE-M3 | 0.97 | **0.97** | 1.00 | **1.00** | 1.00 | 0.63 |
| semantic: text-embedding-3-large | 0.97 | 0.95 | 1.00 | 1.00 | 1.00 | 0.49 |
| semantic: Qwen3-embedding-8B | 0.97 | 0.95 | 1.00 | 1.00 | 1.00 | 0.59 |
| hybrid (RRF, BGE-M3) | 1.00 | 0.45 | 0.90 | 0.68 | 0.97 | 0.01 |

Share of probes whose correct unit scored ≥ 75% fuzzy, i.e. would be displayed by a CAT tool:

| edit | paraphrase | restructure | negation |
|---|---|---|---|
| 100% | **0%** | **0%** | 82% |

**Observations**
* Fuzzy matching works well on small edits and poorly on everything else. The three embedding models perform
  almost the same, so the result does not depend on the choice of embedding model.
* The 75% threshold hides every paraphrase and restructure, even when the TM holds a translation of the same
  sentence.
* Fuzzy matching scores the *negated* sentence higher than a correct paraphrase (AUC 0.01). Embeddings are close
  to chance (0.49–0.63). Neither score can serve as a check that the meaning is the same.

Raw rows: `results/benchmarks/probes_rows.json`, summary: `results/benchmarks/probes_summary.md`.

## Experiment 2: Retrieval-augmented MT across fuzzy bands (RQ2)

**Method.** 200 held-out segments, 40 in each band of best fuzzy score. Each segment was translated with no
examples (zero-shot) and with top-3 examples from each retriever. The *CAT* condition passes only fuzzy matches
≥ 75%, as a CAT tool would. *Tiered* uses fuzzy matches when the best one is ≥ 85% and semantic matches
otherwise. Scores are chrF++ against the human reference.

| fuzzy band | zero-shot | CAT fuzzy ≥ 75% | fuzzy top-3 | semantic top-3 | hybrid | tiered |
|---|---|---|---|---|---|---|
| 95–99 | 71.2 | **92.9** | 92.2 | 92.1 | 91.8 | **92.9** |
| 85–94 | 74.3 | **89.2** | 87.3 | 87.2 | 88.2 | **89.2** |
| 75–84 | 71.2 | 82.2 | **82.9** | 82.6 | 82.3 | 82.6 |
| 50–74 | 75.6 | 75.6 *(nothing shown)* | 79.7 | **81.3** | 78.3 | **81.3** |
| < 50 | 67.1 | 67.1 *(nothing shown)* | 67.0 | 68.3 | **69.6** | 68.3 |
| **all** | 71.7 | 82.8 | 83.0 | 83.5 | 83.2 | **84.1** |

Paired sentence-level comparisons (chrF++ margin 0.5, exact sign test):

| comparison | wins / losses / ties | p |
|---|---|---|
| semantic vs zero-shot | 129 / 38 / 33 | < 0.001 |
| semantic vs CAT fuzzy ≥ 75% | 55 / 44 / 101 | 0.31 |
| semantic vs fuzzy top-3 | 50 / 42 / 108 | 0.47 |
| tiered vs CAT fuzzy ≥ 75% | 47 / 29 / 124 | 0.05 |

**Observations**
* Adding any TM examples is the largest effect (about +11 chrF++).
* The retrievers differ only below the threshold. In the 50–74% band, semantic examples score +5.7 over
  zero-shot, against +4.1 for fuzzy top-3. Below 50%, every condition stays within 2.5 points of zero-shot.
* The tiered rule scored highest overall, but the 85% cut-off was chosen *after* seeing the per-band results,
  so the comparison is exploratory and needs a fresh split to confirm.

Full table with BLEU and the "use the TM target unchanged" baselines: `results/benchmarks/rag_mt_summary.md`.

## Experiment 3: Real segments below the fuzzy threshold (RQ3, RQ4)

**Method.** This experiment covers only the case where a CAT tool currently gives the translator nothing:
300 real held-out segments whose best fuzzy match is < 75%. The baseline is zero-shot translation. The
treatment retrieves semantically and adds the matches as examples when the top cosine similarity is ≥ 0.80
(code: `TMRouter` in `locrag/pipeline.py`). Two blind A/B judges compared the outputs:

* a **localization rubric**: the judge sees the approved TM entry and judges accuracy first, then reuse of
  approved terminology and phrasing;
* a **generic rubric**: the judge does not see the TM entry and judges accuracy, then fluency.

Two constructed sets were added: 80 reworded TM entries (fuzzy score 0% to their source) and 40 *negated*
TM entries forced through retrieval as a stress test.

| set | n | top match reusable (judge) | loc. judge: RAG / tie / zero-shot | accurate: zero-shot → RAG | consistent with approved TM | generic judge: RAG / tie / zero-shot | chrF++ vs human ref |
|---|---|---|---|---|---|---|---|
| real, < 75%, semantic match ≥ 0.80 | 85 | 3 full + 62 partial | **50 / 22 / 13** | 84 → 82 | **36 → 77** | 30 / 30 / 25 | 71.5 → 74.5 |
| real, < 75%, all | 300 | 3 full + 151 partial | 147 / 117 / 36 | 286 → 290 | 157 → 271 | 90 / 113 / 97 | 71.9 → 73.2 |
| reworded TM entries | 80 | 53 full + 25 partial | 60 / 7 / 13 | 79 → 73 | 14 → 73 | 12 / 12 / 56 | n/a |
| negated TM entries (stress test) | 40 | 39 partial | 34 / 2 / 4 | 40 → 38 | 4 → 38 | 8 / 4 / 28 | n/a |

Breakdown of the 300 real segments:

| by best fuzzy score | n | sent to semantic | loc. judge: RAG / tie / zero-shot |
|---|---|---|---|
| 50–74% | 59 | 37 | **38 / 14 / 7** (p ≈ 3×10⁻⁶) |
| 30–49% | 127 | 36 | 52 / 59 / 16 |
| 0–29% | 114 | 12 | 57 / 44 / 13 |

| by top-1 semantic similarity | n | judged reusable | loc. judge: RAG / tie / zero-shot | chrF++ zero-shot → RAG |
|---|---|---|---|---|
| 0.90–1.00 | 17 | 17 | 13 / 3 / 1 | 68.8 → 75.1 |
| 0.85–0.90 | 17 | 12 | 12 / 3 / 2 | 70.5 → 71.5 |
| 0.80–0.85 | 51 | 36 | 25 / 16 / 10 | 72.5 → 75.2 |
| 0.75–0.80 | 70 | 45 | 38 / 22 / 10 | 69.9 → 71.5 |
| < 0.75 | 145 | 44 | 59 / 73 / 13 | 73.0 → 73.5 |

**Observations**
* Semantic search found a usable candidate for about a quarter of the segments that CAT tools would show
  nothing for. The 50–74% band ("near misses") benefits most.
* The two judges disagree in a consistent way. The localization judge, which values reuse of approved wording,
  prefers RAG. The generic judge sees no difference on real segments and prefers zero-shot on reworded ones,
  where approved phrasing sometimes fits the new wording awkwardly (12/80 rated less accurate by at least one
  judge, against 1/80 for zero-shot). Whether RAG "helps" therefore depends on what the workflow values.
* The 0.80 similarity cut-off is conservative. Segments at 0.75–0.80 still showed a judge preference (38 : 10).
* **Polarity risk.** With an opposite-meaning TM example in the prompt, the translator kept the correct polarity
  in 40/40 cases. In 1–2 cases it copied unrelated wording from the example. Experiment 1 shows that the
  retriever offers no protection here, so the translation model is the only safeguard.

Example (real segment, from `results/router/examples.md`):

| | |
|---|---|
| new segment | Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets. |
| best fuzzy match | 67%: *CoAprovel 150 mg/ 12.5 mg tablets.* (below threshold, not shown) |
| semantic match (0.92) | *Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 25 mg film-coated tablets.* → *Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 25 mg, comprimidos recubiertos con película.* |
| zero-shot | Irbesartán hidroclorotiazida Winthrop 300 mg/12,5 mg comprimidos. |
| with semantic examples | Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos. *(identical to the human reference)* |

Per-segment outputs and verdicts: `results/router/rows.jsonl`, report: `results/router/report.md`.

## Discussion

The results fit a simple division of labour. Fuzzy matching is precise when it fires, and above about 85% it is
as good as or better than embeddings for selecting examples. However, it is blind to rewording, and the 75%
threshold turns that blindness into an outright absence: the translator, or the LLM, receives nothing.
Semantic search fills part of that gap. Most of the measurable benefit is *consistency with previously
approved translations*, such as product names, house phrasing and formatting conventions, rather than better
translation in a general sense. That matters in regulated, terminology-heavy content like EMEA, where
approved wording carries weight. It may matter less in domains where fluency is the priority.

The negation results set the main limit. Neither edit distance nor cosine similarity measures whether two
sentences mean the same thing, so retrieval cannot double as verification. In this setup the LLM translator
handled misleading examples well, but that is a property of this model and should not be assumed for others.

## Limitations

* **One language pair and one domain** (en→es, EU pharmaceutical texts). EMEA is repetitive and
  formulaic, which probably favours TM reuse of any kind.
* **LLM judges.** Preferences come from one judge model with fixed rubrics. Human evaluation was not
  performed.
* **Single reference.** chrF++ uses one human reference, and the RQ3 chrF++ gain is not significant.
* **Hand-written probes** (n = 160) are small and written by one person.
* **Post-hoc thresholds.** The 85% tiered cut-off and the 0.80 similarity floor were not pre-registered. The
  similarity breakdown suggests 0.80 is not optimal.
* **One translation model** (GPT-5.4 mini). Robustness to misleading examples may differ in other models.

## Reproducing

```bash
uv sync
cp .env.example .env                    # OpenRouter key, or any OpenAI-compatible endpoint
uv run python -m common.check           # one small call per configured model

./scripts/download_emea.sh              # OPUS EMEA en-es → data/raw/EMEA
uv run python -m locrag.prepare_data    # 20k-unit TM + stratified held-out test set → data/tm/EMEA/

uv run python -m locrag.exp_retrieval   # Experiment 1 → results/benchmarks/probes_*
uv run python -m locrag.exp_rag_mt      # Experiment 2 → results/benchmarks/rag_mt_*
uv run python -m locrag.exp_router      # Experiment 3 → results/router/
```

To trace one segment through the setup (best fuzzy match, route, examples used, translation, and the zero-shot
translation for comparison):

```bash
uv run python -m locrag.pipeline "Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets."
```

Configuration (`.env`): `L10N_MT_MODEL` (translator), `L10N_JUDGE_MODEL`, `L10N_RETRIEVAL_MODEL`
(`openrouter:` prefix = hosted, otherwise local sentence-transformers), `L10N_FUZZY_THRESHOLD` (75),
`L10N_SEMANTIC_MIN_SIM` (80). LLM calls are cached in `.cache/`.

## Repository layout

```
locrag/
  retrievers.py     fuzzy (word-level Levenshtein), semantic (embeddings), hybrid (RRF)
  pipeline.py       fuzzy → semantic → LLM routing used in Experiment 3; single-segment CLI
  prepare_data.py   TM + stratified test set from OPUS EMEA
  exp_retrieval.py  Experiment 1          probes_emea.yaml  40 TM units × 4 hand-written variants
  exp_rag_mt.py     Experiment 2
  exp_router.py     Experiment 3
common/             OpenAI-compatible client with disk cache, embeddings, .env loader
results/            all raw outputs and summaries referenced above
```

## Data

EMEA parallel corpus from OPUS: J. Tiedemann, *Parallel Data, Tools and Interfaces in OPUS*, LREC 2012.
The download script fetches the corpus, which is not redistributed here. Result files include short excerpts
for illustration.

## License

MIT
