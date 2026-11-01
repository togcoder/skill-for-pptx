#!/usr/bin/env python3
"""FilmCraft Native Bridge for Video Domain (T042).

Connects to ``filmcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\FilmCraft).
Provides headless video sequence inspection, timeline script execution,
frame rendering, and master video export.

Reference: domains/video/DOMAIN.md, knowledge/video_canon.json
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

DEFAULT_FILMCRAFT_PATHS = [
    Path(r"D:\artcraft\FilmCraft\filmcraft-cli.exe"),
    Path(r"C:\artcraft\FilmCraft\filmcraft-cli.exe"),
]


def find_filmcraft_cli() -> Optional[Path]:
    env_override = os.environ.get("FILMCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_FILMCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("filmcraft-cli") or shutil.which("filmcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_filmcraft_cli() is not None


def inspect_project(project_path: Optional[str | Path] = None) -> Dict[str, Any]:
    cli = find_filmcraft_cli()
    if not cli:
        raise RuntimeError("filmcraft-cli is not available on this host.")

    cmd = [str(cli)]
    if project_path:
        p = Path(project_path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"FilmCraft project not found: {p}")
        cmd.extend(["--project", str(p)])
    cmd.extend(["inspect", "--compact"])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"filmcraft-cli inspect failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse filmcraft-cli inspect output: {exc}") from exc


def render_frame(
    seconds: float,
    out_path: str | Path,
    project_path: Optional[str | Path] = None,
    scale: float = 1.0,
    allow_offline: bool = True,
) -> Path:
    cli = find_filmcraft_cli()
    if not cli:
        raise RuntimeError("filmcraft-cli is not available on this host.")

    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli)]
    if project_path:
        p = Path(project_path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Project file not found: {p}")
        cmd.extend(["--project", str(p)])
    else:
        cmd.append("--demo")

    cmd.extend([
        "render",
        "--seconds", str(seconds),
        "--out", str(out_path),
        "--scale", str(scale),
    ])
    if allow_offline:
        cmd.append("--allow-offline")

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"filmcraft-cli render frame failed: {res.stderr.strip()}")

    return out_path


def probe_media(media_path: str | Path) -> Dict[str, Any]:
    cli = find_filmcraft_cli()
    if not cli:
        raise RuntimeError("filmcraft-cli is not available on this host.")

    p = Path(media_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Media file not found: {p}")

    cmd = [str(cli), "probe", str(p)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"filmcraft-cli probe failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse filmcraft-cli probe output: {exc}") from exc


def export_video(
    out_path: str | Path,
    project_path: Optional[str | Path] = None,
    preset: Optional[str] = None,
    format_name: Optional[str] = "h264",
    allow_offline: bool = True,
) -> Path:
    cli = find_filmcraft_cli()
    if not cli:
        raise RuntimeError("filmcraft-cli is not available on this host.")

    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli)]
    if project_path:
        p = Path(project_path).resolve()
        cmd.extend(["--project", str(p)])
    else:
        cmd.append("--demo")

    cmd.extend(["export", str(out_path)])
    if preset:
        cmd.extend(["--preset", preset])
    elif format_name:
        cmd.extend(["--format", format_name])

    if allow_offline:
        cmd.append("--allow-offline")

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"filmcraft-cli export failed: {res.stderr.strip()}")

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="FilmCraft Native Bridge")
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("check", help="Check if filmcraft-cli is available")
    p_probe = sub.add_parser("probe", help="Probe media file")
    p_probe.add_argument("media", help="Path to video or audio media")

    args = parser.parse_args()
    if args.subcommand == "check":
        p = find_filmcraft_cli()
        if p:
            print(f"FilmCraft CLI found: {p}")
            return 0
        print("FilmCraft CLI NOT found.")
        return 1
    elif args.subcommand == "probe":
        data = probe_media(args.media)
        print(json.dumps(data, indent=2))
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
