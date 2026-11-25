"""Prepare, execute and reproduce the selective-router experiment."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import os
import sqlite3

from openai import OpenAI

from locrag.pipeline import TMRouter, TranslationTask, build_prompt
from locrag.retrievers import Hit
from locrag.study.config import ROOT, DATA_DIR, write_json
from locrag.study.consistency import grade
from locrag.study.consistency_analysis import decoded, estimate, GROUPS
from locrag.study.consistency_panel import BANDS, DIR, OUT, dump_lines
from locrag.study.data import read_jsonl
from locrag.study.frontier import TRANSLATOR, encoded_request, request, request_args

PANEL = ROOT / "experiments/selective-router/panel.jsonl"
RESULT = ROOT / "results/selective-router"
ARMS = ("zero_shot", "fuzzy_ctx", "router")
DOMAINS = {"EMEA": "EU medicinal product information", "KDE4": "software interface localization"}


def render(src, entries, task):
    return [{"role": "system", "content": task.system},
            {"role": "user", "content": build_prompt(src, entries, task)}]


class ArchivedSemanticSearch:
    """Serve the original nearest neighbors. TMRouter applies its own thresholds."""
    def __init__(self, tm, ranks):
        self.tm = tm
        self.ranks = ranks

    def search(self, query, k):
        r = self.ranks[query]
        hits = []
        for idx in r["semantic"][:k]:
            entry = self.tm[idx]
            m = r["candidates"][str(idx)]
            if m["tm_id"] != entry["tm_id"] or m["cos"] == .8:
                raise ValueError("Misaligned TM or ambiguous rounded cutoff")
            hits.append(Hit(idx, 100 * m["cos"], entry["src"], entry["tgt"]))
        return hits


def prepare():
    ids = {r["row_id"] for r in read_jsonl(DIR / "translations.jsonl") if r["model"] == "Gemma"}
    sources = [r for r in read_jsonl(DIR / "sources.jsonl") if r["row_id"] in ids]
    candidates = {r["src_id"]: r for r in read_jsonl(DATA_DIR / "candidates.jsonl")}
    frozen = {r["row_id"]: r for r in read_jsonl(OUT / "conventions.jsonl")}
    panel = []
    for corpus, domain in DOMAINS.items():
        task = TranslationTask(target="es", domain=domain)
        tm = read_jsonl(DATA_DIR / corpus / "tm_es.jsonl")
        subset = [r for r in sources if r["corpus"] == corpus]
        ranks = {r["src"]: candidates[r["row_id"].split(":")[0]] for r in subset}
        router = TMRouter(tm, fuzzy_threshold=75, semantic_min_sim=80, k=3,
                          semantic=ArchivedSemanticSearch(tm, ranks))
        for r in subset:
            src = r["src"]
            decision = router.route(src)
            c = ranks[src]
            examples = {"zero_shot": [], "fuzzy_ctx": [], "router": []}
            for idx in c["fuzzy"][:3]:
                m = c["candidates"][str(idx)]
                assert m["tm_id"] == tm[idx]["tm_id"]
                examples["fuzzy_ctx"].append(dict(tm[idx], score=m["fuzzy"]))
            for e in decision.examples:
                entry = tm[e["tm_index"]]
                assert (entry["src"], entry["tgt"]) == (e["src"], e["tgt"])
                examples["router"].append(dict(entry, score=e["score"]))
            messages = {a: render(src, entries, task) for a, entries in examples.items()}
            cites = {x["tm_id"] for x in frozen[r["row_id"]]["decision"]["citations"]}
            panel.append({k: r[k] for k in ("row_id", "src", "corpus", "band", "fuzzy_best")} |
                         {"router_fuzzy_best": decision.fuzzy_best, "route": decision.route, "reason": decision.reason,
                          "examples": examples, "messages": messages,
                          "cited_entry_in_router": bool(cites & {e["tm_id"] for e in examples["router"]})})
    assert len(panel) == 480 and len(ids) == 480
    dump_lines(PANEL, sorted(panel, key=lambda r: r["row_id"]))


def run(workers):
    rows = read_jsonl(PANEL)
    assert len(rows) == 480
    frozen = {r["row_id"]: r for r in read_jsonl(OUT / "conventions.jsonl")}
    cache = ROOT / ".cache/frontier.sqlite"
    cache.parent.mkdir(exist_ok=True)
    with closing(sqlite3.connect(cache)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS calls(id INTEGER PRIMARY KEY, hash TEXT, cost REAL, result TEXT)")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://api.openai.com/v1",
                    timeout=150, max_retries=0)

    def process(r):
        with closing(sqlite3.connect(cache, timeout=60)) as db:
            translations = {}
            for arm in ARMS:
                call = request(db, client, TRANSLATOR, r["messages"][arm])
                translations[arm] = {k: v for k,v in call.items() if k != "response_id"}
            item = {"row_id": r["row_id"], "model": "Astra",
                    "outputs": {a: c["text"] for a,c in translations.items()}}
            g = grade(db, client, item, r, frozen[r["row_id"]])
            return {"row_id": r["row_id"], "translations": translations, "evaluations": g["evaluations"]}

    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for start in range(0, len(rows), workers * 2):
            results.extend(pool.map(process, rows[start:start + 2 * workers]))
            print(f"{len(results)}/{len(rows)}", flush=True)
    dump_lines(RESULT / "outputs.jsonl", results)


def summarize():
    panel = {r["row_id"]: r for r in read_jsonl(PANEL)}
    frozen = {r["row_id"]: r for r in read_jsonl(OUT / "conventions.jsonl")}
    rows, calls, seen = [], {}, set()
    repeat = Counter()
    for record in read_jsonl(RESULT / "outputs.jsonl"):
        i = record["row_id"]
        r = panel[i]
        if i in seen:
            raise ValueError(f"Duplicate output {i}")
        seen.add(i)
        row = {**r, "eligible": frozen[i]["eligible"]}
        texts = {}
        task = TranslationTask(target="es", domain=DOMAINS[r["corpus"]])
        for arm in ARMS:
            assert r["messages"][arm] == render(r["src"], r["examples"][arm], task)
            call = record["translations"][arm]
            sha = hashlib.sha256(encoded_request(request_args(TRANSLATOR, r["messages"][arm]))).hexdigest()
            if sha != call["request_hash"] or not call["text"]:
                raise ValueError(f"Translation prompt mismatch {i}/{arm}")
            calls[sha] = call
            texts[arm] = call["text"]
        if r["route"] == "none":
            assert not r["examples"]["router"] and r["messages"]["router"] == r["messages"]["zero_shot"]
            assert texts["router"] == texts["zero_shot"]
        assert ("consistency" in record["evaluations"]) == row["eligible"]
        for task, passes in record["evaluations"].items():
            first = passes[0]
            assert set(first["labels"]) == set(ARMS)
            assert len(set(texts.values())) == len(first["verdicts"])
            row[task] = decoded(first)
            for p in passes:
                call = p["call"]
                calls[call["request_hash"]] = call
            if len(passes) == 2:
                second = decoded(passes[1])
                for arm in {t: a for a,t in texts.items()}.values():
                    repeat[task + "_tested"] += 1
                    repeat[task + "_agree"] += row[task][arm] == second[arm]
        rows.append(row)
    if len(panel) != 480 or seen != panel.keys():
        raise ValueError("Incomplete panel")
    pairs = (("router", "fuzzy_ctx"), ("router", "zero_shot"), ("fuzzy_ctx", "zero_shot"))
    low = [r for r in rows if r["band"] in GROUPS["low"]]
    subsets = {"all": rows, **{k: [r for r in rows if r["band"] in bands] for k,bands in GROUPS.items()},
               **{b: [r for r in rows if r["band"] == b] for b in BANDS},
               "low_semantic_activated": [r for r in low if r["route"] == "semantic"],
               "low_abstained": [r for r in low if r["route"] == "none"]}
    results = {}
    for key, subset in subsets.items():
        stats, _ = estimate(subset, arms=ARMS, pairs=pairs)
        stats["routes"] = dict(Counter(r["route"] for r in subset))
        stats["examples_supplied_by_router"] = dict(Counter(len(r["examples"]["router"]) for r in subset))
        stats["eligible_citation_overlap"] = sum(r["eligible"] and r["cited_entry_in_router"] for r in subset)
        results[key] = stats
    independent = [r for r in rows if not r["cited_entry_in_router"]]
    results["no_cited_entry_in_router"], _ = estimate(independent, arms=ARMS, pairs=pairs)
    write_json(RESULT / "summary.json", {"groups": results, "repeat_grades": dict(repeat),
               "unique_calls": len(calls), "uncached_rate_usd": sum(c["cost_upper_usd"] for c in calls.values())})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "run", "summarize"))
    parser.add_argument("--workers", type=int, default=24)
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare()
    elif args.stage == "run":
        run(args.workers)
    else:
        summarize()
