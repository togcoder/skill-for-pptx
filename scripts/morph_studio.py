#!/usr/bin/env python3
"""Morph Studio — professional cross-slide motion with native Morph (T028).

The techniques motion designers use in PowerPoint, built from an existing deck:

* continuity  — Morph between consecutive slides; matching objects get the same
                ``!!name`` so Morph pairs them even when they are different
                shapes (title → header, card → panel, picture → thumbnail).
                Option byObject / byWord / byChar (letters fly to the new title).
* staging     — objects that appear or disappear across a Morph are staged as
                ``!!`` copies just outside the slide edge, so they fly in or out
                instead of fading. Off-slide copies are invisible in the show.
* camera-zoom — duplicate a slide and transform the whole composition (shapes,
                pictures, text sizes, lines) so a focus object fills the frame;
                Morph turns it into a camera push-in; an optional return slide
                pulls back out.
* card-expand — duplicate a slide where one card grows into a full panel (its
                text scales with it) while the rest fades: the shape-morph trick.
* pan         — duplicate a slide shifted so a row of items scrolls like a
                carousel, one item per Morph.

Added slides are marked ``<p:cSld name="__scene:...">`` and listed with a reason.
Source slides keep their content; matched objects only gain a ``!!`` name.
LibreOffice does not play Morph, so ``preview`` simulates it (paired objects
interpolate geometry and type size, the rest cross-fade). Not PowerPoint playback.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
import pptx_animator as anim  # noqa: E402
import motion_director as md  # noqa: E402

P,A,NS=anim.P,anim.A,anim.NS
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
CT="http://schemas.openxmlformats.org/package/2006/content-types"
SLIDE_T=f"{R}/slide"
SLIDE_CT="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
PARSER=E.XMLParser(resolve_entities=False,no_network=True)
SCENE_PREFIX="__scene:"


def X(data):
    return E.fromstring(data,PARSER)


def B(root):
    return E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)


# ---------------------------------------------------------------------------
# Package


class Package:
    def __init__(self,path):
        with ZipFile(path) as z:
            self.items=[i for i in z.infolist()]
            self.data={i.filename:z.read(i.filename) for i in self.items}
        self.order=[i.filename for i in self.items]

    def xml(self,part):
        return X(self.data[part])

    def put(self,part,root_or_bytes):
        data=root_or_bytes if isinstance(root_or_bytes,bytes) else B(root_or_bytes)
        if part not in self.data:
            self.order.append(part)
        self.data[part]=data

    @staticmethod
    def rels_name(part):
        base,name=part.rsplit("/",1)
        return f"{base}/_rels/{name}.rels"

    def rels(self,part):
        name=self.rels_name(part)
        return X(self.data[name]) if name in self.data else E.Element(f"{{{REL}}}Relationships")

    def resolve(self,part,target):
        # Targets are relative to the part's folder, or package-absolute
        # ("/ppt/slides/slide1.xml", written by some generators).
        base="" if target.startswith("/") else part.rsplit("/",1)[0]
        stack=[]
        for seg in (base+"/"+target).split("/"):
            if seg=="..":
                stack.pop()
            elif seg and seg!=".":
                stack.append(seg)
        return "/".join(stack)

    def slides(self):
        pres=self.xml("ppt/presentation.xml")
        rels={r.get("Id"):r.get("Target") for r in self.rels("ppt/presentation.xml")}
        return [self.resolve("ppt/presentation.xml",rels[s.get(f"{{{R}}}id")])
                for s in pres.findall("p:sldIdLst/p:sldId",NS)]

    def content_type(self,part,ctype):
        ct=self.xml("[Content_Types].xml")
        if not any(o.get("PartName")=="/"+part for o in ct.findall(f"{{{CT}}}Override")):
            E.SubElement(ct,f"{{{CT}}}Override",PartName="/"+part,ContentType=ctype)
            self.put("[Content_Types].xml",ct)

    def override_type(self,part):
        ct=self.xml("[Content_Types].xml")
        o=next((o for o in ct.findall(f"{{{CT}}}Override") if o.get("PartName")=="/"+part),None)
        return o.get("ContentType") if o is not None else None

    def free_name(self,pattern):
        n=1
        while pattern.format(n) in self.data:
            n+=1
        return pattern.format(n)

    def _copy_part_tree(self,part):
        """Deep-copy a part (e.g. a chart) and everything its rels point to."""
        ext=part.rsplit(".",1)[1]
        stem=re.sub(r"\d*\.[^.]+$","",part)
        new=self.free_name(stem+"{}."+ext)
        self.put(new,self.data[part])
        ctype=self.override_type(part)
        if ctype:
            self.content_type(new,ctype)
        rels=self.rels(part)
        if len(rels):
            for r in rels:
                if r.get("TargetMode")=="External":
                    continue
                child=self.resolve(part,r.get("Target"))
                if child in self.data:
                    copied=self._copy_part_tree(child)
                    r.set("Target",copy_rel_target(new,copied))
            self.put(self.rels_name(new),rels)
        return new

    def duplicate_slide(self,src,after,scene):
        """Insert a copy of slide ``src`` after slide ``after``. Charts are
        deep-copied, notes are not; the copy is tagged as a generated scene."""
        new=self.free_name("ppt/slides/slide{}.xml")
        root=self.xml(src)
        root.find("p:cSld",NS).set("name",SCENE_PREFIX+scene)
        timing=root.find("p:timing",NS)
        if timing is not None:
            # A scene continues from the source's end state: objects that
            # have left (or never stay, like a halo) are not copied.
            end=anim.simulate_states(root)[0][-1]
            for spid,node in shape_nodes(root).items():
                if spid in end["hidden_objects"]:
                    node.getparent().remove(node)
            root.remove(timing)
        self.put(new,root)
        rels=self.rels(src)
        for r in list(rels):
            t=r.get("Type","")
            if t.endswith("/notesSlide"):
                rels.remove(r)
            elif t.endswith("/chart") or t.endswith("/diagramData") or t.endswith("/package"):
                copied=self._copy_part_tree(self.resolve(src,r.get("Target")))
                r.set("Target",copy_rel_target(new,copied))
        self.put(self.rels_name(new),rels)
        self.content_type(new,SLIDE_CT)
        prels=self.rels("ppt/presentation.xml")
        rid=f"rIdScene{len(prels)+1}"
        while any(r.get("Id")==rid for r in prels):
            rid+="x"
        E.SubElement(prels,f"{{{REL}}}Relationship",Id=rid,Type=SLIDE_T,Target=new.split("ppt/",1)[1])
        self.put("ppt/_rels/presentation.xml.rels",prels)
        pres=self.xml("ppt/presentation.xml")
        lst=pres.find("p:sldIdLst",NS)
        prels_by={r.get("Id"):self.resolve("ppt/presentation.xml",r.get("Target")) for r in prels}
        after_node=next(s for s in lst if prels_by.get(s.get(f"{{{R}}}id"))==after)
        sid=max(int(s.get("id")) for s in lst)+1
        node=E.Element(f"{{{P}}}sldId",{"id":str(sid),f"{{{R}}}id":rid})
        after_node.addnext(node)
        self.put("ppt/presentation.xml",pres)
        return new

    def save(self,path):
        with ZipFile(path,"w",ZIP_DEFLATED) as z:
            for name in self.order:
                z.writestr(name,self.data[name])


def copy_rel_target(from_part,to_part):
    a=from_part.split("/")[:-1]
    b=to_part.split("/")
    i=0
    while i<len(a) and i<len(b)-1 and a[i]==b[i]:
        i+=1
    return "/".join([".."]*(len(a)-i)+b[i:])


# ---------------------------------------------------------------------------
# Geometry and type


def shape_nodes(root):
    return anim.top_level_objects(root)


def tree_append(tree,node):
    """Append a shape to an spTree, keeping a trailing extLst last."""
    tail=tree.find("p:extLst",NS)
    if tail is not None:
        tail.addprevious(node)
    else:
        tree.append(node)


def xfrm_of(node):
    for path in ("p:spPr/a:xfrm","p:xfrm","p:grpSpPr/a:xfrm"):
        x=node.find(path,NS)
        if x is not None:
            return x
    return None


def ensure_xfrm(node,geom,W,H):
    x=xfrm_of(node)
    if x is not None or not geom:
        return x
    sppr=node.find("p:spPr",NS)
    if sppr is None:
        return None
    x=E.Element(f"{{{A}}}xfrm")
    E.SubElement(x,f"{{{A}}}off",x=str(int(geom["x"]*W)),y=str(int(geom["y"]*H)))
    E.SubElement(x,f"{{{A}}}ext",cx=str(int(geom["w"]*W)),cy=str(int(geom["h"]*H)))
    sppr.insert(0,x)
    return x


def box(x):
    off,ext=x.find("a:off",NS),x.find("a:ext",NS)
    return [int(off.get("x")),int(off.get("y")),int(ext.get("cx")),int(ext.get("cy"))]


def set_box(x,b):
    off,ext=x.find("a:off",NS),x.find("a:ext",NS)
    off.set("x",str(int(round(b[0]))))
    off.set("y",str(int(round(b[1]))))
    ext.set("cx",str(max(1,int(round(b[2])))))
    ext.set("cy",str(max(1,int(round(b[3])))))


class TypeResolver:
    """Effective font size of text runs: run > shape list style > layout
    placeholder > master text styles > presentation default > 18 pt."""

    def __init__(self,pkg,slide_part):
        self.pkg=pkg
        rels=pkg.rels(slide_part)
        layout=next((pkg.resolve(slide_part,r.get("Target")) for r in rels if r.get("Type","").endswith("/slideLayout")),None)
        self.layout=pkg.xml(layout) if layout else None
        master=None
        if layout:
            master=next((pkg.resolve(layout,r.get("Target")) for r in pkg.rels(layout)
                         if r.get("Type","").endswith("/slideMaster")),None)
        self.master=pkg.xml(master) if master else None
        self.pres=pkg.xml("ppt/presentation.xml")

    @staticmethod
    def _lvl(lst,level):
        if lst is None:
            return None
        node=lst.find(f"a:lvl{level+1}pPr/a:defRPr",NS)
        return int(node.get("sz")) if node is not None and (node.get("sz") or "").isdigit() else None

    def _ph_node(self,root,ph):
        if root is None or ph is None:
            return None
        for sp in root.iter(f"{{{P}}}sp"):
            o=sp.find("./p:nvSpPr/p:nvPr/p:ph",NS)
            if o is None:
                continue
            if ph.get("idx") and o.get("idx")==ph.get("idx"):
                return sp
            if (o.get("type") or "obj")==(ph.get("type") or "obj"):
                return sp
        return None

    def size(self,shape,para,run):
        rpr=run.find("a:rPr",NS) if run is not None else None
        if rpr is not None and (rpr.get("sz") or "").isdigit():
            return int(rpr.get("sz"))
        ppr=para.find("a:pPr",NS)
        level=int(ppr.get("lvl","0")) if ppr is not None else 0
        own=self._lvl(shape.find("p:txBody/a:lstStyle",NS),level)
        if own:
            return own
        ph=shape.find("./p:nvSpPr/p:nvPr/p:ph",NS)
        if ph is not None:
            for root in (self.layout,self.master):
                node=self._ph_node(root,ph)
                if node is not None:
                    v=self._lvl(node.find("p:txBody/a:lstStyle",NS),level)
                    if v:
                        return v
            if self.master is not None:
                kind=ph.get("type") or "obj"
                style={"title":"titleStyle","ctrTitle":"titleStyle"}.get(kind,"bodyStyle" if kind in ("body","obj","subTitle") else "otherStyle")
                v=self._lvl(self.master.find(f"p:txStyles/p:{style}",NS),level)
                if v:
                    return v
        v=self._lvl(self.pres.find("p:defaultTextStyle",NS),level)
        return v or 1800


def scale_text(shape,factor,resolver):
    """Bake explicit, scaled font sizes into every run (Morph interpolates
    them, so text grows with its shape during a camera move)."""
    for para in shape.iter(f"{{{A}}}p"):
        runs=para.findall("a:r",NS)+para.findall("a:fld",NS)
        for run in runs:
            rpr=run.find("a:rPr",NS)
            if rpr is None:
                rpr=E.Element(f"{{{A}}}rPr")
                run.insert(0,rpr)
            rpr.set("sz",str(max(100,int(round(resolver.size(shape,para,run)*factor)))))
        end=para.find("a:endParaRPr",NS)
        if end is not None:
            end.set("sz",str(max(100,int(round(resolver.size(shape,para,None)*factor)))))
    body=shape.find(".//a:bodyPr",NS)
    if body is not None:
        for key,default in (("lIns",91440),("rIns",91440),("tIns",45720),("bIns",45720)):
            body.set(key,str(int(int(body.get(key,default))*factor)))
        for fit in body.findall("a:normAutofit",NS):
            body.remove(fit)
    for ln in shape.iter(f"{{{A}}}ln"):
        if (ln.get("w") or "").isdigit():
            ln.set("w",str(int(int(ln.get("w"))*factor)))


# ---------------------------------------------------------------------------
# Matching and naming


def _norm(t):
    return re.sub(r"\s+"," ",(t or "")).strip().lower()


def _is_title(o):
    return bool(o["placeholder"] and o["placeholder"]["type"] in ("title","ctrTitle"))


def match_objects(prev,cur):
    """Pairs (prev_obj, cur_obj, reason) that Morph should treat as one object."""
    pairs=[]
    used=set()
    for o in cur["objects"]:
        best=None
        for p in prev["objects"]:
            if p["id"] in used:
                continue
            if o["image"] and o["image"]==p["image"]:
                best=(p,"same picture")
            elif o["text"] and _norm(o["text"])==_norm(p["text"]) and p["kind"]==o["kind"]:
                best=(p,"same text")
            elif _is_title(o) and _is_title(p):
                best=(p,"title to title")
            elif (o["name"] or "").startswith("!!") and o["name"]==p["name"]:
                best=(p,"existing !! name")
            if best:
                break
        if best:
            used.add(best[0]["id"])
            pairs.append((best[0],o,best[1]))
    return pairs


def _slug(text):
    import unicodedata
    t=unicodedata.normalize("NFD",(text or "").lower()).replace("đ","d")
    t="".join(c for c in t if unicodedata.category(c)!="Mn")
    return re.sub(r"[^a-z0-9]+","-",t).strip("-")[:24] or "obj"


def rename_chain(pkg,old,new):
    """A !! name is an identity shared by every slide in a Morph chain:
    renaming it renames every occurrence so no pairing breaks."""
    for part in pkg.slides():
        root=pkg.xml(part)
        hit=False
        for props in root.iter(f"{{{P}}}cNvPr"):
            if props.get("name")==old:
                props.set("name",new)
                hit=True
        if hit:
            pkg.put(part,root)


def set_name(node,name):
    props=node.find("./*/p:cNvPr",NS)
    old=props.get("name")
    props.set("name",name)
    return old


# ---------------------------------------------------------------------------
# Techniques


def _deck(pkg):
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"d.pptx"
        pkg.save(path)
        return md.deck_model(path)


def _slide_models(pkg):
    model=_deck(pkg)
    by_part={s["part"]:s for s in model["slides"]}
    return model,by_part


def continuity(pkg,prev_part,cur_part,option="byObject",duration_ms=1500,stage=True,extra_pairs=(),receipt=None):
    """Morph from prev to cur with forced !! pairs and off-slide staging."""
    model,by=_slide_models(pkg)
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    prev,cur=by[prev_part],by[cur_part]
    pairs=match_objects(prev,cur)
    for a,b in extra_pairs:
        pa=next(o for o in prev["objects"] if a in (o["name"],o["id"]))
        cb=next(o for o in cur["objects"] if b in (o["name"],o["id"]))
        pairs=[x for x in pairs if x[0] is not pa and x[1] is not cb]+[(pa,cb,"requested")]
    renamed=[]
    for i,(a,b,why) in enumerate(pairs,1):
        names=[n for n in (b["name"],a["name"]) if (n or "").startswith("!!")]
        base=names[0] if names else f"!!m{cur['index']}-{i}-{_slug(a['text'] or a['name'])}"
        for part,obj in ((prev_part,a),(cur_part,b)):
            if obj["name"]==base:
                continue
            if (obj["name"] or "").startswith("!!"):
                rename_chain(pkg,obj["name"],base)
            else:
                root=pkg.xml(part)
                set_name(shape_nodes(root)[obj["id"]],base)
                pkg.put(part,root)
            renamed.append({"slide_part":part,"id":obj["id"],"from":obj["name"],"to":base})
    pr,cr=pkg.xml(prev_part),pkg.xml(cur_part)
    pn,cn=shape_nodes(pr),shape_nodes(cr)
    names_now=lambda root,spid: shape_nodes(root)[spid].find("./*/p:cNvPr",NS).get("name")
    staged=[]
    if stage:
        animated_cur={e["spid"] for g in anim.read_main_sequence(cr) for e in g["effects"]}
        animated_prev={e["spid"] for g in anim.read_main_sequence(pr) for e in g["effects"]}
        paired_prev={a["id"] for a,_,_ in pairs}
        paired_cur={b["id"] for _,b,_ in pairs}
        def visible(o):
            g=o["geometry"]
            return bool(g) and g["x"]+g["w"]>0.001 and g["x"]<0.999 and g["y"]+g["h"]>0.001 and g["y"]<0.999
        enter=[o for o in cur["objects"] if o["id"] not in paired_cur and o["id"] not in animated_cur
               and not o["placeholder"] and visible(o) and o["kind"]!="chart"]
        leave=[o for o in prev["objects"] if o["id"] not in paired_prev and o["id"] not in animated_prev
               and not o["placeholder"] and visible(o) and o["kind"]!="chart"]
        def rigid(objs):
            # Largest first; an object inside a staged container travels with
            # it (same offset), so a card leaves or arrives as one piece.
            objs=sorted(objs,key=md._area,reverse=True)
            host={}
            for i,o in enumerate(objs):
                for c in objs[:i]:
                    if md._contains(c,o):
                        host[o["id"]]=host.get(c["id"],c["id"])
                        break
            return objs,host
        moved={}
        objs,host=rigid(enter)
        for o in objs:
            name=names_now(cr,o["id"])
            if not name.startswith("!!"):
                name=f"!!in{cur['index']}-{o['id']}"
                set_name(cn[o["id"]],name)
            if name in {n.get("name") for n in pr.iter(f"{{{P}}}cNvPr")}:
                continue  # already present on the previous slide
            st=_stage_copy(pkg,cur_part,cn[o["id"]],o,prev_part,pr,name,W,H,moved.get(host.get(o["id"])))
            moved[o["id"]]=st.pop("delta")
            staged.append(st)
        moved={}
        objs,host=rigid(leave)
        for o in objs:
            name=names_now(pr,o["id"])
            if not name.startswith("!!"):
                name=f"!!out{cur['index']}-{o['id']}"
                set_name(pn[o["id"]],name)
            if name in {n.get("name") for n in cr.iter(f"{{{P}}}cNvPr")}:
                continue
            st=_stage_copy(pkg,prev_part,pn[o["id"]],o,cur_part,cr,name,W,H,moved.get(host.get(o["id"])))
            moved[o["id"]]=st.pop("delta")
            staged.append(st)
    _set_transition(cr,option,duration_ms)
    pkg.put(prev_part,pr)
    pkg.put(cur_part,cr)
    if receipt is not None:
        receipt.append({"technique":"continuity","to":cur_part,"option":option,
                        "pairs":[{"from":a["name"],"to":b["name"],"why":why} for a,b,why in pairs],
                        "renamed":renamed,"staged":staged})
    return pairs


def _set_transition(root,option,duration_ms):
    for alt in root.findall(f"{{{anim.MC}}}AlternateContent"):
        if alt.find(f".//{{{anim.P159}}}morph") is not None:
            root.remove(alt)
    if anim.existing_transition(root):
        raise ValueError("slide already has a non-Morph transition; keep it or remove it explicitly")
    alt=anim.add_morph_transition(root,duration_ms)
    alt.find(f".//{{{anim.P159}}}morph").set("option",option)


def _stage_copy(pkg,src_part,node,obj,dst_part,dst_root,name,W,H,follow=None):
    """Copy ``node`` onto ``dst`` just outside the slide edge nearest to it.
    ``follow`` = (side, dx, dy) of a container it travels with."""
    clone=copy.deepcopy(node)
    g=obj["geometry"]
    x=ensure_xfrm(clone,g,W,H)
    b=box(x)
    b0=list(b)
    if follow:
        side,dx,dy=follow
        b[0]+=dx
        b[1]+=dy
        # A member sticking out of its container is pushed fully off-slide.
        if side=="left":
            b[0]=min(b[0],-b[2]-int(0.02*W))
        elif side=="right":
            b[0]=max(b[0],W+int(0.02*W))
        elif side=="top":
            b[1]=min(b[1],-b[3]-int(0.02*H))
        else:
            b[1]=max(b[1],H+int(0.02*H))
    else:
        cx,cy=g["x"]+g["w"]/2,g["y"]+g["h"]/2
        dist={"left":cx,"right":1-cx,"top":cy,"bottom":1-cy}
        side=min(dist,key=dist.get)
        if side=="left":
            b[0]=-b[2]-int(0.02*W)
        elif side=="right":
            b[0]=W+int(0.02*W)
        elif side=="top":
            b[1]=-b[3]-int(0.02*H)
        else:
            b[1]=H+int(0.02*H)
    set_box(x,b)
    props=clone.find("./*/p:cNvPr",NS)
    ids=[int(c.get("id")) for c in dst_root.iter(f"{{{P}}}cNvPr") if (c.get("id") or "").isdigit()]
    props.set("id",str(max(ids,default=1)+1))
    props.set("name",name)
    props.set("descr",(props.get("descr") or "")[:150]+" [Morph staging copy, off-slide]")
    # Relationship ids used by the clone (pictures, links) must exist on dst.
    src_rels={r.get("Id"):r for r in pkg.rels(src_part)}
    dst_rels=pkg.rels(dst_part)
    mapping={}
    for el in clone.iter():
        for attr,val in list(el.attrib.items()):
            if attr.startswith(f"{{{R}}}") and val in src_rels:
                if val not in mapping:
                    r=src_rels[val]
                    target=pkg.resolve(src_part,r.get("Target")) if r.get("TargetMode")!="External" else r.get("Target")
                    rid=f"rIdStage{len(dst_rels)+1}"
                    while any(x.get("Id")==rid for x in dst_rels):
                        rid+="x"
                    E.SubElement(dst_rels,f"{{{REL}}}Relationship",Id=rid,Type=r.get("Type"),
                                 Target=copy_rel_target(dst_part,target) if r.get("TargetMode")!="External" else target,
                                 **({"TargetMode":"External"} if r.get("TargetMode")=="External" else {}))
                    mapping[val]=rid
                el.set(attr,mapping[val])
    pkg.put(pkg.rels_name(dst_part),dst_rels)
    tree_append(dst_root.find("p:cSld/p:spTree",NS),clone)
    return {"name":name,"on":dst_part,"side":side,"source":obj["name"],"delta":(side,b[0]-b0[0],b[1]-b0[1])}


def _camera(root,objects,frame_box,target_box,W,H,resolver):
    """Transform every top-level object so frame_box maps onto target_box."""
    s=min(target_box[2]/frame_box[2],target_box[3]/frame_box[3])
    fcx,fcy=frame_box[0]+frame_box[2]/2,frame_box[1]+frame_box[3]/2
    tcx,tcy=target_box[0]+target_box[2]/2,target_box[1]+target_box[3]/2
    by={o["id"]:o for o in objects}
    for spid,node in shape_nodes(root).items():
        x=ensure_xfrm(node,(by.get(spid) or {}).get("geometry"),W,H)
        if x is None:
            continue
        b=box(x)
        cx,cy=b[0]+b[2]/2,b[1]+b[3]/2
        ncx,ncy=tcx+(cx-fcx)*s,tcy+(cy-fcy)*s
        set_box(x,[ncx-b[2]*s/2,ncy-b[3]*s/2,b[2]*s,b[3]*s])
        scale_text(node,s,resolver)
    return s


def camera_zoom(pkg,part,focus,fill=0.82,back=True,duration_ms=1400,receipt=None,reason=""):
    """Insert a push-in slide on ``focus`` (and a pull-back slide)."""
    model,by=_slide_models(pkg)
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    slide=by[part]
    fo=next(o for o in slide["objects"] if focus in (o["name"],o["id"]))
    g=fo["geometry"]
    frame=[g["x"]*W,g["y"]*H,g["w"]*W,g["h"]*H]
    target=[W*(1-fill)/2,H*(1-fill)/2,W*fill,H*fill]
    pr=pkg.xml(part)
    pn=shape_nodes(pr)
    for o in slide["objects"]:
        if not (o["name"] or "").startswith("!!"):
            set_name(pn[o["id"]],f"!!cam{slide['index']}-{o['id']}")
    pkg.put(part,pr)
    zoom=pkg.duplicate_slide(part,part,f"camera-zoom on {fo['name']}")
    zr=pkg.xml(zoom)
    s=_camera(zr,slide["objects"],frame,target,W,H,TypeResolver(pkg,zoom))
    _set_transition(zr,"byObject",duration_ms)
    pkg.put(zoom,zr)
    added=[zoom]
    if back:
        ret=pkg.duplicate_slide(part,zoom,f"camera pull-back from {fo['name']}")
        rr=pkg.xml(ret)
        _set_transition(rr,"byObject",duration_ms)
        pkg.put(ret,rr)
        added.append(ret)
    if receipt is not None:
        receipt.append({"technique":"camera-zoom","source":part,"focus":fo["name"],"scale":round(s,3),
                        "added_slides":added,"reason":reason})
    return added


def card_expand(pkg,part,card,panel=(0.06,0.2,0.88,0.72),duration_ms=1300,text_scale=1.35,receipt=None,reason=""):
    """Insert a slide where ``card`` grows into a panel; other objects drop out."""
    model,by=_slide_models(pkg)
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    slide=by[part]
    co=next(o for o in slide["objects"] if card in (o["name"],o["id"]))
    members=[o for o in slide["objects"] if o is not co and o["geometry"] and md._contains(co,o) and md._area(o)<md._area(co)]
    pr=pkg.xml(part)
    pn=shape_nodes(pr)
    for o in [co]+members:
        if not (o["name"] or "").startswith("!!"):
            set_name(pn[o["id"]],f"!!card{slide['index']}-{o['id']}")
    pkg.put(part,pr)
    new=pkg.duplicate_slide(part,part,f"card-expand {co['name']}")
    nr=pkg.xml(new)
    nn=shape_nodes(nr)
    keep={co["id"]}|{m["id"] for m in members}|{o["id"] for o in slide["objects"] if _is_title(o)}
    tree=nr.find("p:cSld/p:spTree",NS)
    for spid,node in nn.items():
        if spid not in keep:
            tree.remove(node)
    g=co["geometry"]
    frame=[g["x"]*W,g["y"]*H,g["w"]*W,g["h"]*H]
    target=[panel[0]*W,panel[1]*H,panel[2]*W,panel[3]*H]
    sx,sy=target[2]/frame[2],target[3]/frame[3]
    # The card stretches to the panel; its content scales uniformly so the
    # margins stay even and text keeps its proportions (it widens to use the
    # panel instead of stretching).
    s=min(sx,sy)
    resolver=TypeResolver(pkg,new)
    for o in [co]+members:
        node=nn[o["id"]]
        x=ensure_xfrm(node,o["geometry"],W,H)
        b=box(x)
        if o is co:
            set_box(x,target)
        else:
            left,top=(b[0]-frame[0])*s,(b[1]-frame[1])*s
            right=(frame[0]+frame[2]-b[0]-b[2])*s
            set_box(x,[target[0]+left,target[1]+top,max(b[2]*s,target[2]-left-right),b[3]*s])
        scale_text(node,min(text_scale,s),resolver)
    # The growing card travels over its neighbours.
    for o in [co]+members:
        tree.remove(nn[o["id"]])
        tree_append(tree,nn[o["id"]])
    _set_transition(nr,"byObject",duration_ms)
    pkg.put(new,nr)
    if receipt is not None:
        receipt.append({"technique":"card-expand","source":part,"card":co["name"],"added_slides":[new],"reason":reason})
    return [new]


def pan(pkg,part,items,duration_ms=1200,receipt=None,reason=""):
    """Carousel: one inserted slide per further item, the row shifted so that
    item sits where the first one was."""
    model,by=_slide_models(pkg)
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    slide=by[part]
    objs=[next(o for o in slide["objects"] if t in (o["name"],o["id"])) for t in items]
    pr=pkg.xml(part)
    pn=shape_nodes(pr)
    for o in slide["objects"]:
        if not (o["name"] or "").startswith("!!"):
            set_name(pn[o["id"]],f"!!pan{slide['index']}-{o['id']}")
    pkg.put(part,pr)
    anchor=objs[0]["geometry"]
    moving={o["id"] for o in slide["objects"] if not _is_title(o) and o["geometry"]
            and abs((o["geometry"]["y"]+o["geometry"]["h"]/2)-(anchor["y"]+anchor["h"]/2))<0.25}
    added=[]
    after=part
    for k,o in enumerate(objs[1:],1):
        dx=(anchor["x"]-o["geometry"]["x"])*W
        new=pkg.duplicate_slide(part,after,f"pan to {o['name']}")
        nr=pkg.xml(new)
        for spid,node in shape_nodes(nr).items():
            if spid in moving:
                obj=next(x for x in slide["objects"] if x["id"]==spid)
                x=ensure_xfrm(node,obj["geometry"],W,H)
                b=box(x)
                set_box(x,[b[0]+dx,b[1],b[2],b[3]])
        _set_transition(nr,"byObject",duration_ms)
        pkg.put(new,nr)
        added.append(new)
        after=new
    if receipt is not None:
        receipt.append({"technique":"pan","source":part,"items":items,"added_slides":added,"reason":reason})
    return added


# ---------------------------------------------------------------------------
# Plans


def propose(model):
    """Conservative automatic plan: continuity (with staging) wherever
    consecutive slides share an object or both have titles; scene suggestions
    are listed for the director to accept."""
    plan={"kind":"morph-scenes","version":"0.1","source_sha256":model["sha256"],"continuity":[],"scenes":[],"suggestions":[]}
    slides=model["slides"]
    for prev,cur in zip(slides,slides[1:]):
        if cur["has_transition"] and not cur.get("morph_in"):
            continue
        pairs=match_objects(prev,cur)
        if not pairs:
            continue
        option="byObject"
        titles=[(a,b) for a,b,why in pairs if why=="title to title"]
        if titles:
            a,b=titles[0]
            wa,wb=set(_norm(a["text"]).split()),set(_norm(b["text"]).split())
            if wa&wb and wa!=wb:
                option="byWord"
        plan["continuity"].append({"to_slide":cur["index"],"option":option,"stage":True,
                                   "reason":"; ".join(f"{a['name']} → {b['name']} ({why})" for a,b,why in pairs[:4])})
    # At most one scene idea per slide (camera > pan > card) and about one per
    # three slides overall: scenes cost slides and attention.
    ideas=[]
    for s in slides:
        if s.get("scene"):
            continue
        # Scenes are about layout, so objects count even when they animate.
        units=md._units(dict(s,objects=[dict(o,already_animated=False) for o in s["objects"]]))
        cards=[u for u in units if u["kind"]=="card" and len(u["objs"])>=2 and u["objs"][0]["name"]]
        best=None
        for u in units:
            if u["kind"]=="cycle" and u.get("grid"):
                best=best or (0,{"slide":s["index"],"technique":"camera-zoom","focus":u["members"][0]["name"],
                                 "why":"a matrix cell can be explored with a camera push-in and pull-back"})
            if u["kind"]=="process" and len(u["steps"])>=4:
                cand=(1,{"slide":s["index"],"technique":"pan","items":[st["step"]["name"] for st in u["steps"]],
                         "why":"a long row can scroll like a carousel"})
                best=min(best,cand,key=lambda x:x[0]) if best else cand
        if not best and 2<=len(cards)<=6:
            # The card that carries a headline number, else the first one.
            lead=next((u for u in cards if any(o.get("standalone_number") for o in u["objs"])),cards[0])
            best=(2,{"slide":s["index"],"technique":"card-expand","card":lead["objs"][0]["name"],
                     "why":"one of several cards can grow into a detail panel"})
        if best:
            ideas.append(best)
    cap=max(1,len(slides)//3)
    plan["suggestions"]=[x for _,x in sorted(ideas,key=lambda x:x[0])[:cap]]
    plan["suggestions"].sort(key=lambda x:x["slide"])
    return plan


def apply_plan(source,plan,output):
    pkg=Package(source)
    original=pkg.slides()
    if plan.get("source_sha256") and plan["source_sha256"]!=md.deck_model(source)["sha256"]:
        raise ValueError("plan source hash does not match the deck")
    receipt=[]
    # Scenes first (they add slides after their source), continuity on the
    # original sequence; inserted scene slides carry their own Morph.
    for sc in plan.get("scenes",[]):
        if not (sc.get("reason") or "").strip():
            raise ValueError(f"scene on slide {sc.get('slide')} needs a reason (it adds slides)")
        part=original[sc["slide"]-1]
        t=sc["technique"]
        if t=="camera-zoom":
            camera_zoom(pkg,part,sc["focus"],sc.get("fill",0.82),sc.get("back",True),sc.get("duration_ms",1400),receipt,sc["reason"])
        elif t=="card-expand":
            card_expand(pkg,part,sc["card"],tuple(sc.get("panel",(0.06,0.2,0.88,0.72))),sc.get("duration_ms",1300),
                        sc.get("text_scale",1.35),receipt,sc["reason"])
        elif t=="pan":
            pan(pkg,part,sc["items"],sc.get("duration_ms",1200),receipt,sc["reason"])
        else:
            raise ValueError(f"unknown scene technique {t!r}")
    order=pkg.slides()
    for c in plan.get("continuity",[]):
        cur=original[c["to_slide"]-1]
        prev=order[order.index(cur)-1]
        continuity(pkg,prev,cur,c.get("option","byObject"),c.get("duration_ms",1500),c.get("stage",True),
                   [tuple(p) for p in c.get("pairs",[])],receipt)
    pkg.save(output)
    report=verify_scenes(source,output)
    report["unsettled"]=settle_report(output)
    report["receipt"]=receipt
    return report


def unsettled(pkg,part,slide):
    """Objects a slide's own animation leaves away from their authored
    layout (moved, scaled, turned, dimmed). Morph starts from the authored
    layout, so these snap back when the next slide takes over."""
    import motion_engine as me
    root=pkg.xml(part)
    groups,_=me.effects_from_slide(root)
    if not groups:
        return []
    states=me.initial_states(slide["objects"],groups)
    for g in groups:
        states=me.advance(states,g)
    out=[]
    for o in slide["objects"]:
        st=states.get(o["id"])
        if not st or not st["visible"]:
            continue
        how=[k for k,bad in (("moved",abs(st["dx"])>0.005 or abs(st["dy"])>0.005),("scaled",abs(st["scale"]-1)>0.01),
                             ("turned",abs(st["rot"])>0.5),("dimmed",min(st["opacity"],st["alpha"])<0.98)) if bad]
        if how:
            out.append({"object":o["name"],"ends":how})
    return out


def settle_report(path):
    """Slides left by Morph that do not end in their authored layout."""
    model=md.deck_model(path)
    pkg=Package(path)
    report=[]
    for prev,cur in zip(model["slides"],model["slides"][1:]):
        if cur.get("morph_in"):
            bad=unsettled(pkg,prev["part"],prev)
            if bad:
                report.append({"slide":prev["index"],"objects":bad,
                               "fix":"end the slide on its full picture (a release click), or accept the snap"})
    return report


def verify_scenes(source,output):
    """Originals keep order, objects, text and geometry (names may gain !!);
    inserted slides are tagged scenes; extra objects only as off-slide staging."""
    problems=[]
    src,out=md.deck_model(source),md.deck_model(output)
    pkg=Package(output)
    tagged=[]
    for s in out["slides"]:
        name=pkg.xml(s["part"]).find("p:cSld",NS).get("name") or ""
        tagged.append(name.startswith(SCENE_PREFIX))
    originals=[s for s,t in zip(out["slides"],tagged) if not t]
    if len(originals)!=len(src["slides"]):
        problems.append(f"original slide count changed: {len(src['slides'])} -> {len(originals)}")
    for a,b in zip(src["slides"],originals):
        by={o["id"]:o for o in b["objects"]}
        for o in a["objects"]:
            p=by.get(o["id"])
            if p is None:
                problems.append(f"slide {a['index']}: object {o['name']!r} missing")
                continue
            if p["name"]!=o["name"] and not p["name"].startswith("!!"):
                problems.append(f"slide {a['index']}: {o['name']!r} renamed to non-Morph name {p['name']!r}")
            if p["text"]!=o["text"] or p["geometry"]!=o["geometry"]:
                problems.append(f"slide {a['index']}: {o['name']!r} text/geometry changed")
        for p in b["objects"]:
            if p["id"] in {o["id"] for o in a["objects"]}:
                continue
            g=p["geometry"] or {}
            off=g and (g["x"]+g["w"]<=0.001 or g["x"]>=0.999 or g["y"]+g["h"]<=0.001 or g["y"]>=0.999)
            if not (p["name"].startswith("!!") and off):
                problems.append(f"slide {a['index']}: unexpected visible object {p['name']!r}")
    return {"ok":not problems,"problems":problems,"source_slides":len(src["slides"]),
            "output_slides":len(out["slides"]),"scene_slides":sum(tagged),
            "powerpoint_playback_verified":False}


# ---------------------------------------------------------------------------
# Morph preview (simulation)


def _objects_xml(root):
    out={}
    for spid,node in shape_nodes(root).items():
        props=node.find("./*/p:cNvPr",NS)
        out.setdefault(props.get("name"),node)
    return out


def _font_sizes(node):
    return [int(r.get("sz")) for r in node.iter(f"{{{A}}}rPr") if (r.get("sz") or "").isdigit()]


def morph_frames(pkg,prev_part,cur_part,model,steps=10):
    """Frame roots for a simulated Morph from prev to cur (pairs by name)."""
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    by={s["part"]:s for s in model["slides"]}
    pr,cr=pkg.xml(prev_part),pkg.xml(cur_part)
    # The incoming slide is entered in its *start* state: objects and
    # paragraphs that enter by animation later are not there during Morph.
    start=anim.simulate_states(cr)[0][0]
    # The outgoing slide is left in its *end* state.
    end=anim.simulate_states(pr)[0][-1]
    for root,part,state in ((pr,prev_part,end),(cr,cur_part,start)):
        objs={o["id"]:o for o in by[part]["objects"]}
        resolver=TypeResolver(pkg,part)
        for spid,node in shape_nodes(root).items():
            ensure_xfrm(node,(objs.get(spid) or {}).get("geometry"),W,H)
            scale_text(node,1.0,resolver)  # explicit sizes so they can interpolate
        anim.apply_state_for_preview(root,state)
    po,co=_objects_xml(pr),_objects_xml(cr)
    frames=[]
    import motion_preview as mp
    for k in range(steps+1):
        t=k/steps
        e=t*t*(3-2*t)
        fr=copy.deepcopy(cr)
        fo=_objects_xml(fr)
        tree=fr.find("p:cSld/p:spTree",NS)
        for name,node in fo.items():
            if name in po:
                xa,xb=xfrm_of(po[name]),xfrm_of(node)
                if xa is None or xb is None:
                    continue
                ba,bb=box(xa),box(xb)
                set_box(xb,[ba[i]+(bb[i]-ba[i])*e for i in range(4)])
                sa,sb=_font_sizes(po[name]),_font_sizes(node)
                if sa and sb:
                    for rpr,va,vb in zip([r for r in node.iter(f"{{{A}}}rPr") if (r.get("sz") or "").isdigit()],sa,sb):
                        rpr.set("sz",str(int(va+(vb-va)*e)))
            elif e<0.999:
                mp._fade(node,max(0.0,e))
        if e<0.999:
            # Leaving objects fade behind the paired ones (an assumption: how
            # PowerPoint orders them during Morph has not been observed).
            first=next((c for c in tree if c.tag.split('}')[1] not in ("nvGrpSpPr","grpSpPr")),None)
            for name,node in po.items():
                if name not in co and not any(r for r in node.iter() if r.get(f"{{{R}}}embed") or r.get(f"{{{R}}}id")):
                    ghost=copy.deepcopy(node)
                    mp._fade(ghost,1-e)
                    if first is not None:
                        first.addprevious(ghost)
                    else:
                        tree_append(tree,ghost)
        frames.append(fr)
    return frames


def render_morph(pptx,slide_index,out_gif,steps=10,sheet=None):
    import motion_preview as mp
    pkg=Package(pptx)
    order=pkg.slides()
    model=md.deck_model(pptx)
    cur=order[slide_index-1]
    prev=order[slide_index-2]
    roots=morph_frames(pkg,prev,cur,model,steps)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        deck=td/"frames.pptx"
        mp.build_frames_deck(pptx,cur,roots,deck)
        subprocess.run([shutil.which("soffice"),"--headless","--convert-to","pdf","--outdir",str(td),str(deck)],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
        subprocess.run(["pdftoppm","-r","40","-scale-to-x","640","-scale-to-y","-1","-png",str(td/"frames.pdf"),str(td/"f")],
                       check=True,timeout=600)
        pngs=sorted(td.glob("f-*.png"))
        cmd=["convert","-loop","0"]
        for i,png in enumerate(pngs):
            label="before" if i==0 else ("after" if i==len(pngs)-1 else f"morph {i}/{len(pngs)-1}")
            cmd+=["-delay","80" if i in (0,len(pngs)-1) else "6","(",str(png),"-gravity","southeast","-fill","#666",
                  "-pointsize","13","-annotate","+8+6",f"{label} (simulated Morph)",")"]
        cmd.append(str(out_gif))
        subprocess.run(cmd,check=True,timeout=600)
        if sheet:
            pick=[pngs[0],pngs[len(pngs)//3],pngs[2*len(pngs)//3],pngs[-1]]
            subprocess.run(["montage"]+[str(p) for p in pick]+["-tile","4x","-geometry","+4+4",str(sheet)],check=True,timeout=300)
    return {"gif":str(out_gif),"frames":len(roots),"simulated":True,"powerpoint_playback_verified":False}


# ---------------------------------------------------------------------------
# CLI


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sp=ap.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("propose")
    a.add_argument("deck")
    a.add_argument("-o","--output",required=True)
    a=sp.add_parser("apply")
    a.add_argument("deck")
    a.add_argument("plan")
    a.add_argument("-o","--output",required=True)
    a=sp.add_parser("preview")
    a.add_argument("deck")
    a.add_argument("--slide",type=int,required=True,help="slide that is entered by Morph")
    a.add_argument("-o","--output",required=True)
    a.add_argument("--sheet")
    args=ap.parse_args(argv)
    if args.cmd=="propose":
        plan=propose(md.deck_model(args.deck))
        Path(args.output).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(f"continuity: {len(plan['continuity'])}, suggestions: {len(plan['suggestions'])} -> {args.output}")
    elif args.cmd=="apply":
        plan=json.loads(Path(args.plan).read_text(encoding="utf-8"))
        report=apply_plan(args.deck,plan,args.output)
        print(json.dumps({k:v for k,v in report.items() if k!="receipt"},ensure_ascii=False,indent=2))
        Path(args.output).with_suffix(".morph.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return 0 if report["ok"] else 1
    else:
        print(render_morph(args.deck,args.slide,args.output,sheet=args.sheet))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
