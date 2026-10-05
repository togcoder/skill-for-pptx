#!/usr/bin/env python3
"""Simulated motion preview: animated GIF + key-state contact sheet (T023).

Reads a slide's timing back from the PPTX (any deck, not only ours), samples
the motion with motion_engine's semantics, writes one frame slide per sample
into a temporary deck (moved/scaled/rotated/faded copies of the real slide),
renders it once with LibreOffice and assembles a GIF with ImageMagick.

This is a SIMULATION of the authored intent under the engine's stated
semantics. It is useful for catching wrong order, collisions and off-slide
motion. It is not PowerPoint playback.
"""
import argparse
import copy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
import pptx_animator as anim  # noqa: E402
import motion_engine as me  # noqa: E402

P,A,NS=anim.P,anim.A,anim.NS
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
CT="http://schemas.openxmlformats.org/package/2006/content-types"
SLIDE_CT="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
COLOR_TAGS={f"{{{A}}}{t}" for t in ("srgbClr","schemeClr","prstClr","sysClr","scrgbClr","hslClr")}


def _xfrm(node):
    for path in ("p:spPr/a:xfrm","p:xfrm","p:grpSpPr/a:xfrm"):
        x=node.find(path,NS)
        if x is not None:
            return x
    return None


def _ensure_xfrm(node,obj,W,H):
    x=_xfrm(node)
    if x is not None:
        return x
    sppr=node.find("p:spPr",NS)
    g=obj.get("geometry")
    if sppr is None or not g:
        return None
    x=E.Element(E.QName(A,"xfrm"))
    E.SubElement(x,E.QName(A,"off"),x=str(int(g["x"]*W)),y=str(int(g["y"]*H)))
    E.SubElement(x,E.QName(A,"ext"),cx=str(int(g["w"]*W)),cy=str(int(g["h"]*H)))
    sppr.insert(0,x)
    return x


def _fade(node,alpha):
    amt=str(int(max(0,min(1,alpha))*100000))
    for el in node.iter():
        if el.tag in COLOR_TAGS:
            for old in el.findall(f"{{{A}}}alpha"):
                el.remove(old)
            E.SubElement(el,E.QName(A,"alpha"),val=amt)
        elif el.tag==f"{{{A}}}blip":
            for old in el.findall(f"{{{A}}}alphaModFix"):
                el.remove(old)
            el.insert(0,E.Element(E.QName(A,"alphaModFix"),amt=amt))


def frame_root(root,objects,states,hidden_paras,W,H):
    """Copy of the slide root showing one simulated instant."""
    r=copy.deepcopy(root)
    by_id={o["id"]:o for o in objects}
    tree=r.find("p:cSld/p:spTree",NS)
    nodes=anim.top_level_objects(r)
    for spid,node in nodes.items():
        st=states.get(spid)
        if st is None:
            continue
        if not st["visible"]:
            tree.remove(node)
            continue
        obj=by_id.get(spid,{})
        moved=abs(st["dx"])>1e-6 or abs(st["dy"])>1e-6 or abs(st["scale"]-1)>1e-6 or abs(st["rot"])>1e-6
        if moved:
            x=_ensure_xfrm(node,obj,W,H)
            if x is not None:
                off,ext=x.find("a:off",NS),x.find("a:ext",NS)
                cx,cy=int(ext.get("cx")),int(ext.get("cy"))
                ncx,ncy=int(cx*st["scale"]),int(cy*st["scale"])
                off.set("x",str(int(int(off.get("x"))+st["dx"]*W-(ncx-cx)/2)))
                off.set("y",str(int(int(off.get("y"))+st["dy"]*H-(ncy-cy)/2)))
                ext.set("cx",str(max(1,ncx)))
                ext.set("cy",str(max(1,ncy)))
                if abs(st["rot"])>1e-6:
                    x.set("rot",str(int(int(x.get("rot","0"))+st["rot"]*60000)))
        alpha=st["opacity"]*st.get("alpha",1.0)
        if alpha<0.999:
            _fade(node,alpha)
    if hidden_paras:
        anim.apply_state_for_preview(r,{"hidden_objects":set(),"hidden_paragraphs":hidden_paras})
    timing=r.find("p:timing",NS)
    if timing is not None:
        r.remove(timing)
    return r


def _hidden_paragraphs(groups,upto_group,t):
    """Paragraph visibility (entrance-first paragraphs start hidden)."""
    first={}
    for g in groups:
        for e in g:
            if e.get("paragraph") is not None:
                cls=anim.PRESETS[e["preset"]][0]
                first.setdefault((e["spid"],e["paragraph"]),cls)
    hidden={k for k,v in first.items() if v=="entr"}
    for gi,g in enumerate(groups[:upto_group+1]):
        for start,end,e in me.schedule(g):
            if e.get("paragraph") is None:
                continue
            if gi<upto_group or t>=start:
                key=(e["spid"],e["paragraph"])
                (hidden.discard if anim.PRESETS[e["preset"]][0]=="entr" else hidden.add)(key)
    return hidden


def sample_frames(root,objects,fps=8,hold_ms=700,loop_window_ms=2500):
    """[(label, states, hidden_paragraphs, delay_ms)] covering every click group."""
    groups,autos=me.effects_from_slide(root)
    states=me.initial_states(objects,groups)
    frames=[("start",states,_hidden_paragraphs(groups,-1,0),hold_ms)]
    step=1000/fps
    for gi,g in enumerate(groups):
        # Ambient loops are sampled for a short window only (the GIF stays small);
        # one-shot motion is always sampled to its end.
        ends=[end if not e.get("loop") else start+min(end-start,loop_window_ms) for start,end,e in me.schedule(g)]
        dur=max(ends,default=0)
        t=step
        while t<dur:
            frames.append((f"{'auto' if autos[gi] else 'click'} {gi+1} · {t/1000:.1f}s",
                           me.state_at(states,g,t),_hidden_paragraphs(groups,gi,t),int(step)))
            t+=step
        states=me.advance(states,g)
        frames.append((f"{'auto' if autos[gi] else 'click'} {gi+1} · end",states,_hidden_paragraphs(groups,gi,float("inf")),hold_ms))
    return frames,groups


def build_frames_deck(source,slide_part,roots,out):
    """Package copy whose slide list is exactly the given frame roots."""
    with ZipFile(source) as z:
        names=set(z.namelist())
        pres=E.fromstring(z.read("ppt/presentation.xml"))
        prels=E.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
        ct=E.fromstring(z.read("[Content_Types].xml"))
        base,fname=slide_part.rsplit("/",1)
        rel_part=f"{base}/_rels/{fname}.rels"
        srels=E.fromstring(z.read(rel_part)) if rel_part in names else None
        if srels is not None:
            for r in list(srels):
                if r.get("Type","").endswith("/notesSlide"):
                    srels.remove(r)
        lst=pres.find("p:sldIdLst",NS)
        for sid in list(lst):
            lst.remove(sid)
        extra={}
        for i,root in enumerate(roots):
            part=f"ppt/slides/slide{90000+i}.xml"
            extra[part]=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
            if srels is not None:
                extra[f"ppt/slides/_rels/slide{90000+i}.xml.rels"]=E.tostring(srels,xml_declaration=True,encoding="UTF-8",standalone=True)
            rid=f"rIdFrame{i}"
            E.SubElement(prels,f"{{{REL}}}Relationship",Id=rid,
                         Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
                         Target=f"slides/slide{90000+i}.xml")
            E.SubElement(lst,anim.q("sldId"),{"id":str(100000+i),f"{{{R}}}id":rid})
            E.SubElement(ct,f"{{{CT}}}Override",PartName=f"/{part}",ContentType=SLIDE_CT)
        extra["ppt/presentation.xml"]=E.tostring(pres,xml_declaration=True,encoding="UTF-8",standalone=True)
        extra["ppt/_rels/presentation.xml.rels"]=E.tostring(prels,xml_declaration=True,encoding="UTF-8",standalone=True)
        extra["[Content_Types].xml"]=E.tostring(ct,xml_declaration=True,encoding="UTF-8",standalone=True)
        with ZipFile(out,"w",ZIP_DEFLATED) as dst:
            for item in z.infolist():
                dst.writestr(item,extra.pop(item.filename,z.read(item.filename)))
            for name,data in extra.items():
                dst.writestr(name,data)


def render_slide_motion(pptx,slide_index,out_gif,fps=8,width=640,sheet=None):
    """Render a simulated GIF (and optional key-state sheet) for one slide."""
    for tool in ("soffice","pdftoppm","convert"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required for motion preview")
    import motion_director as md
    model=md.deck_model(pptx)
    slide=model["slides"][slide_index-1]
    W,H=model["slide_size_emu"]["width"],model["slide_size_emu"]["height"]
    with ZipFile(pptx) as z:
        root=E.fromstring(z.read(slide["part"]))
    frames,groups=sample_frames(root,slide["objects"],fps=fps)
    roots=[frame_root(root,slide["objects"],st,hp,W,H) for _,st,hp,_ in frames]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        deck=td/"frames.pptx"
        build_frames_deck(pptx,slide["part"],roots,deck)
        subprocess.run([shutil.which("soffice"),"--headless","--convert-to","pdf","--outdir",str(td),str(deck)],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
        subprocess.run(["pdftoppm","-r","40","-scale-to-x",str(width),"-scale-to-y","-1","-png",
                        str(td/"frames.pdf"),str(td/"f")],check=True,timeout=900)
        pngs=sorted(td.glob("f-*.png"))
        if len(pngs)!=len(frames):
            raise RuntimeError(f"rendered {len(pngs)} frames, expected {len(frames)}")
        cmd=["convert","-loop","0"]
        for (label,_,_,delay),png in zip(frames,pngs):
            cmd+=["-delay",str(max(2,delay//10)),"(",str(png),"-gravity","southeast","-fill","#666",
                  "-pointsize","13","-annotate","+8+6",f"{label} (simulated)",")"]
        out_gif=Path(out_gif)
        out_gif.parent.mkdir(parents=True,exist_ok=True)
        cmd.append(str(out_gif))
        subprocess.run(cmd,check=True,timeout=900)
        if sheet:
            keys=[(label,png) for (label,_,_,_),png in zip(frames,pngs) if label=="start" or label.endswith("end")]
            mcmd=["montage"]
            for label,png in keys:
                mcmd+=["-label",label,str(png)]
            mcmd+=["-tile",f"{min(4,len(keys))}x","-geometry","+6+6","-pointsize","13",str(sheet)]
            subprocess.run(mcmd,check=True,timeout=300)
    return {"slide":slide_index,"frames":len(frames),"click_groups":len(groups),"gif":str(out_gif),
            "sheet":str(sheet) if sheet else None,"simulated":True,"powerpoint_playback_verified":False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pptx")
    ap.add_argument("--slide",type=int,required=True)
    ap.add_argument("-o","--output",required=True,help="GIF path")
    ap.add_argument("--sheet",help="optional key-state contact sheet PNG")
    ap.add_argument("--fps",type=int,default=8)
    args=ap.parse_args()
    print(render_slide_motion(args.pptx,args.slide,args.output,args.fps,sheet=args.sheet))


if __name__=="__main__":
    main()
