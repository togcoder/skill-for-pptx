"""T074: read the PowerPoint video at 30 fps and classify each Morph case.

One tracked colour per case. At the middle of the Morph, a continuous object is
one blob whose centre lies between the A and B positions; a cross-fade shows two
blobs (or an object at one endpoint); a hidden destination shows none.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/T074-20261105-opencode-morph-rules"
MP4 = EXP / "preview/morph-matrix.mp4"
TMP = ROOT / "workspace/T074/frames"
TMP.mkdir(parents=True, exist_ok=True)

CASES = [
    "same-bang", "same-name", "diff-name", "rect-ellipse", "text-same",
    "text-diff", "picture-same", "picture-diff", "group-same", "rotate90",
    "entrance", "byword", "bychar", "zorder", "offslide",
]
PALETTE = [
    (215, 154, 50), (220, 80, 70), (80, 170, 220), (120, 200, 120),
    (200, 120, 220), (240, 200, 80), (90, 200, 190), (240, 140, 180),
    (170, 170, 240), (230, 120, 60), (140, 220, 90), (100, 180, 240),
    (230, 90, 140), (180, 140, 80), (120, 210, 170),
]
W, H = 1280, 720
A_CENTER = 2.5 / 13.333 * W
B_CENTER = 10.5 / 13.333 * W


def grab(t: float, name: str) -> np.ndarray:
    p = TMP / f"{name}-{t:05.2f}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}",
                    "-i", str(MP4), "-frames:v", "1", str(p)], check=True)
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def mask_for(rgb: np.ndarray, colour) -> np.ndarray:
    d = np.abs(rgb - np.array(colour, dtype=np.int16)).sum(axis=2)
    return d < 110


def blobs(mask: np.ndarray) -> dict:
    cols = np.where(mask.any(axis=0))[0]
    if len(cols) == 0:
        return {"blobs": 0, "span_px": 0, "center_px": None,
                "width_px": 0, "pixels": 0}
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > 40:
            groups.append((start, prev))
            start = c
        prev = c
    groups.append((start, prev))
    return {"blobs": len(groups), "span_px": int(cols[-1] - cols[0]),
            "center_px": round(float(cols.mean()), 1),
            "width_px": int(groups[0][1] - groups[0][0]) if len(groups) == 1 else None,
            "group_widths": [int(b - a) for a, b in groups],
            "pixels": int(mask.sum())}


def classify(mid: dict, end: dict, case: str) -> str:
    if case == "offslide":
        return "offscreen" if mid["pixels"] < 200 else "staged"
    if case == "entrance":
        return "hidden-destination" if mid["pixels"] < 200 else "visible-destination"
    if mid["pixels"] < 200:
        return "missing"
    if mid["blobs"] == 1 and mid["center_px"] is not None:
        c = mid["center_px"]
        if A_CENTER + 30 < c < B_CENTER - 30:
            return "continuous"
        if abs(c - A_CENTER) <= 40 or abs(c - B_CENTER) <= 40:
            return "endpoint"
    if mid["blobs"] > 1:
        return "two-blobs"
    return "wide-blob"


def main():
    rows = []
    mid_frames = []
    for i, (case, colour) in enumerate(zip(CASES, PALETTE), 1):
        start = (3 * i - 2) * 2
        mid = blobs(mask_for(grab(start + 0.6, f"{i:02d}-mid"), colour))
        end = blobs(mask_for(grab(start + 1.5, f"{i:02d}-end"), colour))
        verdict = classify(mid, end, case)
        rows.append({"case": case, "i": i, "b_slide": 3 * i - 1,
                     "start_s": start, "mid": mid, "end": end, "verdict": verdict})
        # keep the mid PNG for the contact sheet
        p = TMP / f"{i:02d}-mid-{start + 0.6:05.2f}.png"
        if p.exists():
            mid_frames.append((case, verdict, p))
        print(f"{case:14} {verdict:18} mid={mid}")

    (EXP / "artifacts/matrix.json").write_text(
        json.dumps({"fps": 30, "a_center_px": round(A_CENTER, 1),
                    "b_center_px": round(B_CENTER, 1), "rows": rows},
                   indent=1), encoding="utf-8")

    # contact sheet of mid frames
    thumb_w, thumb_h = 320, 180
    cols, rows_n = 3, 5
    sheet = Image.new("RGB", (cols * thumb_w, rows_n * (thumb_h + 30)), "#111111")
    draw = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    for k, (case, verdict, path) in enumerate(mid_frames):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        x, y = (k % cols) * thumb_w, (k // cols) * (thumb_h + 30)
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + thumb_h + 4), f"{case}: {verdict}",
                  fill="#FFD400" if verdict != "continuous" else "#7CFC98", font=f)
    out = EXP / "preview/matrix-midframes.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print("wrote", out, out.stat().st_size)


if __name__ == "__main__":
    main()
