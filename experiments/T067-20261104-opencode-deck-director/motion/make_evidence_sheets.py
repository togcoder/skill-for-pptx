#!/usr/bin/env python3
"""Compose the before/after evidence sheets from the PowerPoint stable-state PNGs."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

MOTION = Path(__file__).resolve().parent
W, H = 760, 428
LABEL = 30
GAP = 12
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
SMALL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)


def tile(path: Path, label: str, sub: str = "") -> Image.Image:
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, (W, H), method=Image.LANCZOS)
    out = Image.new("RGB", (W, H + LABEL), (20, 8, 10))
    out.paste(im, (0, LABEL))
    d = ImageDraw.Draw(out)
    d.text((10, 4), label, font=FONT, fill=(255, 235, 200))
    if sub:
        d.text((W - 10, 6), sub, font=SMALL, fill=(210, 180, 160), anchor="ra")
    return out


def sheet(pairs, out_path: Path):
    cols, rows = 2, len(pairs)
    sheet = Image.new("RGB", (cols * W + (cols + 1) * GAP, rows * (H + LABEL) + (rows + 1) * GAP),
                      (10, 4, 6))
    for r, (left, right) in enumerate(pairs):
        y = GAP + r * (H + LABEL + GAP)
        sheet.paste(left, (GAP, y))
        sheet.paste(right, (GAP * 2 + W, y))
    sheet.save(out_path)
    print(out_path, sheet.size)


def main():
    pairs = [
        (tile(MOTION / "before/s01-00-base.png", "SLIDE 1 — BEFORE: base state", "empty rings, no title"),
         tile(MOTION / "after/s01-00-base.png", "SLIDE 1 — AFTER: base state", "title + portraits at t=0")),
        (tile(MOTION / "before/s02-00-base.png", "SLIDE 2 — BEFORE: base state", "red disc, no title"),
         tile(MOTION / "after/s02-00-base.png", "SLIDE 2 — AFTER: base state", "title + Plato at t=0")),
        (tile(MOTION / "before/s04-00-base.png", "SLIDE 4 — BEFORE: base state", "arc + dots, no title"),
         tile(MOTION / "after/s04-00-base.png", "SLIDE 4 — AFTER: base state", "title + diagram at t=0")),
        (tile(MOTION / "before/s07-00-base.png", "SLIDE 7 — BEFORE: base state", "empty rings + dates"),
         tile(MOTION / "after/s07-00-base.png", "SLIDE 7 — AFTER: base state", "title + portraits at t=0")),
        (tile(MOTION / "before/s09-00-base.png", "SLIDE 9 — BEFORE: base state", "empty field"),
         tile(MOTION / "after/s09-00-base.png", "SLIDE 9 — AFTER: base state", "full quote at t=0")),
    ]
    sheet(pairs, MOTION / "evidence-sheet.png")

    quad = [
        tile(MOTION / "after/s04-00-base.png", "SLIDE 4 — t=0", "title + diagram"),
        tile(MOTION / "after/s04-01-click1.png", "SLIDE 4 — click 1", "dialectic card"),
        tile(MOTION / "after/s04-02-click2.png", "SLIDE 4 — click 2", "straight line + label"),
        tile(MOTION / "after/s04-03-click3.png", "SLIDE 4 — click 3", "meta card"),
    ]
    out = Image.new("RGB", (2 * W + 3 * GAP, 2 * (H + LABEL) + 3 * GAP), (10, 4, 6))
    for i, im in enumerate(quad):
        r, c = divmod(i, 2)
        out.paste(im, (GAP + c * (W + GAP), GAP + r * (H + LABEL + GAP)))
    out.save(MOTION / "slide4-states.png")
    print(MOTION / "slide4-states.png", out.size)


if __name__ == "__main__":
    main()
