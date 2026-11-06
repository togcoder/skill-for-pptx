"""Render all 8 PPTX test pairs to high-resolution PNG images using PowerPoint COM.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Force UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import win32com.client

PAIRS_DIR = Path(__file__).resolve().parent.parent / "pairs"
PREVIEWS_DIR = PAIRS_DIR / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def render_all_decks():
    pptx_files = sorted(PAIRS_DIR.glob("*.pptx"))
    print(f"Found {len(pptx_files)} PPTX files to render...")

    app = win32com.client.Dispatch("PowerPoint.Application")
    # Don't show full window if possible, but keep accessible
    app.Visible = 1

    try:
        for pfile in pptx_files:
            abs_path = str(pfile.resolve())
            print(f"Opening: {pfile.name}")
            pres = app.Presentations.Open(abs_path, WithWindow=False)
            try:
                deck_slug = pfile.stem
                deck_preview_dir = PREVIEWS_DIR / deck_slug
                deck_preview_dir.mkdir(parents=True, exist_ok=True)

                for idx, slide in enumerate(pres.Slides, start=1):
                    out_png = deck_preview_dir / f"slide-{idx:02d}.png"
                    slide.Export(str(out_png.resolve()), "PNG", 1920, 1080)
                    print(f"  -> Exported: {deck_slug}/slide-{idx:02d}.png")
            finally:
                pres.Close()
    finally:
        app.Quit()

    print(f"\nAll renders complete in: {PREVIEWS_DIR}")


if __name__ == "__main__":
    render_all_decks()
