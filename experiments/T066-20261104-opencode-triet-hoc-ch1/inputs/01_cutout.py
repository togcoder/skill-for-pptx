from pathlib import Path

from PIL import Image, ImageOps
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "cut"
OUT.mkdir(parents=True, exist_ok=True)
session = new_session("u2net")

for p in sorted(RAW.glob("*.jpg")):
    img = Image.open(p).convert("RGB")
    cut = remove(img, session=session, post_process_mask=True)
    cut = cut.convert("RGBA")
    bbox = cut.getbbox()
    if bbox:
        cut = cut.crop(bbox)
    # keep a small transparent margin so the cut-out breathes in the deck
    margin = max(8, int(max(cut.size) * 0.015))
    canvas = Image.new("RGBA", (cut.width + margin * 2, cut.height + margin * 2), (0, 0, 0, 0))
    canvas.alpha_composite(cut, (margin, margin))
    # cap the long edge at 1400 px
    if max(canvas.size) > 1400:
        ratio = 1400 / max(canvas.size)
        canvas = canvas.resize((round(canvas.width * ratio), round(canvas.height * ratio)), Image.LANCZOS)
    canvas.save(OUT / f"{p.stem}.png")
    print(p.name, "->", canvas.size)
