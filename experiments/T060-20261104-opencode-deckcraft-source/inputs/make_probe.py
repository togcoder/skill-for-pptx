"""Build a 4-slide timing probe deck (not committed; workspace only).

Each slide has one auto-start effect that exercises a timing feature DeckCraft's
player models: auto-reverse + repeat (spin), auto-reverse + repeat (pulse),
effect-level easing (fly), and a custom motion path with effect-level easing.
PowerPoint CreateVideo and DeckCraft's render-animation can then be compared on
the same axis.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_animator as anim  # noqa: E402

OUT = ROOT / "workspace/probe.pptx"
BASE = ROOT / "workspace/probe_base.pptx"


def build_base():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for _ in range(4):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        box = slide.shapes.add_shape(1, Inches(4.5), Inches(2.8), Inches(4.2), Inches(1.6))
        box.text_frame.text = "PROBE"
        for p in box.text_frame.paragraphs:
            p.font.size = Pt(48)
    prs.save(BASE)


def rewrite():
    specs = [
        [{"preset": "ppt:spin", "trigger": "with", "start": "auto", "duration_ms": 1000, "auto_reverse": True, "repeat": 2}],
        [{"preset": "pulse", "trigger": "with", "start": "auto", "duration_ms": 500, "repeat": 3}],
        [{"preset": "ppt:fly", "trigger": "with", "start": "auto", "duration_ms": 800, "accel": 0.3, "decel": 0.7}],
        [{"preset": "path", "trigger": "with", "start": "auto", "duration_ms": 1000, "points": [{"x": 0, "y": 0}, {"x": 0.25, "y": 0}], "accel": 0.2, "decel": 0.6}],
    ]
    tmp = OUT.with_suffix(".tmp.pptx")
    with zipfile.ZipFile(BASE) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
                n = int(re.search(r"slide(\d+)\.xml$", item.filename).group(1))
                root = etree.fromstring(data)
                shapes = anim.top_level_objects(root)
                spid = next(iter(shapes))
                effects = [dict(e, spid=spid) for e in specs[n - 1]]
                anim.apply_timeline(root, [{"id": "c1", "start": "auto", "effects": effects}], mode="replace")
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    shutil.move(tmp, OUT)


if __name__ == "__main__":
    build_base()
    rewrite()
    print(OUT)



