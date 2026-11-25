# Translation memory, terminology consistency and accuracy

Written before collecting convention labels or scoring any outputs for this analysis. The v2 and frontier translations and their earlier metric results already exist.

## Question and sample

Does semantic top-3 improve adherence to established Spanish wording compared with fuzzy top-3 more below a 75% fuzzy cutoff than at very high match scores? Compare both against translation without TM. Use existing Gemma outputs for 40 deterministic random test segments per domain (EMEA medical, KDE4 software) and original band (<50, 50–74, 75–84, 85–94, 95–99, 100), 480 sources total. Primary groups are low (<75), middle (75–94), and high (95–100). Report individual bands as well, including exact matches separately. Spanish holds language constant across domains. Repeat the below-cutoff analysis on the existing 100-source Astra panel. Some sources can recur across the two translators; report each panel separately.

## Establish a convention before judging translations

Use the same corpus TM as the translator. Build an English-side BM25 concordance of up to 12 bilingual entries per source. Exclude the union of both arms' top three entries, exact normalized English source matches, and duplicate normalized English entries. Supply the new English source and these entries to GPT-6.2 Astra. Hide translations under evaluation, reference, arm names, match scores and band. Select at most one domain term, UI label or reusable phrase per source. It must apply in the new context and have a consistent Spanish rendering supported by at least two distinct historical source entries. Reject generic function words, unsupported conventions and conflicting evidence. Store the source phrase, preferred wording, acceptable variants and cited TM spans. Verify literal evidence against the stored entries. Abstentions and unsupported annotations have no consistency denominator. This operationalizes a documented corpus convention; the corpora supply no client style guide.

## Blinded evaluation

Freeze all convention decisions before scoring. Give GPT-6.2 Sol unique anonymous candidate translations in deterministic shuffled order. Reuse a grade for identical strings on the same source. Run two separate prompts. The accuracy prompt sees only the English source, domain and candidates and flags meaning errors, including wrong actions or entities, omissions, numbers, negation, and broken placeholders. Accept accurate synonyms. The consistency prompt sees the frozen convention and candidates, and checks correct use in context, accepting legitimate inflections and the recorded variants. Each verdict includes short evidence. Score accuracy on every source. Score consistency on eligible sources only. As a reliability check, reverse candidate order and repeat both judgments on a fixed 10% hash sample with multiple distinct candidates. Use first-pass decisions for primary estimates and disclose disagreement.

## Analysis

For each system, report the share of eligible sources consistent and the share of all sources accurate. The primary contrast is the difference in paired consistency rates, semantic minus fuzzy, in low minus high bands. Positive values favor the hypothesis. Report semantic and fuzzy versus no TM alongside it. Compare source-paired binary outcomes with 10,000 bootstrap resamples inside original domain × band cells, preserving pairing. Pool eligible sources within each group; rates describe the balanced benchmark and its eligible subset. Also count consistency fixes that leave an output accurate, reverse losses, and newly introduced meaning errors. CIs are pointwise; small differences or intervals spanning zero do not establish equivalence. No timed editing or human preference claims. API calls share the existing project's $80 ledger cap.

## Reproduction

The checked-in sources, saved translations, convention decisions and anonymous grades suffice for the main analysis. The exploratory QE comparison also reads the existing v2 results. These commands make no API calls.

```bash
uv sync --locked
uv run python -m locrag.study.consistency_analysis
uv run python -m locrag.study.consistency_figure
```

To recreate the sample and concordances, first rebuild the TMs using the [v2 data preparation](../../docs/v2-reproduction.md), then run `uv run python -m locrag.study.consistency_panel`. The two annotation stages use the direct OpenAI API and the same persistent, budgeted SQLite ledger as the frontier study. Run `uv run python -m locrag.study.consistency conventions` first and `uv run python -m locrag.study.consistency grades` second. Fresh model responses may differ. [Source concordances](sources.jsonl) · [Scored translations](translations.jsonl) · [Convention decisions](../../results/consistency/conventions.jsonl) · [Anonymous grades and decoding keys](../../results/consistency/grades.jsonl)
