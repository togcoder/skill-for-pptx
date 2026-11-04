#!/usr/bin/env python3
"""Count mojibake markers, BOMs and control characters per Markdown file, before/after (T065).

`before` reads the files from a git revision, `after` from the working tree.

    python inputs/encoding_audit.py --rev ac5b45e --out artifacts/encoding-audit.json
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARKERS = ("Ã", "â€", "á»", "Ä‘")
INLINE_CODE = re.compile(r"`[^`\n]*`")


def markers(text: str) -> int:
    """Every marker occurrence, including ones inside an inline code span."""
    return sum(text.count(m) for m in MARKERS)


def flagged_markers(text: str) -> int:
    """Markers the layout rule reports: marker-only spans and pragma lines are exempt."""
    sys.path.insert(0, str(Path("lab/tools").resolve()))
    import check_layout
    total = 0
    for line in text.splitlines():
        if check_layout.ALLOW_MOJIBAKE in line:
            continue
        total += sum(check_layout._strip_marker_quotes(line).count(m)
                     for m in check_layout.MOJIBAKE)
    return total


def controls(text: str) -> list[str]:
    out = set()
    for ch in text:
        code = ord(ch)
        if ch in "\t\n\r":
            continue
        if code < 0x20 or 0x7f <= code <= 0x9f:
            out.add(f"U+{code:04X}")
    return sorted(out)


def audit(text: str) -> dict:
    return {
        "markers": markers(text),
        "flagged_markers": flagged_markers(text),
        "bom": text.startswith("\ufeff"),
        "controls": controls(text),
        "chars": len(text),
        "valid_utf8": True,
    }


def git_show(rev: str, path: str) -> str | None:
    raw = subprocess.run(["git", "show", f"{rev}:{Path(path).as_posix()}"], capture_output=True)
    if raw.returncode:
        return None
    try:
        return raw.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="ac5b45e")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    root = Path(".").resolve()
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md")
                   if not any(part in {".git", ".venv", "node_modules", "__pycache__", "workspace"}
                              for part in p.relative_to(root).parts))
    rows = []
    for rel in files:
        before_text = git_show(a.rev, rel)
        after_text = Path(rel).read_text(encoding="utf-8", errors="strict")
        before = audit(before_text) if before_text is not None else None
        after = audit(after_text)
        if before is None and after["markers"] == 0 and not after["bom"] and not after["controls"]:
            continue
        changed = before is None or any(before[k] != after[k] for k in ("markers", "bom", "controls"))
        if not changed:
            continue
        rows.append({"path": rel, "before": before, "after": after})

    a.out.write_text(json.dumps({"rev": a.rev, "files": rows}, indent=2, ensure_ascii=True) + "\n",
                     encoding="utf-8")
    print(f"{len(rows)} file(s) with encoding findings")
    for r in rows:
        b = r["before"]
        print(f'  {r["path"]}: markers {b["markers"] if b else "-"} -> {r["after"]["markers"]}, '
              f'bom {(b or {}).get("bom", "-")} -> {r["after"]["bom"]}, '
              f'controls {(b or {}).get("controls", "-")} -> {r["after"]["controls"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
