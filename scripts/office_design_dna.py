#!/usr/bin/env python3
"""Design kits from Microsoft's own designer themes (T027).

Reads the Office install's ``Document Themes 16`` folder (``*.thmx``, plus the
``Theme Colors`` and ``Theme Fonts`` scheme files) and extracts what a designer
decided: palette roles, font pairings, the master type scale, title/body
geometry and margins, and how much decoration the master carries. Output is
numbers and names only; no theme files are copied.

    office_design_dna.py -o knowledge/office_design_kits.json
"""
import argparse
import json
import zipfile
from pathlib import Path

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
NS={"p":P,"a":A}
DEFAULT=Path("C:/Program Files/Microsoft Office/root/Document Themes 16")


def _scheme_colors(scheme):
    out={}
    for el in scheme if scheme is not None else []:
        c=el.find("a:srgbClr",NS)
        s=el.find("a:sysClr",NS)
        out[E.QName(el).localname]=c.get("val") if c is not None else (s.get("lastClr") if s is not None else None)
    return out


def _fonts(root):
    return {k:(root.find(f".//a:{k}/a:latin",NS).get("typeface") if root.find(f".//a:{k}/a:latin",NS) is not None else None)
            for k in ("majorFont","minorFont")}


def _sz(el):
    rpr=el.find(".//a:defRPr",NS) if el is not None else None
    return int(rpr.get("sz"))/100 if rpr is not None and rpr.get("sz") else None


def thmx_kit(path):
    z=zipfile.ZipFile(path)
    names=z.namelist()
    theme=E.fromstring(z.read(next(n for n in names if n.endswith("theme1.xml"))))
    pres=E.fromstring(z.read("theme/presentation.xml"))
    sz=pres.find("p:sldSz",NS)
    sw,sh=int(sz.get("cx")),int(sz.get("cy"))
    master=E.fromstring(z.read("theme/slideMasters/slideMaster1.xml"))
    tx=master.find("p:txStyles",NS)
    scale={"title":_sz(tx.find("p:titleStyle/a:lvl1pPr",NS))}
    for lvl in range(1,5):
        scale[f"body_l{lvl}"]=_sz(tx.find(f"p:bodyStyle/a:lvl{lvl}pPr",NS))

    def geom(root,ph_type):
        for sp in root.iter(f"{{{P}}}sp"):
            ph=sp.find(".//p:nvPr/p:ph",NS)
            if ph is not None and (ph.get("type") or "body")==ph_type:
                off=sp.find("p:spPr/a:xfrm/a:off",NS)
                ext=sp.find("p:spPr/a:xfrm/a:ext",NS)
                if off is not None:
                    return [round(int(off.get("x"))/sw,3),round(int(off.get("y"))/sh,3),
                            round(int(ext.get("cx"))/sw,3),round(int(ext.get("cy"))/sh,3)]
        return None

    deco=[sp for sp in master.find("p:cSld/p:spTree",NS) if sp.find(".//p:nvPr/p:ph",NS) is None
          and E.QName(sp).localname in ("sp","pic","grpSp","cxnSp")]
    layouts=sorted(n for n in names if n.startswith("theme/slideLayouts/slideLayout") and n.endswith(".xml"))
    layout_types=[E.fromstring(z.read(n)).get("type") for n in layouts]
    title=geom(master,"title")
    body=geom(master,"body")
    return {
        "name":path.stem,"aspect":round(sw/sh,3),
        "colors":_scheme_colors(theme.find(".//a:clrScheme",NS)),
        "fonts":_fonts(theme),
        "type_scale_pt":scale,
        "title_box":title,"body_box":body,
        "margin_left":title[0] if title else None,
        "master_decoration_shapes":len(deco),
        "background":"picture/gradient" if master.find("p:cSld/p:bg//a:blipFill",NS) is not None
                     or master.find("p:cSld/p:bg//a:gradFill",NS) is not None else "solid/style",
        "layouts":layout_types,
    }


def build(root=DEFAULT):
    kits=[thmx_kit(p) for p in sorted(root.glob("*.thmx"))]
    palettes=[]
    for p in sorted((root/"Theme Colors").glob("*.xml")):
        x=E.fromstring(p.read_bytes())
        palettes.append({"name":x.get("name") or p.stem,"colors":_scheme_colors(x)})
    pairings=[]
    for p in sorted((root/"Theme Fonts").glob("*.xml")):
        pairings.append({"name":p.stem,**_fonts(E.fromstring(p.read_bytes()))})
    return {"source":"Microsoft Office Document Themes 16 (local install); derived metrics only",
            "themes":kits,"palettes":palettes,"font_pairings":pairings}


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root",type=Path,default=DEFAULT)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    data=build(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=1,ensure_ascii=False),encoding="utf-8")
    for k in data["themes"]:
        print(k["name"],k["fonts"],k["type_scale_pt"],"margin",k["margin_left"],"deco",k["master_decoration_shapes"])
    print(len(data["palettes"]),"palettes",len(data["font_pairings"]),"font pairings")


if __name__=="__main__":
    main()
