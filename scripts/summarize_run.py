"""Rebuild the completed 2026-11-16 evaluation report without model calls."""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from locrag.evidence import read_rows, sign_test, paired_mean_ci

RUN = ROOT / "results/runs/2026-11-16"
MULTI = ROOT / "results/multilingual/validation-v1"
NAMES = {"es": "Spanish", "de": "German", "zh_CN": "Simplified Chinese"}


def outcome(j):
    if j["winner"] in ("tie", "error"):
        return j["winner"]
    return "better" if (j["winner"] == "A") == j["treatment_is_a"] else "worse"


def errors(j):
    if not j.get("accuracy_assessed"):
        return 0, 0
    treated = j["a_accurate"] if j["treatment_is_a"] else j["b_accurate"]
    baseline = j["b_accurate"] if j["treatment_is_a"] else j["a_accurate"]
    return int(baseline and not treated), int(treated and not baseline)


def main():
    manifest = json.loads((MULTI / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    rows = read_rows(MULTI / "rows.jsonl")
    assert len(rows) == 3600
    grouped = defaultdict(dict)
    for r in rows:
        assert r["translation"].strip() and r["judgment"]["winner"] != "error"
        assert r["policy"] not in grouped[r["target"], r["id"]]
        grouped[r["target"], r["id"]][r["policy"]] = r
    assert len(grouped) == 900 and all(len(g) == 4 for g in grouped.values())
    incremental = {}
    for lang in NAMES:
        counts, accuracy, routes, deltas = Counter(), Counter(), Counter(), []
        for (target, _), g in grouped.items():
            if target != lang:
                continue
            r, f = g["router"], g["fuzzy-only"]
            routes[r["route"]] += 1
            deltas.append(r["chrf"] - f["chrf"])
            if r["route"] == "none":
                assert r["translation"] == r["zero_shot"] and not r["examples"]
            if r["route"] == "fuzzy":
                assert r["translation"] == f["translation"]
            if r["translation"] == f["translation"]:
                counts["tie"] += 1
                continue
            # Below the fuzzy floor, ordinary matching is exactly the saved
            # zero-shot baseline. Else the two systems have identical outputs.
            assert f["translation"] == r["zero_shot"]
            counts[outcome(r["judgment"])] += 1
            introduced, fixed = errors(r["judgment"])
            accuracy["introduced"] += introduced
            accuracy["fixed"] += fixed
        assert sum(counts.values()) == 300
        incremental[lang] = {"n": 300, "preferences": dict(counts), "accuracy_changes": dict(accuracy),
                             "routes": dict(routes), "sign_test_p": sign_test(counts["better"], counts["worse"]),
                             "paired_sentence_chrf_delta": paired_mean_ci(deltas)}
    medical = read_rows(RUN / "emea-router/rows.jsonl")
    assert all(r["rag"].strip() and r["zero_shot"].strip() for r in medical)
    assert Counter(r["set"] for r in medical) == {"real": 300, "constructed": 80, "risk": 40}
    assert not any(r["loc_pairwise"] == "error" or r["pairwise"] == "error" or r["reuse"].get("reuse") == "error" for r in medical)
    assert all(r["rag"] == r["zero_shot"] and not r["examples_used"] for r in medical if r["route"] == "none")
    real = [r for r in medical if r["set"] == "real"]
    medical_counts = dict(Counter(r["loc_pairwise"] for r in real))
    mt = read_rows(RUN / "emea-mt-deduplicated/rag_mt_outputs.jsonl")
    assert len(mt) == 200 and all(len(r["hyp"]) == 6 for r in mt)
    assert all(text.strip() for r in mt for text in r["hyp"].values())
    assert len(json.loads((RUN / "emea-retrieval/probes_rows.json").read_text())) == 800
    assert all(r["hyp"]["zero_shot"] == r["hyp"]["fuzzy_cat75"] for r in mt if r["top_fuzzy_score"] < 75)
    source_paths = [MULTI / "rows.jsonl", MULTI / "manifest.json", RUN / "emea-router/rows.jsonl",
                    RUN / "emea-mt-deduplicated/rag_mt_outputs.jsonl", RUN / "emea-retrieval/probes_rows.json"]
    result = {"status": "completed automated evaluation", "incremental_semantic_fallback": incremental,
              "medical_real_preferences": medical_counts,
              "medical_accuracy_changes": {"introduced": sum(r["loc_zs_accurate"] and not r["loc_rag_accurate"] for r in real),
                                           "fixed": sum(r["loc_rag_accurate"] and not r["loc_zs_accurate"] for r in real)},
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
              "validation": "3600 multilingual condition rows, 200 medical comparison inputs, 420 router inputs; no grading errors; no-context invariants pass"}
    (RUN / "final_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    summary = json.loads((MULTI / "summary.json").read_text())
    lines = ["# Completed evaluation: plain-language results", "",
             "The system finds reusable-looking past translations that ordinary matching misses. Using those examples helps in some cases, especially with consistent wording, but does not reliably improve accuracy across every language.", "",
             "## New language tests", "",
             "We translated the same 300 English software-localization sentences into Spanish, German and Simplified Chinese: 900 language-specific test cases, each under four conditions. No language was skipped.", "",
             "This table isolates the added value of semantic fallback over ordinary fuzzy matching. Identical outputs count as ties; below the fuzzy threshold the ordinary system is exactly the zero-shot baseline already judged. No new or invented judgments are needed for this comparison.", "",
             "| Target language | Better | Worse | Tie | New meaning errors | Meaning errors fixed |",
             "|---|---:|---:|---:|---:|---:|"]
    for lang, x in incremental.items():
        c, a = x["preferences"], x["accuracy_changes"]
        lines.append(f"| {NAMES[lang]} | {c.get('better',0)} | {c.get('worse',0)} | {c.get('tie',0)} | {a.get('introduced',0)} | {a.get('fixed',0)} |")
    lines += ["", "The system used semantic fallback on 43/300 sources. Ordinary matching handled 22; 235 received no memory examples. Most ties therefore reflect deliberate non-use of memory, not a failed translation attempt.", "",
              "German showed the clearest added benefit in this sample. Spanish and Chinese were mixed; these results do not establish a general accuracy improvement. Judgments prioritize meaning, then reuse of appropriate terminology/phrasing.", "",
              "## Full system versus translating without any memory", "",
              "This includes benefits from ordinary fuzzy matches as well as semantic fallback. It must not be described as the isolated contribution of semantic search.", "",
              "| Target language | Better | Worse | Tie | Character-only chrF: no memory → router |",
              "|---|---:|---:|---:|---:|"]
    for lang in NAMES:
        r = summary[lang]["router"]
        c = r["judgments"]
        lines.append(f"| {NAMES[lang]} | {c.get('treatment',0)} | {c.get('baseline',0)} | {c.get('tie',0)} | {summary[lang]['zero-shot']['chrf']:.2f} → {r['chrf']:.2f} |")
    lines += ["", "Always supplying semantic examples produced more preferred outputs, but also more newly introduced meaning errors: 17 Spanish, 15 German and 29 Chinese. That more aggressive policy is not a free improvement. All four conditions are in the [full summary](../../multilingual/validation-v1/summary.json).", "",
              "## Original Spanish medical-text experiments, rerun", "",
              f"On the 300 real below-threshold cases, the corrected router received **{medical_counts['rag']} wins, {medical_counts['zero_shot']} losses and {medical_counts['tie']} ties** under the localization rubric. It introduced two accuracy errors and fixed one. The generic rubric, which does not reward memory consistency, preferred it 25 times and preferred the baseline 32 times, with 243 ties.", "",
              "On the separate 200-case comparison, reusing memory strongly improved reference similarity over no-memory translation. Semantic retrieval did not beat ordinary thresholded fuzzy matching overall. The prior post-hoc tiered policy's apparent edge was not statistically convincing in this rerun.", "",
              "The constructed rewording tests expose a real failure mode: the localization judge rated 79/80 baseline outputs accurate, versus 71/80 with retrieved examples. The 40 forced opposite-meaning stress cases had 39/40 accuracy ratings in both conditions under that rubric; this is not a dedicated human-verified polarity-safety result.", "",
              "The three embedding models again recovered the original/accepted near-duplicate first on 95–97.5% of paraphrases and 100% of restructures. Good retrieval does not guarantee a good translation.", "",
              "## What can be claimed", "",
              "LocRAG is a tested translation-memory assistant that can recover overlooked examples and improve consistency. Its benefit depends on the language and content, and it sometimes introduces meaning errors. General translation-accuracy improvement is unproven.", "",
              "## Checks and limitations", "",
              "- All planned automated runs completed. No empty translations or failed judgments were found.",
              "- The 200-case comparison deduplicates identical prompts. The first run exposed concurrent cache misses generating different outputs for equivalent no-context conditions; `emea-mt-deduplicated` is the corrected result and supersedes `emea-mt`.",
              "- The multilingual experiment and corrected router reuse their baseline output when context is absent; these invariants were checked on every result.",
              "- The judge is Claude Sonnet 5.5, not a human review panel. A/B order is randomized; judge noise, reference quality and rubric preferences remain limitations.",
              "- Software data are new held-out inputs; the medical runs reproduce previously studied inputs and do not constitute fresh independent medical validation.",
              "- English retrieval inputs are shared across target languages; this does not test German- or Chinese-source retrieval.",
              "- Exploratory sign tests and segment-bootstrap intervals are in `final_summary.json`; they are unadjusted for multiple comparisons and do not account for document dependence or judge error.",
              "- Medical scores use chrF++; the multilingual primary metric is character-only chrF. Absolute scores should not be pooled across these studies or used to rank languages.", "",
              "Rebuild this report without model calls: `uv run python scripts/summarize_run.py`. Input hashes are in `final_summary.json`. Raw [multilingual outputs](../../multilingual/validation-v1/rows.jsonl), [medical router outputs](emea-router/rows.jsonl), [medical comparison](emea-mt-deduplicated/rag_mt_summary.md), and [retrieval probes](emea-retrieval/probes_summary.md) remain available.", ""]
    (RUN / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result["incremental_semantic_fallback"], indent=2))
    print("All completion and consistency checks passed.")


if __name__ == "__main__":
    main()
