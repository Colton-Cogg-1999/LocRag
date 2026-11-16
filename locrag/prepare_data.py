"""Build a translation memory + held-out test set from an OPUS corpus (default: EMEA en-es).

Output (data/tm/<corpus>/):
  tm.jsonl     {"id", "src", "tgt"}           the translation memory
  test.jsonl   {"id", "src", "tgt", "band"}   held-out segments (exact source never in TM),
                                              stratified by best CAT fuzzy band
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from locrag.retrievers import FuzzyRetriever, band_of

ROOT = Path(__file__).resolve().parent.parent
_ALPHA = re.compile(r"[A-Za-z]")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def load_pairs(corpus: str, min_words: int, max_words: int):
    raw = ROOT / "data" / "raw" / corpus
    en = (raw / f"{corpus}.en-es.en").open(encoding="utf-8")
    es = (raw / f"{corpus}.en-es.es").open(encoding="utf-8")
    seen = set()
    for s, t in zip(en, es):
        s, t = s.strip(), t.strip()
        n = len(s.split())
        if not (min_words <= n <= max_words) or len(_ALPHA.findall(s)) < 0.6 * len(s.replace(" ", "")):
            continue
        if not t or not 0.5 < len(t) / len(s) < 2.2:  # crude misalignment filter
            continue
        k = norm(s)
        if k in seen:
            continue
        seen.add(k)
        yield s, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="EMEA")
    ap.add_argument("--tm-size", type=int, default=20000)
    ap.add_argument("--per-band", type=int, default=40)
    ap.add_argument("--min-words", type=int, default=6)
    ap.add_argument("--max-words", type=int, default=40)
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args()

    rng = random.Random(a.seed)
    pairs = list(load_pairs(a.corpus, a.min_words, a.max_words))
    print(f"{len(pairs):,} unique pairs after filtering")
    rng.shuffle(pairs)
    tm_pairs = pairs[: a.tm_size]
    pool = pairs[a.tm_size: a.tm_size + 6000]  # candidates for the test set

    tm = [{"id": f"tm{i}", "src": s, "tgt": t} for i, (s, t) in enumerate(tm_pairs)]
    fz = FuzzyRetriever(tm)
    buckets: dict[str, list] = {}
    for s, t in pool:
        hits = fz.search(s, k=1)
        b = band_of(hits[0].score if hits else 0.0)
        if b == "100" or len(buckets.setdefault(b, [])) >= a.per_band:
            continue
        buckets[b].append((s, t))
        if all(len(buckets.get(x, [])) >= a.per_band for x in ("95-99", "85-94", "75-84", "50-74", "<50")):
            break
    test = [{"id": f"t{b}-{i}", "src": s, "tgt": t, "band": b}
            for b, items in buckets.items() for i, (s, t) in enumerate(items) if b != "100"]

    out = ROOT / "data" / "tm" / a.corpus
    out.mkdir(parents=True, exist_ok=True)
    with (out / "tm.jsonl").open("w", encoding="utf-8") as f:
        for r in tm:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (out / "test.jsonl").open("w", encoding="utf-8") as f:
        for r in test:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"TM: {len(tm):,}  test: {len(test)}  bands: { {b: len(v) for b, v in buckets.items()} }")


if __name__ == "__main__":
    main()
