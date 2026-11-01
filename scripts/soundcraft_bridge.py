#!/usr/bin/env python3
"""SoundCraft Native Bridge for Audio Mastering Domain (T042).

Connects to ``soundcraft-cli.exe`` from the ArtCraft suite (D:\\artcraft\\SoundCraft).
Provides headless audio format inspection, resampling, bit-depth conversion,
normalization, and engine scripting.

Reference: knowledge/sound_canon.json, domains/video/DOMAIN.md
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

DEFAULT_SOUNDCRAFT_PATHS = [
    Path(r"D:\artcraft\SoundCraft\soundcraft-cli.exe"),
    Path(r"C:\artcraft\SoundCraft\soundcraft-cli.exe"),
]


def find_soundcraft_cli() -> Optional[Path]:
    env_override = os.environ.get("SOUNDCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    for candidate in DEFAULT_SOUNDCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("soundcraft-cli") or shutil.which("soundcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    return find_soundcraft_cli() is not None


def inspect_audio(audio_path: str | Path) -> Dict[str, Any]:
    cli = find_soundcraft_cli()
    if not cli:
        raise RuntimeError("soundcraft-cli is not available on this host.")

    p = Path(audio_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Audio file not found: {p}")

    cmd = [str(cli), "info", str(p)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"soundcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse soundcraft-cli info output: {exc}") from exc


def convert_audio(
    in_path: str | Path,
    out_path: str | Path,
    normalize: bool = False,
    sample_rate: Optional[int] = None,
    bit_depth: Optional[int] = None,
) -> Path:
    cli = find_soundcraft_cli()
    if not cli:
        raise RuntimeError("soundcraft-cli is not available on this host.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "convert", str(in_path), str(out_path)]
    if normalize:
        cmd.append("--normalize")
    if sample_rate:
        cmd.extend(["--rate", str(sample_rate)])
    if bit_depth:
        cmd.extend(["--bits", str(bit_depth)])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"soundcraft-cli convert failed: {res.stderr.strip()}")

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="SoundCraft Native Bridge")
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("check", help="Check if soundcraft-cli is available")
    p_info = sub.add_parser("info", help="Inspect audio file")
    p_info.add_argument("file", help="Path to audio file")

    args = parser.parse_args()
    if args.subcommand == "check":
        p = find_soundcraft_cli()
        if p:
            print(f"SoundCraft CLI found: {p}")
            return 0
        print("SoundCraft CLI NOT found.")
        return 1
    elif args.subcommand == "info":
        data = inspect_audio(args.file)
        print(json.dumps(data, indent=2))
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
