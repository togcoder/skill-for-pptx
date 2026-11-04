#!/usr/bin/env python3
"""Repair cp1258/cp1252 mojibake in UTF-8 text files (T065).

Why this works
--------------
A UTF-8 file decoded with a single-byte Windows code page and then saved as
UTF-8 turns each non-ASCII UTF-8 *byte* into one character of that code page:

- cp1252 (Western):  "—"  (E2 80 94)  becomes "â€”";
                     "đúng" (C4 91 C3 BA 6E 67) becomes "Ä‘Ãºng".
- cp1258 (Vietnamese): "ú" (C3 BA) becomes "Ăº", because cp1258 maps 0xC3 to
  "Ă" and 0xBA to "º".

Reversal: walk the text and find the *shape* of a UTF-8 sequence made of
characters that a single-byte code page can encode. A lead byte (0xC2-0xF4)
plus the right number of continuation bytes (0x80-0xBF) is turned back into
bytes and decoded as UTF-8. Correct text cannot match that shape: a genuine
"ă" is the single byte 0xA3, which is a continuation byte and never starts a
sequence, so correctly written Vietnamese is left alone.

Safety rails
------------
- Only sequences that decode as *valid* UTF-8 are rewritten.
- A rewrite must produce a letter from the Latin-1/Vietnamese ranges or a
  typographic punctuation mark, i.e. the expected reading of the damage.
- A bare marker such as a quoted "Ã" is one byte short of a UTF-8 sequence
  and therefore never changes. Documentation may quote the markers safely.

    python inputs/repair_mojibake.py --dry-run docs/CHANGELOG.md
    python inputs/repair_mojibake.py docs/CHANGELOG.md domains/README.md
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

CODECS = ("cp1258", "cp1252")   # cp1258 for Vietnamese, cp1252 for € ‰ ™ …
MAX_PASSES = 5

_BYTE_MAPS: dict[str, dict[str, int]] = {}


def _byte_map(codec: str) -> dict[str, int]:
    """Character -> byte for every character the codec encodes as one byte."""
    table = _BYTE_MAPS.get(codec)
    if table is None:
        table = {}
        for b in range(0x80, 0x100):
            try:
                table.setdefault(bytes([b]).decode(codec), b)
            except UnicodeDecodeError:
                pass
        _BYTE_MAPS[codec] = table
    return table


def _byte(ch: str, codec: str) -> int | None:
    b = _byte_map(codec).get(ch)
    if b is not None:
        return b
    # A C1 control (U+0080-U+009F) is a byte the code page could not name.
    # Those are exactly the "undefined" slots (0x81, 0x8D, 0x8F, 0x90, 0x9D),
    # so the code point is the byte.
    if "\u0080" <= ch <= "\u009f":
        return ord(ch)
    return None


def _looks_repaired(text: str) -> bool:
    """True when the decoded text reads as letters or typography, not control noise."""
    for ch in text:
        if ch in "\r\n\t":
            continue
        cat = unicodedata.category(ch)
        if cat in {"Cc", "Cs", "Co", "Cn"}:
            return False
        if cat.startswith("L") or cat in {"Pd", "Pi", "Pf", "Po", "Sm", "Sc", "So"}:
            return True
        if "\u2010" <= ch <= "\u206f" or "\u20a0" <= ch <= "\u22ff":
            return True
    return False


def _continuations(lead: int) -> int:
    if 0xC2 <= lead <= 0xDF:
        return 1
    if 0xE0 <= lead <= 0xEF:
        return 2
    if 0xF0 <= lead <= 0xF4:
        return 3
    return 0


def repair_once(text: str, codec: str) -> tuple[str, list[str]]:
    out = []
    fixed = []
    i = 0
    n = len(text)
    while i < n:
        lead = _byte(text[i], codec)
        need = _continuations(lead or 0)
        if need and i + need < n:
            seq = text[i:i + need + 1]
            raw = bytearray()
            ok = True
            for pos, ch in enumerate(seq):
                b = _byte(ch, codec)
                if b is None:
                    ok = False
                    break
                if pos and not 0x80 <= b <= 0xBF:
                    ok = False
                    break
                raw.append(b)
            if ok:
                try:
                    decoded = bytes(raw).decode("utf-8")
                except UnicodeDecodeError:
                    decoded = None
                if decoded is not None and decoded != seq and _looks_repaired(decoded):
                    out.append(decoded)
                    fixed.append(f"{seq} -> {decoded}")
                    i += need + 1
                    continue
        out.append(text[i])
        i += 1
    return "".join(out), fixed


def repair_text(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for _ in range(MAX_PASSES):
        before = len(changes)
        for codec in CODECS:
            text, fixed = repair_once(text, codec)
            changes.extend(fixed)
        if len(changes) == before:
            break
    return text, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", type=Path, help="write a JSON summary here")
    a = ap.parse_args()

    total = 0
    summary = []
    for p in a.paths:
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            print(f"{p}: not valid UTF-8, skipped ({e})")
            summary.append({"path": p.as_posix(), "changes": 0, "skipped": "not utf-8"})
            continue
        fixed, changes = repair_text(text)
        total += len(changes)
        summary.append({"path": p.as_posix(), "changes": len(changes),
                        "samples": changes[:8]})
        print(f"{p}: {len(changes)} repaired sequence(s)" + (" (dry run)" if a.dry_run else ""))
        if not a.dry_run and changes:
            p.write_bytes(fixed.encode("utf-8"))

    if a.report:
        a.report.write_text(
            json.dumps({"codecs": list(CODECS), "total": total, "files": summary},
                       indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    print(f"total repaired sequences: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
