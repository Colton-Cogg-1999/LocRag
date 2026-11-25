"""Structured reusable-context construction (condition E) and its automatic faithfulness checks.

The extractor is treated as a fallible component:
  1. its raw JSON is logged;
  2. every term/phrase is checked verbatim: `source` ⊂ historical English, `target` ⊂ historical translation,
     `new_source_span` ⊂ new source (case-insensitive, whitespace-normalized);
  3. failing items are DROPPED before rendering and logged with the reason (pre-filter faithfulness is a result);
  4. a sample is audited semantically by an independent model (reuse.py).
"""
from __future__ import annotations

import json
import re

from locrag.study.prompts import extractor_messages, structured_context_block

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
# "(as seen in pair [2])", "in pairs 1 and 3": the structured prompt shows no numbered pairs
_PAIR_REF = re.compile(r"\s*\(?\s*(?:as\s+)?(?:seen\s+)?(?:in\s+)?(?:historical\s+)?pairs?\s*\[?\d+\]?"
                       r"(?:\s*(?:,|and|&)\s*\[?\d+\]?)*\s*\)?", re.IGNORECASE)


def strip_pair_refs(note: str) -> str:
    out = re.sub(r"\s{2,}", " ", _PAIR_REF.sub("", note))
    return re.sub(r"\s*[,;]\s*([.!?]?)$", r"\1", out).strip(" ,;")


def parse_json_object(raw: str) -> dict:
    """First complete JSON object in the reply (tolerates code fences and trailing text/objects)."""
    raw = raw or ""
    dec = json.JSONDecoder()
    for start in (i for i, ch in enumerate(raw) if ch == "{"):
        try:
            value, _ = dec.raw_decode(raw, start)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError(f"No JSON object in reply: {raw[:200]!r}")


def _norm(s: str) -> str:
    return " ".join(str(s).casefold().split())


def contains(haystack: str, needle: str) -> bool:
    n = _norm(needle)
    return bool(n) and n in _norm(haystack)


def validate_extraction(raw: dict, src: str, pairs: list[tuple[str, str]]) -> dict:
    """Returns {"kept": {...render ctx...}, "items": [...with checks...], "stats": {...}}."""
    items, kept = [], {"terms": [], "phrases": [], "conventions": [], "differences": []}
    seen = set()
    for kind in ("terms", "phrases"):
        for it in raw.get(kind) or []:
            if not isinstance(it, dict):
                items.append({"kind": kind, "raw": it, "ok": False, "reason": "not an object"})
                continue
            rec = {"kind": kind, "pair": it.get("pair"), "source": str(it.get("source", "")),
                   "target": str(it.get("target", "")), "new_source_span": str(it.get("new_source_span", ""))}
            try:
                p = int(rec["pair"]) - 1
                hs, ht = pairs[p]
            except (TypeError, ValueError, IndexError):
                rec.update(ok=False, reason="invalid pair index")
                items.append(rec)
                continue
            checks = {"source_in_historical": contains(hs, rec["source"]),
                      "target_in_historical": contains(ht, rec["target"]),
                      "span_in_new_source": contains(src, rec["new_source_span"])}
            rec.update(checks)
            rec["ok"] = all(checks.values())
            rec["reason"] = "" if rec["ok"] else ",".join(k for k, v in checks.items() if not v)
            items.append(rec)
            key = (kind, _norm(rec["source"]), _norm(rec["target"]))
            if rec["ok"] and key not in seen:
                seen.add(key)
                kept[kind].append((rec["source"], rec["target"]))
    for c in raw.get("conventions") or []:
        if isinstance(c, str) and c.strip():
            items.append({"kind": "conventions", "note": c.strip(), "ok": True, "reason": ""})
            if strip_pair_refs(c):
                kept["conventions"].append(strip_pair_refs(c))
    for d in raw.get("differences") or []:
        note = d.get("note") if isinstance(d, dict) else d
        if isinstance(note, str) and note.strip():
            items.append({"kind": "differences", "pair": d.get("pair") if isinstance(d, dict) else None,
                          "note": note.strip(), "ok": True, "reason": ""})
            if strip_pair_refs(note):
                kept["differences"].append(strip_pair_refs(note))
    spans = [i for i in items if i["kind"] in ("terms", "phrases")]
    stats = {"n_items": len(items), "n_span_items": len(spans), "n_span_ok": sum(i["ok"] for i in spans),
             "n_rendered": sum(len(v) for v in kept.values())}
    return {"kept": kept, "items": items, "stats": stats}


def extract(client, cfg: dict, src: str, lang: str, pairs: list[tuple[str, str]]) -> dict:
    """Run the extractor (one repair attempt on malformed JSON). Never raises on bad model output:
    a failed extraction yields an empty context, recorded with its error."""
    ecfg, tcfg = cfg["extractor"], cfg["translation"]
    msgs = extractor_messages(src, lang, pairs)
    calls, raw_text, parsed, error = [], "", None, ""
    kw = dict(model=ecfg["model"], temperature=ecfg["temperature"], max_tokens=ecfg["max_tokens"],
              seed=tcfg.get("seed"), reasoning_effort=tcfg.get("reasoning_effort"), provider=tcfg.get("provider"))
    res = client.complete(msgs, **kw)
    calls.append(res.accounting())
    raw_text = res.text
    try:
        parsed = parse_json_object(raw_text)
    except (ValueError, json.JSONDecodeError):
        repair = msgs + [{"role": "assistant", "content": raw_text or "(empty)"},
                         {"role": "user", "content": "That was not valid JSON. Reply again with only the JSON object."}]
        res = client.complete(repair, **kw)
        calls.append(res.accounting())
        raw_text = res.text
        try:
            parsed = parse_json_object(raw_text)
        except (ValueError, json.JSONDecodeError) as exc:
            error = f"unparseable extractor output: {exc}"[:300]
    validated = validate_extraction(parsed or {}, src, pairs)
    return {"raw_text": raw_text, "parsed": parsed, "error": error, "calls": calls, **validated,
            "context_block": structured_context_block(validated["kept"], lang)}
