#!/usr/bin/env python3
"""T064: make committed evidence portable.

The probe scripts write their own absolute paths (Windows temp worktrees), which
is exactly the evidence-hygiene defect this task raises as review finding R5
against T055. This pass rewrites every string that points inside the repository
to a repository-relative path, so a reader on another machine can still resolve
it. Run it after the probes, before committing.

Run:  python experiments/T064-.../inputs/normalize_evidence.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = EXP.parents[1]
PREVIEW = EXP / "preview"


def walk(node):
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(v) for v in node]
    if isinstance(node, str):
        text = node.replace("\\", "/")
        marker = f"{ROOT.name}/"
        if marker in text:
            return text[text.index(marker) + len(marker):]
        return node
    return node


def main() -> int:
    changed = []
    for path in sorted(PREVIEW.glob("*.json")):
        before = json.loads(path.read_text(encoding="utf-8"))
        after = walk(before)
        if after != before:
            path.write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
            changed.append(path.name)
    print(json.dumps({"normalized": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
