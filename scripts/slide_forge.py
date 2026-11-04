#!/usr/bin/env python3
"""Slide Forge — an agent-facing deck compiler (T025).

An AI writes a semantic deck spec (JSON); Forge turns it into a finished,
editable, motion-directed PPTX and a machine-readable QA verdict. Nothing here
is meant for a human to click through: every input is declarative, every
failure is a coded error with a fix hint, and the loop is
``spec -> build -> qa -> (repair spec) -> build``.

    slide_forge.py schema                      # spec contract as JSON
    slide_forge.py build SPEC.json -o OUT.pptx # layout + art + motion + QA
    slide_forge.py qa OUT.pptx                 # QA only (any PPTX)
    slide_forge.py render OUT.pptx -d DIR      # PowerPoint render -> MP4 + per-slide strips

Layouts: title, section, statement, bullets, image, kpis, process, cycle,
chart, comparison, quote, closing. Layout geometry is chosen so the Motion
Director recognises the structure (cards, process rows, cycles, charts) and
choreographs it; pictures get Ken Burns and accents draw in (T024). Shared
``!!`` background orbs move between slides so Morph adds a motion-graphic
layer across the deck.

T063: type sizes come from the Office kit's ``type_scale_pt`` (3-6 sizes per
deck), count-up stacks keep only the final value in print/PDF/Morph (the
source is topmost and opaque), and highlight markers follow paragraph
alignment. Ken Burns releases back to the authored frame before Morph.
"""
import argparse
import copy
import hashlib
import io
import json
import math
import random
import re
import sys
from pathlib import Path

from lxml import etree as E
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

sys.path.insert(0,str(Path(__file__).resolve().parent))

VERSION="forge-0.2"
W,H=13.333,7.5
MARGIN=0.7
THEMES={
    "midnight":{"bg":"0F172A","surface":"1E293B","text":"F8FAFC","muted":"94A3B8","accent":"38BDF8","accent2":"F472B6"},
    "paper":{"bg":"FAF7F2","surface":"FFFFFF","text":"1F2A44","muted":"5B6472","accent":"B4532F","accent2":"0F766E"},
    "forest":{"bg":"0B1F17","surface":"13342A","text":"ECFDF5","muted":"A7B5AE","accent":"34D399","accent2":"FBBF24"},
    "sunrise":{"bg":"FFF7ED","surface":"FFFFFF","text":"431407","muted":"7C5A48","accent":"C2410C","accent2":"7C3AED"},
}
FONTS={"head":"Segoe UI Semibold","body":"Segoe UI"}
KITS_PATH=Path(__file__).resolve().parents[1]/"knowledge"/"office_design_kits.json"
# Fonts with complete Vietnamese coverage (Latin Extended Additional).
VI_SAFE_FONTS={"segoe ui","segoe ui semibold","arial","calibri","calibri light","cambria","times new roman",
               "tahoma","verdana","aptos","aptos display","georgia"}


def _mix(a,b,t):
    return "".join(f"{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02X}" for i in (0,2,4))


def _contrast(a,b):
    """WCAG contrast ratio (shared with the design system, T034)."""
    import design_system
    return design_system.contrast(a,b)


def _legible(color,bgs,toward):
    """Nudge a colour toward ``toward`` until it reaches 4.5:1 on every bg."""
    c=color
    for step in range(1,21):
        if all(_contrast(c,b)>=4.5 for b in bgs):
            return c
        c=_mix(color,toward,step/20)
    return c


def office_theme(name,mode="light"):
    """Theme + fonts from a Microsoft Office designer theme (office_design_dna.py)."""
    kits={k["name"].lower():k for k in json.loads(KITS_PATH.read_text(encoding="utf-8"))["themes"]}
    kit=kits[name.lower()]
    c=kit["colors"]
    if mode=="dark":
        bg,text=c.get("dk2") or c["dk1"],c.get("lt1") or "FFFFFF"
        for step in range(1,11):  # mid-tone dk2 (Retrospect, Wisp): deepen until white text is 7:1
            if _contrast(text,bg)>=7:
                break
            bg=_mix(c.get("dk2") or c["dk1"],"000000",step/10)
    else:
        bg,text=c.get("lt1") or "FFFFFF",c.get("dk2") or c["dk1"]
    if _contrast(text,bg)<7:
        text=c["dk1"] if mode!="dark" else "FFFFFF"
    surface=_mix(bg,text,0.06)
    theme={"bg":bg,"surface":surface,"text":text,
           "muted":_legible(_mix(text,bg,0.35),[bg,surface],text),
           "accent":_legible(c["accent1"],[bg,surface],text),
           "accent2":_legible(c["accent2"],[bg,surface],text)}
    fonts={"head":kit["fonts"]["majorFont"],"body":kit["fonts"]["minorFont"]}
    return theme,fonts,kit


def _walk_keys(obj,key):
    if isinstance(obj,dict):
        if key in obj:
            return True
        return any(_walk_keys(v,key) for v in obj.values())
    if isinstance(obj,list):
        return any(_walk_keys(v,key) for v in obj)
    return False


def deck_type_scale(kit=None,spec=None):
    """The deck's type scale, derived from the Office designer kit.

    The kit's ``type_scale_pt`` is the source (Office themes ship 4-5 sizes:
    title + body levels 1..4). Forge collapses it to six semantic levels:
    display, title, subhead, body, label, small. ``body`` is the highest body
    level that still satisfies the design system's 18 pt body minimum, so a
    kit whose second body level is 16 pt (Facet) keeps 18 pt body text and
    uses 16/14/12 for label/small. The display size is the design system's
    ``kpi_stat`` token (72 pt) and is only added when the spec has a KPI, so
    a plain deck stays at 4-5 sizes.
    """
    import design_system as ds
    system=ds.load()
    if kit is None:
        kits={k["name"].lower():k for k in json.loads(KITS_PATH.read_text(encoding="utf-8"))["themes"]}
        kit=kits.get("office theme") or next(iter(kits.values()))
    ts=kit.get("type_scale_pt") or {"title":36.0,"body_l1":18.0,"body_l2":16.0,"body_l3":14.0,"body_l4":12.0}
    title=float(ts.get("title",36.0))
    bodies=sorted({float(v) for k,v in ts.items() if str(k).startswith("body")},reverse=True)
    body=next((v for v in bodies[1:] if v>=18),None)
    if body is None:
        body=max(18.0,bodies[0]) if bodies else 24.0
    subhead=bodies[0] if bodies and bodies[0]>body else body
    label=max([v for v in bodies if v<body],default=body)
    small=min(bodies) if bodies else label
    # Kickers, captions and stage labels need one step below body. The kit's
    # smallest body level can be 18 pt; the design system's body_base token
    # (14 pt) is the cap, never below the 12 pt caption floor.
    tokens=system.get("color_and_type_scales",{}).get("modular_scale",{}).get("tokens_pt",{})
    small=max(12,min(small,float(tokens.get("body_base",14))))
    scale={"title":title,"subhead":subhead,"body":body,"label":label,"small":small}
    has_stats=(spec is not None and (_walk_keys(spec.get("slides") or [],"kpi")
               or any(isinstance(s,dict) and s.get("layout") in ("kpis","duarte_break") for s in spec.get("slides") or [])))
    if has_stats:
        scale["display"]=max(float(tokens.get("kpi_stat",72)),title)
    return {k:int(round(v)) for k,v in scale.items()}
LAYOUTS={
    "title":{"required":["title"],"optional":["subtitle","image","kicker"]},
    "section":{"required":["title"],"optional":["kicker"]},
    "statement":{"required":["text"],"optional":["kicker"]},
    "bullets":{"required":["title","bullets"],"optional":["image"]},
    "image":{"required":["image"],"optional":["title","caption"]},
    "kpis":{"required":["title","items"],"optional":["takeaway"]},
    "process":{"required":["title","steps"],"optional":["takeaway"]},
    "cycle":{"required":["title","items"],"optional":["center"]},
    "chart":{"required":["title","chart"],"optional":["takeaway"]},
    "comparison":{"required":["title","left","right"],"optional":[]},
    "quote":{"required":["quote"],"optional":["author"]},
    "closing":{"required":["title"],"optional":["subtitle"]},
    "asymmetric":{"required":["title","major","minor"],"optional":["kicker","reverse"]},
    "bento":{"required":["title","hero","top_right","bottom_right_1","bottom_right_2"],"optional":["kicker"]},
    "duarte_break":{"required":[],"optional":["statement","kpi","label","theme_invert","text"]},
}
CHART_TYPES={"column":XL_CHART_TYPE.COLUMN_CLUSTERED,"bar":XL_CHART_TYPE.BAR_CLUSTERED,
             "line":XL_CHART_TYPE.LINE_MARKERS,"pie":XL_CHART_TYPE.PIE,"doughnut":XL_CHART_TYPE.DOUGHNUT,
             "stacked":XL_CHART_TYPE.COLUMN_STACKED,"area":XL_CHART_TYPE.AREA}
LIMITS={"bullets":6,"kpis":4,"process":6,"cycle":6,"points":5}


# ---------------------------------------------------------------------------
# Spec contract


def schema():
    return {
        "version":VERSION,
        "deck":{"title":"str (optional)","theme_mode":"light|dark for office:* and seed themes","assets_cache":"dir for downloaded photos/icons (default ~/.cache/slide-forge)",
                "credits_slide":"bool, closing slide attributing licensed photos (default true)","theme":f"one of {sorted(THEMES)}, office:<Name>, {{\"seed\": \"#brandhex\", \"mode\"?: \"dark\", \"harmony\"?: 150}} "
                         "(OKLCH palette from one brand colour, AA guaranteed) or an object with the same color keys (hex)",
                "fonts":{"head":"font family","body":"font family"},
                "motion":{"style":"subtle|modern|bold|cinematic|dynamic (default modern; dynamic = PowerPoint's richer built-ins)","counters":"bool, count up KPI values (default true; the final value stays topmost in print/PDF/Morph)",
                          "morph":"bool, background orbs glide between slides (default true)"},
                "slides":"list of slide objects"},
        "slide":{"layout":{k:v for k,v in LAYOUTS.items()},"notes":"speaker notes; sequence words (first, then, finally) make process steps one click each"},
        "fields":{"image":"path, or {\"search\":\"english keywords\", \"pick\":n?, \"orientation\"?} for a licensed online photo "
                          "(Openverse CC0/BY/BY-SA, or Pexels with PEXELS_API_KEY; preview with `forge_assets.py photos`), "
                          "or {\"generate\":\"seed words\"} for on-theme abstract art (labelled generated)",
                  "icon":"Iconify name like \"lucide:coffee\" or plain keywords; on kpis items and comparison left/right",
                  "bullets":f"list[str] <= {LIMITS['bullets']}",
                  "items (kpis)":f"list[{{value:str, label:str}}] <= {LIMITS['kpis']}",
                  "steps":f"list[str] 3..{LIMITS['process']}",
                  "items (cycle)":f"list[str] 3..{LIMITS['cycle']}",
                  "chart":f"{{type:{sorted(CHART_TYPES)}, categories:list[str], series:list[{{name, values:list[number]}}], number_format?}}",
                  "left/right":f"{{heading:str, points:list[str] <= {LIMITS['points']}}}"},
        "contract":["Text is never truncated: Forge shrinks type to fit and reports TEXT_SHRUNK; below the floor it fails TEXT_OVERFLOW.",
                    "Every error has code, slide, object, detail and fix; repair the spec, not the PPTX.",
                    "Generated art is abstract and labelled; it never stands in for factual imagery."],
    }


def validate_spec(spec):
    errs=[]
    def err(code,slide,detail,fix):
        errs.append({"code":code,"slide":slide,"detail":detail,"fix":fix})
    if not isinstance(spec,dict) or not isinstance(spec.get("slides"),list) or not spec["slides"]:
        err("SPEC_SHAPE",None,"spec needs a nonempty slides list","see `slide_forge.py schema`")
        return errs
    theme=spec.get("theme","midnight")
    kits=[k["name"] for k in json.loads(KITS_PATH.read_text(encoding="utf-8"))["themes"]] if KITS_PATH.is_file() else []
    if isinstance(theme,str) and theme not in THEMES and not (theme.lower().startswith("office:")
                                                               and theme[7:].lower() in {k.lower() for k in kits}):
        err("THEME_UNKNOWN",None,f"theme {theme!r}",f"use one of {sorted(THEMES)} or office:<{'|'.join(kits)}>")
    if isinstance(theme,dict) and "seed" in theme and not re.fullmatch(r"#?[0-9A-Fa-f]{6}",str(theme["seed"])):
        err("THEME_SEED",None,f"seed {theme['seed']!r}","give the brand colour as #RRGGBB")
    text=json.dumps(spec,ensure_ascii=False)
    if any(ch in text for ch in "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ"):
        fonts={**FONTS,**(office_theme(theme[7:])[1] if isinstance(theme,str) and theme.lower().startswith("office:")
                         and theme[7:].lower() in {k.lower() for k in kits} else {}),**(spec.get("fonts") or {})}
        bad=sorted({f for f in fonts.values() if f.lower() not in VI_SAFE_FONTS})
        if bad:
            err("FONT_GLYPHS",None,f"Vietnamese text with fonts lacking full Vietnamese glyphs: {bad}",
                "set \"fonts\": {\"head\": \"Segoe UI Semibold\", \"body\": \"Segoe UI\"} (or Arial/Calibri/Aptos)")
    style=(spec.get("motion") or {}).get("style","modern")
    if style not in ("subtle","modern","bold","cinematic","dynamic"):
        err("MOTION_STYLE",None,f"style {style!r}","use subtle|modern|bold|cinematic|dynamic")
    for i,s in enumerate(spec["slides"],1):
        lay=s.get("layout") if isinstance(s,dict) else None
        if lay not in LAYOUTS:
            err("LAYOUT_UNKNOWN",i,f"layout {lay!r}",f"use one of {sorted(LAYOUTS)}")
            continue
        for key in LAYOUTS[lay]["required"]:
            if not s.get(key):
                err("FIELD_MISSING",i,f"{lay} needs {key!r}","add the field")
        if lay=="duarte_break" and not (s.get("statement") or s.get("kpi") or s.get("text")):
            err("FIELD_MISSING",i,"duarte_break needs 'statement' or 'kpi'","add statement or kpi")
        n=lambda k:len(s.get(k) or [])
        if lay=="bullets" and n("bullets")>LIMITS["bullets"]:
            err("TOO_DENSE",i,f"{n('bullets')} bullets",f"split into two slides or keep <= {LIMITS['bullets']}")
        if lay=="kpis" and not 1<=n("items")<=LIMITS["kpis"]:
            err("TOO_DENSE",i,f"{n('items')} KPIs",f"use 1..{LIMITS['kpis']}")
        if lay=="process" and not 3<=n("steps")<=LIMITS["process"]:
            err("STRUCTURE",i,f"{n('steps')} steps",f"a process needs 3..{LIMITS['process']} steps")
        if lay=="cycle" and not 3<=n("items")<=LIMITS["cycle"]:
            err("STRUCTURE",i,f"{n('items')} cycle items",f"a cycle needs 3..{LIMITS['cycle']} items")
        if lay=="chart" and s.get("chart"):
            c=s["chart"]
            if c.get("type") not in CHART_TYPES:
                err("CHART_TYPE",i,f"chart type {c.get('type')!r}",f"use one of {sorted(CHART_TYPES)}")
            cats=c.get("categories") or []
            for ser in c.get("series") or []:
                if len(ser.get("values") or [])!=len(cats):
                    err("CHART_DATA",i,f"series {ser.get('name')!r} has {len(ser.get('values') or [])} values for {len(cats)} categories",
                        "give one value per category")
            if not c.get("series"):
                err("CHART_DATA",i,"chart has no series","add series:[{name, values}]")
        if lay=="comparison":
            for side in ("left","right"):
                if s.get(side) and len(s[side].get("points") or [])>LIMITS["points"]:
                    err("TOO_DENSE",i,f"{side} has too many points",f"keep <= {LIMITS['points']}")
        img=s.get("image")
        if isinstance(img,str) and not Path(img).is_file():
            err("IMAGE_MISSING",i,f"no file {img!r}","fix the path, or use {\"search\":\"...\"} / {\"generate\":\"...\"}")
        if isinstance(img,dict) and not (img.get("search") or img.get("generate")):
            err("IMAGE_REF",i,"image object needs search or generate","{\"search\": \"words\", \"pick\": n?}")
    return errs


# ---------------------------------------------------------------------------
# Text fitting


import text_metrics

SAFETY=text_metrics.SAFETY
_FONT_FILES=text_metrics.FONT_FILES  # kept for callers/tests that introspect it


def _font_path(family):
    return text_metrics.font_path(family)


def _font(family,size_pt):
    return text_metrics.load_font(family,size_pt)


def text_lines(text,family,size_pt,width_in,bold=False):
    """Lines after word wrap, or inf when a single word is wider than the box
    (PowerPoint would break it mid-word). Measured with the real font file
    when present; otherwise 0.55 em per character. Shared with the motion
    components (``text_metrics``) so highlights and fitting agree."""
    return text_metrics.wrap_lines(text,family,size_pt,width_in,bold)


def fit_size(paragraphs,family,size_pt,box_w,box_h,floor=12,spacing=1.18,gap_pt=6,bold=False):
    """Largest size <= size_pt whose wrapped text fits the box (inches)."""
    size=size_pt
    while True:
        lines=sum(text_lines(p,family,size,box_w-0.2,bold) for p in paragraphs)
        height=(lines*size*spacing+gap_pt*(len(paragraphs)-1))/72+0.15
        if height<=box_h or size<=floor:
            return size,height<=box_h
        size-=1


# ---------------------------------------------------------------------------
# Generated art


def _hex(c):
    return tuple(int(c[i:i+2],16) for i in (0,2,4))


def generated_art(seed,theme,w=1600,h=1000):
    """On-theme abstract art: soft gradient field with blurred orbs and arcs."""
    rnd=random.Random(hashlib.sha256(seed.encode()).hexdigest())
    a,b,bg=_hex(theme["accent"]),_hex(theme["accent2"]),_hex(theme["surface"])
    img=Image.new("RGB",(w,h),bg)
    px=Image.linear_gradient("L").resize((w,h)).rotate(rnd.choice([0,45,90,135]),expand=False)
    img=Image.composite(Image.new("RGB",(w,h),tuple((x*3+y)//4 for x,y in zip(bg,a))),img,px)
    layer=Image.new("RGBA",(w,h),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    for _ in range(7):
        r=rnd.randint(h//6,h//2)
        x,y=rnd.randint(0,w),rnd.randint(0,h)
        col=rnd.choice([a,b])
        d.ellipse((x-r,y-r,x+r,y+r),fill=col+(rnd.randint(70,150),))
    layer=layer.filter(ImageFilter.GaussianBlur(h//14))
    img=Image.alpha_composite(img.convert("RGBA"),layer)
    d=ImageDraw.Draw(img)
    for i in range(4):
        r=h//3+i*h//10
        cx,cy=rnd.randint(w//4,3*w//4),rnd.randint(h//4,3*h//4)
        d.arc((cx-r,cy-r,cx+r,cy+r),rnd.randint(0,180),rnd.randint(200,340),fill=(255,255,255,90),width=3)
    buf=io.BytesIO()
    img.convert("RGB").save(buf,format="PNG")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Builder


class Builder:
    def __init__(self,spec):
        self.spec=spec
        t=spec.get("theme","midnight")
        kit_fonts={}
        self.kit=None
        if isinstance(t,str) and t.lower().startswith("office:"):
            self.theme,kit_fonts,self.kit=office_theme(t.split(":",1)[1],spec.get("theme_mode","light"))
        elif isinstance(t,dict) and t.get("seed"):
            import brand_palette
            self.theme=brand_palette.brand_theme(t["seed"],t.get("mode",spec.get("theme_mode","light")),
                                                 t.get("harmony",150))
        else:
            self.theme=dict(THEMES[t]) if isinstance(t,str) else {**THEMES["midnight"],**t}
        self.fonts={**FONTS,**kit_fonts,**(spec.get("fonts") or {})}
        self.type_scale=deck_type_scale(self.kit,spec)
        self.scale_sizes=sorted(set(self.type_scale.values()),reverse=True)
        self.motion={"style":"modern","counters":True,"morph":True,**(spec.get("motion") or {})}
        self.prs=Presentation()
        self.prs.slide_width=Inches(W)
        self.prs.slide_height=Inches(H)
        self.blank=self.prs.slide_layouts[6]
        self.receipts=[]  # TEXT_SHRUNK etc.
        self.generated=[]
        self.credits=[]
        self.icons=[]
        self.cache=Path(spec.get("assets_cache") or Path.home()/".cache"/"slide-forge")

    def rgb(self,key):
        return RGBColor.from_string(self.theme.get(key,key))

    def snap(self,size):
        """Nearest size on this deck's scale (ties go to the smaller size)."""
        return min(self.scale_sizes,key=lambda s:(abs(s-float(size)),s))

    def fit_level(self,paragraphs,start,box_w,box_h,floor="small",bold=False,gap=6,family=None):
        """Largest size on the deck scale <= ``start`` whose text fits the box.

        Sizes below ``floor`` are never used: the deck scale is the whole
        vocabulary, so PowerPoint receives 3-6 sizes instead of 13 (T063)."""
        start=int(start)
        floor_pt=int(self.type_scale.get(floor,floor)) if isinstance(floor,str) else int(floor)
        allowed=[s for s in self.scale_sizes if floor_pt<=s<=start] or [start]
        fam=family or self.fonts["body"]
        for size in allowed:
            lines=sum(text_lines(p,fam,size,box_w-0.2,bold) for p in paragraphs)
            height=(lines*size*1.18+gap*(len(paragraphs)-1))/72+0.15
            if height<=box_h:
                return size,True
        return allowed[-1],False

    # -- primitives ---------------------------------------------------------

    def text(self,slide,x,y,w,h,paragraphs,name,size=None,role="body",color="text",bold=False,align=None,
             anchor=MSO_ANCHOR.TOP,floor="small",idx=None,gap=6,level=None):
        if isinstance(paragraphs,str):
            paragraphs=[paragraphs]
        family=self.fonts["head" if role=="head" else "body"]
        start=int(self.type_scale[level]) if level else self.snap(size if size is not None else self.type_scale["body"])
        fitted,ok=self.fit_level(paragraphs,start,w,h,floor=floor,gap=gap,bold=bold,family=family)
        if fitted<start:
            self.receipts.append({"code":"TEXT_SHRUNK","slide":idx,"object":name,"detail":f"{start}->{fitted} pt",
                                  "fix":"shorten the text if the smaller size hurts hierarchy"})
        if not ok:
            self.receipts.append({"code":"TEXT_OVERFLOW","slide":idx,"object":name,
                                  "detail":f"does not fit at {self.type_scale.get(floor,floor)} pt",
                                  "fix":"shorten the text or split the slide","severity":"error"})
        box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
        box.name=name
        tf=box.text_frame
        tf.word_wrap=True
        tf.vertical_anchor=anchor
        for m in ("margin_left","margin_right"):
            setattr(tf,m,Inches(0.1))
        for i,t in enumerate(paragraphs):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.text=str(t)
            if align is not None:
                p.alignment=align
            if i:
                p.space_before=Pt(gap)
            for r in p.runs:
                r.font.size=Pt(fitted)
                r.font.bold=bold
                r.font.name=family
                r.font.color.rgb=self.rgb(color)
        return box

    def rect(self,slide,x,y,w,h,fill,name,shape=MSO_SHAPE.RECTANGLE,line=None):
        s=slide.shapes.add_shape(shape,Inches(x),Inches(y),Inches(w),Inches(h))
        s.name=name
        s.fill.solid()
        s.fill.fore_color.rgb=self.rgb(fill)
        if line:
            s.line.color.rgb=self.rgb(line)
            s.line.width=Pt(1)
        else:
            s.line.fill.background()
        s.shadow.inherit=False
        if shape==MSO_SHAPE.ROUNDED_RECTANGLE:
            s.adjustments[0]=0.08
        return s

    def picture(self,slide,img,x,y,w,h,name,idx):
        """Place a picture cropped to fill the box (no distortion)."""
        if isinstance(img,dict) and "search" in img:
            import forge_assets
            src,cand=forge_assets.resolve_photo(img,self.cache,w/h)
            src=str(src)
            self.credits.append({"slide":idx,"object":name,**{k:cand[k] for k in
                                 ("id","attribution","license","license_url","landing","source")}})
        elif isinstance(img,dict):
            src=generated_art(img.get("generate","")+str(idx),self.theme)
            self.generated.append({"slide":idx,"object":name,"seed":img.get("generate","")})
        else:
            src=img
        pic=slide.shapes.add_picture(src,Inches(x),Inches(y),Inches(w),Inches(h))
        pic.name=name
        iw,ih=pic.image.size
        box,ratio=w/h,iw/ih
        if ratio>box:
            c=(1-box/ratio)/2
            pic.crop_left=pic.crop_right=c
        else:
            c=(1-ratio/box)/2
            pic.crop_top=pic.crop_bottom=c
        return pic

    def icon(self,slide,ref,x,y,size,name,color="accent",shape="circle"):
        """Vector icon (Iconify, open-source sets) as an SVG picture: PowerPoint
        2016+ draws the SVG; older readers get a transparent PNG fallback.
        Applies optical balance compensation according to geometry shape."""
        import forge_assets
        import design_system as ds
        from pptx.opc.constants import RELATIONSHIP_TYPE as RT
        from pptx.opc.package import Part
        comp = ds.optical_icon_compensation(shape, size * 72)
        w_in, h_in = comp["width"] / 72, comp["height"] / 72
        dx_in, dy_in = comp["dx"] / 72, comp["dy"] / 72
        svg_path,resolved=forge_assets.fetch_icon(ref,self.theme.get(color,color),self.cache)
        buf=io.BytesIO()
        Image.new("RGBA",(256,256),(0,0,0,0)).save(buf,format="PNG")
        buf.seek(0)
        pic=slide.shapes.add_picture(buf,Inches(x+dx_in),Inches(y+dy_in),Inches(w_in),Inches(h_in))
        pic.name=name
        pkg=slide.part.package
        part=Part(pkg.next_partname("/ppt/media/image%d.svg"),"image/svg+xml",pkg,svg_path.read_bytes())
        rid=slide.part.relate_to(part,RT.IMAGE)
        blip=pic._element.find(".//"+qn("a:blip"))
        ext=E.SubElement(E.SubElement(blip,qn("a:extLst")),qn("a:ext"),uri="{96DAC541-7B7A-43D3-8B79-37D633B846F1}")
        E.SubElement(ext,"{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip",
                     {qn("r:embed"):rid},nsmap={"asvg":"http://schemas.microsoft.com/office/drawing/2016/SVG/main"})
        self.icons.append({"object":name,"icon":resolved})
        return pic

    def background(self,slide,idx,n):
        fill=slide.background.fill
        fill.solid()
        fill.fore_color.rgb=self.rgb("bg")
        if not self.motion["morph"]:
            return
        # Two soft orbs with fixed names sit on opposite corners and rotate a
        # corner per slide, so Morph glides them around the frame, never over content.
        corners=[(0,0),(W,0),(W,H),(0,H)]
        brand="seed" if "seed" in self.theme else "accent"  # decoration may wear the raw brand colour
        for k,(key,r) in enumerate(((brand,2.0),("accent2",1.4))):
            cx,cy=corners[(idx+2*k)%4]
            orb=self.rect(slide,cx-r,cy-r,2*r,2*r,key,f"!!orb-{k+1}",MSO_SHAPE.OVAL)
            _alpha(orb,12)

    def heading(self,slide,title,idx,kicker=None):
        y=0.45
        tw=W-2*MARGIN
        if getattr(self,"spec",{}).get("logo") or getattr(self,"spec",{}).get("chrome"):
            tw-=1.3
        if kicker:
            self.text(slide,MARGIN,0.18,tw,0.38,[kicker.upper()],"Kicker",level="small",color="accent",bold=True,idx=idx)
            y=0.58
        self.text(slide,MARGIN,y,tw,0.85,[title],"Title",level="subhead",role="head",bold=True,idx=idx)
        self.rect(slide,MARGIN+0.1,y+0.92,1.4,0.07,"accent","Title accent")
        return y+1.25

    # -- layouts ------------------------------------------------------------

    def l_title(self,slide,s,idx):
        img=s.get("image") or {"generate":s["title"]}
        self.picture(slide,img,W/2,0,W/2,H,"Hero picture",idx)
        if s.get("kicker"):
            self.text(slide,MARGIN,2.0,W/2-1.2,0.45,[s["kicker"].upper()],"Kicker",level="small",color="accent",bold=True,idx=idx)
        self.text(slide,MARGIN,2.45,W/2-1.2,2.2,[s["title"]],"Title",level="title",role="head",bold=True,
                  anchor=MSO_ANCHOR.BOTTOM,idx=idx)
        self.rect(slide,MARGIN+0.1,4.8,1.8,0.08,"accent","Title accent")
        if s.get("subtitle"):
            self.text(slide,MARGIN,5.05,W/2-1.2,1.2,[s["subtitle"]],"Subtitle",level="label",color="muted",idx=idx)

    def l_section(self,slide,s,idx):
        if s.get("kicker"):
            self.text(slide,MARGIN,2.5,W-2*MARGIN,0.5,[s["kicker"].upper()],"Kicker",level="small",color="accent",bold=True,idx=idx)
        self.text(slide,MARGIN,3.0,W-2*MARGIN,1.4,[s["title"]],"Title",level="title",role="head",bold=True,idx=idx)
        self.rect(slide,MARGIN+0.1,4.5,2.4,0.08,"accent","Section accent")

    def l_statement(self,slide,s,idx):
        if s.get("kicker"):
            self.text(slide,1.4,1.2,W-2.8,0.5,[s["kicker"].upper()],"Kicker",level="small",color="accent",bold=True,idx=idx)
        self.rect(slide,1.2,1.85,0.08,3.6,"accent","Statement bar")
        self.text(slide,1.5,1.7,W-3.0,3.9,[s["text"]],"Statement",level="title",role="head",bold=True,
                  anchor=MSO_ANCHOR.MIDDLE,idx=idx)

    def l_bullets(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx,s.get("kicker"))
        width=W-2*MARGIN
        if s.get("image"):
            width=W*0.52-MARGIN
            self.picture(slide,s["image"],W*0.56,top,W*0.44-MARGIN,H-top-0.7,"Supporting picture",idx)
        self.text(slide,MARGIN,top+0.1,width,H-top-0.8,["• "+b for b in s["bullets"]],"Points",level="body",
                  anchor=MSO_ANCHOR.MIDDLE,gap=18,idx=idx)

    def l_image(self,slide,s,idx):
        if s.get("title"):
            top=self.heading(slide,s["title"],idx)
        else:
            top=0.6
        cap=0.7 if s.get("caption") else 0
        self.picture(slide,s["image"],1.4,top,W-2.8,H-top-0.5-cap,"Feature picture",idx)
        if cap:
            self.text(slide,1.4,H-0.5-cap+0.1,W-2.8,cap-0.1,[s["caption"]],"Caption",level="small",color="muted",
                      align=PP_ALIGN.CENTER,idx=idx)

    def l_kpis(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx)
        items=s["items"]
        n=len(items)
        gap=0.35
        cw=(W-2*MARGIN-gap*(n-1))/n
        ch=3.0+(0.55 if any(t.get("icon") for t in items) else 0)
        y=top+(H-top-0.5-ch-(1.1 if s.get("takeaway") else 0))/2
        # One size for every value so the row reads as a set.
        vsize=min(self.fit_level([it["value"]],self.type_scale["display"],cw-0.4,1.2,floor="body",bold=True,
                                 family=self.fonts["head"])[0] for it in items)
        for i,it in enumerate(items):
            x=MARGIN+i*(cw+gap)
            self.rect(slide,x,y,cw,ch,"surface",f"KPI card {i+1}",MSO_SHAPE.ROUNDED_RECTANGLE)
            dy=0
            if any(t.get("icon") for t in items):
                dy=0.35
                if it.get("icon"):
                    self.icon(slide,it["icon"],x+cw/2-0.3,y+0.22,0.6,f"KPI icon {i+1}")
            self.text(slide,x+0.2,y+0.3+dy*1.6,cw-0.4,1.2,[it["value"]],f"KPI value {i+1}",size=vsize,role="head",color="accent",
                      bold=True,align=PP_ALIGN.CENTER,idx=idx)
            self.text(slide,x+0.2,y+1.75+dy*1.6,cw-0.4,1.0-dy*0.6,[it["label"]],f"KPI label {i+1}",level="label",color="muted",
                      align=PP_ALIGN.CENTER,idx=idx)
        if s.get("takeaway"):
            self.text(slide,MARGIN,y+ch+0.35,W-2*MARGIN,0.8,[s["takeaway"]],"Takeaway",level="subhead",bold=True,
                      align=PP_ALIGN.CENTER,idx=idx)

    def l_process(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx)
        steps=s["steps"]
        n=len(steps)
        gap=0.55
        bw=(W-2*MARGIN-gap*(n-1))/n
        bh=2.2
        y=top+(H-top-0.5-bh-(1.2 if s.get("takeaway") else 0))/2
        for i,st in enumerate(steps):
            x=MARGIN+i*(bw+gap)
            box=self.rect(slide,x,y,bw,bh,"surface" if i<n-1 else "accent",f"Step {i+1}",MSO_SHAPE.ROUNDED_RECTANGLE)
            tf=box.text_frame
            tf.word_wrap=True
            fam=self.fonts["head"]
            size,_=self.fit_level([st],self.type_scale["body"],bw-0.2,bh-0.2,bold=True,family=fam)
            tf.text=st
            for p in tf.paragraphs:
                p.alignment=PP_ALIGN.CENTER
                for r in p.runs:
                    r.font.size=Pt(size)
                    r.font.bold=True
                    r.font.name=fam
                    r.font.color.rgb=self.rgb("text" if i<n-1 else "bg")
            if i:
                c=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x-gap+0.08),Inches(y+bh/2),
                                             Inches(x-0.08),Inches(y+bh/2))
                c.name=f"Link {i}"
                c.line.color.rgb=self.rgb("accent")
                c.line.width=Pt(2.5)
                _arrow(c)
        if s.get("takeaway"):
            self.text(slide,MARGIN,y+bh+0.5,W-2*MARGIN,0.8,[s["takeaway"]],"Takeaway",level="subhead",bold=True,
                      align=PP_ALIGN.CENTER,idx=idx)

    def l_cycle(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx)
        items=s["items"]
        n=len(items)
        cx,cy=W/2,(top+H-0.3)/2
        r=min(2.3,(H-top-0.4)/2-0.85)
        d=1.65
        if s.get("center"):
            hub=self.rect(slide,cx-0.85,cy-0.85,1.7,1.7,"accent","Hub",MSO_SHAPE.OVAL)
            _shape_text(self,hub,s["center"],"bg",level="label")
        for i,it in enumerate(items):
            ang=-math.pi/2+2*math.pi*i/n
            x,y=cx+r*1.2*math.cos(ang),cy+r*math.sin(ang)  # near-circular: the Director detects cycles by radius spread
            node=self.rect(slide,x-d/2,y-d/2,d,d,"surface","Stage "+str(i+1),MSO_SHAPE.OVAL,line="accent")
            _shape_text(self,node,it,"text",level="small")

    def l_chart(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx)
        c=s["chart"]
        data=CategoryChartData(number_format=c.get("number_format","General"))
        data.categories=c["categories"]
        for ser in c["series"]:
            data.add_series(ser["name"],ser["values"])
        cw=W-2*MARGIN if not s.get("takeaway") else W*0.62-MARGIN
        gf=slide.shapes.add_chart(CHART_TYPES[c["type"]],Inches(MARGIN),Inches(top+0.1),Inches(cw),Inches(H-top-0.6),data)
        gf.name="Chart"
        ch=gf.chart
        ch.font.size=Pt(self.type_scale["label"])
        ch.font.name=self.fonts["body"]
        ch.font.color.rgb=self.rgb("muted")
        ch.has_legend=len(c["series"])>1 or c["type"] in ("pie","doughnut")
        if ch.has_legend:
            ch.legend.position=XL_LEGEND_POSITION.BOTTOM
            ch.legend.include_in_layout=False
        palette=[self.theme["accent"],self.theme["accent2"],self.theme["muted"],self.theme["text"]]
        plot=ch.plots[0]
        if c["type"] in ("pie","doughnut"):
            for j,pt in enumerate(plot.series[0].points):
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb=RGBColor.from_string(palette[j%len(palette)])
        else:
            for j,ser in enumerate(plot.series):
                col=RGBColor.from_string(palette[j%len(palette)])
                if c["type"]=="line":
                    ser.format.line.color.rgb=col
                    ser.format.line.width=Pt(3)
                else:
                    ser.format.fill.solid()
                    ser.format.fill.fore_color.rgb=col
            for ax in (ch.category_axis,ch.value_axis):
                ax.format.line.color.rgb=self.rgb("muted")
                ax.tick_labels.font.color.rgb=self.rgb("muted")
            ch.value_axis.has_major_gridlines=False
        if s.get("takeaway"):
            x=W*0.62+0.3
            self.rect(slide,x,top+0.6,0.07,2.6,"accent","Takeaway bar")
            self.text(slide,x+0.25,top+0.5,W-x-0.25-MARGIN,2.9,[s["takeaway"]],"Takeaway",level="subhead",role="head",
                      bold=True,anchor=MSO_ANCHOR.MIDDLE,idx=idx)

    def l_comparison(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx)
        gap=0.5
        cw=(W-2*MARGIN-gap)/2
        chh=H-top-0.7
        for i,side in enumerate(("left","right")):
            x=MARGIN+i*(cw+gap)
            self.rect(slide,x,top+0.1,cw,chh,"surface",f"{side.title()} card",MSO_SHAPE.ROUNDED_RECTANGLE)
            hx=0
            if s[side].get("icon"):
                self.icon(slide,s[side]["icon"],x+0.35,top+0.48,0.62,f"{side.title()} icon",
                          "accent" if i==0 else "accent2")
                hx=0.8
            self.text(slide,x+0.35+hx,top+0.4,cw-0.7-hx,0.8,[s[side]["heading"]],f"{side.title()} heading",level="subhead",role="head",
                      color="accent" if i==0 else "accent2",bold=True,idx=idx)
            self.text(slide,x+0.35,top+1.35,cw-0.7,chh-1.5,["• "+p for p in s[side].get("points",[])], f"{side.title()} points",level="body",gap=14,idx=idx)

    def l_quote(self,slide,s,idx):
        self.text(slide,1.3,0.4,1.8,2.1,["\u201c"],"Quote mark",level="display",role="head",color="accent",bold=True,idx=idx)
        self.text(slide,1.6,2.25,W-3.2,2.95,[s["quote"]],"Quote",level="title",role="head",anchor=MSO_ANCHOR.MIDDLE,idx=idx)
        if s.get("author"):
            self.rect(slide,1.7,5.45,0.9,0.05,"accent","Author rule")
            self.text(slide,2.75,5.2,W-4.4,0.6,[s["author"]],"Author",level="label",color="muted",idx=idx)

    def l_closing(self,slide,s,idx):
        self.text(slide,MARGIN,2.4,W-2*MARGIN,1.6,[s["title"]],"Title",level="title",role="head",bold=True,
                  align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.BOTTOM,idx=idx)
        self.rect(slide,W/2-1.0,4.15,2.0,0.08,"accent","Closing accent")
        if s.get("subtitle"):
            self.text(slide,MARGIN+1,4.45,W-2*MARGIN-2,1.2,[s["subtitle"]],"Subtitle",level="subhead",color="muted",
                      align=PP_ALIGN.CENTER,idx=idx)

    def l_asymmetric(self,slide,s,idx):
        import design_system as ds
        top=self.heading(slide,s["title"],idx,s.get("kicker"))
        rev=bool(s.get("reverse",False))
        lay=ds.asymmetric_golden_layout(reverse=rev)
        maj,minor=lay["major"],lay["minor"]
        card_h=H-top-0.65
        mx,my,mw=maj["x"]/72,top+0.05,maj["w"]/72
        c1=self.rect(slide,mx,my,mw,card_h,"surface","Major Card",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c1,75)
        m_data=s.get("major",{})
        if isinstance(m_data,dict):
            if m_data.get("heading"):
                self.text(slide,mx+0.35,my+0.3,mw-0.7,0.45,[m_data["heading"]],"Major Heading",level="subhead",role="head",bold=True,idx=idx)
            if m_data.get("text"):
                self.text(slide,mx+0.35,my+0.85,mw-0.7,card_h-1.2,[m_data["text"]],"Major Text",level="label",idx=idx)
            elif m_data.get("points"):
                self.text(slide,mx+0.35,my+0.85,mw-0.7,card_h-1.2,["• "+p for p in m_data["points"]],"Major Points",level="label",gap=12,idx=idx)
            if m_data.get("image"):
                self.picture(slide,m_data["image"],mx+0.3,my+0.8,mw-0.6,card_h-1.1,"Major Picture",idx)
        else:
            self.text(slide,mx+0.35,my+0.4,mw-0.7,card_h-0.8,[str(m_data)],"Major Content",level="body",idx=idx)
        nx,ny,nw=minor["x"]/72,top+0.05,minor["w"]/72
        c2=self.rect(slide,nx,ny,nw,card_h,"surface","Minor Card",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c2,75)
        n_data=s.get("minor",{})
        if isinstance(n_data,dict):
            if n_data.get("heading"):
                self.text(slide,nx+0.3,ny+0.3,nw-0.6,0.45,[n_data["heading"]],"Minor Heading",level="label",role="head",bold=True,idx=idx)
            if n_data.get("kpi"):
                self.text(slide,nx+0.3,ny+0.8,nw-0.6,1.2,[n_data["kpi"]],"Minor KPI",level="display",role="head",color="accent",bold=True,idx=idx)
            if n_data.get("points"):
                self.text(slide,nx+0.3,ny+0.85,nw-0.6,card_h-1.2,["• "+p for p in n_data["points"]],"Minor Points",level="small",gap=10,idx=idx)
            elif n_data.get("text"):
                y_off=2.1 if n_data.get("kpi") else 0.85
                self.text(slide,nx+0.3,ny+y_off,nw-0.6,card_h-y_off-0.3,[n_data["text"]],"Minor Text",level="small",color="muted",idx=idx)
        else:
            self.text(slide,nx+0.3,ny+0.4,nw-0.6,card_h-0.8,[str(n_data)],"Minor Content",level="label",idx=idx)

    def l_bento(self,slide,s,idx):
        top=self.heading(slide,s["title"],idx,s.get("kicker"))
        total_h=H-top-0.65
        hero_w=496/72
        hx,hy=48/72,top+0.05
        c_hero=self.rect(slide,hx,hy,hero_w,total_h,"surface","Hero Card",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c_hero,75)
        h_data=s.get("hero",{})
        if isinstance(h_data,dict):
            if h_data.get("title"):
                self.text(slide,hx+0.35,hy+0.3,hero_w-0.7,0.45,[h_data["title"]],"Hero Title",level="subhead",role="head",bold=True,idx=idx)
            if h_data.get("text"):
                self.text(slide,hx+0.35,hy+0.85,hero_w-0.7,total_h-1.2,[h_data["text"]],"Hero Text",level="label",idx=idx)
            elif h_data.get("image"):
                self.picture(slide,h_data["image"],hx+0.25,hy+0.8,hero_w-0.5,total_h-1.05,"Hero Picture",idx)
        else:
            self.text(slide,hx+0.35,hy+0.4,hero_w-0.7,total_h-0.8,[str(h_data)],"Hero Content",level="body",idx=idx)
        rx,rw,gutter=564/72,348/72,20/72
        sub_h=(total_h-gutter)/2
        c_tr=self.rect(slide,rx,hy,rw,sub_h,"surface","Top Right Card",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c_tr,75)
        tr_data=s.get("top_right",{})
        if isinstance(tr_data,dict):
            if tr_data.get("title"):
                self.text(slide,rx+0.3,hy+0.25,rw-0.6,0.4,[tr_data["title"]],"TopRight Title",level="label",role="head",bold=True,idx=idx)
            if tr_data.get("text"):
                self.text(slide,rx+0.3,hy+0.7,rw-0.6,sub_h-0.9,[tr_data["text"]],"TopRight Text",level="small",color="muted",idx=idx)
        else:
            self.text(slide,rx+0.3,hy+0.3,rw-0.6,sub_h-0.6,[str(tr_data)],"TopRight Content",level="small",idx=idx)
        by=hy+sub_h+gutter
        mini_w=(rw-gutter)/2
        c_br1=self.rect(slide,rx,by,mini_w,sub_h,"surface","Bottom Right 1",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c_br1,75)
        b1_data=s.get("bottom_right_1",{})
        if isinstance(b1_data,dict):
            if b1_data.get("kpi"):
                self.text(slide,rx+0.15,by+0.25,mini_w-0.3,0.8,[b1_data["kpi"]],"BR1 KPI",level="subhead",role="head",color="accent",bold=True,align=PP_ALIGN.CENTER,idx=idx)
            if b1_data.get("label"):
                self.text(slide,rx+0.15,by+1.05,mini_w-0.3,0.6,[b1_data["label"]],"BR1 Label",level="small",color="muted",align=PP_ALIGN.CENTER,idx=idx)
        else:
            self.text(slide,rx+0.2,by+0.3,mini_w-0.4,sub_h-0.6,[str(b1_data)],"BR1 Content",level="small",idx=idx)
        rx2=rx+mini_w+gutter
        c_br2=self.rect(slide,rx2,by,mini_w,sub_h,"surface","Bottom Right 2",MSO_SHAPE.ROUNDED_RECTANGLE)
        _alpha(c_br2,75)
        b2_data=s.get("bottom_right_2",{})
        if isinstance(b2_data,dict):
            if b2_data.get("kpi"):
                self.text(slide,rx2+0.15,by+0.25,mini_w-0.3,0.8,[b2_data["kpi"]],"BR2 KPI",level="subhead",role="head",color="accent2",bold=True,align=PP_ALIGN.CENTER,idx=idx)
            if b2_data.get("label"):
                self.text(slide,rx2+0.15,by+1.05,mini_w-0.3,0.6,[b2_data["label"]],"BR2 Label",level="small",color="muted",align=PP_ALIGN.CENTER,idx=idx)
        else:
            self.text(slide,rx2+0.2,by+0.3,mini_w-0.4,sub_h-0.6,[str(b2_data)],"BR2 Content",level="small",idx=idx)

    def l_duarte_break(self,slide,s,idx):
        if s.get("kpi"):
            self.text(slide,1.5,1.8,W-3.0,1.8,[s["kpi"]],"Duarte KPI",level="display",role="head",color="accent",bold=True,align=PP_ALIGN.CENTER,idx=idx)
            lbl=s.get("label") or s.get("statement","")
            if lbl:
                self.text(slide,1.5,3.8,W-3.0,1.2,[lbl],"Duarte Statement",level="subhead",role="body",align=PP_ALIGN.CENTER,idx=idx)
        else:
            stmt=s.get("statement",s.get("text",""))
            self.text(slide,1.6,2.0,W-3.2,3.4,[stmt],"Duarte Statement",level="title",role="head",bold=True,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,idx=idx)

    def chrome_elements(self,slide,s,idx,n,spec):
        lay=s.get("layout")
        use_chrome=spec.get("chrome",False) or s.get("chrome",False) or spec.get("progress_bar",False) or spec.get("logo")
        if not use_chrome:
            return
        if lay not in ("title","closing","duarte_break"):
            y_in=537/72
            h_in=3/72
            track=self.rect(slide,0,y_in,W,h_in,"surface","!!track-bar")
            _alpha(track,15)
            prog_w=W*(idx/n)
            bar=self.rect(slide,0,y_in,prog_w,h_in,"accent","!!progress-bar")
            _alpha(bar,100)
        logo_val=spec.get("logo") or s.get("logo")
        if logo_val and lay not in ("title","section","closing","statement","duarte_break"):
            lw=1.3
            lh=0.42
            lx=W-0.7-lw
            ly=0.25
            box=self.rect(slide,lx,ly,lw,lh,"surface","Logo Watermark")
            _alpha(box,85)
            _shape_text(self,box,str(logo_val),"accent",level="small")

    def build(self,spec,out):
        n=len(spec["slides"])
        for idx,s in enumerate(spec["slides"],1):
            slide=self.prs.slides.add_slide(self.blank)
            self.background(slide,idx,n)
            getattr(self,"l_"+s["layout"])(slide,s,idx)
            self.chrome_elements(slide,s,idx,n,spec)
            notes=[s["notes"]] if s.get("notes") else []
            notes+=[f"Image: {c['attribution']} ({c['landing']})" for c in self.credits if c["slide"]==idx]
            if notes:
                slide.notes_slide.notes_text_frame.text="\n".join(notes)
        if self.credits and spec.get("credits_slide",True):
            # Licensed photos are attributed on a closing credits slide (TASL).
            slide=self.prs.slides.add_slide(self.blank)
            self.background(slide,n+1,n+1)
            top=self.heading(slide,"Image credits",n+1)
            lines=[f"Slide {c['slide']}: {c['attribution']}" for c in self.credits]
            self.text(slide,MARGIN,top+0.1,W-2*MARGIN,H-top-0.6,lines,"Credits",level="small",color="muted",floor=12,idx=n+1)
            slide.notes_slide.notes_text_frame.text="[static] Attribution for licensed images."
        self.prs.save(out)


def _alpha(shape,percent):
    fill=shape.fill._xPr.find(qn("a:solidFill"))
    clr=fill[0]
    E.SubElement(clr,qn("a:alpha"),val=str(percent*1000))


def _arrow(connector):
    ln=connector.line._get_or_add_ln()
    E.SubElement(ln,qn("a:tailEnd"),type="triangle",w="med",len="med")


def _shape_text(b,shape,text,color,level="small"):
    tf=shape.text_frame
    tf.word_wrap=True
    tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    fam=b.fonts["head"]
    # A centred single line sits at the shape's mid-height, where an ellipse is
    # as wide as its bounding box (PowerPoint lays text out in the box, not in
    # a 0.707 inscribed rectangle). Use the full width so short stage labels
    # do not shrink a size step for a conservative geometric fiction.
    fitted,_=b.fit_level([text],b.type_scale.get(level,b.type_scale["body"]),shape.width/914400,
                         shape.height/914400,floor="small",bold=True,family=fam)
    tf.text=text
    for p in tf.paragraphs:
        p.alignment=PP_ALIGN.CENTER
        for r in p.runs:
            r.font.size=Pt(fitted)
            r.font.bold=True
            r.font.name=fam
            r.font.color.rgb=b.rgb(color)


# ---------------------------------------------------------------------------
# Pipeline


def build(spec,out,work=None):
    """spec -> static deck -> Motion Director -> QA. Returns the verdict."""
    import forge_qa
    import motion_director as md
    errs=validate_spec(spec)
    if errs:
        return {"ok":False,"stage":"spec","errors":errs,"warnings":[]}
    out=Path(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    static=Path(work or out.parent)/(out.stem+".static.pptx")
    b=Builder(spec)
    b.build(spec,static)
    model=md.deck_model(static)
    plan=md.draft(model,goal=spec.get("title",""),style=b.motion["style"],counters=bool(b.motion["counters"]),
                  morph=bool(b.motion["morph"]))
    if not plan.get("slides"):
        import shutil
        shutil.copyfile(static,out)
        verdict=forge_qa.qa(out,b.theme)
        verdict["errors"]=[r for r in b.receipts if r.get("severity")=="error"]+verdict["errors"]
        verdict["warnings"]=[r for r in b.receipts if r.get("severity")!="error"]+verdict["warnings"]
        verdict["ok"]=not verdict["errors"]
        verdict["generated_art"]=b.generated
        verdict["image_credits"]=b.credits
        verdict["icons"]=b.icons
        return verdict
    report=md.apply(static,plan,out,force=True)  # the agent loop rebuilds the same output
    verdict=forge_qa.qa(out,b.theme)
    verdict["errors"]=[r for r in b.receipts if r.get("severity")=="error"]+verdict["errors"]
    verdict["warnings"]=[r for r in b.receipts if r.get("severity")!="error"]+verdict["warnings"]
    if not report["ok"]:
        verdict["errors"]+=[{"code":"MOTION_APPLY","slide":None,"object":None,"detail":p,"fix":"report this spec"}
                            for p in report["problems"]]
    verdict["warnings"]+=[{"code":"MOTION_WARNING","slide":None,"object":None,"detail":w,"fix":"check the preview"}
                          for w in report["warnings"]]
    verdict["ok"]=not verdict["errors"]
    verdict["generated_art"]=b.generated
    verdict["image_credits"]=b.credits
    verdict["icons"]=b.icons
    verdict["static_pptx"]=str(static)
    verdict["output"]=str(out)
    verdict["director_notes"]=plan["research_metadata"]["draft_notes"]
    # T034: the same design system the generators read, graded on the output
    # (advisory: QA errors decide ok; the critique says what to polish).
    try:
        import design_critic
        crit=design_critic.critique(out)
        verdict["critique"]={"design_system":crit["design_system"],"scores":crit["scores"],
                             "warnings":[{k:i[k] for k in ("code","slide","object","measured","expected","fix")}
                                         for i in crit["issues"] if i["severity"]=="warn"]}
    except Exception as ex:
        verdict["critique"]={"error":str(ex)}
    return verdict


def render(pptx,outdir,seconds=8):
    """Render with desktop PowerPoint (Windows): MP4 via CreateVideo, the main
    sequence as PowerPoint parsed it, and one 6-frame strip per slide for the
    agent to look at. Returns paths; raises if PowerPoint/ffmpeg is missing."""
    import shutil
    import subprocess
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    if not (shutil.which("powershell") and shutil.which("ffmpeg")):
        raise RuntimeError("render needs Windows PowerShell + desktop PowerPoint + ffmpeg")
    ps1=Path(__file__).with_name("powerpoint_render.ps1")
    subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(ps1),"-Pptx",str(pptx),
                    "-OutDir",str(outdir),"-SecondsPerSlide",str(seconds)],check=True,capture_output=True)
    video=outdir/"native_render.mp4"
    n=len(Presentation(str(pptx)).slides)
    dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(video)],
                             check=True,capture_output=True,text=True).stdout)
    per=dur/n
    sheets=[]
    for i in range(n):
        sheet=outdir/f"slide-{i+1:02d}.png"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{i*per:.3f}","-t",f"{per:.3f}","-i",str(video),
                        "-vf",f"fps={6/per:.4f},scale=480:-1,tile=6x1","-frames:v","1",str(sheet)],check=True)
        sheets.append(str(sheet))
    seq=json.loads((outdir/"native_sequence.json").read_text(encoding="utf-8-sig"))
    return {"ok":True,"stage":"render","powerpoint":f"{seq['powerpoint_version']} build {seq['build']}",
            "video":str(video),"sheets":sheets,"sequence":str(outdir/"native_sequence.json"),
            "note":"CreateVideo auto-advances clicks; it is PowerPoint's renderer, not an interactive slideshow"}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("schema")
    b=sub.add_parser("build")
    b.add_argument("spec",type=Path)
    b.add_argument("-o","--output",type=Path,required=True)
    q=sub.add_parser("qa")
    q.add_argument("pptx",type=Path)
    r=sub.add_parser("render")
    r.add_argument("pptx",type=Path)
    r.add_argument("-d","--dir",type=Path,required=True)
    r.add_argument("--seconds",type=int,default=8)
    a=ap.parse_args(argv)
    if a.cmd=="schema":
        result=schema()
    elif a.cmd=="build":
        result=build(json.loads(a.spec.read_text(encoding="utf-8")),a.output)
    elif a.cmd=="render":
        result=render(a.pptx,a.dir,a.seconds)
    else:
        import forge_qa
        result=forge_qa.qa(a.pptx)
    json.dump(result,sys.stdout,indent=1,ensure_ascii=False)
    print()
    return 0 if result.get("ok",True) else 1


if __name__=="__main__":
    sys.exit(main())
