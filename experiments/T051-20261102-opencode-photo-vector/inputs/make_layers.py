"""Isolate the four SVG layers and compose a layer-stack sheet (T051)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / 'artifacts'
PREVIEW = EXP / 'preview'
VECTORCRAFT = Path(r'D:\artcraft\VectorCraft\vectorcraft-cli.exe')

SOURCE = ART / 'catalogue.svg'
PAPER = '#F7F5F0'
FAINT = '#E8E4DA'


def font(size: int, bold: bool = False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    try:
        return ImageFont.truetype('C:/Windows/Fonts/' + name, size)
    except Exception:
        return ImageFont.load_default()


def group(svg: str, name: str) -> str:
    match = re.search(rf'<g id="{name}".*?</g>', svg, re.S)
    return match.group(0) if match else ''


def make_layer(name: str, body: str) -> Path:
    header = SOURCE.read_text(encoding='utf-8')
    header = header[: header.index('<g id="silhouette-fill"')]
    header = header.replace('<rect id="paper" x="0" y="0" width="1015" height="1200" fill="#F7F5F0"/>',
                            f'<rect id="paper" x="0" y="0" width="1015" height="1200" fill="{FAINT}"/>')
    svg = header + body + '\n</svg>'
    path = ART / f'layer-{name}.svg'
    path.write_text(svg, encoding='utf-8')
    png = PREVIEW / f'layer-{name}.png'
    subprocess.run([str(VECTORCRAFT), 'convert', str(path), str(png), '--scale', '1'],
                   capture_output=True, text=True)
    return png


def main() -> None:
    svg = SOURCE.read_text(encoding='utf-8')
    sil = group(svg, 'silhouette-fill')
    colour = group(svg, 'colour')
    form = group(svg, 'form')
    detail = group(svg, 'detail')
    sil_faint = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{FAINT}"', sil, count=1)
    pngs = {
        'shape': make_layer('shape', sil),
        'colour': make_layer('colour', sil + colour),
        'form': make_layer('form', sil_faint + form),
        'detail': make_layer('detail', sil_faint + detail),
    }

    labels = {
        'shape': '1 · Silhouette',
        'colour': '2 · Flat colour',
        'form': '3 · Form lines',
        'detail': '4 · Detail only',
    }
    panel_w, panel_h = 330, 420
    gap, top = 18, 58
    sheet = Image.new('RGB', (gap + 4 * (panel_w + gap), top + panel_h + 28), '#F2EFE8')
    d = ImageDraw.Draw(sheet)
    d.text((gap, 16), 'T051 — the four layers, isolated', font=font(21, True), fill='#20242A')
    for i, key in enumerate(('shape', 'colour', 'form', 'detail')):
        x = gap + i * (panel_w + gap)
        image = Image.open(pngs[key]).convert('RGB')
        image.thumbnail((panel_w, panel_h), Image.LANCZOS)
        oy = top + (panel_h - image.height) // 2
        sheet.paste(image, (x + (panel_w - image.width) // 2, oy))
        d.rectangle((x, top, x + panel_w, top + panel_h), outline='#D6D0C4')
        d.text((x + 8, top + 6), labels[key], font=font(13, True), fill='#20242A')
    out = PREVIEW / 'layer-stack.png'
    sheet.save(out, optimize=True)
    print(out)


if __name__ == '__main__':
    main()
