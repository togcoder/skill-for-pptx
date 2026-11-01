#!/usr/bin/env python3
"""GridCraft Native Bridge for Skill for Design (T037).

Connects to ``gridcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\GridCraft).
Provides headless spreadsheet inspection, formula evaluation, format conversion
(xlsx, csv, tsv, json, html, pdf), and range content extraction.

Usage:
    python scripts/gridcraft_bridge.py check
    python scripts/gridcraft_bridge.py eval "SUM(A1:A10)" --in sheet.xlsx
    python scripts/gridcraft_bridge.py info sheet.xlsx
    python scripts/gridcraft_bridge.py convert sheet.xlsx sheet.csv
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

DEFAULT_GRIDCRAFT_PATHS = [
    Path(r"D:\artcraft\GridCraft\gridcraft-cli.exe"),
    Path(r"C:\artcraft\GridCraft\gridcraft-cli.exe"),
]


def find_gridcraft_cli() -> Path | None:
    env_override = os.environ.get("GRIDCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_GRIDCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("gridcraft-cli") or shutil.which("gridcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_gridcraft_cli() is not None


def inspect_sheet(file_path: str | Path) -> dict[str, Any]:
    cli = find_gridcraft_cli()
    if not cli:
        raise RuntimeError("gridcraft-cli is not available on this host.")

    file_path = Path(file_path).resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"Spreadsheet not found: {file_path}")

    res = subprocess.run(
        [str(cli), "info", str(file_path), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"gridcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse gridcraft-cli info output: {exc}") from exc


def eval_formula(
    formula: str,
    in_file: str | Path | None = None,
    sheet: str | None = None,
    cell: str | None = None,
) -> Any:
    cli = find_gridcraft_cli()
    if not cli:
        raise RuntimeError("gridcraft-cli is not available on this host.")

    cmd = [str(cli), "eval", formula, "--json"]
    if in_file:
        cmd.extend(["--in", str(Path(in_file).resolve())])
    if sheet:
        cmd.extend(["--sheet", sheet])
    if cell:
        cmd.extend(["--cell", cell])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"gridcraft-cli eval failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        return res.stdout.strip()


def convert_sheet(
    in_path: str | Path,
    out_path: str | Path,
    sheet: str | None = None,
) -> Path:
    cli = find_gridcraft_cli()
    if not cli:
        raise RuntimeError("gridcraft-cli is not available on this host.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "convert", str(in_path), str(out_path)]
    if sheet:
        cmd.extend(["--sheet", sheet])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"gridcraft-cli convert failed: {res.stderr.strip()}")

    return out_path


def cat_range(
    file_path: str | Path,
    range_str: str | None = None,
    sheet: str | None = None,
    as_csv: bool = True,
) -> str:
    cli = find_gridcraft_cli()
    if not cli:
        raise RuntimeError("gridcraft-cli is not available on this host.")

    cmd = [str(cli), "cat", str(Path(file_path).resolve())]
    if range_str:
        cmd.extend(["--range", range_str])
    if sheet:
        cmd.extend(["--sheet", sheet])
    if as_csv:
        cmd.append("--csv")

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"gridcraft-cli cat failed: {res.stderr.strip()}")

    return res.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Check if gridcraft-cli is available")

    p_info = subparsers.add_parser("info", help="Inspect spreadsheet sheets, tables, ranges")
    p_info.add_argument("file", type=Path)

    p_eval = subparsers.add_parser("eval", help="Evaluate a formula")
    p_eval.add_argument("formula", type=str)
    p_eval.add_argument("--in", dest="in_file", type=Path, default=None)
    p_eval.add_argument("--sheet", type=str, default=None)

    p_conv = subparsers.add_parser("convert", help="Convert spreadsheet format")
    p_conv.add_argument("input", type=Path)
    p_conv.add_argument("output", type=Path)
    p_conv.add_argument("--sheet", type=str, default=None)

    args = parser.parse_args()

    if args.command == "check":
        cli = find_gridcraft_cli()
        if cli:
            print(f"GridCraft CLI: FOUND at {cli}")
        else:
            print("GridCraft CLI: NOT FOUND", file=sys.stderr)
            sys.exit(1)
    elif args.command == "info":
        print(json.dumps(inspect_sheet(args.file), indent=2, ensure_ascii=False))
    elif args.command == "eval":
        res = eval_formula(args.formula, in_file=args.in_file, sheet=args.sheet)
        print(json.dumps(res, indent=2, ensure_ascii=False) if isinstance(res, (dict, list)) else res)
    elif args.command == "convert":
        out = convert_sheet(args.input, args.output, sheet=args.sheet)
        print(f"Converted {args.input} -> {out}")


if __name__ == "__main__":
    main()
