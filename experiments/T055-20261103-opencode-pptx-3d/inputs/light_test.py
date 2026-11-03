#!/usr/bin/env python3
"""Can the native 3D light rig be tuned through the am3d XML?

PowerPoint writes an ambient light plus three point lights into each 3D model.
The T055 model was rendered with the default rig. This test lowers the ambient
and key intensities on slide 1 only and exports the slide without saving.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
SRC = ART / "quickmill_native_product_tour_v3.pptx"
DST = ART / "light-test.pptx"
PNG = PREVIEW / "light-test.png"

shutil.copy2(SRC, DST)
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "ppt/slides/slide1.xml":
            s = data.decode("utf-8")
            s = s.replace('<am3d:illuminance n="500000" d="1000000"/>',
                          '<am3d:illuminance n="250000" d="1000000"/>')
            s = s.replace('<am3d:intensity n="9765625" d="1000000"/>',
                          '<am3d:intensity n="6000000" d="1000000"/>')
            s = s.replace('<am3d:intensity n="12250000" d="1000000"/>',
                          '<am3d:intensity n="8000000" d="1000000"/>')
            data = s.encode("utf-8")
        zout.writestr(item, data)

ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Open(str(DST.resolve()), WithWindow=False)
    pres.Slides(1).Export(str(PNG.resolve()), "PNG", 1600, 900)
    print("exported", PNG, PNG.stat().st_size)
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass
