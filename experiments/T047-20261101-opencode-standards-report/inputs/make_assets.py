"""Pre-process the camera PNG and build the T047 cover/figure assets.

Cross-asset pipeline:
  SVG (authored) -> VectorCraft raster -> Pillow trim/grade/composite -> DOCX.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"


def trim(im: Image.Image, pad: int = 24) -> Image.Image:
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(im, (pad, pad))
    return canvas


def grade(im: Image.Image) -> Image.Image:
    # Mild S-curve contrast and a cool shadow / warm highlight grade.
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            r = min(255, int(255 * ((r / 255) ** 0.96) * 1.02))
            g = min(255, int(255 * ((g / 255) ** 0.98) * 1.00))
            b = min(255, int(255 * ((b / 255) ** 1.02) * 1.04))
            px[x, y] = (r, g, b, a)
    return im


def cover(camera: Image.Image) -> Image.Image:
    W, H = 1800, 1040
    base = Image.new("RGB", (W, H), "#0A1A2A")
    # Vertical/diagonal navy gradient.
    px = base.load()
    for y in range(H):
        for x in range(W):
            t = min(1.0, max(0.0, (x / W) * 0.55 + (y / H) * 0.45))
            r = int(9 + (23 - 9) * t)
            g = int(26 + (59 - 26) * t)
            b = int(42 + (92 - 42) * t)
            px[x, y] = (r, g, b)
    draw = ImageDraw.Draw(base, "RGBA")

    # Large quiet year watermark on the left; the Word title sits below.
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 300)
    except Exception:
        font = None
    if font is not None:
        draw.text((70, 560), "2026", font=font, fill=(255, 255, 255, 20))

    # Faint isometric grid.
    for i in range(-10, 30):
        x0 = i * 110
        draw.line([(x0, H), (x0 + 520, 0)], fill=(255, 255, 255, 10), width=1)
        draw.line([(x0, 0), (x0 + 520, H)], fill=(255, 255, 255, 7), width=1)
    # Large soft arc / halo behind the product.
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for r in range(420, 120, -18):
        alpha = int(8 + (420 - r) * 0.05)
        hd.ellipse((W - 640 - r, H // 2 - r, W - 640 + r, H // 2 + r),
                   outline=(46, 117, 182, alpha), width=2)
    base = Image.alpha_composite(base.convert("RGBA"), halo)

    # Product placed on the right, with a soft floor shadow.
    cam = camera.copy()
    target_h = 820
    scale = target_h / cam.height
    cam = cam.resize((int(cam.width * scale), target_h), Image.LANCZOS)
    cx = W - cam.width // 2 - 170
    cy = 80
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((cx - cam.width // 2 + 40, cy + target_h - 32,
                cx + cam.width // 2 + 40, cy + target_h + 42),
               fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    base = Image.alpha_composite(base, shadow)
    base.alpha_composite(cam, (cx - cam.width // 2, cy))

    # Warm accent rule on the left (the Word title sits below the image).
    draw = ImageDraw.Draw(base, "RGBA")
    base.convert("RGB").save(ART / "cover.png", optimize=True)
    return base


def product_figure(camera: Image.Image) -> None:
    camera.save(ART / "product-camera.png", optimize=True)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    raw = Image.open(HERE / "camera.png").convert("RGBA")
    camera = grade(trim(raw))
    cover(camera)
    product_figure(camera)
    print("wrote", ART / "cover.png", ART / "product-camera.png")


if __name__ == "__main__":
    main()
