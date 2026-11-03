#!/usr/bin/env python3
"""Build review contact sheets for the T055 deck and camera study."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PREVIEW = EXP / "preview"
BG = (11, 20, 27)
AMBER = (215, 154, 50)
WHITE = (242, 239, 230)

try:
    FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
    SMALL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)
except OSError:
    FONT = ImageFont.load_default()
    SMALL = FONT


def deck_sheet() -> Path:
    labels = ["01 / STRUCTURE", "02 / BREWING BAY", "03 / CONTROLS"]
    tile_w, tile_h = 800, 450
    sheet = Image.new("RGB", (tile_w * 3 + 40, tile_h + 56), BG)
    draw = ImageDraw.Draw(sheet)
    for i, label in enumerate(labels):
        img = Image.open(PREVIEW / f"tour-v3-{i + 1}.png").convert("RGB")
        img = img.resize((tile_w, tile_h), Image.LANCZOS)
        x = 10 + i * (tile_w + 10)
        sheet.paste(img, (x, 46))
        draw.text((x, 16), label, fill=AMBER, font=FONT)
    out = PREVIEW / "contact-sheet-v3.png"
    sheet.save(out)
    return out


def camera_sheet() -> Path:
    labels = ["A / FRONT-LEFT", "B / LEFT 3/4", "C / LEFT WIDE",
              "D / TURNED MODEL", "E / HIGH LEFT", "F / FRONT-RIGHT"]
    files = ["camera-A_front_left_near.png", "camera-B_left_three_quarter.png",
             "camera-C_left_wide.png", "camera-D_turned_model.png",
             "camera-E_high_left.png", "camera-F_front_right.png"]
    tile_w, tile_h = 600, 338
    sheet = Image.new("RGB", (tile_w * 3 + 40, tile_h * 2 + 82), BG)
    draw = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(zip(labels, files)):
        img = Image.open(PREVIEW / name).convert("RGB")
        img = img.resize((tile_w, tile_h), Image.LANCZOS)
        col, row = i % 3, i // 3
        x = 10 + col * (tile_w + 10)
        y = 42 + row * (tile_h + 20)
        sheet.paste(img, (x, y))
        draw.text((x, y - 20), label, fill=AMBER, font=SMALL)
    out = PREVIEW / "camera-study-sheet.png"
    sheet.save(out)
    return out


if __name__ == "__main__":
    print(deck_sheet())
    print(camera_sheet())
