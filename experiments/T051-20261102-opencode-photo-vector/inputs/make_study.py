"""Build the T051 budget study: four levels, renders and a contact sheet."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.photo_vector import build_illustration  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PHOTO = HERE / 'quickmill.jpg'
ART = EXP / 'artifacts'
PREVIEW = EXP / 'preview'
VECTORCRAFT = Path(r'D:\artcraft\VectorCraft\vectorcraft-cli.exe')
ART_REL = ART.relative_to(ROOT)
LEVELS = ('silhouette', 'form', 'catalogue', 'full')
TITLES = {
    'silhouette': 'Silhouette only',
    'form': 'Silhouette + form',
    'catalogue': 'Catalogue (curated detail)',
    'full': 'Full trace (strawman)',
}


def font(size: int, bold: bool = False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    for base in ('C:/Windows/Fonts/',):
        try:
            return ImageFont.truetype(base + name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def render(svg: Path, png: Path) -> None:
    res = subprocess.run([str(VECTORCRAFT), 'convert', str(svg), str(png), '--scale', '1'],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[-500:])


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    metrics = {}
    for level in LEVELS:
        svg = ART_REL / f'{level}.svg'
        png = ART_REL / f'{level}.png'
        result = build_illustration(
            PHOTO, svg, level=level, colors=5, width_mm=120,
            title=f'Quick Mill Omre — {level}',
            source='Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg',
            license='CC0')
        render(svg, png)
        result['render'] = str(png)
        metrics[level] = result
    # The line style is the recommended print deliverable: it keeps the form
    # hierarchy and drops the flat fills that obscure it.
    line_svg = ART_REL / 'line.svg'
    line_png = ART_REL / 'line.png'
    line = build_illustration(
        PHOTO, line_svg, level='catalogue', colors=5, width_mm=120, style='line',
        title='Quick Mill Omre — line',
        source='Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg',
        license='CC0')
    render(line_svg, line_png)
    line['render'] = str(line_png)
    metrics['line'] = line
    # Same full budget without fills, so the line-vs-full comparison is fair.
    full_line_svg = ART_REL / 'full-line.svg'
    full_line_png = ART_REL / 'full-line.png'
    full_line = build_illustration(
        PHOTO, full_line_svg, level='full', colors=5, width_mm=120, style='line',
        title='Quick Mill Omre — full line trace',
        source='Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg',
        license='CC0')
    render(full_line_svg, full_line_png)
    full_line['render'] = str(full_line_png)
    metrics['full-line'] = full_line
    (ART / 'line.json').write_text(
        json.dumps(line, ensure_ascii=False, indent=2), encoding='utf-8')
    (ART / 'levels.json').write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')

    # Contact sheet: photo + four budgets, same crop and height.
    photo = Image.open(PHOTO).convert('RGB')
    w, h = photo.size
    # object bbox at the 1200-px working size, scaled back to the original.
    scale = 1200 / max(w, h)
    bx, by, bw, bh = 190 / scale, 250 / scale, 637 / scale, 879 / scale
    pad = 60 / scale
    photo = photo.crop((int(bx - pad), int(by - pad), int(bx + bw + pad), int(by + bh + pad)))
    panel_w, panel_h = 300, 340
    gap, top = 18, 58
    cols = len(LEVELS) + 1
    sheet = Image.new('RGB', (gap + cols * (panel_w + gap), top + panel_h + 92), '#F2EFE8')
    d = ImageDraw.Draw(sheet)
    d.text((gap, 16), 'T051 — photo to vector: what each detail budget keeps',
           font=font(21, True), fill='#20242A')
    labels = ['Source photo'] + [TITLES[l] for l in LEVELS]
    images = [photo] + [Image.open(ART / f'{l}.png').convert('RGB') for l in LEVELS]
    for i, (label, image) in enumerate(zip(labels, images)):
        x = gap + i * (panel_w + gap)
        image.thumbnail((panel_w, panel_h - 26), Image.LANCZOS)
        ox = x + (panel_w - image.width) // 2
        oy = top + 24 + (panel_h - 26 - image.height) // 2
        sheet.paste(image, (ox, oy))
        d.rectangle((x, top, x + panel_w, top + panel_h), outline='#D6D0C4')
        d.text((x + 8, top + 6), label, font=font(13, True), fill='#20242A')
        if i == 0:
            note = '1015 × 1200 working crop'
        else:
            m = metrics[LEVELS[i - 1]]
            note = (f"{m['counts']['form']} form · {m['counts']['detail']} detail\n"
                    f"{m['stats']['colour_paths']} fills · {m['stats']['nodes']} nodes\n"
                    f"ΔE {m['fidelity']['colour_delta_e76']} · ink {m['edges']['ink_ratio']}")
        d.multiline_text((x + 8, top + panel_h + 10), note, font=font(12),
                         fill='#4A4F55', spacing=4)
    out = PREVIEW / 'budget-study.png'
    sheet.save(out, optimize=True)
    print(out)


if __name__ == '__main__':
    main()
