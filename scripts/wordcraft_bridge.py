#!/usr/bin/env python3
"""WordCraft Native Bridge for Skill for Design (T037).

Connects to ``wordcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\WordCraft).
Provides headless document inspection, page rendering to PNG, format conversion
(docx, pdf, rtf, html, md, txt, xml), and text extraction.

Usage:
    python scripts/wordcraft_bridge.py check
    python scripts/wordcraft_bridge.py info doc.docx
    python scripts/wordcraft_bridge.py render doc.docx -o page-01.png --page 1
    python scripts/wordcraft_bridge.py convert doc.md doc.docx
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

DEFAULT_WORDCRAFT_PATHS = [
    Path(r"D:\artcraft\WordCraft\wordcraft-cli.exe"),
    Path(r"C:\artcraft\WordCraft\wordcraft-cli.exe"),
]


def find_wordcraft_cli() -> Path | None:
    env_override = os.environ.get("WORDCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_WORDCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("wordcraft-cli") or shutil.which("wordcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_wordcraft_cli() is not None


def inspect_document(doc_path: str | Path) -> dict[str, Any]:
    cli = find_wordcraft_cli()
    if not cli:
        raise RuntimeError("wordcraft-cli is not available on this host.")

    doc_path = Path(doc_path).resolve()
    if not doc_path.is_file():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    res = subprocess.run(
        [str(cli), "info", str(doc_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"wordcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse wordcraft-cli info output: {exc}") from exc


def render_page(
    doc_path: str | Path,
    out_png: str | Path,
    page: int = 1,
    scale: int = 2,
) -> Path:
    cli = find_wordcraft_cli()
    if not cli:
        raise RuntimeError("wordcraft-cli is not available on this host.")

    doc_path = Path(doc_path).resolve()
    if not doc_path.is_file():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(cli),
        "render",
        str(doc_path),
        str(out_png),
        "--page",
        str(page),
        "--scale",
        str(scale),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"wordcraft-cli render failed: {res.stderr.strip()}")

    return out_png


def convert_document(
    in_path: str | Path,
    out_path: str | Path,
    format_arg: str | None = None,
) -> Path:
    cli = find_wordcraft_cli()
    if not cli:
        raise RuntimeError("wordcraft-cli is not available on this host.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "convert", str(in_path), str(out_path)]
    if format_arg:
        cmd.extend(["--format", format_arg])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"wordcraft-cli convert failed: {res.stderr.strip()}")

    return out_path


def extract_text(doc_path: str | Path) -> str:
    cli = find_wordcraft_cli()
    if not cli:
        raise RuntimeError("wordcraft-cli is not available on this host.")

    doc_path = Path(doc_path).resolve()
    if not doc_path.is_file():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    res = subprocess.run(
        [str(cli), "text", str(doc_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"wordcraft-cli text failed: {res.stderr.strip()}")

    return res.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Check if wordcraft-cli is available")

    p_info = subparsers.add_parser("info", help="Document properties as JSON")
    p_info.add_argument("doc", type=Path)

    p_render = subparsers.add_parser("render", help="Render a page as PNG")
    p_render.add_argument("doc", type=Path)
    p_render.add_argument("-o", "--output", type=Path, default=Path("page-01.png"))
    p_render.add_argument("--page", type=int, default=1)
    p_render.add_argument("--scale", type=int, default=2)

    p_conv = subparsers.add_parser("convert", help="Convert document format")
    p_conv.add_argument("input", type=Path)
    p_conv.add_argument("output", type=Path)
    p_conv.add_argument("--format", dest="fmt", type=str, default=None)

    args = parser.parse_args()

    if args.command == "check":
        cli = find_wordcraft_cli()
        if cli:
            print(f"WordCraft CLI: FOUND at {cli}")
        else:
            print("WordCraft CLI: NOT FOUND", file=sys.stderr)
            sys.exit(1)
    elif args.command == "info":
        print(json.dumps(inspect_document(args.doc), indent=2, ensure_ascii=False))
    elif args.command == "render":
        out = render_page(args.doc, args.output, page=args.page, scale=args.scale)
        print(f"Rendered page {args.page} to {out}")
    elif args.command == "convert":
        out = convert_document(args.input, args.output, format_arg=args.fmt)
        print(f"Converted {args.input} -> {out}")


if __name__ == "__main__":
    main()
