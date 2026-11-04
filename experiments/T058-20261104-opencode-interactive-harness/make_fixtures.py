"""Build the synthetic fixtures used by the T058 harness.

Three artifacts, each with a different purpose:

1. ``t032_trigger_fixture.pptx`` — one interactive (shape-click) trigger written
   by ``scripts/interactive_triggers.py`` (the T032-adopted writer, T033 drop).
   **PowerPoint 16.0 refuses to open this file.** It is kept as a negative
   control for T061; see REPORT.md.
2. ``animator_trigger_fixture.pptx`` — the same stage with a trigger written by
   ``scripts/pptx_animator.py`` through ``apply_timeline(trigger_spid=...)``.
   The file opens, but the exit effect is applied when the slide starts instead
   of waiting for the click (the interactiveSeq has no ``p:stCondLst``).
3. ``t049_main_control.pptx`` — a copy of the T049 two-slide game deck with one
   main-sequence click added to slide 1 (``TextBox 3`` fades in).  Used to show
   that ``GotoClick`` advances the main sequence but does not fire a shape
   trigger, and that the trigger still fires afterwards.

All decks are 16:9, 960x540 pt, synthetic, and contain no external media.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402
from lxml import etree as ET  # noqa: E402

from scripts import interactive_triggers as trig  # noqa: E402
from scripts import pptx_animator as anim  # noqa: E402

OUT = Path(__file__).resolve().parent / "artifacts"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
T049_DECK = (ROOT / "experiments" / "T049-20261101-antigravity-advanced-interactivity"
             / "artifacts" / "one_slide_games_suite.pptx")


def _textbox(slide, left, top, width, height, text, size=16, color="FFFFFF", bold=False):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = RGBColor.from_string(color)
    p.font.bold = bold
    return box


def _rounded(slide, name, left, top, width, height, fill, text, text_color="0B1220"):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(left), Inches(top), Inches(width), Inches(height))
    shape.name = name
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(fill)
    shape.line.color.rgb = RGBColor.from_string("FFFFFF")
    shape.line.width = Pt(1.25)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor.from_string(text_color)
    return shape


def build_stage(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor.from_string("0F172A")

    _textbox(slide, 0.6, 0.35, 8.0, 0.5,
             "T058 trigger fixture", size=24, color="FFFFFF", bold=True)
    _textbox(slide, 0.6, 0.95, 8.0, 0.4,
             "Synthetic deck. Click the amber button.", size=13, color="94A3B8")

    _rounded(slide, "TargetCard", 0.8, 2.0, 4.0, 2.6, "22C55E",
             "TARGET CARD\nvisible at start", "052E16")
    _rounded(slide, "StepBox", 5.4, 2.0, 3.2, 1.2, "3B82F6",
             "MAIN SEQUENCE STEP", "EFF6FF")
    _rounded(slide, "TriggerBtn", 5.4, 4.3, 3.2, 1.0, "F59E0B",
             "CLICK ME (trigger)", "1C1917")

    _textbox(slide, 0.8, 6.4, 10.0, 0.5,
             "Interactive trigger: hide TargetCard  |  Main click: reveal StepBox",
             size=11, color="64748B")
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))


def _shape_ids(path: Path, part: str = "ppt/slides/slide1.xml") -> dict:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read(part))
    return {el.get("name"): el.get("id") for el in root.iter()
            if el.tag.endswith("}cNvPr") and el.get("name")}


def _patch_slide_xml(path: Path, mutate, part: str = "ppt/slides/slide1.xml") -> None:
    with zipfile.ZipFile(path) as z:
        items = [(i.filename, i.compress_type, z.read(i.filename)) for i in z.infolist()]
    tmp = path.with_suffix(".tmp.pptx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, compress_type, data in items:
            if name == part:
                root = ET.fromstring(data)
                mutate(root)
                data = ET.tostring(root, xml_declaration=True, encoding="UTF-8",
                                   standalone=True)
            z.writestr(name, data, compress_type=compress_type)
    tmp.replace(path)


def build_t032_trigger(path: Path) -> None:
    build_stage(path)
    ids = _shape_ids(path)

    def mutate(root):
        trig.apply_interactive_triggers(
            root,
            [{
                "trigger": "TriggerBtn",
                "action": "hide",
                "targets": ["TargetCard"],
                "preset": "zoom",
                "duration_ms": 400,
            }],
            shape_id_map=ids,
        )

    _patch_slide_xml(path, mutate)


def build_animator_trigger(path: Path) -> None:
    build_stage(path)
    ids = _shape_ids(path)

    def mutate(root):
        anim.apply_timeline(root, [
            {"id": "trigger-click", "trigger_spid": ids["TriggerBtn"], "effects": [
                {"preset": "fade-out", "spid": ids["TargetCard"], "trigger": "click",
                 "duration_ms": 400},
            ]},
        ])

    _patch_slide_xml(path, mutate)


def build_t049_main_control(path: Path) -> None:
    """Copy the T049 deck and add one main-sequence click on slide 1."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(T049_DECK.read_bytes())

    def mutate(root):
        anim.apply_timeline(root, [
            {"id": "main-1", "start": "click", "effects": [
                {"preset": "fade-out", "spid": "3", "trigger": "click",
                 "duration_ms": 300},
            ]},
        ], mode="extend")

    _patch_slide_xml(path, mutate)


def verify(path: Path) -> dict:
    from scripts.advanced_interactivity import inspect_interactivity
    info = inspect_interactivity(path)
    result = {"path": str(path), "bytes": path.stat().st_size, "inspect": info}
    if path.name == "t049_main_control.pptx":
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("ppt/slides/slide1.xml"))
        result["main_sequence_groups"] = len(anim.read_main_sequence(root))
        result["interactive_sequences"] = len(anim.read_interactive_sequences(root))
    return result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        "t032_trigger_fixture.pptx": build_t032_trigger,
        "animator_trigger_fixture.pptx": build_animator_trigger,
        "t049_main_control.pptx": build_t049_main_control,
    }
    for name, builder in targets.items():
        builder(OUT / name)
    report = {
        "fixtures": [verify(OUT / name) for name in targets],
        "provenance": {
            "t032_trigger_fixture.pptx":
                "scripts/interactive_triggers.apply_interactive_triggers (T032/T033 writer). "
                "PowerPoint 16.0 refuses to open it.",
            "animator_trigger_fixture.pptx":
                "scripts/pptx_animator.apply_timeline(trigger_spid=...). Opens, but the "
                "interactiveSeq has no p:stCondLst and the exit runs at slide start.",
            "t049_main_control.pptx":
                "Byte copy of the T049 one_slide_games_suite.pptx plus one main-sequence "
                "click on slide 1 (pptx_animator.apply_timeline, mode=extend).",
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    (OUT / "fixtures.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
