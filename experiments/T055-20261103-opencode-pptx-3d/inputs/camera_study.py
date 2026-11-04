#!/usr/bin/env python3
"""Render six camera/rotation candidates for the T055 product deck."""
from __future__ import annotations

import json
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
GLB = ART / "quickmill-blockout.glb"
PPTX = ART / "camera-study.pptx"

VARIANTS = [
    ("A_front_left_near", (-0.25, 0.42, 2.70), (0.0, 0.28, 0.0), (6.0, -20.0, 0.0)),
    ("B_left_three_quarter", (-0.85, 0.45, 2.50), (0.0, 0.28, 0.0), (6.0, 0.0, 0.0)),
    ("C_left_wide", (-1.10, 0.50, 2.30), (0.0, 0.28, 0.0), (8.0, 0.0, 0.0)),
    ("D_turned_model", (-0.25, 0.42, 2.70), (0.0, 0.28, 0.0), (6.0, -45.0, 0.0)),
    ("E_high_left", (-0.25, 0.80, 2.40), (0.0, 0.28, 0.0), (6.0, -20.0, 0.0)),
    ("F_front_right", (0.20, 0.45, 2.50), (0.0, 0.28, 0.0), (6.0, 20.0, 0.0)),
]


def text(slide, x, y, w, h, value, size, color, bold=False):
    box = slide.Shapes.AddTextbox(1, x, y, w, h)
    tr = box.TextFrame.TextRange
    tr.Text = value
    tr.Font.Name = "Calibri"
    tr.Font.Size = size
    tr.Font.Bold = bold
    tr.Font.Color.RGB = color
    box.TextFrame.MarginLeft = 0
    box.TextFrame.MarginRight = 0
    box.TextFrame.MarginTop = 0
    box.TextFrame.MarginBottom = 0
    return box


def main() -> dict:
    info = {"views": []}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Add()
        pres.PageSetup.SlideWidth = 960
        pres.PageSetup.SlideHeight = 540
        for i, (label, cam, look, rot) in enumerate(VARIANTS, start=1):
            slide = pres.Slides.Add(i, 12)
            slide.FollowMasterBackground = False
            slide.Background.Fill.ForeColor.RGB = 0x20170E  # #0E1720
            shape = slide.Shapes.Add3DModel(str(GLB.resolve()), 0, -1, 40, 30, 500, 480)
            shape.Name = "Product3D"
            m = shape.Model3D
            m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = cam
            m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = look
            m.FieldOfView = 40.0
            m.RotationX, m.RotationY, m.RotationZ = rot
            text(slide, 20, 12, 500, 24, label, 12, 0xD79A32, True)
            text(slide, 20, 512, 700, 20,
                 f"cam={cam} look={look} rot={rot}", 8, 0xAAB8C4)
            info["views"].append({"slide": i, "label": label, "camera": cam,
                                  "look_at": look, "rotation": rot})
        pres.SaveAs(str(PPTX.resolve()))
        for i in range(1, pres.Slides.Count + 1):
            png = PREVIEW / f"camera-{VARIANTS[i - 1][0]}.png"
            pres.Slides(i).Export(str(png.resolve()), "PNG", 1200, 675)
        info["pptx"] = str(PPTX)
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass
    (PREVIEW / "camera-study.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
