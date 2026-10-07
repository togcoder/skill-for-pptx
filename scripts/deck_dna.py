#!/usr/bin/env python3
"""Design + motion DNA of a deck (T027).

Reads only XML parts (theme, presentation, slides), so it also works on a
remote PPTX over HTTP Range requests without downloading media. The DNA is
numbers, not content: palette, fonts, type scale, density, grid, picture
coverage, transitions and the full animation vocabulary in use. Aggregated
over a corpus it tells Forge and the Director what good design and complex
motion look like in practice.

    deck_dna.py deck.pptx [more.pptx ...]          # JSON per deck
    deck_dna.py --remote URL                        # same, via Range requests
"""
import argparse
import io
import json
import re
import statistics
import sys
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS={"p":P,"a":A,"r":R}
PARSER=E.XMLParser(resolve_entities=False,no_network=True,huge_tree=False)
UA={"User-Agent":"skill-for-pptx deck_dna (research)"}


class RangeFile(io.RawIOBase):
    """Seekable read-only view of a remote file via HTTP Range (block cached)."""

    BLOCK=256*1024

    def __init__(self,url):
        self.url=url
        req=urllib.request.Request(url,headers={**UA,"Range":"bytes=0-0"})
        with urllib.request.urlopen(req,timeout=60) as r:
            self.url=r.geturl()  # follow the CDN redirect once
            total=r.headers.get("Content-Range","").split("/")[-1]
            self.size=int(total) if total.isdigit() else int(r.headers["Content-Length"])
        self.pos=0
        self.cache={}
        self.fetched=0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self,off,whence=0):
        self.pos={0:off,1:self.pos+off,2:self.size+off}[whence]
        return self.pos

    def _block(self,i):
        if i not in self.cache:
            start=i*self.BLOCK
            end=min(self.size,start+self.BLOCK)-1
            req=urllib.request.Request(self.url,headers={**UA,"Range":f"bytes={start}-{end}"})
            with urllib.request.urlopen(req,timeout=60) as r:
                self.cache[i]=r.read()
            self.fetched+=len(self.cache[i])
        return self.cache[i]

    def readinto(self,b):
        n=min(len(b),self.size-self.pos)
        if n<=0:
            return 0
        out=bytearray()
        while len(out)<n:
            i,off=divmod(self.pos+len(out),self.BLOCK)
            blk=self._block(i)
            out+=blk[off:off+n-len(out)]
        b[:n]=out
        self.pos+=n
        return n


def _xml(z,name):
    try:
        return E.fromstring(z.read(name),PARSER)
    except (KeyError,E.XMLSyntaxError):
        return None


def _slides(z):
    rels=_xml(z,"ppt/_rels/presentation.xml.rels")
    pres=_xml(z,"ppt/presentation.xml")
    if rels is None or pres is None:
        return [],None
    target={r.get("Id"):r.get("Target") for r in rels}
    out=[]
    for s in pres.findall("p:sldIdLst/p:sldId",NS):
        t=target.get(s.get(f"{{{R}}}id"),"")
        out.append("ppt/"+t.lstrip("/").removeprefix("ppt/"))
    return out,pres


def theme_dna(z):
    names=sorted(n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml$",n))
    th=_xml(z,names[0]) if names else None
    if th is None:
        return {}
    cs={}
    scheme=th.find(".//a:clrScheme",NS)
    for el in (scheme if scheme is not None else []):
        c=el.find("a:srgbClr",NS)
        s=el.find("a:sysClr",NS)
        cs[E.QName(el).localname]=(c.get("val") if c is not None else (s.get("lastClr") if s is not None else None))
    fonts={k:(th.find(f".//a:fontScheme/a:{k}/a:latin",NS).get("typeface")
              if th.find(f".//a:fontScheme/a:{k}/a:latin",NS) is not None else None) for k in ("majorFont","minorFont")}
    return {"name":th.get("name"),"colors":cs,"fonts":fonts}


def motion_dna(root):
    m=Counter()
    presets=Counter()
    timing=root.find("p:timing",NS)
    trans=root.find("p:transition",NS)
    if trans is None:
        trans=root.find(".//p:transition",NS)  # inside mc:AlternateContent
    if trans is not None:
        kinds=[E.QName(c).localname for c in trans if E.QName(c).localname not in ("sndAc","extLst")]
        morph=root.find(".//{http://schemas.microsoft.com/office/powerpoint/2015/09/main}morph") is not None
        m["transition:"+("morph" if morph else (kinds[0] if kinds else "none"))]+=1
    if timing is None:
        return m,presets,0
    main=timing.find(".//p:cTn[@nodeType='mainSeq']",NS)
    clicks=len(main.findall("p:childTnLst/p:par",NS)) if main is not None else 0
    m["click_groups"]+=clicks
    m["interactive_sequences"]+=len(timing.findall(".//p:cTn[@nodeType='interactiveSeq']",NS))
    effects=timing.findall(".//p:cTn[@presetClass]",NS)
    for c in effects:
        cls=c.get("presetClass")
        presets[f"{cls}:{c.get('presetID')}:{c.get('presetSubtype') or 0}"]+=1
        m["effects"]+=1
        m["class:"+cls]+=1
        m["node:"+(c.get("nodeType") or "?")]+=1
        if c.get("repeatCount"):
            m["repeat"]+=1
        if c.get("autoRev")=="1":
            m["auto_reverse"]+=1
        if cls=="path" and c.get("presetID")=="0":
            m["custom_path"]+=1
        if c.find(".//p:txEl",NS) is not None:
            m["text_build"]+=1
        if c.find(".//p:graphicEl",NS) is not None:
            m["chart_or_diagram_build"]+=1
        d=[int(x.get("dur")) for x in c.iter(f"{{{P}}}cTn") if (x.get("dur") or "").isdigit()]
        if d:
            m["dur_sum_ms"]+=max(d)
    return m,presets,len(effects)


def slide_design(root,sw,sh):
    sizes=[int(r.get("sz"))/100 for r in root.iter(f"{{{A}}}rPr") if r.get("sz")]
    chars=sum(len(t.text or "") for t in root.iter(f"{{{A}}}t"))
    lefts=[]
    pic_area=0.0
    shapes=0
    for x in root.iter(f"{{{A}}}xfrm"):
        off,ext=x.find("a:off",NS),x.find("a:ext",NS)
        if off is None or ext is None:
            continue
        shapes+=1
        lefts.append(round(int(off.get("x"))/sw,2))
        if x.getparent() is not None and x.getparent().getparent() is not None and \
                E.QName(x.getparent().getparent()).localname=="pic":
            pic_area+=int(ext.get("cx"))*int(ext.get("cy"))/(sw*sh)
    return {"sizes":sizes,"chars":chars,"shapes":shapes,"grid_cols":len(set(lefts)),"pic_area":min(pic_area,1.5)}


def dna(source,remote=False,max_slides=80):
    f=RangeFile(source) if remote else open(source,"rb")
    with zipfile.ZipFile(f) as z:
        parts,pres=_slides(z)
        size=pres.find("p:sldSz",NS) if pres is not None else None
        sw,sh=(int(size.get("cx")),int(size.get("cy"))) if size is not None else (12192000,6858000)
        motion=Counter()
        presets=Counter()
        per_slide_effects=[]
        designs=[]
        for part in parts[:max_slides]:
            root=_xml(z,part)
            if root is None:
                continue
            m,p,n=motion_dna(root)
            motion+=m
            presets+=p
            per_slide_effects.append(n)
            designs.append(slide_design(root,sw,sh))
        theme=theme_dna(z)
    sizes=[s for d in designs for s in d["sizes"]]
    out={
        "source":str(source),"slides":len(parts),"aspect":round(sw/sh,3),"theme":theme,
        "design":{
            "type_sizes":sorted(Counter(round(s) for s in sizes).most_common(8)),
            "type_levels":len({round(s) for s in sizes}),
            "max_pt":max(sizes,default=None),"median_pt":statistics.median(sizes) if sizes else None,
            "chars_per_slide":round(statistics.mean(d["chars"] for d in designs),1) if designs else 0,
            "shapes_per_slide":round(statistics.mean(d["shapes"] for d in designs),1) if designs else 0,
            "grid_cols_median":statistics.median(d["grid_cols"] for d in designs) if designs else 0,
            "picture_coverage":round(statistics.mean(d["pic_area"] for d in designs),3) if designs else 0,
        },
        "motion":dict(motion),
        "presets":dict(presets.most_common()),
        "animated_slides":sum(1 for n in per_slide_effects if n),
        "max_effects_slide":max(per_slide_effects,default=0),
    }
    out["motion_complexity"]=complexity(out)
    if remote:
        out["bytes_fetched"]=f.fetched
    return out


def complexity(d):
    """Rough motion richness: vocabulary breadth, density, compound features."""
    m=d["motion"]
    vocab=len(d["presets"])
    return round(vocab*2+min(m.get("effects",0),300)/10+d["max_effects_slide"]
                 +8*m.get("custom_path",0)**0.5+6*m.get("transition:morph",0)**0.5
                 +5*(m.get("repeat",0)>0)+5*(m.get("interactive_sequences",0)>0)
                 +3*m.get("class:path",0)**0.5+3*m.get("class:emph",0)**0.5,1)


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources",nargs="+")
    ap.add_argument("--remote",action="store_true")
    a=ap.parse_args()
    for s in a.sources:
        print(json.dumps(dna(s,a.remote),ensure_ascii=False))


if __name__=="__main__":
    main()
