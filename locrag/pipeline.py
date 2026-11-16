"""TM router: CAT-style fuzzy lookup, with semantic retrieval (RAG) when fuzzy matching fails.

    new segment ─► fuzzy lookup ─► best ≥ X% ─► "fuzzy": fuzzy matches → LLM context
                               └─► best < X% ─► semantic search ─► sim ≥ S ─► "semantic": RAG
                                                                └─► else ────► "none": zero-shot

  uv run python -m locrag.pipeline "Your new English segment here."
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from common.llm import MT_MODEL, chat, clean_translation
from locrag.retrievers import FuzzyRetriever, Hit, SemanticRetriever

ROOT = Path(__file__).resolve().parent.parent
FUZZY_THRESHOLD = float(os.environ.get("L10N_FUZZY_THRESHOLD", 75))
SEMANTIC_MIN_SIM = float(os.environ.get("L10N_SEMANTIC_MIN_SIM", 80))  # cosine × 100

SYSTEM = ("You are a professional English-to-Spanish translator for EU medicinal product information "
          "(SmPC and package leaflets). Previously approved translations from the translation memory are "
          "provided when available: reuse their terminology and phrasing wherever they apply to the new "
          "sentence, but translate the NEW sentence's meaning exactly (do not copy differences). "
          "Output only the Spanish translation.")


@dataclass
class Routed:
    src: str
    route: str                      # fuzzy | semantic | none
    fuzzy_best: float
    fuzzy_best_src: str
    examples: list[dict] = field(default_factory=list)
    translation: str | None = None


def build_prompt(src: str, examples: list[dict]) -> str:
    parts = []
    if examples:
        parts.append("Approved translations from the translation memory:")
        for e in examples:
            parts.append(f"EN: {e['src']}\nES: {e['tgt']}")
        parts.append("")
    parts.append(f"Translate:\nEN: {src}\nES:")
    return "\n".join(parts)


def translate(src: str, examples: list[dict], model: str = MT_MODEL) -> str:
    out = chat(build_prompt(src, examples), system=SYSTEM, model=model, max_tokens=400).strip()
    return clean_translation(out)


class TMRouter:
    def __init__(self, tm: list[dict], fuzzy_threshold: float = FUZZY_THRESHOLD,
                 semantic_min_sim: float = SEMANTIC_MIN_SIM, k: int = 3):
        self.tm = tm
        self.fuzzy = FuzzyRetriever(tm)
        self.semantic = SemanticRetriever(tm)
        self.fuzzy_threshold, self.semantic_min_sim, self.k = fuzzy_threshold, semantic_min_sim, k

    @staticmethod
    def _ex(h: Hit) -> dict:
        return {"src": h.src, "tgt": h.tgt, "score": round(h.score, 1), "tm_index": h.idx}

    def route(self, src: str, qvec=None) -> Routed:
        f_hits = self.fuzzy.search(src, k=self.k)
        best = f_hits[0] if f_hits else None
        r = Routed(src, "none", best.score if best else 0.0, best.src if best else "")
        if best and best.score >= self.fuzzy_threshold:
            r.route = "fuzzy"
            r.examples = [self._ex(h) for h in f_hits if h.score >= self.fuzzy_threshold]
            return r
        s_hits = self.semantic.search_vec(qvec, self.k) if qvec is not None else self.semantic.search(src, self.k)
        good = [h for h in s_hits if h.score >= self.semantic_min_sim]
        if good:
            r.route = "semantic"
            r.examples = [self._ex(h) for h in good]
        return r

    def translate(self, src: str, qvec=None) -> Routed:
        r = self.route(src, qvec)
        r.translation = translate(src, r.examples)
        return r


def load_tm(corpus: str = "EMEA") -> list[dict]:
    return [json.loads(l) for l in (ROOT / "data" / "tm" / corpus / "tm.jsonl").open(encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    a = ap.parse_args()
    router = TMRouter(load_tm())
    r = router.translate(a.text)
    print(f"\nbest fuzzy match: {r.fuzzy_best:.0f}%  ({'shown' if r.fuzzy_best >= router.fuzzy_threshold else 'below threshold: a CAT tool shows nothing'})")
    print(f"  {r.fuzzy_best_src}")
    print(f"\nroute: {r.route.upper()}")
    for e in r.examples:
        print(f"  [{e['score']:.0f}] EN: {e['src']}\n        ES: {e['tgt']}")
    print(f"\ntranslation: {r.translation}")
    if r.route != "fuzzy":
        print(f"zero-shot:   {translate(a.text, [])}")


if __name__ == "__main__":
    main()
