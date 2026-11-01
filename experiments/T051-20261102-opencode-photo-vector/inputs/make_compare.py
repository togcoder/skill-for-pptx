"""Photo vs catalogue vector, same height, for the T051 report."""
from __future__ import annotations

from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PHOTO = HERE / 'quickmill.jpg'
VECTOR = EXP / 'artifacts' / 'line.png'
OUT = EXP / 'preview' / 'photo-vs-vector.png'


def font(size: int, bold: bool = False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    try:
        return ImageFont.truetype('C:/Windows/Fonts/' + name, size)
    except Exception:
        return ImageFont.load_default()


def main() -> None:
    photo = Image.open(PHOTO).convert('RGB')
    w, h = photo.size
    scale = 1200 / max(w, h)
    bx, by, bw, bh = 190 / scale, 250 / scale, 637 / scale, 879 / scale
    pad = 55 / scale
    photo = photo.crop((int(bx - pad), int(by - pad), int(bx + bw + pad), int(by + bh + pad)))
    vector = Image.open(VECTOR).convert('RGB')
    height = 720
    photo.thumbnail((520, height), Image.LANCZOS)
    vector.thumbnail((520, height), Image.LANCZOS)
    gap, top = 24, 64
    sheet = Image.new('RGB', (gap + photo.width + gap + vector.width + gap, top + height + 76),
                      '#F2EFE8')
    d = ImageDraw.Draw(sheet)
    d.text((gap, 18), 'T051 — photo to controlled line illustration',
           font=font(22, True), fill='#20242A')
    d.text((gap, top - 24), 'SOURCE (CC0)', font=font(13, True), fill='#4A4F55')
    d.text((gap + photo.width + gap, top - 24), 'VECTOR — line style, catalogue budget',
           font=font(13, True), fill='#4A4F55')
    sheet.paste(photo, (gap, top))
    sheet.paste(vector, (gap + photo.width + gap, top + (height - vector.height) // 2))
    d.rectangle((gap, top, gap + photo.width, top + photo.height), outline='#D6D0C4')
    d.rectangle((gap + photo.width + gap, top + (height - vector.height) // 2,
                 gap + photo.width + gap + vector.width,
                 top + (height - vector.height) // 2 + vector.height), outline='#D6D0C4')
    metrics = json.loads((EXP / 'artifacts' / 'levels.json').read_text(encoding='utf-8'))['line']
    d.text((gap, top + height + 12),
           (f"GrabCut IoU {metrics['fidelity']['grabcut_iou']:.3f} · "
            f"{metrics['counts']['form']} form · {metrics['counts']['detail']} detail · "
            f"{metrics['stats']['nodes']:,} nodes · line style"),
           font=font(13), fill='#4A4F55')
    d.text((gap, top + height + 36),
           'The badge is a shape, not traced lettering. The cast shadow was trimmed from the silhouette.',
           font=font(13), fill='#4A4F55')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(OUT)


if __name__ == '__main__':
    main()
