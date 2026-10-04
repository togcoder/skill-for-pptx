#!/usr/bin/env python3
"""Read an existing PPTX into a stable deck-intake JSON for motion planning.

This is a read-only package analyzer. It does not infer narrative or edit the
deck. Its job is to give the AI planner a faithful inventory before any motion
or component synthesis is attempted.
"""
import argparse
import hashlib
import json
import posixpath
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
DGM="http://schemas.openxmlformats.org/drawingml/2006/diagram"
NS={"p":P,"a":A,"r":R}
REL_NS={"rel":REL}

TYPE_BY_TAG={
    f"{{{P}}}sp":"shape",
    f"{{{P}}}pic":"picture",
    f"{{{P}}}graphicFrame":"graphic-frame",
    f"{{{P}}}cxnSp":"connector",
    f"{{{P}}}grpSp":"group",
}


def _safe_xml(data,name):
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
        raise ValueError(f"{name}: DTD/entity declarations are not supported")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"{name}: invalid XML: {exc}") from exc


def _resolve_part(base_part,target):
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part),target))


def _relationships(package,part):
    rel_part=posixpath.join(
        posixpath.dirname(part),
        "_rels",
        posixpath.basename(part)+".rels",
    )
    if rel_part not in package.namelist():
        return []
    root=_safe_xml(package.read(rel_part),rel_part)
    out=[]
    for rel in root.findall(f"{{{REL}}}Relationship"):
        out.append({
            "id":rel.get("Id"),
            "type":rel.get("Type",""),
            "target":rel.get("Target",""),
            "target_mode":rel.get("TargetMode"),
            "resolved_target":None if rel.get("TargetMode")=="External" else _resolve_part(part,rel.get("Target","")),
        })
    return out


def _text(root):
    return "".join((node.text or "") for node in root.findall(".//a:t",NS)).strip()


def _cNvPr(node):
    props=node.find(".//p:cNvPr",NS)
    if props is None:
        return {"id":None,"name":None,"descr":None}
    return {
        "id":props.get("id"),
        "name":props.get("name"),
        "descr":props.get("descr"),
    }


def _xfrm(node):
    # Common locations for shapes/pictures/connectors and graphic frames.
    candidates=[
        node.find("p:spPr/a:xfrm",NS),
        node.find("p:spPr/a:xfrm",NS),
        node.find("p:xfrm",NS),
        node.find("p:grpSpPr/a:xfrm",NS),
    ]
    x=next((item for item in candidates if item is not None),None)
    if x is None:
        return None
    off=x.find("a:off",NS)
    ext=x.find("a:ext",NS)
    if off is None or ext is None:
        return None
    try:
        return {
            "x_emu":int(off.get("x")),
            "y_emu":int(off.get("y")),
            "cx_emu":int(ext.get("cx")),
            "cy_emu":int(ext.get("cy")),
            "rot":int(x.get("rot","0")),
        }
    except (TypeError,ValueError):
        return None


def _normalize_geometry(geom,width,height):
    if geom is None or not width or not height:
        return None
    return {
        "x":geom["x_emu"]/width,
        "y":geom["y_emu"]/height,
        "w":geom["cx_emu"]/width,
        "h":geom["cy_emu"]/height,
        "rotation_deg":geom["rot"]/60000,
    }


def _color_token(parent):
    if parent is None:
        return None
    srgb=parent.find(".//a:srgbClr",NS)
    if srgb is not None and srgb.get("val"):
        return "#"+srgb.get("val").upper()
    scheme=parent.find(".//a:schemeClr",NS)
    if scheme is not None and scheme.get("val"):
        return "scheme:"+scheme.get("val")
    return None


def _style_inventory(node):
    sppr=node.find("p:spPr",NS)
    fill=_color_token(sppr.find("a:solidFill",NS) if sppr is not None else None)
    line=None
    geometry=None
    if sppr is not None:
        ln=sppr.find("a:ln",NS)
        line=_color_token(ln.find("a:solidFill",NS) if ln is not None else None)
        geom=sppr.find("a:prstGeom",NS)
        geometry=geom.get("prst") if geom is not None else None

    run_props=node.find(".//a:rPr",NS)
    if run_props is None:
        run_props=node.find(".//a:defRPr",NS)
    font=None
    font_size_pt=None
    bold=None
    text_color=None
    if run_props is not None:
        latin=run_props.find("a:latin",NS)
        if latin is not None:
            font=latin.get("typeface")
        raw_size=run_props.get("sz")
        if raw_size:
            try:
                font_size_pt=int(raw_size)/100
            except ValueError:
                pass
        raw_bold=run_props.get("b")
        if raw_bold is not None:
            bold=raw_bold in ("1","true")
        text_color=_color_token(run_props.find("a:solidFill",NS))
    if font is None:
        latin=node.find(".//a:latin",NS)
        if latin is not None:
            font=latin.get("typeface")
    return {
        "fill":fill,
        "line":line,
        "geometry_preset":geometry,
        "font_family":font,
        "font_size_pt":font_size_pt,
        "bold":bold,
        "text_color":text_color,
    }


def _graphic_kind(node):
    data=node.find(".//a:graphicData",NS)
    if data is None:
        return "graphic"
    uri=data.get("uri","")
    if "chart" in uri:
        return "chart"
    if "table" in uri:
        return "table"
    if "diagram" in uri:
        return "diagram"
    return "graphic"



NUMBER_RE=re.compile(
    r"^\s*(?P<prefix>(?:[$€£¥₫]|USD|EUR|GBP|JPY|VND)?\s*)"
    r"(?P<number>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)"
    r"(?P<suffix>\s*(?:%|x|K|M|B|T|ms|s|h|d|pcs|ppm|dB|Hz|kHz|MHz|GHz|V|A|W|kW|MW|°C|℃|kg|g|mm|cm|m)?)\s*$",
    re.IGNORECASE,
)


def _standalone_number_candidate(text):
    """Return parsed KPI-like text when the whole text is essentially one number."""
    if not isinstance(text,str) or not text.strip():
        return None
    match=NUMBER_RE.match(text)
    if not match:
        return None
    raw_number=match.group("number")
    try:
        value=float(raw_number.replace(",",""))
    except ValueError:
        return None
    return {
        "raw":text.strip(),
        "numeric_value":value,
        "prefix":match.group("prefix").strip(),
        "suffix":match.group("suffix").strip(),
        "integer_like":value.is_integer() and "." not in raw_number,
        "counter_candidate":True,
    }


def _graphic_ref(node):
    chart=node.find(f".//{{{C}}}chart")
    if chart is None:
        return None
    return chart.get(f"{{{R}}}id")


CHART_TYPE_MAP={
    "barChart":"bar-or-column",
    "bar3DChart":"bar-or-column-3d",
    "lineChart":"line",
    "line3DChart":"line-3d",
    "pieChart":"pie",
    "pie3DChart":"pie-3d",
    "doughnutChart":"doughnut",
    "areaChart":"area",
    "area3DChart":"area-3d",
    "scatterChart":"scatter",
    "bubbleChart":"bubble",
    "radarChart":"radar",
    "stockChart":"stock",
    "surfaceChart":"surface",
    "surface3DChart":"surface-3d",
    "ofPieChart":"pie-of-pie",
}


def _cache_point_count(parent):
    if parent is None:
        return None
    counts=[]
    for cache_name in ("strCache","numCache","multiLvlStrCache"):
        for cache in parent.findall(f".//{{{C}}}{cache_name}"):
            points=cache.findall(f".//{{{C}}}pt")
            counts.append(len(points))
    return max(counts) if counts else None


def _chart_summary(package,chart_part):
    if not chart_part or chart_part not in package.namelist():
        return None
    root=_safe_xml(package.read(chart_part),chart_part)
    plot=root.find(f".//{{{C}}}plotArea")
    if plot is None:
        return {
            "part":chart_part,
            "chart_types":[],
            "primary_type":"unknown",
            "series_count":0,
            "category_count":None,
            "point_count":None,
        }

    chart_nodes=[]
    for child in list(plot):
        local=_local_name(child.tag)
        if local in CHART_TYPE_MAP:
            chart_nodes.append((local,child))

    types=[]
    series_count=0
    category_counts=[]
    point_counts=[]
    orientation=None
    grouping=None
    for local,node in chart_nodes:
        mapped=CHART_TYPE_MAP[local]
        if local=="barChart":
            bar_dir=node.find(f"{{{C}}}barDir")
            direction=bar_dir.get("val") if bar_dir is not None else None
            mapped="column" if direction=="col" else "bar" if direction=="bar" else mapped
            if direction:
                orientation=direction
            group=node.find(f"{{{C}}}grouping")
            if group is not None:
                grouping=group.get("val")
        if mapped not in types:
            types.append(mapped)
        series=node.findall(f"{{{C}}}ser")
        series_count+=len(series)
        for ser in series:
            cat=ser.find(f"{{{C}}}cat")
            val=ser.find(f"{{{C}}}val")
            count=_cache_point_count(cat)
            if count is not None:
                category_counts.append(count)
            count=_cache_point_count(val)
            if count is not None:
                point_counts.append(count)

    return {
        "part":chart_part,
        "chart_types":types,
        "primary_type":types[0] if len(types)==1 else ("combo" if len(types)>1 else "unknown"),
        "series_count":series_count,
        "category_count":max(category_counts) if category_counts else None,
        "point_count":max(point_counts) if point_counts else None,
        "bar_direction":orientation,
        "grouping":grouping,
    }


def _enrich_data_semantics(shapes,relationships,package):
    by_rid={rel["id"]:rel for rel in relationships}
    for shape in shapes:
        text=shape.get("text")
        shape["data_semantics"]={
            "standalone_number":_standalone_number_candidate(text),
        }
        if shape.get("kind")!="chart":
            continue
        rid=shape.get("chart_relationship_id")
        rel=by_rid.get(rid)
        target=rel.get("resolved_target") if rel else None
        shape["chart_summary"]=_chart_summary(package,target)
    return shapes


def _shape_inventory(root,width,height):
    tree=root.find("p:cSld/p:spTree",NS)
    if tree is None:
        return []
    out=[]
    z=0
    for node in list(tree):
        base=TYPE_BY_TAG.get(node.tag)
        if base is None:
            continue
        z+=1
        props=_cNvPr(node)
        kind=_graphic_kind(node) if base=="graphic-frame" else base
        geom=_xfrm(node)
        out.append({
            "z_index":z,
            "kind":kind,
            "id":props["id"],
            "name":props["name"],
            "descr":props["descr"],
            "text":_text(node) or None,
            "geometry":_normalize_geometry(geom,width,height),
            "geometry_emu":geom,
            "style":_style_inventory(node),
            "forced_semantic_name":props["name"] if (props["name"] or "").startswith("!!") else None,
            "chart_relationship_id":_graphic_ref(node) if kind=="chart" else None,
        })
    return out


def _notes_text(package,slide_part,relationships):
    rel=next((r for r in relationships if r["type"].endswith("/notesSlide") and r["resolved_target"]),None)
    if rel is None or rel["resolved_target"] not in package.namelist():
        return None
    root=_safe_xml(package.read(rel["resolved_target"]),rel["resolved_target"])
    chunks=[]
    for shape in root.findall("p:cSld/p:spTree/p:sp",NS):
        text=_text(shape)
        if not text:
            continue
        placeholder=shape.find("p:nvSpPr/p:nvPr/p:ph",NS)
        ptype=placeholder.get("type") if placeholder is not None else None
        # Exclude slide image / slide number placeholders but preserve body notes.
        if ptype in ("sldImg","sldNum","hdr","ftr","dt"):
            continue
        chunks.append(text)
    joined="\n".join(chunks).strip()
    return joined or None


def _relationship_summary(relationships):
    out=[]
    for rel in relationships:
        rtype=rel["type"].rsplit("/",1)[-1] if "/" in rel["type"] else rel["type"]
        out.append({
            "id":rel["id"],
            "kind":rtype,
            "target":rel["resolved_target"] or rel["target"],
            "external":rel["target_mode"]=="External",
        })
    return out



TIMING_EFFECT_TAGS={
    "anim","animClr","animEffect","animMotion","animRot","animScale",
    "set","audio","video","cmd",
}


def _local_name(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag


def _timing_conditions(ctn):
    if ctn is None:
        return []
    out=[]
    for cond in ctn.findall("p:stCondLst/p:cond",NS):
        item={"delay":cond.get("delay"),"event":cond.get("evt")}
        tn=cond.find("p:tn",NS)
        if tn is not None and tn.get("val") is not None:
            item["time_node_ref"]=tn.get("val")
        sp=cond.find("p:tgtEl/p:spTgt",NS)
        if sp is not None and sp.get("spid") is not None:
            item["shape_target"]=sp.get("spid")
        out.append(item)
    return out


def _timing_effect_properties(node,kind):
    if kind=="animMotion":
        return {
            "origin":node.get("origin"),
            "path":node.get("path"),
            "path_edit_mode":node.get("pathEditMode"),
        }
    if kind=="animScale":
        out={}
        for child_name in ("from","to","by"):
            child=node.find(f"p:{child_name}",NS)
            if child is not None:
                out[child_name]=dict(child.attrib)
        return out
    if kind=="animRot":
        return {key:node.get(key) for key in ("by","from","to") if node.get(key) is not None}
    if kind=="animEffect":
        return {key:node.get(key) for key in ("transition","filter","prLst") if node.get(key) is not None}
    if kind in ("anim","set"):
        attrs=[x.text for x in node.findall("p:cBhvr/p:attrNameLst/p:attrName",NS) if x.text]
        result={"attributes":attrs}
        if kind=="set":
            to=node.find("p:to",NS)
            if to is not None and len(list(to)):
                child=list(to)[0]
                result["to"]={"kind":_local_name(child.tag),**dict(child.attrib)}
        return result
    return dict(node.attrib)


def _numeric_delay(conditions):
    values=[]
    for cond in conditions:
        raw=cond.get("delay")
        if raw is None:
            continue
        try:
            values.append(int(raw))
        except (TypeError,ValueError):
            continue
    return min(values) if values else None



def _timing_click_groups(timing,by_id):
    """Recover presenter click groups conservatively from mainSeq direct children."""
    main=timing.find(".//p:cTn[@nodeType='mainSeq']",NS)
    if main is None:
        return []
    children=main.find("p:childTnLst",NS)
    if children is None:
        return []

    groups=[]
    for direct in list(children):
        if _local_name(direct.tag)!="par":
            continue
        group_effects=[]
        start_types=[]
        target_ids=[]
        for node in direct.iter():
            kind=_local_name(node.tag)
            if kind in TIMING_EFFECT_TAGS:
                target=node.find(".//p:spTgt",NS)
                spid=target.get("spid") if target is not None else None
                behavior_ctn=node.find("p:cBhvr/p:cTn",NS)
                if behavior_ctn is None:
                    behavior_ctn=node.find("p:cTn",NS)
                group_effects.append({
                    "type":kind,
                    "target_spid":spid,
                    "target":by_id.get(spid),
                    "duration":behavior_ctn.get("dur") if behavior_ctn is not None else None,
                })
                if spid is not None and spid not in target_ids:
                    target_ids.append(spid)
        for ctn in direct.findall(".//p:cTn",NS):
            node_type=ctn.get("nodeType")
            if node_type in ("clickEffect","withEffect","afterEffect") and node_type not in start_types:
                start_types.append(node_type)
        if group_effects or start_types:
            groups.append({
                "index":len(groups)+1,
                "effect_count":len(group_effects),
                "effect_types":[item["type"] for item in group_effects],
                "start_node_types":start_types,
                "target_spids":target_ids,
                "targets":[by_id.get(spid) for spid in target_ids],
            })
    return groups


def _timing_inventory(root,shapes):
    timing=root.find("p:timing",NS)
    if timing is None:
        return None

    by_id={
        str(shape["id"]):{
            "id":str(shape["id"]),
            "name":shape.get("name"),
            "text":shape.get("text"),
            "kind":shape.get("kind"),
        }
        for shape in shapes if shape.get("id") is not None
    }

    time_nodes=[]
    node_type_counts=Counter()
    for ctn in timing.findall(".//p:cTn",NS):
        item={
            "id":ctn.get("id"),
            "node_type":ctn.get("nodeType"),
            "duration":ctn.get("dur"),
            "fill":ctn.get("fill"),
            "group_id":ctn.get("grpId"),
            "preset_class":ctn.get("presetClass"),
            "preset_id":ctn.get("presetID"),
            "start_conditions":_timing_conditions(ctn),
        }
        if item["node_type"]:
            node_type_counts[item["node_type"]]+=1
        time_nodes.append(item)

    effects=[]
    for node in timing.iter():
        kind=_local_name(node.tag)
        if kind not in TIMING_EFFECT_TAGS:
            continue
        behavior_ctn=node.find("p:cBhvr/p:cTn",NS)
        if behavior_ctn is None:
            behavior_ctn=node.find("p:cTn",NS)
        target=node.find(".//p:spTgt",NS)
        spid=target.get("spid") if target is not None else None
        conditions=_timing_conditions(behavior_ctn)
        properties=_timing_effect_properties(node,kind)
        chart_target=node.find(".//a:chart",NS)
        if chart_target is not None:
            properties=dict(properties or {})
            properties["chart_target"]={
                "series_index":chart_target.get("seriesIdx"),
                "category_index":chart_target.get("categoryIdx"),
                "build_step":chart_target.get("bldStep"),
            }
        effects.append({
            "sequence_index":len(effects)+1,
            "type":kind,
            "target_spid":spid,
            "target":by_id.get(spid),
            "duration":behavior_ctn.get("dur") if behavior_ctn is not None else None,
            "node_type":behavior_ctn.get("nodeType") if behavior_ctn is not None else None,
            "start_conditions":conditions,
            "numeric_delay_ms":_numeric_delay(conditions),
            "properties":properties,
        })

    build_entries=[]
    for item in timing.findall("p:bldLst/*",NS):
        spid=item.get("spid")
        build_value=item.get("build")
        anim_bg=item.get("animBg")
        if _local_name(item.tag)=="bldGraphic":
            chart_build=item.find("p:bldSub/a:bldChart",NS)
            if chart_build is not None:
                build_value=chart_build.get("bld")
                anim_bg=chart_build.get("animBg")
            elif item.find("p:bldAsOne",NS) is not None:
                build_value="asWhole"
        build_entries.append({
            "type":_local_name(item.tag),
            "spid":spid,
            "target":by_id.get(spid),
            "group_id":item.get("grpId"),
            "build":build_value,
            "anim_bg":anim_bg,
        })

    all_numeric=bool(effects) and all(effect["numeric_delay_ms"] is not None for effect in effects)
    if all_numeric:
        order=sorted(
            ({"effect_index":effect["sequence_index"],"delay_ms":effect["numeric_delay_ms"]} for effect in effects),
            key=lambda item:(item["delay_ms"],item["effect_index"]),
        )
        order_basis="numeric-behavior-delay"
    else:
        order=[{"effect_index":effect["sequence_index"],"delay_ms":effect["numeric_delay_ms"]} for effect in effects]
        order_basis="document-order-partial"

    click_groups=_timing_click_groups(timing,by_id)

    return {
        "effect_count":len(effects),
        "click_group_count":len(click_groups),
        "click_groups":click_groups,
        "time_node_count":len(time_nodes),
        "node_type_counts":[{"value":key,"count":count} for key,count in node_type_counts.most_common()],
        "effects":effects,
        "order_hint":order,
        "order_basis":order_basis,
        "build_entries":build_entries,
        "note":"Timing inventory is structural evidence. Event/master relationships can make runtime order more complex than this summary.",
    }


def _transition_inventory(root):
    nodes=root.findall(".//p:transition",NS)
    if not nodes:
        return None
    out=[]
    for transition in nodes:
        descendants=[]
        for child in transition.iter():
            if child is transition:
                continue
            name=_local_name(child.tag)
            if name not in descendants:
                descendants.append(name)
        out.append({"attributes":dict(transition.attrib),"descendants":descendants})
    return {"count":len(nodes),"variants":out}


def inspect_existing_deck(path):
    path=Path(path)
    report={
        "version":"0.1",
        "kind":"existing-deck-inventory",
        "source_file":path.name,
        "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "errors":[],
        "slide_size_emu":None,
        "slides":[],
        "package":{},
    }
    try:
        with ZipFile(path) as package:
            infos=package.infolist()
            names=package.namelist()
            dup=[name for name,count in Counter(names).items() if count>1]
            if dup:
                raise ValueError("Duplicate ZIP entries")
            bad=package.testzip()
            if bad:
                report["errors"].append(f"ZIP CRC error: {bad}")

            for required in ("ppt/presentation.xml","ppt/_rels/presentation.xml.rels"):
                if required not in names:
                    raise ValueError(f"Missing required part: {required}")

            presentation=_safe_xml(package.read("ppt/presentation.xml"),"ppt/presentation.xml")
            size=presentation.find(f"{{{P}}}sldSz")
            if size is not None:
                try:
                    width,height=int(size.get("cx")),int(size.get("cy"))
                    report["slide_size_emu"]={"width":width,"height":height}
                except (TypeError,ValueError):
                    width=height=None
            else:
                width=height=None

            rel_root=_safe_xml(package.read("ppt/_rels/presentation.xml.rels"),"ppt/_rels/presentation.xml.rels")
            rels={r.get("Id"):r for r in rel_root.findall(f"{{{REL}}}Relationship")}
            slide_nodes=presentation.findall(f"{{{P}}}sldIdLst/{{{P}}}sldId")
            for index,node in enumerate(slide_nodes,1):
                rid=node.get(f"{{{R}}}id")
                rel=rels.get(rid)
                if rel is None or not rel.get("Type","").endswith("/slide"):
                    report["errors"].append(f"slide {index}: invalid slide relationship {rid}")
                    continue
                part=_resolve_part("ppt/presentation.xml",rel.get("Target",""))
                if part not in names:
                    report["errors"].append(f"slide {index}: missing slide part {part}")
                    continue
                root=_safe_xml(package.read(part),part)
                relationships=_relationships(package,part)
                shapes=_shape_inventory(root,width,height)
                _enrich_data_semantics(shapes,relationships,package)
                title=next((s["text"] for s in shapes if s["text"]),None)
                report["slides"].append({
                    "index":index,
                    "part":part,
                    "title_candidate":title,
                    "text":"\n".join(s["text"] for s in shapes if s["text"]) or None,
                    "speaker_notes":_notes_text(package,part,relationships),
                    "shape_count":len(shapes),
                    "shapes":shapes,
                    "relationships":_relationship_summary(relationships),
                    "has_transition":root.find(f".//{{{P}}}transition") is not None,
                    "has_timing":root.find(f".//{{{P}}}timing") is not None,
                    "transition_summary":_transition_inventory(root),
                    "timing_summary":_timing_inventory(root,shapes),
                    "layout_part":next((r["resolved_target"] for r in relationships if r["type"].endswith("/slideLayout")),None),
                })

            all_shapes=[shape for slide in report["slides"] for shape in slide["shapes"]]
            def ranked(field):
                counter=Counter(
                    shape["style"].get(field) for shape in all_shapes
                    if shape.get("style") and shape["style"].get(field) is not None
                )
                return [{"value":value,"count":count} for value,count in counter.most_common()]
            report["design_profile"]={
                "font_families":ranked("font_family"),
                "fill_colors":ranked("fill"),
                "line_colors":ranked("line"),
                "text_colors":ranked("text_color"),
                "geometry_presets":ranked("geometry_preset"),
            }
            report["package"]={
                "file_count":len(infos),
                "has_theme":any(n.startswith("ppt/theme/") and n.endswith(".xml") for n in names),
                "has_media":any(n.startswith("ppt/media/") for n in names),
                "has_notes":any(n.startswith("ppt/notesSlides/") and n.endswith(".xml") for n in names),
                "has_charts":any(n.startswith("ppt/charts/") and n.endswith(".xml") for n in names),
                "has_embedded_objects":any(n.startswith("ppt/embeddings/") for n in names),
            }
    except (OSError,BadZipFile,ValueError) as exc:
        report["errors"].append(str(exc))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=inspect_existing_deck(args.pptx)
    data=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(data+"\n",encoding="utf-8")
    else:
        print(data)
    return 1 if report["errors"] else 0


if __name__=="__main__":
    raise SystemExit(main())
