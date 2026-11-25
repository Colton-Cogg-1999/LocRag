"""Freeze a matched English→Spanish panel before frontier translation."""
import json
import random
from collections import defaultdict

from locrag.study.config import DATA_DIR, ROOT, load_config, write_json
from locrag.study.data import load_heldout, load_references, load_tm, read_jsonl
from locrag.study.prompts import raw_context_block, translation_messages

PANEL = ROOT / "experiments" / "frontier"
ARMS = ("zero_shot", "random_ctx", "fuzzy_ctx", "semantic_ctx", "hybrid_ctx")
SEED = 20261124


def messages(row, arm):
    pairs = [(e["src"], e["tgt"]) for e in row["examples"][arm]]
    return translation_messages(row["src"], "es", row["domain"], raw_context_block(pairs, "es"))


def main():
    groups = defaultdict(list)
    for row in load_heldout(DATA_DIR, "test"):
        if row["lang"] == "es" and row["band"] in ("<50", "50-74"):
            groups[row["corpus"], row["band"]].append(row)
    cfg = load_config()
    candidates = {r["src_id"]: r for r in read_jsonl(DATA_DIR / "candidates.jsonl")}
    rows = []
    for corpus in ("EMEA", "KDE4"):
        tm = load_tm(DATA_DIR, corpus, "es")
        by_length = defaultdict(list)
        for i, entry in enumerate(tm):
            by_length[len(entry["src"].split())].append(i)
        for band in ("<50", "50-74"):
            rng = random.Random(f"{SEED}/{corpus}/{band}")
            population = sorted(groups[corpus, band], key=lambda r: r["row_id"])
            for r in rng.sample(population, 25):
                ranks = candidates[r["src_id"]]
                ids = {f"{arm}_ctx": ranks[arm][:3] for arm in ("fuzzy", "semantic", "hybrid")}
                excluded = set().union(*ids.values())
                random_ids = []
                for i in ids["fuzzy_ctx"]:
                    length = len(tm[i]["src"].split())
                    options = [j for j in by_length[length] if j not in excluded]
                    j = rng.choice(options)
                    random_ids.append(j)
                    excluded.add(j)
                ids.update(random_ctx=random_ids, zero_shot=[])
                rows.append({"row_id": r["row_id"], "corpus": corpus, "band": band, "src": r["src"],
                             "domain": cfg["corpora"][corpus]["domain"],
                             "examples": {arm: [tm[j] for j in ids[arm]] for arm in ARMS}})
    PANEL.mkdir(parents=True, exist_ok=True)
    (PANEL / "panel.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    references = load_references(DATA_DIR)
    write_json(PANEL / "references.json", {r["row_id"]: references[r["row_id"]]["ref"] for r in rows})


if __name__ == "__main__":
    main()
