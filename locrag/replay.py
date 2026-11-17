"""Recalculate the recorded Spanish study with saved no-route decisions honored.

This is a historical replay, not new inference or a validation of current embeddings.
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

from locrag.evidence import ROOT, read_rows, summarize
from locrag.multilingual import digest, write_json


def replay(rows: list[dict]) -> list[dict]:
    result = copy.deepcopy(rows)
    for row in result:
        if row["route"] == "none":
            row.update(rag=row["zero_shot"], loc_pairwise="tie", pairwise="tie",
                       loc_rag_accurate=row["loc_zs_accurate"], rag_accurate=row["zs_accurate"],
                       rag_consistent=row["zs_consistent"], chrf_rag=row["chrf_zero_shot"])
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    source = ROOT / "results/router/rows.jsonl"
    original = [r for r in read_rows(source) if r["set"] == "real"]
    replayed = replay(original)
    result = {"status": "replay of original recorded route labels; no new translation or judging calls",
              "source_sha256": digest(source), "original": summarize(original),
              "selective_replay": summarize(replayed),
              "introduced_accuracy_errors": sum(r["loc_zs_accurate"] and not r["loc_rag_accurate"] for r in replayed),
              "fixed_accuracy_errors": sum(r["loc_rag_accurate"] and not r["loc_zs_accurate"] for r in replayed)}
    write_json(args.output, result)
    print(f"Saved historical replay to {args.output}; no model calls made.")


if __name__ == "__main__":
    main()
