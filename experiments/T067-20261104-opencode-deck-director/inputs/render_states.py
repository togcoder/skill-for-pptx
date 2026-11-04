#!/usr/bin/env python3
"""Render stable click states of the variant decks with PowerPoint COM.

PowerPoint's object model has no "export the slideshow at click N" call. The
state is therefore reconstructed from the deck's own timing tree
(``simulate_states``: a shape is hidden until its first visibility=visible
effect), written to a temporary PPTX, and exported by PowerPoint itself. The
pixels are PowerPoint's; the *ordering* comes from the timing model. This is a
state render, not a slideshow playback claim.

Run:  python experiments/T067-.../inputs/render_states.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import pptx_animator as anim  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
TMP = ROOT / "workspace" / "T067-states"
OUT = EXP / "preview" / "states"

JOBS = [
    (ROOT / "experiments" / "T066-20261104-opencode-triet-hoc-ch1" / "artifacts"
     / "T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx", "t066",
     [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 7),
      (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5)]),
    (EXP / "artifacts" / "T067-variant-A-cover-flow.pptx", "A",
     [(1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)]),
    (EXP / "artifacts" / "T067-variant-B-cover-flow.pptx", "B",
     [(1, 0), (1, 1), (1, 2), (1, 3),
      (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5)]),
]


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for deck_path, prefix, spec in JOBS:
        for slide_no, click in spec:
            prs = Presentation(str(deck_path))
            slide = prs.slides[slide_no - 1]
            states, _ = anim.simulate_states(slide._element)
            if click >= len(states):
                raise SystemExit(f"{prefix} slide {slide_no}: click {click} "
                                 f">= states {len(states)}")
            anim.apply_state_for_preview(slide._element, states[click])
            tmp = TMP / f"{prefix}-s{slide_no}-c{click}.pptx"
            prs.save(str(tmp))
            manifest.append({
                "pptx": str(tmp), "slide": slide_no,
                "out": str(OUT / f"{prefix}-s{slide_no}-c{click}.png"),
            })
    spec_path = TMP / "manifest.json"
    spec_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ps = HERE / "export_manifest.ps1"
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps),
                    "-Manifest", str(spec_path)], check=True)
    print("states", len(manifest), "->", OUT)


if __name__ == "__main__":
    main()
