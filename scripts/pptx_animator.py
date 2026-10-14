#!/usr/bin/env python3
"""PowerPoint-canonical animation timing writer, reader and state simulator.

T019 / T023 / T024. This module writes the timing tree in the same shape
PowerPoint itself saves for its built-in effects:

    tmRoot > mainSeq > click group (delay=indefinite)
                     > time block (delay = end of previous block)
                     > effect par (presetClass/presetID/nodeType)
                     > behaviours (set visibility + animEffect/anim/...)

T024 extensions:
* Multi-segment cubic Bezier / line motion paths in a single ``p:animMotion``
* Native Color emphasis (``p:animClr``) and Teeter emphasis (``p:animRot``)
* Repeat (``repeatCount``), auto-reverse (``autoRev``), and ``p14:bounceEnd``
* Interactive trigger sequences (``nodeType="interactiveSeq"`` on click of a
  specific shape ``trigger_spid``)
* Detection and optional stripping of empty layout placeholders before Morph
  (preventing the unfilled-placeholder Morph failure mode).

Structural correctness is not PowerPoint playback evidence.
"""
import itertools
import re

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
MC="http://schemas.openxmlformats.org/markup-compatibility/2006"
P14="http://schemas.microsoft.com/office/powerpoint/2010/main"
P159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"
NS={"p":P,"a":A,"c":C,"mc":MC,"p14":P14,"p159":P159}

# name -> (presetClass, presetID, presetSubtype, default duration ms)
PRESETS={
    "appear":("entr",1,0,0),
    "fade":("entr",10,0,500),
    "float-in":("entr",42,0,800),
    "zoom":("entr",53,16,500),
    "wipe-up":("entr",22,4,500),
    "wipe-down":("entr",22,1,500),
    "wipe-left":("entr",22,2,500),
    "wipe-right":("entr",22,8,500),
    "wheel":("entr",21,1,800),
    "circle":("entr",6,16,600),
    "wedge":("entr",20,0,600),
    "disappear":("exit",1,0,0),
    "fade-out":("exit",10,0,400),
    "pulse":("emph",6,0,250),
    "grow":("emph",6,0,600),
    "spin":("emph",8,0,800),
    "dim":("emph",9,0,400),
    "color":("emph",7,0,500),
    "teeter":("emph",14,0,500),
    "path":("path",0,0,800),
}
ENTRANCES={k for k,v in PRESETS.items() if v[0]=="entr"}
EXITS={k for k,v in PRESETS.items() if v[0]=="exit"}
FILTER_TO_PRESET={
    "fade":"fade",
    "wipe(up)":"wipe-up",
    "wipe(down)":"wipe-down",
    "wipe(left)":"wipe-left",
    "wipe(right)":"wipe-right",
    "wheel(1)":"wheel",
    "circle(in)":"circle",
    "wedge":"wedge",
}
PRESET_FILTER={v:k for k,v in FILTER_TO_PRESET.items()}
TRIGGERS={"click","with","after"}
HEX_COLOR_RE=re.compile(r"^#?[0-9A-Fa-f]{6}$")


def q(tag):
    return f"{{{P}}}{tag}"


def sub(parent,tag,**attrs):
    return E.SubElement(parent,q(tag),{k:str(v) for k,v in attrs.items() if v is not None})


def norm_hex(c):
    if not isinstance(c,str) or not HEX_COLOR_RE.match(c.strip()):
        raise ValueError(f"color must be a 6-digit hex RGB string, got {c!r}")
    return c.strip().lstrip("#").upper()


# ---------------------------------------------------------------------------
# Slide object helpers


def top_level_objects(root):
    """Return {spid: element} for animatable top-level spTree children."""
    tree=root.find("p:cSld/p:spTree",NS)
    result={}
    if tree is None:
        return result
    for node in tree:
        props=node.find("./*/p:cNvPr",NS)
        if props is not None and props.get("id"):
            result[props.get("id")]=node
    return result


def text_paragraphs(node):
    """Raw indices of nonempty paragraphs in a shape's text body."""
    body=node.find("p:txBody",NS)
    if body is None:
        return []
    out=[]
    for index,para in enumerate(body.findall("a:p",NS)):
        text="".join(t.text or "" for t in para.findall(".//a:t",NS)).strip()
        if text:
            ppr=para.find("a:pPr",NS)
            out.append({"index":index,"text":text,"level":int(ppr.get("lvl","0")) if ppr is not None else 0})
    return out


def is_chart_frame(node):
    data=node.find("a:graphic/a:graphicData",NS)
    return node.tag==q("graphicFrame") and data is not None and "chart" in (data.get("uri") or "")


def _max_ctn_id(timing):
    ids=[int(c.get("id")) for c in timing.iter(q("cTn")) if (c.get("id") or "").isdigit()]
    return max(ids,default=0)


# ---------------------------------------------------------------------------
# Behaviours


def _ctn(parent,ids,dur,delay=None,fill=None,**extra):
    ctn=sub(parent,"cTn",id=next(ids),dur=dur,fill=fill,**extra)
    if delay is not None:
        st=sub(ctn,"stCondLst")
        sub(st,"cond",delay=delay)
    return ctn


def _target(parent,spid,paragraph=None,chart=None):
    tgt=sub(parent,"tgtEl")
    sp=sub(tgt,"spTgt",spid=spid)
    if paragraph is not None:
        tx=sub(sp,"txEl")
        sub(tx,"pRg",st=paragraph,end=paragraph)
    elif chart is not None:
        g=sub(sp,"graphicEl")
        series,category,step=chart
        E.SubElement(g,E.QName(A,"chart"),seriesIdx=str(series),categoryIdx=str(category),bldStep=step)
    return tgt


def _repeat_attrs(eff,default_auto_rev=False):
    extra={}
    rep=eff.get("repeat")
    if rep=="indefinite":
        extra["repeatCount"]="indefinite"
    elif isinstance(rep,(int,float)) and rep>1:
        extra["repeatCount"]=str(int(round(rep*1000)))
    if eff.get("auto_reverse") or default_auto_rev:
        extra["autoRev"]="1"
    return extra


def _bhvr(parent,ids,eff,dur,delay=None,fill=None,attrs=(),**ctn_extra):
    bhvr=sub(parent,"cBhvr")
    _ctn(bhvr,ids,dur,delay=delay,fill=fill,**ctn_extra)
    _target(bhvr,eff["spid"],eff.get("paragraph"),eff.get("chart"))
    if attrs:
        lst=sub(bhvr,"attrNameLst")
        for a in attrs:
            sub(lst,"attrName").text=a
    return bhvr


def _set_visibility(parent,ids,eff,value,delay):
    node=sub(parent,"set")
    _bhvr(node,ids,eff,1,delay=delay,fill="hold",attrs=("style.visibility",))
    to=sub(node,"to")
    sub(to,"strVal",val=value)


def _anim_effect(parent,ids,eff,transition,filt,dur):
    node=sub(parent,"animEffect",transition=transition,filter=filt)
    _bhvr(node,ids,eff,dur)


def _anim_prop(parent,ids,eff,attr,values,dur,**ctn_extra):
    node=sub(parent,"anim",calcmode="lin",valueType="num")
    _bhvr(node,ids,eff,dur,fill="hold",attrs=(attr,),**ctn_extra)
    lst=sub(node,"tavLst")
    for tm,val in values:
        tav=sub(lst,"tav",tm=tm)
        v=sub(tav,"val")
        if isinstance(val,str):
            sub(v,"strVal",val=val)
        else:
            sub(v,"fltVal",val=val)


def _num(v):
    return f"{round(v,6):g}"


def _path_string(points):
    x0,y0=points[0]["x"],points[0]["y"]
    parts=["M 0 0"]
    for p in points[1:]:
        parts.append(f"L {_num(p['x']-x0)} {_num(p['y']-y0)}")
    return " ".join(parts)+" E"


def anchored_path_string(segments):
    """Path in slide fractions measured from the object's authored (layout)
    position. ``segments`` = [{"x","y"} start, then {"x","y"[,"c1","c2"]} ...];
    c1/c2 are cubic Bezier control points (also anchored offsets).

    T023/T024 hypothesis (T006 matrix "anchored-hold"): chained motion paths with
    fill=hold are written as absolute offsets from the layout position, the way
    PowerPoint's UI continues a second path from the end of the first. Supports
    multi-segment poly-Bezier paths in a single animMotion element.
    """
    first=segments[0]
    parts=[f"M {_num(first['x'])} {_num(first['y'])}"]
    for seg in segments[1:]:
        if "c1" in seg:
            c1,c2=seg["c1"],seg["c2"]
            parts.append(f"C {_num(c1['x'])} {_num(c1['y'])} {_num(c2['x'])} {_num(c2['y'])} {_num(seg['x'])} {_num(seg['y'])}")
        else:
            parts.append(f"L {_num(seg['x'])} {_num(seg['y'])}")
    return " ".join(parts)+" E"


def effective_duration(eff):
    preset=eff["preset"]
    dur=eff["duration_ms"]
    if preset in ("appear","disappear"):
        return 1
    mult=1
    if preset=="pulse" or eff.get("auto_reverse"):
        mult*=2
    rep=eff.get("repeat")
    if isinstance(rep,(int,float)) and rep>1:
        mult*=rep
    return int(round(dur*mult))


def _behaviours(parent,ids,eff):
    preset=eff["preset"]
    dur=max(1,eff["duration_ms"])
    rep_extra=_repeat_attrs(eff)
    if preset in ENTRANCES:
        _set_visibility(parent,ids,eff,"visible",0)
        if preset=="appear":
            return
        if preset=="float-in":
            _anim_effect(parent,ids,eff,"in","fade",dur)
            _anim_prop(parent,ids,eff,"ppt_x",[(0,"#ppt_x"),(100000,"#ppt_x")],dur)
            _anim_prop(parent,ids,eff,"ppt_y",[(0,"#ppt_y+.1"),(100000,"#ppt_y")],dur)
        elif preset=="zoom":
            _anim_prop(parent,ids,eff,"ppt_w",[(0,0),(100000,"#ppt_w")],dur)
            _anim_prop(parent,ids,eff,"ppt_h",[(0,0),(100000,"#ppt_h")],dur)
            _anim_effect(parent,ids,eff,"in","fade",dur)
        else:
            _anim_effect(parent,ids,eff,"in",PRESET_FILTER[preset],dur)
    elif preset in EXITS:
        if preset=="fade-out":
            _anim_effect(parent,ids,eff,"out","fade",dur)
        _set_visibility(parent,ids,eff,"hidden",max(0,dur-1) if preset!="disappear" else 0)
    elif preset=="grow":
        ratio=eff["ratio"]
        node=sub(parent,"animScale")
        _bhvr(node,ids,eff,dur,fill="hold",**rep_extra)
        sub(node,"by",x=round(ratio*100000),y=round(ratio*100000))
    elif preset=="pulse":
        scale=eff.get("scale",1.08)
        node=sub(parent,"animScale")
        _bhvr(node,ids,eff,dur,fill="hold",**_repeat_attrs(eff,default_auto_rev=True))
        sub(node,"by",x=round(scale*100000),y=round(scale*100000))
    elif preset=="spin":
        node=sub(parent,"animRot",by=round(eff.get("by_deg",360)*60000))
        _bhvr(node,ids,eff,dur,fill="hold",attrs=("r",),**rep_extra)
    elif preset=="teeter":
        deg=eff.get("by_deg",2.0)
        node=sub(parent,"animRot",by=round(deg*60000))
        teeter_extra={"autoRev":"1","repeatCount":str(int(round(eff.get("repeat",2)*1000)))}
        _bhvr(node,ids,eff,max(1,dur//2),fill="hold",attrs=("r",),**teeter_extra)
    elif preset=="color":
        hx=norm_hex(eff.get("color","#E06C4F"))
        node=sub(parent,"animClr",clrSpc="rgb")
        _bhvr(node,ids,eff,dur,fill="hold",attrs=("fillcolor",),**rep_extra)
        to=sub(node,"to")
        E.SubElement(to,E.QName(A,"srgbClr"),val=hx)
    elif preset=="dim":
        # PowerPoint "Transparency" emphasis, held until the slide ends or a
        # later dim on the same object sets another opacity (1 restores).
        opacity=eff.get("opacity",0.35)
        s=sub(parent,"set")
        _bhvr(s,ids,eff,"indefinite",fill="hold",attrs=("style.opacity",))
        sub(sub(s,"to"),"strVal",val=f"{opacity:g}")
        node=sub(parent,"animEffect",filter="image",prLst=f"opacity: {opacity:g}")
        bhvr=sub(node,"cBhvr",rctx="IE")
        _ctn(bhvr,ids,"indefinite",fill="hold")
        _target(bhvr,eff["spid"],eff.get("paragraph"))
    elif preset=="path":
        if eff.get("anchored"):
            path=anchored_path_string(eff["anchored"])
            curved=any("c1" in seg for seg in eff["anchored"])
            pts=None if curved else "A"*len(eff["anchored"])
        else:
            path=_path_string(eff["points"])
            pts="A"*len(eff["points"])
        node=sub(parent,"animMotion",origin="layout",path=path,
                 pathEditMode="relative",rAng="0",ptsTypes=pts)
        _bhvr(node,ids,eff,dur,fill="hold",attrs=("ppt_x","ppt_y"),**rep_extra)
        sub(node,"rCtr",x=0,y=0)
    else:
        raise ValueError(f"unsupported preset {preset}")


def _effect_par(parent,ids,eff,node_type,grp_id):
    cls,pid,subtype,_=PRESETS[eff["preset"]]
    par=sub(parent,"par")
    extra={}
    if cls=="path":
        extra={"accel":"50000","decel":"50000"}
    if "accel" in eff or "decel" in eff:
        extra={"accel":str(round(eff.get("accel",0)*100000)),"decel":str(round(eff.get("decel",0)*100000))}
        extra={k:v for k,v in extra.items() if v!="0"}
    ctn=sub(par,"cTn",id=next(ids),presetID=pid,presetClass=cls,presetSubtype=subtype,
            **extra,fill="hold",grpId=grp_id,nodeType=node_type)
    if eff.get("bounce_end"):
        ctn.set(E.QName(P14,"bounceEnd"),str(round(float(eff["bounce_end"])*100000)))
    st=sub(ctn,"stCondLst")
    sub(st,"cond",delay=eff.get("delay_ms",0))
    children=sub(ctn,"childTnLst")
    _behaviours(children,ids,eff)
    return ctn


# ---------------------------------------------------------------------------
# Timeline assembly


def validate_effect(eff):
    if eff.get("preset") not in PRESETS:
        raise ValueError(f"unknown preset {eff.get('preset')!r}")
    if eff.get("trigger") not in TRIGGERS:
        raise ValueError(f"unknown trigger {eff.get('trigger')!r}")
    if not isinstance(eff.get("spid"),str):
        raise ValueError("effect spid must be text")
    if type(eff.get("duration_ms")) is not int or eff["duration_ms"]<0:
        raise ValueError("duration_ms must be a nonnegative integer")
    if type(eff.get("delay_ms",0)) is not int or eff.get("delay_ms",0)<0:
        raise ValueError("delay_ms must be a nonnegative integer")
    if eff["preset"]=="path":
        pts=eff.get("anchored") or eff.get("points")
        if not isinstance(pts,list) or len(pts)<2:
            raise ValueError("path effect requires >=2 points")
    if eff["preset"]=="grow" and not (isinstance(eff.get("ratio"),(int,float)) and eff["ratio"]>0):
        raise ValueError("grow effect requires a positive ratio")
    if eff["preset"]=="color":
        norm_hex(eff.get("color",""))
    for key in ("accel","decel","bounce_end"):
        if key in eff and not (0<=eff[key]<=1):
            raise ValueError(f"{key} must be within 0..1")
    rep=eff.get("repeat")
    if rep is not None and rep!="indefinite" and (type(rep) not in (int,float) or rep<=0):
        raise ValueError("repeat must be a positive number or 'indefinite'")


def plan_blocks(effects):
    """Group a click group's effects into sequential time blocks.

    Returns [(begin_ms, [(effect,node_type), ...]), ...]. The first effect opens
    block 0; "after" opens a new block that begins when the previous block ends.
    """
    blocks=[]
    begin=0
    end=0
    for i,eff in enumerate(effects):
        if i==0 or eff["trigger"]=="after":
            begin=end if i else 0
            blocks.append((begin,[]))
        blocks[-1][1].append(eff)
        end=max(end,begin+eff.get("delay_ms",0)+effective_duration(eff))
    return blocks,end


def _new_timing():
    timing=E.Element(q("timing"))
    tn=sub(timing,"tnLst")
    par=sub(tn,"par")
    sub(par,"cTn",id=1,dur="indefinite",restart="never",nodeType="tmRoot")
    return timing


def _main_sequence(timing,ids):
    main=timing.find(".//p:cTn[@nodeType='mainSeq']",NS)
    if main is not None:
        children=main.find("p:childTnLst",NS)
        if children is None:
            children=sub(main,"childTnLst")
        return children,False
    root_ctn=timing.find("p:tnLst/p:par/p:cTn",NS)
    root_children=root_ctn.find("p:childTnLst",NS)
    if root_children is None:
        root_children=sub(root_ctn,"childTnLst")
    seq=E.Element(q("seq"),concurrent="1",nextAc="seek")
    root_children.insert(0,seq)
    ctn=sub(seq,"cTn",id=next(ids),dur="indefinite",nodeType="mainSeq")
    children=sub(ctn,"childTnLst")
    prev=sub(seq,"prevCondLst")
    cond=sub(prev,"cond",evt="onPrev",delay=0)
    sub(sub(cond,"tgtEl"),"sldTgt")
    nxt=sub(seq,"nextCondLst")
    cond=sub(nxt,"cond",evt="onNext",delay=0)
    sub(sub(cond,"tgtEl"),"sldTgt")
    return children,True


def _interactive_sequence(timing,ids,trigger_spid):
    """Find or create a shape-triggered interactiveSeq for ``trigger_spid``."""
    root_ctn=timing.find("p:tnLst/p:par/p:cTn",NS)
    root_children=root_ctn.find("p:childTnLst",NS)
    if root_children is None:
        root_children=sub(root_ctn,"childTnLst")
    for seq in root_children.findall("p:seq",NS):
        ctn=seq.find("p:cTn[@nodeType='interactiveSeq']",NS)
        if ctn is None:
            continue
        tgt=seq.find("p:nextCondLst/p:cond/p:tgtEl/p:spTgt",NS)
        if tgt is not None and tgt.get("spid")==str(trigger_spid):
            children=ctn.find("p:childTnLst",NS)
            if children is None:
                children=sub(ctn,"childTnLst")
            return children
    seq=sub(root_children,"seq",concurrent="1",nextAc="seek")
    ctn=sub(seq,"cTn",id=next(ids),dur="indefinite",restart="whenNotActive",
            fill="hold",evtFilter="cancelBubble",nodeType="interactiveSeq")
    children=sub(ctn,"childTnLst")
    nxt=sub(seq,"nextCondLst")
    cond=sub(nxt,"cond",evt="onClick",delay=0)
    sub(sub(cond,"tgtEl"),"spTgt",spid=trigger_spid)
    return children


def _existing_grp_ids(timing):
    result={}
    for ctn in timing.iter(q("cTn")):
        grp=ctn.get("grpId")
        if grp is None or not grp.isdigit():
            continue
        tgt=ctn.find(".//p:spTgt",NS)
        if tgt is not None:
            result.setdefault(tgt.get("spid"),set()).add(int(grp))
    for bld in timing.iter(q("bldP"),q("bldGraphic"),q("bldDgm"),q("bldOleChart")):
        if (bld.get("grpId") or "").isdigit():
            result.setdefault(bld.get("spid"),set()).add(int(bld.get("grpId")))
    return result


def apply_timeline(root,clicks,mode="extend"):
    """Write click groups onto a slide root (lxml element) in canonical form.

    clicks: [{"id":..., "start":"click"|"auto", "trigger_spid"?:spid, "effects":[effect, ...]}]
    effect: {"preset","spid","trigger","duration_ms","delay_ms"?, "paragraph"?,
             "chart"?, "scale"?, "by_deg"?, "points"?, "opacity"?, "color"?,
             "repeat"?, "auto_reverse"?, "bounce_end"?, "beat"?}
    mode: "extend" appends after existing main-sequence clicks; "replace"
          discards existing timing (caller must have an explicit reason).
    Returns a receipt.
    """
    if mode not in ("extend","replace"):
        raise ValueError("mode must be extend or replace")
    objects=top_level_objects(root)
    for click in clicks:
        if not click.get("effects"):
            raise ValueError(f"click {click.get('id')} has no effects")
        if click.get("start","click") not in ("click","auto"):
            raise ValueError("click start must be click or auto")
        trig_spid=click.get("trigger_spid")
        if trig_spid is not None:
            if click.get("start","click")=="auto":
                raise ValueError("interactive trigger_spid click cannot start automatically")
            if str(trig_spid) not in objects:
                raise ValueError(f"trigger_spid {trig_spid} is not a top-level object on this slide")
        for eff in click["effects"]:
            validate_effect(eff)
            node=objects.get(eff["spid"])
            if node is None:
                raise ValueError(f"spid {eff['spid']} is not a top-level object on this slide")
            if eff.get("paragraph") is not None:
                indices={p["index"] for p in text_paragraphs(node)}
                if eff["paragraph"] not in indices:
                    raise ValueError(f"spid {eff['spid']} has no nonempty paragraph {eff['paragraph']}")
            if eff.get("chart") is not None and not is_chart_frame(node):
                raise ValueError(f"spid {eff['spid']} is not a chart")

    timing=root.find("p:timing",NS)
    existing=timing is not None
    replaced=False
    if existing and mode=="replace":
        root.remove(timing)
        timing=None
        replaced=True
    if timing is None:
        timing=_new_timing()
        ext=root.find("p:extLst",NS)
        if ext is not None:
            ext.addprevious(timing)
        else:
            root.append(timing)
    id_iter=itertools.count(_max_ctn_id(timing)+1)

    has_ordinary=any(c.get("trigger_spid") is None for c in clicks)
    main_children,created_main=_main_sequence(timing,id_iter) if has_ordinary else (None,False)
    existing_clicks=len(main_children.findall("p:par",NS)) if main_children is not None else 0
    used_grp=_existing_grp_ids(timing)
    next_grp={}
    grp_for={}
    builds={}
    receipts=[]
    ordinary_ci=0

    for ci,click in enumerate(clicks):
        trig_spid=click.get("trigger_spid")
        auto=click.get("start","click")=="auto"
        seq_children=_interactive_sequence(timing,id_iter,str(trig_spid)) if trig_spid is not None else main_children
        outer=sub(seq_children,"par")
        octn=sub(outer,"cTn",id=next(id_iter),fill="hold")
        st=sub(octn,"stCondLst")
        sub(st,"cond",delay="indefinite")
        if trig_spid is not None:
            cond=sub(st,"cond",evt="onBegin",delay=0)
            sub(cond,"tn",val=seq_children.getparent().get("id"))
        elif auto:
            if existing_clicks+ordinary_ci!=0:
                raise ValueError("only the first main-sequence group can start automatically")
            cond=sub(st,"cond",evt="onBegin",delay=0)
            sub(cond,"tn",val=2)
        if trig_spid is None:
            ordinary_ci+=1
        ochildren=sub(octn,"childTnLst")
        blocks,end=plan_blocks(click["effects"])
        block_receipts=[]
        for bi,(begin,effs) in enumerate(blocks):
            bpar=sub(ochildren,"par")
            bctn=sub(bpar,"cTn",id=next(id_iter),fill="hold")
            sub(sub(bctn,"stCondLst"),"cond",delay=begin)
            bchildren=sub(bctn,"childTnLst")
            for ei,eff in enumerate(effs):
                if bi==0 and ei==0:
                    node_type="afterEffect" if auto else "clickEffect"
                else:
                    node_type="withEffect" if ei>0 else "afterEffect"
                key=(eff["spid"],eff.get("beat") or f"{ci}:{bi}:{ei}")
                if key not in grp_for:
                    spid=eff["spid"]
                    if spid not in next_grp:
                        next_grp[spid]=max(used_grp.get(spid,{-1}))+1
                    grp_for[key]=next_grp[spid]
                    next_grp[spid]+=1
                grp=grp_for[key]
                _effect_par(bchildren,id_iter,eff,node_type,grp)
                build=builds.setdefault((eff["spid"],grp),{"paragraph":False,"chart":None})
                if eff.get("paragraph") is not None:
                    build["paragraph"]=True
                if eff.get("chart") is not None:
                    build["chart"]=eff.get("chart_build","series")
                    build["chart_bg"]=eff.get("chart_background",False)
            block_receipts.append({"begin_ms":begin,"effects":[
                {k:v for k,v in e.items() if k in ("preset","spid","paragraph","chart","trigger","duration_ms","delay_ms","color","repeat","auto_reverse","bounce_end")}
                for e in effs]})
        rec_item={"id":click.get("id"),"start":"auto" if auto else "click",
                  "duration_ms":end,"blocks":block_receipts}
        if trig_spid is not None:
            rec_item["trigger_spid"]=str(trig_spid)
        receipts.append(rec_item)

    bld=timing.find("p:bldLst",NS)
    if bld is None:
        bld=sub(timing,"bldLst")
    for (spid,grp),info in sorted(builds.items(),key=lambda kv:(int(kv[0][0]),kv[0][1])):
        node=objects[spid]
        if info["chart"] is not None:
            g=sub(bld,"bldGraphic",spid=spid,grpId=grp)
            if info["chart"]=="as-whole":
                sub(g,"bldAsOne")
            else:
                s=sub(g,"bldSub")
                E.SubElement(s,E.QName(A,"bldChart"),bld=info["chart"],
                             animBg="1" if info.get("chart_bg") else "0")
        elif node.tag==q("sp") and node.find("p:txBody",NS) is not None:
            if info["paragraph"]:
                sub(bld,"bldP",spid=spid,grpId=grp,build="p")
            else:
                sub(bld,"bldP",spid=spid,grpId=grp,animBg="1")
    if len(bld)==0:
        timing.remove(bld)
    return {
        "mode":mode,
        "had_existing_timing":existing,
        "replaced_existing_timing":replaced,
        "existing_click_groups":0 if replaced else existing_clicks,
        "appended_click_groups":ordinary_ci,
        "interactive_click_groups":len(clicks)-ordinary_ci,
        "created_main_sequence":created_main,
        "clicks":receipts,
    }


# ---------------------------------------------------------------------------
# Reader / simulator


def _first_target(ctn):
    tgt=ctn.find(".//p:spTgt",NS)
    if tgt is None:
        return None,None
    pr=tgt.find("p:txEl/p:pRg",NS)
    return tgt.get("spid"),(int(pr.get("st")) if pr is not None else None)


def _read_sequence_groups(seq_ctn,trigger_spid=None):
    groups=[]
    if seq_ctn is None:
        return groups
    for gpar in seq_ctn.findall("p:childTnLst/p:par",NS):
        gctn=gpar.find("p:cTn",NS)
        conds=gctn.findall("p:stCondLst/p:cond",NS)
        auto=(trigger_spid is None) and (any(c.get("evt")=="onBegin" for c in conds) or not any(c.get("delay")=="indefinite" for c in conds))
        effects=[]
        for ctn in gctn.iter(q("cTn")):
            cls=ctn.get("presetClass")
            if cls is None and ctn.get("nodeType") not in ("clickEffect","withEffect","afterEffect"):
                continue
            spid,para=_first_target(ctn)
            if spid is None:
                continue
            vis=None
            for s in ctn.findall(".//p:set",NS):
                attr=s.find("p:cBhvr/p:attrNameLst/p:attrName",NS)
                val=s.find("p:to/p:strVal",NS)
                if attr is not None and attr.text=="style.visibility" and val is not None:
                    vis=val.get("val")
            if vis is None:
                if cls=="entr":
                    vis="visible"
                elif cls=="exit":
                    vis="hidden"
                else:
                    tr=ctn.find(".//p:animEffect",NS)
                    if tr is not None and tr.get("transition") in ("in","out"):
                        vis="visible" if tr.get("transition")=="in" else "hidden"
            effects.append({"spid":spid,"paragraph":para,"class":cls,"preset_id":ctn.get("presetID"),
                            "node_type":ctn.get("nodeType"),"visibility":vis})
        item={"auto":auto,"effects":effects}
        if trigger_spid is not None:
            item["trigger_spid"]=trigger_spid
        groups.append(item)
    return groups


def read_main_sequence(root):
    """Parse the main sequence into click groups of effect records.

    Works for PowerPoint-authored timing and for this writer's output.
    """
    main=root.find(".//p:timing//p:cTn[@nodeType='mainSeq']",NS)
    return _read_sequence_groups(main)


def read_interactive_sequences(root):
    """Parse shape-triggered interactive sequences into click group records."""
    out=[]
    for seq in root.findall(".//p:timing//p:seq",NS):
        ctn=seq.find("p:cTn[@nodeType='interactiveSeq']",NS)
        if ctn is None:
            continue
        tgt=seq.find("p:nextCondLst/p:cond/p:tgtEl/p:spTgt",NS)
        spid=tgt.get("spid") if tgt is not None else None
        out.extend(_read_sequence_groups(ctn,trigger_spid=spid))
    return out


def simulate_states(root):
    """Return visibility states: [initial, after group 1, ...].

    Each state is {"hidden_objects": set(spid), "hidden_paragraphs": set((spid, idx))}.
    An object/paragraph whose first visibility change is "visible" starts hidden.
    This is a model of the authored intent, not PowerPoint playback.
    """
    groups=read_main_sequence(root)
    first={}
    for g in groups:
        for e in g["effects"]:
            if e["visibility"] is None:
                continue
            key=(e["spid"],e["paragraph"])
            first.setdefault(key,e["visibility"])
    hidden_obj={k[0] for k,v in first.items() if v=="visible" and k[1] is None}
    hidden_par={k for k,v in first.items() if v=="visible" and k[1] is not None}
    states=[]

    def snap(label):
        states.append({"label":label,"hidden_objects":set(hidden_obj),"hidden_paragraphs":set(hidden_par)})
    snap("start")
    for i,g in enumerate(groups,1):
        for e in g["effects"]:
            if e["visibility"] is None:
                continue
            if e["paragraph"] is None:
                (hidden_obj.discard if e["visibility"]=="visible" else hidden_obj.add)(e["spid"])
            else:
                key=(e["spid"],e["paragraph"])
                (hidden_par.discard if e["visibility"]=="visible" else hidden_par.add)(key)
        snap(f"after group {i}"+(" (auto)" if g["auto"] else ""))
    return states,groups


def apply_state_for_preview(root,state):
    """Mutate a slide root so a static render shows a simulated stable state."""
    objects=top_level_objects(root)
    tree=root.find("p:cSld/p:spTree",NS)
    for spid in state["hidden_objects"]:
        node=objects.get(spid)
        if node is not None and node.getparent() is tree:
            tree.remove(node)
    for spid,idx in state["hidden_paragraphs"]:
        node=objects.get(spid)
        if node is None or node.getparent() is None:
            continue
        paras=node.findall("p:txBody/a:p",NS)
        if idx>=len(paras):
            continue
        para=paras[idx]
        ppr=para.find("a:pPr",NS)
        if ppr is None:
            ppr=E.Element(E.QName(A,"pPr"))
            para.insert(0,ppr)
        for bu in list(ppr):
            if E.QName(bu).localname.startswith("bu"):
                ppr.remove(bu)
        E.SubElement(ppr,E.QName(A,"buNone"))
        for run in para.findall("a:r",NS)+para.findall("a:fld",NS):
            rpr=run.find("a:rPr",NS)
            if rpr is None:
                rpr=E.Element(E.QName(A,"rPr"))
                run.insert(0,rpr)
            for fill in list(rpr):
                if E.QName(fill).localname in ("solidFill","gradFill","noFill","pattFill"):
                    rpr.remove(fill)
            fill=E.Element(E.QName(A,"noFill"))
            ln=rpr.find("a:ln",NS)
            if ln is not None:
                ln.addnext(fill)
            else:
                rpr.insert(0,fill)
    timing=root.find("p:timing",NS)
    if timing is not None:
        root.remove(timing)
    return root


# ---------------------------------------------------------------------------
# Slide transitions & Morph placeholder sanitizer


def empty_placeholders(root):
    """Return [(spid, name, ph_type)] for unfilled placeholder shapes on a slide.

    Per python-pptx issue #942, unfilled layout placeholders left on a slide
    can prevent PowerPoint from running the Morph transition.
    """
    out=[]
    for spid,node in top_level_objects(root).items():
        if node.tag!=q("sp"):
            continue
        ph=node.find("./p:nvSpPr/p:nvPr/p:ph",NS)
        if ph is None:
            continue
        if text_paragraphs(node):
            continue
        sppr=node.find("p:spPr",NS)
        has_visual=(sppr is not None and any(sppr.find(f"a:{t}",NS) is not None
                    for t in ("solidFill","gradFill","pattFill","blipFill")))
        if has_visual:
            continue
        cNvPr=node.find("./p:nvSpPr/p:cNvPr",NS)
        name=cNvPr.get("name","") if cNvPr is not None else ""
        out.append((spid,name,ph.get("type","obj")))
    return out


def existing_transition(root):
    return root.find("p:transition",NS) is not None or root.find(f"{{{MC}}}AlternateContent/{{{MC}}}Choice/p:transition",NS) is not None


def add_morph_transition(root,duration_ms=1500,strip_empty_placeholders=False):
    """Insert a Morph (by object) transition with a Fade fallback, the way
    PowerPoint 2019+/365 saves it. Refuses to replace an existing transition.
    Optionally strips empty placeholder shapes that would block Morph."""
    if existing_transition(root):
        raise ValueError("slide already has a transition")
    if strip_empty_placeholders:
        tree=root.find("p:cSld/p:spTree",NS)
        objs=top_level_objects(root)
        for spid,_,_ in empty_placeholders(root):
            node=objs.get(spid)
            if node is not None and tree is not None and node.getparent() is tree:
                tree.remove(node)
    alt=E.Element(E.QName(MC,"AlternateContent"),nsmap={"mc":MC})
    choice=E.SubElement(alt,E.QName(MC,"Choice"),nsmap={"p159":P159},Requires="p159")
    tr=E.SubElement(choice,q("transition"),{"spd":"slow",E.QName(P14,"dur"):str(int(duration_ms))},nsmap={"p14":P14})
    E.SubElement(tr,E.QName(P159,"morph"),option="byObject")
    fallback=E.SubElement(alt,E.QName(MC,"Fallback"))
    fb=E.SubElement(fallback,q("transition"),spd="slow")
    E.SubElement(fb,q("fade"))
    # Schema order: cSld, clrMapOvr, transition, timing, extLst.
    anchor=root.find("p:timing",NS)
    if anchor is None:
        anchor=root.find("p:extLst",NS)
    if anchor is not None:
        anchor.addprevious(alt)
    else:
        root.append(alt)
    return alt
