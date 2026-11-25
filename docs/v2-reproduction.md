# Reproducing the LocRAG 2.0 study

Protocol and rationale: [v2-assessment-and-plan.md](v2-assessment-and-plan.md). Frozen config: [`experiments/study_v2.yaml`](../experiments/study_v2.yaml).

## Setup

```bash
uv sync --locked                 # main pipeline (Python ≥3.12)
uv sync --project qe             # isolated QE environment (Python 3.12, CPU torch, unbabel-comet)
cp .env.example .env             # OPENROUTER_API_KEY, DEEPL_API_KEY, HF_TOKEN
bash scripts/download_emea.sh && bash scripts/download_kde4.sh
```

`HF_TOKEN` must belong to an account that has accepted the CometKiwi license at
https://huggingface.co/Unbabel/wmt22-cometkiwi-da. Fine-grained tokens also need read access to public gated repositories.

## Stages

Every stage is resumable. A rerun skips completed `(row, condition)` outputs and already-scored QE items.

```bash
uv run python -m locrag.study prepare     # TMs + band-stratified held-out sets → data/study/ (offline, ~6 min)
uv run python -m locrag.study retrieve    # fuzzy/semantic/hybrid candidates for all held-out sources

RUN=dev-v1
uv run python -m locrag.study generate --run $RUN --split development   # Gemma 4 A–E, A′, TM-as-is, DeepL
uv run python -m locrag.study audit    --run $RUN                       # Sonnet reuse labels + extractor audit
uv run python -m locrag.study qe       --run $RUN                       # CometKiwi, MetricX QE, COMET-22 (CPU)
uv run python -m locrag.study audit    --run $RUN --tasks mqm           # MQM sample (needs QE for selection)
uv run python -m locrag.study analyze  --run $RUN
uv run python -m locrag.study cost     --run $RUN                       # measured spend + projection
```

For a test run, reuse the dev noise floor so the meaningful-improvement threshold is frozen before test results are seen:

```bash
uv run python -m locrag.study analyze --run test-v1 --noise-from dev-v1
```

The test run reported in [v2-results.md](v2-results.md) used these exact commands (after the dev run above):

```bash
RUN=test-v1
uv run python -m locrag.study generate --run $RUN --split test
uv run python -m locrag.study generate --run $RUN --conditions draft_ctx --skip-nmt
uv run python -m locrag.study audit    --run $RUN --tasks reuse,extraction --reuse-rows 1200 --extraction-sample 150
uv run python -m locrag.study qe       --run $RUN --metrics cometkiwi22
uv run python -m locrag.study qe       --run $RUN --metrics comet22      # 1,500-source reference subsample on test
uv run python -m locrag.study analyze  --run $RUN --noise-from dev-v1
```

Measured cost: about $2.70 of Gemma generation plus $9.50 of Sonnet auditing on test, and $4.10 for the dev run. DeepL used about 350k free-tier characters. QE took about 6 h on a 6-core laptop CPU.

`--per-band N` limits a new run to N sources per (corpus, band) stratum (smoke tests). `--skip-nmt` defers DeepL. You can add it later by rerunning `generate`.

## Outputs (`results/study/<run>/`)

| File | Contents |
|---|---|
| `manifest.json` | config + hash, git commit/dirty state, code and data hashes, prompt template hashes, row strata |
| `rows.json` | held-out row ids in this run |
| `translations.jsonl` | one record per (row, condition): context block, candidate TM indices, model/params, served provider and snapshot, tokens, cost, latency, errors |
| `prompts.jsonl` | exact messages for every unique prompt (keyed by `messages_sha`) |
| `extractions.jsonl` | raw extractor output, per-item verbatim checks, rendered context |
| `reuse.jsonl`, `extraction_audit.jsonl`, `mqm.jsonl` | auditor outputs |
| `qe/` | blinded scorer inputs (`id, src, mt[, ref]` only) and scores per metric |
| `rows_analysis.jsonl` | merged per-(row, condition) analysis record |
| `summary.json`, `report.md`, `examples.md` | results |
| `human_eval/` | blinded stratified sample (`items.csv`) and the separate key (`key.csv`) |

Human reuse annotations can be added later as `annotations/reuse_human.csv` (`row_id, tm_id, label`). Merging them is a planned extension of `analyze`.
