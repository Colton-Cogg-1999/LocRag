# Matched Spanish, German, and Simplified Chinese study

**Status:** data preparation, fuzzy audit and all 900 language-specific test cases under four conditions are complete. See the [completed report](../results/runs/2026-11-16/README.md) and [raw outputs](../results/multilingual/validation-v1/). Human review remains outstanding.

## Design

[OPUS KDE4 v2](https://opus.nlpl.eu/legacy/KDE4.php) supplies software-localization text for all three targets. Intersecting normalized English sources avoids confounding target language with source difficulty and domain.

The downloaded release yields 42,461 shared eligible sources. Each language gets the same 5,000 English memory entries, 150 development queries and 300 test queries, paired with its own targets. English retrieval is shared, not three independent validations. Absolute scores must not be pooled with the original Spanish EMEA medical study.

## Frozen protocol

Configuration: [`experiments/multilingual.json`](../experiments/multilingual.json).

- Seed 20261116; 4–60 English source words; non-empty targets. No Latin-script length-ratio filter on Chinese.
- Group normalized sources with number/placeholder variants before splitting. Groups cannot cross splits; surplus members are discarded, not reassigned.
- Fuzzy threshold 75%, cosine floor 0.80, k=3, fixed from the earlier exploratory study. Tune only on development data, documenting a new configuration before opening test translation results.
- Conditions: zero-shot, thresholded fuzzy, always-semantic top-k, selective routing.
- Same translator, judge, retrieval model and prompts apart from language labels across targets.
- Primary metric: character-only corpus chrF (`word_order=0`). Paired mean sentence changes and exploratory bootstrap intervals are separate statistics.
- Report sample size, route coverage, effects by fuzzy band, accuracy judgments, terminology consistency and categorized meaning errors separately.
- Differing outputs receive deterministic randomized A/B judgments. Identical outputs are ties, not proof of accuracy. One LLM judge is not human evaluation.

Moses exports lack document IDs. Source grouping does not eliminate semantic near-duplicates or corpus errors. Chinese references come from `zh_CN`; the code does not silently convert their script.

## Prepare and estimate calls

```bash
bash scripts/download_kde4.sh
uv run python -m locrag.multilingual prepare
uv run python -m locrag.multilingual plan --split development --limit 5
```

Prepared corpus files stay in ignored `data/multilingual/`. The tracked [audit](../results/multilingual/data_audit.json) includes archive/split hashes, shared-source counts, measured fuzzy latency and prefilter misses. Preparation makes no embedding or LLM calls.

Five development segments per language require at most 60 logical translation calls and 45 judge calls, plus embeddings. The full test run has bounds of 3,600 translation and 2,700 judge calls, plus embeddings. Cache hits and identical treatments reduce these; retries/repairs add requests. No dollar estimate is claimed without provider/token information.

## New inference

Configure `.env` locally, then start small:

```bash
uv run python -m locrag.multilingual run --split development --limit 5 \
  --output results/multilingual/run-smoke-v1
```

Review outputs and provider usage before the frozen test run:

```bash
uv run python -m locrag.multilingual run --split test \
  --output results/multilingual/run-test-v1
```

Output directories must be new. Manifests record configuration, model IDs, data hashes, Git commit/dirty state, Python source hashes, and metric signature. Interrupted runs preserve completed rows with a `running` status; automatic resume is not supported. Preserve the partial run and choose a new output directory when retrying.

## Human review and presentation

After inference, sample 50–100 blinded pairs per language across fuzzy bands and outcomes. Record sampling weights: a diagnostic sample is not population accuracy. Bilingual reviewers should score source-first accuracy, numbers/units/negation/placeholders and terminology separately. Preserve A/B assignments and disagreements. No human review has occurred yet.

Use one table per language with identical columns: n, route coverage, chrF change, preference wins/ties/losses, accuracy errors and terminology consistency. Include uncertainty and failure examples, rather than pooling languages into a headline score.
