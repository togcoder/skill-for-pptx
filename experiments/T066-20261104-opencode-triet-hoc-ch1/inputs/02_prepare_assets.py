from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

HERE = Path(__file__).resolve().parent
CUT = HERE / "cut"
OUT = HERE / "assets"
OUT.mkdir(parents=True, exist_ok=True)
CREAM = (247, 241, 232, 255)


def duotone(img: Image.Image, shadow=(20, 4, 6), light=(150, 18, 26)) -> Image.Image:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    gray = ImageOps.grayscale(rgba.convert("RGB"))
    rgb = ImageOps.colorize(gray, black=shadow, white=light).convert("RGBA")
    rgb.putalpha(alpha)
    return rgb


def circle_portrait(src: Path, dst: Path, top_fraction: float, size: int = 1000):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    img = img.crop((0, 0, w, int(h * top_fraction)))
    img = duotone(img)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    disc = Image.new("RGBA", (size, size), CREAM)
    scale = min(0.94 * size / img.width, 0.96 * size / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    disc.alpha_composite(img, ((size - img.width) // 2, int(size * 0.015)))
    ss = 4
    mask = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    disc.putalpha(mask)
    disc.save(dst)


circle_portrait(CUT / "marx.png", OUT / "marx-circle.png", 0.62)
circle_portrait(CUT / "engels.png", OUT / "engels-circle.png", 0.72)
circle_portrait(CUT / "lenin.png", OUT / "lenin-circle.png", 0.68)

plato = Image.open(CUT / "plato.png").convert("RGBA")
plato = duotone(plato, shadow=(20, 4, 6), light=(190, 60, 58))
bbox = plato.getbbox()
if bbox:
    plato = plato.crop(bbox)
if max(plato.size) > 1300:
    r = 1300 / max(plato.size)
    plato = plato.resize((round(plato.width * r), round(plato.height * r)), Image.LANCZOS)
plato.save(OUT / "plato-full.png")

print("assets", [p.name for p in OUT.glob("*.png")])
