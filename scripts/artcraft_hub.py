#!/usr/bin/env python3
"""Universal ArtCraft Hub (T036).

Provides a single unified Python gateway to discover, query, and run any of the
13 ArtCraft tools (DeckCraft, WordCraft, GridCraft, VectorCraft, DesignCraft,
FigCraft, PhotoCraft, LightCraft, FilmCraft, SoundCraft, PdfCraft, CADCraft, SolidCraft).

Enforces the Pre-flight Capability Gate: verifies whether a tool or subcommand
exists before allowing agents to execute actions.

Usage:
    python scripts/artcraft_hub.py list
    python scripts/artcraft_hub.py info wordcraft
    python scripts/artcraft_hub.py run deckcraft --help
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.sync_artcraft_capabilities import sync_capabilities, find_artcraft_root
except ImportError:
    from sync_artcraft_capabilities import sync_capabilities, find_artcraft_root


def get_capabilities_file() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "registry" / "artcraft_capabilities.json"


def load_capabilities(refresh_if_missing: bool = True) -> dict[str, Any]:
    cap_file = get_capabilities_file()
    if not cap_file.is_file() and refresh_if_missing:
        manifest = sync_capabilities()
        cap_file.parent.mkdir(parents=True, exist_ok=True)
        cap_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return manifest

    if not cap_file.is_file():
        raise FileNotFoundError(f"Capabilities file not found: {cap_file}")

    return json.loads(cap_file.read_text(encoding="utf-8"))


def list_tools() -> list[dict[str, Any]]:
    caps = load_capabilities()
    return list(caps.get("tools", {}).values())


def get_tool(tool_name: str) -> dict[str, Any] | None:
    caps = load_capabilities()
    tool_key = tool_name.lower().replace("-cli", "")
    return caps.get("tools", {}).get(tool_key)


def is_tool_available(tool_name: str) -> bool:
    tool = get_tool(tool_name)
    if not tool:
        return False
    cli_path = Path(tool.get("cli_path", ""))
    return cli_path.is_file()


def run_tool(tool_name: str, args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    tool = get_tool(tool_name)
    if not tool:
        raise ValueError(f"Unknown ArtCraft tool: {tool_name}")

    cli_path = Path(tool["cli_path"])
    if not cli_path.is_file():
        raise FileNotFoundError(f"CLI executable not found for {tool_name} at {cli_path}")

    cmd = [str(cli_path)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all detected ArtCraft tools")

    # info
    p_info = subparsers.add_parser("info", help="Get capability info for a specific tool")
    p_info.add_argument("tool", type=str, help="Tool name (e.g. wordcraft, gridcraft)")

    # run
    p_run = subparsers.add_parser("run", help="Run a command on a tool's CLI")
    p_run.add_argument("tool", type=str, help="Tool name")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to the CLI")

    # sync
    subparsers.add_parser("sync", help="Force resync capabilities from disk")

    args = parser.parse_args()

    if args.command == "list":
        tools = list_tools()
        print(f"Detected {len(tools)} ArtCraft tools:")
        for t in tools:
            mcp_tag = "[MCP]" if t["has_mcp"] else "     "
            run_tag = "[RUN]" if t["has_run"] else "     "
            print(f"  {mcp_tag} {run_tag} {t['name']:<12} -> {t['domain']:<20} ({t['cli_name']})")

    elif args.command == "info":
        tool = get_tool(args.tool)
        if not tool:
            print(f"Tool '{args.tool}' not found.", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(tool, indent=2, ensure_ascii=False))

    elif args.command == "run":
        res = run_tool(args.tool, args.args)
        if res.stdout:
            sys.stdout.write(res.stdout)
        if res.stderr:
            sys.stderr.write(res.stderr)
        sys.exit(res.returncode)

    elif args.command == "sync":
        sync_capabilities()
        print("Capabilities synced.")


if __name__ == "__main__":
    main()
