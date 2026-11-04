#!/usr/bin/env python3
"""Prepare the one photograph for five style treatments (T067).

Source: Karl Marx, 1875 (Wikimedia Commons, public domain).
Pipeline: background removal (rembg/U2Net) -> figure crop -> per-style grade and
mask. Everything is done before the PPTX is written (lab pre-processing rule);
the PPTX embeds only treated PNGs, never the raw photograph.

Outputs (inputs/assets/):
  marx-editorial.png  1:1 circle mask, crimson duotone, hard edge
  marx-glass.png      4:5 rounded mask, indigo duotone, cool
  marx-clay.png       4:5 blob mask, warm 6-level posterize, 8 px feather
  marx-swiss.png      1:1 square, grayscale
  marx-collage.png    4:5 rect, 4-level ink/paper posterize
"""
from __future__ import annotations

import argparse
import math
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
RAW = HERE / "raw" / "marx.jpg"
CUT = HERE / "raw" / "marx-cut.png"
URL = "https://commons.wikimedia.org/wiki/Special:FilePath/Karl%20Marx%20001.jpg"
SOURCE_NOTE = (
    "Karl Marx 001.jpg, Wikimedia Commons, public domain, "
    "downloaded 2026-11-04; background removed with rembg 2.0.86 (U2Net); "
    "cropped, graded and masked by inputs/prepare_assets.py"
)


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _luma(im: Image.Image) -> Image.Image:
    return ImageOps.grayscale(im.convert("RGB"))


def duotone(im: Image.Image, shadow: str, highlight: str, posterize: int | None = None,
            gamma: float = 1.0) -> Image.Image:
    g = _luma(im)
    if posterize:
        levels = max(2, posterize)
        g = g.point(lambda v: round(v / 255 * (levels - 1)) * 255 // (levels - 1))
    if gamma != 1.0:
        g = g.point(lambda v: round(255 * (v / 255) ** gamma))
    lo, hi = _hex(shadow), _hex(highlight)
    lut = []
    for c in range(3):
        lut += [_mix(lo, hi, i / 255)[c] for i in range(256)]
    return Image.merge("RGB", [g.point(lut[c * 256:(c + 1) * 256]) for c in range(3)])


def circle_mask(size: int, ss: int = 4) -> Image.Image:
    m = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def rounded_mask(w: int, h: int, radius: int, ss: int = 4) -> Image.Image:
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1),
                                        radius=radius * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def blob_mask(w: int, h: int, feather: int = 8, ss: int = 2) -> Image.Image:
    """A soft superellipse with four low-frequency lobes (clay, not a circle)."""
    big = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(big)
    cx, cy = w * ss / 2, h * ss / 2
    rx, ry = w * ss * 0.49, h * ss * 0.49
    pts = []
    for i in range(240):
        t = 2 * math.pi * i / 240
        wobble = 1 + 0.035 * math.sin(3 * t + 0.7) + 0.02 * math.cos(5 * t)
        x = cx + rx * math.copysign(abs(math.cos(t)) ** 0.72, math.cos(t)) * wobble
        y = cy + ry * math.copysign(abs(math.sin(t)) ** 0.72, math.sin(t)) * wobble
        pts.append((x, y))
    d.polygon(pts, fill=255)
    m = big.resize((w, h), Image.LANCZOS)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return m


def apply_mask(im: Image.Image, mask: Image.Image) -> Image.Image:
    """Clip an RGBA image by a frame mask without losing its own silhouette."""
    from PIL import ImageChops
    out = im.convert("RGBA")
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return out


def panelize(im: Image.Image, bg: str, mask: Image.Image) -> Image.Image:
    """Composite a cut-out over an opaque card colour, then clip to the frame."""
    base = Image.new("RGB", im.size, _hex(bg))
    base.paste(im.convert("RGB"), (0, 0), im.getchannel("A"))
    out = base.convert("RGBA")
    out.putalpha(mask)
    return out


def figure_crop(cut: Image.Image, aspect: float, top: float = 0.0,
                height: float = 0.65) -> Image.Image:
    """Crop the cut-out to `aspect`, measured from the head down.

    top/height are fractions of the figure's alpha bbox. Padding added to reach
    the aspect ratio stays transparent.
    """
    bbox = cut.getchannel("A").getbbox()
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0, y1 - y0
    cy0 = y0 + int(bh * top)
    ch = int(bh * height)
    cw = int(ch * aspect)
    cx = x0 + bw // 2
    return cut.crop((cx - cw // 2, cy0, cx - cw // 2 + cw, cy0 + ch))


def load_cut(raw: Path, cut_path: Path) -> Image.Image:
    if cut_path.is_file():
        return Image.open(cut_path).convert("RGBA")
    from rembg import new_session, remove
    im = Image.open(raw).convert("RGB")
    out = remove(im, session=new_session("u2net"), post_process_mask=True)
    cut_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(cut_path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--cut", type=Path, default=CUT)
    ap.add_argument("--out", type=Path, default=ASSETS)
    ns = ap.parse_args()
    ns.out.mkdir(parents=True, exist_ok=True)
    if not ns.raw.is_file():
        ns.raw.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", URL)
        urllib.request.urlretrieve(URL, ns.raw)
    cut = load_cut(ns.raw, ns.cut)

    # 1. editorial: crimson duotone cut-out, clipped by the circle
    fig = figure_crop(cut, 1.0, top=0.0, height=0.50).resize((800, 800), Image.LANCZOS)
    ed = duotone(fig, "#4A0A10", "#D8A791", gamma=1.2)
    ed.putalpha(fig.getchannel("A"))
    ed = apply_mask(ed, circle_mask(800)).quantize(96, method=Image.FASTOCTREE)
    ed.save(ns.out / "marx-editorial.png", optimize=True)

    # 2. glass: 4:5 card, indigo duotone over a night panel, rounded frame
    fig = figure_crop(cut, 0.8, top=0.0, height=0.55).resize((760, 950), Image.LANCZOS)
    gl = duotone(fig, "#0A1030", "#DCE9FF", gamma=1.05)
    gl.putalpha(fig.getchannel("A"))
    gl = panelize(gl, "#141B3A", rounded_mask(760, 950, 48))
    gl.quantize(128, method=Image.FASTOCTREE).save(
        ns.out / "marx-glass.png", optimize=True)

    # 3. clay: 4:5 medallion, warm posterize smoothed first, blob frame + rim
    fig = figure_crop(cut, 0.8, top=0.0, height=0.55).resize((620, 775), Image.LANCZOS)
    fig = fig.filter(ImageFilter.MedianFilter(5))
    cl = duotone(fig, "#5A3A2E", "#FFE9CF", posterize=5, gamma=1.08)
    cl.putalpha(fig.getchannel("A"))
    mask = blob_mask(620, 775, feather=0)
    medallion = panelize(cl, "#5A3A2E", mask)
    rim_mask = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(15)), mask)
    rim = Image.new("RGBA", medallion.size, _hex("#FFF8F0") + (255,))
    rim.putalpha(rim_mask)
    medallion = Image.alpha_composite(medallion, rim)
    medallion.save(ns.out / "marx-clay.png", optimize=True)

    # 4. swiss: the photograph as a document — square crop of the raw, grayscale
    sw = Image.open(ns.raw).convert("RGB")
    side = min(sw.size)
    box = ((sw.width - side) // 2, 150, (sw.width + side) // 2, 150 + side)
    sw = ImageOps.autocontrast(ImageOps.grayscale(sw.crop(box)), cutoff=1)
    sw.resize((600, 600), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE,
                                                 colors=32).save(
        ns.out / "marx-swiss.png", optimize=True)

    # 5. collage: xerox plate — 4:5 crop of the raw, 4-level ink/paper
    co = Image.open(ns.raw).convert("RGB")
    cw = int(co.height * 0.8)
    box = ((co.width - cw) // 2, 140, (co.width + cw) // 2, co.height)
    co = co.crop(box).resize((600, 750), Image.LANCZOS)
    duotone(co, "#141414", "#F4E9D8", posterize=4, gamma=0.9).save(
        ns.out / "marx-collage.png", optimize=True)

    note = ns.out / "SOURCE.txt"
    note.write_text(SOURCE_NOTE + "\n", encoding="utf-8")
    for f in sorted(ns.out.glob("*.png")):
        print(f"{f.name:24s} {f.stat().st_size / 1024:7.1f} KB "
              f"{Image.open(f).size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
