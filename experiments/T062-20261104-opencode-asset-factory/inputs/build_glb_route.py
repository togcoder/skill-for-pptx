#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - route C: the part table extruded into one GLB.

Each art polygon becomes a prism at its own depth, assembled into one glTF
scene, then inserted with PowerPoint's ``Shapes.Add3DModel`` (the T055 route).
Text parts cannot be turned into geometry, so they are dropped here and would
have to be baked into a texture - the report records that as a cost.

Not a product path.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route_stage as stage  # noqa: E402

# z and thickness, in slide points, per part. Derived from the flat art's own
# stacking intent: the body is 7 pt thick, every UI mark sits on the glass.
# art-shadow and art-badge-glow are excluded: they are 2D compositing tricks
# (soft-edged alpha) that a lit 3D renderer cannot reproduce - a disc at z=0
# renders as a black plate under the model.
DEPTHS = {
    "art-back": (0.0, 5.0),
    "art-body": (5.0, 7.0),
    "art-screen": (12.0, 0.8),
    "art-notch": (12.8, 0.8),
    "art-topbar": (12.8, 0.8),
    "art-baseline": (12.8, 0.6),
    "art-bar-1": (12.8, 1.2),
    "art-bar-2": (12.8, 1.2),
    "art-bar-3": (12.8, 1.2),
    "art-bar-4": (12.8, 1.2),
    "art-bar-5": (12.8, 1.2),
    "art-badge-glow": (18.0, 0.2),
    "art-badge-ring": (18.0, 3.0),
    "art-badge-bolt": (21.0, 1.0),
}
SKIP_IN_3D = {"art-shadow", "art-badge-glow"}


def rounded_rect(x, y, w, h, r):
    base = box(x, y, x + w, y + h)
    if not r:
        return base
    r = min(r, min(w, h) / 2)
    if abs(r - min(w, h) / 2) < 1e-6:
        # radius == half the short side: a stadium, not a rounded rectangle
        from shapely.geometry import LineString

        if w >= h:
            spine = LineString([(x + r, y + h / 2), (x + w - r, y + h / 2)])
        else:
            spine = LineString([(x + w / 2, y + r), (x + w / 2, y + h - r)])
        return spine.buffer(r, cap_style=1, quad_segs=24)
    return base.buffer(-r, join_style=1, resolution=12).buffer(r, join_style=1, resolution=12)


def ellipse(x, y, w, h):
    return Point(x + w / 2, y + h / 2).buffer(max(w, h) / 2, quad_segs=48)


def _rgba(part: dict, theme: dict, scale: float = 1.0) -> list[float]:
    hex_value = theme[part["fill"]["color"]] if part["fill"]["color"] in theme else part["fill"]["color"]
    hex_value = hex_value.lstrip("#")
    return [min(1.0, int(hex_value[i:i + 2], 16) / 255 * scale) for i in (0, 2, 4)] + [1.0]


def profile(part: dict, hole: dict | None) -> Polygon:
    if part["kind"] in ("rect", "roundRect"):
        shape = rounded_rect(*part["rect"], part.get("radius_pt", 0))
    elif part["kind"] == "ellipse":
        shape = ellipse(*part["rect"])
        if hole is not None:
            shape = shape.difference(ellipse(*hole["rect"]))
    elif part["kind"] == "polygon":
        shape = Polygon(part["polygon"])
    else:
        raise ValueError(part["kind"])
    if not shape.is_valid:
        shape = shape.buffer(0)
    return orient(shape, 1.0)


def build_glb(spec_path: Path, out_glb: Path, colour_scale: float = 1.0) -> dict:
    spec, theme = stage.load(spec_path)
    asset = spec["asset"]["native_art"]
    merged = {}
    helpers = set()
    for op in asset.get("ops", []):
        merge = op["merge"]
        merged[merge["name"]] = next(p for p in asset["parts"] if p["name"] == merge["ids"][1])
        helpers.update(n for n in merge["ids"] if n != merge["name"])
    by_name = {p["name"]: p for p in asset["parts"]}

    meshes, dropped = [], []
    for part in stage.art_parts(asset):
        if part["kind"] == "text":
            dropped.append(part["name"])
            continue
        if part["name"] in helpers or part["name"] in SKIP_IN_3D:
            continue
        z, depth = DEPTHS.get(part["name"], (0.0, 2.0))
        poly = profile(part, merged.get(part["name"]))
        mesh = trimesh.creation.extrude_polygon(poly, height=depth)
        mesh.apply_translation((0, 0, z))
        # glTF is Y-up: slide x -> x, slide y -> -y, slide z -> z.
        mesh.apply_scale((1, -1, 1))
        mesh.visual = trimesh.visual.TextureVisuals(
            material=trimesh.visual.material.PBRMaterial(
                name=part["name"],
                baseColorFactor=_rgba(part, theme, colour_scale),
                metallicFactor=0.0,
                roughnessFactor=0.55,
                alphaMode="BLEND" if part.get("fill", {}).get("transparency") else "OPAQUE",
                alphaCutoff=0.5,
            )
        )
        mesh.metadata["name"] = part["name"]
        meshes.append(mesh)

    scene = trimesh.Scene()
    for mesh in meshes:
        scene.add_geometry(mesh, geom_name=mesh.metadata["name"], node_name=mesh.metadata["name"])
    bounds = scene.bounds
    centre = (bounds[0] + bounds[1]) / 2
    scene.apply_translation([-centre[0], -centre[1], -bounds[0][2]])
    out_glb.parent.mkdir(parents=True, exist_ok=True)
    out_glb.write_bytes(scene.export(file_type="glb"))
    return {
        "glb": str(out_glb),
        "bytes": out_glb.stat().st_size,
        "meshes": len(meshes),
        "dropped_text_parts": dropped,
        "bounds": [[round(v, 2) for v in row] for row in scene.bounds.tolist()],
    }


def insert_in_powerpoint(base_pptx: Path, glb: Path, out_pptx: Path, rect: list[float],
                         rot: tuple[float, float], cam: tuple[float, float, float],
                         png: Path | None = None) -> dict:
    import win32com.client as win32

    app = win32.Dispatch("PowerPoint.Application")
    app.Visible = True
    presentation = app.Presentations.Open(str(base_pptx.resolve()), WithWindow=False)
    try:
        slide = presentation.Slides(1)
        # Signature: (FileName, LinkToFile, SaveWithDocument, Left, Top, Width, Height)
        shape = slide.Shapes.Add3DModel(str(glb.resolve()), False, True, rect[0], rect[1], rect[2], rect[3])
        model = shape.Model3D
        model.CameraPositionX, model.CameraPositionY, model.CameraPositionZ = cam
        model.RotationX, model.RotationY, model.RotationZ = rot[0], rot[1], 0.0
        shape.Name = "art-field-terminal-3d"
        presentation.SaveAs(str(out_pptx.resolve()))
        if png is not None:
            png.parent.mkdir(parents=True, exist_ok=True)
            slide.Export(str(png.resolve()), "PNG", 1920, 1080)
        info = {
            "shape": shape.Name,
            "type": int(shape.Type),
            "camera": [model.CameraPositionX, model.CameraPositionY, model.CameraPositionZ],
            "rotation": [model.RotationX, model.RotationY, model.RotationZ],
            "frame": [shape.Left, shape.Top, shape.Width, shape.Height],
        }
    finally:
        presentation.Close()
        app.Quit()
    return info


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rot-y", type=float, default=-18.0)
    parser.add_argument("--rot-x", type=float, default=6.0)
    parser.add_argument("--cam-scale", type=float, default=3.2, help="camera distance / model height")
    parser.add_argument("--frame-scale", type=float, default=1.0, help="3D frame vs the flat art bbox")
    parser.add_argument("--colour-scale", type=float, default=1.0, help="pre-compensate the fixed 3D light rig")
    parser.add_argument("--export-png", type=Path, default=None, help="also export the slide at 1920x1080")
    args = parser.parse_args(argv)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    glb_info = build_glb(args.spec, out / "field-terminal-art.glb", args.colour_scale)

    spec, theme = stage.load(args.spec)
    asset = spec["asset"]["native_art"]
    art = [p for p in stage.art_parts(asset) if p["name"] not in SKIP_IN_3D and p.get("rect")]
    xs = [p["rect"][0] for p in art] + [p["rect"][0] + p["rect"][2] for p in art]
    ys = [p["rect"][1] for p in art] + [p["rect"][1] + p["rect"][3] for p in art]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = (max(xs) - min(xs)) * args.frame_scale, (max(ys) - min(ys)) * args.frame_scale
    rect = [cx - w / 2, cy - h / 2, w, h]

    base = out / "route-c-stage.pptx"
    stage.build_stage(args.spec, base)

    bounds = glb_info["bounds"]
    height = bounds[1][1] - bounds[0][1]
    # PowerPoint normalises the model: the default camera distance is ~1.49
    # whatever the GLB's own units, so the camera is set in that space too.
    cam = (-0.34, 0.20, 1.45)
    info = insert_in_powerpoint(base, out / "field-terminal-art.glb",
                                out / f"{spec['asset']['id']}-routeC.pptx", rect,
                                (args.rot_x, args.rot_y), cam, args.export_png)
    result = {**glb_info, "pptx": str(out / f"{spec['asset']['id']}-routeC.pptx"), **info,
              "pptx_bytes": (out / f"{spec['asset']['id']}-routeC.pptx").stat().st_size}
    (out / "route-c.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
