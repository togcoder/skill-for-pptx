#!/usr/bin/env python3
"""Turn the PowerPoint-authored preset deck (harvest_presets.ps1) into a preset
library: for every built-in effect, the presetClass/ID/Subtype PowerPoint
writes and its behaviour subtree with the target abstracted to ``{spid}``.

    extract_presets.py local-media/corpus/powerpoint_presets.pptx -o knowledge/powerpoint_presets.json
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
import pptx_animator as anim  # noqa: E402

NS=anim.NS
P=anim.P


def _ordered_slides(z):
    rels=E.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    target={r.get("Id"):r.get("Target") for r in rels}
    pres=E.fromstring(z.read("ppt/presentation.xml"))
    ids=pres.findall("p:sldIdLst/p:sldId",NS)
    rid="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    return ["ppt/"+target[s.get(rid)] for s in ids]


def _kebab(name):
    name=re.sub(r"^msoAnimEffect","",name)
    return re.sub(r"(?<!^)(?=[A-Z])","-",name).lower()


def behaviours(ctn):
    """Behaviour tags in document order with the attributes that matter."""
    out=[]
    for el in ctn.find("p:childTnLst",NS):
        tag=E.QName(el).localname
        info={"tag":tag}
        for k in ("transition","filter","prLst","path","by","from","to","calcmode","valueType","origin","pathEditMode"):
            if el.get(k) is not None:
                info[k]=el.get(k)
        attrs=[a.text for a in el.iterfind(".//p:attrName",NS)]
        if attrs:
            info["attr"]=attrs
        inner=el.find("p:cBhvr/p:cTn",NS)
        if inner is not None:
            info["dur"]=inner.get("dur")
            for k in ("autoRev","accel","decel","repeatCount","fill"):
                if inner.get(k):
                    info[k]=inner.get(k)
        tav=[(t.get("tm"),(t.find("p:val/*",NS).get("val") if t.find("p:val/*",NS) is not None else None))
             for t in el.iterfind("p:tavLst/p:tav",NS)]
        if tav:
            info["tav"]=tav
        for child in ("by","from","to"):
            node=el.find(f"p:{child}",NS)
            if node is not None:
                val=node.find("*",NS)
                info[child]=dict(node.attrib) or ({"val":val.get("val")} if val is not None else {})
        out.append(info)
    return out


def template(ctn):
    """Behaviour subtree as XML with spid -> {spid} and ids stripped."""
    clone=copy.deepcopy(ctn.find("p:childTnLst",NS))
    for t in clone.iter(f"{{{P}}}spTgt"):
        t.set("spid","{spid}")
        for tx in list(t):
            t.remove(tx)
    for c in clone.iter(f"{{{P}}}cTn"):
        c.attrib.pop("id",None)
    return E.tostring(clone,encoding="unicode")


def extract(pptx,manifest):
    rows=json.loads(Path(manifest).read_text(encoding="utf-8-sig"))["effects"]
    by_slide={r["slide"]:r for r in rows if r.get("ok")}
    lib=[]
    with ZipFile(pptx) as z:
        for idx,part in enumerate(_ordered_slides(z),1):
            row=by_slide.get(idx)
            if not row:
                continue
            root=E.fromstring(z.read(part))
            ctn=root.find(".//p:cTn[@presetClass]",NS)
            if ctn is None:
                continue
            bld=root.find(".//p:bldLst/*",NS)
            lib.append({
                "name":_kebab(row["name"])+("-out" if row["exit"] else ""),
                "mso":row["name"],"mso_value":row["value"],"exit":row["exit"],
                "presetClass":ctn.get("presetClass"),"presetID":int(ctn.get("presetID")),
                "presetSubtype":int(ctn.get("presetSubtype") or 0),
                "default_ms":None if row.get("duration_s",0) in (None,float("inf")) or row.get("duration_s",0)>1e6
                             else round(row.get("duration_s",0)*1000),
                "ctn_attrs":{k:v for k,v in ctn.attrib.items() if k in ("accel","decel","autoRev","repeatCount")},
                "behaviours":behaviours(ctn),
                "build":E.QName(bld).localname+(":"+",".join(f"{k}={v}" for k,v in bld.attrib.items() if k not in ("spid","grpId"))) if bld is not None else None,
                "xml":template(ctn),
            })
    return lib


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx",type=Path)
    ap.add_argument("--manifest",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    lib=extract(a.pptx,a.manifest or a.pptx.with_suffix(".json"))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"source":"PowerPoint-authored via harvest_presets.ps1","count":len(lib),"presets":lib},
                                   indent=1,ensure_ascii=False),encoding="utf-8")
    from collections import Counter
    print(len(lib),Counter(p["presetClass"] for p in lib))


if __name__=="__main__":
    main()
