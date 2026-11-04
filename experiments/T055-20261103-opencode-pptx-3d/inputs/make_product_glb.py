#!/usr/bin/env python3
"""Build the T055 product GLB from the T054 SolidCraft blockout definition.

Why this file exists
--------------------
The SolidCraft OBJ export merges bodies that lack a `usemtl` line (for example
`group_housing` disappears into `chrome_top`), so the GLB is rebuilt from the
canonical `blockout.json` command stream: boxes, cylinders and two boolean cuts.

PowerPoint's native 3D renderer has two hard constraints learned in the T055
spike:
  1. metallic materials become a white mirror under its image-based lighting;
  2. a mesh with a material ignores per-vertex COLOR_0, so a yellow face painted
     into a cream body renders cream.
Every material therefore uses metallicFactor 0, and colour regions are split
into separate meshes with their own material (body / yellow tower / dark bay).
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box, cylinder
from trimesh.visual import ColorVisuals
from trimesh.visual.material import PBRMaterial

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
T054 = Path(r"C:\Users\COMPUTER\AppData\Local\Temp\opencode\skill-for-pptx-T054"
            r"\experiments\T054-20261102-opencode-vector-match\artifacts\blockout.json")

ART.mkdir(parents=True, exist_ok=True)
commands = json.loads(T054.read_text(encoding="utf-8"))["commands"]

# ---------------------------------------------------------------- geometry
bodies: dict[str, trimesh.Trimesh] = {}


def add_box(p: dict) -> trimesh.Trimesh:
    size = [p["length"], p["width"], p["height"]]
    mesh = box(extents=size)
    mesh.apply_translation([p["corner"][i] + size[i] / 2 for i in range(3)])
    return mesh


def add_cylinder(p: dict) -> trimesh.Trimesh:
    r, h = p["radius"], p["height"]
    axis = p["axis"]
    if axis == "Z":
        direction = np.array([0.0, 0.0, 1.0])
    else:
        direction = np.asarray(axis, dtype=float)
    direction = direction / np.linalg.norm(direction)
    mesh = cylinder(radius=r, height=h, sections=64)
    rot = trimesh.geometry.align_vectors([0, 0, 1], direction)
    mesh.apply_transform(rot)
    base = np.asarray(p["base"], dtype=float)
    mesh.apply_translation(base + direction * h / 2)
    return mesh


for cmd in commands:
    name, params = cmd["command"], cmd["params"]
    if name == "solid.box":
        bodies[params["body_name"]] = add_box(params)
    elif name == "solid.cylinder":
        bodies[params["body_name"]] = add_cylinder(params)
    elif name == "solid.combine":
        target = params["target"]
        tools = [bodies.pop(t) for t in params["tools"]]
        if params["operation"] != "cut":
            raise ValueError(params["operation"])
        bodies[target] = trimesh.boolean.difference([bodies[target], *tools])

bodies = {k: v for k, v in bodies.items() if not k.endswith("_cut")}
print("bodies", len(bodies))

# ---------------------------------------------------------------- palette
COLORS = {
    "base": "#17191C",
    "lower_body": "#918E86",
    "upper_core": "#86837B",
    "top_housing": "#16181B",
    "top_chrome_left": "#D5D2C8",
    "chrome_top": "#D5D2C8",
    "group_housing": "#A8A59C",
    "group_head": "#DCDAD2",
    "group_collar": "#9E9C93",
    "basket": "#8E8C84",
    "portafilter_handle": "#111315",
    "steam_wand": "#E8E6DE",
    "steam_grip": "#111315",
    "knob_l": "#D9A21B",
    "knob_r": "#D9A21B",
    "badge": "#EDE4CF",
    "switch_plate": "#1B1D20",
    "tray_grate": "#0C0E10",
    "tray_front_lip": "#BCB9B0",
    "red_light": "#B5322A",
    "steam_valve": "#C9C6BC",
    "switch_1": "#EDE4CF",
    "switch_2": "#EDE4CF",
    "switch_3": "#EDE4CF",
}
YELLOW = "#E0AE2E"
BAY_DARK = "#141619"
TRAY_DARK = "#191B1E"
CHROME = "#8E8C84"
ROUGH = {
    "lower_body": 0.34, "upper_core": 0.36, "chrome_top": 0.34,
    "top_chrome_left": 0.32, "group_head": 0.30, "group_collar": 0.32,
    "basket": 0.38, "steam_wand": 0.30, "steam_valve": 0.32,
    "tray_front_lip": 0.34, "badge": 0.55, "knob_l": 0.42, "knob_r": 0.42,
    "base": 0.82, "top_housing": 0.82, "portafilter_handle": 0.82,
    "steam_grip": 0.82, "switch_plate": 0.82,
}


def rgba(hexv: str) -> np.ndarray:
    h = hexv.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], dtype=np.uint8)


def face_colors(name: str, mesh: trimesh.Trimesh) -> np.ndarray:
    """Per-face colour in source millimetres, before the Y-up transform."""
    colors = np.tile(rgba(COLORS[name]), (len(mesh.faces), 1))
    n = mesh.face_normals
    c = mesh.triangles_center

    if name in {"lower_body", "upper_core", "top_housing"}:
        colors[(n[:, 0] < -0.9) & (c[:, 0] < 1.0)] = rgba(YELLOW)

    if name == "upper_core":
        inside = (
            (c[:, 0] > 151.0) & (c[:, 0] < 382.0)
            & (c[:, 1] > -2.0) & (c[:, 1] < 121.0)
            & (c[:, 2] > 209.0) & (c[:, 2] < 422.0)
        )
        outer_front = (c[:, 1] < 1.0) & (n[:, 1] < -0.9)
        outer_right = (c[:, 0] > 379.0) & (n[:, 0] > 0.9)
        colors[inside & ~outer_front & ~outer_right] = rgba(BAY_DARK)

    if name == "lower_body":
        inside = (
            (c[:, 0] > 19.0) & (c[:, 0] < 361.0)
            & (c[:, 1] > 19.0) & (c[:, 1] < 261.0)
            & (c[:, 2] > 179.0) & (c[:, 2] < 212.0)
        )
        outer_front = (c[:, 1] < 1.0) & (n[:, 1] < -0.9)
        colors[inside & ~outer_front] = rgba(TRAY_DARK)
    return colors


def tag_for(color: np.ndarray, name: str) -> str:
    if np.array_equal(color, rgba(YELLOW)):
        return "yellow"
    if name == "upper_core" and np.array_equal(color, rgba(BAY_DARK)):
        return "bay"
    if name == "lower_body" and np.array_equal(color, rgba(TRAY_DARK)):
        return "tray"
    return "body"


def material(name: str, color: np.ndarray, material_name: str | None = None) -> PBRMaterial:
    return PBRMaterial(
        name=material_name or name,
        baseColorFactor=color / 255.0,
        metallicFactor=0.0,
        roughnessFactor=ROUGH.get(name, 0.62),
    )


# ---------------------------------------------------------------- transform
# SolidCraft: X width, Y depth, Z up (mm). glTF: X right, Y up, Z forward (m).
# Front (-Y in SolidCraft) becomes +Z. Bottom sits on Y=0.
M = np.array([
    [0.001, 0, 0, -0.190],
    [0, 0, 0.001, 0.0],
    [0, -0.001, 0, 0.150],
    [0, 0, 0, 1],
])

scene = trimesh.Scene()
region_summary = []
for name, mesh in bodies.items():
    colors = face_colors(name, mesh)
    unique, inverse = np.unique(colors, axis=0, return_inverse=True)
    for i, color in enumerate(unique):
        index = np.where(inverse == i)[0]
        part = mesh.submesh([index], append=True)
        if isinstance(part, list):
            part = part[0]
        part.apply_transform(M)
        tag = tag_for(color, name)
        part_name = f"{name}_{tag}" if tag != "body" else name
        # Uniform vertex colour as well, so the renderer is correct whether it
        # reads COLOR_0 or the material base colour.
        part.visual = ColorVisuals(mesh=part, face_colors=np.tile(color, (len(part.faces), 1)))
        part.visual.material = material(name, color, part_name)
        scene.add_geometry(part, geom_name=part_name, node_name=part_name)
        region_summary.append({
            "name": part_name, "source": name, "region": tag,
            "faces": int(len(part.faces)), "color": "#" + "".join(f"{v:02X}" for v in color[:3]),
            "metallic": 0.0, "roughness": ROUGH.get(name, 0.62),
        })

# Chrome rim around the black top: four native glTF bars.
rim_y = 0.514
rim_specs = [
    ([0.400, 0.007, 0.010], (0, rim_y, 0.158)),
    ([0.400, 0.007, 0.010], (0, rim_y, -0.158)),
    ([0.010, 0.007, 0.310], (0.193, rim_y, 0)),
    ([0.010, 0.007, 0.310], (-0.193, rim_y, 0)),
]
for i, (extents, pos) in enumerate(rim_specs):
    bar = box(extents=extents)
    bar.apply_translation(pos)
    color = rgba(CHROME)
    bar.visual = ColorVisuals(mesh=bar, face_colors=np.tile(color, (len(bar.faces), 1)))
    bar.visual.material = PBRMaterial(
        name=f"chrome_rim_{i}", baseColorFactor=color / 255.0,
        metallicFactor=0.0, roughnessFactor=0.28)
    scene.add_geometry(bar, geom_name=f"chrome_rim_{i}", node_name=f"chrome_rim_{i}")
    region_summary.append({"name": f"chrome_rim_{i}", "source": "chrome_top",
                           "region": "rim", "faces": int(len(bar.faces)),
                           "color": CHROME, "metallic": 0.0, "roughness": 0.28})

# Vertical chrome trim on the front-left corner of the yellow tower.
trim = box(extents=[0.004, 0.430, 0.004])
trim.apply_translation([-0.189, 0.285, 0.150])
trim.visual = ColorVisuals(mesh=trim, face_colors=np.tile(rgba(CHROME), (len(trim.faces), 1)))
trim.visual.material = PBRMaterial(
    name="tower_trim", baseColorFactor=rgba(CHROME) / 255.0,
    metallicFactor=0.0, roughnessFactor=0.26)
scene.add_geometry(trim, geom_name="tower_trim", node_name="tower_trim")
region_summary.append({"name": "tower_trim", "source": "lower_body",
                       "region": "trim", "faces": int(len(trim.faces)),
                       "color": CHROME, "metallic": 0.0, "roughness": 0.26})

glb = ART / "quickmill-blockout.glb"
scene.export(glb)
print("glb", glb, glb.stat().st_size)
print("scene bounds", np.round(scene.bounds, 4).tolist())

# ---------------------------------------------------------------- evidence
data = glb.read_bytes()
jlen = struct.unpack("<I", data[12:16])[0]
gltf = json.loads(data[20:20 + jlen])
manifest = {
    "source": str(T054),
    "source_commands": len(commands),
    "glb": str(glb),
    "bytes": glb.stat().st_size,
    "bounds_m": np.round(scene.bounds, 4).tolist(),
    "meshes": len(gltf.get("meshes", [])),
    "materials": [
        {"name": m.get("name"), **m.get("pbrMetallicRoughness", {})}
        for m in gltf.get("materials", [])
    ],
    "regions": region_summary,
}
(EXP / "preview" / "glb-manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"meshes": manifest["meshes"], "materials": len(manifest["materials"]),
                  "regions": len(region_summary)}, indent=1))
