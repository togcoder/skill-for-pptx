#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - the shared stage for the three illustration routes.

Builds the same 960x540 slide (background + native copy) with python-pptx so
that route A (DeckCraft native shapes), route B (one SVG picture) and route C
(one GLB model) differ only in how the *art* is represented. Copy stays native
in all three, which is what Forge would ship.

Not a product path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_native_art as bn  # noqa: E402  (theme + pacing authority)


def rgb(value: str, theme: dict) -> RGBColor:
    return RGBColor.from_string(bn.colour(value, theme))


def load(spec_path: Path) -> tuple[dict, dict]:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    asset = spec["asset"]["native_art"]
    return spec, bn.load_theme(asset["stage"]["theme"])


def art_parts(asset: dict) -> list[dict]:
    return [p for p in asset["parts"] if p["role"] == "art"]


def new_deck(asset: dict, theme: dict) -> Presentation:
    prs = Presentation()
    prs.slide_width = Pt(asset["stage"]["size"][0])
    prs.slide_height = Pt(asset["stage"]["size"][1])
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = rgb(asset["stage"]["background"], theme)
    return prs


def _set_spacing(run, points: float) -> None:
    run.font._rPr.set("spc", str(int(round(points * 100))))


def add_copy(slide, asset: dict, theme: dict) -> list[str]:
    """The slide copy (rule + text). Native in every route; returns shape names."""
    names = []
    for part in asset["parts"]:
        if part["role"] != "copy":
            continue
        x, y, w, h = part["rect"]
        if part["kind"] == "rect":
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb(part["fill"]["color"], theme)
            shape.line.fill.background()
            shape.shadow.inherit = False
        elif part["kind"] == "text":
            text = part["text"]["value"].replace("{art_parts}", str(len(art_parts(asset))))
            shape = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
            frame = shape.text_frame
            frame.word_wrap = True
            frame.auto_size = MSO_AUTO_SIZE.NONE
            frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
            frame.vertical_anchor = MSO_ANCHOR.TOP
            for index, line in enumerate(text.split("\n")):
                paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
                paragraph.line_spacing = part["text"].get("line_spacing", 1.0)
                paragraph.alignment = PP_ALIGN.CENTER if part["text"].get("align") == "center" else PP_ALIGN.LEFT
                run = paragraph.add_run()
                run.text = line
                run.font.name = asset.get("font", "Segoe UI")
                run.font.size = Pt(part["text"]["size_pt"])
                run.font.bold = bool(part["text"].get("bold"))
                run.font.color.rgb = rgb(part["text"].get("color", "text"), theme)
                if part["text"].get("spacing_pt") is not None:
                    _set_spacing(run, part["text"]["spacing_pt"])
        else:
            raise ValueError(f"copy part {part['name']} has kind {part['kind']}")
        shape.name = part["name"]
        names.append(part["name"])
    return names


def build_stage(spec_path: Path, out_pptx: Path) -> tuple[Path, dict]:
    """Background + copy only: the shell route B and C add their art to."""
    spec, theme = load(spec_path)
    asset = spec["asset"]["native_art"]
    prs = new_deck(asset, theme)
    slide = prs.slides[0]
    names = add_copy(slide, asset, theme)
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_pptx)
    return out_pptx, {"copy_shapes": names}


if __name__ == "__main__":
    target, info = build_stage(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps({"stage": str(target), **info}, indent=1))
