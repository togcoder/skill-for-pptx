#!/usr/bin/env python3
"""Compatibility entry point for the DOCX structural audit (T039, docx).

Status: EXPERIMENTAL — T039 [docx], review requested.

The implementation lives in ``word_field_kit.audit_docx`` so the generator and
the standalone auditor cannot drift apart.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from .word_field_kit import audit_docx
except ImportError:
    from word_field_kit import audit_docx


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--md", type=Path, default=None)
    args = parser.parse_args()
    report = audit_docx(args.docx)
    print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    if args.md:
        lines = ["# DOCX audit", "", f"**ok:** {report.ok}", ""]
        for label, items in [("Errors", report.errors), ("Warnings", report.warnings), ("Notes", report.notes)]:
            lines.append(f"## {label}")
            lines.extend(f"- {x}" for x in items) if items else lines.append("- none")
            lines.append("")
        args.md.write_text("\n".join(lines), encoding="utf-8")
    raise SystemExit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
