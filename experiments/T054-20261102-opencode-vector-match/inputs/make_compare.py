#!/usr/bin/env python3
"""Put the source photo and the vector reconstruction together at matched height.

Outputs:
  preview/compare-current.png   source | vector | 50% overlay | edge overlay
  preview/measure-current.json  bbox aspect and landmark ratios (manual rows)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parents[2]
HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PREVIEW = EXP / "preview"

PHOTO = ROOT / "experiments/T051-20261102-opencode-photo-vector/inputs/quickmill.jpg"
VECTOR = ROOT / "experiments/T054-20261102-opencode-vector-match/preview/quickmill-t054.png"

# Full machine, including knobs and portafilter handle; manual boxes on the
# source grid, documented in the report.
PHOTO_CROP = (220, 300, 1100, 1400)
VECTOR_CROP = (250, 70, 1750, 1930)

# Manual landmark rows, in source pixels: top panel, black band bottom,
# group-head centre, tray top, lower-panel top, base top, base bottom.
PHOTO_ROWS = [370, 590, 650, 900, 1000, 1230, 1390]
VECTOR_ROWS = [240, 594, 692, 1093, 1253, 1623, 1880]

TARGET_H = 1000
PANEL_W = 900
GAP = 26
LABEL_H = 44


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(r"C:\Windows\Fonts" + "\\" + name, size)


def crop(im: Image.Image, box) -> Image.Image:
    return im.crop(box)


def resize_h(im: Image.Image, height: int) -> Image.Image:
    w = round(im.width * height / im.height)
    return im.resize((w, height), Image.LANCZOS)


def center_on(im: Image.Image, w: int, h: int, bg="#FBFAF6") -> Image.Image:
    canvas = Image.new("RGB", (w, h), bg)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def edge_map(im: Image.Image) -> np.ndarray:
    gray = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 40, 100)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    return edges


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", type=Path, default=PHOTO)
    parser.add_argument("--vector", type=Path, default=VECTOR)
    parser.add_argument("--out", type=Path, default=PREVIEW / "compare-t054.png")
    parser.add_argument("--json", type=Path, default=PREVIEW / "measure-t054.json")
    parser.add_argument("--photo-crop", default="220,300,1100,1400")
    parser.add_argument("--vector-crop", default="250,70,1750,1930")
    args = parser.parse_args()

    pbox = tuple(int(v) for v in args.photo_crop.split(","))
    vbox = tuple(int(v) for v in args.vector_crop.split(","))
    photo = resize_h(crop(Image.open(args.photo).convert("RGB"), pbox), TARGET_H)
    vector = resize_h(crop(Image.open(args.vector).convert("RGB"), vbox), TARGET_H)

    # panel 1 and 2: same height, same panel width, centred horizontally
    p_panel = center_on(photo, PANEL_W, TARGET_H)
    v_panel = center_on(vector, PANEL_W, TARGET_H)

    # panel 3: 50% overlay, both centred
    blend = Image.blend(p_panel, v_panel, 0.5)

    # panel 4: source edges red, vector edges blue
    edge_canvas = Image.new("RGB", (PANEL_W, TARGET_H), "#FBFAF6")
    en = np.array(edge_canvas)
    pe = edge_map(p_panel)
    ve = edge_map(v_panel)
    en[pe > 0] = (190, 40, 30)
    en[ve > 0] = (30, 70, 190)
    edge_img = Image.fromarray(en)

    panels = [("SOURCE PHOTO", p_panel), ("T053 VECTOR", v_panel),
              ("50% OVERLAY", blend), ("EDGES  red=photo  blue=vector", edge_img)]
    cols = len(panels)
    sheet = Image.new("RGB", (GAP + cols * (PANEL_W + GAP),
                              LABEL_H + TARGET_H + 50), "#E9E4D7")
    d = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate(panels):
        x = GAP + i * (PANEL_W + GAP)
        d.text((x, 14), label, font=font(19, True), fill="#1F3B57")
        sheet.paste(im, (x, LABEL_H))
        d.rectangle((x, LABEL_H, x + PANEL_W, LABEL_H + TARGET_H),
                    outline="#D6D0C4", width=1)
    d.text((GAP, LABEL_H + TARGET_H + 12),
           "Matched to the same machine height; no non-uniform scaling.",
           font=font(13), fill="#5E5A50")
    PREVIEW.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=92, optimize=True)

    # measurements
    py0, py1 = PHOTO_ROWS[0], PHOTO_ROWS[-1]
    vy0, vy1 = VECTOR_ROWS[0], VECTOR_ROWS[-1]
    photo_ratios = [round((y - py0) / (py1 - py0), 3) for y in PHOTO_ROWS]
    vector_ratios = [round((y - vy0) / (vy1 - vy0), 3) for y in VECTOR_ROWS]
    data = {
        "photo_crop": pbox,
        "vector_crop": vbox,
        "photo_aspect_w_over_h": round((pbox[2] - pbox[0]) / (pbox[3] - pbox[1]), 3),
        "vector_aspect_w_over_h": round((vbox[2] - vbox[0]) / (vbox[3] - vbox[1]), 3),
        "landmark_names": ["top_panel_top", "black_band_bottom", "group_centre",
                           "tray_top", "lower_panel_top", "base_top", "base_bottom"],
        "photo_fractions": photo_ratios,
        "vector_fractions": vector_ratios,
        "delta": [round(v - p, 3) for p, v in zip(photo_ratios, vector_ratios)],
    }
    args.json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(args.out)
    print(args.json)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
