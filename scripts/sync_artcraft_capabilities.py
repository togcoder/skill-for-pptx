#!/usr/bin/env python3
"""Sync ArtCraft Capabilities Registry (T036).

Discovers all available tools in D:\\artcraft (DeckCraft, WordCraft, GridCraft,
VectorCraft, DesignCraft, FigCraft, PhotoCraft, LightCraft, FilmCraft, SoundCraft,
PdfCraft, CADCraft, SolidCraft), parses their CLI capabilities, subcommands,
and MCP server support, and writes a machine-readable capability manifest to
``lab/registry/artcraft_capabilities.json``.

This acts as the Pre-flight Capability Gate to prevent AI agents from
reinventing the wheel with custom scripts when native commands already exist.

Usage:
    python scripts/sync_artcraft_capabilities.py
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

DEFAULT_ARTCRAFT_ROOTS = [
    Path(r"D:\artcraft"),
    Path(r"C:\artcraft"),
]

DOMAIN_MAP = {
    "deckcraft": "presentations",
    "wordcraft": "documents",
    "gridcraft": "spreadsheets",
    "vectorcraft": "vector_graphics",
    "designcraft": "desktop_publishing",
    "figcraft": "ui_prototyping",
    "photocraft": "raster_editing",
    "lightcraft": "raw_photo_library",
    "filmcraft": "video_motion",
    "soundcraft": "audio_production",
    "pdfcraft": "pdf_processing",
    "cadcraft": "cad_2d",
    "solidcraft": "solid_modeling_3d",
}


def find_artcraft_root() -> Path | None:
    env_root = os.environ.get("ARTCRAFT_ROOT")
    if env_root and Path(env_root).is_dir():
        return Path(env_root)

    for root in DEFAULT_ARTCRAFT_ROOTS:
        if root.is_dir():
            return root
    return None


def parse_cli_help(cli_path: Path) -> dict:
    """Run CLI with --help and extract subcommands and summary."""
    try:
        res = subprocess.run(
            [str(cli_path), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        text = res.stdout or res.stderr
    except Exception as exc:
        text = f"Error running --help: {exc}"

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    summary = lines[0] if lines else ""

    subcommands: list[str] = []
    # Common patterns for subcommands in ArtCraft CLIs
    for line in lines:
        m = re.match(r"^\s*([a-zA-Z0-9_\-]+)\s{2,}(.+)$", line)
        if m:
            cmd_name = m.group(1).lower()
            if cmd_name not in ("usage:", "options:", "commands:", "flags:"):
                subcommands.append(cmd_name)
        elif line.startswith(f"{cli_path.stem} "):
            parts = line.split()
            if len(parts) >= 2 and not parts[1].startswith(("-", "<", "[")):
                subcommands.append(parts[1].lower())

    subcommands = sorted(set(subcommands))
    has_mcp = "mcp" in subcommands or " mcp" in text.lower()
    has_run = "run" in subcommands or " run" in text.lower()
    has_render = "render" in subcommands or " render" in text.lower()

    return {
        "summary": summary,
        "subcommands": subcommands,
        "has_mcp": has_mcp,
        "has_run": has_run,
        "has_render": has_render,
    }


def sync_capabilities(artcraft_root: Path | None = None) -> dict:
    if artcraft_root is None:
        artcraft_root = find_artcraft_root()

    if not artcraft_root:
        raise FileNotFoundError("Could not find ArtCraft directory on this host.")

    tools = {}
    hasher = hashlib.sha256()

    for folder in sorted(artcraft_root.iterdir()):
        if not folder.is_dir():
            continue

        tool_id = folder.name.lower()
        clis = list(folder.glob("*-cli.exe"))
        guis = list(folder.glob("*.exe"))
        # filter out CLI from GUI
        guis = [g for g in guis if not g.name.endswith("-cli.exe")]

        if not clis:
            continue

        primary_cli = clis[0]
        stat = primary_cli.stat()
        hasher.update(f"{primary_cli.name}:{stat.st_size}:{stat.st_mtime}".encode("utf-8"))

        parsed = parse_cli_help(primary_cli)
        tools[tool_id] = {
            "name": folder.name,
            "domain": DOMAIN_MAP.get(tool_id, "unknown"),
            "cli_path": str(primary_cli),
            "cli_name": primary_cli.name,
            "cli_size_bytes": stat.st_size,
            "gui_path": str(guis[0]) if guis else None,
            "has_mcp": parsed["has_mcp"],
            "has_run": parsed["has_run"],
            "has_render": parsed["has_render"],
            "subcommands": parsed["subcommands"],
            "summary": parsed["summary"],
        }

    manifest = {
        "version": "1.0.0",
        "artcraft_root": str(artcraft_root),
        "version_hash": hasher.hexdigest()[:16],
        "tool_count": len(tools),
        "tools": tools,
    }

    return manifest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry_dir = repo_root / "lab" / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)

    out_file = registry_dir / "artcraft_capabilities.json"
    backlog_file = registry_dir / "capability_gaps_backlog.md"

    try:
        manifest = sync_capabilities()
        out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Synced {manifest['tool_count']} ArtCraft tools into {out_file.relative_to(repo_root)}")
        print(f"Manifest Version Hash: {manifest['version_hash']}")

        if not backlog_file.is_file():
            backlog_content = (
                "# Capability Gaps Backlog\n\n"
                "Log of requested features and gaps where AI agents required custom fallbacks\n"
                "because an ArtCraft native CLI or MCP capability was absent or incomplete.\n\n"
                "| ID | Tool | Requested Capability | Fallback Used | Reported By | Status |\n"
                "|---|---|---|---|---|---|\n"
            )
            backlog_file.write_text(backlog_content, encoding="utf-8")
            print(f"Initialized {backlog_file.relative_to(repo_root)}")

    except Exception as exc:
        print(f"Error syncing ArtCraft capabilities: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
