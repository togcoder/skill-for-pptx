#!/usr/bin/env python3
"""AI Motion Director for existing PowerPoint decks — one entry point (T019).

    inspect     compact, AI-readable outline of a deck (objects, text, notes,
                existing animation) + JSON model
    draft       autonomous Director v0.5 plan from deck evidence
    apply       validate a Director plan and write canonical native timing
    auto        draft + apply in one step
    storyboard  static render of every simulated click state (LibreOffice)
    verify      preservation + timing checks of an output against its source

Typical use by an AI agent:

    python3 scripts/motion_director.py inspect deck.pptx
    python3 scripts/motion_director.py draft deck.pptx -o director.json
    # read/edit director.json: script, click rhythm, effects
    python3 scripts/motion_director.py apply deck.pptx director.json -o out.pptx
    python3 scripts/motion_director.py storyboard out.pptx -o storyboard/

The output keeps every source slide, object, text and geometry; existing
animation is extended rather than replaced. Nothing here proves PowerPoint
playback; see docs/POWERPOINT_NATIVE_HARNESS.md for the native gate.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
from inspect_existing_deck import inspect_existing_deck  # noqa: E402
from validate_director_plan import validate as validate_director  # noqa: E402
from data_motion_recipes import chart_motion_recipe, number_counter_recipe  # noqa: E402
from chart_native_timing import chart_fanout, guard_chart_fanout, concrete_chart_filter  # noqa: E402
from generic_motion_recipes import focus_scale  # noqa: E402
from counter_component import insert_counter_stack  # noqa: E402
import pptx_animator as anim  # noqa: E402
import motion_engine as me  # noqa: E402

P=anim.P
A=anim.A
NS=anim.NS
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
PARSER=E.XMLParser(resolve_entities=False,no_network=True,remove_blank_text=False)

CINEMATIC={"text":("float-in",600),"bullet":("float-in",500),"card":("zoom",500),"step":("zoom",400),
           "connector":("wipe-right",300),"picture":("zoom",600),"callout":("float-in",600),"shape":("zoom",450)}
STYLES={
    # role -> (preset, duration)
    "subtle":{"text":("fade",400),"bullet":("fade",400),"card":("fade",400),"step":("fade",350),
              "connector":("wipe-right",250),"picture":("fade",500),"callout":("fade",400),"shape":("fade",400)},
    "modern":{"text":("float-in",600),"bullet":("float-in",500),"card":("float-in",600),"step":("fade",400),
              "connector":("wipe-right",300),"picture":("fade",600),"callout":("float-in",600),"shape":("fade",450)},
    "cinematic":CINEMATIC,
    "bold":{"text":("float-in",600),"bullet":("float-in",500),"card":("zoom",500),"step":("zoom",400),
            "connector":("wipe-right",300),"picture":("zoom",600),"callout":("zoom",500),"shape":("zoom",450)},
}
# Director v0.4 plans keep the T017 recipe look (Fade 320 ms, Wipe connectors).
LEGACY_V04_STYLE={k:(("wipe-right",320) if k=="connector" else ("fade",320)) for k in STYLES["subtle"]}
SEQUENCE_CUES=re.compile(r"\b(then|next|finally|first|second|third|walk|step|in order|after that|lastly"
                         r"|đầu tiên|sau đó|tiếp theo|cuối cùng|lần lượt|từng bước|bước)\b",re.I)
TITLE_TYPES={"title","ctrTitle"}
CHROME_TYPES={"dt","ftr","sldNum","hdr"}


# ---------------------------------------------------------------------------
# Deck model


def _xml(z,part):
    return E.fromstring(z.read(part),PARSER)


def _rels(z,part):
    base,name=part.rsplit("/",1)
    rp=f"{base}/_rels/{name}.rels"
    if rp not in z.namelist():
        return {}
    out={}
    for r in _xml(z,rp).findall(f"{{{REL}}}Relationship"):
        target=r.get("Target","")
        if r.get("TargetMode")=="External":
            continue
        parts=(base+"/"+target).split("/") if not target.startswith("/") else target.lstrip("/").split("/")
        stack=[]
        for p in parts:
            if p=="..":
                stack.pop()
            elif p and p!=".":
                stack.append(p)
        out[r.get("Id")]=(r.get("Type",""),"/".join(stack))
    return out


def _ph(node):
    ph=node.find("./*/p:nvPr/p:ph",NS)
    if ph is None:
        return None
    return {"type":ph.get("type","obj"),"idx":ph.get("idx")}


def _xfrm(node):
    x=node.find("./p:spPr/a:xfrm",NS)
    if x is None:
        x=node.find("./p:xfrm",NS)
    if x is None:
        x=node.find("./p:grpSpPr/a:xfrm",NS)
    if x is None:
        return None
    off,ext=x.find("a:off",NS),x.find("a:ext",NS)
    if off is None or ext is None:
        return None
    return [int(off.get("x")),int(off.get("y")),int(ext.get("cx")),int(ext.get("cy"))]


def _ph_geometry(root,ph):
    if root is None:
        return None
    candidates=[]
    for node in root.iter(f"{{{P}}}sp"):
        other=_ph(node)
        if other is None:
            continue
        candidates.append((other,node))
    for other,node in candidates:
        if ph["idx"] is not None and other["idx"]==ph["idx"]:
            return _xfrm(node)
    family={"ctrTitle":"title","subTitle":"body","obj":"body"}.get(ph["type"],ph["type"])
    for other,node in candidates:
        ofam={"ctrTitle":"title","subTitle":"body","obj":"body"}.get(other["type"],other["type"])
        if other["type"]==ph["type"] or ofam==family:
            return _xfrm(node)
    return None


def _max_font_pt(node):
    sizes=[int(r.get("sz")) for r in node.iter(f"{{{A}}}rPr",f"{{{A}}}defRPr",f"{{{A}}}endParaRPr") if (r.get("sz") or "").isdigit()]
    return max(sizes)/100 if sizes else None


def _has_fill(node):
    sppr=node.find("p:spPr",NS)
    if sppr is None:
        return False
    if sppr.find("a:noFill",NS) is not None:
        return False
    if any(sppr.find(f"a:{t}",NS) is not None for t in ("solidFill","gradFill","pattFill","blipFill")):
        return True
    style=node.find("p:style/a:fillRef",NS)
    return style is not None and style.get("idx") not in (None,"0")


def deck_model(path):
    """Inventory + slide-level facts needed for directing (resolved geometry,
    placeholders, paragraphs, font sizes, existing animation)."""
    path=Path(path)
    inv=inspect_existing_deck(path)
    if inv["errors"]:
        raise ValueError("Invalid deck: "+"; ".join(inv["errors"]))
    size=inv["slide_size_emu"] or {"width":12192000,"height":6858000}
    W,H=size["width"],size["height"]
    model={"source":str(path),"sha256":inv["source_sha256"],"slide_size_emu":size,"inventory":inv,"slides":[]}
    with ZipFile(path) as z:
        for s in inv["slides"]:
            root=_xml(z,s["part"])
            rels=_rels(z,s["part"])
            layout_part=s.get("layout_part")
            layout=_xml(z,layout_part) if layout_part and layout_part in z.namelist() else None
            master=None
            if layout_part:
                for typ,target in _rels(z,layout_part).values():
                    if typ.endswith("/slideMaster") and target in z.namelist():
                        master=_xml(z,target)
            objects=anim.top_level_objects(root)
            groups=anim.read_main_sequence(root)
            animated={e["spid"] for g in groups for e in g["effects"]}
            inv_by_id={sh["id"]:sh for sh in s["shapes"]}
            names=[sh["name"] for sh in s["shapes"]]
            objs=[]
            for spid,node in objects.items():
                sh=inv_by_id.get(spid)
                if sh is None:
                    continue
                ph=_ph(node)
                emu=_xfrm(node)
                inherited=False
                if emu is None and ph is not None:
                    emu=_ph_geometry(layout,ph) or _ph_geometry(master,ph)
                    inherited=emu is not None
                geom=None
                if emu:
                    geom={"x":emu[0]/W,"y":emu[1]/H,"w":emu[2]/W,"h":emu[3]/H}
                paras=anim.text_paragraphs(node)
                number=(sh.get("data_semantics") or {}).get("standalone_number")
                blip=node.find(f".//{{{A}}}blip")
                image=rels.get(blip.get(f"{{{R}}}embed"),(None,None))[1] if blip is not None else None
                objs.append({
                    "id":spid,
                    "name":sh["name"],
                    "token":sh["name"] if sh["name"] and names.count(sh["name"])==1 else spid,
                    "kind":sh["kind"],
                    "placeholder":ph,
                    "geometry":geom,
                    "geometry_inherited":inherited,
                    "text":"\n".join(p["text"] for p in paras) or sh.get("text"),
                    "paragraphs":paras,
                    "max_font_pt":_max_font_pt(node),
                    "filled":_has_fill(node),
                    "has_text_body":node.find("p:txBody",NS) is not None,
                    "chart_summary":sh.get("chart_summary"),
                    "standalone_number":number,
                    "already_animated":spid in animated,
                    "image":image,
                    "preset_geometry":(node.find("p:spPr/a:prstGeom",NS).get("prst") if node.find("p:spPr/a:prstGeom",NS) is not None else None),
                    "z":sh["z_index"],
                })
            model["slides"].append({
                "index":s["index"],
                "aspect":W/H,
                "part":s["part"],
                "notes":s.get("speaker_notes"),
                "has_transition":s["has_transition"] or anim.existing_transition(root),
                "morph_in":root.find(f".//{{{anim.P159}}}morph") is not None,
                "existing_click_groups":len(groups),
                "existing_animated_ids":sorted(animated,key=int),
                "objects":objs,
            })
    return model


def outline(model):
    """Human/AI-readable text outline."""
    lines=[f"# {Path(model['source']).name}  sha256={model['sha256'][:12]}…  slides={len(model['slides'])}"]
    for s in model["slides"]:
        lines.append(f"\n## Slide {s['index']}"+(f"  [existing animation: {s['existing_click_groups']} click group(s)]" if s["existing_click_groups"] else "")
                     +("  [transition]" if s["has_transition"] else ""))
        if s["notes"]:
            lines.append(f"notes: {s['notes'][:300]}")
        for o in s["objects"]:
            g=o["geometry"]
            pos=f"@({g['x']:.2f},{g['y']:.2f} {g['w']:.2f}x{g['h']:.2f})" if g else "@(?)"
            tags=[o["kind"]]
            if o["placeholder"]:
                tags.append(f"ph:{o['placeholder']['type']}")
            if o["chart_summary"]:
                cs=o["chart_summary"]
                tags.append(f"chart:{cs.get('primary_type')} {cs.get('series_count')}s×{cs.get('category_count')}c")
            if o["standalone_number"]:
                tags.append("number")
            if o["already_animated"]:
                tags.append("ANIMATED")
            if o["max_font_pt"]:
                tags.append(f"{o['max_font_pt']:g}pt")
            text=""
            if len(o["paragraphs"])>1:
                text=" | ".join(f"¶{p['index']}{'·'*p['level']} {p['text'][:50]}" for p in o["paragraphs"][:8])
            elif o["text"]:
                text=o["text"][:80].replace("\n"," ")
            lines.append(f"- id={o['id']} \"{o['name']}\" {' '.join(tags)} {pos} {text}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Autonomous draft


def _center(o):
    g=o["geometry"]
    return (g["x"]+g["w"]/2,g["y"]+g["h"]/2)


def _contains(outer,inner):
    g=outer["geometry"]
    cx,cy=_center(inner)
    return g["x"]<=cx<=g["x"]+g["w"] and g["y"]<=cy<=g["y"]+g["h"]


def _area(o):
    g=o["geometry"]
    return g["w"]*g["h"] if g else 0


def _reading_key(unit_objs):
    xs=[o["geometry"]["x"] for o in unit_objs if o["geometry"]]
    ys=[o["geometry"]["y"] for o in unit_objs if o["geometry"]]
    return (round(min(ys,default=1)/0.12),min(xs,default=1))


def _is_heading(o):
    """Short text such as a title, label or wrapped heading (T022)."""
    text=o["text"] or ""
    return bool(o["has_text_body"] and text and len(text)<=90 and len(o["paragraphs"])<=2)


def _implicit_title(slide):
    """Title of a slide built from plain text boxes (no title placeholder)."""
    if any(o["placeholder"] and o["placeholder"]["type"] in TITLE_TYPES for o in slide["objects"]):
        return None
    cands=[o for o in slide["objects"] if o["geometry"] and _is_heading(o) and o["geometry"]["y"]<0.2]
    return min(cands,key=lambda o:(o["geometry"]["y"],o["geometry"]["x"])) if cands else None


def _is_text_title_slide(slide):
    """First slide made only of heading-like text (no placeholders)."""
    if slide["index"]!=1 or not slide["objects"]:
        return False
    texts=[o for o in slide["objects"] if o["text"]]
    return bool(texts) and all(_is_heading(o) for o in texts) and not any(
        o["kind"] in ("chart","table") for o in slide["objects"])


def _label_body_pairs(objs,used):
    """Pair a short label with the larger text block directly below it."""
    pairs=[]
    texts=[o for o in objs if o["geometry"] and o["text"] and o["id"] not in used]
    for label in sorted(texts,key=lambda o:o["geometry"]["y"]):
        if label["id"] in used or not _is_heading(label) or len(label["paragraphs"])>1:
            continue
        lg=label["geometry"]
        below=[b for b in texts if b is not label and b["id"] not in used
               and -0.02<=b["geometry"]["y"]-(lg["y"]+lg["h"])<0.05
               and min(lg["x"]+lg["w"],b["geometry"]["x"]+b["geometry"]["w"])-max(lg["x"],b["geometry"]["x"])>0.3*lg["w"]
               and (len(b["text"])>150 or b["geometry"]["h"]>=2*lg["h"])]
        if below:
            body=min(below,key=lambda b:b["geometry"]["y"])
            pairs.append([label,body])
            used.update([label["id"],body["id"]])
    return pairs


def _radial_group(objs,used,aspect=16/9):
    """Self-contained shapes of similar size arranged around a common centre
    (cycle / hub-and-spoke diagrams). Returns (members in clockwise order from
    the top, hub or None) or None."""
    shapes=[o for o in objs if o["geometry"] and o["kind"]=="shape" and o["id"] not in used and o["text"]]
    buckets={}
    for o in shapes:
        g=o["geometry"]
        buckets.setdefault((round(g["w"]/0.03),round(g["h"]/0.03)),[]).append(o)
    for members in sorted(buckets.values(),key=len,reverse=True):
        if not 3<=len(members)<=8:
            continue
        # Measure in true slide proportions so circles stay circles.
        pts=[(_center(m)[0]*aspect,_center(m)[1]) for m in members]
        cx=sum(p[0] for p in pts)/len(pts)
        cy=sum(p[1] for p in pts)/len(pts)
        dists=[math.dist(p,(cx,cy)) for p in pts]
        mean=sum(dists)/len(dists)
        if mean<0.08 or (max(dists)-min(dists))>0.35*mean:
            continue
        if max(p[1] for p in pts)-min(p[1] for p in pts)<0.1:
            continue  # a row is a process, not a cycle
        angles=sorted(math.atan2(p[1]-cy,p[0]-cx) for p in pts)
        gaps=[b-a for a,b in zip(angles,angles[1:])]+[angles[0]+2*math.pi-angles[-1]]
        if max(gaps)>math.pi:
            continue
        others=[o for o in objs if o not in members and o["geometry"]]
        if any(_contains(m,o) and _area(o)<_area(m) for m in members for o in others):
            continue  # labels are separate objects; tracks would tear them apart
        order=sorted(members,key=lambda m:(math.atan2(_center(m)[1]-cy,_center(m)[0]*aspect-cx)+math.pi/2)%(2*math.pi))
        hub=next((o for o in others if o["id"] not in used and o["text"]
                  and math.dist((_center(o)[0]*aspect,_center(o)[1]),(cx,cy))<0.08),None)
        return order,hub
    return None


def _units(slide,continuing=()):
    title=_implicit_title(slide)
    objs=[o for o in slide["objects"]
          if not (o["placeholder"] and o["placeholder"]["type"] in TITLE_TYPES|CHROME_TYPES)
          and not o["already_animated"] and o is not title and o["id"] not in continuing]
    with_geom=[o for o in objs if o["geometry"]]
    used=set()
    units=[]

    for o in with_geom:
        if o["kind"]=="chart":
            units.append({"kind":"chart","objs":[o]})
            used.add(o["id"])

    radial=_radial_group(with_geom,used,slide.get("aspect",16/9))
    if radial:
        members,hub=radial
        units.append({"kind":"cycle","objs":([hub] if hub else [])+members,"members":members,"hub":hub})
        used.update(o["id"] for o in members)
        if hub:
            used.add(hub["id"])

    # Cards: filled shapes that contain the centres of other objects.
    for o in sorted(with_geom,key=_area,reverse=True):
        if o["id"] in used or o["kind"]!="shape" or not o["filled"]:
            continue
        members=[m for m in with_geom if m is not o and m["id"] not in used and m["kind"]!="chart"
                 and _area(m)<_area(o) and _contains(o,m)]
        if members:
            members.sort(key=lambda m:(m["geometry"]["y"],m["geometry"]["x"]))
            units.append({"kind":"card","objs":[o]+members})
            used.update([o["id"]]+[m["id"] for m in members])

    # Process rows: >=3 similar shapes on one row, connectors between them.
    rest=[o for o in with_geom if o["id"] not in used and o["kind"]=="shape"]
    rows={}
    for o in rest:
        g=o["geometry"]
        key=(round(_center(o)[1]/0.05),round(g["w"]/0.02),round(g["h"]/0.02))
        rows.setdefault(key,[]).append(o)
    for key,members in rows.items():
        if len(members)<3:
            continue
        members.sort(key=lambda m:m["geometry"]["x"])
        cy=_center(members[0])[1]
        connectors=[c for c in with_geom if c["kind"]=="connector" and c["id"] not in used
                    and abs(_center(c)[1]-cy)<0.08]
        steps=[]
        for i,m in enumerate(members):
            incoming=[c for c in connectors if i>0 and members[i-1]["geometry"]["x"]<_center(c)[0]<m["geometry"]["x"]+m["geometry"]["w"]/2]
            steps.append({"step":m,"connectors":incoming})
            used.update([m["id"]]+[c["id"] for c in incoming])
        units.append({"kind":"process","objs":members,"steps":steps})

    for pair in _label_body_pairs(objs,used):
        units.append({"kind":"labeled","objs":pair})

    # A short heading sitting directly under the title belongs to the title zone.
    if title is not None:
        tg=title["geometry"]
        for o in with_geom:
            if o["id"] not in used and _is_heading(o) and -0.02<=o["geometry"]["y"]-(tg["y"]+tg["h"])<0.06:
                used.add(o["id"])

    for o in objs:
        if o["id"] in used:
            continue
        area=_area(o)
        if o["kind"] in ("picture","media","group","connector","shape") and not o["has_text_body"] and o["kind"]!="picture":
            # Decorative or unlabeled shapes stay static unless large.
            if area<0.05:
                continue
        if o["kind"]=="group" and area<0.03:
            continue
        if o["kind"]=="picture" and (area<0.08 or area>=0.5):
            continue  # icons stay put; a backdrop picture moves in the slide intro instead
        if o["has_text_body"] and not o["text"]:
            continue
        if len(o["paragraphs"])>=2 and not _is_heading(o):
            units.append({"kind":"bullets","objs":[o]})
        else:
            kind="picture" if o["kind"]=="picture" else ("text" if o["text"] else "shape")
            units.append({"kind":kind,"objs":[o]})
        used.add(o["id"])
    units.sort(key=lambda u:_reading_key(u["objs"]))
    return units


def _paragraph_groups(o):
    groups=[]
    for p in o["paragraphs"]:
        if p["level"]>0 and groups:
            groups[-1].append(p["index"])
        else:
            groups.append([p["index"]])
    return groups


def _beat(bid,purpose,operation,targets,timing,effect=None,duration=None,**extra):
    beat={"id":bid,"purpose":purpose,"operation":operation,"targets":targets,
          "reuse_existing":True,"same_slide":True,"timing_intent":timing}
    if effect:
        beat["effect"]=effect
    if duration is not None:
        beat["duration_ms"]=duration
    beat.update(extra)
    return beat


def _click(cid,purpose,members,stable,pause,boundary):
    return {"id":cid,"purpose":purpose,"motion_beats":members,"stable_state":stable,
            "pause_after":pause,"boundary_reason":boundary}


def _label(o):
    return (o["text"] or o["name"] or o["id"]).split("\n")[0][:60]


MAX_DECOR=8


def _free(o,continuing):
    return (o["geometry"] and not o["already_animated"] and o["id"] not in continuing
            and not (o["placeholder"] and o["placeholder"]["type"] in CHROME_TYPES))


def _owned(units):
    ids={o["id"] for u in units for o in u["objs"]}
    ids.update(c["id"] for u in units for st in u.get("steps",()) for c in st["connectors"])
    return ids


def _decor(slide,units,continuing=()):
    """Small text-free accents (bars, lines) that no content unit owns.
    Drawn in at slide start they give the slide a motion-graphic intro."""
    used=_owned(units)
    def line_like(o,aspect=slide.get("aspect",16/9)):
        w,h=o["geometry"]["w"]*aspect,o["geometry"]["h"]
        return o["kind"]=="connector" or max(w,h)>=4*max(min(w,h),1e-6)
    out=[o for o in slide["objects"] if o["id"] not in used and _free(o,continuing)
         and o["kind"] in ("shape","connector") and not o["text"] and _area(o)<0.05 and line_like(o)]
    # ponytail: a busy pattern (> MAX_DECOR pieces) stays static; cluster it into one group if needed.
    return out if len(out)<=MAX_DECOR else []


def _hero_pictures(slide,units,continuing=()):
    """Large pictures that are visible from the start and keep moving (Ken Burns)."""
    used=_owned(units)
    return [o for o in slide["objects"] if o["id"] not in used and _free(o,continuing)
            and o["kind"]=="picture" and _area(o)>=0.08]


def _intro(slide,decor,heroes,nid,aspect=16/9):
    """One automatic click: accents draw in along their long axis while hero
    pictures start a slow push-in. Returns (beats, click) or ([], None)."""
    beats=[]
    for direction in ("wipe-right","wipe-down"):
        parts=[o for o in decor if ("wipe-right" if o["geometry"]["w"]*aspect>=o["geometry"]["h"] else "wipe-down")==direction]
        if parts:
            beats.append(_beat(nid("accent"),"Accent shapes draw in as the slide opens.","stagger-reveal",
                               [o["token"] for o in parts],"with-previous",direction,250))
    if heroes:
        beats.append(_beat(nid("kenburns"),"Keep the picture alive with a slow push-in while the slide is discussed.",
                           "choreography",[o["token"] for o in heroes],"with-previous",
                           recipe="ken-burns",motion_parameters={"duration_ms":7000,"scale":1.06}))
    if not beats:
        return [],None
    beats[0]["timing_intent"]="on-slide-start"
    click=_click(nid("click"),"Slide opens with its motion-graphic intro.",[b["id"] for b in beats],
                 "Accents drawn; pictures drifting.","presenter-explanation","First reveal on this slide.")
    return beats,click


def draft_slide(slide,style="modern",counters=False,continuing=(),outgoing=()):
    """Return (slide plan or None, note). ``outgoing`` objects carry into the
    next slide by Morph, so they must end where they were authored (no Ken Burns)."""
    if slide["existing_click_groups"]:
        return None,"existing native animation preserved as the slide's choreography"
    n=[0]

    def nid(prefix):
        n[0]+=1
        return f"{prefix}-{n[0]}"

    aspect=slide.get("aspect",16/9)
    types={(o["placeholder"] or {}).get("type") for o in slide["objects"]}
    if "ctrTitle" in types or ("subTitle" in types and len(slide["objects"])<=3) or _is_text_title_slide(slide):
        beats,click=_intro(slide,_decor(slide,[],continuing) if style!="subtle" else [],
                           _hero_pictures(slide,[],set(continuing)|set(outgoing)),nid,aspect)
        if not click:
            return None,"title slide kept static"
        click["pause_after"]="slide-complete"
        return ({"source_index":slide["index"],"role":"title slide",
                 "objective":"Title stays still; accents and picture give the opening life.",
                 "beats":beats,"click_beats":[click],"components":[]},
                "title text static; automatic motion-graphic intro")
    units=_units(slide,continuing)
    if len(units)==1 and units[0]["kind"]=="picture":
        units=[]  # the picture is the slide: visible from the start, kept alive by Ken Burns
    beats,intro=_intro(slide,_decor(slide,units,continuing) if style!="subtle" else [],
                       _hero_pictures(slide,units,set(continuing)|set(outgoing)),nid,aspect)
    if not units and not intro:
        return None,("no content beyond the title"+(" (continuing objects arrive by Morph)" if continuing else "")
                     +(" (objects carry on to the next slide by Morph)" if outgoing else ""))
    fx=STYLES[style]
    notes=slide["notes"] or ""
    sequenced=bool(SEQUENCE_CUES.search(notes))
    clicks=[intro] if intro else []

    prev_kind=None
    for unit in units:
        kind=unit["kind"]
        if kind=="chart":
            o=unit["objs"][0]
            rec=chart_motion_recipe(o["chart_summary"])
            b=_beat(nid("chart"),"Build the chart data in its reading order so each series lands as the presenter explains it.",
                    "chart-build",[o["token"]],"on-click",
                    data_motion={"kind":"chart","chart_type":rec["chart_type"],"recipe":rec["recipe"],
                                 "build":rec["preferred_build"],"animate_background":False,"rationale":rec["reason"]})
            beats.append(b)
            clicks.append(_click(nid("click"),"Show the data.",[b["id"]],"Complete chart visible for discussion.",
                                 "presenter-explanation","Data is discussed before its interpretation." if clicks else "First reveal on this slide."))
        elif kind=="cycle":
            members,hub=unit["members"],unit["hub"]
            ids=[]
            if hub:
                hb=_beat(nid("hub"),f"Establish the centre '{_label(hub)}'.","reveal",[hub["token"]],"on-click",
                         fx["card"][0],fx["card"][1])
                beats.append(hb)
                ids.append(hb["id"])
            ab=_beat(nid("assemble"),"Elements assemble around the centre in cycle order.","choreography",
                     [m["token"] for m in members],"with-previous" if hub else "on-click",
                     recipe="assemble",motion_parameters={"from":"center","stagger_ms":140,"duration_ms":700})
            beats.append(ab)
            ids.append(ab["id"])
            clicks.append(_click(nid("click"),"Show the whole cycle.",ids,"All elements in place.",
                                 "presenter-explanation","The cycle is introduced as one system." if clicks else "First reveal on this slide."))
            if len(members)<=5 and style!="subtle":
                for m in members:
                    others=[x["token"] for x in members if x is not m]
                    sb=_beat(nid("focus"),f"Walk the cycle: focus '{_label(m)}'.","choreography",[m["token"]]+others,
                             "on-click",recipe="spotlight",motion_parameters={"scale":1.12,"dim":0.35,"duration_ms":500})
                    beats.append(sb)
                    clicks.append(_click(nid("click"),f"Discuss '{_label(m)}'.",[sb["id"]],
                                         f"'{_label(m)}' enlarged, the rest dimmed.","presenter-explanation",
                                         "Each stage of the cycle is explained on its own."))
                rb=_beat(nid("release"),"Return to the whole cycle.","choreography",[m["token"] for m in members],
                         "on-click",recipe="release",motion_parameters={"duration_ms":500})
                beats.append(rb)
                clicks.append(_click(nid("click"),"Back to the full cycle.",[rb["id"]],"Full cycle restored.",
                                     "slide-complete","The tour ends by showing the system as a whole again."))
        elif kind=="labeled":
            label,body=unit["objs"]
            lp,ld=fx["text"]
            groups=_paragraph_groups(body) if len(body["paragraphs"])>=2 else []
            if groups and len(groups)<=6:
                lb=_beat(nid("label"),f"Introduce '{_label(label)}'.","reveal",[label["token"]],"on-click",lp,ld)
                beats.append(lb)
                members=[lb["id"]]
                bp,bd=fx["bullet"]
                for gi,g in enumerate(groups):
                    pb=_beat(nid("para"),f"Reveal paragraph {g[0]} of '{_label(label)}'.","text-build",[body["token"]],
                             "after-previous" if gi==0 else "on-click",bp,bd,paragraphs=g)
                    beats.append(pb)
                    if gi==0:
                        members.append(pb["id"])
                        clicks.append(_click(nid("click"),f"Present '{_label(label)}'.",members,
                                             "Label and its first paragraph visible.","presenter-explanation",
                                             "New labelled section." if clicks else "First reveal on this slide."))
                    else:
                        clicks.append(_click(nid("click"),"Advance to the next paragraph.",[pb["id"]],
                                             "Next paragraph visible.","presenter-explanation",
                                             "The paragraph turns to a separate idea for the presenter to explain."))
            else:
                b=_beat(nid("block"),f"Reveal '{_label(label)}' with its text.","stagger-reveal",
                        [label["token"],body["token"]],"on-click",fx["text"][0],fx["text"][1])
                beats.append(b)
                clicks.append(_click(nid("click"),f"Present '{_label(label)}'.",[b["id"]],"Label and text visible.",
                                     "presenter-explanation",
                                     "Each labelled alternative is a separate talking point." if clicks else "First reveal on this slide."))
        elif kind=="bullets":
            o=unit["objs"][0]
            groups=[]
            for p in o["paragraphs"]:
                if p["level"]>0 and groups:
                    groups[-1].append(p["index"])
                else:
                    groups.append([p["index"]])
            per_click=len(groups)<=6
            preset,dur=fx["bullet"]
            if per_click:
                for gi,g in enumerate(groups):
                    b=_beat(nid("point"),f"Reveal point: {o['paragraphs'][[p['index'] for p in o['paragraphs']].index(g[0])]['text'][:60]}",
                            "text-build",[o["token"]],"on-click",preset,dur,paragraphs=g)
                    beats.append(b)
                    clicks.append(_click(nid("click"),"Advance to the next point.",[b["id"]],
                                         "Points so far are visible while the presenter speaks to the newest one.",
                                         "presenter-explanation","Each point gets its own spoken explanation." if clicks else "First reveal on this slide."))
            else:
                b=_beat(nid("points"),"Reveal the list in order within one click.","text-build",[o["token"]],"on-click",preset,dur,
                        paragraphs=[i for g in groups for i in g])
                beats.append(b)
                clicks.append(_click(nid("click"),"Show the list.",[b["id"]],"Whole list visible.","presenter-explanation",
                                     "Long list is revealed as one unit to avoid click fatigue." if clicks else "First reveal on this slide."))
        elif kind=="card":
            card=unit["objs"]
            preset,dur=fx["card"]
            members=[]
            number=next((m for m in card[1:] if m["standalone_number"] and (m["max_font_pt"] or 0)>=28),None)
            reveal_targets=[m["token"] for m in card if not (counters and m is number)]
            b=_beat(nid("card"),f"Reveal the card '{_label(number or card[-1])}' as one unit.","reveal",reveal_targets,"on-click",preset,dur)
            beats.append(b)
            members.append(b["id"])
            if counters and number:
                rec=number_counter_recipe(number["standalone_number"])
                if rec:
                    cb=_beat(nid("count"),f"Count up to the hero metric {number['text']}.","kpi-highlight",[number["token"]],"with-previous",
                             data_motion={"kind":"number-counter","recipe":rec["recipe"],"from_value":rec["from_value"],
                                          "to_value":rec["to_value"],"duration_ms":rec["duration_ms"],"steps":rec["steps"],
                                          "prefix":rec["prefix"],"suffix":rec["suffix"],"decimal_places":rec["decimal_places"],
                                          "implementation":"stepped-text","rationale":"Hero KPI on its own card."})
                    beats.append(cb)
                    members.append(cb["id"])
            clicks.append(_click(nid("click"),f"Present {_label(number or card[-1])}.",members,"Card fully visible.",
                                 "presenter-explanation","Each card is a separate talking point." if clicks else "First reveal on this slide."))
        elif kind=="process":
            preset,dur=fx["step"]
            cpreset,cdur=fx["connector"]
            ids=[]
            for si,step in enumerate(unit["steps"]):
                targets=[c["token"] for c in step["connectors"]]
                step_beats=[]
                if targets:
                    cb=_beat(nid("link"),"Draw the connector that leads into the next step.","stagger-reveal",targets,
                             "on-click" if sequenced else "after-previous",cpreset,cdur)
                    beats.append(cb)
                    step_beats.append(cb["id"])
                sb=_beat(nid("step"),f"Reveal step '{_label(step['step'])}'.","reveal",[step["step"]["token"]],
                         "after-previous" if (targets or (not sequenced and si>0)) else "on-click",preset,dur)
                if not targets and si==0:
                    sb["timing_intent"]="on-click"
                beats.append(sb)
                step_beats.append(sb["id"])
                if sequenced:
                    clicks.append(_click(nid("click"),f"Walk to step '{_label(step['step'])}'.",step_beats,
                                         "Steps so far visible.","presenter-explanation",
                                         "Speaker notes walk the steps one at a time." if clicks else "First reveal on this slide."))
                else:
                    ids.extend(step_beats)
            if not sequenced:
                clicks.append(_click(nid("click"),"Show the process flow.",ids,"Full process visible.","presenter-explanation",
                                     "Process is introduced as one unit." if clicks else "First reveal on this slide."))
        else:
            o=unit["objs"][0]
            role="callout" if prev_kind in ("chart","process","card") else ("picture" if kind=="picture" else "text" if o["text"] else "shape")
            preset,dur=fx[role]
            b=_beat(nid("reveal"),f"Reveal '{_label(o)}'.","reveal",[o["token"]],"on-click",preset,dur)
            beats.append(b)
            members=[b["id"]]
            if kind=="picture" and o["id"] not in outgoing:
                kb=_beat(nid("kenburns"),f"Keep '{_label(o)}' alive with a slow push-in.","choreography",[o["token"]],
                         "after-previous",recipe="ken-burns",motion_parameters={"duration_ms":6000,"scale":1.05})
                beats.append(kb)
                members.append(kb["id"])
            reason=("The conclusion lands after the evidence has been discussed." if role=="callout"
                    else "New idea for the presenter to introduce.")
            clicks.append(_click(nid("click"),f"Introduce '{_label(o)}'.",members,"Content visible.","presenter-explanation",
                                 reason if clicks else "First reveal on this slide."))
        prev_kind=kind

    # Keep click rhythm humane: merge tail clicks beyond the cap.
    cap=8
    if len(clicks)>cap:
        tail=clicks[cap-1:]
        merged=tail[0]
        for extra in tail[1:]:
            for mid in extra["motion_beats"]:
                beat=next(b for b in beats if b["id"]==mid)
                if beat["timing_intent"]=="on-click":
                    beat["timing_intent"]="after-previous"
                merged["motion_beats"].append(mid)
        merged["boundary_reason"]+=" Remaining reveals merged to keep at most 8 clicks."
        clicks=clicks[:cap-1]+[merged]
    clicks[-1]["pause_after"]="slide-complete"
    plan={"source_index":slide["index"],"role":"report slide",
          "objective":f"Audience follows slide {slide['index']} one idea at a time.",
          "beats":beats,"click_beats":clicks,"components":[]}
    return plan,f"{len(clicks)} click(s), {len(beats)} motion beat(s)"


def _norm_text(t):
    return re.sub(r"\s+"," ",(t or "")).strip().lower()


def shared_objects(prev,cur):
    """Objects of ``cur`` that continue from ``prev`` (same text, same image or
    the same !! Morph name) -> (ids, names of those whose geometry changes)."""
    moved=[]
    shared=[]
    for o in cur["objects"]:
        if not o["geometry"]:
            continue
        for p in prev["objects"]:
            if not p["geometry"] or p["kind"]!=o["kind"]:
                continue
            same=((o["image"] and o["image"]==p["image"])
                  or (o["text"] and _norm_text(o["text"])==_norm_text(p["text"]))
                  or ((o["name"] or "").startswith("!!") and o["name"]==p["name"]))
            if not same:
                continue
            shared.append(o["id"])
            if max(abs(o["geometry"][k]-p["geometry"][k]) for k in ("x","y","w","h"))>0.02:
                moved.append(o["name"])
            break
    return shared,moved


def detect_morph_pairs(model):
    """Consecutive slides sharing an object (same text or same image) whose
    geometry changes: a Morph transition lets that object travel between them."""
    out=[]
    slides=model["slides"]
    for prev,cur in zip(slides,slides[1:]):
        if cur["has_transition"]:
            continue
        shared,moved=shared_objects(prev,cur)
        if moved:
            out.append({"slide":cur["index"],"kind":"morph","duration_ms":1500,"continuing_ids":shared,
                        "reason":"Continuity: "+", ".join(f"'{m}'" for m in moved[:4])+" moves/resizes from the previous slide."})
    return out


def draft(model,goal="",style="modern",counters=False,morph=True):
    if style not in STYLES:
        raise ValueError(f"style must be one of {sorted(STYLES)}")
    slides=[]
    notes={}
    transitions=detect_morph_pairs(model) if morph else []
    continuing={t["slide"]:set(t["continuing_ids"]) for t in transitions}
    slides_by={s["index"]:s for s in model["slides"]}
    outgoing={t["slide"]-1:set(shared_objects(slides_by[t["slide"]],slides_by[t["slide"]-1])[0]) for t in transitions}
    for t in transitions:
        t.pop("continuing_ids")
    for s in model["slides"]:
        if s.get("morph_in") and s["index"]>1:
            # An existing Morph carries shared objects in; re-entering them would break continuity.
            continuing.setdefault(s["index"],set()).update(shared_objects(slides_by[s["index"]-1],s)[0])
            outgoing.setdefault(s["index"]-1,set()).update(shared_objects(s,slides_by[s["index"]-1])[0])
    for s in model["slides"]:
        plan,note=draft_slide(s,style,counters,continuing.get(s["index"],()),outgoing.get(s["index"],()))
        notes[s["index"]]=note
        if plan:
            slides.append(plan)
    has_notes=any(s["notes"] for s in model["slides"])
    has_existing=any(s["existing_click_groups"] for s in model["slides"])
    inv=model["inventory"]
    return {
        "version":"0.6",
        "kind":"existing-deck-motion-director",
        "source":{"pptx_sha256":model["sha256"],"inventory_version":inv["version"],
                  "source_slide_count":len(model["slides"])},
        "user_instruction":goal or "Add presenter-paced native motion to the existing deck.",
        "script":{
            "source":"speaker-notes" if has_notes else ("existing-timing" if has_existing else "inferred"),
            "summary":"Each slide reveals its content in reading order, one talking point per click; "
                      "data before conclusions; existing animation preserved.",
            "evidence":["slide titles and reading order","speaker notes" if has_notes else "no speaker notes",
                        "existing native animation" if has_existing else "no existing animation"],
            "beats":[f"slide {s['index']}: {(next((o['text'] for o in s['objects'] if o['text']),'') or '')[:60]}" for s in model["slides"]],
        },
        "preservation":{"preserve_text_by_default":True,"preserve_media_by_default":True,
                        "preserve_theme_by_default":True,"preserve_slide_order_by_default":True,
                        "slide_count_policy":"preserve"},
        "slides":slides,
        **({"transitions":transitions} if transitions else {}),
        "target_slide_count":len(model["slides"]),
        "research_metadata":{"sources":[],"draft_notes":{str(k):v for k,v in notes.items()},
                             "style":style,"drafted_by":"motion_director.py heuristic v0.1"},
    }


# ---------------------------------------------------------------------------
# Compile Director v0.4/v0.5 -> canonical click groups


def _resolve(slide_model,token):
    hits=[o for o in slide_model["objects"] if token in (o["name"],o["id"],o["token"])]
    ids={o["id"] for o in hits}
    if len(ids)!=1:
        raise ValueError(f"slide {slide_model['index']}: target {token!r} is {'ambiguous' if ids else 'missing'}")
    return hits[0]


def _beat_effects(beat,slide_model,style="modern",states=None):
    timing=beat["timing_intent"]
    first_trigger={"on-click":"click","with-previous":"with","after-previous":"after","on-slide-start":"click"}[timing]
    objs=[_resolve(slide_model,t) for t in beat["targets"]]
    op=beat["operation"]
    dm=beat.get("data_motion")
    effects=[]
    if op=="choreography":
        by_token={}
        for o in slide_model["objects"]:
            for key in (o["name"],o["id"],o["token"]):
                by_token.setdefault(key,o)
        tracks=None
        if beat["recipe"]=="tracks":
            tracks=[{"target":_resolve(slide_model,tr["target"]),"keyframes":tr["keyframes"]}
                    for tr in beat["tracks"]]
        effects=me.compile_choreography(beat["recipe"],objs,states,by_token,beat["id"],
                                        beat.get("motion_parameters") or {},tracks)
        effects[0]["trigger"]=first_trigger
        for e in effects[1:]:
            e["trigger"]="with"
        return effects
    default=LEGACY_V04_STYLE if style=="v0.4" else STYLES.get(style,STYLES["modern"])
    if isinstance(dm,dict) and dm.get("kind")=="chart":
        o=objs[0]
        cs=o["chart_summary"] or {}
        guard=guard_chart_fanout(dm["build"],cs.get("series_count") or 1,cs.get("category_count"),dm.get("fanout_limit",24))
        build=guard["effective_build"]
        steps=chart_fanout(build,cs.get("series_count") or 1,cs.get("category_count")) or [None]
        preset=anim.FILTER_TO_PRESET.get(beat.get("effect_filter") or concrete_chart_filter(dm["chart_type"]),"fade")
        unit=max(300,min(800,2400//len(steps)))
        for i,step in enumerate(steps):
            effects.append({"preset":preset,"spid":o["id"],"trigger":first_trigger if i==0 else "after",
                            "duration_ms":unit,"chart":step,"chart_build":{"as-whole":"as-whole","series":"series","category":"category",
                            "series-elements":"seriesEl","category-elements":"categoryEl"}[build],
                            "chart_background":dm.get("animate_background",False)})
        return effects
    if isinstance(dm,dict) and dm.get("kind")=="number-counter":
        o=objs[0]
        return [{"preset":"counter","spid":o["id"],"name":o["name"],"trigger":first_trigger,
                 "duration_ms":dm["duration_ms"],"counter":dm,"text":o["text"],"beat":beat["id"]}]
    role_default={"text-build":"bullet","reveal":"text","stagger-reveal":"text","process-reveal":"step"}.get(op,"text")
    preset=beat.get("effect")
    duration=beat.get("duration_ms")
    if op in ("reveal","stagger-reveal","process-reveal"):
        for i,o in enumerate(objs):
            role="connector" if o["kind"]=="connector" else role_default
            p,d=default[role]
            pr=preset or p
            if pr not in anim.ENTRANCES:
                raise ValueError(f"beat {beat['id']}: reveal needs an entrance effect, got {pr}")
            if op=="reveal":
                effects.append({"preset":pr,"spid":o["id"],"trigger":first_trigger if i==0 else "with",
                                "delay_ms":0 if i==0 else min(400,80*i),"duration_ms":duration if duration is not None else d})
            else:
                effects.append({"preset":pr,"spid":o["id"],"trigger":first_trigger if i==0 else "after",
                                "duration_ms":duration if duration is not None else d})
    elif op=="text-build":
        o=objs[0]
        paras=beat.get("paragraphs") or [p["index"] for p in o["paragraphs"]]
        valid={p["index"]:p for p in o["paragraphs"]}
        p,d=default["bullet"]
        pr=preset or p
        for i,idx in enumerate(paras):
            if idx not in valid:
                raise ValueError(f"beat {beat['id']}: {o['name']!r} has no nonempty paragraph {idx}")
            level=valid[idx]["level"]
            trig=first_trigger if i==0 else ("with" if level>0 else "after")
            effects.append({"preset":pr,"spid":o["id"],"paragraph":idx,"trigger":trig,
                            "delay_ms":0 if trig!="with" else 150,"duration_ms":duration if duration is not None else d})
    elif op in ("focus","emphasize"):
        o=objs[0]
        effects.append({"preset":preset or "pulse","spid":o["id"],"trigger":first_trigger,
                        "duration_ms":duration if duration is not None else 250,
                        "scale":focus_scale(o)})
    elif op=="exit":
        for i,o in enumerate(objs):
            effects.append({"preset":preset or "fade-out","spid":o["id"],"trigger":first_trigger if i==0 else "with",
                            "duration_ms":duration if duration is not None else 400})
    elif op=="dim":
        for i,o in enumerate(objs):
            effects.append({"preset":"dim","spid":o["id"],"trigger":first_trigger if i==0 else "with",
                            "duration_ms":duration if duration is not None else 400,
                            "opacity":(beat.get("motion_parameters") or {}).get("opacity",0.35)})
    elif op=="move":
        mp=beat["motion_parameters"]
        effects.append({"preset":"path","spid":objs[0]["id"],"trigger":first_trigger,"points":mp["points"],
                        "duration_ms":mp.get("duration_ms",duration or 800)})
    elif op=="rotate":
        mp=beat["motion_parameters"]
        effects.append({"preset":"spin","spid":objs[0]["id"],"trigger":first_trigger,"by_deg":mp["by_deg"],
                        "duration_ms":mp.get("duration_ms",duration or 800)})
    else:
        raise ValueError(f"beat {beat['id']}: unsupported operation {op!r}")
    for e in effects:
        e["beat"]=beat["id"]
    return effects


ENTERING_OPS={"reveal","stagger-reveal","process-reveal"}


def _first_visibility(plan_slide,slide_model):
    """spid -> "enter" | "exit" for the first beat that changes visibility."""
    beats={b["id"]:b for b in plan_slide["beats"]}
    first={}
    for click in plan_slide["click_beats"]:
        for mid in click["motion_beats"]:
            b=beats[mid]
            op=b["operation"]
            ids=[_resolve(slide_model,t)["id"] for t in b["targets"]]
            if isinstance(b.get("data_motion"),dict) or op in ENTERING_OPS:
                kind,touched="enter",ids
            elif op=="choreography" and b.get("recipe")=="assemble":
                kind,touched="enter",ids
            elif op=="choreography" and b.get("recipe")=="tracks":
                for tr in b.get("tracks",[]):
                    vis=next((k["visible"] for k in sorted(tr["keyframes"],key=lambda k:k["t"]) if "visible" in k),None)
                    if vis is not None:
                        first.setdefault(_resolve(slide_model,tr["target"])["id"],"enter" if vis else "exit")
                continue
            elif op=="exit" or (op=="choreography" and b.get("recipe") in ("disperse","zoom-focus")):
                kind,touched="exit",ids if op!="choreography" or b["recipe"]=="disperse" else ids[1:]
            else:
                continue
            for spid in touched:
                first.setdefault(spid,kind)
    return first


def compile_slide(plan_slide,slide_model,style="modern",prior_groups=()):
    """Compile a slide plan into click groups. Object state (position, scale,
    rotation, opacity, visibility) is carried through existing timing and
    earlier clicks so compound choreography continues where it left off.
    Objects whose first visibility change in the plan is an entrance start
    hidden (unless existing timing already animates them)."""
    beats={b["id"]:b for b in plan_slide["beats"]}
    objects=[o for o in slide_model["objects"]]

    def run(initial):
        states=initial
        for g in prior_groups:
            states=me.advance(states,g)
        clicks=[]
        looping={}
        for ci,click in enumerate(plan_slide["click_beats"]):
            effects=[]
            for mid in click["motion_beats"]:
                beat=beats[mid]
                current=me.advance(states,effects) if effects else states
                effects.extend(_beat_effects(beat,slide_model,style,current))
            issues=[]
            for e in effects:
                key=(e["spid"],me.PROP_OF.get(e["preset"]))
                if key in looping and e.get("paragraph") is None:
                    issues.append(f"object {e['spid']} is still looping from click {looping[key]}; "
                                  f"it cannot also {e['preset']} on a later click")
            for e in effects:
                if e.get("repeat")=="indefinite":
                    looping[(e["spid"],me.PROP_OF.get(e["preset"]))]=click["id"]
            issues+=me.conflicts(effects)
            if issues:
                raise ValueError(f"slide {slide_model['index']} click {click['id']}: "+"; ".join(issues))
            start="auto" if ci==0 and beats[click["motion_beats"][0]]["timing_intent"]=="on-slide-start" else "click"
            clicks.append({"id":click["id"],"start":start,"effects":effects})
            states=me.advance(states,effects)
        return clicks

    initial=me.initial_states(objects,list(prior_groups))
    prior_touched={e["spid"] for g in prior_groups for e in g if e.get("paragraph") is None}
    for spid,first in _first_visibility(plan_slide,slide_model).items():
        if spid not in prior_touched and first=="enter":
            initial[spid]["visible"]=False
    return run(initial)


def _expand_counters(root,clicks):
    """Insert stepped-text proxies for counter effects and replace each counter
    with appear/disappear effects inside the same time block."""
    generated=[]
    for click in clicks:
        out=[]
        for eff in click["effects"]:
            if eff["preset"]!="counter":
                out.append(eff)
                continue
            dm=eff["counter"]
            component=insert_counter_stack(root,{
                "target":{"source_id":eff["spid"],"source_name":eff["name"]},
                "from_value":dm["from_value"],"to_value":dm["to_value"],"steps":dm["steps"],
                "decimal_places":dm["decimal_places"],"prefix":dm.get("prefix",""),"suffix":dm.get("suffix",""),
                "preserve_final_text":eff["text"],
            })
            proxies=component["proxies"]
            unit=max(30,dm["duration_ms"]//(len(proxies)+1))
            for i,proxy in enumerate(proxies):
                out.append({"preset":"appear","spid":proxy["source_id"],"trigger":eff["trigger"] if i==0 else "with",
                            "delay_ms":i*unit,"duration_ms":0,"beat":eff["beat"]})
                out.append({"preset":"disappear","spid":proxy["source_id"],"trigger":"with",
                            "delay_ms":(i+1)*unit,"duration_ms":0,"beat":eff["beat"]+"-x"})
            out.append({"preset":"appear","spid":eff["spid"],"trigger":"with",
                        "delay_ms":len(proxies)*unit,"duration_ms":0,"beat":eff["beat"]})
            generated.append({"source_id":eff["spid"],"proxy_count":len(proxies),
                              "proxy_texts":[p["text"] for p in proxies]})
        click["effects"]=out
    return generated


# ---------------------------------------------------------------------------
# Apply


def _write_package(source,destination,updates):
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=destination.parent,suffix=".pptx")
    os.close(fd)
    try:
        with ZipFile(source) as src, ZipFile(tmp,"w",ZIP_DEFLATED) as dst:
            for item in src.infolist():
                dst.writestr(item,updates.get(item.filename,src.read(item.filename)))
        os.replace(tmp,destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def apply(source,plan,destination,force=False,style=None):
    source=Path(source)
    destination=Path(destination)
    if destination.exists() and not force:
        raise ValueError(f"refuse to overwrite {destination} (use --force)")
    if destination.resolve()==source.resolve():
        raise ValueError("output must differ from source")
    model=deck_model(source)
    if plan.get("version") not in ("0.4","0.5","0.6"):
        raise ValueError("apply requires Director v0.4, v0.5 or v0.6")
    errors=validate_director(plan,model["inventory"])
    if errors:
        raise ValueError("Invalid director plan:\n  - "+"\n  - ".join(errors))
    style=style or ("v0.4" if plan["version"]=="0.4" else (plan.get("research_metadata") or {}).get("style","modern"))
    by_index={s["index"]:s for s in model["slides"]}
    updates={}
    receipts=[]
    with ZipFile(source) as z:
        for ps in plan["slides"]:
            sm=by_index[ps["source_index"]]
            policy=ps.get("existing_timing","extend")
            if policy=="replace" and not (ps.get("replace_reason") or "").strip():
                raise ValueError(f"slide {sm['index']}: replacing existing timing requires replace_reason")
            root=E.fromstring(z.read(sm["part"]),PARSER)
            prior=[] if policy=="replace" else me.effects_from_slide(root)[0]
            clicks=compile_slide(ps,sm,style,prior)
            counters=_expand_counters(root,clicks)
            receipt=anim.apply_timeline(root,clicks,mode="replace" if policy=="replace" else "extend")
            receipt["slide"]=sm["index"]
            receipt["counters"]=counters
            updates[sm["part"]]=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
            receipts.append(receipt)
        for tr in plan.get("transitions") or []:
            sm=by_index[tr["slide"]]
            data=updates.get(sm["part"]) or z.read(sm["part"])
            root=E.fromstring(data,PARSER)
            if tr["kind"]!="morph":
                raise ValueError(f"unsupported transition kind {tr['kind']!r}")
            anim.add_morph_transition(root,tr.get("duration_ms",1500))
            updates[sm["part"]]=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
            receipts.append({"slide":sm["index"],"transition":"morph","reason":tr["reason"]})
    _write_package(source,destination,updates)
    report=verify(source,destination)
    report["receipts"]=receipts
    return report


# ---------------------------------------------------------------------------
# Verify


def verify(source,output):
    """Preservation + timing checks. Returns a report dict with `ok`."""
    problems=[]
    warnings=[]
    src,out=deck_model(source),deck_model(output)
    if len(src["slides"])!=len(out["slides"]):
        problems.append("slide count changed")
    with ZipFile(source) as a, ZipFile(output) as b:
        an,bn=set(a.namelist()),set(b.namelist())
        if an!=bn:
            problems.append(f"package parts changed: +{sorted(bn-an)} -{sorted(an-bn)}")
        changed=sorted(n for n in an&bn if a.read(n)!=b.read(n))
        slide_parts={s["part"] for s in src["slides"]}
        if any(n not in slide_parts for n in changed):
            problems.append(f"non-slide parts changed: {[n for n in changed if n not in slide_parts]}")
        slides=[]
        for s_src,s_out in zip(src["slides"],out["slides"]):
            entry={"slide":s_src["index"],"changed":s_src["part"] in changed}
            out_by={o["id"]:o for o in s_out["objects"]}
            for o in s_src["objects"]:
                p=out_by.get(o["id"])
                if p is None or p["name"]!=o["name"]:
                    problems.append(f"slide {s_src['index']}: object {o['id']} {o['name']!r} missing")
                    continue
                if p["text"]!=o["text"] or p["geometry"]!=o["geometry"]:
                    problems.append(f"slide {s_src['index']}: object {o['name']!r} text/geometry changed")
            added=[o for o in s_out["objects"] if o["id"] not in {x["id"] for x in s_src["objects"]}]
            if any(not o["name"].startswith("__counter_") for o in added):
                problems.append(f"slide {s_src['index']}: unexpected new objects {[o['name'] for o in added]}")
            if entry["changed"]:
                root=_xml(b,s_out["part"])
                entry["transition"]="morph" if root.find(f".//{{{anim.P159}}}morph") is not None else None
                timing=root.find("p:timing",NS)
                if timing is None:
                    entry["click_groups"]=0
                    entry["storyboard"]=[]
                    slides.append(entry)
                    continue
                ids=[c.get("id") for c in timing.iter(f"{{{P}}}cTn")]
                if len(ids)!=len(set(ids)):
                    problems.append(f"slide {s_src['index']}: duplicate cTn ids")
                present=set(anim.top_level_objects(root))
                for t in timing.iter(f"{{{P}}}spTgt"):
                    if t.get("spid") not in present:
                        problems.append(f"slide {s_src['index']}: animation targets missing spid {t.get('spid')}")
                for bld in timing.iter(f"{{{P}}}bldP",f"{{{P}}}bldGraphic"):
                    if bld.get("spid") not in present:
                        problems.append(f"slide {s_src['index']}: build list targets missing spid {bld.get('spid')}")
                states,groups=anim.simulate_states(root)
                final=states[-1]
                proxies={o["id"] for o in added}
                visible_end={o["id"] for o in s_out["objects"]}-final["hidden_objects"]
                lost=[o["name"] for o in s_src["objects"] if o["id"] not in visible_end]
                if lost:
                    warnings.append(f"slide {s_src['index']}: hidden at end of slide: {lost}")
                if final["hidden_paragraphs"]:
                    warnings.append(f"slide {s_src['index']}: paragraphs hidden at end: {sorted(final['hidden_paragraphs'])}")
                leftover=proxies-final["hidden_objects"]
                if leftover:
                    problems.append(f"slide {s_src['index']}: counter proxies remain visible at end: {sorted(leftover)}")
                if s_src["existing_click_groups"] and len(groups)<s_src["existing_click_groups"]:
                    problems.append(f"slide {s_src['index']}: existing click groups were lost")
                entry["click_groups"]=len(groups)
                entry["existing_click_groups"]=s_src["existing_click_groups"]
                mgroups,_=me.effects_from_slide(root)
                mstates=me.initial_states(s_out["objects"],mgroups)
                for gi,g in enumerate(mgroups,1):
                    problems.extend(f"slide {s_src['index']} click {gi}: {c}" for c in me.conflicts(g))
                    mstates=me.advance(mstates,g)
                    warnings.extend(me.layout_warnings(
                        [o for o in s_out["objects"] if not o["name"].startswith("__counter_")],
                        mstates,f"slide {s_src['index']} after click {gi}"))
                entry["storyboard"]=_storyboard_text(s_out,states,groups)
            slides.append(entry)
    return {"ok":not problems,"problems":problems,"warnings":warnings,
            "source_sha256":src["sha256"],"output_sha256":out["sha256"],"slides":slides,
            "powerpoint_playback_verified":False}


def _storyboard_text(slide_model,states,groups):
    names={o["id"]:o for o in slide_model["objects"]}
    lines=[]
    for gi,g in enumerate(groups,1):
        parts=[]
        for e in g["effects"]:
            o=names.get(e["spid"])
            if o and o["name"].startswith("__counter_"):
                continue
            label=(o["name"] if o else e["spid"])
            if e["paragraph"] is not None and o:
                para=next((p["text"] for p in o["paragraphs"] if p["index"]==e["paragraph"]),"")
                label=f"{label} ¶{e['paragraph']} '{para[:40]}'"
            verb={"visible":"+","hidden":"−"}.get(e["visibility"],"~")
            kind=""
            if verb=="~":
                kind={"path":" (move)","emph":" (emphasis)"}.get(e["class"]," (motion)")
            parts.append(f"{verb}{label}{kind}")
        dedup=list(dict.fromkeys(parts))
        lines.append(f"{'auto' if g['auto'] else 'click'} {gi}: "+", ".join(dedup))
    return lines


# ---------------------------------------------------------------------------
# Storyboard render (static simulation of stable states via LibreOffice)


def storyboard(pptx,outdir,slides=None,dpi=60):
    soffice=shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice (soffice) is required for storyboard rendering")
    pptx=Path(pptx)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    model=deck_model(pptx)
    frames=[]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        with ZipFile(pptx) as z:
            pres=_xml(z,"ppt/presentation.xml")
            prels=_rels(z,"ppt/presentation.xml")
            for s in model["slides"]:
                if slides and s["index"] not in slides:
                    continue
                root=_xml(z,s["part"])
                states,_=anim.simulate_states(root)
                for si,state in enumerate(states):
                    if len(states)==1 and si==0:
                        label="static"
                    else:
                        label=state["label"]
                    p2=E.fromstring(E.tostring(pres))
                    lst=p2.find("p:sldIdLst",NS)
                    for sid in list(lst):
                        if prels.get(sid.get(f"{{{R}}}id"),("",""))[1]!=s["part"]:
                            lst.remove(sid)
                    r2=anim.apply_state_for_preview(E.fromstring(E.tostring(root)),state)
                    name=f"s{s['index']:02d}_{si:02d}.pptx"
                    _write_package(pptx,td/name,{"ppt/presentation.xml":E.tostring(p2,xml_declaration=True,encoding="UTF-8",standalone=True),
                                                  s["part"]:E.tostring(r2,xml_declaration=True,encoding="UTF-8",standalone=True)})
                    frames.append((s["index"],si,label,td/name))
        if not frames:
            return []
        subprocess.run([soffice,"--headless","--convert-to","png","--outdir",str(td/"png")]+[str(f[3]) for f in frames],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=600)
        sheets=[]
        for idx in sorted({f[0] for f in frames}):
            imgs=[]
            for (si_idx,si,label,f) in frames:
                if si_idx!=idx:
                    continue
                png=td/"png"/(f.stem+".png")
                if png.exists():
                    imgs.append(("-label",f"slide {idx} · {label}",str(png)))
            if not imgs:
                continue
            out=outdir/f"slide-{idx:02d}.png"
            cmd=["montage"]
            for lab,txt,path in imgs:
                cmd+=[lab,txt,path]
            cmd+=["-tile",f"{min(4,len(imgs))}x","-geometry","480x270+6+6","-pointsize","14",str(out)]
            if shutil.which("montage"):
                subprocess.run(cmd,check=True,timeout=120)
            else:
                shutil.copy(imgs[-1][2],out)
            sheets.append(str(out))
    return sheets


# ---------------------------------------------------------------------------
# Reports + CLI


def markdown_report(report,plan=None):
    lines=["# Motion Director report","",
           f"- source sha256: `{report['source_sha256']}`",
           f"- output sha256: `{report['output_sha256']}`",
           f"- structural checks: {'PASS' if report['ok'] else 'FAIL'}",
           "- PowerPoint playback: **not verified** (structural + simulated states only)",""]
    if report["problems"]:
        lines+=["## Problems"]+[f"- {p}" for p in report["problems"]]+[""]
    if report["warnings"]:
        lines+=["## Warnings"]+[f"- {w}" for w in report["warnings"]]+[""]
    notes=((plan or {}).get("research_metadata") or {}).get("draft_notes",{})
    lines.append("## Slides")
    for s in report["slides"]:
        head=f"### Slide {s['slide']}"
        if not s["changed"]:
            lines+=[head,f"unchanged — {notes.get(str(s['slide']),'no motion planned')}",""]
            continue
        extra=f" (existing groups kept: {s['existing_click_groups']})" if s.get("existing_click_groups") else ""
        if s.get("transition"):
            extra+=f"; enters with {s['transition'].capitalize()} transition"
        lines+=[head,f"{s['click_groups']} click group(s){extra}"]+[f"- {l}" for l in s["storyboard"]]+[""]
    return "\n".join(lines)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dump(obj,path):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sp=ap.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("inspect",help="print an AI-readable outline")
    a.add_argument("deck")
    a.add_argument("--json",help="also write the deck model JSON here")
    a=sp.add_parser("draft",help="autonomous Director v0.5 plan")
    a.add_argument("deck")
    a.add_argument("-o","--output",required=True)
    a.add_argument("--goal",default="")
    a.add_argument("--style",default="modern",choices=sorted(STYLES))
    a.add_argument("--counters",action="store_true",help="use stepped-text KPI counters (adds proxy shapes)")
    a.add_argument("--no-morph",action="store_true",help="do not add Morph transitions")
    for name in ("apply","auto"):
        a=sp.add_parser(name)
        a.add_argument("deck")
        if name=="apply":
            a.add_argument("plan")
        a.add_argument("-o","--output",required=True)
        a.add_argument("--report",help="markdown report path (default OUTPUT.report.md)")
        a.add_argument("--force",action="store_true")
        if name=="auto":
            a.add_argument("--goal",default="")
            a.add_argument("--style",default="modern",choices=sorted(STYLES))
            a.add_argument("--counters",action="store_true")
            a.add_argument("--no-morph",action="store_true",help="do not add Morph transitions")
        a.add_argument("--storyboard",help="also render storyboard PNGs into this directory")
        a.add_argument("--preview",help="also render simulated motion GIFs for changed slides into this directory")
    a=sp.add_parser("storyboard")
    a.add_argument("deck")
    a.add_argument("-o","--output",required=True)
    a.add_argument("--slides",help="comma-separated slide numbers")
    a=sp.add_parser("preview",help="simulated motion GIF + key-state sheet for one slide")
    a.add_argument("deck")
    a.add_argument("--slide",type=int,required=True)
    a.add_argument("-o","--output",required=True,help="GIF path")
    a.add_argument("--sheet",help="key-state contact sheet PNG")
    a.add_argument("--fps",type=int,default=8)
    a=sp.add_parser("verify")
    a.add_argument("source")
    a.add_argument("output")
    args=ap.parse_args(argv)

    if args.cmd=="inspect":
        model=deck_model(args.deck)
        print(outline(model))
        if args.json:
            _dump({k:v for k,v in model.items() if k!="inventory"},args.json)
        return 0
    if args.cmd=="draft":
        model=deck_model(args.deck)
        plan=draft(model,args.goal,args.style,args.counters,morph=not args.no_morph)
        errors=validate_director(plan,model["inventory"])
        if errors:
            raise SystemExit("draft failed validation:\n"+"\n".join(errors))
        _dump(plan,args.output)
        for k,v in plan["research_metadata"]["draft_notes"].items():
            print(f"slide {k}: {v}")
        print(f"wrote {args.output}")
        return 0
    if args.cmd in ("apply","auto"):
        if args.cmd=="auto":
            model=deck_model(args.deck)
            plan=draft(model,args.goal,args.style,args.counters,morph=not args.no_morph)
            _dump(plan,str(Path(args.output).with_suffix(".director.json")))
        else:
            plan=_load(args.plan)
        if not plan["slides"] and not plan.get("transitions"):
            for k,v in (plan.get("research_metadata") or {}).get("draft_notes",{}).items():
                print(f"slide {k}: {v}")
            print("Nothing to add: every slide is static by design or keeps its existing choreography. No file written.")
            return 0
        report=apply(args.deck,plan,args.output,force=args.force)
        md=markdown_report(report,plan)
        rp=args.report or str(Path(args.output).with_suffix(".report.md"))
        Path(rp).write_text(md+"\n",encoding="utf-8")
        print(md)
        if args.storyboard:
            for sheet in storyboard(args.output,args.storyboard,
                                    [s["slide"] for s in report["slides"] if s["changed"]]):
                print("storyboard:",sheet)
        if args.preview:
            from motion_preview import render_slide_motion
            for s in report["slides"]:
                if s["changed"] and s.get("click_groups"):
                    out=Path(args.preview)/f"slide-{s['slide']:02d}.gif"
                    r=render_slide_motion(args.output,s["slide"],out,sheet=out.with_suffix(".png"))
                    print("preview:",r["gif"])
        return 0 if report["ok"] else 1
    if args.cmd=="storyboard":
        slides=[int(x) for x in args.slides.split(",")] if args.slides else None
        for sheet in storyboard(args.deck,args.output,slides):
            print(sheet)
        return 0
    if args.cmd=="preview":
        from motion_preview import render_slide_motion
        print(json.dumps(render_slide_motion(args.deck,args.slide,args.output,args.fps,sheet=args.sheet)))
        return 0
    if args.cmd=="verify":
        report=verify(args.source,args.output)
        print(markdown_report(report))
        return 0 if report["ok"] else 1
    return 2


if __name__=="__main__":
    raise SystemExit(main())
