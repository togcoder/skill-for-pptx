#!/usr/bin/env python3
"""Replay the reversible repair on a git revision (or the working tree) and count changes.

The working tree is already repaired, so re-running the tool there must report
zero. This script shows the same tool on the base blob, which is the number
quoted in the T065 report, and proves the repair is idempotent.

    python inputs/replay_repair.py --rev ac5b45e --out artifacts/repair-replay.json
    python inputs/replay_repair.py --worktree
"""
import argparse
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
FILES = [
    "docs/CHANGELOG.md",
    "domains/README.md",
    "experiments/T045-20261101-opencode-advanced-docx/REPORT.md",
    "experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md",
    "research/claims/T050-opencode-20261102.md",
]


def load_repair():
    spec = importlib.util.spec_from_file_location("repair_mojibake", HERE / "repair_mojibake.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="ac5b45e")
    ap.add_argument("--worktree", action="store_true")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    repair = load_repair()
    rows = []
    for rel in FILES:
        if a.worktree:
            with open(rel, encoding="utf-8", newline="") as fh:
                text = fh.read()
            source = "worktree"
        else:
            raw = subprocess.run(["git", "show", f"{a.rev}:{rel}"], capture_output=True)
            text = raw.stdout.decode("utf-8")
            source = a.rev
        _, changes = repair.repair_text(text)
        rows.append({"path": rel, "source": source, "sequences": len(changes)})
        print(f"{rel}: {len(changes)} sequence(s) from {source}")

    total = sum(r["sequences"] for r in rows)
    print(f"total: {total}")
    if a.out:
        a.out.write_text(json.dumps({"rows": rows, "total": total}, indent=2) + "\n",
                         encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
