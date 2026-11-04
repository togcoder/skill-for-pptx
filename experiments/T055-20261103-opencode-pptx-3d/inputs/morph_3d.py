#!/usr/bin/env python3
"""Add the real PowerPoint Morph transition to the T055 3D deck.

The T055 first attempt used <p14:morph>, which PowerPoint silently stripped.
`scripts/add_morph.py` in this repo carries the working shape: an
mc:AlternateContent wrapper, a p159:morph inside p:transition, and a fade
fallback. This script applies that structure to slides 2 and 3 and checks
whether PowerPoint keeps it.
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
SRC = ART / "quickmill_native_product_tour_v3.pptx"
DST = ART / "morph-3d.pptx"
SAVED = ART / "morph-3d-saved.pptx"

ALT = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" '
    'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
    '<mc:Choice Requires="p159 p14">'
    '<p:transition spd="slow" p14:dur="1800">'
    '<p159:morph option="byObject"/>'
    '</p:transition>'
    '</mc:Choice>'
    '<mc:Fallback>'
    '<p:transition spd="slow"><p:fade/></p:transition>'
    '</mc:Fallback>'
    '</mc:AlternateContent>'
)

shutil.copy2(SRC, DST)
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in {"ppt/slides/slide2.xml", "ppt/slides/slide3.xml"}:
            text = data.decode("utf-8")
            if "</p:sld>" not in text:
                raise ValueError(item.filename)
            text = text.replace("</p:sld>", ALT + "</p:sld>")
            data = text.encode("utf-8")
        zout.writestr(item, data)

info = {"patched": str(DST)}
ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Open(str(DST.resolve()), WithWindow=False)
    info["slides"] = pres.Slides.Count
    info["entry_effect"] = []
    for i in range(1, pres.Slides.Count + 1):
        try:
            effect = pres.Slides(i).SlideShowTransition.EntryEffect
        except Exception as exc:
            effect = f"ERR {exc}"
        info["entry_effect"].append(effect)
    pres.SaveAs(str(SAVED.resolve()))
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass

with zipfile.ZipFile(SAVED) as z:
    info["xml_after_save"] = {}
    for n in ("ppt/slides/slide2.xml", "ppt/slides/slide3.xml"):
        s = z.read(n).decode("utf-8")
        info["xml_after_save"][n] = {
            "has_morph": "morph" in s,
            "has_alternate": "AlternateContent" in s,
            "has_transition": "<p:transition" in s,
            "snippet": s[s.find("<mc:AlternateContent"):s.find("<mc:AlternateContent") + 500]
            if "<mc:AlternateContent" in s else "",
        }

PREVIEW.mkdir(parents=True, exist_ok=True)
(PREVIEW / "morph-3d.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
print(json.dumps(info, indent=2))
