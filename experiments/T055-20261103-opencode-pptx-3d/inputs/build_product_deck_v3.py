#!/usr/bin/env python3
"""T055 final spike: a three-slide, PowerPoint-native 3D product study.

The model is an embedded GLB. Every callout, focus box, rule, spec row and
footer is a native PowerPoint object, so the deck stays editable. The three
slides use the same three-quarter camera and move a native focus box to the
feature under discussion, which is the honest way to annotate a 3D model whose
projection changes when the audience rotates it.
"""
from __future__ import annotations

import json
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
GLB = ART / "quickmill-blockout.glb"
PPTX = ART / "quickmill_native_product_tour_v3.pptx"

# COM colours are 0xBBGGRR.
def rgb(hexv: str) -> int:
    h = hexv.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return r | (g << 8) | (b << 16)

BG = rgb("#0B141B")
GLOW = rgb("#17303F")
WHITE = rgb("#F2EFE6")
MUTED = rgb("#93A3AF")
AMBER = rgb("#D79A32")
LINE = rgb("#243642")
GHOST = rgb("#142430")
INK = rgb("#0A1117")

# Common camera: left three-quarter, front features readable, yellow tower visible.
CAM = (-0.85, 0.45, 2.10, 0.0, 0.28, 0.0, 40.0, 6.0, 0.0)

VIEWS = [
    {
        "kicker": "01 / STRUCTURE",
        "title": "A black bay,\na chrome lid.",
        "body": "The black housing wraps the brewing bay. The chrome lid overhangs it; "
                "the left tower is the only yellow volume.",
        "specs": [("HEIGHT", "553 mm"), ("WIDTH", "400 mm"), ("DEPTH", "326 mm")],
        "label": "TOP HOUSING",
        "caption": "80 mm black massing. The bay soffit is part of the same volume.",
        "focus": (252, 234, 148, 46),
        "chip": (256, 240),
        "tab": "01",
        "number": "01",
    },
    {
        "kicker": "02 / BREWING BAY",
        "title": "The group sits\ninside the mass.",
        "body": "A 229 × 121 × 211 mm recess holds the group head and portafilter. "
                "The steam wand enters from the right.",
        "specs": [("BAY", "229 × 121 × 211 mm"), ("GROUP HEAD", "Ø100 mm"),
                  ("BASKET", "Ø88 mm")],
        "label": "GROUP HEAD",
        "caption": "Ø100 mm, 60 mm deep. The portafilter projects into the bay.",
        "focus": (292, 280, 64, 76),
        "tab": "02",
        "number": "02",
    },
    {
        "kicker": "03 / CONTROLS",
        "title": "Three switches,\none cast base.",
        "body": "The switch plate sits on the lower front-left. The tray is a 31 mm "
                "recess under a black grate; the base is a single dark casting.",
        "specs": [("TRAY", "340 × 240 mm"), ("SWITCH PLATE", "120 × 82 mm"),
                  ("BASE", "400 × 320 mm")],
        "label": "SWITCH PLATE",
        "caption": "Three 18 × 50 mm rockers on a 120 × 82 mm plate.",
        "focus": (182, 434, 62, 50),
        "tab": "03",
        "number": "03",
    },
]


def text(slide, x, y, w, h, value, size, color, font="Calibri", bold=False,
         align=1):
    box = slide.Shapes.AddTextbox(1, x, y, w, h)
    tr = box.TextFrame.TextRange
    tr.Text = value
    tr.Font.Name = font
    tr.Font.Size = size
    tr.Font.Bold = bold
    tr.Font.Color.RGB = color
    tr.ParagraphFormat.Alignment = align
    box.TextFrame.MarginLeft = 0
    box.TextFrame.MarginRight = 0
    box.TextFrame.MarginTop = 0
    box.TextFrame.MarginBottom = 0
    return box


def rect(slide, x, y, w, h, fill=None, line=None, weight=0.75):
    shape = slide.Shapes.AddShape(1, x, y, w, h)
    if fill is None:
        shape.Fill.Visible = False
    else:
        shape.Fill.ForeColor.RGB = fill
        shape.Fill.Visible = True
    if line is None:
        shape.Line.Visible = False
    else:
        shape.Line.ForeColor.RGB = line
        shape.Line.Weight = weight
        shape.Line.Visible = True
    return shape


def line(slide, x1, y1, x2, y2, color, weight=1.0, dash=None):
    shp = slide.Shapes.AddLine(x1, y1, x2, y2)
    shp.Line.ForeColor.RGB = color
    shp.Line.Weight = weight
    if dash is not None:
        shp.Line.DashStyle = dash
    return shp


def focus_box(slide, x, y, w, h, tab, chip_pos=None):
    """Corner ticks + a numbered tab, not a full rectangle."""
    tick = 14
    gap = 3
    for sx, sy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1),
                           (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        line(slide, sx - dx * gap, sy - dy * gap,
             sx - dx * gap + dx * tick, sy - dy * gap, AMBER, 1.5)
        line(slide, sx - dx * gap, sy - dy * gap,
             sx - dx * gap, sy - dy * gap + dy * tick, AMBER, 1.5)
    cx, cy = chip_pos if chip_pos else (x - gap, y - 20)
    chip = rect(slide, cx, cy, 22, 16, AMBER, None)
    tf = chip.TextFrame.TextRange
    tf.Text = tab
    tf.Font.Name = "Consolas"
    tf.Font.Size = 8
    tf.Font.Bold = True
    tf.Font.Color.RGB = INK
    chip.TextFrame.MarginLeft = 0
    chip.TextFrame.MarginRight = 0
    chip.TextFrame.MarginTop = 0
    chip.TextFrame.MarginBottom = 0
    tf.ParagraphFormat.Alignment = 2


def build() -> dict:
    info = {"views": [], "pptx": str(PPTX)}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Add()
        pres.PageSetup.SlideWidth = 960
        pres.PageSetup.SlideHeight = 540
        for i, v in enumerate(VIEWS, start=1):
            slide = pres.Slides.Add(i, 12)
            slide.FollowMasterBackground = False
            slide.Background.Fill.ForeColor.RGB = BG

            # Stage: a soft radial glow behind the model, plus a floor line.
            glow = slide.Shapes.AddShape(9, -40, 40, 560, 520)
            glow.Fill.TwoColorGradient(7, 1)  # from centre
            stops = glow.Fill.GradientStops
            stops(1).Color.RGB = GLOW
            stops(1).Transparency = 0.0
            stops(1).Position = 0.0
            stops(2).Color.RGB = BG
            stops(2).Transparency = 0.0
            stops(2).Position = 1.0
            glow.Line.Visible = False
            glow.Shadow.Visible = False

            floor = line(slide, 40, 498, 500, 498, LINE, 0.75)
            floor.Line.DashStyle = 4  # dash

            # Native 3D model.
            shape = slide.Shapes.Add3DModel(str(GLB.resolve()), 0, -1, 0, 9, 500, 490)
            shape.Name = "Product3D"
            shape.AlternativeText = ("Embedded 3D model of the Quick Mill Omre massing "
                                     "study. Drag to rotate in PowerPoint.")
            m = shape.Model3D
            cx, cy, cz, lx, ly, lz, fov, rx, ry = CAM
            m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = cx, cy, cz
            m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = lx, ly, lz
            m.FieldOfView = fov
            m.RotationX, m.RotationY, m.RotationZ = rx, ry, 0.0

            # Focus box and chip.
            fx, fy, fw, fh = v["focus"]
            focus_box(slide, fx, fy, fw, fh, v["tab"], v.get("chip"))

            # Top rule, brand and right column.
            rect(slide, 0, 0, 960, 2, AMBER, None)
            text(slide, 30, 18, 220, 12, "QUICK MILL", 8, WHITE, "Consolas", True)
            text(slide, 30, 31, 260, 12, "OMRE  /  MASSING STUDY", 7.5,
                 MUTED, "Consolas")
            text(slide, 556, 92, 360, 16, v["kicker"], 8.5, AMBER, "Consolas", True)
            text(slide, 556, 116, 380, 78, v["title"], 26, WHITE, "Georgia", False)
            text(slide, 556, 202, 356, 62, v["body"], 10.5, MUTED, "Calibri")

            # Spec rows.
            y = 282
            for label, value in v["specs"]:
                text(slide, 556, y, 150, 12, label, 7.5, MUTED, "Consolas", True)
                text(slide, 556, y + 13, 356, 18, value, 12.5, WHITE, "Calibri")
                line(slide, 556, y + 34, 912, y + 34, LINE, 0.5)
                y += 44

            # Callout legend.
            text(slide, 556, 424, 22, 14, v["tab"], 8, AMBER, "Consolas", True)
            text(slide, 580, 424, 332, 14, v["label"], 8, WHITE, "Consolas", True)
            text(slide, 556, 442, 356, 34, v["caption"], 9, MUTED, "Calibri")

            # Ghost number and footer.
            text(slide, 820, 24, 110, 70, v["number"], 48, GHOST, "Georgia", True,
                 align=3)
            text(slide, 30, 518, 620, 14,
                 "NATIVE 3D  ·  EMBEDDED GLB  ·  EDITABLE CALLOUTS", 7.5,
                 MUTED, "Consolas")
            text(slide, 780, 518, 150, 14, "ROTATE IN POWERPOINT", 7.5,
                 MUTED, "Consolas", align=3)

            info["views"].append({
                "slide": i, "shape": shape.Name, "type": shape.Type,
                "camera": [m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ],
                "look_at": [m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ],
                "rotation": [m.RotationX, m.RotationY, m.RotationZ],
                "fov": m.FieldOfView,
                "focus_box": [fx, fy, fw, fh],
                "label": v["label"],
            })

        pres.SaveAs(str(PPTX.resolve()))
        for i in range(1, pres.Slides.Count + 1):
            png = PREVIEW / f"tour-v3-{i}.png"
            pres.Slides(i).Export(str(png.resolve()), "PNG", 1600, 900)
        info["bytes"] = PPTX.stat().st_size
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass
    (PREVIEW / "tour-v3-manifest.json").write_text(json.dumps(info, indent=2),
                                                    encoding="utf-8")
    return info


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
