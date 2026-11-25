from locrag.study.data import read_jsonl
from locrag.study.selective_router import PANEL


def test_frozen_router_canaries():
    rows = {r["row_id"]: r for r in read_jsonl(PANEL)}
    # Starter-pack entry cleared the semantic floor; two unrelated neighbors did not.
    starter = rows["E454684e46b6e:es"]
    assert starter["route"] == "semantic"
    assert len(starter["examples"]["router"]) == 1
    assert "envase de iniciación" in starter["examples"]["router"][0]["tgt"].lower()
    low = [r for r in rows.values() if r["fuzzy_best"] < 75]
    assert len(low) == 160
    assert sum(r["route"] == "none" for r in low) == 78
    for r in rows.values():
        assert len(r["examples"]["fuzzy_ctx"]) == 3
        assert not r["examples"]["zero_shot"]
        if r["route"] == "none":
            assert not r["examples"]["router"]
            assert r["messages"]["router"] == r["messages"]["zero_shot"]
