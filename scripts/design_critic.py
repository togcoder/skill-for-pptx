#!/usr/bin/env python3
"""Design critic: one measurable verdict on beauty and technique (T034).

Every check grades a measurement against ``knowledge/design_system.json``,
the same bands the generators read, so a finding names the rule it breaks,
the value measured, the band expected and the tool that fixes it. It closes
the loop generator -> deck -> critic -> fix (the detect-and-correct shape of
DesignLab), with computed metrics rather than an LLM judge: computed slide
aesthetics track human rankings better than LLM judges do (SlidesGen-Bench
2026: Spearman 0.71 vs 0.53-0.57; Inui et al. 2025: Pearson up to 0.83).
No benchmark measures slide *motion*; the motion rules come from perception
research (slow-in/slow-out, staggering, tracking load) and design-system
tokens, see docs/DESIGN_SYSTEM.md.

Dimensions: design (colour, type, density, layout), motion (each move:
duration, easing, stagger, loops), rhythm (clicks, simultaneous movers,
static slides, settle before Morph), coherence (one type and motion
language), technique (schema validity, when an XSD is given).

    design_critic.py deck.pptx                      # JSON verdict
    design_critic.py deck.pptx --md verdict.md      # also a readable report
    design_critic.py deck.pptx --render lo          # + frame metrics (LibreOffice render)
    design_critic.py deck.pptx --render DIR         # + frame metrics from slide-NN.png (PowerPoint render)
    design_critic.py deck.pptx --xsd pml.xsd        # + ISO 29500 PresentationML schema check

Scores are 1-5 per dimension: 1 + 4 x (good + 0.5 x note) / checks. They are
a summary of the findings, not a calibrated human rating.
"""
import argparse
import colorsys
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
import design_system as ds  # noqa: E402
import morph_studio as mstu  # noqa: E402
import motion_components as mc  # noqa: E402
import motion_director as md  # noqa: E402
import pptx_animator as anim  # noqa: E402

NS=anim.NS
P=anim.P
A=anim.A
P14="http://schemas.microsoft.com/office/powerpoint/2010/main"
P159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"
PARSER=E.XMLParser(resolve_entities=False,no_network=True)
BEHAVIOURS={"anim","animEffect","animMotion","animScale","animRot","animClr","set","cmd","audio","video"}
SPATIAL={"animMotion","animScale","animRot"}
WEIGHT_WORDS={"light","semilight","semibold","bold","black","medium","thin","display","text","condensed","narrow","regular"}
EXEMPT_GRAPHIC={"mask","highlight","backdrop"}
DIMENSION={"COL-TEXT":"design","COL-GRAPHIC":"design","TYP-SMALL":"design","TYP-RATIO":"design",
           "DEN-WORDS":"design","LAY-SAFE":"design","LAY-DENSITY":"design","LAY-BALANCE":"design",
           "COL-COLOURFUL":"design",
           "MOT-DURATION":"motion","MOT-EASING":"motion","MOT-STAGGER":"motion","MOT-AMBIENT":"motion",
           "MOT-TITLE":"motion","TEC-PRESET":"motion",
           "MOT-CLICKS":"rhythm","MOT-MOVERS":"rhythm","MOT-EFFECTS":"rhythm","MOT-STATIC":"rhythm",
           "MOT-SETTLE":"rhythm",
           "TYP-SIZES":"coherence","TYP-FAMILIES":"coherence","MOT-VOCAB":"coherence",
           "TEC-SCHEMA":"technique"}
FIX={
    "COL-TEXT":("use the theme text colour or a palette colour that reaches the contrast","slide_forge theme / brand_palette"),
    "COL-GRAPHIC":("re-apply: helpers take a deck colour that reaches 3:1 (motion_components.deck_style), or set components[].generate.color","motion_director"),
    "TYP-SMALL":("raise the size: body text >= 18 pt in a presentation, never below 12","slide_forge spec / manual"),
    "TYP-RATIO":("make the title about 1.5-2.6x the body size","slide_forge type scale"),
    "TYP-SIZES":("use the theme scale: 3-6 sizes per deck","slide_forge type scale"),
    "TYP-FAMILIES":("one display face plus its text sibling","slide_forge theme"),
    "DEN-WORDS":("cut to the claim and its evidence, or split the slide","slide_forge spec / author"),
    "LAY-SAFE":("bring the text inside the slide (3% safe margin)","author / slide_forge"),
    "LAY-DENSITY":("too crowded: split the slide; nearly empty: enlarge or merge","author / slide_forge"),
    "LAY-BALANCE":("move or enlarge the lighter side","author"),
    "COL-COLOURFUL":("grey decks read as unfinished, garish ones as noisy: use the palette's accent roles","slide_forge theme"),
    "MOT-DURATION":("set duration_ms in the role band","motion_director plan / design_system defaults"),
    "MOT-EASING":("give moves a slow-in/slow-out (ease: standard/enter/exit)","motion_director plan"),
    "MOT-STAGGER":("stagger 60-150 ms, only to show order; move together otherwise","motion_director plan (stagger_ms)"),
    "MOT-AMBIENT":("slow the loop: a cycle of 6 s or more","motion_director plan (period_ms)"),
    "MOT-TITLE":("keep titles still inside a slide; move them by Morph","motion_director / morph_studio"),
    "TEC-PRESET":("use a named PowerPoint preset (ppt:<name>) so the Animation Pane shows it","motion_director"),
    "MOT-CLICKS":("merge reveals into fewer beats or split the slide","motion_director plan"),
    "MOT-MOVERS":("move fewer things at once; group what moves together","motion_director plan"),
    "MOT-EFFECTS":("fewer simultaneous effects per click","motion_director plan"),
    "MOT-STATIC":("give structure (process, data, pictures) motion","motion_director auto"),
    "MOT-SETTLE":("end the slide on its full picture (release click) before Morph","motion_director / motion_script"),
    "MOT-VOCAB":("one motion language: a style with 3-10 effect kinds","motion_director --style"),
    "TEC-SCHEMA":("remove attributes/elements outside ISO 29500 (PowerPoint may repair or drop the slide)","writer"),
}


def _q(ns,tag):
    return f"{{{ns}}}{tag}"


def _delay(ctn):
    cond=ctn.find("p:stCondLst/p:cond",NS) if ctn is not None else None
    v=cond.get("delay") if cond is not None else None
    return int(v) if v and v.isdigit() else 0


def _repeat(ctn):
    v=ctn.get("repeatCount")
    if v is None:
        return None
    return "indefinite" if v=="indefinite" else int(v)/1000 if v.isdigit() else None


def _effect(ectn,block_start):
    """One effect node: timing, behaviours, easing and target."""
    start=block_start+_delay(ectn)
    dur=0
    kinds=set()
    accel=float(ectn.get("accel","0"))/100000
    decel=float(ectn.get("decel","0"))/100000
    repeat=_repeat(ectn)
    auto_rev=ectn.get("autoRev")=="1"
    path=None
    sig=[]
    for el in ectn.iter():
        tag=E.QName(el).localname if isinstance(el.tag,str) else ""
        if tag not in BEHAVIOURS:
            continue
        kinds.add(tag)
        bc=el.find("p:cBhvr/p:cTn",NS)
        if bc is not None:
            d=bc.get("dur")
            if d and d.isdigit():
                dur=max(dur,_delay(bc)+int(d))
            accel=max(accel,float(bc.get("accel","0"))/100000)
            decel=max(decel,float(bc.get("decel","0"))/100000)
            repeat=repeat or _repeat(bc)
            auto_rev=auto_rev or bc.get("autoRev")=="1"
        if tag=="animMotion":
            path=el.get("path")
            sig.append(path)
        elif tag in ("animScale","animRot"):
            by=el.find("p:by",NS)
            sig.append((tag,tuple(sorted(by.attrib.items())) if by is not None else el.get("by")))
        elif tag=="anim":
            attr=el.find("p:cBhvr/p:attrNameLst/p:attrName",NS)
            if attr is not None and attr.text in ("ppt_x","ppt_y"):
                kinds.add("animXY")
    it=ectn.find("p:iterate",NS)
    iterate=None
    if it is not None:
        tm=it.find("p:tmAbs",NS)
        iterate={"by":it.get("type","el"),"gap_ms":int(tm.get("val")) if tm is not None and (tm.get("val") or "").isdigit() else None}
    tgt=ectn.find(".//p:spTgt",NS)
    cls=ectn.get("presetClass")
    pid=int(ectn.get("presetID") or 0)
    if auto_rev and repeat is None:
        dur*=2  # SMIL: autoRev plays the behaviour forward then back
    return {"cls":cls,"pid":pid,"subtype":ectn.get("presetSubtype") or "0","node":ectn.get("nodeType"),
            "spid":tgt.get("spid") if tgt is not None else None,"start":start,"dur":dur,"end":start+dur,
            "accel":accel,"decel":decel,"repeat":repeat,"auto_rev":auto_rev,"kinds":kinds,"path":path,
            "spatial":bool(kinds&SPATIAL) or "animXY" in kinds,"sig":tuple(sig),"iterate":iterate}


def _merge_segments(effects):
    """A gesture written as consecutive path segments on one object (main
    move + overshoot settle, anticipation + move, poly paths) is one move."""
    out=[]
    for e in effects:
        # Merge per channel: a path chain may interleave with a scale chain on
        # the same object (keyframed motion written as segments).
        prev=next((x for x in reversed(out) if x["spid"]==e["spid"] and x["cls"]==e["cls"]
                   and x["kinds"]==e["kinds"]),None)
        if (prev is not None and e["cls"] in ("path","emph") and e["spatial"] and prev["repeat"] is None
                and e["repeat"] is None and abs(e["start"]-prev["end"])<=20):
            prev["end"]=e["end"]
            prev["dur"]=prev["end"]-prev["start"]
            prev["decel"]=e["decel"]
            prev["accel"]=prev["accel"] or e["accel"]
            prev["segments"]=prev.get("segments",1)+1
            continue
        out.append(e)
    return out


def slide_timing(root):
    """Click groups of the main sequence plus interactive effects."""
    timing=root.find("p:timing",NS)
    if timing is None:
        return [],[]
    groups=[]
    main=timing.find(".//p:cTn[@nodeType='mainSeq']",NS)
    if main is not None:
        for gpar in main.findall("p:childTnLst/p:par",NS):
            gctn=gpar.find("p:cTn",NS)
            effects=[]
            for bpar in gctn.findall("p:childTnLst/p:par",NS):
                bctn=bpar.find("p:cTn",NS)
                bstart=_delay(bctn)
                for ectn in bctn.iter(_q(P,"cTn")):
                    if ectn.get("presetClass"):
                        effects.append(_effect(ectn,bstart))
            if effects:
                trig="click" if effects[0]["node"]=="clickEffect" else "auto"
                groups.append({"trigger":trig,"effects":_merge_segments(effects)})
    inter=[_effect(c,0) for seq in timing.findall(".//p:cTn[@nodeType='interactiveSeq']",NS)
           for c in seq.iter(_q(P,"cTn")) if c.get("presetClass")]
    return groups,inter


def morph_duration(root):
    for tr in root.iter(_q(P,"transition")):
        if tr.find(_q(P159,"morph")) is not None:
            d=tr.get(_q(P14,"dur")) or tr.get("dur")
            if d and d.isdigit():
                return int(d)
            return {"fast":500,"med":750,"slow":1000}.get(tr.get("spd","med"),750)
    return None


def role(eff):
    """Design-system role of an effect, or None when it has no duration to grade."""
    if eff["repeat"]=="indefinite" or (isinstance(eff["repeat"],(int,float)) and eff["repeat"]>3):
        return "ambient"
    if eff["dur"]<=1 or (eff["cls"] in ("entr","exit") and eff["pid"]==1):
        return None  # Appear / Disappear, instant sets (counter proxies)
    if eff["cls"] in ("path","emph") and eff["spatial"] and eff["dur"]>=3000:
        return "ambient"  # a slow one-shot drift (Ken Burns), not a move
    if eff["cls"]=="emph" and eff["spatial"] and eff.get("segments",1)>1:
        return "move"  # a keyframed scale/rotation chain is a transformation, not a pulse
    return {"entr":"enter","exit":"exit","emph":"emphasis","path":"move"}.get(eff["cls"])


class Colours:
    """Theme-aware colour resolution for one slide (scheme colours, colour
    map, lumMod/lumOff/tint/shade), enough to measure contrast."""

    def __init__(self,pkg,slide_part):
        self.pkg=pkg
        rels=pkg.rels(slide_part)
        layout=next((pkg.resolve(slide_part,r.get("Target")) for r in rels if r.get("Type","").endswith("/slideLayout")),None)
        master=next((pkg.resolve(layout,r.get("Target")) for r in pkg.rels(layout)
                     if r.get("Type","").endswith("/slideMaster")),None) if layout else None
        self.chain=[slide_part]+[p for p in (layout,master) if p]
        self.master=pkg.xml(master) if master else None
        self.layout=pkg.xml(layout) if layout else None
        self.scheme={}
        if master:
            theme=next((pkg.resolve(master,r.get("Target")) for r in pkg.rels(master) if r.get("Type","").endswith("/theme")),None)
            if theme:
                cs=pkg.xml(theme).find(".//a:clrScheme",NS)
                for node in (cs if cs is not None else []):
                    c=node.find("a:srgbClr",NS)
                    c=c.get("val") if c is not None else (node.find("a:sysClr",NS).get("lastClr") if node.find("a:sysClr",NS) is not None else None)
                    if c:
                        self.scheme[E.QName(node).localname]=c.upper()
        cmap=self.master.find("p:clrMap",NS) if self.master is not None else None
        self.cmap=dict(cmap.attrib) if cmap is not None else {"bg1":"lt1","tx1":"dk1","bg2":"lt2","tx2":"dk2"}

    def _mods(self,hexv,node):
        r,g,b=(int(hexv[i:i+2],16)/255 for i in (0,2,4))
        h,l,s=colorsys.rgb_to_hls(r,g,b)
        for m in node:
            tag=E.QName(m).localname
            v=int(m.get("val","100000"))/100000
            if tag=="lumMod":
                l*=v
            elif tag=="lumOff":
                l+=v
            elif tag=="tint":
                l=l+(1-l)*(1-v)
            elif tag=="shade":
                l*=v
        r,g,b=colorsys.hls_to_rgb(h,max(0,min(1,l)),s)
        return f"{round(r*255):02X}{round(g*255):02X}{round(b*255):02X}"

    def of(self,fill):
        """Hex of an a:solidFill (or a colour element); None when not solid."""
        if fill is None:
            return None
        node=fill if E.QName(fill).localname in ("srgbClr","schemeClr","sysClr","prstClr") else next(iter(fill),None)
        if node is None:
            return None
        tag=E.QName(node).localname
        if tag=="srgbClr":
            base=node.get("val")
        elif tag=="sysClr":
            base=node.get("lastClr")
        elif tag=="schemeClr":
            name=node.get("val")
            base=self.scheme.get(self.cmap.get(name,name)) or self.scheme.get(name)
        elif tag=="prstClr":
            base={"white":"FFFFFF","black":"000000"}.get(node.get("val"))
        else:
            base=None
        return self._mods(base.upper(),node) if base else None

    def background(self):
        for part in self.chain:
            bg=self.pkg.xml(part).find("p:cSld/p:bg",NS)
            if bg is None:
                continue
            fill=bg.find("p:bgPr/a:solidFill",NS)
            if fill is not None:
                return self.of(fill)
            ref=bg.find("p:bgRef",NS)
            if ref is not None and len(ref):
                return self.of(ref[0])
            return None  # picture or gradient
        return self.scheme.get(self.cmap.get("bg1","lt1"),"FFFFFF")

    def text(self,shape,para,run):
        """Effective text colour: run > paragraph > shape list style >
        placeholder (layout, master) > master text style > tx1."""
        for node in (run.find("a:rPr",NS) if run is not None else None,):
            f=node.find("a:solidFill",NS) if node is not None else None
            if f is not None:
                return self.of(f)
        ppr=para.find("a:pPr",NS)
        level=int(ppr.get("lvl","0")) if ppr is not None else 0
        def from_lst(lst):
            if lst is None:
                return None
            f=lst.find(f"a:lvl{level+1}pPr/a:defRPr/a:solidFill",NS)
            return self.of(f) if f is not None else None
        c=from_lst(shape.find("p:txBody/a:lstStyle",NS))
        if c:
            return c
        ph=shape.find("./p:nvSpPr/p:nvPr/p:ph",NS)
        if ph is not None:
            for root in (self.layout,self.master):
                node=mstu.TypeResolver._ph_node(None,root,ph)
                if node is not None:
                    c=from_lst(node.find("p:txBody/a:lstStyle",NS))
                    if c:
                        return c
            if self.master is not None:
                kind=ph.get("type") or "obj"
                style={"title":"titleStyle","ctrTitle":"titleStyle"}.get(kind,"bodyStyle" if kind in ("body","obj","subTitle") else "otherStyle")
                c=from_lst(self.master.find(f"p:txStyles/p:{style}",NS))
                if c:
                    return c
        style=shape.find("p:style/a:fontRef",NS)
        if style is not None and len(style):
            return self.of(style[0])
        return self.scheme.get(self.cmap.get("tx1","dk1"),"000000")

    def shape_fill_alpha(self,shape):
        """(fill, alpha): alpha from an a:alpha on the solid fill colour."""
        col=self.shape_fill(shape)
        node=shape.find("p:spPr/a:solidFill",NS)
        alpha=1.0
        if node is not None and len(node):
            a=node[0].find("a:alpha",NS)
            if a is not None and (a.get("val") or "").isdigit():
                alpha=int(a.get("val"))/100000
        return col,alpha

    def shape_fill(self,shape):
        sppr=shape.find("p:spPr",NS)
        if sppr is None:
            return None
        f=sppr.find("a:solidFill",NS)
        if f is not None:
            return self.of(f)
        if sppr.find("a:gradFill",NS) is not None or sppr.find("a:blipFill",NS) is not None or sppr.find("a:pattFill",NS) is not None:
            return "NONSOLID"
        if sppr.find("a:noFill",NS) is not None:
            return None
        ref=shape.find("p:style/a:fillRef",NS)
        if ref is not None and ref.get("idx","0")!="0" and len(ref):
            return self.of(ref[0])
        return None


def _blend(top,under,alpha):
    return "".join(f"{round(int(top[i:i+2],16)*alpha+int(under[i:i+2],16)*(1-alpha)):02X}" for i in (0,2,4))


def _family(name,theme_fonts):
    if not name:
        return None
    if name.startswith("+"):
        name=theme_fonts.get(name[1:3],name)
    words=[w for w in name.split() if w.lower() not in WEIGHT_WORDS]
    return " ".join(words) or name


def _theme_fonts(pkg,slide_part):
    rels=pkg.rels(slide_part)
    layout=next((pkg.resolve(slide_part,r.get("Target")) for r in rels if r.get("Type","").endswith("/slideLayout")),None)
    master=next((pkg.resolve(layout,r.get("Target")) for r in pkg.rels(layout) if r.get("Type","").endswith("/slideMaster")),None) if layout else None
    theme=next((pkg.resolve(master,r.get("Target")) for r in pkg.rels(master) if r.get("Type","").endswith("/theme")),None) if master else None
    out={}
    if theme:
        fs=pkg.xml(theme).find(".//a:fontScheme",NS)
        if fs is not None:
            for key,tag in (("mj","majorFont"),("mn","minorFont")):
                lat=fs.find(f"a:{tag}/a:latin",NS)
                if lat is not None:
                    out[key]=lat.get("typeface")
    return out


def _frames(images,aspect):
    """Settled frame of each slide image. A PowerPoint render strip
    (slide_forge render) holds several frames side by side, and its last one
    can be the transition into the next slide; the settled state is the frame
    with the most content (least background)."""
    from PIL import Image
    out=[]
    for path in images:
        im=Image.open(path).convert("RGB")
        n=max(1,round(im.width/(im.height*aspect)))
        w=im.width//n
        frames=[im.crop((k*w,0,(k+1)*w,im.height)) for k in range(n)]
        out.append(min(frames,key=lambda f:frame_metrics(f,light=True)["background_share"]))
    return out


def frame_metrics(img,light=False):
    """Background share, balance offset and Hasler-Suesstrunk colourfulness."""
    small=img.resize((160,90))
    px=list(small.getdata()) if not hasattr(small,"get_flattened_data") else list(small.get_flattened_data())
    bg=Counter(px).most_common(1)[0][0]
    ink=[(i%160,i//160) for i,p in enumerate(px) if sum(abs(a-b) for a,b in zip(p,bg))>60]
    share=1-len(ink)/len(px)
    if light:
        return {"background_share":share}
    if ink:
        cx=sum(x for x,_ in ink)/len(ink)/160
        cy=sum(y for _,y in ink)/len(ink)/90
        bal=((cx-0.5)**2+(cy-0.5)**2)**0.5
    else:
        bal=0.0
    mid=img.resize((320,180))
    data=list(mid.getdata()) if not hasattr(mid,"get_flattened_data") else list(mid.get_flattened_data())
    rg=[r-g for r,g,_ in data]
    yb=[(r+g)/2-b for r,g,b in data]
    colourful=math.hypot(statistics.pstdev(rg),statistics.pstdev(yb))+0.3*math.hypot(statistics.mean(rg),statistics.mean(yb))
    return {"background_share":round(share,3),"balance_offset":round(bal,3),"colourfulness":round(colourful,1)}


def render_lo(pptx,out_dir):
    soffice=shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice or not shutil.which("pdftoppm"):
        raise RuntimeError("LibreOffice render needs soffice and pdftoppm")
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    subprocess.run([soffice,"--headless","--convert-to","pdf","--outdir",str(out_dir),str(pptx)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
    pdf=out_dir/(Path(pptx).stem+".pdf")
    subprocess.run(["pdftoppm","-png","-scale-to-x","640","-scale-to-y","-1",str(pdf),str(out_dir/"slide")],check=True,timeout=600)
    pngs=sorted(out_dir.glob("slide-*.png"))
    return pngs


def critique(path,render=None,xsd=None):
    path=Path(path)
    model=md.deck_model(path)
    pkg=mstu.Package(path)
    parts=pkg.slides()
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    aspect=W/H
    preset_names={}
    lib=Path(__file__).resolve().parents[1]/"knowledge"/"powerpoint_presets.json"
    if lib.is_file():
        for p in json.loads(lib.read_text(encoding="utf-8"))["presets"]:
            preset_names.setdefault((p["presetClass"],int(p["presetID"])),p["name"])
    checks=[]
    issues=[]
    slides=[]

    def check(code,grade,slide=None,obj=None,measured=None,expected=None,detail=""):
        checks.append((code,grade,slide is None))
        if grade!="good":
            fix,tool=FIX.get(code,("",""))
            issues.append({"code":code,"dimension":DIMENSION.get(code,"design"),"severity":grade,"slide":slide,
                           "object":obj,"measured":measured,"expected":expected,"detail":detail,"fix":fix,"tool":tool})

    deck_kinds=Counter()
    unknown_presets={}
    sizes_all=Counter()
    families=Counter()
    title_sizes=[]
    static=[]
    content=0
    schema=None
    if xsd:
        schema=E.XMLSchema(E.parse(str(xsd)))
    for s,part in zip(model["slides"],parts):
        root=pkg.xml(part)
        idx=s["index"]
        colours=Colours(pkg,part)
        resolver=mstu.TypeResolver(pkg,part)
        fonts=_theme_fonts(pkg,part)
        bg=colours.background()
        nodes=mstu.shape_nodes(root)
        objs={o["id"]:o for o in s["objects"]}
        info={"slide":idx,"words":0,"sizes":[],"effects":0,"clicks":0,"max_movers":0}

        def visible(o):
            g=o.get("geometry")
            return not g or (g["x"]+g["w"]>0.001 and g["x"]<0.999 and g["y"]+g["h"]>0.001 and g["y"]<0.999)

        def behind(o):
            """Solid colour behind object ``o``: the smallest filled shape below it containing its centre, else the slide."""
            g=o.get("geometry")
            if not g:
                return bg
            cx,cy=g["x"]+g["w"]/2,g["y"]+g["h"]/2
            best=None
            for other in s["objects"]:
                og=other.get("geometry")
                if other is o or not og or other["z"]>=o["z"] or not other.get("filled"):
                    continue
                if og["x"]<=cx<=og["x"]+og["w"] and og["y"]<=cy<=og["y"]+og["h"]:
                    if best is None or og["w"]*og["h"]<best[0]:
                        best=(og["w"]*og["h"],other)
            if best:
                node=nodes.get(best[1]["id"])
                if node is None:
                    return None
                col,alpha=colours.shape_fill_alpha(node)
                if col and col!="NONSOLID" and alpha<0.99:
                    under=behind(best[1])  # a tint: blend with what is behind it
                    return _blend(col,under,alpha) if under and under!="NONSOLID" else None
                return col
            return bg

        # ---- design: text, type, colour, density, safe area
        texty=[o for o in s["objects"] if o.get("has_text_body") and (o.get("text") or "").strip()
               and not (o["name"] or "").startswith(("__gen_","__counter_")) and visible(o)]
        if len([o for o in s["objects"] if visible(o) and not (o["name"] or "").startswith(("__gen_","__counter_"))
                and not (o.get("placeholder") and o["placeholder"]["type"] in md.TITLE_TYPES)])>=2:
            content+=1
            is_content=True
        else:
            is_content=False
        for o in texty:
            node=nodes.get(o["id"])
            if node is None:
                continue
            info["words"]+=len((o.get("text") or "").split())
            own,own_alpha=colours.shape_fill_alpha(node) if o.get("filled") else (None,1.0)
            back=own if own and own_alpha>=0.99 else behind(o)
            is_title=bool(o.get("placeholder") and o["placeholder"]["type"] in md.TITLE_TYPES)
            worst=None
            for para in node.iter(_q(A,"p")):
                for run in para.findall("a:r",NS):
                    if not (run.findtext("a:t",namespaces=NS) or "").strip():
                        continue
                    pt=resolver.size(node,para,run)/100
                    sizes_all[round(pt)]+=len(run.findtext("a:t",namespaces=NS))
                    info["sizes"].append(round(pt,1))
                    if is_title:
                        title_sizes.append(pt)
                    rpr=run.find("a:rPr",NS)
                    lat=rpr.find("a:latin",NS) if rpr is not None else None
                    fam=_family(lat.get("typeface") if lat is not None else ("+mj" if is_title else "+mn"),fonts)
                    if fam:
                        families[fam]+=1
                    col=colours.text(node,para,run)
                    if col and back and back!="NONSOLID":
                        bold=rpr is not None and rpr.get("b")=="1"
                        need=ds.text_contrast_needed(pt,bold)
                        ratio=ds.contrast(col,back)
                        if worst is None or ratio/need<worst[0]/worst[1]:
                            worst=(ratio,need,col,back)
            if worst:
                ratio,need,col,back_c=worst
                check("COL-TEXT","good" if ratio>=need else "warn",idx,o["name"],round(ratio,2),f">= {need}",f"{col} on {back_c}")
            g=o.get("geometry")
            if g:
                off=g["x"]<-0.005 or g["y"]<-0.005 or g["x"]+g["w"]>1.005 or g["y"]+g["h"]>1.005
                if s.get("scene"):
                    continue  # Morph scene slides (camera, pan) crop on purpose
                check("LAY-SAFE","warn" if off else "good",idx,o["name"],
                      [round(g["x"],3),round(g["y"],3),round(g["x"]+g["w"],3),round(g["y"]+g["h"],3)],"inside the slide")
        for o in s["objects"]:
            name=o["name"] or ""
            if not name.startswith("__gen_"):
                continue
            kind=name[len("__gen_"):].rsplit("_",1)[0]
            node=nodes.get(o["id"])
            if kind in EXEMPT_GRAPHIC or node is None:
                continue
            sppr=node.find("p:spPr",NS)
            fill=sppr.find("a:ln/a:solidFill",NS) if kind in ("orbit-ring","highlight-frame","arrow","callout") else None
            if fill is None and sppr is not None:
                fill=sppr.find("a:solidFill",NS)
                if fill is None:
                    gs=sppr.find("a:gradFill/a:gsLst/a:gs",NS)
                    fill=gs if gs is not None else None
            col=colours.of(fill) if fill is not None else None
            back=behind(o)
            if col and back and back!="NONSOLID":
                ratio=ds.contrast(col,back)
                need=ds.graphic_contrast_needed()
                check("COL-GRAPHIC","good" if ratio>=need else "warn",idx,name,round(ratio,2),f">= {need}",f"{col} on {back}")
        if is_content:
            check("DEN-WORDS",ds.grade(info["words"],ds.load()["density"]["words_per_slide"]),idx,None,info["words"],
                  ds.load()["density"]["words_per_slide"]["band"])

        # ---- motion and rhythm
        groups,inter=slide_timing(root)
        effects=[e for g in groups for e in g["effects"]]+inter
        info["effects"]=len(effects)
        clicks=sum(1 for g in groups if g["trigger"]=="click")
        info["clicks"]=clicks
        mdur=morph_duration(root)
        if mdur is not None:
            check("MOT-DURATION",ds.grade(mdur,ds.duration("morph")),idx,"Morph transition",mdur,ds.duration("morph")["band"])
        if is_content and not effects and mdur is None:
            static.append(idx)
        if effects:
            check("MOT-CLICKS",ds.grade(clicks,ds.rhythm("clicks_per_slide")),idx,None,clicks,ds.rhythm("clicks_per_slide")["band"])
        titles={o["id"] for o in s["objects"] if o.get("placeholder") and o["placeholder"]["type"] in md.TITLE_TYPES}
        for e in effects:
            deck_kinds[(e["cls"],e["pid"] if e["cls"]!="path" else 0)]+=1
            r=role(e)
            label=objs.get(e["spid"],{}).get("name") if e["spid"] else None
            if e["cls"] in ("entr","exit","emph") and e["pid"] and preset_names and (e["cls"],e["pid"]) not in preset_names:
                unknown_presets.setdefault((e["cls"],e["pid"]),idx)
            if r=="ambient":
                if e["repeat"]=="indefinite":
                    cycle=e["dur"]*(2 if e["auto_rev"] else 1)
                    check("MOT-AMBIENT",ds.grade(cycle,ds.duration("ambient_cycle")),idx,label,cycle,ds.duration("ambient_cycle")["band"])
                continue
            if r is None:
                continue
            if e["iterate"] and e["iterate"].get("gap_ms") is not None:
                spec=ds.duration("letter_gap" if e["iterate"]["by"]=="lt" else "word_gap")
                check("MOT-DURATION",ds.grade(e["iterate"]["gap_ms"],spec),idx,label,e["iterate"]["gap_ms"],spec["band"],"iteration gap")
            else:
                check("MOT-DURATION",ds.grade(e["dur"],ds.duration(r)),idx,label,e["dur"],ds.duration(r)["band"],r)
            # Slow-in/slow-out is about position (object tracking). A path
            # sampled into many linear segments can encode any speed profile,
            # so only single-segment moves are judged.
            if "animMotion" in e["kinds"] and e.get("segments",1)==1:
                linear=e["accel"]+e["decel"]<=0.001
                check("MOT-EASING","warn" if linear else "good",idx,label,
                      {"accel":e["accel"],"decel":e["decel"]},"accel or decel > 0 (slow-in/slow-out)")
            if e["spid"] in titles and idx>1:
                check("MOT-TITLE","note",idx,label,e["cls"],"no in-slide motion on titles")
        for g in groups:
            live=[e for e in g["effects"] if role(e) not in ("ambient",None)]
            check("MOT-EFFECTS",ds.grade(len(live),ds.rhythm("effects_per_click")),idx,None,len(live),ds.rhythm("effects_per_click")["band"])
            movers=[e for e in live if e["spatial"] and e["dur"]>0]
            peak=0
            for t in sorted({e["start"] for e in movers}):
                active={(e["start"],e["end"],e["sig"] or e["pid"],e["cls"]) for e in movers if e["start"]<=t<e["end"]}
                peak=max(peak,len(active))
            info["max_movers"]=max(info["max_movers"],peak)
            if movers:
                check("MOT-MOVERS",ds.grade(peak,ds.rhythm("movers_per_click")),idx,None,peak,ds.rhythm("movers_per_click")["band"])
            chains={}
            for e in live:
                chains.setdefault((e["cls"],e["pid"]),[]).append(e["start"])
            for key,starts in chains.items():
                starts=sorted(starts)
                gaps=[b-a for a,b in zip(starts,starts[1:]) if 0<b-a<=400]
                if len(starts)>=3 and len(gaps)>=2:
                    gap=statistics.median(gaps)
                    check("MOT-STAGGER",ds.grade(gap,ds.duration("stagger")),idx,None,gap,ds.duration("stagger")["band"])
        if schema is not None:
            ok=schema.validate(E.ElementTree(root))
            check("TEC-SCHEMA","good" if ok else "warn",idx,None,
                  None if ok else str(schema.error_log.last_error.message)[:160],"valid ISO 29500 PresentationML")
        slides.append(info)

    # ---- deck level
    if content:
        share=len(static)/content
        check("MOT-STATIC","good" if share<=ds.rhythm("static_slide_share_max") else "warn",None,None,
              {"static":static,"content_slides":content},f"<= {ds.rhythm('static_slide_share_max'):.0%} of content slides")
    for (cls,pid),first in unknown_presets.items():
        check("TEC-PRESET","note",first,None,f"{cls}:{pid}","a PowerPoint preset id (knowledge/powerpoint_presets.json)")
    kinds=len(deck_kinds)
    if kinds:
        check("MOT-VOCAB",ds.grade(kinds,ds.rhythm("effect_kinds_per_deck")),None,None,kinds,ds.rhythm("effect_kinds_per_deck")["band"],
              ", ".join(f"{preset_names.get(k,'%s:%s'%k)}" for k,_ in deck_kinds.most_common(8)))
    try:
        for row in mstu.settle_report(path):
            check("MOT-SETTLE","warn",row["slide"],", ".join(o["object"] for o in row["objects"][:4]),
                  [o["ends"] for o in row["objects"][:4]],"authored layout before Morph")
    except Exception as ex:  # a settle check must not break the critique
        issues.append({"code":"MOT-SETTLE","dimension":"rhythm","severity":"note","slide":None,"object":None,
                       "measured":None,"expected":None,"detail":f"settle check failed: {ex}","fix":"","tool":""})
    typ=ds.load()["type"]
    if sizes_all:
        distinct=sorted(sizes_all)
        check("TYP-SIZES",ds.grade(len(distinct),typ["sizes_per_deck"]),None,None,len(distinct),typ["sizes_per_deck"]["band"],
              f"sizes {distinct}")
        body=max((sz for sz in sizes_all if not title_sizes or sz<max(title_sizes)),key=lambda sz:sizes_all[sz],default=None)
        if body:
            check("TYP-SMALL",ds.grade(body,typ["body_min_pt"]),None,None,body,typ["body_min_pt"]["band"],"most used body size")
            small=min(distinct)
            if small<typ["body_min_pt"]["limit"][0]:
                check("TYP-SMALL","warn",None,None,small,f">= {typ['body_min_pt']['limit'][0]}","smallest text")
            if title_sizes:
                ratio=round(statistics.median(title_sizes)/body,2)
                check("TYP-RATIO",ds.grade(ratio,typ["title_to_body"]),None,None,ratio,typ["title_to_body"]["band"],"title / body")
    if families:
        check("TYP-FAMILIES",ds.grade(len(families),typ["families_per_deck"]),None,None,len(families),
              typ["families_per_deck"]["band"],", ".join(families))

    frame=[]
    if render:
        lay=ds.load()["layout"]
        with tempfile.TemporaryDirectory() as td:
            if str(render)=="lo":
                images=render_lo(path,td)
            else:
                images=sorted(Path(render).glob("slide-*.png"))
            for i,img in enumerate(_frames(images,aspect),1):
                m=frame_metrics(img)
                m["slide"]=i
                frame.append(m)
                check("LAY-DENSITY",ds.grade(m["background_share"],lay["frame_background_share"]),i,None,
                      m["background_share"],lay["frame_background_share"]["band"],"background share of the settled frame")
                check("LAY-BALANCE",ds.grade(m["balance_offset"],lay["balance_offset"]),i,None,m["balance_offset"],
                      lay["balance_offset"]["band"])
                check("COL-COLOURFUL",ds.grade(m["colourfulness"],lay["colourfulness"]),i,None,m["colourfulness"],
                      lay["colourfulness"]["band"],"Hasler-Suesstrunk")

    # Deck-level findings (a static or monotone deck) weigh as much as all
    # slide-level checks of the same dimension together, so many passing
    # slide checks cannot hide a deck-wide problem.
    def part_score(got):
        good=sum(g=="good" for g in got)
        note=sum(g=="note" for g in got)
        return 1+4*(good+0.5*note)/len(got)
    scores={}
    for dim in ("design","motion","rhythm","coherence","technique"):
        halves=[part_score(got) for got in ([g for c,g,d in checks if DIMENSION.get(c)==dim and not d],
                                            [g for c,g,d in checks if DIMENSION.get(c)==dim and d]) if got]
        if halves:
            scores[dim]=round(statistics.mean(halves),2)
    scores["overall"]=round(statistics.mean(v for v in scores.values()),2) if scores else None
    counts=Counter(i["severity"] for i in issues)
    for info in slides:
        info["sizes"]=sorted(set(info["sizes"]))
    # Object lifecycles (an object with two or more effects: enter -> dim ->
    # exit ...) are where real complexity lives (knowledge/README, T027).
    lifecycles=0
    for part in parts:
        per=Counter(e["spid"] for g in slide_timing(pkg.xml(part))[0] for e in g["effects"] if e["spid"])
        lifecycles+=sum(1 for n in per.values() if n>=2)
    return {"design_system":ds.load()["version"],"scores":scores,
            "checks":len(checks),"issues_by_severity":dict(counts),
            "issues_by_code":dict(Counter(i["code"] for i in issues if i["severity"]=="warn")),
            "issues":issues,"slides":slides,"frames":frame,
            "deck":{"slides":len(slides),"content_slides":content,"static_slides":static,"lifecycles":lifecycles,
                    "effect_kinds":kinds,"type_sizes":sorted(sizes_all),"families":dict(families)},
            "path":str(path)}


def markdown(v):
    s=v["scores"]
    lines=[f"# Design critique: {Path(v['path']).name}","",
           f"Design system {v['design_system']} · {v['checks']} checks · "
           +", ".join(f"{k} {n}" for k,n in sorted(v["issues_by_severity"].items())),"",
           "| " + " | ".join(s) + " |","|"+"---|"*len(s),"| " + " | ".join(str(x) for x in s.values()) + " |",""]
    warns=[i for i in v["issues"] if i["severity"]=="warn"]
    notes=[i for i in v["issues"] if i["severity"]=="note"]
    for title,rows in (("Warnings",warns),("Notes",notes)):
        if not rows:
            continue
        lines+=[f"## {title}",""]
        for i in rows[:60]:
            where=f"slide {i['slide']}" if i["slide"] else "deck"
            obj=f" `{i['object']}`" if i["object"] else ""
            lines.append(f"- **{i['code']}** {where}{obj}: {i['measured']} (expected {i['expected']}) {i['detail']} → {i['fix']}")
        if len(rows)>60:
            lines.append(f"- … {len(rows)-60} more")
        lines.append("")
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx",type=Path)
    ap.add_argument("--render",help="'lo' to render with LibreOffice, or a directory of slide-NN.png")
    ap.add_argument("--xsd",type=Path,default=os.environ.get("PPTX_PML_XSD"))
    ap.add_argument("--md",type=Path)
    ap.add_argument("-o","--output",type=Path)
    a=ap.parse_args()
    v=critique(a.pptx,a.render,a.xsd)
    text=json.dumps(v,indent=1,ensure_ascii=False,default=list)
    if a.output:
        a.output.write_text(text+"\n",encoding="utf-8")
    else:
        print(text)
    if a.md:
        a.md.write_text(markdown(v)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
