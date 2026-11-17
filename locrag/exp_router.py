"""Project 2: when fuzzy matching finds nothing usable (< 75%), can semantic retrieval find a
reusable previous translation and turn it into a better translation?

  uv run python -m locrag.exp_router [--n-real 300]

Sets
  real         new EMEA segments (not in TM) whose best fuzzy match is < 75%  (human reference available)
  constructed  reworded versions of TM entries (paraphrase / restructure): a reusable translation exists by design
  risk         negated versions of TM entries, forced through the semantic path: does RAG copy the wrong meaning?

For every segment: zero-shot (what you get today: CAT shows nothing) vs semantic RAG (router output).
Judged blind (A/B order randomised) by the judge model; chrF++ vs reference where one exists.
Writes results/router/{report.md, examples.md, rows.jsonl}.
"""

from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import yaml
from sacrebleu.metrics import CHRF

from common.llm import JUDGE_MODEL, MT_MODEL, chat_json, describe, validate_judgment
from locrag.pipeline import FUZZY_THRESHOLD, SEMANTIC_MIN_SIM, TMRouter, load_tm, translate
from locrag.prepare_data import load_pairs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "router"
CHRF_M = CHRF(word_order=2)
SIM_BUCKETS = [(90, 101), (85, 90), (80, 85), (75, 80), (0, 75)]

REUSE_PROMPT = """A translator must translate a NEW English segment. The translation memory (TM) returned a
previously approved translation pair. Can the approved Spanish translation be reused for the new segment?

NEW segment: {new}
TM entry EN: {tm_src}
TM entry ES: {tm_tgt}

- "full": the TM entry means the same as the new segment; its translation can be reused with little or no editing.
- "partial": a substantial part of the new segment (a clause, key phrase or terminology) can be reused.
- "none": not usefully reusable.
Reply with JSON only: {{"reuse": "full|partial|none", "why": "<one sentence>"}}"""

PAIR_PROMPT = """Compare two Spanish translations of an English segment from EU medicinal product information
(SmPC / package leaflet). Judge ACCURACY first (meaning, negation, numbers, conditions, nothing added or
lost), then correct pharmaceutical terminology and natural regulatory style.

English source: {src}
{ref_line}
Translation A: {a}
Translation B: {b}

Reply with JSON only:
{{"a_accurate": true|false, "b_accurate": true|false, "winner": "A|B|tie", "reason": "<one sentence>"}}"""


LOC_PROMPT = """Compare two Spanish translations of a NEW English segment for a client whose translation memory
holds the approved translation below. In this localization workflow a good translation:
  1. is fully ACCURATE to the NEW segment (meaning, negation, numbers, conditions; nothing added or lost), and
  2. REUSES the client's approved terminology and phrasing wherever it fits the new segment, instead of
     inventing different wording for the same thing.
Accuracy always outweighs consistency. Generic fluency preferences do not override approved phrasing.

NEW English segment: {src}
Approved TM entry (EN): {tm_src}
Approved TM entry (ES): {tm_tgt}
{ref_line}
Translation A: {a}
Translation B: {b}

Reply with JSON only:
{{"a_accurate": true|false, "b_accurate": true|false, "a_consistent": true|false, "b_consistent": true|false,
  "winner": "A|B|tie", "reason": "<one sentence>"}}"""


# ------------------------------------------------------------------ data

def real_below_threshold(router: TMRouter, n: int, seed: int = 21) -> list[dict]:
    """New EMEA segments (never in the TM, not in the earlier test set) with best fuzzy < threshold."""
    cache = ROOT / "data" / "tm" / "EMEA" / f"below{int(FUZZY_THRESHOLD)}.jsonl"
    if cache.exists():
        rows = [json.loads(l) for l in cache.open(encoding="utf-8")]
        if len(rows) >= n:
            return rows[:n]
    pairs = list(load_pairs("EMEA", 6, 40))
    random.Random(13).shuffle(pairs)                    # same shuffle as prepare_data → [20000:] is non-TM
    used = {json.loads(l)["src"] for l in (ROOT / "data" / "tm" / "EMEA" / "test.jsonl").open(encoding="utf-8")}
    pool = [p for p in pairs[26000:] if p[0] not in used]
    random.Random(seed).shuffle(pool)
    rows = []
    for s, t in pool:
        best = router.fuzzy.search(s, k=1)
        if best and best[0].score < FUZZY_THRESHOLD:
            rows.append({"set": "real", "src": s, "ref": t, "fuzzy_best": round(best[0].score, 1)})
            if len(rows) >= n:
                break
    with cache.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def constructed_sets(tm: list[dict]) -> tuple[list[dict], list[dict]]:
    id2 = {r["id"]: r for r in tm}
    probes = yaml.safe_load((ROOT / "locrag" / "probes_emea.yaml").read_text(encoding="utf-8"))
    cons = [{"set": "constructed", "variant": v, "src": p[v], "ref": None, "origin": id2[p["tm"]]}
            for p in probes for v in ("paraphrase", "restructure")]
    risk = [{"set": "risk", "variant": "negation", "src": p["negation"], "ref": None, "origin": id2[p["tm"]]}
            for p in probes]
    return cons, risk


# ------------------------------------------------------------------ evaluation

def evaluate(router: TMRouter, items: list[dict], force_semantic: bool = False, workers: int = 8,
             policy: str = "router") -> list[dict]:
    qv = router.semantic.encode_queries([it["src"] for it in items])
    rng = random.Random(7)
    flips = [rng.random() < 0.5 for _ in items]

    def one(i):
        it = dict(items[i])
        f = router.fuzzy.search(it["src"], k=1)
        it["fuzzy_best"] = round(f[0].score, 1) if f else 0.0
        it["fuzzy_best_src"] = f[0].src if f else ""
        hits = router.semantic.search_vec(qv[i], router.k)
        it["sem_top"] = [{"src": h.src, "tgt": h.tgt, "sim": round(h.score, 1)} for h in hits]
        it["sem_top1_sim"] = it["sem_top"][0]["sim"]
        decision = router.route(it["src"], qv[i], policy="always-semantic" if force_semantic else policy)
        it["route"] = decision.route
        it["policy"] = "always-semantic" if force_semantic else policy
        it["examples_used"] = decision.examples
        it["route_reason"] = decision.reason
        it["zero_shot"] = translate(it["src"], [])
        it["rag"] = translate(it["src"], decision.examples) if decision.examples else it["zero_shot"]
        top = it["sem_top"][0]
        try:
            it["reuse"] = chat_json(REUSE_PROMPT.format(new=it["src"], tm_src=top["src"], tm_tgt=top["tgt"]),
                                    max_tokens=300, model=JUDGE_MODEL)
            validate_judgment(it["reuse"], reuse=True)
        except Exception as e:
            it["reuse"] = {"reuse": "error", "why": str(e)[:200]}
        a, b = (it["rag"], it["zero_shot"]) if flips[i] else (it["zero_shot"], it["rag"])
        ref_line = f"Human reference translation (for orientation): {it['ref']}" if it.get("ref") else ""
        try:
            j = chat_json(PAIR_PROMPT.format(src=it["src"], ref_line=ref_line, a=a, b=b), max_tokens=300,
                          model=JUDGE_MODEL)
            validate_judgment(j)
        except Exception as e:
            j = {"winner": "error", "reason": str(e)[:200]}
        rag_is_a = flips[i]
        w = str(j.get("winner", "tie")).strip().upper()
        it["pairwise"] = ("error" if w == "ERROR" else "rag" if (w == "A") == rag_is_a and w in ("A", "B")
                          else "zero_shot" if w in ("A", "B") else "tie")
        it["rag_accurate"] = bool(j.get("a_accurate") if rag_is_a else j.get("b_accurate"))
        it["zs_accurate"] = bool(j.get("b_accurate") if rag_is_a else j.get("a_accurate"))
        it["judge_reason"] = j.get("reason", "")
        try:
            L = chat_json(LOC_PROMPT.format(src=it["src"], tm_src=top["src"], tm_tgt=top["tgt"], ref_line=ref_line,
                                            a=a, b=b), max_tokens=300, model=JUDGE_MODEL)
            validate_judgment(L, localization=True)
        except Exception as e:
            L = {"winner": "error", "reason": str(e)[:200]}
        wl = str(L.get("winner", "tie")).strip().upper()
        it["loc_pairwise"] = ("error" if wl == "ERROR" else "rag" if (wl == "A") == rag_is_a and wl in ("A", "B")
                              else "zero_shot" if wl in ("A", "B") else "tie")
        it["loc_rag_accurate"] = bool(L.get("a_accurate") if rag_is_a else L.get("b_accurate"))
        it["loc_zs_accurate"] = bool(L.get("b_accurate") if rag_is_a else L.get("a_accurate"))
        it["rag_consistent"] = bool(L.get("a_consistent") if rag_is_a else L.get("b_consistent"))
        it["zs_consistent"] = bool(L.get("b_consistent") if rag_is_a else L.get("a_consistent"))
        it["loc_reason"] = L.get("reason", "")
        if it.get("ref"):
            it["chrf_zero_shot"] = CHRF_M.sentence_score(it["zero_shot"], [it["ref"]]).score
            it["chrf_rag"] = CHRF_M.sentence_score(it["rag"], [it["ref"]]).score
        # how much of the previous approved translation was reused
        it["reuse_chrf_rag"] = CHRF_M.sentence_score(it["rag"], [top["tgt"]]).score
        it["reuse_chrf_zero_shot"] = CHRF_M.sentence_score(it["zero_shot"], [top["tgt"]]).score
        return it

    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, range(len(items))))


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0}
    s = {"n": n,
         "generic_judge_errors": sum(r["pairwise"] == "error" for r in rows),
         "localization_judge_errors": sum(r["loc_pairwise"] == "error" for r in rows),
         "rag_wins": sum(r["pairwise"] == "rag" for r in rows),
         "zero_shot_wins": sum(r["pairwise"] == "zero_shot" for r in rows),
         "ties": sum(r["pairwise"] == "tie" for r in rows),
         "rag_accurate": sum(r["rag_accurate"] for r in rows),
         "zs_accurate": sum(r["zs_accurate"] for r in rows),
         "loc_rag_wins": sum(r["loc_pairwise"] == "rag" for r in rows),
         "loc_zero_shot_wins": sum(r["loc_pairwise"] == "zero_shot" for r in rows),
         "loc_ties": sum(r["loc_pairwise"] == "tie" for r in rows),
         "loc_rag_accurate": sum(r["loc_rag_accurate"] for r in rows),
         "loc_zs_accurate": sum(r["loc_zs_accurate"] for r in rows),
         "rag_consistent": sum(r["rag_consistent"] for r in rows),
         "zs_consistent": sum(r["zs_consistent"] for r in rows),
         "reuse_full": sum(r["reuse"].get("reuse") == "full" for r in rows),
         "reuse_partial": sum(r["reuse"].get("reuse") == "partial" for r in rows),
         "reuse_chrf_rag": round(float(np.mean([r["reuse_chrf_rag"] for r in rows])), 1),
         "reuse_chrf_zero_shot": round(float(np.mean([r["reuse_chrf_zero_shot"] for r in rows])), 1)}
    if all(r.get("ref") for r in rows):
        hyp = lambda k: [r[k] for r in rows]
        refs = [[r["ref"] for r in rows]]
        s["chrf_zero_shot"] = round(CHRF_M.corpus_score(hyp("zero_shot"), refs).score, 1)
        s["chrf_rag"] = round(CHRF_M.corpus_score(hyp("rag"), refs).score, 1)
    return s


def fmt_row(label, s):
    if not s.get("n"):
        return f"| {label} | 0 | | | | | |"
    chrf = f"{s['chrf_zero_shot']} → **{s['chrf_rag']}**" if "chrf_rag" in s else "n/a (no reference)"
    return (f"| {label} | {s['n']} | {s['reuse_full']} full + {s['reuse_partial']} partial | "
            f"**{s['loc_rag_wins']}** / {s['loc_ties']} / {s['loc_zero_shot_wins']} | "
            f"{s['loc_zs_accurate']} → **{s['loc_rag_accurate']}** | {s['zs_consistent']} → **{s['rag_consistent']}** | "
            f"{s['rag_wins']} / {s['ties']} / {s['zero_shot_wins']} | {chrf} | "
            f"{s['reuse_chrf_zero_shot']} → {s['reuse_chrf_rag']} |")


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-real", type=int, default=300)
    ap.add_argument("--output", type=Path, default=ROOT / "results" / "router-v2")
    ap.add_argument("--policy", choices=("router", "fuzzy-only", "always-semantic"), default="router")
    a = ap.parse_args()
    OUT = a.output
    OUT.mkdir(parents=True, exist_ok=True)
    print(describe(), flush=True)

    tm = load_tm()
    router = TMRouter(tm)
    real = real_below_threshold(router, a.n_real)
    cons, risk = constructed_sets(tm)
    print(f"real<{FUZZY_THRESHOLD:.0f}%: {len(real)}  constructed: {len(cons)}  risk: {len(risk)}", flush=True)

    R = evaluate(router, real, policy=a.policy)
    C = evaluate(router, cons, policy=a.policy)
    K = evaluate(router, risk, force_semantic=True)
    with (OUT / "rows.jsonl").open("w", encoding="utf-8") as f:
        for r in R + C + K:
            f.write(json.dumps({k: v for k, v in r.items() if k != "origin"}, ensure_ascii=False) + "\n")

    routed = [r for r in R if r["route"] == "semantic"]
    md = [f"# Project 2: semantic retrieval where fuzzy matching fails (< {FUZZY_THRESHOLD:.0f}%)", "",
          f"TM: 20,000 EMEA units (en→es). MT: **{MT_MODEL}**, k ≤ {router.k}. Retrieval: **{router.semantic.model}**. "
          f"Judge (blind A/B): **{JUDGE_MODEL}**. Semantic route used when top similarity ≥ {SEMANTIC_MIN_SIM:.0f}.", "",
          "Baseline = what happens today when the best fuzzy match is below threshold: the CAT/TMS offers nothing, "
          "so the LLM translates with no TM context (zero-shot).", "",
          "## Headline", "",
          f"* Real new segments with fuzzy < {FUZZY_THRESHOLD:.0f}%: **{len(R)}**. Semantic search found a candidate "
          f"≥ {SEMANTIC_MIN_SIM:.0f} for **{len(routed)} ({100 * len(routed) / max(1, len(R)):.0f}%)**; the judge rated the top "
          f"match reusable (full/partial) for **{sum(r['reuse'].get('reuse') in ('full', 'partial') for r in routed)}** of them.",
          f"Policy: **{a.policy}**. Risk probes deliberately force semantic context. "
          "Two rubrics from the same judge model: **localization rubric** (sees the TM entry; accuracy first, then reuse of "
          "approved terminology/phrasing) and **generic rubric** (no TM entry; accuracy then general fluency).", "",
          "| set | n | top match reusable? | **loc judge:** RAG wins / tie / zero-shot wins | accurate: zero-shot → RAG | consistent w/ approved TM: zero-shot → RAG | generic judge: RAG / tie / zero-shot | chrF++ vs human ref | chrF++ vs approved TM translation |",
          "|---|---|---|---|---|---|---|---|---|",
          fmt_row(f"real, fuzzy < {FUZZY_THRESHOLD:.0f}%, routed to semantic", summarise(routed)),
          fmt_row(f"real, fuzzy < {FUZZY_THRESHOLD:.0f}%, all decisions including declines", summarise(R)),
          fmt_row("constructed rewordings", summarise(C)),
          fmt_row("**risk:** negated rewordings forced through RAG", summarise(K)), "",
          "## Where does semantic retrieval stop helping? (real set, by top-1 similarity)", "",
          "| top-1 similarity | n | reusable (full+partial) | loc judge: RAG / tie / zero-shot | accurate: zero-shot → RAG | chrF++ zero-shot → RAG |",
          "|---|---|---|---|---|---|"]
    for lo, hi in SIM_BUCKETS:
        B = [r for r in R if lo <= r["sem_top1_sim"] < hi]
        if B:
            s = summarise(B)
            md.append(f"| {lo}–{min(hi, 100)} | {s['n']} | {s['reuse_full'] + s['reuse_partial']} | "
                      f"{s['loc_rag_wins']} / {s['loc_ties']} / {s['loc_zero_shot_wins']} | "
                      f"{s['loc_zs_accurate']} → {s['loc_rag_accurate']} | {s['chrf_zero_shot']} → {s['chrf_rag']} |")
    md += ["", "## Fuzzy band of the real set", "", "| best fuzzy | n | routed to semantic | loc judge: RAG / tie / zero-shot |", "|---|---|---|---|"]
    for lo, hi in [(50, 75), (30, 50), (0, 30)]:
        B = [r for r in R if lo <= r["fuzzy_best"] < hi]
        if B:
            s = summarise(B)
            md.append(f"| {lo}–{hi}% | {s['n']} | {sum(r['route'] == 'semantic' for r in B)} | {s['loc_rag_wins']} / {s['loc_ties']} / {s['loc_zero_shot_wins']} |")
    (OUT / "report.md").write_text("\n".join(md), encoding="utf-8")

    # ---- side-by-side examples: biggest wins (real), constructed wins, and risk failures
    def card(r, title):
        return "\n".join([
            f"### {title}", "",
            f"**New segment:** {r['src']}", "",
            f"**Best fuzzy match ({r['fuzzy_best']:.0f}% → a CAT tool shows nothing):** {r['fuzzy_best_src']}", "",
            f"**Semantic match (similarity {r['sem_top'][0]['sim']:.0f}, judged reusable: {r['reuse'].get('reuse')}):**  ",
            f"EN: {r['sem_top'][0]['src']}  ", f"ES: {r['sem_top'][0]['tgt']}", "",
            f"| | translation |", "|---|---|",
            f"| zero-shot (today) | {r['zero_shot']} |", f"| **semantic RAG** | {r['rag']} |",
            *([f"| human reference | {r['ref']} |"] if r.get("ref") else []), "",
            f"Localization judge: **{r['loc_pairwise']}** better. {r['loc_reason']}  ",
            f"Generic judge: **{r['pairwise']}** better. {r['judge_reason']}", ""])

    wins = sorted([r for r in routed if r["loc_pairwise"] == "rag" and r["reuse"].get("reuse") in ("full", "partial")],
                  key=lambda r: r.get("chrf_rag", 0) - r.get("chrf_zero_shot", 0), reverse=True)
    cwins = [r for r in C if r["loc_pairwise"] == "rag"]
    risks = [r for r in K if not r["loc_rag_accurate"]]
    losses = [r for r in routed + C if r["loc_pairwise"] == "zero_shot"]
    ex = ["# Side-by-side examples", ""]
    ex += [card(r, f"Real segment win {i + 1}") for i, r in enumerate(wins[:6])]
    ex += [card(r, f"Reworded TM entry ({r['variant']}) win {i + 1}") for i, r in enumerate(cwins[:3])]
    ex += [card(r, f"Where RAG lost {i + 1}") for i, r in enumerate(losses[:3])]
    ex += [card(r, f"Risk: negated segment, RAG output inaccurate {i + 1}") for i, r in enumerate(risks[:3])]
    (OUT / "examples.md").write_text("\n".join(ex), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
