"""Matched English→Spanish/German/Simplified Chinese evaluation.

prepare: create shared source splits and a corpus audit (offline after download).
plan: show the run size without loading a model.
run: explicit model inference, separate immutable output directory per run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import re
import subprocess
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path

import numpy as np
from sacrebleu.metrics import CHRF

from locrag.evidence import paired_mean_ci, read_rows
from locrag.retrievers import FuzzyRetriever, band_of, cat_fuzzy

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "experiments/multilingual.json"
PAIRS = {"es": "en-es", "de": "de-en", "zh_CN": "en-zh_CN"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def group_key(text: str) -> str:
    # Keep numeric/placeholder variants together. Not a full semantic deduplication.
    return re.sub(r"%\d+|\d+(?:[.,]\d+)*", "#", normalized(text))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_parallel(archive: Path, target: str, config: dict) -> dict:
    pair = PAIRS[target]
    mapping = {}
    with zipfile.ZipFile(archive) as z:
        # Unicode splitlines() also splits embedded U+2028 etc. Alignment uses LF only.
        sources = z.read(f"KDE4.{pair}.en").decode("utf-8").rstrip("\n").split("\n")
        targets = z.read(f"KDE4.{pair}.{target}").decode("utf-8").rstrip("\n").split("\n")
    if len(sources) != len(targets):
        raise ValueError(f"Alignment length mismatch in {archive}")
    for src, tgt in zip(sources, targets):
        src, tgt = src.strip(), tgt.strip()
        if not config["min_source_words"] <= len(src.split()) <= config["max_source_words"] or not tgt:
            continue
        # No Latin character-ratio filter: that would exclude valid Chinese targets.
        mapping.setdefault(normalized(src), (src, tgt))
    return mapping


def split_keys(keys: list[str], config: dict) -> dict[str, list[str]]:
    groups = {}
    for key in sorted(keys):
        groups.setdefault(group_key(key), []).append(key)
    shuffled = sorted(groups)
    random.Random(config["seed"]).shuffle(shuffled)
    splits = {"tm": [], "development": [], "test": []}
    cursor = 0
    for split, size in (("tm", config["tm_size"]), ("development", config["development_size"]),
                        ("test", config["test_size"])):
        while len(splits[split]) < size and cursor < len(shuffled):
            # Surplus group members are discarded, never moved into another split.
            splits[split].extend(groups[shuffled[cursor]][:size-len(splits[split])])
            cursor += 1
        if len(splits[split]) < size:
            raise ValueError("Insufficient shared source groups for configured split sizes")
    return splits


def prepare(config: dict, raw: Path, output: Path) -> None:
    maps = {lang: load_parallel(raw / f"{PAIRS[lang]}.zip", lang, config) for lang in config["languages"]}
    shared = sorted(set.intersection(*(set(m) for m in maps.values())))
    splits = split_keys(shared, config)
    hashes = {}
    for lang in config["languages"]:
        for split, keys in splits.items():
            # Canonical English comes from one pair, making retrieval identical across targets.
            rows = [{"id": hashlib.sha256(key.encode()).hexdigest()[:16],
                     "src": maps[config["languages"][0]][key][0], "tgt": maps[lang][key][1],
                     "target": lang, "set": split} for key in keys]
            path = output / lang / f"{split}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            hashes[str(path.relative_to(output))] = digest(path)
    tm = read_rows(output / "es/tm.jsonl")
    test = read_rows(output / "es/test.jsonl")
    fuzzy = FuzzyRetriever(tm)
    timings, bands, misses = [], Counter(), []
    for row in test:
        start = time.perf_counter()
        hit = fuzzy.search(row["src"], k=1)[0]
        timings.append(1000 * (time.perf_counter()-start))
        bands[band_of(hit.score)] += 1
        exhaustive = max(cat_fuzzy(row["src"], r["src"]) for r in tm)
        if exhaustive > hit.score + 1e-9:
            misses.append({"id": row["id"], "prefilter_best": hit.score, "exhaustive_best": exhaustive,
                           "threshold_crossing": hit.score < config["fuzzy_threshold"] <= exhaustive})
    audit = {
        "status": "data preparation and fuzzy audit complete; no model inference performed",
        "config": config, "eligible_pairs": {lang: len(m) for lang, m in maps.items()},
        "shared_english_sources": len(shared), "split_sizes": {k: len(v) for k, v in splits.items()},
        "split_method": "shared normalized English source groups; numbers/placeholders collapsed within groups",
        "document_split": False, "limitation": "Moses files do not retain document IDs; semantic near-duplicates may remain.",
        "source_urls": {lang: f"https://object.pouta.csc.fi/OPUS-KDE4/v2/moses/{PAIRS[lang]}.txt.zip" for lang in maps},
        "archive_sha256": {lang: digest(raw / f"{PAIRS[lang]}.zip") for lang in maps},
        "file_sha256": hashes, "test_fuzzy_bands": dict(bands),
        "fuzzy_prefilter_audit": {"n": len(test), "missed_best": len(misses),
                                  "threshold_crossings": sum(r["threshold_crossing"] for r in misses), "rows": misses},
        "fuzzy_latency_ms": {"p50": float(np.percentile(timings, 50)), "p95": float(np.percentile(timings, 95))},
        "hardware": {"platform": platform.platform(), "processor": platform.processor(), "python": platform.python_version()},
    }
    write_json(output / "manifest.json", audit)
    # Share metadata and aggregate audit only; downloaded corpus content stays ignored.
    write_json(ROOT / "results/multilingual/data_audit.json", audit)
    print(json.dumps({k: audit[k] for k in ("shared_english_sources", "split_sizes", "test_fuzzy_bands")}, indent=2))


def run(config: dict, data: Path, output: Path, limit: int | None, split: str, workers: int = 4) -> None:
    from common.llm import JUDGE_MODEL, MT_MODEL, BASE_URL, REASONING_EFFORT, chat_json, validate_judgment
    from common.embed import RETRIEVAL_MODEL
    from locrag.pipeline import TMRouter, TranslationTask, LANGUAGES, translate
    if output.exists():
        raise ValueError("Use a new output directory; completed and partial runs are preserved")
    data_manifest = json.loads((data / "manifest.json").read_text())
    if data_manifest["config"] != config:
        raise ValueError("Prepared data configuration differs; prepare data with this config first")
    for name, expected in data_manifest["file_sha256"].items():
        if digest(data / name) != expected:
            raise ValueError(f"Prepared data checksum mismatch: {name}")
    output.mkdir(parents=True)
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()
    manifest = {"status": "running", "config": config, "split": split, "limit": limit, "workers": workers,
                "exploratory_smoke_run": limit is not None, "data_manifest_sha256": digest(data / "manifest.json"),
                "git_commit": git("rev-parse", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
                "code_sha256": {str(p.relative_to(ROOT)): digest(p) for d in (ROOT / "locrag", ROOT / "common")
                                for p in sorted(d.glob("*.py"))},
                "models": {"translation": MT_MODEL, "judge": JUDGE_MODEL, "retrieval": RETRIEVAL_MODEL},
                "endpoint": BASE_URL, "reasoning_effort": REASONING_EFFORT,
                "note": "Durations include cache hits when available; provider token/cost accounting is not available."}
    write_json(output / "manifest.json", manifest)
    metric = CHRF(word_order=0)
    all_rows = []
    for lang in config["languages"]:
        tm, test = read_rows(data / lang / "tm.jsonl"), read_rows(data / lang / f"{split}.jsonl")
        if limit is not None:
            test = test[:limit]
        router = TMRouter(tm, config["fuzzy_threshold"], config["semantic_min_sim"], config["k"])
        task = TranslationTask(lang, config["domain"])
        qvecs = router.semantic.encode_queries([r["src"] for r in test])
        def evaluate_segment(item):
            i, row = item
            records = []
            sentence_metric = CHRF(word_order=0)
            started = time.perf_counter()
            baseline = translate(row["src"], [], task=task)
            baseline_score = sentence_metric.sentence_score(baseline, [row["tgt"]]).score
            for policy in config["policies"]:
                decision = None if policy == "zero-shot" else router.route(row["src"], qvecs[i], policy=policy)
                examples = decision.examples if decision else []
                hypothesis = translate(row["src"], examples, task=task) if examples else baseline
                record = {**row, "policy": policy, "route": decision.route if decision else "none",
                          "fuzzy_best": decision.fuzzy_best if decision else router.fuzzy.search(row["src"], 1)[0].score,
                          "examples": examples, "zero_shot": baseline, "translation": hypothesis,
                          "chrf": sentence_metric.sentence_score(hypothesis, [row["tgt"]]).score,
                          "baseline_chrf": baseline_score}
                # Judge only distinct treatments. Identical outputs are deterministic ties;
                # their absolute accuracy remains unassessed, never assumed true.
                if hypothesis == baseline:
                    record["judgment"] = {"winner": "tie", "reason": "Identical outputs", "accuracy_assessed": False}
                else:
                    flipped = int(hashlib.sha256((row["id"]+policy+lang).encode()).hexdigest(), 16) % 2 == 0
                    a, b = (hypothesis, baseline) if flipped else (baseline, hypothesis)
                    prompt = (f"Compare two {LANGUAGES[lang]} translations for {config['domain']}. "
                              "Judge accuracy to the English source first (negation, numbers, units, conditions, "
                              "placeholders, omissions/additions). Then judge consistency with relevant TM terminology. "
                              "TM is evidence, not ground truth; do not reward copying incorrect content. "
                              f"Source: {row['src']}\nReference: {row['tgt']}\nTM: {json.dumps(examples, ensure_ascii=False)}\n"
                              f"A: {a}\nB: {b}\nReturn JSON with winner (A/B/tie), a_accurate, b_accurate, "
                              "a_consistent, b_consistent (JSON booleans), error_categories (list drawn from "
                              "negation/numbers/units/conditions/placeholders/omission/addition/terminology/other), reason.")
                    try:
                        judgment = validate_judgment(chat_json(prompt, model=JUDGE_MODEL, max_tokens=600), localization=True)
                        categories = judgment.get("error_categories")
                        allowed = {"negation", "numbers", "units", "conditions", "placeholders", "omission", "addition", "terminology", "other"}
                        if not isinstance(categories, list) or any(not isinstance(x, str) or x not in allowed for x in categories):
                            raise ValueError("Judge error_categories must be a list of supported labels")
                        judgment["treatment_is_a"] = flipped
                        judgment["accuracy_assessed"] = True
                        record["judgment"] = judgment
                    except (ValueError, RuntimeError) as exc:
                        record["judgment"] = {"winner": "error", "error_type": type(exc).__name__}
                record["segment_elapsed_ms"] = (time.perf_counter()-started)*1000
                records.append(record)
            return records
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for i, records in enumerate(pool.map(evaluate_segment, enumerate(test))):
                all_rows.extend(records)
                with (output / "rows.jsonl").open("a", encoding="utf-8") as f:
                    for record in records:
                        f.write(json.dumps(record, ensure_ascii=False)+"\n")
                print(f"{lang}: {i+1}/{len(test)} segments", flush=True)
    summary = {}
    for lang in config["languages"]:
        summary[lang] = {}
        for policy in config["policies"]:
            rows = [r for r in all_rows if r["target"] == lang and r["policy"] == policy]
            judgments = Counter()
            accurate = Counter()
            consistent = Counter()
            errors = Counter()
            for r in rows:
                j = r["judgment"]
                w = j["winner"]
                key = w if w in ("tie", "error") else "treatment" if (w == "A") == j["treatment_is_a"] else "baseline"
                judgments[key] += 1
                if j.get("accuracy_assessed"):
                    accurate["assessed_n"] += 1
                    treatment_accurate = j["a_accurate"] if j["treatment_is_a"] else j["b_accurate"]
                    baseline_accurate = j["b_accurate"] if j["treatment_is_a"] else j["a_accurate"]
                    accurate["treatment"] += treatment_accurate
                    accurate["baseline"] += baseline_accurate
                    accurate["introduced_errors"] += baseline_accurate and not treatment_accurate
                    accurate["fixed_errors"] += treatment_accurate and not baseline_accurate
                    consistent["assessed_n"] += 1
                    consistent["treatment"] += j["a_consistent"] if j["treatment_is_a"] else j["b_consistent"]
                    consistent["baseline"] += j["b_consistent"] if j["treatment_is_a"] else j["a_consistent"]
                errors.update(j.get("error_categories", []))
            summary[lang][policy] = {
                "n": len(rows), "chrf": metric.corpus_score([r["translation"] for r in rows], [[r["tgt"] for r in rows]]).score,
                "paired_sentence_chrf_delta": paired_mean_ci([r["chrf"]-r["baseline_chrf"] for r in rows]),
                "routes": dict(Counter(r["route"] for r in rows)), "judgments": dict(judgments),
                "accuracy_on_distinct_outputs": dict(accurate), "error_categories": dict(errors),
                "terminology_consistency_on_distinct_outputs": dict(consistent),
                "by_fuzzy_band": {band: {"n": len(subset), "paired_sentence_chrf_delta": paired_mean_ci([
                    r["chrf"]-r["baseline_chrf"] for r in subset])} for band in ("100", "95-99", "85-94", "75-84", "50-74", "<50")
                    if (subset := [r for r in rows if band_of(r["fuzzy_best"]) == band])},
            }
    write_json(output / "summary.json", summary)
    manifest.update(status="complete", metric_signature=str(metric.get_signature()), rows_sha256=digest(output / "rows.jsonl"))
    write_json(output / "manifest.json", manifest)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("prepare", "plan", "run"))
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--raw", type=Path, default=ROOT / "data/raw/KDE4")
    ap.add_argument("--data", type=Path, default=ROOT / "data/multilingual")
    ap.add_argument("--output", type=Path, default=ROOT / "results/multilingual/run-v1")
    ap.add_argument("--split", choices=("development", "test"), default="test")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    if args.limit is not None and args.limit < 1:
        ap.error("--limit must be positive")
    if args.workers < 1:
        ap.error("--workers must be positive")
    if args.action == "prepare":
        prepare(config, args.raw, args.data)
    elif args.action == "plan":
        n = min(args.limit, config[args.split+"_size"]) if args.limit else config[args.split+"_size"]
        print(json.dumps({"languages": config["languages"], "segments_per_language": n, "split": args.split,
                          "translation_call_upper_bound": n*len(config["languages"])*len(config["policies"]),
                          "judge_call_upper_bound": n*len(config["languages"])*(len(config["policies"])-1),
                          "embedding_calls": "model batch-size dependent; shared English sources reuse the TM embedding cache",
                          "cost": "unknown until provider pricing and token usage are supplied; no calls made"}, indent=2))
    else:
        run(config, args.data, args.output, args.limit, args.split, args.workers)


if __name__ == "__main__":
    main()
