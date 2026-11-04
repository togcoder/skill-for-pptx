#!/usr/bin/env python3
"""Contact sheets of the rendered click states (3 columns, labelled)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
STATES = EXP / "preview" / "states"
OUT = EXP / "preview" / "sheets"
CELL = (600, 338)
PAD = 10
LABEL_H = 30

SHEETS = {
    "t066-cover": ("T066 cover — click 0 → 4 (images enter last)", "t066-s1-c0"),
    "t066-plato": ("T066 slide 2 — the empty disc and its caption for 6 clicks", "t066-s2-c0"),
    "t066-flow": ("T066 slide 7 — portraits 2-4, timeline 5 (order contradicts dates)", "t066-s7-c0"),
    "A-cover": ("Variant A cover — anchors at t=0, title over them", "A-s1-c0"),
    "B-cover": ("Variant B cover — title first, portraits on the naming click", "B-s1-c0"),
    "A-flow": ("Variant A flow — whole picture at t=0, then walk the stops", "A-s2-c0"),
    "B-flow": ("Variant B flow — spine, then each marker on its date", "B-s2-c0"),
}


def frames(prefix: str):
    stem = prefix.rsplit("-c", 1)[0]
    return sorted(STATES.glob(f"{stem}-c*.png"))


def build(name: str, title: str, prefix: str):
    files = frames(prefix)
    cols = 3
    rows = (len(files) + cols - 1) // cols
    w = cols * CELL[0] + (cols + 1) * PAD
    h = 56 + rows * (CELL[1] + LABEL_H + PAD) + PAD
    sheet = Image.new("RGB", (w, h), (12, 12, 12))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        small = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((PAD, 14), title, fill=(240, 235, 225), font=font)
    for i, f in enumerate(files):
        r, c = divmod(i, cols)
        x = PAD + c * (CELL[0] + PAD)
        y = 56 + r * (CELL[1] + LABEL_H + PAD)
        im = Image.open(f).convert("RGB").resize(CELL, Image.LANCZOS)
        sheet.paste(im, (x, y))
        label = f.stem.split("-c")[-1]
        d.rectangle([x, y + CELL[1], x + CELL[0], y + CELL[1] + LABEL_H],
                    fill=(24, 24, 24))
        d.text((x + 8, y + CELL[1] + 7), f"click {int(label)}", fill=(232, 176, 75),
               font=small)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"sheet-{name}.png"
    sheet.save(path)
    print(path, sheet.size)


if __name__ == "__main__":
    for name, (title, prefix) in SHEETS.items():
        build(name, title, prefix)
