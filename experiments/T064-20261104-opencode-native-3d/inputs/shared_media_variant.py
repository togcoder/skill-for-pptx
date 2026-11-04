#!/usr/bin/env python3
"""T064: variant B -- both slides share one embedded GLB and one raster.

`Shapes.Add3DModel` embeds a private copy of the model (and of its preview
raster) on every slide, so the two morph candidates carry different media
parts and different `am3d:raster` images even when they are the same file.
This variant points slide 2 at slide 1's `model3d1.glb` and `image1.png`, so the
only difference between the slides is the `am3d:camera` element.

If Morph animates the camera here but not in variant A, the blocker is media
identity, not 3D support. If it fades here too, model3d camera interpolation is
not implemented by PowerPoint's Morph.

Run:  python experiments/T064-.../inputs/shared_media_variant.py
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
DST = ART / "camera-morph-shared.pptx"

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


def main() -> dict:
    if DST.exists():
        raise SystemExit(f"refuse to overwrite {DST}")
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>'
        '<Relationship Id="rId2" Type="http://schemas.microsoft.com/office/2017/06/relationships/model3d" Target="../media/model3d1.glb"/>'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout7.xml"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in {"ppt/media/model3d2.glb", "ppt/media/image2.png"}:
                continue
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/_rels/slide2.xml.rels":
                data = rels.encode("utf-8")
            elif item.filename == "ppt/slides/slide2.xml":
                text = data.decode("utf-8").replace("</p:sld>", MORPH_XML + "</p:sld>")
                data = text.encode("utf-8")
            zout.writestr(item, data)

    with zipfile.ZipFile(DST) as z:
        s2 = z.read("ppt/slides/slide2.xml").decode("utf-8")
        r2 = z.read("ppt/slides/_rels/slide2.xml.rels").decode("utf-8")
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    info = {
        "pptx": str(DST), "bytes": DST.stat().st_size,
        "media": media,
        "slide2_camera": s2[s2.find("<am3d:camera>"):s2.find("</am3d:camera>") + 14],
        "slide2_model_rel": "model3d1.glb" if "model3d1.glb" in r2 else "other",
        "slide2_has_morph": "p159:morph" in s2,
    }
    (PREVIEW / "shared-media-variant.json").write_text(json.dumps(info, indent=2),
                                                       encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    main()
