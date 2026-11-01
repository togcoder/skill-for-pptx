#!/usr/bin/env python3
"""Compatibility entry point for the DOCX structural audit (T039, docx).

Status: EXPERIMENTAL — T039 [docx], review requested.

The implementation lives in ``word_field_kit.audit_docx`` so the generator and
the standalone auditor cannot drift apart.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

try:
    from .word_field_kit import audit_docx
except ImportError:
    from word_field_kit import audit_docx

try:
    from .docx_profiles import get_profile
except ImportError:
    from docx_profiles import get_profile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SYSTEM_PATH = ROOT / "domains" / "docx" / "data" / "document_system.json"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--md", type=Path, default=None)
    parser.add_argument("--profile", default=None,
                        help="Named profile; relaxes the generic 20 mm margin floor")
    parser.add_argument("--profiles", type=Path, default=None)
    args = parser.parse_args()
    system = None
    if args.profile:
        profile = get_profile(args.profile, args.profiles)
        system = json.loads(DEFAULT_SYSTEM_PATH.read_text(encoding="utf-8"))
        margins = (profile.get("page") or {}).get("margins_mm") or {}
        if margins:
            system.setdefault("page", {})["margin_min_mm"] = max(
                5.0, min(float(v) for v in margins.values()) - 0.6)
    report = audit_docx(args.docx, system=system)
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
