"""Contact sheet for the four T069 state-pair Morphs (static endpoints)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"

PAIRS = [
    ("3", "4", "VẬT CHẤT / Ý THỨC  ->  VẬT CHẤT QUYẾT ĐỊNH"),
    ("5", "6", "HAI CÁCH NHÌN  ->  BIỆN CHỨNG"),
    ("8", "9", "BA BỘ PHẬN  ->  MỘT CHỈNH THỂ"),
    ("12", "13", "LUẬN CƯƠNG  ->  CẢI TẠO THẾ GIỚI"),
]

W, H = 1280, 720
THUMB_W = 560
THUMB_H = int(THUMB_W * H / W)
MARGIN = 32
LABEL_H = 44
HEADER_H = 72
COLS = 2
ROWS = len(PAIRS)

canvas_w = MARGIN * 2 + THUMB_W * COLS + MARGIN
canvas_h = HEADER_H + MARGIN + ROWS * (THUMB_H + LABEL_H + MARGIN)
canvas = Image.new("RGB", (canvas_w, canvas_h), "#F7F1E8")
draw = ImageDraw.Draw(canvas)
font_path = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(font_path, 22)
small = ImageFont.truetype(font_path, 16)
head = ImageFont.truetype(font_path, 30)

draw.text((MARGIN, 20), "T069 — bốn cặp trạng thái, bốn Morph có nghĩa (1.2 s, byObject)",
          fill="#C1121F", font=head)

for row, (a, b, label) in enumerate(PAIRS):
    top = HEADER_H + MARGIN + row * (THUMB_H + LABEL_H + MARGIN)
    for col, (idx, tag) in enumerate([(a, "TRƯỚC"), (b, "SAU")]):
        img = Image.open(PREVIEW / f"slide-{int(idx):02d}.png").convert("RGB")
        img = img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        x = MARGIN + col * (THUMB_W + MARGIN)
        canvas.paste(img, (x, top))
        draw.rectangle([x, top, x + THUMB_W, top + THUMB_H], outline="#7A0C14", width=2)
        draw.text((x, top + THUMB_H + 6), f"{tag}  slide {idx}", fill="#7A0C14", font=small)
    draw.text((MARGIN, top + THUMB_H + 24), label, fill="#C1121F", font=font)

canvas.save(PREVIEW / "morph-pairs.png", optimize=True)
print("wrote", PREVIEW / "morph-pairs.png", (PREVIEW / "morph-pairs.png").stat().st_size)
