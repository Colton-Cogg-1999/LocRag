import json
import sqlite3
from types import SimpleNamespace

import pytest

from locrag.study import frontier
from locrag.study.data import read_jsonl
from locrag.study.frontier_panel import ARMS, PANEL


def test_panel_is_paired_and_random_control_matches_length():
    rows = read_jsonl(PANEL / "panel.jsonl")
    refs = json.loads((PANEL / "references.json").read_text())
    assert len(rows) == len(refs) == 100
    assert {r["row_id"] for r in rows} == set(refs)
    for r in rows:
        arms = r["examples"]
        assert set(arms) == set(ARMS)
        assert arms["zero_shot"] == []
        controls = {e["tm_id"] for e in arms["random_ctx"]}
        assert len(controls) == 3
        for arm in ("semantic_ctx", "fuzzy_ctx", "hybrid_ctx"):
            assert len(arms[arm]) == 3
            assert controls.isdisjoint(e["tm_id"] for e in arms[arm])
        assert [len(e["src"].split()) for e in arms["fuzzy_ctx"]] == [len(e["src"].split()) for e in arms["random_ctx"]]


def test_paid_request_resumes_and_preserves_failed_reservation(monkeypatch):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE calls(id INTEGER PRIMARY KEY, hash TEXT, cost REAL, result TEXT)")
    usage = SimpleNamespace(input_tokens=10, output_tokens=20, model_dump=lambda: {})
    reply = SimpleNamespace(status="completed", output_text="traducción", model="snapshot", id="one", usage=usage)
    responses = SimpleNamespace(create=lambda **kw: reply)
    args = db, SimpleNamespace(responses=responses), frontier.TRANSLATOR
    rec = frontier.request(*args, [{"role": "user", "content": "first"}])

    def fail(**kw):
        raise TimeoutError

    responses.create = fail
    assert frontier.request(*args, [{"role": "user", "content": "first"}]) == rec
    with pytest.raises(TimeoutError):
        frontier.request(*args, [{"role": "user", "content": "second"}])
    assert db.execute("SELECT count(*) FROM calls WHERE result IS NULL AND cost>0").fetchone()[0] == 1
    monkeypatch.setattr(frontier, "CAP", .001)
    with pytest.raises(SystemExit, match="cap"):
        frontier.request(*args, [{"role": "user", "content": "third"}])


@pytest.mark.parametrize(
    "same,picks,expected",
    [
        (True, [], "tie"),
        (False, ["hybrid_ctx", "hybrid_ctx"], "hybrid_ctx"),
        (False, ["hybrid_ctx", "tie"], "order_disagreement"),
    ],
)
def test_judgments_are_decoded_in_both_orders(tmp_path, monkeypatch, same, picks, expected):
    row = read_jsonl(PANEL / "panel.jsonl")[0]
    orders = []
    monkeypatch.setattr(frontier, "OUT", tmp_path)
    monkeypatch.setattr(frontier, "messages", lambda row, arm: arm)

    def respond(db, client, model, prompt, judge=False):
        if not judge:
            return {"text": "same" if same else prompt}
        candidates = json.loads(prompt[1]["content"])
        orders.append(candidates["A"])
        pick = picks[len(orders) - 1]
        label = "tie"
        if pick != "tie":
            label = "A" if candidates["A"] == pick else "B"
        return {"text": json.dumps({"winner": label, "evidence": "fixture"})}

    monkeypatch.setattr(frontier, "request", respond)
    frontier.translate_and_judge(None, None, row)
    saved = json.loads(next((tmp_path / "rows").glob("*.json")).read_text())
    assert saved["winner"] == expected
    assert [j["pick"] for j in saved["judgments"]] == picks
    assert sorted(orders) == ([] if same else ["fuzzy_ctx", "hybrid_ctx"])
