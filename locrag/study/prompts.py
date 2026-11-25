"""Versioned prompt templates. Every rendered prompt records TEMPLATE_VERSION and the template hash.

All translation conditions share ONE system prompt and ONE final instruction; only the context block differs.
No template ever receives a held-out reference translation.
"""
from __future__ import annotations

import json

from locrag.study.config import text_sha

TEMPLATE_VERSION = "v2.0"
LANG_NAMES = {"es": "Spanish", "de": "German", "zh_CN": "Simplified Chinese"}

SYSTEM = ("You are a professional English-to-{lang} translator specializing in {domain}. "
          "Translate the source segment accurately and naturally. Preserve its meaning exactly, including "
          "negation, numbers, units, conditions and placeholders (such as %1, &File or <b>). "
          "Output only the {lang} translation of the source segment, with no notes or quotation marks.")

TASK = "Translate this English source segment into {lang}.\n\nSource: {src}"

RAW_HEADER = ("Reference material: previously approved translations from a translation memory. These "
              "historical segments are NOT translations of the source segment and may differ in meaning, "
              "scope, negation or detail. Reuse their terminology and phrasing only where it fits the source "
              "segment; wherever they conflict with the source, follow the source.")

STRUCT_HEADER = ("Reusable context extracted from previously approved translations in a translation memory. "
                 "The historical segments were NOT translations of the source segment. Apply an item only "
                 "where it fits the source segment, and always follow the meaning of the source segment.")


DRAFT_HEADER = ("Below is a previously approved translation of a similar English sentence from a translation memory. "
                "Use it as a possible starting draft. It translates a DIFFERENT sentence, so it may differ from the "
                "source segment in meaning, scope, negation, numbers or detail. Keep its wording wherever it still "
                "correctly translates the source segment, and change, add or remove whatever differs. If it is not a "
                "useful starting point, translate from scratch.")


def draft_context_block(pairs: list[tuple[str, str]], lang: str) -> str:
    """Fuzzy-match-repair framing: the top pair is a draft to adapt; remaining pairs are references."""
    if not pairs:
        return ""
    (s0, t0), rest = pairs[0], pairs[1:]
    lines = [DRAFT_HEADER, "", f"Similar sentence: {s0}", f"Its approved {LANG_NAMES[lang]} translation (draft): {t0}"]
    if rest:
        lines += ["", "Other approved translations, for reference only:"]
        for n, (s, t) in enumerate(rest, 2):
            lines += [f"[{n}] English: {s}", f"    {LANG_NAMES[lang]}: {t}"]
    return "\n".join(lines)


def translation_messages(src: str, lang: str, domain: str, context_block: str = "") -> list[dict]:
    task = TASK.format(lang=LANG_NAMES[lang], src=src)
    user = f"{context_block}\n\n{task}" if context_block else task
    return [{"role": "system", "content": SYSTEM.format(lang=LANG_NAMES[lang], domain=domain)},
            {"role": "user", "content": user}]


def raw_context_block(pairs: list[tuple[str, str]], lang: str) -> str:
    if not pairs:
        return ""
    lines = [RAW_HEADER, ""]
    for n, (s, t) in enumerate(pairs, 1):
        lines += [f"[{n}] English: {s}", f"    {LANG_NAMES[lang]}: {t}"]
    return "\n".join(lines)


def structured_context_block(ctx: dict, lang: str) -> str:
    """ctx = {"terms": [(src, tgt)], "phrases": [(src, tgt)], "conventions": [str], "differences": [str]}.
    Empty context → "" (the condition then renders exactly the zero-shot prompt)."""
    if not any(ctx.get(k) for k in ("terms", "phrases", "conventions", "differences")):
        return ""
    lines = [STRUCT_HEADER]
    if ctx.get("terms"):
        lines += ["", "Terminology in previous translations:"] + [f'- "{s}" → "{t}"' for s, t in ctx["terms"]]
    if ctx.get("phrases"):
        lines += ["", "Phrasing in previous translations:"] + [f'- "{s}" → "{t}"' for s, t in ctx["phrases"]]
    if ctx.get("conventions"):
        lines += ["", f"{LANG_NAMES[lang]} conventions seen in previous translations:"] + [f"- {c}" for c in ctx["conventions"]]
    if ctx.get("differences"):
        lines += ["", "Differences from the historical segments (do not carry these over):"] + [f"- {d}" for d in ctx["differences"]]
    return "\n".join(lines)


EXTRACTOR = """You prepare translation-memory context for a translator. A NEW English source segment must be
translated into {lang}. Below are historical English segments with their approved {lang} translations. They are
NOT translations of the new segment.

Identify only material that the translator can safely reuse for the NEW segment:
- "terms": single terms or short noun phrases whose meaning in the new segment matches the historical segment.
- "phrases": longer expressions (verb phrases, clauses, fixed formulations) that recur with the same meaning.
- "conventions": {lang} style or formatting conventions evidenced by the historical translations and relevant to
  the new segment (e.g. formal/informal address, imperative vs. infinitive, unit or placeholder formatting).
- "differences": meaning differences between a historical segment and the new segment that the translator must NOT
  carry over (e.g. "historical segment says persistent dizziness; new segment says severe dizziness").

Rules:
- Copy "source" verbatim from the historical English segment, "target" verbatim from its {lang} translation, and
  "new_source_span" verbatim from the NEW segment. Do not paraphrase, correct or invent spans.
- Include an item only if the target span is the translation of the source span in that historical pair AND the
  new segment uses that expression with the same meaning.
- Never present a historical translation as a translation of the new segment.
- At most 6 terms, 4 phrases, 3 conventions and 4 differences. Empty lists are fine.

NEW segment: {src}

Historical pairs:
{pairs}

Reply with JSON only:
{{"terms": [{{"pair": 1, "source": "...", "target": "...", "new_source_span": "..."}}],
  "phrases": [{{"pair": 1, "source": "...", "target": "...", "new_source_span": "..."}}],
  "conventions": ["..."],
  "differences": [{{"pair": 1, "note": "..."}}]}}"""


def extractor_messages(src: str, lang: str, pairs: list[tuple[str, str]]) -> list[dict]:
    listing = "\n".join(f"[{n}] English: {s}\n    {LANG_NAMES[lang]}: {t}" for n, (s, t) in enumerate(pairs, 1))
    return [{"role": "user", "content": EXTRACTOR.format(lang=LANG_NAMES[lang], src=src, pairs=listing)}]


REUSE_LABELS = ("full", "partial", "terminology", "style_convention", "none", "misleading")

REUSE = """You audit translation-memory (TM) retrieval for a {lang} localization project ({domain}).
A NEW English source segment must be translated. For each retrieved historical TM pair below, classify how much of
its approved {lang} translation is genuinely reusable for translating the NEW segment.

Labels (choose the single most valuable applicable label):
- "full": the historical English means the same as the new segment; its translation could be reused with at most
  trivial edits (punctuation, a placeholder, a number that is visibly different).
- "partial": a clause or a substantial multi-word phrase of the historical translation can be reused verbatim for
  part of the new segment.
- "terminology": only specific terms (domain terms, UI labels, product or substance names) carry over.
- "style_convention": no specific wording carries over, but the translation shows a convention relevant to the new
  segment (register, address form, imperative style, unit/placeholder formatting).
- "none": nothing useful for this segment.
- "misleading": the pair looks relevant, but reusing it would likely introduce an error (different negation,
  number, dosage, condition, scope, or a different sense of a shared term).

For every label except "none" and "style_convention", give at most 2 evidence items: a span copied verbatim from
the historical {lang} translation and the verbatim span of the NEW segment it would translate. Set "risk" to true
when the pair also contains content that would be wrong for the new segment. "note": at most 15 words, only for
"misleading" or risk=true; otherwise "".

NEW segment: {src}

Historical TM pairs:
{pairs}

Reply with JSON only, one object per pair, in order:
{{"pairs": [{{"id": 1, "label": "...", "evidence": [{{"target_span": "...", "new_source_span": "..."}}], "risk": false, "note": ""}}]}}"""


def reuse_messages(src: str, lang: str, domain: str, pairs: list[tuple[str, str]]) -> list[dict]:
    listing = "\n".join(f"[{n}] English: {s}\n    {LANG_NAMES[lang]}: {t}" for n, (s, t) in enumerate(pairs, 1))
    return [{"role": "user", "content": REUSE.format(lang=LANG_NAMES[lang], domain=domain, src=src, pairs=listing)}]


EXTRACTION_AUDIT = """You audit an automatic extractor that pulled reusable translation-memory context for a
{lang} translator. Judge each extracted item strictly against the historical pairs and the NEW segment.

NEW segment: {src}

Historical pairs:
{pairs}

Extracted items:
{items}

For each item answer:
- "mapping_correct": in that historical pair, is "target" the correct translation of "source"? (differences: is the
  stated difference factually true of the two English segments?)
- "applies": does the NEW segment use the expression with the same meaning, so that reusing the target is correct?
  (conventions/differences: is it relevant and would following it be correct?)
Reply with JSON only: {{"items": [{{"id": 1, "mapping_correct": true, "applies": true, "note": ""}}]}}"""


def extraction_audit_messages(src: str, lang: str, pairs: list[tuple[str, str]], items: list[dict]) -> list[dict]:
    listing = "\n".join(f"[{n}] English: {s}\n    {LANG_NAMES[lang]}: {t}" for n, (s, t) in enumerate(pairs, 1))
    item_lines = "\n".join(f"{i}. {json.dumps(it, ensure_ascii=False)}" for i, it in enumerate(items, 1))
    return [{"role": "user", "content": EXTRACTION_AUDIT.format(lang=LANG_NAMES[lang], src=src, pairs=listing,
                                                                items=item_lines)}]


MQM = """You are an expert {lang} translation reviewer ({domain}). Annotate the errors in the translation of the
English source using MQM. Judge only this translation against the source; there is no other information.

Categories: accuracy/mistranslation, accuracy/omission, accuracy/addition, accuracy/untranslated,
accuracy/negation, accuracy/number, terminology, fluency, style, locale.
Severities: minor, major (changes or obscures meaning, or would mislead a user), critical (could cause harm).

Source: {src}
Translation: {hyp}

Reply with JSON only: {{"errors": [{{"span": "...", "category": "...", "severity": "...", "note": "..."}}]}}"""


def mqm_messages(src: str, hyp: str, lang: str, domain: str) -> list[dict]:
    return [{"role": "user", "content": MQM.format(lang=LANG_NAMES[lang], domain=domain, src=src, hyp=hyp)}]


def template_hashes() -> dict:
    return {name: text_sha(t) for name, t in {
        "system": SYSTEM, "task": TASK, "raw_header": RAW_HEADER, "struct_header": STRUCT_HEADER, "draft_header": DRAFT_HEADER,
        "extractor": EXTRACTOR, "reuse": REUSE, "extraction_audit": EXTRACTION_AUDIT, "mqm": MQM}.items()}
