#!/usr/bin/env python3
"""Photo | T053 | T054 at matched machine height, plus the metric strip."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parents[2]
EXP = Path(__file__).resolve().parent.parent
OUT = EXP / "preview"
PHOTO = ROOT / "experiments/T051-20261102-opencode-photo-vector/inputs/quickmill.jpg"
T053 = ROOT / "experiments/T053-20261102-opencode-vector-reconstruction/preview/quickmill-reconstruction.png"
T054 = EXP / "preview/quickmill-t054.png"

CROPS = [
    ("SOURCE PHOTO", PHOTO, (220, 300, 1100, 1400), "0.800 W/H"),
    ("T053 — BOXY FIRST PASS", T053, (500, 530, 1730, 1800),
     "0.969 W/H · group 0.424"),
    ("T054 — LANDMARK MATCH", T054, (250, 70, 1900, 1930),
     "0.806 W/H · group 0.276"),
]
H = 980
PANEL_W = 980
GAP = 24
TOP = 76


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(r"C:\Windows\Fonts" + "\\" + name, size)


def main() -> None:
    imgs = []
    for label, path, box, metric in CROPS:
        im = Image.open(path).convert("RGB").crop(box)
        im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
        imgs.append((label, metric, im))
    sheet = Image.new("RGB", (GAP + 3 * (PANEL_W + GAP), TOP + H + 54), "#E9E4D7")
    d = ImageDraw.Draw(sheet)
    for i, (label, metric, im) in enumerate(imgs):
        x = GAP + i * (PANEL_W + GAP)
        d.text((x, 14), label, font=font(20, True), fill="#1F3B57")
        d.text((x, 43), metric, font=font(14), fill="#6E6A5E")
        if im.width > PANEL_W:
            im = im.crop(((im.width - PANEL_W) // 2, 0,
                          (im.width - PANEL_W) // 2 + PANEL_W, H))
        sheet.paste(im, (x + (PANEL_W - im.width) // 2, TOP))
        d.rectangle((x, TOP, x + PANEL_W, TOP + H), outline="#D6D0C4", width=1)
    d.text((GAP, TOP + H + 14),
           "Matched to the same machine height. The overlay/edge comparison is in compare-t054.png.",
           font=font(13), fill="#5E5A50")
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "t053-vs-t054.png", quality=92, optimize=True)
    print(OUT / "t053-vs-t054.png")


if __name__ == "__main__":
    main()
