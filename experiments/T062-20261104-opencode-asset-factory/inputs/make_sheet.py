#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - 3-up review sheet for the owner eye test."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 980
PAD = 24
PANEL_W = (W - PAD * 4) // 3
PANEL_H = int(PANEL_W * 9 / 16)

LABELS = [
    ("A  native shapes", "25 shapes - 20/20 art parts addressable"),
    ("B  one SVG picture", "1 p:pic + PNG fallback - 0/20 parts addressable"),
    ("C  one GLB model", "1 model3d - 0/20 parts addressable"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("segoeuib.ttf", "segoeui.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main(artifacts: Path, out: Path) -> int:
    sheet = Image.new("RGB", (W, H), (11, 17, 32))
    draw = ImageDraw.Draw(sheet)
    head, sub = font(40), font(20)

    for index, (title, caption) in enumerate(LABELS):
        x = PAD + index * (PANEL_W + PAD)
        y = 130
        render = Image.open(artifacts / f"render-{'abc'[index]}.png").convert("RGB")
        sheet.paste(render.resize((PANEL_W, PANEL_H), Image.LANCZOS), (x, y))
        draw.rectangle([x, y, x + PANEL_W, y + PANEL_H], outline=(45, 60, 90), width=2)
        draw.text((x, 84), title, fill=(248, 250, 252), font=head)
        draw.text((x, y + PANEL_H + 12), caption, fill=(148, 163, 184), font=sub)

    # Detail row: the badge at 2x, where the three representations diverge most.
    detail_y = 130 + PANEL_H + 58
    draw.text((PAD, detail_y), "Badge detail (2x): native custGeom ring  ·  SVG ring  ·  extruded ring",
              fill=(248, 250, 252), font=font(24))
    crop_w, crop_h = 360, 300
    for index in range(3):
        x = PAD + index * (crop_w + PAD)
        render = Image.open(artifacts / f"render-{'abc'[index]}.png").convert("RGB")
        # 720x600 px around the badge, shown at 1x
        crop = render.crop((1200, 0, 1920, 600)).resize((crop_w, crop_h), Image.LANCZOS)
        sheet.paste(crop, (x, detail_y + 40))
        draw.rectangle([x, detail_y + 40, x + crop_w, detail_y + 40 + crop_h], outline=(45, 60, 90), width=2)

    note = ("Slide copy is native in all three routes. Route C drops the five in-screen labels and the soft shadow: "
            "geometry cannot carry live text, and a lit 3D renderer has no soft-edge alpha.")
    draw.text((PAD, H - 46), note, fill=(148, 163, 184), font=font(20))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, optimize=True)
    print(out, sheet.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
