"""Row features and automatic contamination detectors (heuristic flags, not error proofs).

Terminology density (proxy): share of a source's content tokens that are domain-specific, where a token is
domain-specific if it is ≥10× more frequent (relative, add-one smoothed) in its own corpus's TM sources than in
the other corpus's TM sources and occurs ≥3 times in its own corpus. EMEA and KDE4 serve as each other's
contrast corpus. This is a lexical proxy, not a terminology database.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_WORD = re.compile(r"[A-Za-z][A-Za-z\-]{2,}")
STOP = set("""the and for with that this from are was were has have had not but you your can will may
should into when which their they them then than there these those been being its also any all each other
more most such only over under per after before about between while where what who how why use used using""".split())

NEGATION = {
    "en": re.compile(r"\b(no|not|never|none|nor|neither|cannot|can't|don't|doesn't|won't|without)\b|n't\b", re.I),
    "es": re.compile(r"\b(no|nunca|jamás|ningún|ninguna|ninguno|ni|tampoco|nada|nadie)\b", re.I),
    "de": re.compile(r"\b(nicht|kein|keine|keinen|keinem|keiner|keines|nie|niemals|weder|nichts|niemand)\b", re.I),
    "zh_CN": re.compile(r"[不没無无未勿非别否]"),
}
_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def content_tokens(text: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(text) if t.lower() not in STOP]


class TermDensity:
    def __init__(self, corpus_sources: dict[str, list[str]], ratio: float = 10.0, min_count: int = 3):
        self.counts = {c: Counter(t for s in srcs for t in content_tokens(s)) for c, srcs in corpus_sources.items()}
        self.totals = {c: sum(v.values()) for c, v in self.counts.items()}
        self.ratio, self.min_count = ratio, min_count

    def is_term(self, tok: str, corpus: str) -> bool:
        own = self.counts[corpus][tok]
        if own < self.min_count:
            return False
        others = [c for c in self.counts if c != corpus]
        if not others:
            return False
        rel_own = (own + 1) / (self.totals[corpus] + 1)
        rel_other = max((self.counts[o][tok] + 1) / (self.totals[o] + 1) for o in others)
        return rel_own / rel_other >= self.ratio

    def density(self, text: str, corpus: str) -> float:
        toks = content_tokens(text)
        return sum(self.is_term(t, corpus) for t in toks) / len(toks) if toks else 0.0


def numbers(text: str) -> Counter:
    return Counter(re.sub(r"[.,]", "", n) for n in _NUM.findall(text))


def number_mismatch(src: str, hyp: str) -> bool:
    return numbers(src) != numbers(hyp)


def has_negation(text: str, lang: str) -> bool:
    return bool(NEGATION[lang].search(text))


def negation_mismatch(src: str, hyp: str, lang: str) -> bool:
    return has_negation(src, "en") != has_negation(hyp, lang)


def ngrams(text: str, lang: str, n: int | None = None) -> set:
    if lang == "zh_CN":
        s = re.sub(r"\s+", "", text)
        n = n or 3
        return {s[i:i + n] for i in range(len(s) - n + 1)}
    toks = re.findall(r"\w+", text.lower())
    n = n or 3
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def tm_induced_ngrams(hyp: str, baseline: str, tm_targets: list[str], lang: str) -> int:
    """n-grams in the output that also occur in a shown TM target but not in the zero-shot output."""
    h = ngrams(hyp, lang)
    tm = set().union(*(ngrams(t, lang) for t in tm_targets)) if tm_targets else set()
    return len((h & tm) - ngrams(baseline, lang))


def length_ratio(src: str, hyp: str) -> float:
    return len(hyp) / max(1, len(src))


def log_or_zero(x: float) -> float:
    return math.log(x) if x > 0 else 0.0
