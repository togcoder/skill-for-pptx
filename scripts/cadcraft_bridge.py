#!/usr/bin/env python3
"""CADCraft Native Bridge for Technical CAD Domain (T042).

Connects to ``cadcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\CADCraft).
Provides headless 2D/3D CAD drawing generation, format conversion (dxf, dwg, svg, png, pdf),
and ISO standard verification.

Reference: domains/cad/DOMAIN.md, knowledge/cad_iso_canon.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

DEFAULT_CADCRAFT_PATHS = [
    Path(r"D:\artcraft\CADCraft\cadcraft-cli.exe"),
    Path(r"C:\artcraft\CADCraft\cadcraft-cli.exe"),
]


def find_cadcraft_cli() -> Optional[Path]:
    env_override = os.environ.get("CADCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_CADCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("cadcraft-cli") or shutil.which("cadcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_cadcraft_cli() is not None


def inspect_drawing(drawing_path: str | Path) -> Dict[str, Any]:
    cli = find_cadcraft_cli()
    if not cli:
        raise RuntimeError("cadcraft-cli is not available on this host.")

    p = Path(drawing_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Drawing file not found: {p}")

    cmd = [str(cli), "info", str(p)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"cadcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse cadcraft-cli info output: {exc}") from exc


def generate_sample(sample_type: str = "bracket", out_path: str | Path = "bracket.svg") -> Path:
    """Generate built-in CADCraft sample drawing (bracket or floorplan)."""
    cli = find_cadcraft_cli()
    if not cli:
        raise RuntimeError("cadcraft-cli is not available on this host.")

    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "sample", sample_type, str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"cadcraft-cli sample failed: {res.stderr.strip()}")

    return out_path


def convert_drawing(in_path: str | Path, out_path: str | Path) -> Path:
    cli = find_cadcraft_cli()
    if not cli:
        raise RuntimeError("cadcraft-cli is not available on this host.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.is_file():
        raise FileNotFoundError(f"Input drawing not found: {in_path}")

    cmd = [str(cli), "convert", str(in_path), str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"cadcraft-cli convert failed: {res.stderr.strip()}")

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="CADCraft Native Bridge")
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("check", help="Check if cadcraft-cli is available")
    p_samp = sub.add_parser("sample", help="Generate sample drawing")
    p_samp.add_argument("type", choices=["bracket", "floorplan"], default="bracket", nargs="?")
    p_samp.add_argument("out", help="Output file (extension picks format: dxf, svg, png, pdf)")

    args = parser.parse_args()
    if args.subcommand == "check":
        p = find_cadcraft_cli()
        if p:
            print(f"CADCraft CLI found: {p}")
            return 0
        print("CADCraft CLI NOT found.")
        return 1
    elif args.subcommand == "sample":
        out = generate_sample(args.type, args.out)
        print(f"Generated sample to {out}")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
