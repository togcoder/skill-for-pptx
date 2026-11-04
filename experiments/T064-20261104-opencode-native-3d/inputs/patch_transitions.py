#!/usr/bin/env python3
"""T064: write the two transition variants into copies of the camera deck.

`camera-morph.pptx` gets the structure `scripts/add_morph.py` proved PowerPoint
keeps: mc:AlternateContent / p159:morph / p:transition, with a fade fallback.
`camera-fade.pptx` gets a plain p:fade control on the same slide, so identical
frames would prove that Morph fell back to a cross-fade.

Run:  python experiments/T064-.../inputs/patch_transitions.py
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"

SRC = ART / "camera-morph-base.pptx"
MORPH = ART / "camera-morph.pptx"
FADE = ART / "camera-fade.pptx"

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
FADE_XML = '<p:transition spd="slow"><p:fade/></p:transition>'


def patch(dst: Path, xml: str) -> None:
    if dst.exists():
        raise SystemExit(f"refuse to overwrite {dst}")
    with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/slide2.xml":
                text = data.decode("utf-8")
                if "<p:transition" in text:
                    raise SystemExit("source slide already has a transition")
                text = text.replace("</p:sld>", xml + "</p:sld>")
                data = text.encode("utf-8")
            zout.writestr(item, data)


patch(MORPH, MORPH_XML)
patch(FADE, FADE_XML)

info = {}
for path in (MORPH, FADE):
    with zipfile.ZipFile(path) as z:
        s = z.read("ppt/slides/slide2.xml").decode("utf-8")
    start = s.find("<mc:AlternateContent", s.find("<p:clrMapOvr"))
    if start < 0:
        start = s.rfind("<p:transition")
    end = s.find("</mc:AlternateContent>", start)
    transition = s[start:end + 21] if end > 0 else s[start:s.find("</p:transition>") + 15]
    info[path.name] = {
        "bytes": path.stat().st_size,
        "has_morph": "morph" in transition,
        "has_fade_fallback": "<mc:Fallback>" in transition and "p:fade" in transition,
        "transition": transition,
    }
PREVIEW.mkdir(parents=True, exist_ok=True)
(PREVIEW / "patch-transitions.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
print(json.dumps(info, indent=2))
