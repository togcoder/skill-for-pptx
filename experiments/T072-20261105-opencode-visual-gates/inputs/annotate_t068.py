"""Annotate the two VIS-EMPTY-CARD hits on the T068 slide 2 render."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PNG = ROOT / "experiments/T068-20261104-antigravity-deck-director/preview/slide-02.png"
OUT = ROOT / "experiments/T072-20261105-opencode-visual-gates/preview/t068-empty-cards.png"
BOXES = {
    "Major Content": (0.076, 0.287, 0.491, 0.580),
    "Minor Content": (0.637, 0.287, 0.290, 0.580),
}

img = Image.open(PNG).convert("RGB")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
W, H = img.size
for name, (x, y, w, h) in BOXES.items():
    box = (int(x * W), int(y * H), int((x + w) * W), int((y + h) * H))
    draw.rectangle(box, outline="#FFD400", width=6)
    draw.text((box[0] + 12, box[3] - 44), f"VIS-EMPTY-CARD · {name}", fill="#FFD400", font=font)
draw.rectangle((20, H - 54, W - 20, H - 12), fill="#111111")
draw.text((32, H - 48), "T072: two large content fields hold only a label (T068 slide 2).",
          fill="#FFFFFF", font=small)
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
print("wrote", OUT, OUT.stat().st_size)
