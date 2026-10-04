#!/usr/bin/env python3
"""Read-only H001 plan/package comparison. Does not execute PowerPoint."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from inspect_pptx import inspect

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main",
}
PLAN = ROOT / "experiments/H001/plan.json"
DECK = ROOT / "output/PPTX_Motion_Lab_H001.pptx"
plan = json.loads(PLAN.read_text())
inventory = inspect(DECK)
failures = list(inventory["errors"])
checks = []
slide_rows = []


def check(name, passed):
    checks.append({"check": name, "passed": bool(passed)})
    if not passed:
        failures.append(name)


check("two ordered slides", len(inventory["slides"]) == len(plan["states"]) == 2)
objects = {obj["id"]: obj for obj in plan["objects"]}
with ZipFile(DECK) as package:
    for slide, state in zip(inventory["slides"], plan["states"]):
        root = ET.fromstring(package.read(slide["part"]))
        shapes = root.findall("p:cSld/p:spTree/p:sp", NS)
        actual = {}
        for shape in shapes:
            props = shape.find("p:nvSpPr/p:cNvPr", NS)
            name = props.attrib["name"]
            transform = shape.find("p:spPr/a:xfrm", NS)
            off = transform.find("a:off", NS).attrib
            ext = transform.find("a:ext", NS).attrib
            actual[name] = {
                "geometry_emu": [int(off["x"]), int(off["y"]), int(ext["cx"]), int(ext["cy"])],
                "text": "".join(node.text or "" for node in shape.findall(".//a:t", NS)),
                "textbox": shape.find("p:nvSpPr/p:cNvSpPr", NS).get("txBox") == "1",
                "preset_geometry": shape.find("p:spPr/a:prstGeom", NS).get("prst"),
                "font_sizes_hundredth_pt": [node.get("sz") for node in shape.findall(".//a:rPr", NS)],
            }
        expected_names = {objects[oid]["morph_name"] for oid in state["objects"]}
        check(f"slide {slide['index']} exact unique semantic names", set(actual) == expected_names and len(actual) == len(shapes) == 12)
        for oid, frame in state["objects"].items():
            obj = objects[oid]
            row = actual.get(obj["morph_name"])
            if row is None:
                continue
            expected = [frame["x"] * 12192000, frame["y"] * 6858000, frame["w"] * 12192000, frame["h"] * 6858000]
            check(f"slide {slide['index']} {oid} geometry", all(abs(x - y) <= 1 for x, y in zip(row["geometry_emu"], expected)))
            check(f"slide {slide['index']} {oid} native type", row["textbox"] == (obj["kind"] == "text") and row["preset_geometry"] == "rect")
            check(f"slide {slide['index']} {oid} text", row["text"] == frame.get("text", obj.get("text", "")))
        morph_nodes = root.findall(".//p159:morph", NS)
        transition = root.find(".//mc:Choice/p:transition", NS)
        duration = None if transition is None else transition.get(f"{{{NS['p14']}}}dur")
        if slide["index"] == 1:
            check("first slide has no Morph", not morph_nodes and transition is None)
        else:
            check("destination has one byObject Morph", len(morph_nodes) == 1 and morph_nodes[0].get("option") == "byObject")
            check("destination duration equals plan", duration == str(plan["transitions"][0]["duration_ms"]))
        check(f"slide {slide['index']} no raster or video", not root.findall(".//p:pic", NS) and not root.findall(".//p:graphicFrame", NS))
        slide_rows.append({
            "index": slide["index"], "ordered_part": slide["part"],
            "native_rectangles": sum(not v["textbox"] for v in actual.values()),
            "native_textboxes": sum(v["textbox"] for v in actual.values()),
            "morph_duration_ms": duration, "objects": actual,
        })
    notes = [package.read(n).decode("utf-8") for n in package.namelist() if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml")]
    check("Microsoft mechanism URL in both notes", len(notes) == 2 and all("support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks" in note for note in notes))
    check("no hardcoded E001 provenance in notes", all("powerpointschool.com" not in note and "Native PowerPoint playback" not in note for note in notes))
    check("no embedded media", not any(n.startswith("ppt/media/") for n in package.namelist()))

first, second = [row["objects"] for row in slide_rows]
inspect1 = first["!!h001-inspect-block"]["geometry_emu"]
inspect2 = second["!!h001-inspect-block"]["geometry_emu"]
check("Inspect grows in both dimensions", inspect2[2] > inspect1[2] and inspect2[3] > inspect1[3])
check("Inspect stays centered horizontally", abs(inspect1[0] + inspect1[2] / 2 - 6096000) <= 1 and abs(inspect2[0] + inspect2[2] / 2 - 6096000) <= 1)
for index, slide in enumerate(slide_rows, 1):
    context = slide["objects"]
    for prefix in ["collect", "inspect", "decide"]:
        x, y, w, h = context[f"!!h001-{prefix}-block"]["geometry_emu"]
        check(f"slide {index} {prefix} block on canvas", x >= 0 and y >= 0 and x + w <= 12192000 and y + h <= 6858000)
    l = context["!!h001-collect-block"]["geometry_emu"]
    c = context["!!h001-inspect-block"]["geometry_emu"]
    r = context["!!h001-decide-block"]["geometry_emu"]
    check(f"slide {index} left-center-right sequence", l[0] + l[2] < c[0] and c[0] + c[2] < r[0])

report = {
    "experiment": "H001", "pptx_sha256": hashlib.sha256(DECK.read_bytes()).hexdigest(),
    "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
    "passed": not failures, "failures": failures, "checks": checks, "slides": slide_rows,
    "inspect_width_ratio": inspect2[2] / inspect1[2], "inspect_height_ratio": inspect2[3] / inspect1[3],
    "native_powerpoint_playback_verified": False, "application_editability_verified": False,
    "boundary": "Ordered OOXML objects and declared transitions only. No PowerPoint execution or full OOXML schema certification.",
}
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if report["passed"] else 1)
