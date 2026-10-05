#!/usr/bin/env python3
"""Generated helper components for motion layers and script gaps (T024).

Components are native, editable shapes added to a slide only when a plan names
them, each with a role: they carry secondary or ambient motion (halo that
follows the spotlight, orbit ring behind a cycle, track under a process,
progress token, soft backdrop for parallax) or fill a resource gap the script
needs (callout, badge, highlight frame, arrow).

Style comes from the deck: the most used non-neutral fill colour is the accent,
the most used font is the text font. Background components sit behind every
source object at low opacity; foreground ones sit on top. Every generated
shape is named ``__gen_<id>`` and described as generated, so it is easy to find,
edit or delete in PowerPoint.
"""
import math

from lxml import etree as E

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
NS={"p":P,"a":A}
GEN_PREFIX="__gen_"

BACKGROUND={"halo","orbit-ring","track-line","backdrop"}
FOREGROUND={"token","callout","badge","highlight-frame","arrow"}
KINDS=BACKGROUND|FOREGROUND


def _q(ns,tag):
    return E.QName(ns,tag)


def _hex(value):
    v=(value or "").lstrip("#").upper()
    return v if len(v)==6 and all(c in "0123456789ABCDEF" for c in v) else None


def _neutral(hexv):
    r,g,b=(int(hexv[i:i+2],16) for i in (0,2,4))
    return max(r,g,b)-min(r,g,b)<24


def deck_style(model):
    """Accent colour, a dark text colour and the main font from the deck."""
    prof=model["inventory"].get("design_profile",{})
    fills=[_hex(f["value"]) for f in prof.get("fill_colors",[])]
    fills=[f for f in fills if f]
    accent=next((f for f in fills if not _neutral(f)),None) or "0F9D8A"
    second=next((f for f in fills if f!=accent and not _neutral(f)),None) or accent
    texts=[_hex(t["value"]) for t in prof.get("text_colors",[])]
    dark=next((t for t in texts if t and sum(int(t[i:i+2],16) for i in (0,2,4))<300),None) or "1F2A44"
    fonts=[f["value"] for f in prof.get("font_families",[]) if f.get("value")]
    return {"accent":accent,"second":second,"text":dark,"font":fonts[0] if fonts else None}


def _center(o):
    g=o["geometry"]
    return (g["x"]+g["w"]/2,g["y"]+g["h"]/2)


def _bbox(objs):
    xs=[o["geometry"]["x"] for o in objs]
    ys=[o["geometry"]["y"] for o in objs]
    xe=[o["geometry"]["x"]+o["geometry"]["w"] for o in objs]
    ye=[o["geometry"]["y"]+o["geometry"]["h"] for o in objs]
    return min(xs),min(ys),max(xe),max(ye)


def _overlap(a,b):
    w=min(a[2],b[2])-max(a[0],b[0])
    h=min(a[3],b[3])-max(a[1],b[1])
    return max(0,w)*max(0,h)


def layout(spec,anchors,slide,aspect):
    """Normalised geometry (x,y,w,h) for a component spec."""
    kind=spec["kind"]
    if kind=="halo":
        a=anchors[0]
        g=a["geometry"]
        side=max(g["w"]*aspect,g["h"])*float(spec.get("size",1.6))
        cx,cy=_center(a)
        return (cx-side/aspect/2,cy-side/2,side/aspect,side)
    if kind=="orbit-ring":
        pts=[(_center(o)[0]*aspect,_center(o)[1]) for o in anchors]
        cx=sum(p[0] for p in pts)/len(pts)
        cy=sum(p[1] for p in pts)/len(pts)
        r=sum(math.dist(p,(cx,cy)) for p in pts)/len(pts)
        return ((cx-r)/aspect,cy-r,2*r/aspect,2*r)
    if kind=="track-line":
        first,last=_center(anchors[0]),_center(anchors[-1])
        h=float(spec.get("thickness",0.012))
        y=(first[1]+last[1])/2+float(spec.get("offset_y",0))
        return (first[0],y-h/2,max(0.01,last[0]-first[0]),h)
    if kind=="backdrop":
        i=int(spec.get("index",0))
        size=float(spec.get("size",0.55))
        spots=[(-0.12,-0.25),(0.72,0.55),(0.78,-0.3),(-0.08,0.62)]
        x,y=spots[i%len(spots)]
        return (x,y,size/aspect,size)
    if kind=="token":
        a=anchors[0]
        g=a["geometry"]
        d=float(spec.get("size",0.06))
        cx,cy=g["x"]-d/aspect*0.9,g["y"]+g["h"]/2+float(spec.get("offset_y",0))
        return (cx-d/aspect/2,cy-d/2,d/aspect,d)
    if kind=="badge":
        a=anchors[0]
        g=a["geometry"]
        d=float(spec.get("size",0.075))
        return (g["x"]+g["w"]-d/aspect*0.6,g["y"]-d*0.4,d/aspect,d)
    if kind=="highlight-frame":
        x0,y0,x1,y1=_bbox(anchors)
        pad=float(spec.get("padding",0.015))
        return (x0-pad/aspect*1.0,y0-pad,x1-x0+2*pad/aspect,y1-y0+2*pad)
    if kind=="arrow":
        return None  # computed from endpoints in insert()
    if kind=="callout":
        text=spec.get("text","")
        size=float(spec.get("font_size",16))
        char_w=size*0.55/72/13.333  # rough average glyph width as a slide fraction (16:9 baseline)
        w=float(spec.get("width",min(0.46,max(0.2,char_w*len(text)*0.62+0.03))))
        lines=max(1,math.ceil(char_w*len(text)/max(0.05,w-0.03)))
        h=float(spec.get("height",min(0.3,0.035+lines*size*1.25/72/7.5)))
        others=[o for o in slide["objects"] if o.get("geometry")]
        if anchors:
            x0,y0,x1,y1=_bbox(anchors)
            cands=[(x1+0.015,(y0+y1)/2-h/2),((x0+x1)/2-w/2,y1+0.015),((x0+x1)/2-w/2,y0-h-0.015),(x0-w-0.015,(y0+y1)/2-h/2)]
        else:
            cands=[(0.5-w/2,0.86-h/2),(0.06,0.86-h/2),(0.94-w,0.86-h/2)]
        def cost(c):
            box=(c[0],c[1],c[0]+w,c[1]+h)
            outside=max(0,-box[0])+max(0,-box[1])+max(0,box[2]-1)+max(0,box[3]-1)
            covered=sum(_overlap(box,(o["geometry"]["x"],o["geometry"]["y"],o["geometry"]["x"]+o["geometry"]["w"],
                                         o["geometry"]["y"]+o["geometry"]["h"])) for o in others if o not in anchors)
            return outside*10+covered
        best=min(cands,key=cost)
        return (best[0],best[1],w,h)
    raise ValueError(f"unknown component kind {kind!r}")


def _solid(parent,hexv,alpha=None):
    fill=E.SubElement(parent,_q(A,"solidFill"))
    clr=E.SubElement(fill,_q(A,"srgbClr"),val=hexv)
    if alpha is not None:
        E.SubElement(clr,_q(A,"alpha"),val=str(int(alpha*100000)))
    return fill


def _txbody(sp,text,style,size,color,bold=True,center=True):
    body=E.SubElement(sp,_q(P,"txBody"))
    E.SubElement(body,_q(A,"bodyPr"),wrap="square",lIns="45720",rIns="45720",tIns="22860",bIns="22860",anchor="ctr")
    E.SubElement(body,_q(A,"lstStyle"))
    p=E.SubElement(body,_q(A,"p"))
    if center:
        E.SubElement(p,_q(A,"pPr"),algn="ctr")
    r=E.SubElement(p,_q(A,"r"))
    rpr=E.SubElement(r,_q(A,"rPr"),lang="vi-VN",sz=str(int(size*100)),b="1" if bold else "0",dirty="0")
    _solid(rpr,color)
    if style.get("font"):
        E.SubElement(rpr,_q(A,"latin"),typeface=style["font"])
        E.SubElement(rpr,_q(A,"cs"),typeface=style["font"])
    E.SubElement(r,_q(A,"t")).text=text


def _shape(spid,name,descr,geom,W,H,prst,flip=None):
    sp=E.Element(_q(P,"sp"))
    nv=E.SubElement(sp,_q(P,"nvSpPr"))
    E.SubElement(nv,_q(P,"cNvPr"),id=str(spid),name=name,descr=descr)
    E.SubElement(nv,_q(P,"cNvSpPr"))
    E.SubElement(nv,_q(P,"nvPr"))
    sppr=E.SubElement(sp,_q(P,"spPr"))
    x=E.SubElement(sppr,_q(A,"xfrm"),**(flip or {}))
    E.SubElement(x,_q(A,"off"),x=str(int(geom[0]*W)),y=str(int(geom[1]*H)))
    E.SubElement(x,_q(A,"ext"),cx=str(max(1,int(geom[2]*W))),cy=str(max(1,int(geom[3]*H))))
    pg=E.SubElement(sppr,_q(A,"prstGeom"),prst=prst)
    E.SubElement(pg,_q(A,"avLst"))
    return sp,sppr


def _next_id(root):
    ids=[int(c.get("id")) for c in root.iter(_q(P,"cNvPr")) if (c.get("id") or "").isdigit()]
    return max(ids,default=1)+1


def insert(root,slide,specs,style,W,H):
    """Insert components into a slide root. Returns object dicts shaped like
    motion_director.deck_model objects so plans can target them by id."""
    tree=root.find("p:cSld/p:spTree",NS)
    by_token={}
    for o in slide["objects"]:
        for key in (o["name"],o["id"],o.get("token")):
            if key:
                by_token.setdefault(key,o)
    aspect=W/H
    first_shape=next((i for i,c in enumerate(tree) if E.QName(c).localname not in ("nvGrpSpPr","grpSpPr")),len(tree))
    back_index=first_shape
    created=[]
    nid=_next_id(root)
    for spec in specs:
        kind=spec["kind"]
        if kind not in KINDS:
            raise ValueError(f"unknown component kind {kind!r}")
        anchors=[]
        for t in spec.get("anchors",[]):
            if t not in by_token:
                raise ValueError(f"component {spec['id']}: anchor {t!r} not found")
            anchors.append(by_token[t])
        if any(not a.get("geometry") for a in anchors):
            raise ValueError(f"component {spec['id']}: anchor has no geometry")
        need={"halo":1,"orbit-ring":3,"track-line":2,"token":1,"badge":1,"highlight-frame":1,"arrow":2}.get(kind,0)
        if len(anchors)<need:
            raise ValueError(f"component {spec['id']}: {kind} needs {need} anchor(s)")
        name=f"{GEN_PREFIX}{kind}_{spec['id']}"
        descr=f"Generated by motion director ({kind}): {spec.get('role','')}"[:250]
        accent=_hex(spec.get("color")) or style["accent"]
        if kind=="arrow":
            (ax,ay),(bx,by)=_center(anchors[0]),_center(anchors[1])
            ga,gb=anchors[0]["geometry"],anchors[1]["geometry"]
            def shrink(px,py,qx,qy,g):
                dx,dy=qx-px,qy-py
                tx=(g["w"]/2)/abs(dx) if dx else float("inf")
                ty=(g["h"]/2)/abs(dy) if dy else float("inf")
                t=min(tx,ty,0.45)
                return px+dx*t,py+dy*t
            sx,sy=shrink(ax,ay,bx,by,ga)
            ex,ey=shrink(bx,by,ax,ay,gb)
            geom=(min(sx,ex),min(sy,ey),max(abs(ex-sx),0.001),max(abs(ey-sy),0.001))
            flip={}
            if ex<sx:
                flip["flipH"]="1"
            if ey<sy:
                flip["flipV"]="1"
            sp=E.Element(_q(P,"cxnSp"))
            nv=E.SubElement(sp,_q(P,"nvCxnSpPr"))
            E.SubElement(nv,_q(P,"cNvPr"),id=str(nid),name=name,descr=descr)
            E.SubElement(nv,_q(P,"cNvCxnSpPr"))
            E.SubElement(nv,_q(P,"nvPr"))
            sppr=E.SubElement(sp,_q(P,"spPr"))
            x=E.SubElement(sppr,_q(A,"xfrm"),**flip)
            E.SubElement(x,_q(A,"off"),x=str(int(geom[0]*W)),y=str(int(geom[1]*H)))
            E.SubElement(x,_q(A,"ext"),cx=str(int(geom[2]*W)),cy=str(int(geom[3]*H)))
            pg=E.SubElement(sppr,_q(A,"prstGeom"),prst="straightConnector1")
            E.SubElement(pg,_q(A,"avLst"))
            ln=E.SubElement(sppr,_q(A,"ln"),w="28575")
            _solid(ln,accent)
            E.SubElement(ln,_q(A,"tailEnd"),type="triangle")
            obj_kind="connector"
        else:
            geom=layout(spec,anchors,slide,aspect)
            prst={"halo":"ellipse","orbit-ring":"ellipse","track-line":"roundRect","backdrop":"ellipse",
                  "token":"ellipse","badge":"ellipse","highlight-frame":"roundRect","callout":"roundRect"}[kind]
            sp,sppr=_shape(nid,name,descr,geom,W,H,prst)
            if kind=="halo":
                grad=E.SubElement(sppr,_q(A,"gradFill"),rotWithShape="1")
                gl=E.SubElement(grad,_q(A,"gsLst"))
                for pos,alpha in ((0,float(spec.get("opacity",0.45))),(100000,0.0)):
                    gs=E.SubElement(gl,_q(A,"gs"),pos=str(pos))
                    c=E.SubElement(gs,_q(A,"srgbClr"),val=accent)
                    E.SubElement(c,_q(A,"alpha"),val=str(int(alpha*100000)))
                path=E.SubElement(grad,_q(A,"path"),path="circle")
                E.SubElement(path,_q(A,"fillToRect"),l="50000",t="50000",r="50000",b="50000")
                E.SubElement(E.SubElement(sppr,_q(A,"ln")),_q(A,"noFill"))
            elif kind in ("orbit-ring","highlight-frame"):
                E.SubElement(sppr,_q(A,"noFill"))
                ln=E.SubElement(sppr,_q(A,"ln"),w="22225" if kind=="orbit-ring" else "28575")
                _solid(ln,accent,float(spec.get("opacity",0.55 if kind=="orbit-ring" else 1.0)))
                if kind=="orbit-ring":
                    E.SubElement(ln,_q(A,"prstDash"),val="dash")
            elif kind in ("track-line","backdrop","token","badge"):
                default={"track-line":0.35,"backdrop":0.08,"token":1.0,"badge":1.0}[kind]
                color=style["second"] if kind=="backdrop" and int(spec.get("index",0))%2 else accent
                _solid(sppr,color,float(spec.get("opacity",default)) if default<1 or "opacity" in spec else None)
                E.SubElement(E.SubElement(sppr,_q(A,"ln")),_q(A,"noFill"))
                if kind=="badge":
                    _txbody(sp,str(spec.get("text","1")),style,float(spec.get("font_size",14)),"FFFFFF")
            elif kind=="callout":
                _solid(sppr,"FFFFFF",0.92)
                ln=E.SubElement(sppr,_q(A,"ln"),w="19050")
                _solid(ln,accent)
                _txbody(sp,spec["text"],style,float(spec.get("font_size",16)),style["text"],bold=True)
            obj_kind="shape"
        if kind in BACKGROUND:
            tree.insert(back_index,sp)
            back_index+=1
        else:
            tree.append(sp)
        text=spec.get("text") if kind in ("callout","badge") else None
        created.append({
            "id":str(nid),"name":name,"token":spec["id"],"kind":obj_kind,"placeholder":None,
            "geometry":{"x":geom[0],"y":geom[1],"w":geom[2],"h":geom[3]},"geometry_inherited":False,
            "text":text,"paragraphs":[{"index":0,"text":text,"level":0}] if text else [],
            "max_font_pt":None,"filled":kind not in ("orbit-ring","highlight-frame","arrow"),
            "has_text_body":bool(text),"chart_summary":None,"standalone_number":None,
            "already_animated":False,"z":0,"image":None,"preset_geometry":None,
            "generated":{"component_id":spec["id"],"kind":kind,"role":spec.get("role")},
        })
        by_token[spec["id"]]=created[-1]
        by_token[name]=created[-1]
        nid+=1
    return created
