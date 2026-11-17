"""Config loading, hashing and small I/O helpers shared by the study stages."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "experiments" / "study_v2.yaml"
DATA_DIR = ROOT / "data" / "study"
RESULTS_DIR = ROOT / "results" / "study"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sha(text: str, n: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_state() -> dict:
    def git(*args):
        try:
            return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
        except (OSError, subprocess.CalledProcessError):
            return ""
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}


def code_hashes() -> dict:
    dirs = [ROOT / "locrag" / "study", ROOT / "common", ROOT / "qe" / "locrag_qe"]
    return {str(p.relative_to(ROOT)): file_sha256(p) for d in dirs if d.exists() for p in sorted(d.glob("*.py"))}
