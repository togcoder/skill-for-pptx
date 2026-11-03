#!/usr/bin/env python3
"""Try the PowerPoint 2010 Morph transition through OOXML.

The COM enum rejects EntryEffect=384 ("Invalid enumeration value"), so the
transition is written directly into the slide XML and PowerPoint is asked to
open, save and report it back.
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
DST = ART / "morph-ooxml.pptx"
SAVED = ART / "morph-ooxml-saved.pptx"

TRANSITION = (
    '<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
    'spd="slow"><p14:morph option="byObject"/></p:transition>'
)

shutil.copy2(SRC, DST)
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in {"ppt/slides/slide2.xml", "ppt/slides/slide3.xml"}:
            text = data.decode("utf-8")
            text = text.replace("</p:clrMapOvr></p:sld>",
                                "</p:clrMapOvr>" + TRANSITION + "</p:sld>")
            data = text.encode("utf-8")
        zout.writestr(item, data)

info = {}
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
            "has_transition": "<p:transition" in s,
            "snippet": s[s.find("<p:transition"):s.find("<p:transition") + 260]
            if "<p:transition" in s else "",
        }

PREVIEW.mkdir(parents=True, exist_ok=True)
(PREVIEW / "morph-ooxml.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
print(json.dumps(info, indent=2))
