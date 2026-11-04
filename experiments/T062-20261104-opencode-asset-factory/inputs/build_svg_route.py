#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - route B: the same part table baked to one SVG picture.

Emits a 960x540 SVG from the same ``native_art`` part table route A compiles to
native shapes, rasterises a PNG fallback with resvg, and drops both into the
shared stage the way Slide Forge inserts an Iconify icon (SVG blip + PNG
fallback). The art is one picture; PowerPoint can edit it as a picture only.

Not a product path.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import resvg_py
from lxml import etree
from PIL import Image
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import Part
from pptx.oxml.ns import qn
from pptx.util import Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_native_art as bn  # noqa: E402
import route_stage as stage  # noqa: E402


def _rect(part: dict) -> str:
    x, y, w, h = part["rect"]
    rx = part.get("radius_pt", 0)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}"'


def _ellipse(part: dict) -> str:
    x, y, w, h = part["rect"]
    return f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}"'


def _ring(part: dict, hole: dict) -> str:
    """The merged ring as one path with a hole (even-odd), like the native custGeom."""
    paths = []
    for box in (part["rect"], hole["rect"]):
        x, y, w, h = box
        cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
        paths.append(
            f"M {cx - rx} {cy} a {rx} {ry} 0 1 0 {2 * rx} 0 a {rx} {ry} 0 1 0 {-2 * rx} 0 Z"
        )
    return f'<path d="{" ".join(paths)}" fill-rule="evenodd"'


def build_svg(asset: dict, theme: dict) -> str:
    width, height = asset["stage"]["size"]
    merged = {}
    helpers = set()
    for op in asset.get("ops", []):
        merge = op["merge"]
        merged[merge["name"]] = [n for n in merge["ids"] if n != merge["name"]]
        helpers.update(merged[merge["name"]])
    by_name = {p["name"]: p for p in asset["parts"]}

    defs, body = [], []
    blur_id = 0
    for part in asset["parts"]:
        if part["role"] != "art":
            continue
        if part["name"] in helpers:
            continue
        if part["kind"] != "text":
            fill = "#" + bn.colour(part["fill"]["color"], theme)
            alpha = 1 - part.get("fill", {}).get("transparency", 0)
            opacity = f' fill-opacity="{alpha:g}"' if alpha < 1 else ""
            filter_attr = ""
            if part.get("effects", {}).get("softEdges"):
                blur_id += 1
                defs.append(
                    f'<filter id="b{blur_id}" x="-50%" y="-50%" width="200%" height="200%" '
                    f'color-interpolation-filters="sRGB">'
                    f'<feGaussianBlur stdDeviation="{part["effects"]["softEdges"] / 2:g}"/></filter>'
                )
                filter_attr = f' filter="url(#b{blur_id})"'
            style = f'fill="{fill}"{opacity}{filter_attr}'

        if part["kind"] in ("rect", "roundRect"):
            body.append(f"{_rect(part)} {style}/>")
        elif part["kind"] == "ellipse":
            if part["name"] in merged:
                body.append(f"{_ring(part, by_name[merged[part['name']][0]])} {style}/>")
            else:
                body.append(f"{_ellipse(part)} {style}/>")
        elif part["kind"] == "polygon":
            points = " ".join(f"{x},{y}" for x, y in part["polygon"])
            body.append(f'<polygon points="{points}" {style}/>')
        elif part["kind"] == "text":
            text = part["text"]
            x, y = part["rect"][0], part["rect"][1]
            size = text["size_pt"]
            baseline = y + size * 0.82
            attrs = [
                f'font-family="{asset.get("font", "Segoe UI")}"',
                f'font-size="{size}"',
                f'font-weight="{"bold" if text.get("bold") else "normal"}"',
                f'fill="#{bn.colour(text.get("color", "text"), theme)}"',
            ]
            if text.get("spacing_pt"):
                attrs.append(f'letter-spacing="{text["spacing_pt"]}"')
            for index, line in enumerate(text["value"].replace("{art_parts}", "").split("\n")):
                dy = 0 if index == 0 else size * text.get("line_spacing", 1.0) * 1.2
                body.append(
                    f'<text x="{x}" y="{baseline + dy}" {" ".join(attrs)}>{escape(line)}</text>'
                )
        else:
            raise ValueError(part["kind"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n<defs>{"".join(defs)}</defs>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def insert_svg_picture(slide, png_path: Path, svg_path: Path, name: str):
    with Image.open(png_path) as image:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    buffer.seek(0)
    picture = slide.shapes.add_picture(buffer, 0, 0, width=Pt(960), height=Pt(540))
    picture.name = name
    package = slide.part.package
    svg_part = Part(package.next_partname("/ppt/media/image%d.svg"), "image/svg+xml", package,
                    svg_path.read_bytes())
    rel_id = slide.part.relate_to(svg_part, RT.IMAGE)
    blip = picture._element.find(".//" + qn("a:blip"))
    ext_list = etree.SubElement(blip, qn("a:extLst"))
    ext = etree.SubElement(ext_list, qn("a:ext"), uri="{96DAC541-7B7A-43D3-8B79-37D633B846F1}")
    etree.SubElement(ext, "{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip",
                     {qn("r:embed"): rel_id},
                     nsmap={"asvg": "http://schemas.microsoft.com/office/drawing/2016/SVG/main"})
    return picture


def build(spec_path: Path, out_dir: Path) -> dict:
    spec, theme = stage.load(spec_path)
    asset = spec["asset"]["native_art"]
    out_dir.mkdir(parents=True, exist_ok=True)
    art = stage.art_parts(asset)

    svg_path = out_dir / "field-terminal-art.svg"
    svg_path.write_text(build_svg(asset, theme), encoding="utf-8")
    png_bytes = resvg_py.svg_to_bytes(svg_path=str(svg_path), width=1920, height=1080)
    png_path = out_dir / "field-terminal-art.png"
    png_path.write_bytes(bytes(png_bytes))

    base = out_dir / "route-b-stage.pptx"
    stage.build_stage(spec_path, base)
    from pptx import Presentation

    prs = Presentation(str(base))
    insert_svg_picture(prs.slides[0], png_path, svg_path, "art-field-terminal")
    pptx = out_dir / f"{spec['asset']['id']}-routeB.pptx"
    prs.save(pptx)
    return {
        "route": "svg_picture",
        "svg": str(svg_path),
        "png": str(png_path),
        "pptx": str(pptx),
        "art_parts_in_source": len(art),
        "svg_bytes": svg_path.stat().st_size,
        "pptx_bytes": pptx.stat().st_size,
    }


if __name__ == "__main__":
    print(json.dumps(build(Path(sys.argv[1]), Path(sys.argv[2])), indent=1))
