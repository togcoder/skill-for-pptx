#!/usr/bin/env python3
"""Open the frozen T066 deck and the directed copy in PowerPoint 16 and read
the facts COM can prove: slide count, effect count, transition kind/duration,
and that the Morph naming convention is gone."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import win32com.client

ROOT = Path(__file__).resolve().parents[3]
BEFORE = ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx"
AFTER = ROOT / "experiments/T067-20261104-opencode-deck-director/motion/artifacts/T066-deck-directed.pptx"
OUT = ROOT / "experiments/T067-20261104-opencode-deck-director/motion/com-verify.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_deck(app, path: Path) -> dict:
    pres = app.Presentations.Open(str(path), ReadOnly=True, Untitled=False, WithWindow=False)
    try:
        slides = []
        bang_names = []
        for i in range(1, int(pres.Slides.Count) + 1):
            s = pres.Slides(i)
            names = [str(sh.Name) for sh in s.Shapes]
            bang_names.extend([n for n in names if n.startswith("!!")])
            slides.append({
                "slide": i,
                "effects": int(s.TimeLine.MainSequence.Count),
                "entry_effect": int(s.SlideShowTransition.EntryEffect),
                "transition_duration_s": round(float(s.SlideShowTransition.Duration), 4),
                "shape_count": len(names),
                "has_thread_or_dot": any(n in ("!!thread", "!!dot") for n in names),
                "has_dialectic_foot": "dialectic-foot" in names,
            })
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "slides": slides,
            "total_effects": sum(s["effects"] for s in slides),
            "morph_slides": [s["slide"] for s in slides if s["entry_effect"] == 3954],
            "fade_slides": [s["slide"] for s in slides if s["entry_effect"] == 3849],
            "bang_names": bang_names,
            "read_only": bool(pres.ReadOnly),
        }
    finally:
        pres.Close()


def main() -> int:
    app = win32com.client.DispatchEx("PowerPoint.Application")
    app.Visible = True
    try:
        result = {
            "application": str(app.Name),
            "version": str(app.Version),
            "build": str(app.Build),
            "before": read_deck(app, BEFORE),
            "after": read_deck(app, AFTER),
        }
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "before_effects": result["before"]["total_effects"],
            "after_effects": result["after"]["total_effects"],
            "before_morph": result["before"]["morph_slides"],
            "after_morph": result["after"]["morph_slides"],
            "after_fade": result["after"]["fade_slides"],
            "after_thread_dot": [s["slide"] for s in result["after"]["slides"] if s["has_thread_or_dot"]],
            "after_bang_names": result["after"]["bang_names"],
            "after_dialectic_foot": [s["slide"] for s in result["after"]["slides"] if s["has_dialectic_foot"]],
        }, ensure_ascii=False, indent=2))
        return 0
    finally:
        app.Quit()


if __name__ == "__main__":
    sys.exit(main())
