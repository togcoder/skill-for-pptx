"""Artifact generator for T049 Advanced Presentation Interactivity & 1-Slide Mini-Games.

Produces:
1. one_slide_games_suite.pptx: Master 2-slide interactive game suite:
   - Slide 1: Mystery Treasure Chests Game (3 chests with reveal & reset, 100% in 1 slide).
   - Slide 2: Interactive Quiz Battle (3 choices with instant feedback & reset, 100% in 1 slide).
2. Rendered preview images (1920x1080) via DeckCraft CLI.
3. audit_one_slide_games.json: Structural audit receipt.
4. SHA256SUMS.txt: Checksums of all deliverables.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.advanced_interactivity import (
    compile_one_slide_games_suite,
    inspect_interactivity
)

EXP_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = EXP_DIR / "artifacts"
PREVIEWS_DIR = ARTIFACTS_DIR / "previews"
DECKCRAFT_CLI = Path(r"D:\artcraft\DeckCraft\deckcraft-cli.exe")


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    suite_pptx = ARTIFACTS_DIR / "one_slide_games_suite.pptx"
    print(f"[1/4] Compiling 1-slide games suite: {suite_pptx.name}...")
    res = compile_one_slide_games_suite(suite_pptx)
    if not res["ok"]:
        raise RuntimeError("Failed to compile 1-slide games suite")

    print("[2/4] Inspecting and saving interactivity audit...")
    audit = inspect_interactivity(suite_pptx)
    audit_file = ARTIFACTS_DIR / "audit_one_slide_games.json"
    audit_file.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[3/4] Rendering slide previews via DeckCraft CLI...")
    if DECKCRAFT_CLI.is_file():
        subprocess.run(
            [str(DECKCRAFT_CLI), "render", str(suite_pptx), "--all", str(PREVIEWS_DIR)],
            check=True
        )
        print("      Previews rendered successfully.")
    else:
        print(f"      DeckCraft CLI not found at {DECKCRAFT_CLI}, skipping render.")

    print("[4/4] Generating SHA256SUMS.txt...")
    lines = []
    for f in sorted(ARTIFACTS_DIR.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS.txt":
            rel = f.relative_to(ARTIFACTS_DIR)
            lines.append(f"{compute_sha256(f)}  {rel.as_posix()}")
            
    (ARTIFACTS_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Done! All artifacts generated successfully.")


if __name__ == "__main__":
    main()
