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
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from openai import APIError

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

LANGUAGES = {"es": "Spanish", "de": "German", "zh_CN": "Simplified Chinese"}


@dataclass(frozen=True)
class TranslationTask:
    target: str = "es"
    domain: str = "EU medicinal product information"

    def __post_init__(self):
        if self.target not in LANGUAGES:
            raise ValueError(f"Unsupported target language: {self.target}")

    @property
    def system(self) -> str:
        if self.target == "es" and self.domain == "EU medicinal product information":
            return SYSTEM
        return (f"You are a professional English-to-{LANGUAGES[self.target]} translator for {self.domain}. "
                "Translation-memory examples are provided when available. Reuse terminology only where "
                "it applies, and translate the NEW sentence's meaning exactly. Preserve numbers, negation, "
                "conditions and placeholders. Memory entries may contain errors. "
                f"Output only the {LANGUAGES[self.target]} translation.")


@dataclass
class Routed:
    src: str
    route: str                      # fuzzy | semantic | none
    fuzzy_best: float
    fuzzy_best_src: str
    examples: list[dict] = field(default_factory=list)
    translation: str | None = None
    reason: str = ""
    retrieval_ms: float | None = None
    translation_ms: float | None = None


def build_prompt(src: str, examples: list[dict], task: TranslationTask | None = None) -> str:
    label = (task.target if task else "es").upper()
    parts = []
    if examples:
        parts.append("Approved translations from the translation memory:")
        for e in examples:
            parts.append(f"EN: {e['src']}\n{label}: {e['tgt']}")
        parts.append("")
    parts.append(f"Translate:\nEN: {src}\n{label}:")
    return "\n".join(parts)


def translate(src: str, examples: list[dict], model: str = MT_MODEL,
              task: TranslationTask | None = None) -> str:
    task = task or TranslationTask()
    out = chat(build_prompt(src, examples, task), system=task.system, model=model, max_tokens=400).strip()
    cleaned = clean_translation(out)
    if not cleaned:
        raise RuntimeError("The translation provider returned no usable translation. Retry or check the model configuration.")
    return cleaned


class TMRouter:
    def __init__(self, tm: list[dict], fuzzy_threshold: float = FUZZY_THRESHOLD,
                 semantic_min_sim: float = SEMANTIC_MIN_SIM, k: int = 3,
                 *, fuzzy=None, semantic=None, model: str | None = None):
        for name, value in (("fuzzy_threshold", fuzzy_threshold), ("semantic_min_sim", semantic_min_sim)):
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError(f"{name} must be finite and between 0 and 100")
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        if any(not isinstance(r, dict) or not isinstance(r.get("src"), str) or not r["src"].strip()
               or not isinstance(r.get("tgt"), str) or not r["tgt"].strip() for r in tm):
            raise ValueError("Each translation-memory entry needs non-empty src and tgt strings")
        self.tm = tm
        self.fuzzy = fuzzy if fuzzy is not None else FuzzyRetriever(tm)
        self._semantic = semantic
        self.model = model
        self.fuzzy_threshold, self.semantic_min_sim, self.k = fuzzy_threshold, semantic_min_sim, k

    @property
    def semantic(self):
        # A strong fuzzy match must not require an embedding download or API call.
        if self._semantic is None:
            self._semantic = SemanticRetriever(self.tm, model=self.model)
        return self._semantic

    @staticmethod
    def _ex(h: Hit) -> dict:
        return {"src": h.src, "tgt": h.tgt, "score": round(h.score, 1), "tm_index": h.idx}

    def route(self, src: str, qvec=None, *, policy: str = "router") -> Routed:
        if not src.strip():
            raise ValueError("Source text must not be empty")
        if policy not in ("router", "fuzzy-only", "always-semantic"):
            raise ValueError(f"Unknown routing policy: {policy}")
        started = time.perf_counter()
        f_hits = self.fuzzy.search(src, k=self.k)
        best = f_hits[0] if f_hits else None
        r = Routed(src, "none", best.score if best else 0.0, best.src if best else "")
        if best and best.score >= self.fuzzy_threshold and policy != "always-semantic":
            r.route = "fuzzy"
            r.examples = [self._ex(h) for h in f_hits if h.score >= self.fuzzy_threshold]
            r.reason = f"Fuzzy match meets the {self.fuzzy_threshold:g}% threshold."
            r.retrieval_ms = (time.perf_counter() - started) * 1000
            return r
        if not self.tm or policy == "fuzzy-only":
            r.reason = "No memory entries available." if not self.tm else "No fuzzy match meets the threshold."
            r.retrieval_ms = (time.perf_counter() - started) * 1000
            return r
        s_hits = self.semantic.search_vec(qvec, self.k) if qvec is not None else self.semantic.search(src, self.k)
        good = s_hits if policy == "always-semantic" else [h for h in s_hits if h.score >= self.semantic_min_sim]
        if good:
            r.route = "semantic"
            r.examples = [self._ex(h) for h in good]
            r.reason = ("Always-semantic experimental policy uses top-k matches without a floor."
                        if policy == "always-semantic" else
                        f"Fuzzy match is below threshold; semantic similarity meets {self.semantic_min_sim / 100:g}.")
        else:
            r.reason = "Neither retrieval threshold is met; translate without memory examples."
        r.retrieval_ms = (time.perf_counter() - started) * 1000
        return r

    def translate(self, src: str, qvec=None, *, task: TranslationTask | None = None) -> Routed:
        r = self.route(src, qvec)
        started = time.perf_counter()
        r.translation = translate(src, r.examples, task=task)
        r.translation_ms = (time.perf_counter() - started) * 1000
        return r


def load_tm(corpus: str = "EMEA") -> list[dict]:
    return [json.loads(l) for l in (ROOT / "data" / "tm" / corpus / "tm.jsonl").open(encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--tm", type=Path, help="JSONL translation memory with src/tgt fields")
    ap.add_argument("--json", action="store_true", help="Emit the decision, examples and timings as JSON")
    ap.add_argument("--fuzzy-threshold", type=float, default=FUZZY_THRESHOLD)
    ap.add_argument("--semantic-min-sim", type=float, default=SEMANTIC_MIN_SIM, help="Cosine similarity × 100")
    ap.add_argument("--target", choices=LANGUAGES, default="es")
    ap.add_argument("--domain", default="EU medicinal product information")
    a = ap.parse_args()
    try:
        tm = [json.loads(line) for line in a.tm.read_text().splitlines()] if a.tm else load_tm()
        router = TMRouter(tm, fuzzy_threshold=a.fuzzy_threshold, semantic_min_sim=a.semantic_min_sim)
        task = TranslationTask(a.target, a.domain)
        r = router.translate(a.text, task=task)
    except (OSError, ValueError, RuntimeError) as exc:
        ap.exit(1, f"LocRAG: {exc}\n")
    except APIError as exc:
        ap.exit(1, f"LocRAG: provider request failed ({type(exc).__name__}). Check endpoint, credentials and model availability.\n")
    if a.json:
        print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
        return
    print(f"\nbest fuzzy match: {r.fuzzy_best:.0f}%  ({'shown' if r.fuzzy_best >= router.fuzzy_threshold else 'below threshold: a CAT tool shows nothing'})")
    print(f"  {r.fuzzy_best_src}")
    print(f"\nroute: {r.route.upper()}")
    for e in r.examples:
        print(f"  [{e['score']:.0f}] EN: {e['src']}\n        ES: {e['tgt']}")
    print(f"\ntranslation: {r.translation}")
    if r.route != "fuzzy":
        print(f"zero-shot:   {translate(a.text, [], task=task)}")


if __name__ == "__main__":
    main()
