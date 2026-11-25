from locrag.study.consistency_analysis import estimate
from locrag.study.consistency_panel import ARMS, DIR, words
from locrag.study.data import read_jsonl


def test_denominators_and_paired_changes():
    def outcomes(a, b, c):
        return dict(zip(ARMS, (a, b, c)))
    rows = [
        dict(corpus="EMEA", band="<50", eligible=True, accuracy=outcomes(True, True, True),
             consistency=outcomes(False, False, True)),
        dict(corpus="EMEA", band="<50", eligible=False, accuracy=outcomes(True, True, False)),
        dict(corpus="KDE4", band="50-74", eligible=True, accuracy=outcomes(False, False, True),
             consistency=outcomes(True, True, False)),
    ]
    out, _ = estimate(rows)
    assert out["n"] == 3 and out["eligible"] == 2
    paired = out["paired"]["semantic_ctx_minus_fuzzy_ctx"]
    assert paired["consistency_pp"] == paired["accuracy_pp"] == 0
    assert paired["con_fixes_both_accurate"] == 1 and paired["con_losses_both_accurate"] == 0
    assert paired["meaning_errors_introduced"] == paired["meaning_errors_fixed"] == 1


def test_concordances_are_separate_from_candidate_evidence():
    for r in read_jsonl(DIR / "sources.jsonl"):
        entries = r["evidence"]
        assert {e["tm_id"] for e in entries}.isdisjoint(r["excluded"])
        normalized = {tuple(words(e["src"])) for e in entries}
        assert len(normalized) == len(entries) <= 12
        assert tuple(words(r["src"])) not in normalized
