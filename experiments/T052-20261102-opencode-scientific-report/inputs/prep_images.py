"""Crop the chart images from Excel exports and prepare print-sized PNGs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
CHARTS = HERE.parent / "artifacts" / "charts"
FIGURES = HERE.parent / "artifacts" / "figures"


def trim(im: Image.Image, pad: int = 18) -> Image.Image:
    rgb = im.convert("RGB")
    bbox = ImageOps.invert(rgb).getbbox()
    if bbox:
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(rgb.width, bbox[2] + pad)
        bottom = min(rgb.height, bbox[3] + pad)
        rgb = rgb.crop((left, top, right, bottom))
    return rgb


def prepare(name: str, source: Path, *, crop=None, scale: int = 2, pad: int = 18,
            out_dir: Path | None = None) -> None:
    im = Image.open(source)
    if crop:
        im = im.crop(crop)
    im = trim(im, pad=pad)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    out = (out_dir or CHARTS) / f"{name}-print.png"
    im.save(out, optimize=True)
    print(out, im.size)


def main() -> None:
    # The line chart is exported as a whole worksheet page; crop the chart body.
    training_page = CHARTS / "page-01.png"
    if training_page.is_file():
        im = Image.open(training_page)
        # Chart occupies the right half of the exported A4 landscape page.
        crop = (int(im.width * 0.33), int(im.height * 0.08),
                int(im.width * 0.80), int(im.height * 0.44))
        prepare("training", training_page, crop=crop, scale=2)
    for name in ("pr", "f1", "ablation", "latency"):
        prepare(name, CHARTS / f"{name}.png", scale=2)
    for name in ("architecture", "windowing"):
        prepare(name, FIGURES / f"{name}.png", scale=1, pad=12, out_dir=FIGURES)


if __name__ == "__main__":
    main()
