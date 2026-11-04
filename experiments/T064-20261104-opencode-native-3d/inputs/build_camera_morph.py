#!/usr/bin/env python3
"""T064: build a two-slide deck whose only difference is the 3D camera.

Both slides embed the same GLB (SHA-256 pinned, T055 artifact) in the same
position and size, with the same shape name, so PowerPoint Morph has an object
identity to match. Slide 1 shows the model from the left three-quarter view,
slide 2 from the right three-quarter view. Every other object (background,
rule, caption) is identical, so any pixel change during the transition comes
from the camera.

Run:  python experiments/T064-.../inputs/build_camera_morph.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = EXP.parents[1]
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"

GLB = HERE / "quickmill-blockout.glb"
GLB_SHA256 = "fd252d7c6e2470b9809766d9dcba0bbd546c8169209b7426ea6ceb363f959143"
PPTX = ART / "camera-morph-base.pptx"

# Two authored camera views of the same model. Only the eye moves; the model
# rotation and look-at point are identical, so an interpolated frame must show
# a single model seen from an in-between angle.
VIEWS = [
    {"name": "A_left_three_quarter", "camera": (-1.20, 0.45, 2.20)},
    {"name": "B_right_three_quarter", "camera": (1.20, 0.45, 2.20)},
]
LOOK_AT = (0.0, 0.28, 0.0)
ROTATION = (6.0, 0.0, 0.0)
FOV = 40.0

BG = 0x1B140B      # 0xBBGGRR -> #0B141B
AMBER = 0x329AD7   # #D79A32
WHITE = 0xF6EFF2   # #F2EFF6
MUTED = 0xAFA393   # #93A3AF


def main() -> dict:
    actual = hashlib.sha256(GLB.read_bytes()).hexdigest()
    if actual != GLB_SHA256:
        raise SystemExit(f"GLB hash changed: {actual}")

    info = {"glb": {"path": str(GLB), "sha256": actual,
                    "bytes": GLB.stat().st_size}, "views": []}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Add()
        pres.PageSetup.SlideWidth = 960
        pres.PageSetup.SlideHeight = 540
        for i, view in enumerate(VIEWS, start=1):
            slide = pres.Slides.Add(i, 12)
            slide.FollowMasterBackground = False
            slide.Background.Fill.ForeColor.RGB = BG

            shape = slide.Shapes.Add3DModel(str(GLB.resolve()), 0, -1, 0, 9, 500, 490)
            shape.Name = "Product3D"
            shape.AlternativeText = ("T064 camera Morph probe. Same embedded model on "
                                     "both slides; only the camera differs.")
            m = shape.Model3D
            cx, cy, cz = view["camera"]
            m.CameraPositionX, m.CameraPositionY, m.CameraPositionZ = cx, cy, cz
            m.LookAtPointX, m.LookAtPointY, m.LookAtPointZ = LOOK_AT
            m.FieldOfView = FOV
            m.RotationX, m.RotationY, m.RotationZ = ROTATION

            # Identical objects on both slides: a rule, a caption, a slide tab.
            rule = slide.Shapes.AddLine(556, 120, 912, 120)
            rule.Line.ForeColor.RGB = AMBER
            rule.Line.Weight = 1.0

            cap = slide.Shapes.AddTextbox(1, 556, 140, 356, 60)
            tr = cap.TextFrame.TextRange
            tr.Text = "CAMERA MORPH PROBE"
            tr.Font.Name = "Consolas"
            tr.Font.Size = 14
            tr.Font.Bold = True
            tr.Font.Color.RGB = WHITE

            sub = slide.Shapes.AddTextbox(1, 556, 176, 356, 80)
            tr = sub.TextFrame.TextRange
            tr.Text = ("Two views, one model, one object name.\n"
                       "If Morph animates the camera, the frames show one model\n"
                       "from an in-between angle. If it fades, the frames show\n"
                       "two models ghosted over each other.")
            tr.Font.Name = "Calibri"
            tr.Font.Size = 11
            tr.Font.Color.RGB = MUTED

            foot = slide.Shapes.AddTextbox(1, 30, 518, 700, 14)
            tr = foot.TextFrame.TextRange
            tr.Text = "T064  ·  NATIVE 3D  ·  MORPH  ·  CREATEVIDEO"
            tr.Font.Name = "Consolas"
            tr.Font.Size = 7.5
            tr.Font.Color.RGB = MUTED

            # Morph control: a plain 2D shape with the same name on both slides.
            # If Morph is really playing, this square travels smoothly; if the
            # whole transition were a fallback, two squares would cross-fade.
            sq = slide.Shapes.AddShape(1, 300 if i == 1 else 860, 26, 60, 60)
            sq.Name = "ProbeSquare"
            sq.Fill.Visible = False
            sq.Line.ForeColor.RGB = AMBER
            sq.Line.Weight = 2.0
            info.setdefault("probe_square", []).append(
                {"slide": i, "name": sq.Name, "left": sq.Left, "top": sq.Top,
                 "width": sq.Width, "height": sq.Height})

            info["views"].append({
                "slide": i, "label": view["name"],
                "shape": shape.Name, "type": shape.Type, "id": shape.Id,
                "camera": [round(m.CameraPositionX, 3), round(m.CameraPositionY, 3),
                           round(m.CameraPositionZ, 3)],
                "look_at": [round(m.LookAtPointX, 3), round(m.LookAtPointY, 3),
                            round(m.LookAtPointZ, 3)],
                "rotation": [m.RotationX, m.RotationY, m.RotationZ],
                "fov": m.FieldOfView,
            })

        pres.SaveAs(str(PPTX.resolve()))
        PREVIEW.mkdir(parents=True, exist_ok=True)
        for i in range(1, pres.Slides.Count + 1):
            pres.Slides(i).Export(str((PREVIEW / f"view-{i}.png").resolve()),
                                  "PNG", 1600, 900)
        info["pptx"] = str(PPTX)
        info["bytes"] = PPTX.stat().st_size
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass

    (PREVIEW / "build-camera-morph.json").write_text(
        json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    main()
