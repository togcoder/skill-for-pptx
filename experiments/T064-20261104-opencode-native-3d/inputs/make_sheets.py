#!/usr/bin/env python3
"""T064: contact sheets of the transition window, cropped to the model.

One row per 0.1 s step, so a camera move and a cross-fade look different at a
glance: a fade shows two silhouettes in the same cell, a camera move shows one.

Run:  python experiments/T064-.../inputs/make_sheets.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PREVIEW = EXP / "preview"
TMP = EXP.parents[1] / "workspace" / "t064" / "frames" / "sheet"
CROP = (150, 250, 800, 870)      # model area at 1080p
THUMB = (260, 248)
START, STOP, STEP = 4.1, 6.1, 0.1


def frame(mp4: Path, t: float) -> Image.Image:
    p = TMP / f"{mp4.stem}-{t:04.1f}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4),
                    "-frames:v", "1", str(p)], check=True)
    return Image.open(p).convert("RGB")


def sheet(mp4: Path, out: Path) -> None:
    steps = [round(START + i * STEP, 1) for i in range(int((STOP - START) / STEP) + 1)]
    cols = 5
    rows = (len(steps) + cols - 1) // cols
    pad, label = 4, 16
    w = cols * (THUMB[0] + pad) + pad
    h = rows * (THUMB[1] + pad + label) + pad
    canvas = Image.new("RGB", (w, h), (24, 26, 30))
    draw = ImageDraw.Draw(canvas)
    for i, t in enumerate(steps):
        img = frame(mp4, t).crop(CROP).resize(THUMB, Image.LANCZOS)
        x = pad + (i % cols) * (THUMB[0] + pad)
        y = pad + (i // cols) * (THUMB[1] + pad + label)
        canvas.paste(img, (x, y))
        draw.text((x + 2, y + THUMB[1] + 2), f"t={t:.1f}s", fill=(210, 210, 210))
    canvas.save(out)
    print(out, canvas.size)


if __name__ == "__main__":
    for key in ("morph", "fade", "shared", "modelonly"):
        mp4 = PREVIEW / f"camera-{key}.mp4"
        sheet(mp4, PREVIEW / f"transition-sheet-{key}.png")
