"""Run source-side retrieval on every prepared multilingual query, without translation calls."""
from __future__ import annotations

import argparse
import json
import platform
import time
from collections import Counter
from pathlib import Path

import numpy as np

from locrag.evidence import read_rows
from locrag.multilingual import ROOT, digest, write_json
from locrag.pipeline import TMRouter
from locrag.retrievers import SemanticRetriever


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=ROOT / "data/multilingual")
    ap.add_argument("--output", type=Path, default=ROOT / "results/runs/multilingual-retrieval")
    ap.add_argument("--model", default="BAAI/bge-m3")
    args = ap.parse_args()
    if args.output.exists():
        ap.error("Use a fresh output directory to preserve prior runs")
    import torch
    torch.set_num_threads(6)
    manifest = json.loads((args.data / "manifest.json").read_text())
    for name, expected in manifest["file_sha256"].items():
        if digest(args.data / name) != expected:
            raise ValueError(f"Data fingerprint mismatch: {name}")
    tm = read_rows(args.data / "es/tm.jsonl")
    queries = [r for split in ("development", "test") for r in read_rows(args.data / "es" / f"{split}.jsonl")]
    start = time.perf_counter()
    print(f"Indexing {len(tm)} shared English sources with {args.model}; {len(queries)} queries.", flush=True)
    sem = SemanticRetriever(tm, model=args.model)
    index_seconds = time.perf_counter() - start
    start = time.perf_counter()
    vectors = sem.encode_queries([r["src"] for r in queries])
    encode_seconds = time.perf_counter() - start
    config = manifest["config"]
    router = TMRouter(tm, config["fuzzy_threshold"], config["semantic_min_sim"], config["k"], semantic=sem)
    rows = []
    for query, vector in zip(queries, vectors):
        decision = router.route(query["src"], vector)
        hits = sem.search_vec(vector, config["k"])
        rows.append({"id": query["id"], "set": query["set"], "src": query["src"],
                     "route": decision.route, "fuzzy_best": decision.fuzzy_best,
                     "top_cosine": hits[0].score / 100, "used_example_count": len(decision.examples),
                     "retrieval_ms_excluding_query_encoding": decision.retrieval_ms,
                     "semantic_matches": [{"tm_index": h.idx, "src": h.src, "cosine": h.score / 100} for h in hits]})
    args.output.mkdir(parents=True)
    (args.output / "rows.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows))
    summary = {"status": "retrieval complete; no new translations or usefulness judgments",
               "model": args.model, "data_manifest_sha256": digest(args.data / "manifest.json"),
               "languages_sharing_these_sources": config["languages"], "tm_size": len(tm),
               "index_seconds_including_model_load_or_cache": index_seconds,
               "query_encoding_seconds": encode_seconds, "platform": platform.platform(), "splits": {}}
    for split in ("development", "test"):
        subset = [r for r in rows if r["set"] == split]
        summary["splits"][split] = {"n": len(subset), "routes": dict(Counter(r["route"] for r in subset)),
            "top_cosine_quantiles": {str(q): float(np.quantile([r["top_cosine"] for r in subset], q)) for q in (.1,.5,.9)},
            "latency_ms_excluding_query_encoding": {"p50": float(np.median([r["retrieval_ms_excluding_query_encoding"] for r in subset])),
                                                   "p95": float(np.percentile([r["retrieval_ms_excluding_query_encoding"] for r in subset],95))}}
    write_json(args.output / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
