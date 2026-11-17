"""Offline tests for the LocRAG 2.0 study pipeline (no API keys, models or corpora)."""
import json
import random

import numpy as np
import pytest

from locrag.retrievers import cat_fuzzy
from locrag.study import stats as S
from locrag.study.context import validate_extraction
from locrag.study.fuzzy import ExactFuzzyIndex, pairwise_max
from locrag.study.generate import JsonlStore, clean_output, noise_subset
from locrag.study.prompts import (LANG_NAMES, raw_context_block, structured_context_block, translation_messages)
from locrag.study.qe_bridge import export_items, item_id
from locrag.study.retrieval import rrf_fuse

TM = ["Keep this medicine out of the sight and reach of children.", "Do not store above 25 °C.",
      "Swallow the tablets whole with a glass of water.", "Patients experiencing persistent dizziness should stop taking the medication."]


# ---------------------------------------------------------------- fuzzy
def test_exact_index_matches_cat_fuzzy_everywhere():
    idx = ExactFuzzyIndex(TM)
    rng = random.Random(0)
    queries = ["Do not store above 30 °C.", "Swallow the tablet whole with water.", "Unseen words entirely here.",
               "Patients should discontinue treatment if severe dizziness occurs."]
    for q in queries:
        hits = idx.search(q, k=len(TM))
        for i, s in hits:
            assert s == pytest.approx(cat_fuzzy(q, TM[i]), abs=1e-6)
        assert idx.best_scores([q])[0] == pytest.approx(max(cat_fuzzy(q, t) for t in TM), abs=1e-4)
    rng.shuffle(queries)


def test_unseen_query_tokens_never_match_tm_tokens():
    idx = ExactFuzzyIndex(["alpha beta"])
    # two unseen tokens must not collide with each other or the TM vocabulary
    assert idx.search("gamma delta", 1)[0][1] == 0.0
    assert idx.search("alpha gamma", 1)[0][1] == pytest.approx(50.0)


def test_pairwise_max_is_symmetric_with_zero_diagonal():
    m = pairwise_max(TM[:3])
    assert np.allclose(m, m.T) and np.all(np.diag(m) == 0)


# ---------------------------------------------------------------- retrieval fusion
def test_rrf_near_exact_fuzzy_always_first():
    fuzzy = [(7, 97.0), (3, 60.0)]
    semantic = [(3, 0.9), (5, 0.8), (7, 0.1)]
    assert rrf_fuse(fuzzy, semantic, k=2)[0] == 7


def test_rrf_rewards_agreement():
    assert rrf_fuse([(1, 70.0), (2, 60.0)], [(2, 0.9), (3, 0.8)], k=1) == [2]


# ---------------------------------------------------------------- prompts: blinding and equivalence
def test_reference_never_enters_translation_prompts():
    ref = "Los pacientes deben interrumpir el tratamiento si aparecen mareos intensos."
    src = "Patients should discontinue treatment if severe dizziness occurs."
    pairs = [(TM[3], "Los pacientes que experimenten mareos persistentes deben dejar de tomar el medicamento.")]
    for block in ("", raw_context_block(pairs, "es"),
                  structured_context_block({"terms": [("dizziness", "mareos")], "differences": ["persistent vs severe"]}, "es")):
        text = json.dumps(translation_messages(src, "es", "medicine", block), ensure_ascii=False)
        assert ref not in text and src in text


def test_all_conditions_share_system_prompt_and_task():
    src = "Open the file."
    base = translation_messages(src, "de", "software")
    ctx = translation_messages(src, "de", "software", raw_context_block([("Open the folder.", "Ordner öffnen.")], "de"))
    assert base[0] == ctx[0]
    assert ctx[1]["content"].endswith(base[1]["content"])


def test_empty_structured_context_renders_exact_zero_shot_prompt():
    assert structured_context_block({"terms": [], "phrases": [], "conventions": [], "differences": []}, "es") == ""
    assert translation_messages("x y z", "es", "d", "") == translation_messages("x y z", "es", "d")


def test_raw_context_never_claims_equivalence():
    block = raw_context_block([("a", "b")], "zh_CN")
    assert "NOT translations of the source segment" in block and LANG_NAMES["zh_CN"] in block


# ---------------------------------------------------------------- extractor validation
def test_extractor_drops_non_verbatim_spans():
    src = "Patients should discontinue treatment if severe dizziness occurs."
    pairs = [(TM[3], "Los pacientes que experimenten mareos persistentes deben dejar de tomar el medicamento.")]
    raw = {"terms": [{"pair": 1, "source": "dizziness", "target": "mareos", "new_source_span": "dizziness"},
                     {"pair": 1, "source": "dizziness", "target": "vértigo", "new_source_span": "dizziness"},
                     {"pair": 2, "source": "x", "target": "y", "new_source_span": "z"}],
           "phrases": [{"pair": 1, "source": "stop taking the medication", "target": "dejar de tomar el medicamento",
                        "new_source_span": "stop taking the medication"}],
           "differences": [{"pair": 1, "note": "persistent vs severe"}], "conventions": []}
    v = validate_extraction(raw, src, pairs)
    assert v["kept"]["terms"] == [("dizziness", "mareos")]
    assert v["kept"]["phrases"] == []          # new_source_span not verbatim in the new source
    assert v["kept"]["differences"] == ["persistent vs severe"]
    assert v["stats"]["n_span_items"] == 4 and v["stats"]["n_span_ok"] == 1
    reasons = [i["reason"] for i in v["items"] if not i["ok"]]
    assert "target_in_historical" in reasons[0] and reasons[1] == "invalid pair index"


# ---------------------------------------------------------------- generation helpers
def test_clean_output_strips_labels_and_wrapping_quotes():
    assert clean_output('Spanish: "Abra el archivo."', "Open the file.") == "Abra el archivo."
    assert clean_output('"Quoted"', '"Quoted"') == '"Quoted"'


def test_jsonl_store_resumes(tmp_path):
    s = JsonlStore(tmp_path / "x.jsonl")
    s.add({"row_id": "a", "condition": "zero_shot", "v": 1})
    s2 = JsonlStore(tmp_path / "x.jsonl")
    assert s2.has("a", "zero_shot") and not s2.has("a", "fuzzy_ctx")


def test_noise_subset_is_deterministic_and_stratified():
    rows = [{"row_id": f"r{i}", "corpus": "E" if i % 2 else "K", "band": ["<50", "100"][i % 3 == 0]} for i in range(60)]
    a, b = noise_subset(rows, 12, 1), noise_subset(rows, 12, 1)
    assert a == b and len(a) == 12
    assert {r["corpus"] for r in rows if r["row_id"] in a} == {"E", "K"}


# ---------------------------------------------------------------- QE blinding
def test_qe_export_contains_only_opaque_id_source_and_hypothesis(tmp_path):
    outs = [{"row_id": "r1", "condition": "hybrid_ctx", "translation": "Hola", "context_block": "TM: secret"},
            {"row_id": "r1", "condition": "zero_shot", "translation": "Hola"},
            {"row_id": "r2", "condition": "zero_shot", "translation": "Adiós"}]
    p = tmp_path / "in.jsonl"
    n = export_items(outs, {"r1": "Hello", "r2": "Bye"}, None, p, seed=1)
    rows = [json.loads(l) for l in p.read_text().splitlines()]
    assert n == 2  # identical outputs from two conditions become one item
    assert all(set(r) == {"id", "src", "mt"} for r in rows)
    assert "hybrid_ctx" not in p.read_text() and "secret" not in p.read_text() and "r1" not in p.read_text()
    assert {r["id"] for r in rows} == {item_id("Hello", "Hola"), item_id("Bye", "Adiós")}


# ---------------------------------------------------------------- stats
def test_bootstrap_ci_contains_mean_and_is_deterministic():
    v = np.random.default_rng(0).normal(0.1, 1, 300)
    a, b = S.bootstrap_mean_ci(v, B=2000, seed=3), S.bootstrap_mean_ci(v, B=2000, seed=3)
    assert a == b and a["ci"][0] < a["mean"] < a["ci"][1]


def test_cluster_bootstrap_is_wider_for_duplicated_rows():
    v = np.random.default_rng(1).normal(0, 1, 100)
    rep = np.repeat(v, 3)
    clusters = np.repeat(np.arange(100), 3)
    naive = S.bootstrap_mean_ci(rep, B=3000)
    clustered = S.bootstrap_mean_ci(rep, clusters, B=3000)
    assert (clustered["ci"][1] - clustered["ci"][0]) > 1.4 * (naive["ci"][1] - naive["ci"][0])


def test_holm_monotone_and_capped():
    adj = S.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": None})
    assert adj["a"] == pytest.approx(0.03) and adj["c"] == pytest.approx(0.06) and adj["b"] == pytest.approx(0.06)
    assert adj["d"] is None


def test_crossover_finds_sign_change():
    x = np.linspace(40, 100, 200)
    d = (x - 80) / 20 + np.random.default_rng(0).normal(0, 0.05, 200)
    assert 75 <= S.crossover(x, d) <= 85
    assert S.crossover(x, -np.ones_like(x)) is None


def test_threshold_sweep_picks_tm_only_where_it_wins():
    f = np.array([100, 98, 90, 60, 40])
    tm = np.array([1.0, 0.9, 0.5, 0.1, 0.0])
    alt = np.full(5, 0.6)
    best = max(S.threshold_sweep(f, tm, alt, taus=range(50, 101), B=50), key=lambda s: s["mean"])
    assert 91 <= best["tau"] <= 98


def test_meaningful_requires_robustness_agreement():
    r = S.paired_summary([0.1, 0.1, -0.1, 0.0], eps=0.05, agree=[1.0, -1.0, -1.0, 0.0], B=200)
    assert r["improved"] == 1 and r["degraded"] == 1


def test_auc_perfect_and_null():
    assert S.auc([1, 2, 3, 4], [0, 0, 1, 1]) == 1.0
    assert S.auc([1, 1, 1, 1], [0, 1, 0, 1]) == 0.5


def test_rendered_notes_drop_pair_back_references():
    from locrag.study.context import strip_pair_refs
    assert strip_pair_refs("Formal address (usted) as seen in pair [2]") == "Formal address (usted)"
    assert strip_pair_refs("Units use a space before °C") == "Units use a space before °C"


def test_draft_block_frames_top_pair_as_adaptable_draft():
    from locrag.study.prompts import draft_context_block
    b = draft_context_block([("Stop the medicine.", "Deje el medicamento."), ("Other.", "Otro.")], "es")
    assert "DIFFERENT sentence" in b and "draft): Deje el medicamento." in b and "[2] English: Other." in b
    assert draft_context_block([], "es") == ""


def test_paired_summary_degraded_without_agree():
    from locrag.study.stats import paired_summary
    r = paired_summary([0.05, -0.05, 0.0, -0.01], B=200, eps=0.02)
    assert (r["improved"], r["degraded"]) == (1, 1)
    r = paired_summary([0.05, -0.05], B=200, eps=0.02, agree=[1.0, 1.0])
    assert (r["improved"], r["degraded"]) == (1, 0)
