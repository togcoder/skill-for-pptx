"""T074: finalise verdicts, copy evidence frames, write the rule proposal."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/T074-20261105-opencode-morph-rules"
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
FRAMES = ROOT / "workspace/T074/frames2"

# Measured in artifacts/matrix.json, plus the two cases the colour tracker
# cannot see: different picture media changes the colour; an off-slide
# destination has no colour in the B frame.
OVERRIDES = {
    "picture-diff": {
        "verdict": "not-measured",
        "note": "different media colour; frame pairing not colour-tracked",
    },
    "offslide": {
        "verdict": "offscreen",
        "note": "B object at x=14.5 in; frame at 106 s shows an empty stage",
    },
    "zorder": {
        "verdict": "continuous-occluded",
        "note": "one blob, 11 px visible; foreground covers most of the object",
    },
}

RULES = [
    {"id": "M-01", "rule": "Same shape type + similar geometry pairs even when the names differ.",
     "evidence": ["diff-name", "same-name"], "rung": 5,
     "meaning": "PowerPoint's default byObject match is not name-only; `!!` is a hint, not a requirement, for simple shapes."},
    {"id": "M-02", "rule": "`!!` cannot force a pair across shape types.",
     "evidence": ["rect-ellipse"], "rung": 5,
     "meaning": "rect→ellipse with the same `!!track` shows two blobs in the middle: a cross-fade, not one object."},
    {"id": "M-03", "rule": "Text boxes pair as shapes; different text does not break geometry.",
     "evidence": ["text-same", "text-diff"], "rung": 5,
     "meaning": "Both moved continuously; the text content itself was not measured word-by-word."},
    {"id": "M-04", "rule": "A picture frame pairs with a picture of the same frame; media change is not proven.",
     "evidence": ["picture-same"], "rung": 5,
     "meaning": "Same picture moved continuously. Different media was not colour-tracked and stays open."},
    {"id": "M-05", "rule": "Groups pair as groups when the group name/geometry matches.",
     "evidence": ["group-same"], "rung": 5,
     "meaning": "The group moved as one blob; ungrouping was not tested."},
    {"id": "M-06", "rule": "90° rotation still pairs.",
     "evidence": ["rotate90"], "rung": 5,
     "meaning": "One blob crossed the frame; >180° and flips stay open."},
    {"id": "M-07", "rule": "An entrance effect on the destination object blocks the Morph.",
     "evidence": ["entrance"], "rung": 5,
     "meaning": "The destination stayed hidden for the whole video; no object crossed."},
    {"id": "M-08", "rule": "An off-slide destination is absent, not staged.",
     "evidence": ["offslide"], "rung": 5,
     "meaning": "B object at x=14.5 in produced an empty stage; Morph does not fly it in by itself."},
    {"id": "M-09", "rule": "byWord and byChar keep the frame continuous.",
     "evidence": ["byword", "bychar"], "rung": 3,
     "meaning": "Geometry is continuous; the word/character interpolation was not verified frame-by-frame."},
    {"id": "M-10", "rule": "Z-order does not stop the pairing but can hide the object.",
     "evidence": ["zorder"], "rung": 4,
     "meaning": "One small blob remained under the foreground; use the object order deliberately."},
    {"id": "M-11", "rule": "A Morph adds its duration to the slide advance.",
     "evidence": ["video"], "rung": 5,
     "meaning": "45 slides × 2 s = 90 s expected; PowerPoint produced 109.4 s with 15 × 1.2 s Morphs."},
]

CASES = [
    ("same-bang", "Same `!!track`, same rect", "continuous"),
    ("same-name", "Same plain name, same rect", "continuous"),
    ("diff-name", "Different names, same rect", "continuous"),
    ("rect-ellipse", "Same `!!track`, rect→ellipse", "two-blobs"),
    ("text-same", "Same text", "continuous"),
    ("text-diff", "Different text", "continuous"),
    ("picture-same", "Same picture", "continuous"),
    ("picture-diff", "Different picture media", "not-measured"),
    ("group-same", "Group moves", "continuous"),
    ("rotate90", "90° rotation", "continuous"),
    ("entrance", "Destination has entrance", "static/no-match"),
    ("byword", "Morph byWord", "continuous"),
    ("bychar", "Morph byChar", "continuous"),
    ("zorder", "Z-order change", "continuous-occluded"),
    ("offslide", "Destination off-slide", "offscreen"),
]


def main():
    data = json.loads((ART / "matrix.json").read_text(encoding="utf-8"))
    by_case = {r["case"]: r for r in data["rows"]}
    final = []
    for case, label, fallback in CASES:
        row = by_case.get(case, {})
        override = OVERRIDES.get(case, {})
        final.append({
            "case": case, "label": label,
            "verdict": override.get("verdict", row.get("verdict", fallback)),
            "note": override.get("note", ""),
            "start_center_px": row.get("start_center"),
            "end_center_px": row.get("end_center"),
            "mid_blobs": row.get("mid", {}).get("blobs"),
            "mid_pixels": row.get("mid", {}).get("pixels"),
        })
    (ART / "matrix-final.json").write_text(
        json.dumps({"video": "preview/morph-matrix.mp4", "video_seconds": 109.395,
                    "cases": final, "rules": RULES}, indent=1), encoding="utf-8")

    states = PREVIEW / "states"
    states.mkdir(parents=True, exist_ok=True)
    keep = {"offslide", "zorder"}
    thumbs = []
    for case, _, _ in CASES:
        src = FRAMES / f"{case}.png"
        dst = states / f"{case}.png"
        if src.exists() and case not in keep:
            shutil.copy2(src, dst)
        if dst.exists():
            thumbs.append((case, dst))
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    tw, th, cols = 320, 180, 3
    sheet = Image.new("RGB", (cols * tw, 5 * (th + 30)), "#111111")
    draw = ImageDraw.Draw(sheet)
    verdicts = {c["case"]: c["verdict"] for c in final}
    for k, (case, path) in enumerate(thumbs):
        im = Image.open(path).convert("RGB").resize((tw, th))
        x, y = (k % cols) * tw, (k // cols) * (th + 30)
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + th + 4), f"{case}: {verdicts[case]}",
                  fill="#7CFC98" if verdicts[case].startswith("continuous") else "#FFD400",
                  font=font)
    sheet.save(PREVIEW / "morph-matrix-evidence.png")
    print("cases", len(final), "rules", len(RULES), "frames", len(thumbs))


if __name__ == "__main__":
    main()
