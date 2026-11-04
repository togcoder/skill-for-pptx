#!/usr/bin/env python3
"""Calibration: does PowerPoint's native 3D renderer show glTF textures?"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import trimesh
import win32com.client as win32
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
PREVIEW = HERE.parent / "preview"

# A texture with unmistakable quadrants and text.
tex = Image.new("RGB", (512, 512), (230, 220, 200))
d = ImageDraw.Draw(tex)
d.rectangle([0, 0, 255, 255], fill=(200, 40, 40))
d.rectangle([256, 0, 511, 255], fill=(40, 160, 70))
d.rectangle([0, 256, 255, 511], fill=(40, 80, 200))
d.rectangle([256, 256, 511, 511], fill=(230, 180, 40))
d.text((210, 230), "TEX", fill=(255, 255, 255))
tex_path = ART / "calib-texture.png"
tex.save(tex_path)

mesh = trimesh.creation.box(extents=[0.4, 0.4, 0.4])
mesh.apply_translation([0, 0.2, 0])
mesh.unmerge_vertices()

# Planar UVs per face, normalised to 0..1.
uv = np.zeros((len(mesh.vertices), 2))
for face in mesh.faces:
    pts = mesh.vertices[face]
    normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    normal /= np.linalg.norm(normal)
    e1 = pts[1] - pts[0]
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(normal, e1)
    local = np.array([[np.dot(p - pts[0], e1), np.dot(p - pts[0], e2)] for p in pts])
    lo, hi = local.min(axis=0), local.max(axis=0)
    local = (local - lo) / np.maximum(hi - lo, 1e-9)
    for k, vi in enumerate(face):
        uv[vi] = local[k]

material = PBRMaterial(name="quadrants", baseColorTexture=tex,
                       metallicFactor=0.0, roughnessFactor=0.55)
mesh.visual = TextureVisuals(uv=uv, material=material)
glb = ART / "calib-texture.glb"
mesh.export(glb)
print("glb", glb, glb.stat().st_size)

ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Add()
    pres.PageSetup.SlideWidth = 960
    pres.PageSetup.SlideHeight = 540
    slide = pres.Slides.Add(1, 12)
    slide.FollowMasterBackground = False
    slide.Background.Fill.ForeColor.RGB = 0x20170E
    shape = slide.Shapes.Add3DModel(str(glb.resolve()), 0, -1, 280, 80, 400, 400)
    m = shape.Model3D
    m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = -0.25, 0.35, 1.8
    m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = 0, 0.2, 0
    m.FieldOfView = 40.0
    m.RotationX, m.RotationY, m.RotationZ = 8.0, -20.0, 0.0
    pptx = ART / "calib-texture.pptx"
    png = PREVIEW / "calib-texture.png"
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
