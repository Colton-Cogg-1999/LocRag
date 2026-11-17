# LocRAG 2.0: technical assessment and study plan

Status: **Phase 1 (audit and design) complete; Phase 2 in progress.** Written 2026-11-16 before any v2 inference. Results in this document are from v1 runs only.

## 1. What exists (v1 audit)

| Component | Location | Assessment | v2 action |
|---|---|---|---|
| Data: EMEA en→es | `prepare_data.py`, `data/tm/EMEA` | 20k TM, 200 banded test, 300 below-75. Random split of unique sources, length and ratio filters. 223,237 unique pairs (4–60 words) are available. | Reuse the loader logic. Rebuild at 100k TM / 2k held-out with a new seed. |
| Data: KDE4 en→es/de/zh_CN | `multilingual.py prepare` | 42,461 shared English sources. Groups numeric/placeholder variants before splitting. 5k TM / 300 test. | Reuse the shared-source design. Rebuild at 30k TM / 800 held-out sources. |
| Fuzzy matching | `retrievers.cat_fuzzy`, `FuzzyRetriever` | Word-level Levenshtein %, similar to memoQ-style word matching. A character prefilter (top-100) **missed the true best match for 26/300 queries** (v1 audit). | Keep the definition. Replace the prefilter with an **exact** search: tokens are mapped to code points so rapidfuzz's C++ Levenshtein computes the word-level score over the whole TM. |
| Semantic retrieval | `SemanticRetriever` | Exact cosine over a normalized matrix. BGE-M3 via OpenRouter with an `.npy` cache. | Reuse as-is. |
| Hybrid retrieval | `HybridRetriever` | RRF of fuzzy and semantic plus a 95% fuzzy override. | Reuse the fusion over exact-fuzzy and semantic pools. |
| Translation | `pipeline.translate`, `common/llm.chat` | Text-only return: **no token usage, cost, provider or latency logging**. The cache key omits provider routing. | New client with usage, cost, served provider and model snapshot, plus retry/backoff. Old client untouched so v1 stays reproducible. |
| Evaluation | `exp_router`, `multilingual run` | **LLM pairwise preference** (same judge model, rubrics that reward TM consistency). | Superseded as primary evidence by independent QE. |
| Resumability | `multilingual run` | Not resumable: you have to start a new output directory. | Append-only JSONL per stage, keyed by `(row_id, stage, condition)`. Reruns skip completed keys. |
| Stats | `evidence.paired_mean_ci`, `sign_test`, `wilson` | Percentile bootstrap, sign test. | Reuse. Add cluster bootstrap, Wilcoxon signed-rank and Holm correction. |
| Tests/CI | `tests/`, `.github/workflows` | Offline unit tests. | Extend with leakage, blinding, fuzzy-exactness and stats tests. |

### Leakage review (v1)

1. **The evaluator saw the human reference.** `exp_router.PAIR_PROMPT`/`LOC_PROMPT` and the multilingual judge prompt include `Reference:` and the retrieved TM examples. Judgments were therefore not blind to the treatment's context, and the localization rubric explicitly rewarded TM consistency. **v2: the QE process receives only `(opaque_id, source, hypothesis)` and runs in a separate Python environment (`qe/`) that never imports the pipeline.**
2. **Retrieval and prompting never saw references.** Held-out `tgt` was not passed into prompts in v1. v2 enforces this structurally: references are written to a separate file that the translation stage never opens, and a unit test checks that rendered prompts don't contain reference strings.
3. **Reference and TM overlap.** A held-out reference can occur verbatim as a TM *target* for a different source. That's legitimate TM content, but it inflates reference-based scores for TM-reuse conditions. v2 flags `ref_in_tm_targets` and reports reference-based results with and without those rows.
4. **v1 route bug** (semantic context supplied when the route was `none`): already documented in `results/audit/`. v2 conditions are explicit and don't depend on route labels.

### What is preserved

All v1 results stay in `results/` unchanged as historical findings. v2 writes only under `results/study/`. The README will present v1 as historical findings with their known limits (LLM preference judging, small n).

## 2. Research questions (unchanged from the brief)

- **H1 (recoverability):** a meaningful share of held-out source segments whose best fuzzy match falls below conventional thresholds have *verified reusable* historical TM material.
- **H2 (quality):** giving Gemma 4 31B appropriately selected TM material improves reference-free QE relative to zero-shot.
- **H3 (crossover, added):** at what fuzzy score does inserting the raw TM target stop beating NMT (DeepL) and LLM translation, and at what score does LLM+TM context start beating zero-shot?

H1 and H2 are analysed separately. Recovering context doesn't imply a quality gain.

## 3. Data design

| Corpus | Domain | Targets | TM (retrieval corpus) | Held-out test | Dev (validation only) |
|---|---|---|---|---|---|
| OPUS EMEA v3 | medicinal product information | es | 100,000 | 2,000 | 120 |
| OPUS KDE4 v2 | software UI | es, de, zh_CN (shared English) | 30,000 | 800 sources × 3 = 2,400 | 60 × 3 = 180 |

**Total test: 4,400 segment-language rows.** The dev split is used for Phase 3 validation and any prompt or threshold fixes. Test outputs aren't inspected until the protocol is frozen.

**Band-stratified sampling.** Candidates are drawn from the non-TM pool (seeded shuffle). The exact best word-level fuzzy score against the full TM sets the band, and each band is filled up to a quota:

| Band | EMEA | KDE4 (sources) |
|---|---:|---:|
| 100 (exact baseline) | 100 | 50 |
| 95–99 | 250 | 100 |
| 85–94 | 300 | 120 |
| 75–84 | 350 | 150 |
| 50–74 | 500 | 190 |
| <50 | 500 | 190 |

The pool's natural band frequencies are recorded, so population-weighted estimates can be reported alongside per-band ones. If a band can't be filled, its actual n is reported, never padded.

**Exact-match band.** Sources are deduplicated before splitting, so true 100% matches only come from repeated sources. For the 100 band, we sample sources that occur in the raw corpus with **two or more distinct translations**: one goes into the TM, and the held-out copy keeps a *different* reference. This is the conventional TM-leverage case and a sanity baseline. It isn't part of the principal analysis.

**Duplicate handling.**
- (a) Normalized-source groups (case, whitespace, numbers and placeholders collapsed) never cross TM and held-out, except for the designed 100 band.
- (b) Held-out items are greedily de-clustered: no two held-out sources in the same corpus have word-level fuzzy ≥ 90 with each other. This keeps the held-out rows roughly independent.
- (c) **Similarity between held-out and TM is the independent variable, not leakage**, so it's measured, not removed.
- (d) `ref_in_tm_targets` is flagged as described above.

Moses exports have no document IDs, so document-level separation isn't possible. This is listed as a limitation.

## 4. Systems and conditions

All LLM conditions use **one translator, `google/gemma-4-31b-it`**. Settings: temperature 0, reasoning off, `max_tokens` 512, bf16/fp8 providers only (no fp4). The served snapshot and provider are logged per call. Prompts share one system/user skeleton, and only the context block differs.

| ID | Condition | Context |
|---|---|---|
| A | `zero_shot` | none |
| A′ | `zero_shot_repeat` | none, independent second generation. **Measures the generation noise floor** (subsample) |
| B | `fuzzy_ctx` | top-k exact fuzzy matches (no threshold), as raw bilingual pairs |
| C | `semantic_ctx` | top-k BGE-M3 cosine matches, raw pairs |
| D | `hybrid_ctx` | top-k RRF fusion of fuzzy top-20 and semantic top-20, raw pairs |
| F | `draft_ctx` | the **same candidates as D**, framed as a draft to adapt (fuzzy-match repair); added as amendment 6 |
| E | `structured_ctx` | the **same candidates as D**. A Gemma 4 extractor call turns them into source-specific reusable context (term pairs, phrases, conventions, explicit difference warnings) and renders it deterministically. D vs E isolates the presentation effect. |
| N | `nmt_deepl` | DeepL API (Free), no context |
| T | `tm_as_is` | the top-1 fuzzy target inserted unchanged (classic leverage, no post-editing) |

**Derived pipelines** (no extra calls) for H3: `TM≥τ → T, else N`; `TM≥τ → T, else A`; `TM≥τ → T, else D/E`; and the v1 router (fuzzy ≥ 75 → B, cosine ≥ 0.80 → C, else A). τ is swept from 50 to 100.

k defaults to 3 and is configurable. Candidates are fixed per row before any translation, so every condition sees the same retrieval results. Prompt tokens are logged, so prompt length can be used as a covariate. Raw conditions B–D all present exactly k pairs.

**Structured context safeguards.** The extractor must quote spans verbatim. Term pairs whose target span doesn't occur in the historical translation (or whose source span doesn't occur in the historical source) are **dropped and logged**. The pre-filter faithfulness rate is a reported result. The rendered block always says that the examples are not equivalents of the new source and that source meaning wins.

## 5. Evaluation

- **Primary: reference-free QE with CometKiwi-22** (`Unbabel/wmt22-cometkiwi-da`).
- **Robustness: MetricX-24-hybrid-large in QE mode** (`google/metricx-24-hybrid-large-v2p6`, lower is better, 0–25).
- **Secondary, reference-based:** chrF (sacrebleu) and COMET-22 (`Unbabel/wmt22-comet-da`).
- **Blinding:** unique `(src, hyp)` pairs are exported with opaque hash IDs, shuffled, and scored in the isolated `qe/` environment. The scorer never sees the condition, retrieved TM, prompt or model. Identical outputs get identical scores by construction.
- **Primary statistic:** the paired difference ΔQE = QE(condition) − QE(A) per row. For each condition, band, corpus and language, we report the mean Δ, a 95% paired bootstrap CI (10,000 resamples, seeded, clustered by English source for pooled KDE4) and a Wilcoxon signed-rank p, with Holm correction within each family.
- **Meaningful-improvement threshold:** the generation noise floor ε comes from the |ΔQE| distribution of A′ vs A (an independent regeneration of the same prompt). It's the 90th percentile of |ΔQE(A′,A)| on the dev split, **frozen before test inference**.
  - A segment counts as *meaningfully improved* or *degraded* when ΔKiwi crosses ±ε **and** MetricX moves in the same direction.
  - At system level, an improvement is meaningful when the mean Δ's CI excludes 0 and the mean exceeds ε/4. A sensitivity table reports results across a grid of thresholds.
- **QE validity probes:** controlled perturbations of A outputs (number change, dropped final clause, source copied untranslated, appended unrelated sentence, TM target swapped in), each measuring the share detected by QE. We also report score distributions, the correlation of QE with length ratio and with whether the output came from an LLM or NMT, and how `tm_as_is` scores in the 100 band (human-approved text) vs LLM outputs.

## 6. Recoverability (H1)

There are three separate layers, each reported per band with Wilson CIs. The denominator is **eligible held-out rows**, never TM entries:

1. **Candidate coverage:** at least one candidate retrieved above the semantic similarity floor (cosine ≥ 0.80, as in v1).
2. **Verified reusable context:** at least one candidate (from any retriever shown to the translator) labelled reusable. Labels: `full`, `partial`, `terminology`, `style_convention`, `none`, `misleading`. A label needs **both** `claude-sonnet-5.5` classification (independent of the Gemma translator, never shown the held-out reference) **and** at least one evidence target span found verbatim in the historical translation.
3. **Downstream improvement:** the share of rows meaningfully improved by B–E (as defined in §5).

Human annotations can override labels (`annotations/reuse_human.csv`, merged by `(row_id, tm_id)`). The analysis reports agreement between the automated and human labels when human labels exist.

## 7. When does RAG help or hurt?

- **Segment-level regression** of ΔQE on: fuzzy score, top cosine, best reuse label, `misleading` presence, source length, terminology density, prompt tokens, baseline QE, corpus and language.
  - Terminology density is a cross-domain log-odds proxy: the share of content tokens far more frequent in the row's domain corpus than in the other corpus.
  - Regression to the mean on baseline QE is flagged.
- **Automated contamination detectors:** number mismatch, negation mismatch (language-specific markers), and TM-only n-grams (n-grams present in the TM target and the output but in neither zero-shot nor anything licensed by the source).
- **MQM error spans from Sonnet** on a stratified sample of the largest improvements and degradations. This is diagnostic only and not a preference judgment.
- **Retrieval confidence as a predictor:** AUC of fuzzy score, cosine and reuse label for predicting meaningful improvement.

A gating model is deferred until the main results are in.

## 8. Cost estimate (to be replaced by measured cost from Phase 3)

| Role | Calls (test) | Approx. tokens | Price | Est. |
|---|---:|---|---|---:|
| Gemma 4 31B: A, B, C, D, E, extractor | ~26k (+~1k A′) | ~16M in / ~3M out | $0.14–0.20 in / $0.40 out per M | ~$4 |
| Sonnet 5.5: reuse classification (batch API) | 4.4k | ~5M in / ~1.3M out | $1 / $5 per M (batch) | ~$12 |
| Sonnet 5.5: extractor audit + MQM samples | ~1k | ~1.5M / ~0.4M | batch | ~$3 |
| BGE-M3 embeddings | 130k texts | ~4M | ~$0.01/M | <$0.10 |
| DeepL Free | ~320k chars | | free tier (500k/month) | $0 |
| QE (local CPU) | ~30k unique pairs × 3 models | | | $0 |
| **Total** | | | | **~$19** |

## 9. Execution order and stopping points

1. Phase 2: implementation plus offline tests (no spend).
2. Phase 3: dev split (~300 rows). Measured cost, manual inspection of prompts, extractions, language and QE. Noise floor frozen. **We stop here so you can review cost before Phase 4.**
3. Phase 4: test split, full run.
4. Phase 5: report and README. v1 is kept as historical findings.

## 10. Protocol amendments (made before any test QE score was seen)

1. **Sync auditor calls.** The OpenRouter account uses Zero Data Retention, so the Batch API is refused. Auditor calls are synchronous, at twice the price.
2. **Reuse labels on a stratified 2,000-row test subsample** (all rows on dev) to stay within budget. Recovery rates use that subsample. Translation quality uses every row.
3. **Noise floor redefined** after the smoke run. ε is the 90th percentile of |ΔKiwi| over zero-shot regenerations *whose outputs differ*. Most regenerations are identical, which would make a quantile over all pairs ≈ 0.
4. **Single QE model on test.** The full CPU run of three neural metrics would take about 12 h, so the test split is scored with CometKiwi-22 only. MetricX-24 QE and COMET-22 are kept on the 300-row dev run, where they calibrate agreement between metrics. Reference-based chrF (no model) is kept on test. On test, "meaningful" therefore means ΔKiwi ≥ ε, without the MetricX agreement condition.
5. **Credit limit.** With about $13.66 of OpenRouter credit left after the dev run, the test auditor samples were cut to 1,200 rows for reuse labels and 150 rows for the extractor audit. MQM error spans were planned for the dev run only (later skipped, see 10). The overrides are logged in `results/study/test-v1/amendments.jsonl`.
6. **Condition F `draft_ctx` added (user suggestion), before any test QE score was seen.** It uses the same 3 hybrid candidates as D, but in fuzzy-match-repair framing: the top pair is a *draft to adapt* (keep what still applies, change what differs, translate from scratch if it doesn't help), and the rest are references. F vs D isolates framing. F vs E compares "edit a draft" with "extracted reusable items". Run via `generate --conditions draft_ctx` so the frozen config hash is unchanged.
7. **H3 crossover cross-checked with reference-based metrics.** On the smoke run, reference-free QE never preferred human TM text, even for exact matches.
8. **COMET-22 on a 1,500-source stratified test subsample.** Added after the dev run showed reference-free QE (CometKiwi, MetricX) and reference-based metrics (COMET-22, chrF) disagreeing in direction. The decision was made before any test score existed. It costs no API credit and was scheduled after the primary CometKiwi pass.
9. **(Post-test, reporting only.) H2 also reported under reference-based metrics** (report §H), including a "clean" variant that drops rows whose reference occurs verbatim as a TM target. The primary metric and the pre-registered verdict are unchanged.
10. **Dev MQM not run.** The credit guard refused it (estimated $1.08 against $1.73 remaining, $1.50 reserve). The human-evaluation export (`human_eval/`) is the remaining route to adjudicate the QE-vs-reference disagreement.
11. **(Post-test.) Analysis fix, no data changed.** Without a second QE metric, `paired_summary` forced the degraded share to 0. Fixed, covered by a test, and both runs re-analysed.

## 11. Known limitations (designed in)

- Corpus translations stand in for approved client TMs and contain errors and misalignments.
- There are no document IDs, so random sentence-level splits overstate how "historical" the TM is relative to new content.
- QE is a model and not human judgment. CometKiwi and MetricX may share biases (for example, a preference for fluent LLM output or a penalty on terse UI strings). The probes measure some of these but not all.
- `tm_as_is` is scored as unedited leverage. Real workflows post-edit fuzzy matches, so this condition is a lower bound on TM value in mid bands.
- One translator model. Results may not transfer to stronger or weaker models.
- Sonnet reuse labels are automated. Human annotation is supported but not yet performed.

Results: [v2-results.md](v2-results.md).
