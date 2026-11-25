"""Score a blinded JSONL file with one metric. Resumable: ids already in the output are skipped.

    uv run --project qe python -m locrag_qe.score --metric cometkiwi22 --input in.jsonl --output out.jsonl

Input rows: {"id", "src", "mt"} (+ "ref" for comet22 / metricx24_ref). No other fields are read.
Output rows: {"id", "score"}; a sidecar <output>.meta.json records model ids and library versions.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

MODELS = {
    "cometkiwi22": "Unbabel/wmt22-cometkiwi-da",
    "comet22": "Unbabel/wmt22-comet-da",
    "metricx24_qe": "google/metricx-24-hybrid-large-v2p6",
    "metricx24_ref": "google/metricx-24-hybrid-large-v2p6",
}
NEEDS_REF = {"comet22", "metricx24_ref"}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").split("\n") if l.strip()]


def comet_scorer(model_id: str, batch_size: int):
    from comet import download_model, load_from_checkpoint
    model = load_from_checkpoint(download_model(model_id))
    model.eval()

    def score(rows: list[dict]) -> list[float]:
        data = [{k: r[k] for k in ("src", "mt", "ref") if k in r} for r in rows]
        out = model.predict(data, batch_size=batch_size, gpus=0, progress_bar=False, num_workers=1)
        return [float(s) for s in out.scores]
    return score


def metricx_scorer(model_id: str, tokenizer_id: str, batch_size: int, with_ref: bool, max_len: int = 1536):
    import torch
    from transformers import AutoTokenizer
    from locrag_qe.metricx import MT5ForRegression, qe_input, ref_input
    tok = AutoTokenizer.from_pretrained(tokenizer_id)
    model = MT5ForRegression.from_pretrained(model_id, torch_dtype=torch.float32)
    model.eval()

    def score(rows: list[dict]) -> list[float]:
        texts = [ref_input(r["src"], r["mt"], r["ref"]) if with_ref else qe_input(r["src"], r["mt"]) for r in rows]
        enc = [tok(t, max_length=max_len, truncation=True)["input_ids"][:-1] for t in texts]  # drop EOS, as upstream
        order = sorted(range(len(enc)), key=lambda i: len(enc[i]))
        scores = [0.0] * len(enc)
        for s in range(0, len(order), batch_size):
            idx = order[s:s + batch_size]
            L = max(len(enc[i]) for i in idx)
            ids = torch.full((len(idx), L), tok.pad_token_id, dtype=torch.long)
            mask = torch.zeros((len(idx), L), dtype=torch.long)
            for j, i in enumerate(idx):
                ids[j, :len(enc[i])] = torch.tensor(enc[i])
                mask[j, :len(enc[i])] = 1
            for i, v in zip(idx, model.score(ids, mask).tolist()):
                scores[i] = float(v)
        return scores
    return score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metric", choices=sorted(MODELS), required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--metricx-tokenizer", default="google/mt5-xl")
    a = ap.parse_args()

    import torch
    torch.set_num_threads(a.threads)
    torch.manual_seed(0)
    rows = read_jsonl(a.input)
    allowed = {"id", "src", "mt"} | ({"ref"} if a.metric in NEEDS_REF else set())
    for r in rows:  # blinding guard: refuse any input that carries more than it should
        extra = set(r) - allowed
        if extra:
            print(f"refusing input with unexpected fields {sorted(extra)}", file=sys.stderr)
            return 2
    done = {r["id"] for r in read_jsonl(a.output)}
    todo = [r for r in rows if r["id"] not in done]
    print(f"{a.metric}: {len(rows)} items, {len(todo)} to score", flush=True)
    if todo:
        if a.metric.startswith("metricx"):
            score = metricx_scorer(MODELS[a.metric], a.metricx_tokenizer, a.batch_size, a.metric == "metricx24_ref")
        else:
            score = comet_scorer(MODELS[a.metric], a.batch_size)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        for s in range(0, len(todo), a.chunk):
            chunk = todo[s:s + a.chunk]
            scores = score(chunk)
            with a.output.open("a", encoding="utf-8") as f:
                for r, v in zip(chunk, scores):
                    f.write(json.dumps({"id": r["id"], "score": v}) + "\n")
            n = s + len(chunk)
            rate = n / max(1e-9, time.time() - started)
            print(f"  {n}/{len(todo)} ({rate:.1f}/s)", flush=True)
    import transformers
    try:
        import comet
        comet_v = getattr(comet, "__version__", "unknown")
    except ImportError:
        comet_v = None
    meta = {"metric": a.metric, "model": MODELS[a.metric], "direction": "lower_better" if a.metric.startswith("metricx") else "higher_better",
            "tokenizer": a.metricx_tokenizer if a.metric.startswith("metricx") else None,
            "torch": torch.__version__, "transformers": transformers.__version__, "unbabel_comet": comet_v,
            "python": platform.python_version(), "threads": a.threads, "batch_size": a.batch_size}
    Path(str(a.output) + ".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
