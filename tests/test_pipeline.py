import numpy as np
import pytest

from locrag.pipeline import TMRouter, TranslationTask, build_prompt
from locrag.retrievers import Hit, SemanticRetriever, FuzzyRetriever
from common.llm import validate_judgment

TM = [{"src": "Keep the original text.", "tgt": "Conserve el texto original."},
      {"src": "Open the settings window.", "tgt": "Abra la ventana de configuración."}]


class FixedRetriever:
    def __init__(self, scores):
        self.scores = scores
        self.calls = 0

    def search(self, query, k=3):
        self.calls += 1
        return [Hit(i, score, TM[i]["src"], TM[i]["tgt"]) for i, score in enumerate(self.scores)][:k]

    def search_vec(self, query, k=3):
        return self.search(query, k)


@pytest.mark.parametrize("fuzzy,semantic,route,n", [
    ([75, 74], [99, 98], "fuzzy", 1),
    ([74, 70], [80, 79.99], "semantic", 1),
    ([74, 70], [79.99, 50], "none", 0),
])
def test_routes_match_threshold_boundaries(fuzzy, semantic, route, n):
    f, s = FixedRetriever(fuzzy), FixedRetriever(semantic)
    router = TMRouter(TM, fuzzy=f, semantic=s)
    result = router.route("New source")
    assert result.route == route and len(result.examples) == n
    assert result.reason and result.retrieval_ms >= 0
    if route == "fuzzy":
        assert s.calls == 0


def test_fuzzy_and_empty_memory_need_no_semantic_provider():
    router = TMRouter(TM)
    assert router.route(TM[0]["src"]).route == "fuzzy"
    assert router._semantic is None
    empty = TMRouter([])
    assert empty.route("Source").examples == []
    assert empty._semantic is None


def test_baseline_policies_do_not_apply_selective_floor():
    router = TMRouter(TM, fuzzy=FixedRetriever([20, 10]), semantic=FixedRetriever([40, 30]))
    assert router.route("Source", policy="router").route == "none"
    assert router.route("Source", policy="fuzzy-only").examples == []
    assert len(router.route("Source", policy="always-semantic").examples) == 2


@pytest.mark.parametrize("kwargs", [{"k": 0}, {"k": 1.5}, {"fuzzy_threshold": -1},
                                   {"semantic_min_sim": 101}, {"semantic_min_sim": float("nan")}])
def test_invalid_router_config(kwargs):
    with pytest.raises(ValueError):
        TMRouter(TM, **kwargs)


def test_invalid_input():
    with pytest.raises(ValueError):
        TMRouter([{"src": "", "tgt": "x"}])
    with pytest.raises(ValueError):
        TMRouter(TM).route(" ")


@pytest.mark.parametrize("size,k", [(0, 3), (1, 3), (2, 2), (2, 0)])
def test_semantic_small_memories(size, k):
    retriever = SemanticRetriever.__new__(SemanticRetriever)
    retriever.tm = TM[:size]
    retriever.mat = np.eye(2, dtype=np.float32)[:size]
    hits = retriever.search_vec(np.array([1., 0.]), k=k)
    assert len(hits) == min(size, k)
    if hits:
        assert hits[0].src == TM[0]["src"]


def test_invalid_vectors():
    retriever = SemanticRetriever.__new__(SemanticRetriever)
    retriever.tm, retriever.mat = TM, np.eye(2)
    for vector in (np.array([1.]), np.array([np.nan, 0.])):
        with pytest.raises(ValueError):
            retriever.search_vec(vector)
    with pytest.raises(ValueError):
        FuzzyRetriever(TM).search("x", -1)


@pytest.mark.parametrize("lang,label", [("de", "German"), ("zh_CN", "Simplified Chinese"), ("es", "Spanish")])
def test_translation_language_is_explicit(lang, label):
    task = TranslationTask(lang, "software localization")
    assert label in task.system
    assert f"{lang.upper()}:" in build_prompt("Open", [], task)
    if lang != "es":
        assert "Spanish" not in task.system and "ES:" not in build_prompt("Open", TM, task)


def test_judge_rejects_strings_and_missing_fields():
    with pytest.raises(ValueError):
        validate_judgment({"winner": "A", "a_accurate": "false", "b_accurate": True})
    with pytest.raises(ValueError):
        validate_judgment({"winner": "unexpected"})
    assert validate_judgment({"winner": "tie", "a_accurate": False, "b_accurate": False})


def test_empty_translation_fails_clearly(monkeypatch):
    import locrag.pipeline as pipeline
    monkeypatch.setattr(pipeline, "chat", lambda *args, **kwargs: "ES: ")
    with pytest.raises(RuntimeError, match="no usable translation"):
        pipeline.translate("Source", [])


def test_evaluation_uses_router_and_reuses_baseline_on_none(monkeypatch):
    from locrag import exp_router
    semantic = FixedRetriever([79, 60])
    semantic.encode_queries = lambda queries: np.zeros((len(queries), 2))
    router = TMRouter(TM, fuzzy=FixedRetriever([20, 10]), semantic=semantic)
    calls = []
    def translation(src, examples):
        calls.append(examples)
        return "Una traducción."
    monkeypatch.setattr(exp_router, "translate", translation)
    def judge(prompt, **kwargs):
        if '"reuse"' in prompt:
            return {"reuse": "none"}
        return {"winner": "tie", "a_accurate": True, "b_accurate": True,
                "a_consistent": False, "b_consistent": False}
    monkeypatch.setattr(exp_router, "chat_json", judge)
    row = exp_router.evaluate(router, [{"src": "A source sentence", "ref": "Una traducción."}], workers=1)[0]
    assert row["route"] == "none" and row["examples_used"] == []
    assert row["rag"] == row["zero_shot"] and calls == [[]]
