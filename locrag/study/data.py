"""Build the v2 retrieval corpora (TMs) and band-stratified held-out sets.

    uv run python -m locrag.study prepare

Outputs in data/study/<corpus>/ (git-ignored):
  tm_<lang>.jsonl       {"tm_id", "src", "tgt"}                   the retrieval corpus
  heldout.jsonl         {"row_id", "src_id", "corpus", "lang", "split", "src", "band", "fuzzy_best"}
  references.jsonl      {"row_id", "ref", "ref_in_tm_targets"}   NEVER read by retrieval/translation stages
  manifest.json         counts, natural band frequencies, shortfalls, hashes

Leakage rules (docs/v2-assessment-and-plan.md §3):
  * normalized-source groups (case/space/number/placeholder-collapsed) never cross TM and held-out,
    except the designed exact-match ("100") band, whose held-out reference is a *different* translation;
  * held-out sources are de-clustered: no two (same corpus) with word-level fuzzy >= the configured bound;
  * held-out ↔ TM similarity is the experimental variable and is measured, not removed.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import zipfile
from collections import Counter
from pathlib import Path

from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

from locrag.retrievers import band_of
from locrag.study.config import ROOT, file_sha256, write_json
from locrag.study.fuzzy import ExactFuzzyIndex

BAND_ORDER = ["100", "95-99", "85-94", "75-84", "50-74", "<50"]
_ALPHA = re.compile(r"[A-Za-z]")
KDE_PAIRS = {"es": "en-es", "de": "de-en", "zh_CN": "en-zh_CN"}


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def group_key(text: str) -> str:
    return re.sub(r"%\d+|\d+(?:[.,]\d+)*", "#", normalized(text))


def stable_id(prefix: str, text: str) -> str:
    return prefix + hashlib.sha256(normalized(text).encode()).hexdigest()[:12]


def _source_ok(src: str, cfg: dict) -> bool:
    n = len(src.split())
    return cfg["min_words"] <= n <= cfg["max_words"] and len(_ALPHA.findall(src)) >= 0.6 * len(src.replace(" ", ""))


def _target_ok(src: str, tgt: str, lang: str) -> bool:
    if not tgt:
        return False
    if lang == "zh_CN":  # no Latin length-ratio filter for Chinese
        return True
    return 0.5 < len(tgt) / len(src) < 2.2


def _collect(pairs, cfg: dict, lang: str, table: dict) -> None:
    """table[norm_src] = {"src": first surface form, "tgts": distinct targets in order}"""
    for src, tgt in pairs:
        src, tgt = src.strip(), tgt.strip()
        if not _source_ok(src, cfg) or not _target_ok(src, tgt, lang):
            continue
        entry = table.setdefault(normalized(src), {"src": src, "tgts": {}})
        tgts = entry["tgts"].setdefault(lang, [])
        if normalized(tgt) not in {normalized(t) for t in tgts}:
            tgts.append(tgt)


def load_emea(cfg: dict) -> dict:
    raw = ROOT / cfg["raw"]
    table: dict = {}
    with (raw / "EMEA.en-es.en").open(encoding="utf-8") as en, (raw / "EMEA.en-es.es").open(encoding="utf-8") as es:
        _collect(zip(en, es), cfg, "es", table)
    return table


def load_kde4(cfg: dict) -> dict:
    raw = ROOT / cfg["raw"]
    table: dict = {}
    for lang in cfg["targets"]:
        pair = KDE_PAIRS[lang]
        with zipfile.ZipFile(raw / f"{pair}.zip") as z:
            # LF-only split: Unicode splitlines() would break alignment on U+2028 etc.
            src = z.read(f"KDE4.{pair}.en").decode("utf-8").rstrip("\n").split("\n")
            tgt = z.read(f"KDE4.{pair}.{lang}").decode("utf-8").rstrip("\n").split("\n")
        if len(src) != len(tgt):
            raise ValueError(f"Alignment length mismatch in {pair}")
        _collect(zip(src, tgt), cfg, lang, table)
    # shared English sources only: retrieval is identical across targets
    return {k: v for k, v in table.items() if all(v["tgts"].get(l) for l in cfg["targets"])}


def _decluster_accept(enc: str, accepted: list[str], bound: float) -> bool:
    if not accepted:
        return True
    hit = process.extractOne(enc, accepted, scorer=Levenshtein.normalized_similarity, processor=None,
                             score_cutoff=bound / 100.0)
    return hit is None


def build_corpus(name: str, cfg: dict, seed: int, decluster: float, out_dir: Path) -> dict:
    table = load_emea(cfg) if cfg["kind"] == "emea" else load_kde4(cfg)
    langs = cfg["targets"]
    rng = random.Random(f"{seed}:{name}")

    groups: dict[str, list[str]] = {}
    for key in sorted(table):
        groups.setdefault(group_key(key), []).append(key)
    order = sorted(groups)
    rng.shuffle(order)

    tm_keys: list[str] = []
    cursor = 0
    while len(tm_keys) < cfg["tm_size"] and cursor < len(order):
        tm_keys.extend(groups[order[cursor]])  # whole groups go to the TM
        cursor += 1
    tm_keys = tm_keys[: cfg["tm_size"]]
    # one representative per remaining group: numeric/placeholder variants never both enter held-out
    pool_keys = [groups[g][0] for g in order[cursor:]][: cfg["pool_scan_limit"]]

    tm_rows = {lang: [] for lang in langs}
    for i, key in enumerate(tm_keys):
        for lang in langs:
            tm_rows[lang].append({"tm_id": f"{name[0]}{i}", "src": table[key]["src"], "tgt": table[key]["tgts"][lang][0]})
    tm_sources = [table[k]["src"] for k in tm_keys]
    index = ExactFuzzyIndex(tm_sources)
    tm_targets = {lang: {normalized(r["tgt"]) for r in tm_rows[lang]} for lang in langs}

    # ---- band assignment for the pool (exact word-level fuzzy vs the full TM)
    pool_src = [table[k]["src"] for k in pool_keys]
    best = index.best_scores(pool_src)
    pool_bands = [band_of(float(s)) for s in best]
    natural = Counter(b for b in pool_bands)

    # ---- designed exact-match band: TM sources with >= 2 distinct translations in every target
    exact_keys = [k for k in tm_keys if all(len(table[k]["tgts"][l]) >= 2 for l in langs)]
    rng.shuffle(exact_keys)

    quotas = cfg["bands"]
    dev_q = cfg["dev_per_band"]
    candidates: dict[str, list[tuple[str, float]]] = {b: [] for b in BAND_ORDER}
    for key, band, score in zip(pool_keys, pool_bands, best):
        if band != "100":  # tokenization-equivalent of a TM source: excluded; band 100 is built by design
            candidates[band].append((key, float(score)))
    candidates["100"] = [(k, 100.0) for k in exact_keys]

    enc_index = ExactFuzzyIndex([table[k]["src"] for b in BAND_ORDER for k, _ in candidates[b]])
    accepted_enc: list[str] = []
    selected = {"development": [], "test": []}
    shortfall = {}
    for band in BAND_ORDER:
        need = {"development": dev_q, "test": quotas[band]}
        for key, score in candidates[band]:
            if need["development"] == 0 and need["test"] == 0:
                break
            enc = enc_index._encode(table[key]["src"])
            if not _decluster_accept(enc, accepted_enc, decluster):
                continue
            accepted_enc.append(enc)
            split = "development" if need["development"] else "test"
            need[split] -= 1
            selected[split].append((key, band, score))
        if any(need.values()):
            shortfall[band] = need

    heldout, refs = [], []
    for split, items in selected.items():
        for key, band, score in items:
            entry = table[key]
            src_id = stable_id(name[0], key)
            for lang in langs:
                # band 100: the TM holds tgts[0]; the held-out reference is a different translation
                ref = entry["tgts"][lang][1] if band == "100" else entry["tgts"][lang][0]
                row_id = f"{src_id}:{lang}"
                heldout.append({"row_id": row_id, "src_id": src_id, "corpus": name, "lang": lang, "split": split,
                                "src": entry["src"], "band": band, "fuzzy_best": round(score, 2)})
                refs.append({"row_id": row_id, "ref": ref, "ref_in_tm_targets": normalized(ref) in tm_targets[lang]})

    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for lang in langs:
        p = out_dir / f"tm_{lang}.jsonl"
        _write_jsonl(p, tm_rows[lang])
        files[p.name] = file_sha256(p)
    for fname, rows in (("heldout.jsonl", heldout), ("references.jsonl", refs)):
        _write_jsonl(out_dir / fname, rows)
        files[fname] = file_sha256(out_dir / fname)

    count = Counter((r["split"], r["band"]) for r in heldout if r["lang"] == langs[0])
    manifest = {
        "corpus": name, "config": cfg, "seed": seed, "eligible_sources": len(table), "tm_size": len(tm_keys),
        "pool_scanned": len(pool_keys), "pool_natural_band_counts": dict(natural),
        "exact_match_candidates": len(exact_keys),
        "selected_sources": {f"{s}/{b}": n for (s, b), n in sorted(count.items())},
        "shortfall": shortfall, "heldout_declustering_fuzzy": decluster,
        "ref_in_tm_targets": sum(r["ref_in_tm_targets"] for r in refs), "files_sha256": files,
    }
    write_json(out_dir / "manifest.json", manifest)
    return manifest


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def read_jsonl(path: Path | str) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    # LF only: str.splitlines() would also split on U+2028/U+0085 inside JSON strings
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def load_tm(data_dir: Path, corpus: str, lang: str) -> list[dict]:
    return read_jsonl(data_dir / corpus / f"tm_{lang}.jsonl")


def load_heldout(data_dir: Path, split: str | None = None) -> list[dict]:
    rows = []
    for d in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        rows += [r for r in read_jsonl(d / "heldout.jsonl") if split is None or r["split"] == split]
    return rows


def load_references(data_dir: Path) -> dict[str, dict]:
    """Only evaluation code may call this."""
    out = {}
    for d in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        out.update({r["row_id"]: r for r in read_jsonl(d / "references.jsonl")})
    return out
