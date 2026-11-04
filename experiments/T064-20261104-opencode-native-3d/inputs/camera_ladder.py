#!/usr/bin/env python3
"""T064: render a ladder of static camera positions of the same model.

Seven slides, same GLB, same look-at / model rotation / FOV; only the camera x
moves from the probe's view A (-1.2) to view B (+1.2) in 0.4 steps. Each slide
is exported at 1920x1080, the same size as the CreateVideo frames, so the
silhouette of a transition frame can be matched against a known camera.

Run:  python experiments/T064-.../inputs/camera_ladder.py
"""
from __future__ import annotations

import json
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
LADDER = PREVIEW / "ladder"

GLB = HERE / "quickmill-blockout.glb"
PPTX = ART / "camera-ladder.pptx"
LOOK_AT = (0.0, 0.28, 0.0)
ROTATION = (6.0, 0.0, 0.0)
FOV = 40.0
XS = [round(-1.2 + 0.1 * i, 1) for i in range(25)]
Y, Z = 0.45, 2.20
BG = 0x1B140B


def main() -> dict:
    LADDER.mkdir(parents=True, exist_ok=True)
    info = {"glb": str(GLB), "look_at": LOOK_AT, "rotation": ROTATION,
            "fov": FOV, "views": []}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Add()
        pres.PageSetup.SlideWidth = 960
        pres.PageSetup.SlideHeight = 540
        for i, x in enumerate(XS, start=1):
            slide = pres.Slides.Add(i, 12)
            slide.FollowMasterBackground = False
            slide.Background.Fill.ForeColor.RGB = BG
            shape = slide.Shapes.Add3DModel(str(GLB.resolve()), 0, -1, 0, 9, 500, 490)
            shape.Name = "Product3D"
            m = shape.Model3D
            m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = x, Y, Z
            m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = LOOK_AT
            m.FieldOfView = FOV
            m.RotationX, m.RotationY, m.RotationZ = ROTATION
            info["views"].append({"slide": i, "camera": [x, Y, Z]})
        pres.SaveAs(str(PPTX.resolve()))
        for i in range(1, pres.Slides.Count + 1):
            png = LADDER / f"cam-{XS[i - 1]:+.1f}.png"
            pres.Slides(i).Export(str(png.resolve()), "PNG", 1920, 1080)
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass
    (PREVIEW / "camera-ladder.json").write_text(json.dumps(info, indent=2),
                                                encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    main()
