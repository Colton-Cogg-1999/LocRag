"""TM retrievers: CAT-style fuzzy matching vs. semantic (embedding) search vs. hybrid."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from rapidfuzz import fuzz, process
from rapidfuzz.distance import Levenshtein

ROOT = Path(__file__).resolve().parent.parent
_TOK = re.compile(r"\w+|[^\w\s]")

BANDS = [(100, "100"), (95, "95-99"), (85, "85-94"), (75, "75-84"), (50, "50-74"), (0, "<50")]


def band_of(score: float) -> str:
    for lo, name in BANDS:
        if score >= lo:
            return name
    return "<50"


@dataclass
class Hit:
    idx: int
    score: float  # fuzzy: 0-100 ; semantic: cosine*100 ; hybrid: rrf
    src: str
    tgt: str


def tokens(s: str) -> list[str]:
    return _TOK.findall(s.lower())


def cat_fuzzy(a: str, b: str) -> float:
    """Word-level Levenshtein similarity in %, roughly what Trados/memoQ show."""
    return 100.0 * Levenshtein.normalized_similarity(tokens(a), tokens(b))


class FuzzyRetriever:
    """Classic TM lookup: char-level prefilter (like an n-gram index), word-level edit-distance score."""

    name = "fuzzy"

    def __init__(self, tm: list[dict], prefilter: int = 100):
        self.tm = tm
        self.srcs = [r["src"] for r in tm]
        self.srcs_lc = [s.lower() for s in self.srcs]
        self.prefilter = prefilter

    def search(self, query: str, k: int = 5) -> list[Hit]:
        cands = process.extract(query.lower(), self.srcs_lc, scorer=fuzz.ratio, limit=self.prefilter)
        scored = sorted(((cat_fuzzy(query, self.srcs[i]), i) for _, _, i in cands), reverse=True)[:k]
        return [Hit(i, s, self.tm[i]["src"], self.tm[i]["tgt"]) for s, i in scored]


class SemanticRetriever:
    """Embedding search over TM sources (cosine, exact via matrix product; fine to ~1M on CPU)."""

    def __init__(self, tm: list[dict], model: str | None = None, query_prefix: str = "",
                 doc_prefix: str = "", cache_dir: Path = ROOT / ".cache" / "emb"):
        from common.embed import RETRIEVAL_MODEL, embed

        model = model or RETRIEVAL_MODEL
        self.tm, self.model = tm, model
        self.name = "semantic:" + model.split("/")[-1]
        self.query_prefix = query_prefix
        self._embed = embed
        h = hashlib.sha1(("\n".join(r["src"] for r in tm) + model + doc_prefix).encode()).hexdigest()[:12]
        cache = cache_dir / f"{model.replace('/', '_')}_{h}.npy"
        if cache.exists():
            self.mat = np.load(cache)
        else:
            cache.parent.mkdir(parents=True, exist_ok=True)
            self.mat = embed([doc_prefix + r["src"] for r in tm], model, show_progress=True)
            np.save(cache, self.mat)

    def encode_queries(self, queries: list[str]) -> np.ndarray:
        return self._embed([self.query_prefix + q for q in queries], self.model)

    def search_vec(self, qv: np.ndarray, k: int = 5) -> list[Hit]:
        sims = self.mat @ qv
        top = np.argpartition(-sims, k)[:k]
        top = top[np.argsort(-sims[top])]
        return [Hit(int(i), float(sims[i]) * 100, self.tm[i]["src"], self.tm[i]["tgt"]) for i in top]

    def search(self, query: str, k: int = 5) -> list[Hit]:
        return self.search_vec(self.encode_queries([query])[0], k)


class HybridRetriever:
    """Reciprocal-rank fusion of fuzzy + semantic (what production RAG-for-TM usually ends up as)."""

    name = "hybrid"

    def __init__(self, fuzzy: FuzzyRetriever, semantic: SemanticRetriever, depth: int = 20, c: int = 60):
        self.f, self.s, self.depth, self.c = fuzzy, semantic, depth, c

    def fuse(self, f_hits: list[Hit], s_hits: list[Hit], k: int) -> list[Hit]:
        scores: dict[int, float] = {}
        for hits in (f_hits, s_hits):
            for rank, h in enumerate(hits):
                scores[h.idx] = scores.get(h.idx, 0.0) + 1.0 / (self.c + rank + 1)
        # an exact/near-exact fuzzy match always wins: CAT tools must never lose a 95%+ match
        if f_hits and f_hits[0].score >= 95:
            scores[f_hits[0].idx] += 1.0
        top = sorted(scores, key=scores.get, reverse=True)[:k]
        tm = self.f.tm
        return [Hit(i, scores[i], tm[i]["src"], tm[i]["tgt"]) for i in top]

    def search(self, query: str, k: int = 5) -> list[Hit]:
        return self.fuse(self.f.search(query, self.depth), self.s.search(query, self.depth), k)
