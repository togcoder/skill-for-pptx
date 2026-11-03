#!/usr/bin/env python3
"""Native audit of the T055 v3 deck: reopen in PowerPoint, count 3D shapes,
read cameras back, export PDF, inspect the embedded GLBs."""
from __future__ import annotations

import json
import struct
import zipfile
from pathlib import Path

import trimesh
import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
PPTX = ART / "quickmill_native_product_tour_v3.pptx"
PDF = PREVIEW / "quickmill_native_product_tour_v3.pdf"
JSON = PREVIEW / "native-audit-v3.json"

info = {"pptx": str(PPTX), "slides": [], "package": {}, "glb": []}
ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Open(str(PPTX.resolve()), WithWindow=False)
    info["slide_count"] = pres.Slides.Count
    info["slide_width"] = pres.PageSetup.SlideWidth
    info["slide_height"] = pres.PageSetup.SlideHeight
    for i in range(1, pres.Slides.Count + 1):
        slide = pres.Slides(i)
        rec = {"index": i, "shapes": slide.Shapes.Count, "models": [], "texts": []}
        for j in range(1, slide.Shapes.Count + 1):
            sh = slide.Shapes(j)
            if sh.Type == 30:
                m = sh.Model3D
                rec["models"].append({
                    "name": sh.Name, "type": sh.Type, "id": sh.Id,
                    "camera": [round(m.CameraPositionX, 4), round(m.CameraPositionY, 4),
                               round(m.CameraPositionZ, 4)],
                    "look_at": [round(m.LookAtPointX, 4), round(m.LookAtPointY, 4),
                                round(m.LookAtPointZ, 4)],
                    "rotation": [round(m.RotationX, 2), round(m.RotationY, 2),
                                 round(m.RotationZ, 2)],
                    "fov": m.FieldOfView,
                    "alt_text": sh.AlternativeText,
                })
            if sh.HasTextFrame and sh.TextFrame.HasText:
                t = sh.TextFrame.TextRange.Text.strip().replace("\r", " ")
                if t:
                    rec["texts"].append(t)
        info["slides"].append(rec)
    pres.SaveAs(str(PDF.resolve()), 32)  # ppSaveAsPDF
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass

with zipfile.ZipFile(PPTX) as z:
    names = z.namelist()
    media = [n for n in names if n.startswith("ppt/media/")]
    glbs = [n for n in media if n.endswith(".glb")]
    info["package"] = {
        "media": media,
        "model_glb": glbs,
        "slides": [n for n in names if n.startswith("ppt/slides/slide")
                   and n.endswith(".xml")],
    }
    for n in glbs:
        raw = z.read(n)
        jlen = struct.unpack("<I", raw[12:16])[0]
        gltf = json.loads(raw[20:20 + jlen])
        tmp = PREVIEW / f"_{Path(n).name}"
        tmp.write_bytes(raw)
        scene = trimesh.load(str(tmp), force="scene")
        bounds = scene.bounds
        info["glb"].append({
            "name": n, "bytes": len(raw),
            "meshes": len(gltf.get("meshes", [])),
            "materials": len(gltf.get("materials", [])),
            "metallic": sorted({m.get("pbrMetallicRoughness", {}).get("metallicFactor")
                                for m in gltf.get("materials", [])}),
            "bounds_m": [[round(float(v), 4) for v in row] for row in bounds],
        })
        tmp.unlink(missing_ok=True)

info["pdf"] = str(PDF)
JSON.write_text(json.dumps(info, indent=2), encoding="utf-8")
print(json.dumps({k: info[k] for k in ("slide_count", "package", "glb")}, indent=2))
print("pdf", PDF.exists(), PDF.stat().st_size if PDF.exists() else 0)
print("slides", json.dumps(info["slides"], indent=1)[:1200])
