#!/usr/bin/env python3
"""VectorCraft Native Bridge for Skill for Design (T037).

Connects to ``vectorcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\VectorCraft).
Provides headless vector illustration inspection, format conversion (svg, ai, pdf, png, psd),
artboard extraction, and batch execution.

Usage:
    python scripts/vectorcraft_bridge.py check
    python scripts/vectorcraft_bridge.py info logo.svg
    python scripts/vectorcraft_bridge.py convert logo.svg logo.png --scale 2
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

DEFAULT_VECTORCRAFT_PATHS = [
    Path(r"D:\artcraft\VectorCraft\vectorcraft-cli.exe"),
    Path(r"C:\artcraft\VectorCraft\vectorcraft-cli.exe"),
]


def find_vectorcraft_cli() -> Path | None:
    env_override = os.environ.get("VECTORCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_VECTORCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("vectorcraft-cli") or shutil.which("vectorcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_vectorcraft_cli() is not None


def inspect_vector(file_path: str | Path) -> dict[str, Any]:
    cli = find_vectorcraft_cli()
    if not cli:
        raise RuntimeError("vectorcraft-cli is not available on this host.")

    file_path = Path(file_path).resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"Vector file not found: {file_path}")

    res = subprocess.run(
        [str(cli), "info", str(file_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"vectorcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse vectorcraft-cli info output: {exc}") from exc


def convert_vector(
    in_path: str | Path,
    out_path: str | Path,
    scale: int = 1,
    artboard: int | None = None,
) -> Path:
    cli = find_vectorcraft_cli()
    if not cli:
        raise RuntimeError("vectorcraft-cli is not available on this host.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "convert", str(in_path), str(out_path), "--scale", str(scale)]
    if artboard is not None:
        cmd.extend(["--artboard", str(artboard)])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"vectorcraft-cli convert failed: {res.stderr.strip()}")

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Check if vectorcraft-cli is available")

    p_info = subparsers.add_parser("info", help="Inspect vector document properties")
    p_info.add_argument("file", type=Path)

    p_conv = subparsers.add_parser("convert", help="Convert vector format")
    p_conv.add_argument("input", type=Path)
    p_conv.add_argument("output", type=Path)
    p_conv.add_argument("--scale", type=int, default=1)
    p_conv.add_argument("--artboard", type=int, default=None)

    args = parser.parse_args()

    if args.command == "check":
        cli = find_vectorcraft_cli()
        if cli:
            print(f"VectorCraft CLI: FOUND at {cli}")
        else:
            print("VectorCraft CLI: NOT FOUND", file=sys.stderr)
            sys.exit(1)
    elif args.command == "info":
        print(json.dumps(inspect_vector(args.file), indent=2, ensure_ascii=False))
    elif args.command == "convert":
        out = convert_vector(args.input, args.output, scale=args.scale, artboard=args.artboard)
        print(f"Converted {args.input} -> {out}")


if __name__ == "__main__":
    main()
