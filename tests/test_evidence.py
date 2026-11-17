from locrag.evidence import build_evidence, sign_test, paired_mean_ci
from locrag.multilingual import split_keys, group_key
from locrag.multilingual import load_parallel
import zipfile
import json
import numpy as np
from locrag.multilingual import run, digest, write_json


def test_committed_evidence_denominators_and_provenance():
    evidence = build_evidence()
    c = evidence["coverage"]
    assert (c["real_n"], c["passing_n"], c["reusable_passing_n"]) == (300, 85, 65)
    assert evidence["no_route_changed_outputs"] == 168
    assert evidence["routed_subset"]["localization"] == {"rag": 50, "tie": 22, "zero_shot": 13}
    assert all(len(h) == 64 for h in evidence["provenance"].values())
    assert evidence["mt_by_band"]["ALL"]["n"] == 200


def test_statistics_handle_ties_and_identical_outputs():
    assert sign_test(0, 0) == 1
    assert sign_test(10, 0) == 2 / 2**10
    assert paired_mean_ci([0, 0, 0])["ci95"] == [0, 0]


def test_recorded_replay_keeps_originals_and_declines_context():
    from locrag.replay import replay
    row = {"route": "none", "zero_shot": "baseline", "rag": "original treatment", "loc_pairwise": "rag",
           "pairwise": "rag", "loc_zs_accurate": True, "zs_accurate": True, "loc_rag_accurate": False,
           "rag_accurate": False, "zs_consistent": False, "rag_consistent": True,
           "chrf_zero_shot": 50, "chrf_rag": 30}
    result = replay([row])[0]
    assert row["rag"] == "original treatment"
    assert result["rag"] == "baseline" and result["loc_pairwise"] == "tie"
    assert result["loc_rag_accurate"] is True and result["rag_consistent"] is False


def test_multilingual_splits_are_reproducible_and_group_disjoint():
    config = {"seed": 7, "tm_size": 2, "development_size": 2, "test_size": 2}
    keys = ["Use 10 units", "Use 20 units", "Open settings", "Close settings", "Load file", "Save file", "Quit app", "Help menu"]
    split = split_keys(keys, config)
    assert split == split_keys(list(reversed(keys)), config)
    groups = {name: {group_key(k) for k in rows} for name, rows in split.items()}
    assert not groups["tm"] & groups["test"]
    assert not groups["tm"] & groups["development"]
    assert not groups["test"] & groups["development"]


def test_chinese_embedded_unicode_separator_does_not_break_alignment(tmp_path):
    archive = tmp_path / "pair.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("KDE4.en-zh_CN.en", "Open the settings window.\nClose the settings window.\n")
        z.writestr("KDE4.en-zh_CN.zh_CN", "打开\u2028设置窗口。\n关闭设置窗口。\n")
    mapping = load_parallel(archive, "zh_CN", {"min_source_words": 4, "max_source_words": 60})
    assert len(mapping) == 2
    assert mapping["open the settings window."][1] == "打开\u2028设置窗口。"


def test_multilingual_run_records_each_language_and_policy_without_network(tmp_path, monkeypatch):
    from locrag import pipeline
    from common import llm
    from locrag.retrievers import Hit
    config = {"languages": ["es", "de", "zh_CN"], "domain": "software localization",
              "fuzzy_threshold": 75, "semantic_min_sim": 80, "k": 3,
              "policies": ["zero-shot", "fuzzy-only", "always-semantic", "router"]}
    data, output = tmp_path / "data", tmp_path / "run"
    hashes = {}
    for lang in config["languages"]:
        for split in ("tm", "test"):
            path = data / lang / f"{split}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"id": "sample", "src": "Open the settings window.",
                                        "tgt": "Reference", "target": lang})+"\n")
            hashes[str(path.relative_to(data))] = digest(path)
    write_json(data / "manifest.json", {"config": config, "file_sha256": hashes})
    class FakeRetriever:
        def encode_queries(self, queries):
            return np.ones((len(queries), 2))
        def search(self, query, k):
            return [Hit(0, 30, "Settings", "Reference")]
    class FakeRouter:
        semantic = FakeRetriever()
        fuzzy = FakeRetriever()
        def __init__(self, *args):
            pass
        def route(self, src, qvec, *, policy):
            examples = [{"src": "Settings", "tgt": "Reference"}] if policy == "always-semantic" else []
            return pipeline.Routed(src, "semantic" if examples else "none", 30, "Settings", examples)
    monkeypatch.setattr(pipeline, "TMRouter", FakeRouter)
    monkeypatch.setattr(pipeline, "translate", lambda src, examples, task: f"{task.target} " + ("Reference" if examples else "Baseline"))
    monkeypatch.setattr(llm, "chat_json", lambda *a, **kw: {
        "winner": "tie", "a_accurate": True, "b_accurate": True,
        "a_consistent": True, "b_consistent": True, "error_categories": []})
    run(config, data, output, None, "test")
    manifest = json.loads((output / "manifest.json").read_text())
    summary = json.loads((output / "summary.json").read_text())
    assert manifest["status"] == "complete"
    assert set(summary) == set(config["languages"])
    for lang in config["languages"]:
        assert summary[lang]["router"]["paired_sentence_chrf_delta"]["mean"] == 0
        assert summary[lang]["router"]["accuracy_on_distinct_outputs"] == {}
        assert summary[lang]["always-semantic"]["terminology_consistency_on_distinct_outputs"]["assessed_n"] == 1
