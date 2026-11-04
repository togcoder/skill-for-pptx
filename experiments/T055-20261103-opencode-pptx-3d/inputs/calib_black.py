#!/usr/bin/env python3
"""Calibration: how does PowerPoint light a rough black glTF cube?"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh
import win32com.client as win32
from trimesh.visual import ColorVisuals
from trimesh.visual.material import PBRMaterial

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
PREVIEW = HERE.parent / "preview"
color = np.array([14, 16, 19, 255], dtype=np.uint8)

mesh = trimesh.creation.box(extents=[0.4, 0.4, 0.4])
mesh.apply_translation([0, 0.2, 0])
mesh.visual = ColorVisuals(mesh=mesh, face_colors=np.tile(color, (len(mesh.faces), 1)))
mesh.visual.material = PBRMaterial(name="black", baseColorFactor=color / 255.0,
                                   metallicFactor=0.0, roughnessFactor=0.82)
glb = ART / "calib-black.glb"
mesh.export(glb)

ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Add()
    pres.PageSetup.SlideWidth = 960
    pres.PageSetup.SlideHeight = 540
    slide = pres.Slides.Add(1, 12)
    slide.FollowMasterBackground = False
    slide.Background.Fill.ForeColor.RGB = 0x20170E  # BGR for #0E1720
    shape = slide.Shapes.Add3DModel(str(glb.resolve()), 0, -1, 280, 80, 400, 400)
    m = shape.Model3D
    m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = -0.25, 0.35, 1.8
    m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = 0, 0.2, 0
    m.FieldOfView = 40.0
    m.RotationX, m.RotationY, m.RotationZ = 8.0, -20.0, 0.0
    pptx = ART / "calib-black.pptx"
    png = PREVIEW / "calib-black.png"
    pres.SaveAs(str(pptx.resolve()))
    slide.Export(str(png.resolve()), "PNG", 1280, 720)
    print("saved", pptx, png)
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass
