# Reproducing LocRAG

Python 3.12+ and uv are required. `uv sync --locked` installs lightweight hosted/offline dependencies and test tools. Local embeddings are optional: `uv sync --locked --extra local`.

## Offline checks

```bash
uv sync --locked
uv run pytest -q
uv run python -m locrag.evidence
uv run python -m locrag.demo
node --check demo/src/app.js
python -m http.server 8000 --bind 127.0.0.1 --directory demo/dist
```

Open http://127.0.0.1:8000. The audit is rebuilt from committed outputs; hashes identify inputs. Bootstrap intervals use seed 2026 and 2,000 segment resamples. They describe mean sentence chrF++ changes, not corpus-score intervals or independent-document estimates.

## Fresh EMEA inference

Fresh inference needs data, model access and potentially paid requests. The ignored local response cache is not part of a clone. Configure `.env` before running:

```bash
cp .env.example .env
bash scripts/download_emea.sh
uv run python -m locrag.prepare_data --tm-size 20000 --per-band 40 --seed 13
uv run python -m locrag.exp_retrieval
uv run python -m locrag.exp_rag_mt --per-band 40 --k 3
uv run python -m locrag.exp_router --n-real 300 --output results/router-v2
```

The published translation study used 40 segments per band (now the default). The first two experiment scripts write original benchmark paths: use a separate checkout to preserve published results. Corrected router runs default to `results/router-v2` and preserve the historical `results/router` artifacts.

The corrected router is a new experiment, not a byte-for-byte recreation of the old treatment. No-route decisions now use no examples. Alternative policies: `--policy always-semantic` or `--policy fuzzy-only`, each with a distinct output directory.

## Provider configuration

Use `.env.example`; never commit keys. Real environment variables override `.env`.

- Hosted: `OPENROUTER_API_KEY` and translation, judge, retrieval model IDs.
- Local: install the `local` extra; start an OpenAI-compatible server; configure `L10N_LLM_BASE_URL`, `L10N_LLM_MODEL`, and a local `L10N_RETRIEVAL_MODEL`.
- `.cache/` contains responses and embeddings. New response keys include reasoning effort, so old entries may not be reused.

Historical costs/tokens were not recorded. Multilingual plans show upper bounds on logical calls, excluding retries and JSON repairs. Dollar estimates need provider pricing and expected tokens.

## Browser checks

With an existing Chromium and the server running:

```bash
node scripts/check_demo.mjs /absolute/path/to/chromium http://127.0.0.1:8000
```

Checks cover search, replay, navigation, desktop/mobile overflow and browser exceptions. Screenshots go to `docs/workbench.png` and `/tmp/locrag-mobile.png`.
