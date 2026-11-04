#!/usr/bin/env python3
"""T064: does duplicating a slide share the 3D model part?

Variant B/C showed that Morph animates the camera only when both slides point at
one `model3d` part. This probe asks whether a normal authoring move -- duplicate
the slide, then change the camera on the copy -- produces that shared part
without a package patch.

Run:  python experiments/T064-.../inputs/duplicate_slide_probe.py
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"

GLB = HERE / "quickmill-blockout.glb"
BUILT = ART / "camera-morph-duplicated-raw.pptx"
PPTX = ART / "camera-morph-duplicated.pptx"

MORPH_XML = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" '
    'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
    '<mc:Choice Requires="p159 p14">'
    '<p:transition spd="slow" p14:dur="2000">'
    '<p159:morph option="byObject"/>'
    '</p:transition>'
    '</mc:Choice>'
    '<mc:Fallback>'
    '<p:transition spd="slow"><p:fade/></p:transition>'
    '</mc:Fallback>'
    '</mc:AlternateContent>'
)
BG = 0x1B140B


def build() -> dict:
    for stale in (BUILT, PPTX):
        stale.unlink(missing_ok=True)
    info = {}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Add()
        pres.PageSetup.SlideWidth = 960
        pres.PageSetup.SlideHeight = 540
        slide = pres.Slides.Add(1, 12)
        slide.FollowMasterBackground = False
        slide.Background.Fill.ForeColor.RGB = BG
        shape = slide.Shapes.Add3DModel(str(GLB.resolve()), 0, -1, 0, 9, 500, 490)
        shape.Name = "Product3D"
        m = shape.Model3D
        m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = -1.2, 0.45, 2.2
        m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = 0.0, 0.28, 0.0
        m.FieldOfView = 40.0
        m.RotationX, m.RotationY, m.RotationZ = 6.0, 0.0, 0.0

        copy = slide.Duplicate()
        copy.MoveTo(2)
        m2 = copy.Shapes("Product3D").Model3D
        m2.CameraPositionX = 1.2
        info["copy_camera"] = [m2.CameraPositionX, m2.CameraPositionY, m2.CameraPositionZ]
        pres.SaveAs(str(BUILT.resolve()))
        info["raw_bytes"] = BUILT.stat().st_size
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass
    return info


def add_morph() -> dict:
    with zipfile.ZipFile(BUILT) as zin, zipfile.ZipFile(PPTX, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/slide2.xml":
                data = data.decode("utf-8").replace("</p:sld>", MORPH_XML + "</p:sld>").encode("utf-8")
            zout.writestr(item, data)
    with zipfile.ZipFile(PPTX) as z:
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
        r1 = z.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")
        r2 = z.read("ppt/slides/_rels/slide2.xml.rels").decode("utf-8")
    return {"media": media,
            "slide1_model": "model3d1.glb" in r1,
            "slide2_model": "model3d1.glb" in r2,
            "shared_model_part": len([m for m in media if m.endswith(".glb")]) == 1}


if __name__ == "__main__":
    info = build()
    info.update(add_morph())
    PREVIEW.mkdir(parents=True, exist_ok=True)
    (PREVIEW / "duplicate-slide.json").write_text(json.dumps(info, indent=2),
                                                  encoding="utf-8")
    print(json.dumps(info, indent=2))
