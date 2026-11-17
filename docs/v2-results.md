# LocRAG 2.0: results

Test run `test-v1`, analysed with the noise floor frozen from `dev-v1`. Design and pre-registered protocol: [v2-assessment-and-plan.md](v2-assessment-and-plan.md). Reproduction: [v2-reproduction.md](v2-reproduction.md). Machine-generated report with every table: [`results/study/test-v1/report.md`](../results/study/test-v1/report.md). Every number below is copied from that report, from `summary.json`, or from the row-level file `rows_analysis.jsonl` in the same directory.

## Summary

1. **H1, recoverability: supported.** Below the 75% fuzzy cutoff, retrieved TM units contained reusable translation material for almost every sentence. The material was substantive (full or partial reuse with a verbatim-verified span) for 96% of EMEA rows and 80% of KDE4 rows, re-weighted to each corpus's natural mix of 50–74 and <50 matches. Retrieval by meaning alone (semantic-only) added little: substantive material that fuzzy top-3 missed and semantic top-3 found occurred in 12.5% of EMEA below-75 rows and 6.6% of KDE4 below-75 rows.
2. **H2, quality vs zero-shot: the primary metric and the cross-checks disagree.**
   - **Primary metric, reference-free QE (CometKiwi-22):** every TM-context condition scores slightly *below* zero-shot Gemma, by 0.8 to 1.1 Kiwi points pooled, and DeepL scores slightly *above* it (+0.65). On the dev split, MetricX-24 QE agrees in direction. Under the pre-registered primary metric, **H2 is not supported.**
   - **Reference-based cross-checks (COMET-22, chrF):** every TM-context condition is clearly *above* zero-shot, by +1.7 to +2.4 COMET-22 points and +7.7 to +10.9 chrF points pooled. DeepL is *below* it (−0.7 COMET, −3.2 chrF). The gain holds below the 75 cutoff (+0.8 to +1.2 COMET, +3 to +5 chrF), and it holds after removing rows whose reference also occurs in the TM.
3. **Why they disagree (best supported explanation).** TM context pulls Gemma toward the corpus's own terminology and phrasing. The independent human references share those conventions, and QE does not reward them.
   - QE scores human-approved exact-match translations *below* Gemma's zero-shot output (band 100: 0.781 vs 0.841).
   - On rows where context changed the output, the QE change and the COMET-22 change are negatively correlated (Spearman −0.09 to −0.16). In half of those rows QE says "worse" while COMET-22 says "better".
4. **H3, crossover (where raw TM stops being worth using).** Under reference-based metrics, unedited TM beats zero-shot LLM and DeepL only above roughly 80–90 fuzzy, depending on corpus and language. It never beats the LLM *with* that same TM as context except at about 96–100. Under QE, raw TM never wins, not even at exact matches.
5. **Which way of presenting the context works best.** Prompt framing barely matters:
   - fuzzy, semantic, hybrid RRF and "use this as a draft" (`draft_ctx`) are within about 0.3 points of each other on every metric;
   - `draft_ctx` is marginally best on reference metrics and marginally worst on QE;
   - structured extraction (E) is the weakest context condition on reference metrics and costs about 4× more.
6. **An LLM judge settles the fuzzy-match question.** Claude scored 72 blinded rows against the reference. RAG beat the unedited fuzzy match in 64 rows, tied 8 and lost none (judge score 96.9 vs 37.2), and the fuzzy match had a major or critical error in 59 of 72 rows. RAG tied zero-shot (96.9 vs 96.8) and edged DeepL (93.7). Reference metrics rated many critically wrong fuzzy matches (wrong drug, opposite direction) as good, because those matches share almost every word with the reference.
7. **Retrieval confidence doesn't predict QE benefit.** AUC is about 0.50 for fuzzy score, cosine and reuse label. Low zero-shot QE predicts improvement (AUC 0.89), but that is largely regression to the mean.

The honest headline: **TM context makes a frontier LLM's output measurably more like the client's own approved translations, but it doesn't make the output look better to a reference-free quality model.** Which of those matters depends on the use case. Settling it needs human judgment, which this study didn't buy (see "What would settle it").

## What was run

| | |
|---|---|
| Data | OPUS EMEA en→es (TM 100k entries, 2,000 held-out test rows) and KDE4 en→de/es/zh_CN (TM 30k per language, 743 sources × 3 = 2,229 rows). Band quotas cover 100 / 95–99 / 85–94 / 75–84 / 50–74 / <50. KDE4 95–99 fell short at 43 of 100 sources. Dev split: 300 rows. |
| Separation | The TM, held-out sources and references are disjoint. Held-out sources are de-clustered (no two above fuzzy 90). Dedup collapses numbers and placeholders. In the exact band the TM holds one translation and the reference is a *different* one. References are never read by retrieval, translation or the auditor. |
| Retrieval | Exact word-level Levenshtein fuzzy matching, BGE-M3 cosine, and hybrid RRF with a near-exact override. k=3, frozen before translation. |
| Translator | `google/gemma-4-31b-it` via OpenRouter, temperature 0, bf16/fp8 providers. All test rows were served by the same snapshot (`-20260402`). |
| Conditions | A `zero_shot`, B `fuzzy_ctx`, C `semantic_ctx`, D `hybrid_ctx`, E `structured_ctx` (Gemma extracts verbatim-checked reusable items, then translates from them), F `draft_ctx` (top hybrid match framed as a draft to adapt, as fuzzy-match repair), N `nmt_deepl` (DeepL API, classic NMT), T `tm_as_is` (unedited fuzzy top-1 target), A′ `zero_shot_repeat` (noise floor, 600 rows). |
| Auditor | `claude-sonnet-5.5`: reuse labels (1,200-row stratified subsample) and extractor audit (150 rows). It never sees references and never judges translation preference. |
| Metrics | CometKiwi-22 QE (primary, every row). COMET-22 (1,500-source stratified subsample) and chrF (every row) as reference-based cross-checks. MetricX-24 QE on dev only. All scoring is blind: an opaque ID plus source and hypothesis only. |
| Statistics | Paired bootstrap CIs (10k resamples, clustered by source when languages are pooled), Wilcoxon with Holm correction, isotonic crossover with bootstrap CI, threshold sweep. Meaningful change: ε = 0.0216 Kiwi, the 90th percentile of \|ΔKiwi\| between differing zero-shot regenerations on dev. |

## H1: is there reusable material below the fuzzy cutoff?

Reuse labels come from the stratified subsample. "Any" means at least one shown TM unit is labelled full, partial, terminology or style **and** the cited span is found verbatim in the TM translation. "Substantive" restricts this to full or partial.

| stratum | rows | cos ≥ 0.80 | any reuse | substantive | substantive, semantic-only | ≥1 misleading unit shown |
|---|---:|---:|---:|---:|---:|---:|
| EMEA/es, below 75 | 200 | 53.5% | 100% [98.1, 100] | 96.5% [93.0, 98.3] | 12.5% | 33.0% |
| EMEA/es, <50 | 100 | 33.0% | 100% | 94.0% [87.5, 97.2] | 20.0% | 24.0% |
| KDE4 (3 langs), below 75 | 121 | 56.2% | 99.2% [95.5, 99.9] | 85.1% [77.7, 90.4] | 6.6% | 25.6% |
| KDE4 (3 langs), <50 | 24 | 0% | 100% | 70.8% [50.8, 85.1] | 12.5% | 20.8% |

Re-weighted to each corpus's natural mix of matches below 75:
- EMEA: 100% any reuse, 95.7% substantive.
- KDE4: 99.5% any reuse, 79.6% substantive. By language: de 73.6%, es 85.1%, zh_CN 81.5%.

Caveats:
- These are *presence* rates. The 100k-entry EMEA TM is very repetitive (regulatory boilerplate), so almost every sentence has a partially reusable neighbour.
- 96% of rows also had at least one shown unit flagged as *risky if copied*. With k=3 partial matches, some shown content almost always doesn't apply.
- Labels are automated (Sonnet plus a verbatim check), not human.

## H2: does the context improve translation?

Pooled over all 4,229 test rows (ALL), and over the 2,140 rows whose best fuzzy match is below 75. Δ vs zero-shot, 95% CI:

| condition | ΔKiwi ×100 (all) | ΔCOMET-22 ×100 (all, n=1,501) | ΔchrF (all) | ΔKiwi ×100 (<75) | ΔCOMET-22 ×100 (<75, n=510) | ΔchrF (<75) |
|---|---:|---:|---:|---:|---:|---:|
| B fuzzy_ctx | −0.89 [−1.1, −0.7] | +2.37 [2.0, 2.7] | +10.5 [9.8, 11.2] | −0.52 [−0.7, −0.3] | +0.98 [0.6, 1.4] | +5.0 [4.3, 5.7] |
| C semantic_ctx | −0.84 [−1.0, −0.7] | +2.22 [1.9, 2.5] | +10.1 [9.5, 10.8] | −0.47 [−0.7, −0.3] | +0.79 [0.4, 1.2] | +4.9 [4.2, 5.7] |
| D hybrid_ctx | −0.90 [−1.1, −0.7] | +2.37 [2.0, 2.7] | +10.4 [9.8, 11.1] | −0.53 [−0.7, −0.3] | +1.02 [0.6, 1.4] | +5.0 [4.3, 5.8] |
| E structured_ctx | −1.01 [−1.2, −0.8] | +1.67 [1.4, 2.0] | +7.7 [7.1, 8.3] | −0.72 [−0.9, −0.5] | +0.76 [0.4, 1.2] | +3.1 [2.3, 3.8] |
| F draft_ctx | −1.13 [−1.3, −0.9] | +2.34 [2.0, 2.7] | +10.9 [10.2, 11.6] | −0.61 [−0.8, −0.4] | +1.16 [0.8, 1.6] | +5.3 [4.6, 6.1] |
| N nmt_deepl | +0.65 [0.5, 0.8] | −0.67 [−0.9, −0.5] | −3.2 [−3.6, −2.8] | +0.60 [0.4, 0.8] | −0.96 [−1.4, −0.6] | −3.7 [−4.3, −3.1] |
| T tm_as_is | −21.7 [−22.4, −21.0] | −8.2 [−9.2, −7.3] | −13.1 [−14.4, −11.8] | −30.8 [−31.7, −30.0] | −21.6 [−23.2, −20.1] | −30.8 [−32.4, −29.3] |

Under the primary metric's segment-level threshold (|ΔKiwi| ≥ ε):
- The context conditions meaningfully improve about 6–7% of rows and meaningfully degrade 15–17%.
- DeepL improves 13% and degrades 6%.
- 22–25% of context outputs are character-identical to zero-shot.

The direction is the same in every corpus and language. KDE4 shows larger QE drops (−1.2 to −1.7) and larger reference gains (B/C/D/F about +2.6 COMET, +12 chrF) than EMEA.

### The two metric families disagree

| | context conditions vs zero-shot | DeepL vs zero-shot |
|---|---|---|
| CometKiwi-22 QE (test) | worse | better |
| MetricX-24 QE (dev, 300 rows) | worse (−0.07 to −0.17 on 0–25) | better (+0.37) |
| COMET-22, reference-based | better | worse |
| chrF, reference-based | better | worse |

So the split is between *with references* and *without*, not between individual metrics. Evidence on the cause:

- **QE scores human corpus translations below LLM output.** In band 100, the TM holds an approved human translation of the *identical* source. Mean Kiwi: TM-as-is 0.781, zero-shot Gemma 0.841, DeepL 0.843. A metric that ranks the client's approved translation of the exact sentence below a zero-shot LLM can't reward moving toward the client's conventions.
- **The two kinds of metric disagree row by row.** On rows where `hybrid_ctx` changed the output (3,235 rows), ΔKiwi and ΔCOMET-22 have Spearman ρ = −0.09, and ΔKiwi with ΔchrF ρ = −0.14. 50% of those rows have ΔKiwi < 0 and ΔCOMET > 0; only 8% go the other way. DeepL shows the mirror image (13% vs 36%).
- **It's convention, not leakage.** Dropping the 280 rows whose reference also occurs verbatim as a TM target changes the context conditions' reference-metric deltas by at most about 0.5 points (report §H, "clean" columns).
- **A typical case.** Source "There are no adequate data from the use of Keppra in pregnant women.":
  - Zero-shot: "No existen datos *adecuados* sobre el *uso* de Keppra…"
  - With context: "No existen datos *suficientes* sobre la *utilización* de Keppra…", the corpus's wording, seen in three retrieved TM neighbours.
  - The reference uses the corpus wording too. Kiwi −0.6 points, chrF +32.
- **Corpus artefacts contribute a little.** Some EMEA segments carry English boilerplate that the corpus's Spanish side leaves untranslated, and with context Gemma copies that habit. QE punishes this heavily and the reference rewards it. Excluding those rows moves the EMEA Kiwi delta by only about 0.1, so this doesn't explain the overall pattern.

The QE validity probes show CometKiwi does catch real errors:
- dropped endings, untranslated output, appended content, removed negation and a swapped-in wrong TM target: 99–100% lower, 96–99% by at least ε;
- number changes: 91% lower, but only 26% by at least ε.

So the QE penalty on context is more plausibly a *style/convention* signal than evidence of new meaning errors. The failure detectors agree: number mismatches 25–35 per condition vs 32 for zero-shot, negation mismatches 210–216 vs 202. A judgment of "no new errors" would need MQM or human review, and it was not funded (see Amendments).

## H3: at which match band does raw TM stop being useful?

τ\* is the lowest best-fuzzy score at which an isotonic fit of [score(TM-as-is) − score(alternative)] reaches 0, with a 95% bootstrap CI. Above τ\*, inserting the unedited TM match is at least as good as the alternative.

| stratum | vs zero-shot, COMET-22 | vs zero-shot, chrF | vs DeepL, COMET-22 | vs hybrid_ctx, COMET-22 | under CometKiwi |
|---|---:|---:|---:|---:|---|
| EMEA/es | 91 [88, 96] | 87 [86, 89] | 91 [87, 96] | 100 [96, 100] | never |
| KDE4 pooled | 82 [80, 100] | 80 [79, 82] | 82 [80, 100] | 100 | 100 or never |
| KDE4/de | 90 [80, 100] | 80 [79, 82] | 90 [80, 100] | 100 | 100 |
| KDE4/es | 100 [83, 100] | 83 [80, 88] | 100 [83, 100] | 100 | 100 |
| KDE4/zh_CN | 78 [75, 93] | 75 [73, 80] | 78 [75, 90] | 100 [82, 100] | never |

How to read this:
- **Raw TM vs a context-free system.** By reference metrics, unedited fuzzy matches stop paying off at about 80–90 fuzzy, which is close to the 75–85 cutoffs CAT tools use. QE never prefers raw TM.
- **Raw TM vs an LLM given that same TM.** The crossover moves to about 96–100: the LLM-with-context matches or beats raw TM everywhere except near-exact matches. The best "TM-as-is if fuzzy ≥ τ, else hybrid_ctx" threshold is 93–99 by COMET-22.
- **Caveat at band 100.** In the exact band the reference is by design a *different* translation from the TM's, so reference metrics understate TM-as-is there.
- **Where context helps, by band.** By COMET-22, `hybrid_ctx` beats zero-shot significantly in 95–99, 85–94, 75–84 and 50–74 in almost every stratum (+1 to +6 points). At <50 the gain mostly isn't significant (+0.2 to +1.1). In KDE4 it's slightly negative at 100, consistent with the exact-band design. chrF gains stay significant at <50 (+1 to +7).

So, for the question "at what band does TM stop being useful and RAG start being useful":
- **Raw TM stops being worth inserting at about 80–90 fuzzy.**
- **Giving the TM to the LLM as context helps from about 95 down to 50, by reference metrics.** Below 50 the benefit fades toward zero.
- **No band shows a QE benefit.**

## LLM judge: RAG vs the fuzzy match, read by a model

To get a judgment that reads meaning rather than surface overlap, Claude Opus 5.5 (in the analysis session, so no API spend) scored a blinded, stratified sample. The sample was 72 test rows (12 per band; EMEA/es 36, KDE4 de/es/zh_CN 12 each), each with four systems: unedited fuzzy match, hybrid RAG, zero-shot, DeepL.
- **Blinding:** candidates were shuffled under letters and identical outputs merged, which gave 249 unique translations. The key was opened only after all scores were written.
- **Rubric:** MQM-lite (minor 1, major 5, critical 10) plus a 0–100 score. The reference was used as a guide to meaning, and wording that differed from it was not penalised.
- **Files:** `results/study/test-v1/llm_judge/` (items, key, scores, `report.md`, `analyze_judge.py`).

| system | mean judge score | rows with a major/critical error | rows with a critical error |
|---|---:|---:|---:|
| fuzzy match, unedited | 37.2 | 59 / 72 | 31 / 72 |
| hybrid RAG | 96.9 | 1 / 72 | 0 / 72 |
| zero-shot Gemma | 96.8 | 0 / 72 | 0 / 72 |
| DeepL | 93.7 | 2 / 72 | 1 / 72 |

- **RAG vs fuzzy match:** RAG wins 64, ties 8 (exact matches where it reproduced the TM) and loses 0, a gap of +59.7 [51.8, 67.7]. It wins all 12 rows in every band from 95–99 down to <50. Near-matches fail on exactly the word that differs: a different product name, up vs down, "some" vs "all", encrypt vs decrypt, a different section number.
- **RAG vs zero-shot:** a tie (+0.2 [−1.4, 1.4]). The context didn't reduce meaning errors. Its gain on reference metrics is wording conformity, and the QE penalty doesn't show up as errors either.
- **RAG vs DeepL:** +3.2 [0.4, 6.8]. DeepL's two serious errors were software terminology ("watches" as wristwatches; "keyring database" as a key fob).
- **Which metric agrees with the judge** (Spearman over all row-system pairs): CometKiwi 0.53, COMET-22 0.47, chrF 0.36.
- **Reference metrics miss critical errors.** Of the 62 outputs with a major or critical error, COMET-22 scored 15 above the median *clean* translation and chrF 26. CometKiwi scored 2 (AUC 0.92 vs COMET 0.72, chrF 0.59). Examples: Viagra and 1998 for CHAMPIX and 2006 (COMET 0.90), "move up" for "move down" (0.92), aripiprazole for olanzapine (0.89). These share almost every word with the reference. In some rows the reference itself carries the same defect as the TM (a dropped verb, a wrong section number), which reference metrics reward.
- **Caveats:**
  - One LLM judge, which also designed the study. It was blind to labels, but a wrong-sentence fuzzy match is recognisable as such.
  - 72 rows.
  - Only 3 serious errors occurred in generated output, too few to say whether QE misses subtle errors that the judge catches.

## Which retrieval and framing

- **Fuzzy vs semantic vs hybrid:** indistinguishable. All pairwise differences are ≤ 0.15 Kiwi, ≤ 0.15 COMET and ≤ 0.4 chrF pooled. Semantic search finds some material fuzzy misses (H1), but on these corpora that doesn't translate into measurably different output quality.
- **Draft framing (F) vs plain references (D):** same candidates, different prompt.
  - F has slightly higher chrF (+0.5) and slightly lower Kiwi (−0.2).
  - F copies the draft verbatim in 5.0% of rows (D 5.6%).
  - Framing the match as a "possible solution" did not change the result materially.
- **Structured extraction (E):**
  - 95.1% of extracted spans pass the verbatim check.
  - The independent audit found the mapping correct for 93.2% of items, and 87.9% apply to the new source.
  - Still, E is the weakest context condition on reference metrics (+1.7 vs +2.4 COMET) and costs about 4× as much per row (the extractor call). The extraction step loses information that raw examples carry.

## When context helps or hurts

- **Predictors of benefit** (AUC for ΔKiwi ≥ ε): fuzzy score 0.51, cosine 0.50, reuse label 0.47–0.49. Retrieval confidence carries no information about QE benefit. Low zero-shot QE (AUC 0.89) mostly reflects regression to the mean.
- **Descriptive regression** (`hybrid_ctx`): ΔKiwi falls with fuzzy score (−0.014 per 100 points), with prompt length (−0.076 per 1k tokens) and in KDE4 (−0.014). It rises slightly with source length.
- **ΔKiwi by best verified label of the shown context** (`hybrid_ctx`): full −1.3, partial −1.1, terminology −1.4. Even "fully reusable" context lowers QE, consistent with the convention explanation.
- **Largest degradations** (`examples.md`): mostly segments where the TM carries a corpus quirk and Gemma copies it. Examples:
  - English boilerplate left untranslated;
  - KDE4 strings with a stray "Stencils" suffix from misaligned entries;
  - the TM's longer UI wording ("Diese Nachfrage & nicht mehr anzeigen" for "& Do not ask again") where the reference is the shorter "& Nicht mehr fragen".

## Cost

| | measured |
|---|---:|
| Test generation (Gemma, all LLM conditions + extractor) | $2.66 |
| Test auditor (Sonnet: 1,200 reuse + 150 extractor audit) | $9.50 |
| Dev run (300 rows, everything incl. full reuse labels) | $4.11 |
| Smoke run | $0.62 |
| DeepL (349,824 characters) | $0 (free tier) |
| QE / COMET / chrF (local CPU) | $0 (~3.7 h CometKiwi, ~2 h COMET-22) |

Per row on test:

| condition | $/row | extra $/row vs zero-shot |
|---|---:|---:|
| zero-shot | ~$0.000036 | — |
| hybrid_ctx | $0.000062 | +$0.000026 |
| draft_ctx | $0.000096 | +$0.000060 |
| structured_ctx | $0.000281 | +$0.000245 |

At these prices, retrieval context adds well under a cent per thousand segments. The auditor was 78% of the spend.

## Amendments and deviations

All are logged in [the plan](v2-assessment-and-plan.md#10-protocol-amendments-made-before-any-test-qe-score-was-seen) and in `results/study/test-v1/amendments.jsonl`.

1. **Synchronous auditor.** The account uses Zero Data Retention, which the Batch API refuses.
2. **Smaller auditor samples (credit limit).** Reuse labels were planned for 2,000 test rows and ran on 1,200. The extractor audit was planned for 300 rows and ran on 150.
3. **Noise floor over differing regenerations.** 83% of zero-shot regenerations are identical, so a quantile over all pairs would be about 0.
4. **Single QE model on test** (CometKiwi). MetricX ran on dev only.
5. **COMET-22 added on a 1,500-source test subsample.** Decided after the dev run showed QE and reference metrics disagreeing, and before any test score existed. It is reference-based, adds no API cost, and ran after CometKiwi.
6. **`draft_ctx` (F) added** at the user's suggestion, before any test score was seen.
7. **MQM error annotation not run.** The planned dev MQM (50 per condition) was refused by the credit guard: estimated $1.08 against $1.73 remaining, with a $1.50 reserve. It was the planned tie-breaker for the QE-vs-reference question, so this is the study's biggest gap.
8. **Analysis bug fixed before reporting.** With no second QE metric (test), the "degraded" share was forced to 0, which overstated net improvement in the cost-benefit table. It was fixed and covered by a test (`test_paired_summary_degraded_without_agree`), and both runs were re-analysed. No generated or scored data changed.

## What would settle it

The open question is whether moving toward the TM's conventions is what a reviewer wants (consistency with approved translations) or a mild loss in fluency or adequacy that QE is right to flag. Ways to settle it, roughly in order of value:

1. **Human review of the 305 exported items** in `results/study/test-v1/human_eval/`. They are blinded and stratified across conditions and bands; 320 equivalent items exist for dev.
2. **The dev MQM pass** (about $1.10), which the code already supports: `python -m locrag.study audit --run dev-v1 --tasks mqm --mqm-per-condition 50`.
3. **A second translator model** and **document-level splits**. The current random sentence split makes the TM unusually "historical" relative to new content.

## Limitations

- Corpus translations stand in for approved client TMs. They contain misalignments and boilerplate quirks that the context conditions faithfully copy.
- There are no document IDs, so neighbouring sentences from the same document can sit on both sides of the split.
- One translator, `gemma-4-31b-it`. Stronger or weaker models may use context differently.
- Reuse labels are automated: Sonnet plus a verbatim check, on a 1,200-row subsample.
- Reference-based metrics use one reference per row, from the same corpus as the TM. They measure agreement with that corpus's conventions, which is the property TM reuse is meant to deliver, but they are not a neutral quality measure either.
- KDE4 95–99 band: 43 sources instead of 100.
