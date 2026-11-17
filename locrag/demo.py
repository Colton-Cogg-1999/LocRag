"""Build the dependency-free, recorded-results workbench: python -m locrag.demo."""
import hashlib
import json
import shutil
from pathlib import Path

from locrag.evidence import ROOT, build_evidence, read_rows


def build(output: Path | None = None) -> Path:
    output = output or ROOT / "demo/dist"
    output.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / "demo/src").iterdir():
        if path.is_file():
            shutil.copy2(path, output / path.name)
    rows = read_rows(ROOT / "results/router/rows.jsonl")
    for i, row in enumerate(rows):
        row["row_number"] = i + 1
        row["id"] = hashlib.sha256(row["src"].encode()).hexdigest()[:12]
    data = {"rows": rows, "evidence": build_evidence(),
            "curated": [{"index": 10, "label": "Terminology recovered", "tag": "Real segment"},
                        {"index": 300, "label": "A paraphrase found", "tag": "Constructed probe"},
                        {"index": 0, "label": "When to decline", "tag": "Weak match"},
                        {"index": 197, "label": "When retrieval hurts", "tag": "Accuracy failure"},
                        {"index": 393, "label": "Opposite meaning", "tag": "Negation stress test"}]}
    audit = ROOT / "results/multilingual/data_audit.json"
    data["multilingual"] = json.loads(audit.read_text()) if audit.exists() else None
    (output / "data.js").write_text("window.LOCRAG_DATA = " + json.dumps(data, ensure_ascii=True) + ";\n", encoding="utf-8")
    shutil.copy2(ROOT / "results/audit/summary.json", output / "evidence.json")
    return output


if __name__ == "__main__":
    print(f"Built {build()}. Serve with python -m http.server 8000 --directory demo/dist")
