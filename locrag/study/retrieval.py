"""Candidate retrieval, computed once per held-out English source and frozen before any translation.

For every source: exact word-level fuzzy top-N, BGE-M3 cosine top-N, and an RRF fusion (hybrid). Every
candidate in the union carries BOTH its fuzzy score and its cosine, so analyses can relate lexical and
semantic similarity to reuse and to downstream quality. Targets are attached per language at prompt time.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from rapidfuzz.distance import Levenshtein

from locrag.retrievers import SemanticRetriever
from locrag.study.data import load_heldout, load_tm, read_jsonl
from locrag.study.fuzzy import ExactFuzzyIndex


def rrf_fuse(fuzzy: list[tuple[int, float]], semantic: list[tuple[int, float]], k: int, c: int = 60,
             near_exact: float = 95.0) -> list[int]:
    """Reciprocal-rank fusion; a near-exact fuzzy match always ranks first (CAT tools never hide it)."""
    scores: dict[int, float] = {}
    for hits in (fuzzy, semantic):
        for rank, (idx, _) in enumerate(hits):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (c + rank + 1)
    if fuzzy and fuzzy[0][1] >= near_exact:
        scores[fuzzy[0][0]] += 1.0
    return sorted(scores, key=lambda i: (-scores[i], i))[:k]


def retrieve_corpus(data_dir: Path, corpus: str, cfg: dict, log=print) -> list[dict]:
    rcfg = cfg["retrieval"]
    langs = cfg["corpora"][corpus]["targets"]
    tm = load_tm(data_dir, corpus, langs[0])  # English sources identical across targets
    heldout = [r for r in load_heldout(data_dir) if r["corpus"] == corpus and r["lang"] == langs[0]]
    log(f"{corpus}: {len(tm):,} TM entries, {len(heldout):,} held-out sources")
    fuzzy = ExactFuzzyIndex([r["src"] for r in tm])
    semantic = SemanticRetriever(tm, model=rcfg["embedding_model"])
    qv = semantic.encode_queries([r["src"] for r in heldout])
    depth, k = rcfg["pool_depth"], rcfg["k"]
    out = []
    for i, row in enumerate(heldout):
        f_hits = fuzzy.search(row["src"], depth)
        sims = semantic.mat @ qv[i]
        top = np.argpartition(-sims, depth - 1)[:depth]
        s_hits = sorted(((int(j), float(sims[j])) for j in top), key=lambda x: (-x[1], x[0]))
        hybrid = rrf_fuse(f_hits, s_hits, k, rcfg["rrf_c"], rcfg["near_exact_override"])
        union = {i for i, _ in f_hits} | {i for i, _ in s_hits}
        q_enc = fuzzy._encode(row["src"])
        cand = {str(j): {"tm_id": tm[j]["tm_id"],
                         "fuzzy": round(100.0 * Levenshtein.normalized_similarity(q_enc, fuzzy.encoded[j]), 2),
                         "cos": round(float(sims[j]), 4)} for j in sorted(union)}
        out.append({
            "src_id": row["src_id"], "corpus": corpus,
            "fuzzy": [j for j, _ in f_hits], "semantic": [j for j, _ in s_hits], "hybrid": hybrid,
            "candidates": cand,
            "fuzzy_best": round(f_hits[0][1], 2) if f_hits else 0.0,
            "cos_best": round(s_hits[0][1], 4) if s_hits else 0.0,
        })
    return out


def run_retrieval(data_dir: Path, cfg: dict, out_path: Path, log=print) -> None:
    rows = []
    for corpus in cfg["corpora"]:
        rows += retrieve_corpus(data_dir, corpus, cfg, log)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    log(f"wrote {len(rows):,} candidate sets → {out_path}")


def load_candidates(path: Path) -> dict[str, dict]:
    return {r["src_id"]: r for r in read_jsonl(path)}


def condition_candidates(cands: dict, condition: str, k: int) -> list[int]:
    """TM indices shown to the translator under each raw-context condition (fixed rank order)."""
    key = {"fuzzy_ctx": "fuzzy", "semantic_ctx": "semantic", "hybrid_ctx": "hybrid",
           "structured_ctx": "hybrid", "draft_ctx": "hybrid"}.get(condition)
    return [] if key is None else cands[key][:k]
