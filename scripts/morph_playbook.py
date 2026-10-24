# -*- coding: utf-8 -*-
"""
EXPERIMENTAL — quarantined by T034 (experiments/T033-20261016-argon-research/REPORT.md).
Not used by any product path. The canonical cross-slide Morph is
scripts/morph_studio.py (continuity, rename_chain, _stage_copy, scenes,
verify_scenes); the canonical object model is motion_director.deck_model.
Audit findings: the standard-library parser breaks on lxml input, placeholder
shapes are skipped, renaming only the source slide breaks existing Morph
pairs, post-stage clones cascade, picture relationships are not remapped, a
second solidFill and a misplaced alphaModFix make XML schema-invalid, and no
Morph transition is written. Ideas worth porting after a PowerPoint render:
portal-seed / telescopic-stack / corner-badge staging modes.

PPTX Motion Lab — Cross-Slide Morph Playbook (Milestone T033)
Module: scripts/morph_playbook.py

Provides OOXML shape extraction with recursive group affine transformation,
cross-slide Morph (!!) twin staging, arc-length homotopy path resampling,
custom geometry injection, and cognitive motion budget auditing.
"""

from __future__ import annotations

import copy
import math
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

# Standard 16:9 Widescreen Slide Dimensions in EMU (13.333 in x 7.5 in)
SLIDE_W: int = 12192000
SLIDE_H: int = 6858000

# ECMA-376 & PowerPoint 2016+ Morph Namespaces
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P159_NS = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"

NS: Dict[str, str] = {
    "p": P_NS,
    "a": A_NS,
    "r": R_NS,
    "p159": P159_NS,
}

for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)

MORPH_PREFIX = "!!"
STAGE_NAMING_PREFIX = "!!__stage_"

VALID_STAGE_MODES = frozenset({
    "off-left",
    "off-right",
    "off-top",
    "off-bottom",
    "portal-seed",
    "telescopic-stack",
    "corner-badge",
})

COLOR_TAGS = frozenset({
    f"{{{A_NS}}}srgbClr",
    f"{{{A_NS}}}schemeClr",
    f"{{{A_NS}}}prstClr",
    f"{{{A_NS}}}sysClr",
    f"{{{A_NS}}}hslClr",
    f"{{{A_NS}}}scrgbClr",
})


def _qname(ns: str, local: str) -> str:
    """Return Clark-notation qualified XML tag name."""
    return f"{{{ns}}}{local}"


def _local_name(tag: str) -> str:
    """Strip namespace URI from Clark-notation tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _append_subelement(
    parent: ET.Element,
    tag: str,
    attrib: Optional[Dict[str, str]] = None,
) -> ET.Element:
    """Create and append a child element compatibly across stdlib ET and lxml."""
    attrib_clean = {k: str(v) for k, v in (attrib or {}).items()}
    if hasattr(parent, "makeelement"):
        child = parent.makeelement(tag, attrib_clean)
        parent.append(child)
        return child
    return ET.SubElement(parent, tag, attrib_clean)


def _insert_subelement(
    parent: ET.Element,
    index: int,
    tag: str,
    attrib: Optional[Dict[str, str]] = None,
) -> ET.Element:
    """Create and insert a child element at a specific position."""
    attrib_clean = {k: str(v) for k, v in (attrib or {}).items()}
    if hasattr(parent, "makeelement"):
        child = parent.makeelement(tag, attrib_clean)
    else:
        child = ET.Element(tag, attrib_clean)
    parent.insert(index, child)
    return child


def _get_sp_tree(slide_root: ET.Element) -> ET.Element:
    """Locate p:spTree from a p:sld root or return slide_root if already p:spTree."""
    if _local_name(slide_root.tag) == "spTree":
        return slide_root
    sp_tree = slide_root.find(".//p:cSld/p:spTree", NS)
    if sp_tree is None:
        sp_tree = slide_root.find(".//p:spTree", NS)
    return sp_tree if sp_tree is not None else slide_root


def _get_cnvpr(shape_node: ET.Element) -> Optional[ET.Element]:
    """Locate the direct cNvPr node for p:sp, p:pic, p:grpSp, or p:cxnSp."""
    local = _local_name(shape_node.tag)
    nv_map = {
        "sp": "p:nvSpPr/p:cNvPr",
        "pic": "p:nvPicPr/p:cNvPr",
        "grpSp": "p:nvGrpSpPr/p:cNvPr",
        "cxnSp": "p:nvCxnSpPr/p:cNvPr",
        "graphicFrame": "p:nvGraphicFramePr/p:cNvPr",
    }
    xpath = nv_map.get(local)
    if xpath:
        found = shape_node.find(xpath, NS)
        if found is not None:
            return found
    for child in shape_node:
        if _local_name(child.tag).startswith("nv"):
            cnv = child.find("p:cNvPr", NS)
            if cnv is not None:
                return cnv
    return None


def _get_sppr(shape_node: ET.Element) -> Optional[ET.Element]:
    """Locate the direct p:spPr (or p:grpSpPr for groups)."""
    local = _local_name(shape_node.tag)
    if local == "grpSp":
        return shape_node.find("p:grpSpPr", NS)
    return shape_node.find("p:spPr", NS)


def _read_xfrm_emu(
    xfrm: Optional[ET.Element],
) -> Optional[Tuple[float, float, float, float]]:
    """Read (x, y, cx, cy) in EMU from an a:xfrm element."""
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    try:
        x = float(off.attrib.get("x", "0"))
        y = float(off.attrib.get("y", "0"))
        cx = float(ext.attrib.get("cx", "0"))
        cy = float(ext.attrib.get("cy", "0"))
        return (x, y, cx, cy)
    except (ValueError, TypeError):
        return None


def _read_group_mapping(
    grp_node: ET.Element,
    parent_transform: Tuple[float, float, float, float, float, float],
) -> Tuple[float, float, float, float, float, float]:
    """
    Compute cumulative affine parameters (off_x, off_y, scale_x, scale_y, ch_x, ch_y)
    mapping child group coordinates into root slide EMU coordinates.
    """
    p_off_x, p_off_y, p_scale_x, p_scale_y, p_ch_x, p_ch_y = parent_transform
    grp_sp_pr = grp_node.find("p:grpSpPr", NS)
    if grp_sp_pr is None:
        return parent_transform
    xfrm = grp_sp_pr.find("a:xfrm", NS)
    if xfrm is None:
        return parent_transform

    base = _read_xfrm_emu(xfrm)
    ch_off = xfrm.find("a:chOff", NS)
    ch_ext = xfrm.find("a:chExt", NS)
    if base is None or ch_off is None or ch_ext is None:
        return parent_transform

    gx, gy, gcx, gcy = base
    try:
        chx = float(ch_off.attrib.get("x", "0"))
        chy = float(ch_off.attrib.get("y", "0"))
        chcx = float(ch_ext.attrib.get("cx", "0"))
        chcy = float(ch_ext.attrib.get("cy", "0"))
    except (ValueError, TypeError):
        return parent_transform

    if chcx <= 0 or chcy <= 0:
        return parent_transform

    # Map group's own origin through parent transform first
    canvas_gx = p_off_x + (gx - p_ch_x) * p_scale_x
    canvas_gy = p_off_y + (gy - p_ch_y) * p_scale_y
    scale_x = p_scale_x * (gcx / chcx)
    scale_y = p_scale_y * (gcy / chcy)

    return (canvas_gx, canvas_gy, scale_x, scale_y, chx, chy)


def extract_objects(
    slide_root: ET.Element,
    slide_w: float = SLIDE_W,
    slide_h: float = SLIDE_H,
    flatten_groups: bool = True,
    include_groups: bool = False,
) -> List[Dict[str, Any]]:
    """
    Traverse p:spTree and extract all visual objects (p:sp, p:pic, p:cxnSp, and p:grpSp).

    Coordinates in p:spPr/a:xfrm/a:off (@x, @y) and a:ext (@cx, @cy) are transformed
    from local group space (if inside p:grpSp) into global slide EMU space and
    normalized to [0..1] floats relative to (slide_w, slide_h).

    Returns:
        List of dicts:
        [
            {
                "node": shape_node,
                "name": shape_name,
                "id": shape_id (int),
                "geometry": {"x": norm_x, "y": norm_y, "w": norm_w, "h": norm_h}
            },
            ...
        ]
    """
    if slide_w <= 0 or slide_h <= 0:
        raise ValueError(f"slide_w ({slide_w}) and slide_h ({slide_h}) must be > 0.")

    sp_tree = _get_sp_tree(slide_root)
    results: List[Dict[str, Any]] = []

    # Identity affine transform: (off_x, off_y, scale_x, scale_y, ch_x, ch_y)
    identity_tf = (0.0, 0.0, 1.0, 1.0, 0.0, 0.0)

    def _walk(
        container: ET.Element,
        tf: Tuple[float, float, float, float, float, float],
    ) -> None:
        off_x, off_y, scale_x, scale_y, ch_x, ch_y = tf

        for child in list(container):
            local = _local_name(child.tag)

            if local == "grpSp":
                grp_tf = _read_group_mapping(child, tf)
                if include_groups or not flatten_groups:
                    cnv = _get_cnvpr(child)
                    sp_pr = _get_sppr(child)
                    xfrm = sp_pr.find("a:xfrm", NS) if sp_pr is not None else None
                    raw_box = _read_xfrm_emu(xfrm)
                    if cnv is not None and raw_box is not None:
                        rx, ry, rcx, rcy = raw_box
                        gx = off_x + (rx - ch_x) * scale_x
                        gy = off_y + (ry - ch_y) * scale_y
                        gw = rcx * scale_x
                        gh = rcy * scale_y
                        try:
                            sid = int(cnv.attrib.get("id", "0"))
                        except ValueError:
                            sid = 0
                        results.append({
                            "node": child,
                            "name": cnv.attrib.get("name", ""),
                            "id": sid,
                            "geometry": {
                                "x": gx / float(slide_w),
                                "y": gy / float(slide_h),
                                "w": gw / float(slide_w),
                                "h": gh / float(slide_h),
                            },
                        })
                if flatten_groups:
                    _walk(child, grp_tf)
                continue

            if local not in ("sp", "pic", "cxnSp"):
                continue

            cnv = _get_cnvpr(child)
            sp_pr = _get_sppr(child)
            if cnv is None or sp_pr is None:
                continue

            xfrm = sp_pr.find("a:xfrm", NS)
            raw_box = _read_xfrm_emu(xfrm)
            if raw_box is None:
                continue

            rx, ry, rcx, rcy = raw_box
            canvas_x = off_x + (rx - ch_x) * scale_x
            canvas_y = off_y + (ry - ch_y) * scale_y
            canvas_w = rcx * scale_x
            canvas_h = rcy * scale_y

            try:
                shape_id = int(cnv.attrib.get("id", "0"))
            except ValueError:
                shape_id = 0

            shape_name = cnv.attrib.get("name", "")

            results.append({
                "node": child,
                "name": shape_name,
                "id": shape_id,
                "geometry": {
                    "x": canvas_x / float(slide_w),
                    "y": canvas_y / float(slide_h),
                    "w": canvas_w / float(slide_w),
                    "h": canvas_h / float(slide_h),
                },
            })

    _walk(sp_tree, identity_tf)
    return results


def _get_max_shape_id(slide_root: ET.Element) -> int:
    """Find the maximum integer @id across all p:cNvPr elements on a slide."""
    max_id = 1
    for cnv in slide_root.findall(".//p:cNvPr", NS):
        raw_id = cnv.attrib.get("id")
        if raw_id is not None:
            try:
                val = int(raw_id)
                if val > max_id:
                    max_id = val
            except ValueError:
                pass
    return max_id


def _ensure_morph_twin_name(name: str) -> str:
    """Ensure shape name carries the PowerPoint 16.0 '!!' Morph prefix."""
    if name.startswith(MORPH_PREFIX):
        return name
    clean = name.strip() or "unnamed"
    return f"{STAGE_NAMING_PREFIX}{clean}"


def _set_shape_name_and_id(
    shape_node: ET.Element,
    new_name: Optional[str] = None,
    new_id: Optional[int] = None,
) -> None:
    """Update @name and/or @id on a shape's cNvPr element."""
    cnv = _get_cnvpr(shape_node)
    if cnv is None:
        return
    if new_name is not None:
        cnv.set("name", new_name)
    if new_id is not None:
        cnv.set("id", str(new_id))


def _set_shape_geometry_norm(
    shape_node: ET.Element,
    geom: Dict[str, float],
    slide_w: float = SLIDE_W,
    slide_h: float = SLIDE_H,
) -> None:
    """Write normalized [0..1] geometry back into p:spPr/a:xfrm in EMU integers."""
    sp_pr = _get_sppr(shape_node)
    if sp_pr is None:
        sp_pr = _append_subelement(shape_node, _qname(P_NS, "spPr"))

    xfrm = sp_pr.find("a:xfrm", NS)
    if xfrm is None:
        xfrm = _insert_subelement(sp_pr, 0, _qname(A_NS, "xfrm"))

    off = xfrm.find("a:off", NS)
    if off is None:
        off = _insert_subelement(xfrm, 0, _qname(A_NS, "off"))

    ext = xfrm.find("a:ext", NS)
    if ext is None:
        ext = _append_subelement(xfrm, _qname(A_NS, "ext"))

    emu_x = int(round(geom["x"] * slide_w))
    emu_y = int(round(geom["y"] * slide_h))
    emu_w = max(1, int(round(geom["w"] * slide_w)))
    emu_h = max(1, int(round(geom["h"] * slide_h)))

    off.set("x", str(emu_x))
    off.set("y", str(emu_y))
    ext.set("cx", str(emu_w))
    ext.set("cy", str(emu_h))


def _apply_shape_opacity(shape_node: ET.Element, alpha_ratio: float) -> None:
    """
    Inject DrawingML opacity (a:alpha) into color nodes and a:alphaModFix for pictures.
    alpha_ratio is clamped to [0.0, 1.0] and converted to 1/1000th percent [0..100000].
    """
    clamped = max(0.0, min(1.0, float(alpha_ratio)))
    val_str = str(int(round(clamped * 100000)))

    # 1. Inject a:alpha into any color definitions under fills, lines, or text
    color_found = False
    for elem in shape_node.iter():
        if elem.tag in COLOR_TAGS:
            color_found = True
            alpha_el = elem.find("a:alpha", NS)
            if alpha_el is None:
                alpha_el = _append_subelement(elem, _qname(A_NS, "alpha"))
            alpha_el.set("val", val_str)

    # 2. For p:pic elements, also inject a:alphaModFix into p:blipFill/a:blip
    if _local_name(shape_node.tag) == "pic":
        blip = shape_node.find(".//p:blipFill/a:blip", NS)
        if blip is not None:
            mod_fix = blip.find("a:alphaModFix", NS)
            if mod_fix is None:
                mod_fix = _append_subelement(blip, _qname(A_NS, "alphaModFix"))
            mod_fix.set("amt", val_str)
            color_found = True

    # 3. If shape had no explicit fill/color nodes, create a default solidFill with a:alpha
    if not color_found:
        sp_pr = _get_sppr(shape_node)
        if sp_pr is not None:
            solid = sp_pr.find("a:solidFill", NS)
            if solid is None:
                solid = _append_subelement(sp_pr, _qname(A_NS, "solidFill"))
            srgb = solid.find("a:srgbClr", NS)
            if srgb is None:
                srgb = _append_subelement(
                    solid, _qname(A_NS, "srgbClr"), {"val": "FFFFFF"}
                )
            alpha_el = srgb.find("a:alpha", NS)
            if alpha_el is None:
                alpha_el = _append_subelement(srgb, _qname(A_NS, "alpha"))
            alpha_el.set("val", val_str)


def _compute_staged_geometry(
    orig: Dict[str, float],
    mode: str,
    stack_index: int = 0,
    margin: float = 0.06,
) -> Tuple[Dict[str, float], float]:
    """
    Calculate normalized staged geometry {"x", "y", "w", "h"} and default alpha
    for a given staging mode.
    """
    if mode not in VALID_STAGE_MODES:
        raise ValueError(
            f"Unsupported staging mode '{mode}'. Must be one of {sorted(VALID_STAGE_MODES)}."
        )

    x, y, w, h = orig["x"], orig["y"], orig["w"], orig["h"]
    cx = x + w * 0.5
    cy = y + h * 0.5

    if mode == "off-left":
        return {"x": -w - margin, "y": y, "w": w, "h": h}, 0.0

    if mode == "off-right":
        return {"x": 1.0 + margin, "y": y, "w": w, "h": h}, 0.0

    if mode == "off-top":
        return {"x": x, "y": -h - margin, "w": w, "h": h}, 0.0

    if mode == "off-bottom":
        return {"x": x, "y": 1.0 + margin, "w": w, "h": h}, 0.0

    if mode == "portal-seed":
        seed_scale = 0.02
        sw = max(0.004, w * seed_scale)
        sh = max(0.004, h * seed_scale)
        return {
            "x": cx - sw * 0.5,
            "y": cy - sh * 0.5,
            "w": sw,
            "h": sh,
        }, 0.0

    if mode == "telescopic-stack":
        # Progressive depth scaling + cascade offset
        depth_factor = max(0.35, 0.72 - 0.06 * stack_index)
        sw = w * depth_factor
        sh = h * depth_factor
        offset_step = 0.018 * (stack_index + 1)
        return {
            "x": cx - sw * 0.5 + offset_step,
            "y": cy - sh * 0.5 + offset_step,
            "w": sw,
            "h": sh,
        }, 0.0

    # mode == "corner-badge"
    badge_scale = 0.22
    bw = min(0.10, max(0.025, w * badge_scale))
    bh = min(0.10, max(0.025, h * badge_scale))
    bx = 1.0 - bw - 0.03
    by = 0.04 + stack_index * (bh + 0.015)
    return {"x": bx, "y": by, "w": bw, "h": bh}, 0.0


def _normalize_plan(plan: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize flexible plan formats into a canonical list of staging rules.
    Supports:
      1. List of directive dicts:
         [{"name": "Box", "pre_stage": "off-left", "post_stage": "off-right", ...}]
      2. Dict keyed by shape name:
         {"Box": {"pre_stage": "off-left", "post_stage": "off-right"}}
         or {"Box": "off-left"}
      3. Wrapper dict containing "directives", "twins", "rules", or "items".
    """
    if isinstance(plan, list):
        return list(plan)

    if isinstance(plan, dict):
        for list_key in ("directives", "twins", "rules", "items", "objects"):
            if list_key in plan and isinstance(plan[list_key], list):
                return list(plan[list_key])

        # Check if plan itself is a single rule dict
        if any(k in plan for k in ("name", "shape_name", "target", "pre_stage", "post_stage")):
            return [plan]

        # Otherwise treat keys as shape names
        normalized: List[Dict[str, Any]] = []
        for shape_name, cfg in plan.items():
            if isinstance(cfg, str):
                normalized.append({
                    "name": shape_name,
                    "pre_stage": cfg,
                    "post_stage": cfg,
                })
            elif isinstance(cfg, dict):
                entry = dict(cfg)
                entry.setdefault("name", shape_name)
                normalized.append(entry)
        return normalized

    raise TypeError(f"Unsupported plan type: {type(plan).__name__}")


def stage_cross_slide_morph_twins(
    slide_roots: Sequence[ET.Element],
    plan: Union[List[Dict[str, Any]], Dict[str, Any]],
    slide_w: float = SLIDE_W,
    slide_h: float = SLIDE_H,
) -> List[Dict[str, Any]]:
    """
    Stage cross-slide Morph twins across adjacent slides in `slide_roots`.

    For each directive in `plan`:
      - Ensures the matched shape has the Microsoft PowerPoint 16.0 Morph prefix `!!`
        (renaming `<orig_name>` to `!!__stage_<orig_name>` on both slides if needed).
      - `pre_stage`: If a shape appears on slide `i` (and is absent on slide `i - 1`),
        clones the shape via `copy.deepcopy` onto slide `i - 1` with `max_id + 1`,
        applies the pre-stage geometry (`off-left`, `portal-seed`, etc.) and `a:alpha`.
      - `post_stage`: If a shape appears on slide `i` (and is absent on slide `i + 1`),
        clones the shape via `copy.deepcopy` onto slide `i + 1` with `max_id + 1`,
        applies the post-stage geometry (`off-right`, `corner-badge`, etc.) and `a:alpha`.

    Returns:
        List of staged twin metadata records for auditing/verification.
    """
    if len(slide_roots) < 2:
        return []

    directives = _normalize_plan(plan)
    staged_records: List[Dict[str, Any]] = []

    # Index objects per slide
    slide_Maps: List[Dict[str, Dict[str, Any]]] = []
    for root in slide_roots:
        objs = extract_objects(root, slide_w=slide_w, slide_h=slide_h)
        by_name: Dict[str, Dict[str, Any]] = {}
        for obj in objs:
            by_name[obj["name"]] = obj
        slide_Maps.append(by_name)

    stack_counters: Dict[Tuple[int, str], int] = {}

    def _clone_and_stage(
        src_obj: Dict[str, Any],
        src_slide_idx: int,
        dst_slide_idx: int,
        mode: str,
        stage_kind: str,
        alpha_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        dst_root = slide_roots[dst_slide_idx]
        dst_sp_tree = _get_sp_tree(dst_root)

        orig_name = src_obj["name"]
        twin_name = _ensure_morph_twin_name(orig_name)

        # Rename original shape on source slide so both slides share identical !! name
        _set_shape_name_and_id(src_obj["node"], new_name=twin_name)
        slide_Maps[src_slide_idx][twin_name] = src_obj
        src_obj["name"] = twin_name

        # Deepcopy node and assign non-colliding ID on destination slide
        cloned_node = copy.deepcopy(src_obj["node"])
        new_id = _get_max_shape_id(dst_root) + 1
        _set_shape_name_and_id(cloned_node, new_name=twin_name, new_id=new_id)

        # Compute staged geometry and opacity
        counter_key = (dst_slide_idx, mode)
        stack_idx = stack_counters.get(counter_key, 0)
        stack_counters[counter_key] = stack_idx + 1

        staged_geom, default_alpha = _compute_staged_geometry(
            src_obj["geometry"], mode=mode, stack_index=stack_idx
        )
        final_alpha = default_alpha if alpha_override is None else float(alpha_override)

        _set_shape_geometry_norm(
            cloned_node, staged_geom, slide_w=slide_w, slide_h=slide_h
        )
        _apply_shape_opacity(cloned_node, final_alpha)

        dst_sp_tree.append(cloned_node)

        record = {
            "name": twin_name,
            "original_name": orig_name,
            "id": new_id,
            "source_slide": src_slide_idx,
            "staged_slide": dst_slide_idx,
            "stage_kind": stage_kind,
            "mode": mode,
            "alpha": final_alpha,
            "geometry": staged_geom,
            "node": cloned_node,
        }
        slide_Maps[dst_slide_idx][twin_name] = {
            "node": cloned_node,
            "name": twin_name,
            "id": new_id,
            "geometry": staged_geom,
        }
        staged_records.append(record)
        return record

    for rule in directives:
        target_name = (
            rule.get("name")
            or rule.get("shape_name")
            or rule.get("target")
            or ""
        )
        if not target_name:
            continue

        twin_candidate = _ensure_morph_twin_name(target_name)
        pre_mode = rule.get("pre_stage")
        post_mode = rule.get("post_stage")

        # Support shorthand rule with {"mode": "...", "direction": "pre"|"post"}
        if not pre_mode and not post_mode and "mode" in rule:
            direction = rule.get("direction", "pre")
            if direction == "post":
                post_mode = rule["mode"]
            else:
                pre_mode = rule["mode"]

        alpha_override = rule.get("alpha")
        explicit_slide = rule.get("slide_index", rule.get("slide_idx", rule.get("source_slide")))
        explicit_target_slide = rule.get("target_slide")

        if explicit_slide is not None:
            candidate_indices = [int(explicit_slide)]
        else:
            candidate_indices = list(range(len(slide_roots)))

        for idx in candidate_indices:
            if idx < 0 or idx >= len(slide_roots):
                continue

            s_map = slide_Maps[idx]
            src_obj = s_map.get(target_name) or s_map.get(twin_candidate)
            if src_obj is None:
                continue

            # 1. Handle PRE-STAGE (clone onto preceding slide idx - 1, or explicit_target_slide)
            if pre_mode:
                pre_dst = (
                    int(explicit_target_slide)
                    if (explicit_target_slide is not None and not post_mode)
                    else idx - 1
                )
                if 0 <= pre_dst < len(slide_roots) and pre_dst != idx:
                    dst_map = slide_Maps[pre_dst]
                    if target_name not in dst_map and twin_candidate not in dst_map:
                        _clone_and_stage(
                            src_obj=src_obj,
                            src_slide_idx=idx,
                            dst_slide_idx=pre_dst,
                            mode=pre_mode,
                            stage_kind="pre_stage",
                            alpha_override=alpha_override,
                        )

            # 2. Handle POST-STAGE (clone onto following slide idx + 1, or explicit_target_slide)
            if post_mode:
                post_dst = (
                    int(explicit_target_slide)
                    if explicit_target_slide is not None
                    else idx + 1
                )
                if 0 <= post_dst < len(slide_roots) and post_dst != idx:
                    dst_map = slide_Maps[post_dst]
                    if target_name not in dst_map and twin_candidate not in dst_map:
                        _clone_and_stage(
                            src_obj=src_obj,
                            src_slide_idx=idx,
                            dst_slide_idx=post_dst,
                            mode=post_mode,
                            stage_kind="post_stage",
                            alpha_override=alpha_override,
                        )

    return staged_records


def _resample_single_polyline(
    points: Sequence[Tuple[float, float]],
    num_points: int,
    closed: bool = True,
) -> List[Tuple[float, float]]:
    """Resample a 2D polyline/polygon to `num_points` uniform arc-length vertices."""
    pts = [(float(p[0]), float(p[1])) for p in points]
    if not pts:
        raise ValueError("points cannot be empty.")
    if num_points < 2:
        raise ValueError("num_points must be >= 2.")
    if len(pts) == 1:
        return [pts[0]] * num_points

    work_pts = list(pts)
    if closed and work_pts[0] != work_pts[-1]:
        work_pts.append(work_pts[0])

    # Compute cumulative arc lengths
    cum_len: List[float] = [0.0]
    for i in range(1, len(work_pts)):
        dx = work_pts[i][0] - work_pts[i - 1][0]
        dy = work_pts[i][1] - work_pts[i - 1][1]
        cum_len.append(cum_len[-1] + math.hypot(dx, dy))

    total_len = cum_len[-1]
    if total_len <= 1e-12:
        return [pts[0]] * num_points

    step = total_len / float(num_points if closed else (num_points - 1))
    resampled: List[Tuple[float, float]] = []

    seg_idx = 0
    for k in range(num_points):
        target_d = min(k * step, total_len)
        while seg_idx < len(cum_len) - 2 and cum_len[seg_idx + 1] < target_d:
            seg_idx += 1

        d0 = cum_len[seg_idx]
        d1 = cum_len[seg_idx + 1]
        seg_len = d1 - d0
        t = 0.0 if seg_len <= 1e-12 else (target_d - d0) / seg_len

        x0, y0 = work_pts[seg_idx]
        x1, y1 = work_pts[seg_idx + 1]
        resampled.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))

    return resampled


def _align_closed_polygon_phase(
    src: List[Tuple[float, float]],
    tgt: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """
    Cyclic shift of `tgt` vertices to minimize total squared Euclidean homotopy distance
    against `src`, preventing path twisting during PowerPoint Morph transitions.
    """
    n = len(src)
    if n != len(tgt) or n <= 1:
        return tgt

    best_shift = 0
    best_cost = float("inf")
    for shift in range(n):
        cost = 0.0
        for i in range(n):
            sx, sy = src[i]
            tx, ty = tgt[(i + shift) % n]
            cost += (sx - tx) ** 2 + (sy - ty) ** 2
        if cost < best_cost:
            best_cost = cost
            best_shift = shift

    return [tgt[(i + best_shift) % n] for i in range(n)]


def resample_custom_path_homotopy(
    points_or_source: Sequence[Tuple[float, float]],
    target_or_count: Union[int, Sequence[Tuple[float, float]]] = 64,
    num_points: int = 64,
    closed: bool = True,
) -> Union[List[Tuple[float, float]], Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]]:
    """
    Uniform arc-length homotopy path resampler for Custom Geometry (`a:custGeom`) Morphing.

    Supports two calling conventions:
      1. Single path:
         `resample_custom_path_homotopy(points, target_count=64, closed=True)`
         -> returns `List[Tuple[float, float]]` of length `target_count`.
      2. Source-Target pair homotopy alignment:
         `resample_custom_path_homotopy(src_points, tgt_points, num_points=64, closed=True)`
         -> resamples both paths to `num_points` and aligns cyclic vertex phase,
            returning `(resampled_src, resampled_tgt)`.
    """
    if isinstance(target_or_count, int):
        count = int(target_or_count)
        return _resample_single_polyline(points_or_source, num_points=count, closed=closed)

    # Pair mode: target_or_count is a sequence of (x, y) points
    src_resampled = _resample_single_polyline(
        points_or_source, num_points=num_points, closed=closed
    )
    tgt_resampled = _resample_single_polyline(
        target_or_count, num_points=num_points, closed=closed
    )
    if closed:
        tgt_resampled = _align_closed_polygon_phase(src_resampled, tgt_resampled)
    return src_resampled, tgt_resampled


def apply_custom_geometry_points(
    shape_node: ET.Element,
    points: Sequence[Tuple[float, float]],
    path_w: int = 100000,
    path_h: int = 100000,
    closed: bool = True,
) -> ET.Element:
    """
    Replace a shape's geometry (`a:prstGeom` or `a:custGeom`) with a valid ECMA-376
    `<a:custGeom>` element constructed from `points`.

    If coordinates in `points` are normalized in [0.0, 1.0], they are scaled to
    `(path_w, path_h)`. Otherwise they are treated as direct path units.
    """
    if not points:
        raise ValueError("points must contain at least one (x, y) coordinate.")

    sp_pr = _get_sppr(shape_node)
    if sp_pr is None:
        sp_pr = _append_subelement(shape_node, _qname(P_NS, "spPr"))

    # Determine insertion index (immediately after a:xfrm per CT_ShapeProperties schema)
    insert_idx = 0
    for idx, child in enumerate(list(sp_pr)):
        local = _local_name(child.tag)
        if local == "xfrm":
            insert_idx = idx + 1
        elif local in ("prstGeom", "custGeom"):
            sp_pr.remove(child)

    cust_geom = _insert_subelement(sp_pr, insert_idx, _qname(A_NS, "custGeom"))
    _append_subelement(cust_geom, _qname(A_NS, "avLst"))
    _append_subelement(cust_geom, _qname(A_NS, "gdLst"))
    _append_subelement(cust_geom, _qname(A_NS, "ahLst"))
    _append_subelement(cust_geom, _qname(A_NS, "cxnLst"))
    _append_subelement(
        cust_geom,
        _qname(A_NS, "rect"),
        {"l": "0", "t": "0", "r": "r", "b": "b"},
    )
    path_lst = _append_subelement(cust_geom, _qname(A_NS, "pathLst"))

    # Detect whether input coordinates are normalized [0..1] floats
    max_coord = max(max(abs(float(px)), abs(float(py))) for px, py in points)
    is_normalized = max_coord <= 1.0 and any(
        isinstance(px, float) or isinstance(py, float) for px, py in points
    )

    eff_w = int(path_w)
    eff_h = int(path_h)
    if not is_normalized and max_coord > max(eff_w, eff_h):
        eff_w = int(math.ceil(max_coord))
        eff_h = int(math.ceil(max_coord))

    path_el = _append_subelement(
        path_lst,
        _qname(A_NS, "path"),
        {"w": str(eff_w), "h": str(eff_h)},
    )

    for idx, (px, py) in enumerate(points):
        if is_normalized:
            ix = int(round(float(px) * eff_w))
            iy = int(round(float(py) * eff_h))
        else:
            ix = int(round(float(px)))
            iy = int(round(float(py)))

        cmd_tag = _qname(A_NS, "moveTo" if idx == 0 else "lnTo")
        cmd_el = _append_subelement(path_el, cmd_tag)
        _append_subelement(cmd_el, _qname(A_NS, "pt"), {"x": str(ix), "y": str(iy)})

    if closed:
        _append_subelement(path_el, _qname(A_NS, "close"))

    return cust_geom


def audit_cognitive_motion_budget(
    source: Union[ET.Element, Sequence[ET.Element], List[Dict[str, Any]]],
    target_slide: Optional[ET.Element] = None,
    max_simultaneous: int = 4,
    max_total_displacement: float = 2.5,
    max_single_displacement: float = 1.25,
    slide_w: float = SLIDE_W,
    slide_h: float = SLIDE_H,
) -> Dict[str, Any]:
    """
    Evaluate whether a slide transition or staged Morph twin set stays within human
    visual working memory (FINST / Multiple Object Tracking) limits.

    Accepts:
      - Two slide XML roots: `audit_cognitive_motion_budget(slide_1, slide_2)`
      - Sequence of slide XML roots: `audit_cognitive_motion_budget([slide_1, slide_2])`
      - Single slide XML root: `audit_cognitive_motion_budget(slide_1)`
      - List of motion/staged twin dicts returned by `stage_cross_slide_morph_twins`.

    Returns:
        Dict with keys:
          "passed" (bool), "status" ("PASS" | "FAIL"), "simultaneous_count" (int),
          "total_displacement" (float), "max_displacement" (float),
          "cognitive_load_score" (float), "violations" (List[str]).
    """
    displacements: List[float] = []
    scale_deltas: List[float] = []

    if isinstance(source, ET.Element) and target_slide is not None:
        slide_pair = [source, target_slide]
    elif (
        isinstance(source, (list, tuple))
        and len(source) >= 2
        and all(isinstance(x, ET.Element) for x in source)
    ):
        slide_pair = [source[0], source[1]]
    else:
        slide_pair = None

    if slide_pair is not None:
        objs_a = {
            o["name"]: o
            for o in extract_objects(slide_pair[0], slide_w=slide_w, slide_h=slide_h)
            if o["name"].startswith(MORPH_PREFIX)
        }
        objs_b = {
            o["name"]: o
            for o in extract_objects(slide_pair[1], slide_w=slide_w, slide_h=slide_h)
            if o["name"].startswith(MORPH_PREFIX)
        }
        shared_names = set(objs_a.keys()) & set(objs_b.keys())
        for name in sorted(shared_names):
            ga = objs_a[name]["geometry"]
            gb = objs_b[name]["geometry"]
            cxa, cya = ga["x"] + ga["w"] * 0.5, ga["y"] + ga["h"] * 0.5
            cxb, cyb = gb["x"] + gb["w"] * 0.5, gb["y"] + gb["h"] * 0.5
            dist = math.hypot(cxb - cxa, cyb - cya)
            area_a = max(1e-6, ga["w"] * ga["h"])
            area_b = max(1e-6, gb["w"] * gb["h"])
            s_delta = abs(math.log(area_b / area_a))
            if dist > 1e-4 or s_delta > 1e-3:
                displacements.append(dist)
                scale_deltas.append(s_delta)

    elif isinstance(source, ET.Element):
        # Single slide audit: count !! morph objects and timing animation nodes
        objs = extract_objects(source, slide_w=slide_w, slide_h=slide_h)
        morph_objs = [o for o in objs if o["name"].startswith(MORPH_PREFIX)]
        for obj in morph_objs:
            g = obj["geometry"]
            # Estimate off-canvas travel distance if staged outside [0..1]
            cx, cy = g["x"] + g["w"] * 0.5, g["y"] + g["h"] * 0.5
            clamped_x = max(0.0, min(1.0, cx))
            clamped_y = max(0.0, min(1.0, cy))
            dist = math.hypot(cx - clamped_x, cy - clamped_y)
            displacements.append(max(0.25, dist))
            scale_deltas.append(0.0)

    elif isinstance(source, (list, tuple)):
        # List of motion records or object dicts
        for item in source:
            if not isinstance(item, dict):
                continue
            if "displacement" in item:
                displacements.append(float(item["displacement"]))
            elif "geometry" in item:
                g = item["geometry"]
                cx = g.get("x", 0.0) + g.get("w", 0.0) * 0.5
                cy = g.get("y", 0.0) + g.get("h", 0.0) * 0.5
                dist = math.hypot(cx - 0.5, cy - 0.5)
                displacements.append(dist)
            else:
                displacements.append(0.5)
            scale_deltas.append(float(item.get("scale_delta", 0.0)))

    simultaneous_count = len(displacements)
    total_disp = sum(displacements)
    max_disp = max(displacements) if displacements else 0.0
    cognitive_score = total_disp + 0.35 * sum(scale_deltas) + 0.25 * simultaneous_count

    violations: List[str] = []
    if simultaneous_count > max_simultaneous:
        violations.append(
            f"Simultaneous moving objects ({simultaneous_count}) exceeds limit ({max_simultaneous})."
        )
    if total_disp > max_total_displacement:
        violations.append(
            f"Total normalized displacement ({total_disp:.2f}) exceeds budget ({max_total_displacement:.2f})."
        )
    if max_disp > max_single_displacement:
        violations.append(
            f"Single object displacement ({max_disp:.2f}) exceeds max threshold ({max_single_displacement:.2f})."
        )

    passed = len(violations) == 0
    return {
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
        "simultaneous_count": simultaneous_count,
        "total_displacement": round(total_disp, 4),
        "max_displacement": round(max_disp, 4),
        "cognitive_load_score": round(cognitive_score, 4),
        "violations": violations,
    }
