#!/usr/bin/env python3
"""DeckCraft native bridge for PPTX Motion Lab and Skill for Design (T035).

Provides native rendering, inspection, and verification of PowerPoint (.pptx)
and DeckCraft (.deckcraft) presentations using the ArtCraft suite's
``deckcraft-cli.exe`` headless engine.

This resolves the long-standing verification gap (Rung 5 in docs/VERIFICATION.md)
by enabling instantaneous, offline, full-HD (1920x1080) slide rendering without
requiring a full Microsoft Office COM automation setup or LibreOffice.

Usage:
    python scripts/deckcraft_bridge.py check
    python scripts/deckcraft_bridge.py render deck.pptx -o previews/
    python scripts/deckcraft_bridge.py info deck.pptx
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

DEFAULT_DECKCRAFT_PATHS = [
    Path(r"D:\artcraft\DeckCraft\deckcraft-cli.exe"),
    Path(r"C:\artcraft\DeckCraft\deckcraft-cli.exe"),
]


def find_deckcraft_cli() -> Path | None:
    """Locate the deckcraft-cli binary from env, default locations, or PATH."""
    env_override = os.environ.get("DECKCRAFT_CLI")
    if env_override:
        p = Path(env_override)
        if p.is_file() and os.access(p, os.X_OK):
            return p

    for candidate in DEFAULT_DECKCRAFT_PATHS:
        if candidate.is_file():
            return candidate

    found = shutil.which("deckcraft-cli") or shutil.which("deckcraft-cli.exe")
    if found:
        return Path(found)

    return None


def is_available() -> bool:
    """Return True if deckcraft-cli is found and executable."""
    return find_deckcraft_cli() is not None


def inspect_deck(pptx_path: str | Path) -> dict:
    """Return presentation metadata (slides, shapes, theme) via deckcraft-cli info."""
    cli = find_deckcraft_cli()
    if not cli:
        raise RuntimeError("deckcraft-cli is not available on this system.")

    pptx_path = Path(pptx_path).resolve()
    if not pptx_path.is_file():
        raise FileNotFoundError(f"Presentation not found: {pptx_path}")

    res = subprocess.run(
        [str(cli), "info", str(pptx_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"deckcraft-cli info failed: {res.stderr.strip()}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse deckcraft-cli info output: {exc}") from exc


def render_slides(
    pptx_path: str | Path,
    out_dir: str | Path,
    scale: int = 2,
    slide_index: int | None = None,
) -> list[Path]:
    """Render one or all slides of a presentation to PNG.

    Args:
        pptx_path: Path to .pptx or .deckcraft file.
        out_dir: Output folder where slide PNGs are saved.
        scale: Scale factor (default 2 -> 960x540 pt becomes 1920x1080 px).
        slide_index: 0-based slide index to render a single slide, or None for all.

    Returns:
        List of generated PNG Path objects sorted by filename.
    """
    cli = find_deckcraft_cli()
    if not cli:
        raise RuntimeError("deckcraft-cli is not available on this system.")

    pptx_path = Path(pptx_path).resolve()
    if not pptx_path.is_file():
        raise FileNotFoundError(f"Presentation not found: {pptx_path}")

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if slide_index is not None:
        target_png = out_dir / f"slide-{slide_index + 1:02d}.png"
        cmd = [
            str(cli),
            "render",
            str(pptx_path),
            "--slide",
            str(slide_index),
            "--scale",
            str(scale),
            str(target_png),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)
        if res.returncode != 0:
            raise RuntimeError(f"deckcraft-cli render failed: {res.stderr.strip()}")
        return [target_png]

    cmd = [
        str(cli),
        "render",
        str(pptx_path),
        "--all",
        "--scale",
        str(scale),
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"deckcraft-cli render failed: {res.stderr.strip()}")

    return sorted(out_dir.glob("slide-*.png"))


def convert_presentation(in_path: str | Path, out_path: str | Path) -> Path:
    """Convert a presentation between supported formats (.pptx, .deckcraft, .pdf, .md)."""
    cli = find_deckcraft_cli()
    if not cli:
        raise RuntimeError("deckcraft-cli is not available on this system.")

    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(cli), "convert", str(in_path), str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)
    if res.returncode != 0:
        raise RuntimeError(f"deckcraft-cli convert failed: {res.stderr.strip()}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    subparsers.add_parser("check", help="Check if deckcraft-cli is available and print version")

    # render
    p_render = subparsers.add_parser("render", help="Render slides to PNG")
    p_render.add_argument("pptx", type=Path, help="Input PPTX or DeckCraft file")
    p_render.add_argument("-o", "--out-dir", type=Path, default=Path("previews"), help="Output directory")
    p_render.add_argument("--scale", type=int, default=2, help="Scale factor (2 = 1920x1080)")
    p_render.add_argument("--slide", type=int, default=None, help="Specific slide index (0-based)")

    # info
    p_info = subparsers.add_parser("info", help="Inspect presentation structure")
    p_info.add_argument("pptx", type=Path, help="Input PPTX or DeckCraft file")

    args = parser.parse_args()

    if args.command == "check":
        cli = find_deckcraft_cli()
        if cli:
            res = subprocess.run([str(cli), "--version"], capture_output=True, text=True)
            ver = res.stdout.strip() or res.stderr.strip()
            print(f"DeckCraft CLI: FOUND at {cli}")
            print(f"Version: {ver}")
            sys.exit(0)
        else:
            print("DeckCraft CLI: NOT FOUND")
            sys.exit(1)

    elif args.command == "render":
        images = render_slides(args.pptx, args.out_dir, scale=args.scale, slide_index=args.slide)
        print(f"Rendered {len(images)} slide(s) to {args.out_dir}:")
        for img in images:
            print(f"  - {img.name} ({img.stat().st_size:,} bytes)")

    elif args.command == "info":
        info = inspect_deck(args.pptx)
        print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
