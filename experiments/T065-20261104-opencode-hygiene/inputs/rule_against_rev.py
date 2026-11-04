#!/usr/bin/env python3
"""Apply the T065 Markdown rule to a git revision, without checking it out.

The rule lives in lab/tools/check_layout.py and reads files from disk. This
script feeds it the *base revision's* blobs instead, so the report can show
what the rule would have reported before the repair.

    python inputs/rule_against_rev.py --rev ac5b45e
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path("lab/tools").resolve()))
import check_layout  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="ac5b45e")
    a = ap.parse_args()

    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", a.rev],
                             capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    md = [p for p in listing if p.endswith(".md")]
    findings = 0
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "file.md"
        for rel in md:
            blob = subprocess.run(["git", "show", f"{a.rev}:{rel}"], capture_output=True).stdout
            scratch.write_bytes(blob)
            for line, kind, detail in check_layout._text_problems(scratch):
                findings += 1
                print(f"{rel}:{line}: {kind}: {detail}")
    print(f"{findings} finding(s) in {len(md)} Markdown file(s) at {a.rev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
