"""LocRAG 2.0 study CLI.

  uv run python -m locrag.study prepare                         # build TMs + held-out sets (offline)
  uv run python -m locrag.study retrieve                        # candidates for every held-out source
  uv run python -m locrag.study generate --run dev-smoke --split development --per-band 2
  uv run python -m locrag.study audit    --run dev-smoke        # Sonnet reuse labels + extractor audit
  uv run python -m locrag.study qe       --run dev-smoke        # isolated, blinded QE scoring (local CPU)
  uv run python -m locrag.study analyze  --run dev-smoke        # report.md + summary.json
  uv run python -m locrag.study cost     --run dev-smoke        # measured spend + projection to test

Every stage is resumable; rerunning skips completed (row, condition) outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

from locrag.study.config import (DATA_DIR, DEFAULT_CONFIG, RESULTS_DIR, code_hashes, config_hash, git_state,
                                 load_config, write_json)
from locrag.study.data import load_heldout

CANDIDATES = DATA_DIR / "candidates.jsonl"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def select_rows(cfg: dict, split: str, per_band: int | None, seed: int) -> list[dict]:
    rows = load_heldout(DATA_DIR, split)
    if per_band is None:
        return rows
    by_stratum: dict[tuple, list[str]] = {}
    for r in rows:
        by_stratum.setdefault((r["corpus"], r["band"]), [])
        if r["src_id"] not in by_stratum[(r["corpus"], r["band"])]:
            by_stratum[(r["corpus"], r["band"])].append(r["src_id"])
    keep = set()
    for ids in by_stratum.values():
        keep |= set(sorted(ids, key=lambda s: hashlib.sha256(f"{seed}:{s}".encode()).hexdigest())[:per_band])
    return [r for r in rows if r["src_id"] in keep]


def run_rows(run_dir: Path) -> list[dict]:
    ids = set(json.loads((run_dir / "rows.json").read_text()))
    split = json.loads((run_dir / "manifest.json").read_text())["split"]
    return [r for r in load_heldout(DATA_DIR, split) if r["row_id"] in ids]


def ensure_run(args, cfg) -> Path:
    run_dir = RESULTS_DIR / args.run
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text())
        if m["config_hash"] != config_hash(cfg):
            raise SystemExit(f"Config changed since run '{args.run}' started ({m['config_hash']} → {config_hash(cfg)}). "
                             "Use a new --run name.")
        return run_dir
    if not getattr(args, "split", None):
        raise SystemExit("New run: pass --split")
    rows = select_rows(cfg, args.split, args.per_band, cfg["seed"])
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "rows.json", sorted(r["row_id"] for r in rows))
    from locrag.study.prompts import TEMPLATE_VERSION, template_hashes
    data_manifests = {p.parent.name: json.loads(p.read_text()).get("files_sha256")
                      for p in sorted(DATA_DIR.glob("*/manifest.json"))}
    write_json(manifest_path, {
        "run": args.run, "split": args.split, "per_band": args.per_band, "n_rows": len(rows),
        "n_sources": len({r["src_id"] for r in rows}), "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config_hash": config_hash(cfg), "config": cfg, "git": git_state(), "code_sha256": code_hashes(),
        "template_version": TEMPLATE_VERSION, "template_sha": template_hashes(), "data_sha256": data_manifests,
        "rows_by_corpus_band": {f"{c}/{b}": n for (c, b), n in sorted(Counter((r["corpus"], r["band"]) for r in rows).items())},
    })
    log(f"new run {args.run}: {len(rows)} rows ({args.split})")
    return run_dir


def cmd_prepare(args, cfg):
    from locrag.study.data import build_corpus
    for name, c in cfg["corpora"].items():
        m = build_corpus(name, c, cfg["seed"], cfg["heldout_declustering_fuzzy"], DATA_DIR / name)
        log(f"{name}: TM {m['tm_size']:,}; selected {m['selected_sources']}; shortfall {m['shortfall']}")


def cmd_retrieve(args, cfg):
    from locrag.study.retrieval import run_retrieval
    run_retrieval(DATA_DIR, cfg, CANDIDATES, log)


def cmd_generate(args, cfg):
    from locrag.study.generate import Generator, noise_subset
    from locrag.study.llm import Client
    from locrag.study.retrieval import load_candidates
    run_dir = ensure_run(args, cfg)
    rows = run_rows(run_dir)
    gen = Generator(cfg, DATA_DIR, run_dir, Client(), load_candidates(CANDIDATES), log)
    conditions = args.conditions.split(",") if args.conditions else cfg["conditions"]
    nf = cfg["noise_floor"]
    split = json.loads((run_dir / "manifest.json").read_text())["split"]
    noise_ids = (noise_subset(rows, int(len(rows) * nf["dev_fraction"]), cfg["seed"]) if split == "development"
                 else noise_subset(rows, nf["test_rows"], cfg["seed"]))
    workers = args.workers or cfg["translation"]["workers"]
    gen.run_tm_as_is(rows)
    if "structured_ctx" in conditions:
        gen.run_extractions(rows, workers)
    gen.run_translations(rows, conditions, noise_ids, workers)
    if not args.skip_nmt:
        from locrag.study.nmt import DeepL
        gen.run_nmt(rows, DeepL(model_type=cfg["nmt"].get("model_type", "latency_optimized")))
    log("generation complete")


def cmd_audit(args, cfg):
    from locrag.study.audit import Auditor
    from locrag.study.llm import Client
    from locrag.study.retrieval import load_candidates
    run_dir = ensure_run(args, cfg)
    rows = run_rows(run_dir)
    aud = Auditor(cfg, run_dir, Client(), log)
    overrides = {k: getattr(args, k) for k in ("reuse_rows", "extraction_sample", "mqm_per_condition") if getattr(args, k)}
    if overrides:
        amend = run_dir / "amendments.jsonl"
        with amend.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": "audit", "overrides": overrides,
                                "reason": "OpenRouter credit limit (~$13.66 remaining)"}) + "\n")
    if args.sync:
        aud.use_batch = False
    tasks = args.tasks.split(",")
    if "reuse" in tasks:
        reuse_rows = rows
        split = json.loads((run_dir / "manifest.json").read_text())["split"]
        n_reuse = args.reuse_rows or cfg["auditor"].get("reuse_test_rows")
        if split == "test" and n_reuse:
            # Budget: reuse labels on a stratified test subsample (documented in the plan); seed-offset 2
            from locrag.study.generate import noise_subset
            keep = noise_subset(rows, n_reuse, cfg["seed"] + 2)
            reuse_rows = [r for r in rows if r["row_id"] in keep]
            log(f"reuse classification on a stratified subsample: {len(reuse_rows)}/{len(rows)} rows")
        aud.reuse(reuse_rows, load_candidates(CANDIDATES), DATA_DIR, cfg["retrieval"]["k"])
    if "extraction" in tasks:
        aud.extraction_audit(rows, DATA_DIR, args.extraction_sample or cfg["auditor"]["extraction_audit_sample"], cfg["seed"])
    if "mqm" in tasks:
        from locrag.study.analyze import mqm_sample
        if args.mqm_per_condition:
            cfg = {**cfg, "auditor": {**cfg["auditor"], "mqm_sample_per_condition": args.mqm_per_condition}}
        aud.mqm(mqm_sample(run_dir, rows, cfg))
    log("audit complete")


def cmd_qe(args, cfg):
    from locrag.study.data import load_references
    from locrag.study.generate import latest_outputs
    from locrag.study.qe_bridge import score_run
    run_dir = ensure_run(args, cfg)
    rows = run_rows(run_dir)
    sources = {r["row_id"]: r["src"] for r in rows}
    latest = {k: v for k, v in latest_outputs(run_dir / "translations.jsonl").items() if k[0] in sources}
    outs = list(latest.values())
    # QE validity probes: corrupted zero-shot outputs, exported in the same blinded, shuffled file
    probe_path = run_dir / "probes.jsonl"
    if not probe_path.exists():
        from locrag.study.analyze import make_probes
        from locrag.study.data import load_tm
        from locrag.study.retrieval import load_candidates
        tms: dict = {}
        probes = make_probes({r["row_id"]: r for r in rows}, latest, load_candidates(CANDIDATES),
                             lambda c, l: tms.setdefault((c, l), load_tm(DATA_DIR, c, l)), cfg["seed"])
        probe_path.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in probes), encoding="utf-8")
    from locrag.study.data import read_jsonl
    probes = read_jsonl(probe_path)
    metrics = args.metrics.split(",") if args.metrics else [cfg["qe"]["primary"], cfg["qe"]["robustness"], "comet22"]
    refs = load_references(DATA_DIR)
    qe_only = [m for m in metrics if m in ("cometkiwi22", "metricx24_qe")]
    score_run(run_dir, outs + probes, sources, refs, qe_only, cfg["seed"], log)  # probes: reference-free metrics only
    ref_outs = outs
    n_ref = cfg["qe"].get("reference_test_rows")
    if json.loads((run_dir / "manifest.json").read_text())["split"] == "test" and n_ref:
        from locrag.study.generate import noise_subset
        keep = noise_subset(rows, n_ref, cfg["seed"] + 3)
        ref_outs = [o for o in outs if o["row_id"] in keep]
        log(f"reference-based metrics on a stratified subsample: {len(keep)}/{len(rows)} rows")
    score_run(run_dir, ref_outs, sources, refs, [m for m in metrics if m not in qe_only], cfg["seed"], log)
    log("QE complete")


def cmd_analyze(args, cfg):
    from locrag.study.analyze import analyze
    run_dir = ensure_run(args, cfg)
    analyze(run_dir, run_rows(run_dir), cfg, log, noise_from=args.noise_from)


def cmd_cost(args, cfg):
    from locrag.study.analyze import cost_report
    run_dir = ensure_run(args, cfg)
    print(json.dumps(cost_report(run_dir, run_rows(run_dir), cfg), indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare")
    sub.add_parser("retrieve")
    for name in ("generate", "audit", "qe", "analyze", "cost"):
        p = sub.add_parser(name)
        p.add_argument("--run", required=True)
        p.add_argument("--split", choices=("development", "test"))
        p.add_argument("--per-band", type=int, help="sources per (corpus, band) stratum; default all")
        if name == "generate":
            p.add_argument("--conditions")
            p.add_argument("--workers", type=int)
            p.add_argument("--skip-nmt", action="store_true")
        if name == "audit":
            p.add_argument("--tasks", default="reuse,extraction")
            p.add_argument("--sync", action="store_true", help="synchronous calls instead of the Batch API")
            # budget overrides (recorded in the run log; config hash unchanged)
            p.add_argument("--reuse-rows", type=int, help="test reuse subsample size (overrides config)")
            p.add_argument("--extraction-sample", type=int)
            p.add_argument("--mqm-per-condition", type=int)
        if name == "qe":
            p.add_argument("--metrics")
        if name == "analyze":
            p.add_argument("--noise-from", help="run whose A/A′ noise floor to use (frozen dev floor for test)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    globals()[f"cmd_{args.cmd}"](args, cfg)


if __name__ == "__main__":
    main()
