#!/usr/bin/env python3
"""Restore lines damaged by a lossy code-page round trip, using an earlier git blob.

The reversible repair (repair_mojibake.py) cannot rebuild a byte that the code
page never had: cp1252 leaves 0x81, 0x8D, 0x8F, 0x90 and 0x9D undefined, so
"giờ" (E1 BB 9D) survives as "giá»" plus a dropped byte. No decoder can guess
that byte from the file.

Git has the answer: the damage landed in a few commits, and the revision just
before them holds the same lines undamaged. This tool

1. reads the damaged file and the two revisions,
2. pairs a damaged line with its closest undamaged counterpart,
3. accepts the pair only if the *damage can be simulated exactly*: taking the
   undamaged line, encoding it as UTF-8, decoding each byte with a single-byte
   code page and dropping the bytes the code page lacks reproduces the damaged
   line character for character.

Because the acceptance test is exact equality, a real content edit in the same
line cannot sneak in: an edited line no longer simulates its old form, so the
pair is rejected and printed for a human to look at.

    python inputs/restore_from_git.py FILE GOOD_REV BAD_REV --dry-run
"""
import argparse
import difflib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARKERS = ("Ã", "â€", "á»", "Ä‘", "áº", "Ă")
CODECS = ("cp1258", "cp1252")
THRESHOLD = 0.90
BOM = "\ufeff"


def blob(rev: str, path: str) -> list[str]:
    raw = subprocess.run(["git", "show", f"{rev}:{Path(path).as_posix()}"], capture_output=True)
    if raw.returncode:
        raise SystemExit(f"cannot read {rev}:{Path(path).as_posix()}: "
                         f"{raw.stderr.decode('utf-8', 'replace')}")
    return raw.stdout.decode("utf-8", "replace").splitlines()


def simulate(line: str, codec: str) -> str:
    """Reproduce the damage: UTF-8 bytes read through one code page, undefined bytes dropped."""
    out = []
    for b in line.encode("utf-8"):
        if b < 0x80:
            out.append(chr(b))
            continue
        try:
            out.append(bytes([b]).decode(codec))
        except UnicodeDecodeError:
            pass
    return "".join(out)


def accepts(good_line: str, bad_line: str) -> str | None:
    for codec in CODECS:
        if simulate(good_line, codec) == bad_line:
            return codec
        if simulate(good_line, codec) == bad_line.lstrip(BOM):
            return codec
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("good_rev")
    ap.add_argument("bad_rev")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()

    good = blob(a.good_rev, a.file)
    bad = blob(a.bad_rev, a.file)
    with open(a.file, encoding="utf-8", newline="") as fh:
        current = fh.read()

    pairs = []
    rejected = []
    for bad_line in dict.fromkeys(bad):
        if not any(m in bad_line for m in MARKERS) and not bad_line.startswith(BOM):
            continue
        matches = difflib.get_close_matches(bad_line, good, n=1, cutoff=THRESHOLD)
        if not matches:
            rejected.append({"damaged": bad_line, "reason": "no close line in the good blob"})
            continue
        good_line = matches[0]
        codec = accepts(good_line, bad_line)
        if not codec:
            rejected.append({"damaged": bad_line, "reason": "damage not reproducible from this line",
                             "candidate": good_line})
            continue
        pairs.append({"damaged": bad_line, "restored": good_line, "codec": codec})

    changed = 0
    for pair in pairs:
        if pair["damaged"] not in current:
            pair["applied"] = 0
            continue
        count = current.count(pair["damaged"])
        current = current.replace(pair["damaged"], pair["restored"])
        pair["applied"] = count
        changed += count

    for pair in pairs:
        print(f'{pair["applied"]}x [{pair["codec"]}]\n  - {pair["damaged"]}\n  + {pair["restored"]}')
    for rej in rejected:
        print(f'REJECTED: {rej["reason"]}\n  - {rej["damaged"]}')

    print(f"\nrestored {changed} line occurrence(s) from {a.good_rev} "
          f"({len(pairs)} verified pair(s), {len(rejected)} rejected)")
    if changed and not a.dry_run:
        Path(a.file).write_text(current, encoding="utf-8", newline="")
    if a.report:
        a.report.write_text(
            json.dumps({"file": a.file, "good_rev": a.good_rev, "bad_rev": a.bad_rev,
                        "changed": changed, "pairs": pairs, "rejected": rejected},
                       indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
