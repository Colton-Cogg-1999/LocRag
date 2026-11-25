"""Freeze the source panel, independent TM concordances and pre-existing translations."""
import json
import math
import random
import re
from collections import Counter, defaultdict

import numpy as np

from locrag.study.config import DATA_DIR, ROOT, RESULTS_DIR
from locrag.study.data import read_jsonl
from locrag.study.frontier_panel import PANEL as FRONTIER_PANEL

SEED = 20261125
DIR = ROOT / "experiments" / "consistency"
OUT = ROOT / "results" / "consistency"
ARMS = ("zero_shot", "fuzzy_ctx", "semantic_ctx")
BANDS = ("<50", "50-74", "75-84", "85-94", "95-99", "100")


def dump_lines(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def words(text):
    return re.findall(r"\w+", text.casefold())


def concordances(corpus, rows):
    tm = read_jsonl(DATA_DIR / corpus / "tm_es.jsonl")
    terms = {w for row in rows for w in words(row["src"])}
    postings = defaultdict(list)
    lengths = []
    for i, entry in enumerate(tm):
        tokens = words(entry["src"])
        lengths.append(len(tokens))
        for w, count in Counter(tokens).items():
            if w in terms:
                postings[w].append((i, count))
    norm = 1.2 * (.25 + .75 * np.array(lengths) / np.mean(lengths))
    index = {}
    for w, hits in postings.items():
        ids, counts = np.asarray(hits).T
        idf = math.log1p((len(tm) - len(ids) + .5) / (len(ids) + .5))
        index[w] = ids, idf * counts * 2.2 / (counts + norm[ids])
    for r in rows:
        score = np.zeros(len(tm))
        for w in sorted(set(words(r["src"])) & index.keys()):
            ids, weight = index[w]
            score[ids] += weight
        seen = {tuple(words(r["src"]))}
        evidence = []
        for i in np.argsort(-score, kind="stable"):
            if score[i] <= 0 or len(evidence) == 12:
                break
            entry = tm[i]
            key = tuple(words(entry["src"]))
            if key not in seen and entry["tm_id"] not in r["excluded"]:
                evidence.append(entry)
                seen.add(key)
        r["evidence"] = evidence


def main():
    pool = defaultdict(dict)
    for r in read_jsonl(RESULTS_DIR / "test-v1" / "rows_analysis.jsonl"):
        if r["lang"] == "es" and r["condition"] in ARMS:
            assert not r["error"] and r["condition"] not in pool[r["row_id"]]
            pool[r["row_id"]][r["condition"]] = r
    strata = defaultdict(list)
    for i, arms in pool.items():
        r = arms["zero_shot"]
        strata[r["corpus"], r["band"]].append(i)
    gemma = set()
    for group, ids in sorted(strata.items()):
        gemma.update(random.Random(f"{SEED}/{group}").sample(sorted(ids), 40))
    astra = {r["row_id"] for r in read_jsonl(FRONTIER_PANEL / "panel.jsonl")}
    rows, outputs = [], []
    for i in sorted(gemma | astra):
        arms = pool[i]
        r = arms["zero_shot"]
        excluded = sorted({e["tm_id"] for a in ARMS for e in arms[a]["retrieved"]})
        rows.append({k: r[k] for k in ("row_id", "src", "corpus", "band", "fuzzy_best")} | {"excluded": excluded})
        if i in gemma:
            outputs.append({"row_id": i, "model": "Gemma", "outputs": {a: arms[a]["translation"] for a in ARMS}})
        if i in astra:
            file = ROOT / "results/frontier/rows" / (i.replace(":", "-") + ".json")
            saved = json.loads(file.read_text())["translations"]
            outputs.append({"row_id": i, "model": "Astra", "outputs": {a: saved[a]["text"] for a in ARMS}})
    for corpus in ("EMEA", "KDE4"):
        concordances(corpus, [r for r in rows if r["corpus"] == corpus])
    dump_lines(DIR / "sources.jsonl", rows)
    dump_lines(DIR / "translations.jsonl", outputs)
    print(len(rows), "sources;", len(outputs), "source/model pairs")


if __name__ == "__main__":
    main()
