"""Exact word-level fuzzy matching over a whole TM.

The score is the same as `locrag.retrievers.cat_fuzzy`: 100 × normalized word-level Levenshtein similarity
(1 − distance / max(len_a, len_b)) over lower-cased word/punctuation tokens. Each distinct token is
mapped to one Unicode code point, so rapidfuzz's bit-parallel *string* Levenshtein computes the
*word*-level distance exactly. This removes the v1 character prefilter, which missed the true best
match for 26/300 audited queries.
"""
from __future__ import annotations

import numpy as np
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

from locrag.retrievers import tokens

_SURROGATES = range(0xD800, 0xE000)


def _code_point(i: int) -> str:
    cp = 0x100 + i
    if cp >= _SURROGATES.start:
        cp += len(_SURROGATES)
    if cp > 0x10FFFF:
        raise ValueError("Token vocabulary too large for code-point encoding")
    return chr(cp)


class ExactFuzzyIndex:
    def __init__(self, sources: list[str]):
        self.vocab: dict[str, str] = {}
        self.encoded = [self._encode(s, grow=True) for s in sources]

    def _encode(self, text: str, grow: bool = False) -> str:
        out, local = [], {}
        for tok in tokens(text):
            ch = self.vocab.get(tok)
            if ch is None:
                if grow:
                    ch = self.vocab[tok] = _code_point(len(self.vocab))
                else:  # unseen query token: a private code point that matches nothing in the TM
                    ch = local.setdefault(tok, _code_point(len(self.vocab) + len(local)))
            out.append(ch)
        return "".join(out)

    def search(self, query: str, k: int = 5, exclude: set[int] | None = None) -> list[tuple[int, float]]:
        """Top-k (tm_index, score 0–100), ties broken by lower index."""
        q = self._encode(query)
        extra = len(exclude) if exclude else 0
        hits = process.extract(q, self.encoded, scorer=Levenshtein.normalized_similarity,
                               processor=None, limit=k + extra)
        ranked = sorted(((i, 100.0 * s) for _, s, i in hits if not exclude or i not in exclude),
                        key=lambda x: (-x[1], x[0]))
        return ranked[:k]

    def best_scores(self, queries: list[str], chunk: int = 256) -> np.ndarray:
        """Best fuzzy score (0–100) against the whole TM for many queries, multi-threaded."""
        best = np.zeros(len(queries), dtype=np.float32)
        for start in range(0, len(queries), chunk):
            enc = [self._encode(q) for q in queries[start:start + chunk]]
            m = process.cdist(enc, self.encoded, scorer=Levenshtein.normalized_similarity,
                              processor=None, dtype=np.float32, workers=-1)
            best[start:start + len(enc)] = m.max(axis=1) * 100.0
        return best


def pairwise_max(texts: list[str]) -> np.ndarray:
    """Symmetric word-level fuzzy matrix (0–100) among a small set of texts; diagonal zeroed."""
    idx = ExactFuzzyIndex(texts)
    m = process.cdist(idx.encoded, idx.encoded, scorer=Levenshtein.normalized_similarity,
                      processor=None, dtype=np.float32, workers=-1) * 100.0
    np.fill_diagonal(m, 0.0)
    return m
