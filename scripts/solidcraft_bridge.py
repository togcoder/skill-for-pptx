#!/usr/bin/env python3
"""SolidCraft Native Bridge for 3D Solid & CAD Modeling (T042).

Connects to ``solidcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\SolidCraft).
Provides headless 3D CAD modeling script execution, physical evaluation,
orthographic/isometric snapshots, and high-fidelity rendering.

Reference: domains/3d/DOMAIN.md, knowledge/3d_solid_canon.json
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

DEFAULT_SOLIDCRAFT_PATHS = [
    Path(r"D:\artcraft\SolidCraft\solidcraft-cli.exe"),
    Path(r"C:\artcraft\SolidCraft\solidcraft-cli.exe"),
]


def find_solidcraft_cli() -> Optional[Path]:
    env_override = os.environ.get("SOLIDCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_SOLIDCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("solidcraft-cli") or shutil.which("solidcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_solidcraft_cli() is not None


def export_icon(out_png: str | Path, size: int = 256) -> Path:
    cli = find_solidcraft_cli()
    if not cli:
        raise RuntimeError("solidcraft-cli is not available on this host.")

    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "icon", "--out", str(out_png), "--size", str(size)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"solidcraft-cli icon failed: {res.stderr.strip()}")

    return out_png


def take_snapshot(
    input_model: str | Path,
    out_png: str | Path,
    view: str = "iso",
    width: int = 1920,
    height: int = 1080,
    no_grid: bool = False,
    no_axes: bool = False,
) -> Path:
    cli = find_solidcraft_cli()
    if not cli:
        raise RuntimeError("solidcraft-cli is not available on this host.")

    input_model = Path(input_model).resolve()
    if not input_model.is_file():
        raise FileNotFoundError(f"Input model/script not found: {input_model}")

    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(cli), "snapshot", str(input_model),
        "--out", str(out_png),
        "--view", view,
        "--width", str(width),
        "--height", str(height),
    ]
    if no_grid:
        cmd.append("--no-grid")
    if no_axes:
        cmd.append("--no-axes")

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"solidcraft-cli snapshot failed: {res.stderr.strip()}")

    return out_png


def eval_model(model_or_script: str | Path) -> Dict[str, Any]:
    cli = find_solidcraft_cli()
    if not cli:
        raise RuntimeError("solidcraft-cli is not available on this host.")

    p = Path(model_or_script).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    cmd = [str(cli), "eval", str(p)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"solidcraft-cli eval failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse solidcraft eval output: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="SolidCraft Native Bridge")
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("check", help="Check if solidcraft-cli is available")
    p_icon = sub.add_parser("icon", help="Generate SolidCraft icon")
    p_icon.add_argument("out", help="Output PNG path")
    p_icon.add_argument("--size", type=int, default=256, help="Icon size")

    args = parser.parse_args()
    if args.subcommand == "check":
        p = find_solidcraft_cli()
        if p:
            print(f"SolidCraft CLI found: {p}")
            return 0
        print("SolidCraft CLI NOT found.")
        return 1
    elif args.subcommand == "icon":
        out = export_icon(args.out, args.size)
        print(f"Wrote icon to {out}")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
