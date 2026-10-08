#!/usr/bin/env python3
"""PowerPoint-canonical animation timing writer, reader and state simulator.

T019. This module writes the timing tree in the same shape PowerPoint itself
saves for its built-in effects:

    tmRoot > mainSeq > click group (delay=indefinite)
                     > time block (delay = end of previous block)
                     > effect par (presetClass/presetID/nodeType)
                     > behaviours (set visibility + animEffect/anim/...)

Two defects of the earlier research writers are fixed here:

* "after-previous" effects start in a *new* time block whose delay is the end
  of the previous block.  Siblings with delay=0 inside one ``p:par`` run
  concurrently, so the old structure played staged reveals all at once.
* Entrance effects start with ``p:set style.visibility=visible`` and exits end
  with ``hidden``; PowerPoint derives the initial hidden state of an entrance
  target from that behaviour.

Existing timing is extended, never replaced: new click groups are appended to
the slide's main sequence with fresh cTn ids and build-group ids.

Structural correctness is not PowerPoint playback evidence.
"""
import itertools

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
NS={"p":P,"a":A,"c":C}

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


def q(tag):
    return f"{{{P}}}{tag}"


def sub(parent,tag,**attrs):
    return E.SubElement(parent,q(tag),{k:str(v) for k,v in attrs.items() if v is not None})


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


def _anim_prop(parent,ids,eff,attr,values,dur):
    node=sub(parent,"anim",calcmode="lin",valueType="num")
    _bhvr(node,ids,eff,dur,fill="hold",attrs=(attr,))
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

    T023 hypothesis (T006 matrix "anchored-hold"): chained motion paths with
    fill=hold are written as absolute offsets from the layout position, the way
    PowerPoint's UI continues a second path from the end of the first.
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


def loop_cycle(eff):
    """Duration of one loop cycle (auto-reverse doubles it), or None."""
    loop=eff.get("loop")
    if not loop:
        return None
    return max(1,eff["duration_ms"])*(2 if loop.get("auto_reverse") else 1)


def effective_duration(eff):
    """Time the effect occupies for sequencing. A loop counts one cycle: later
    'after previous' blocks do not wait for an endless ambient loop."""
    preset=eff["preset"]
    dur=eff["duration_ms"]
    if eff.get("loop"):
        return loop_cycle(eff)
    it=eff.get("iterate")
    if it:
        # Text animated by word/letter: the last unit starts (units-1) gaps later.
        base=1 if preset in ("appear","disappear") else dur
        gap=it["gap_ms"] if "gap_ms" in it else int(dur*it.get("pct",0.1))
        return base+max(0,it.get("units",1)-1)*gap
    if preset=="pulse":
        return 2*dur
    if preset in ("appear","disappear"):
        return 1
    return dur


def _behaviours(parent,ids,eff):
    preset=eff["preset"]
    dur=max(1,eff["duration_ms"])
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
        _bhvr(node,ids,eff,dur,fill="hold")
        sub(node,"by",x=round(ratio*100000),y=round(ratio*100000))
    elif preset=="pulse":
        scale=eff.get("scale",1.08)
        node=sub(parent,"animScale")
        _bhvr(node,ids,eff,dur,fill="hold",autoRev="1")
        sub(node,"by",x=round(scale*100000),y=round(scale*100000))
    elif preset=="spin":
        node=sub(parent,"animRot",by=round(eff.get("by_deg",360)*60000))
        _bhvr(node,ids,eff,dur,fill="hold",attrs=("r",))
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
        _bhvr(node,ids,eff,dur,fill="hold",attrs=("ppt_x","ppt_y"))
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
    loop=eff.get("loop") or {}
    if loop:
        repeat=loop.get("repeat","indefinite")
        extra["repeatCount"]="indefinite" if repeat in ("indefinite","until-next-click") else str(int(repeat)*1000)
        if loop.get("auto_reverse"):
            extra["autoRev"]="1"
    ctn=sub(par,"cTn",id=next(ids),presetID=pid,presetClass=cls,presetSubtype=subtype,
            **extra,fill="hold",grpId=grp_id,nodeType=node_type)
    st=sub(ctn,"stCondLst")
    sub(st,"cond",delay=eff.get("delay_ms",0))
    if loop.get("repeat")=="until-next-click":
        # PowerPoint "Repeat: Until Next Click".
        end=sub(ctn,"endCondLst")
        cond=sub(end,"cond",evt="onNext",delay=0)
        sub(sub(cond,"tgtEl"),"sldTgt")
    it=eff.get("iterate")
    if it:
        # Animate text by word ("wd") or letter ("lt"), PowerPoint's
        # "Animate text" option; schema order puts iterate before childTnLst.
        node=sub(ctn,"iterate",type={"word":"wd","letter":"lt"}[it["by"]])
        if "gap_ms" in it:
            sub(node,"tmAbs",val=int(it["gap_ms"]))
        else:
            sub(node,"tmPct",val=int(it.get("pct",0.1)*100000))
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
    for key in ("accel","decel"):
        if key in eff and not (0<=eff[key]<=1):
            raise ValueError(f"{key} must be within 0..1")
    it=eff.get("iterate")
    if it is not None and (it.get("by") not in ("word","letter") or type(it.get("units",1)) is not int):
        raise ValueError("iterate needs by=word|letter and an integer unit count")
    loop=eff.get("loop")
    if loop is not None:
        if eff["preset"] not in ("grow","spin","path","pulse"):
            raise ValueError(f"preset {eff['preset']} cannot loop")
        repeat=loop.get("repeat","indefinite")
        if repeat not in ("indefinite","until-next-click") and not (type(repeat) is int and 1<=repeat<=100):
            raise ValueError("loop.repeat must be indefinite, until-next-click or 1..100")


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

    clicks: [{"id":..., "start":"click"|"auto", "effects":[effect, ...]}]
    effect: {"preset","spid","trigger","duration_ms","delay_ms"?, "paragraph"?,
             "chart"?, "scale"?, "by_deg"?, "points"?, "opacity"?, "beat"?}
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

    main_children,created_main=_main_sequence(timing,id_iter)
    existing_clicks=len(main_children.findall("p:par",NS))
    used_grp=_existing_grp_ids(timing)
    next_grp={}
    grp_for={}
    builds={}
    receipts=[]

    for ci,click in enumerate(clicks):
        auto=click.get("start","click")=="auto"
        outer=sub(main_children,"par")
        octn=sub(outer,"cTn",id=next(id_iter),fill="hold")
        st=sub(octn,"stCondLst")
        sub(st,"cond",delay="indefinite")
        if auto:
            if existing_clicks+ci!=0:
                raise ValueError("only the first main-sequence group can start automatically")
            cond=sub(st,"cond",evt="onBegin",delay=0)
            sub(cond,"tn",val=2)
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
                {k:v for k,v in e.items() if k in ("preset","spid","paragraph","chart","trigger","duration_ms","delay_ms")}
                for e in effs]})
        receipts.append({"id":click.get("id"),"start":"auto" if auto else "click",
                         "duration_ms":end,"blocks":block_receipts})

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
        "appended_click_groups":len(clicks),
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


def read_main_sequence(root):
    """Parse the main sequence into click groups of effect records.

    Works for PowerPoint-authored timing and for this writer's output.
    """
    main=root.find(".//p:timing//p:cTn[@nodeType='mainSeq']",NS)
    if main is None:
        return []
    groups=[]
    for gpar in main.findall("p:childTnLst/p:par",NS):
        gctn=gpar.find("p:cTn",NS)
        conds=gctn.findall("p:stCondLst/p:cond",NS)
        auto=any(c.get("evt")=="onBegin" for c in conds) or not any(c.get("delay")=="indefinite" for c in conds)
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
        groups.append({"auto":auto,"effects":effects})
    return groups


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
    # Auto groups at the start play before the first click.
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
            # noFill must precede most rPr children (ln is first).
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
# Slide transitions

MC="http://schemas.openxmlformats.org/markup-compatibility/2006"
P14="http://schemas.microsoft.com/office/powerpoint/2010/main"
P159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"


def existing_transition(root):
    return root.find(f"p:transition",NS) is not None or root.find(f"{{{MC}}}AlternateContent/{{{MC}}}Choice/p:transition",NS) is not None


def add_morph_transition(root,duration_ms=1500):
    """Insert a Morph (by object) transition with a Fade fallback, the way
    PowerPoint 2019+/365 saves it. Refuses to replace an existing transition."""
    if existing_transition(root):
        raise ValueError("slide already has a transition")
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
