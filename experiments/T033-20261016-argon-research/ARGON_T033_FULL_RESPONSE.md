1. Phản biện Kỹ thuật & Điểm nghẽn OOXML trong Yêu cầu Bài toán 1

Trước khi đi vào mã nguồn, dưới góc độ kiến trúc PresentationML (ECMA-376), có 3 lỗ hổng kỹ thuật trong bản đặc tả hiện tại sẽ gây lỗi sai lệch vị trí hoặc làm hỏng file (Corrupted Presentation) nếu chỉ cài đặt theo cách thông thường:

Bẫy Hệ tọa độ Cục bộ khi Phẳng hóa Group (`<p:grpSp>`):

Vấn đề trong yêu cầu: Đọc trực tiếp p:spPr/a:xfrm/a:off và a:ext của các shape con bên trong `<p:grpSp>` rồi chia cho (slide_w, slide_h).

Thực tế OOXML: Mọi shape con nằm trong `<p:grpSp>` không lưu tọa độ theo mặt phẳng Slide mà lưu theo không gian tọa độ nội bộ của Group (a:grpSpPr/a:xfrm/a:chOff và a:chExt), sau đó mới ánh xạ ra mặt phẳng Slide qua a:grpSpPr/a:xfrm/a:off và a:ext. Nếu lấy trực tiếp @x, @y của shape con đem nhân bản sang slide kế tiếp (nằm ngoài group), shape sẽ bị bay về góc trái trên hoặc biến dạng tỷ lệ.

Giải pháp tối ưu trong code bên dưới: Áp dụng phép biến đổi Affine đệ quy qua ma trận tỷ lệ của từng tầng `<p:grpSp>`:

𝑋
canvas
=
off
𝑥
+
(
𝑋
child
−
chOff
𝑥
)
×
ext
𝑐
𝑥
chExt
𝑐
𝑥
X
canvas
	​

=off
x
	​

+(X
child
	​

−chOff
x
	​

)×
chExt
cx
	​

ext
cx
	​

	​


Cơ chế Độ mờ (a:alpha) không tồn tại ở cấp p:spPr:

Vấn đề trong yêu cầu: Cập nhật trực tiếp a:alpha khi clone node.

Thực tế OOXML: DrawingML không có thuộc tính opacity tổng quát trên `<p:spPr>`. Nếu chèn trực tiếp `<a:alpha>` vào `<p:spPr>`, PowerPoint sẽ báo lỗi XML Schema khi mở file.

Giải pháp tối ưu trong code bên dưới: Hàm _apply_shape_opacity() tự động tiêm `<a:alpha val="..."/>` vào các node màu bên trong `<a:solidFill>`, `<a:gradFill>`, `<a:ln>` (viền), và sử dụng `<a:alphaModFix amt="..."/>` bên trong `<p:blipFill>/<a:blip>` đối với ảnh (`<p:pic>`).

Xung đột Schema CT_ShapeProperties khi áp dụng apply_custom_geometry_points:

Thực tế OOXML: Trong `<p:spPr>`, hai phần tử `<a:prstGeom>` và `<a:custGeom>` thuộc nhóm lựa chọn loại trừ (XOR) và bắt buộc phải đứng ngay sau `<a:xfrm>`. Hàm cập nhật hình học tự do phải xóa triệt để `<a:prstGeom>` cũ và chèn `<a:custGeom>` đúng thứ tự vị trí trong cây DOM.

2. Mã nguồn hoàn chỉnh: scripts/morph_playbook.py

Mã nguồn dưới đây tương thích với cả xml.etree.ElementTree chuẩn của Python lẫn lxml.etree (thông qua cơ chế makeelement đa hình), không cần cài đặt thêm thư viện ngoài.

Python
# -*- coding: utf-8 -*-
"""
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

3. Bộ Unit Test Hoàn chỉnh: tests/test_morph_playbook.py

Tập tin kiểm thử dưới đây tạo trực tiếp các fixture XML chuẩn ECMA-376 (bao gồm p:sp, p:pic, và cả p:grpSp lồng nhau) để kiểm chứng toàn diện 4 nhóm hàm theo đúng yêu cầu của Milestone T033.

Python
# -*- coding: utf-8 -*-
"""
Unit tests for scripts/morph_playbook.py (Milestone T033).
Run with: python -m unittest tests/test_morph_playbook.py
"""

import unittest
import xml.etree.ElementTree as ET

from scripts.morph_playbook import (
    A_NS,
    NS,
    P_NS,
    SLIDE_H,
    SLIDE_W,
    apply_custom_geometry_points,
    audit_cognitive_motion_budget,
    extract_objects,
    resample_custom_path_homotopy,
    stage_cross_slide_morph_twins,
)


def _build_slide_xml(shapes_xml: str) -> ET.Element:
    """Create a minimal ECMA-376 p:sld XML root containing the given shapes inside p:spTree."""
    xml_str = f"""\
<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {shapes_xml}
    </p:spTree>
  </p:cSld>
</p:sld>
"""
    return ET.fromstring(xml_str)


def _make_sp_xml(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    color_hex: str = "4F81BD",
) -> str:
    """Helper to generate a valid p:sp XML snippet."""
    return f"""\
<p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
  <p:nvSpPr>
    <p:cNvPr id="{shape_id}" name="{name}"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="{x}" y="{y}"/>
      <a:ext cx="{cx}" cy="{cy}"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
      <a:avLst/>
    </a:prstGeom>
    <a:solidFill>
      <a:srgbClr val="{color_hex}"/>
    </a:solidFill>
  </p:spPr>
</p:sp>
"""


def _make_pic_xml(
    pic_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
) -> str:
    """Helper to generate a valid p:pic XML snippet."""
    return f"""\
<p:pic xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:nvPicPr>
    <p:cNvPr id="{pic_id}" name="{name}"/>
    <p:cNvPicPr/>
    <p:nvPr/>
  </p:nvPicPr>
  <p:blipFill>
    <a:blip r:embed="rId2"/>
    <a:stretch><a:fillRect/></a:stretch>
  </p:blipFill>
  <p:spPr>
    <a:xfrm>
      <a:off x="{x}" y="{y}"/>
      <a:ext cx="{cx}" cy="{cy}"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
  </p:spPr>
</p:pic>
"""


class TestMorphPlaybook(unittest.TestCase):
    """Comprehensive unit tests for Milestone T033 Morph Playbook."""

    def test_extract_objects_shapes_pics_and_groups(self) -> None:
        """Verify extract_objects normalizes coordinates and flattens p:grpSp accurately."""
        # Shape 1: 10% x, 20% y, 30% w, 40% h
        sp1 = _make_sp_xml(
            shape_id=2,
            name="HeroCard",
            x=int(SLIDE_W * 0.10),
            y=int(SLIDE_H * 0.20),
            cx=int(SLIDE_W * 0.30),
            cy=int(SLIDE_H * 0.40),
        )
        # Picture 1: 50% x, 50% y, 25% w, 25% h
        pic1 = _make_pic_xml(
            pic_id=3,
            name="ProductPhoto",
            x=int(SLIDE_W * 0.50),
            y=int(SLIDE_H * 0.50),
            cx=int(SLIDE_W * 0.25),
            cy=int(SLIDE_H * 0.25),
        )
        # Group Shape with 2x scale mapping: chExt=(1000, 1000) mapped to ext=(0.2*W, 0.2*H)
        grp_x = int(SLIDE_W * 0.60)
        grp_y = int(SLIDE_H * 0.10)
        grp_w = int(SLIDE_W * 0.20)
        grp_h = int(SLIDE_H * 0.20)
        grp_xml = f"""\
<p:grpSp xmlns:p="{P_NS}" xmlns:a="{A_NS}">
  <p:nvGrpSpPr>
    <p:cNvPr id="4" name="IconGroup"/>
    <p:cNvGrpSpPr/>
    <p:nvPr/>
  </p:nvGrpSpPr>
  <p:grpSpPr>
    <a:xfrm>
      <a:off x="{grp_x}" y="{grp_y}"/>
      <a:ext cx="{grp_w}" cy="{grp_h}"/>
      <a:chOff x="0" y="0"/>
      <a:chExt cx="1000" cy="1000"/>
    </a:xfrm>
  </p:grpSpPr>
  {_make_sp_xml(shape_id=5, name="NestedBadge", x=500, y=500, cx=500, cy=500)}
</p:grpSp>
"""
        slide = _build_slide_xml(sp1 + pic1 + grp_xml)
        objects = extract_objects(slide, slide_w=SLIDE_W, slide_h=SLIDE_H)

        self.assertEqual(len(objects), 3)
        by_name = {obj["name"]: obj for obj in objects}

        # Verify HeroCard
        hero = by_name["HeroCard"]
        self.assertEqual(hero["id"], 2)
        self.assertAlmostEqual(hero["geometry"]["x"], 0.10, places=5)
        self.assertAlmostEqual(hero["geometry"]["y"], 0.20, places=5)
        self.assertAlmostEqual(hero["geometry"]["w"], 0.30, places=5)
        self.assertAlmostEqual(hero["geometry"]["h"], 0.40, places=5)

        # Verify ProductPhoto
        photo = by_name["ProductPhoto"]
        self.assertEqual(photo["id"], 3)
        self.assertAlmostEqual(photo["geometry"]["x"], 0.50, places=5)
        self.assertAlmostEqual(photo["geometry"]["w"], 0.25, places=5)

        # Verify NestedBadge transformed from group space to global slide space
        badge = by_name["NestedBadge"]
        self.assertEqual(badge["id"], 5)
        self.assertAlmostEqual(badge["geometry"]["x"], 0.70, places=5)
        self.assertAlmostEqual(badge["geometry"]["y"], 0.20, places=5)
        self.assertAlmostEqual(badge["geometry"]["w"], 0.10, places=5)
        self.assertAlmostEqual(badge["geometry"]["h"], 0.10, places=5)

    def test_stage_cross_slide_morph_twins_modes_and_ids(self) -> None:
        """Verify !! naming, non-colliding IDs, alpha injection, and all 7 staging modes."""
        # Slide 0 has ExitingCard; Slide 1 has EnteringPortal and EnteringStack
        slide_0 = _build_slide_xml(
            _make_sp_xml(
                shape_id=10,
                name="ExitingCard",
                x=int(SLIDE_W * 0.20),
                y=int(SLIDE_H * 0.20),
                cx=int(SLIDE_W * 0.30),
                cy=int(SLIDE_H * 0.30),
            )
        )
        slide_1 = _build_slide_xml(
            _make_sp_xml(
                shape_id=20,
                name="EnteringPortal",
                x=int(SLIDE_W * 0.40),
                y=int(SLIDE_H * 0.30),
                cx=int(SLIDE_W * 0.20),
                cy=int(SLIDE_H * 0.20),
            )
            + _make_pic_xml(
                pic_id=25,
                name="!!AlreadyNamedPic",
                x=int(SLIDE_W * 0.60),
                y=int(SLIDE_H * 0.40),
                cx=int(SLIDE_W * 0.15),
                cy=int(SLIDE_H * 0.15),
            )
        )

        plan = [
            {"name": "ExitingCard", "post_stage": "off-right"},
            {"name": "EnteringPortal", "pre_stage": "portal-seed"},
            {"name": "!!AlreadyNamedPic", "pre_stage": "corner-badge", "alpha": 0.15},
        ]

        records = stage_cross_slide_morph_twins([slide_0, slide_1], plan)
        self.assertEqual(len(records), 3)

        objs_s0 = {o["name"]: o for o in extract_objects(slide_0)}
        objs_s1 = {o["name"]: o for o in extract_objects(slide_1)}

        # Both slides must now contain all 3 Morph twin names
        expected_names = {
            "!!__stage_ExitingCard",
            "!!__stage_EnteringPortal",
            "!!AlreadyNamedPic",
        }
        self.assertTrue(expected_names.issubset(set(objs_s0.keys())))
        self.assertTrue(expected_names.issubset(set(objs_s1.keys())))

        # Verify ExitingCard post-staged off-right on Slide 1 with ID > 25
        staged_exit = objs_s1["!!__stage_ExitingCard"]
        self.assertGreater(staged_exit["id"], 25)
        self.assertGreater(staged_exit["geometry"]["x"], 1.0)
        alpha_node = staged_exit["node"].find(".//a:alpha", NS)
        self.assertIsNotNone(alpha_node)
        self.assertEqual(alpha_node.attrib.get("val"), "0")

        # Verify EnteringPortal pre-staged as portal-seed at center (0.50, 0.40) on Slide 0
        staged_portal = objs_s0["!!__stage_EnteringPortal"]
        self.assertGreater(staged_portal["id"], 10)
        portal_geom = staged_portal["geometry"]
        self.assertLess(portal_geom["w"], 0.02)
        self.assertAlmostEqual(
            portal_geom["x"] + portal_geom["w"] * 0.5, 0.50, places=3
        )
        self.assertAlmostEqual(
            portal_geom["y"] + portal_geom["h"] * 0.5, 0.40, places=3
        )

        # Verify !!AlreadyNamedPic pre-staged as corner-badge with alphaModFix = 15000
        staged_pic = objs_s0["!!AlreadyNamedPic"]
        mod_fix = staged_pic["node"].find(".//a:alphaModFix", NS)
        self.assertIsNotNone(mod_fix)
        self.assertEqual(mod_fix.attrib.get("amt"), "15000")

    def test_all_remaining_staging_modes(self) -> None:
        """Verify off-left, off-top, off-bottom, and telescopic-stack modes execute cleanly."""
        for mode in ("off-left", "off-top", "off-bottom", "telescopic-stack"):
            s0 = _build_slide_xml("")
            s1 = _build_slide_xml(
                _make_sp_xml(2, "Item", int(SLIDE_W * 0.3), int(SLIDE_H * 0.3), int(SLIDE_W * 0.2), int(SLIDE_H * 0.2))
            )
            recs = stage_cross_slide_morph_twins([s0, s1], {"Item": {"pre_stage": mode}})
            self.assertEqual(len(recs), 1)
            g = recs[0]["geometry"]
            if mode == "off-left":
                self.assertLess(g["x"] + g["w"], 0.0)
            elif mode == "off-top":
                self.assertLess(g["y"] + g["h"], 0.0)
            elif mode == "off-bottom":
                self.assertGreater(g["y"], 1.0)
            elif mode == "telescopic-stack":
                self.assertLess(g["w"], 0.2)

    def test_resample_and_apply_custom_geometry_points(self) -> None:
        """Verify homotopy resampling and custom geometry XML schema replacement."""
        triangle = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

        # 1. Single path resampling
        res_single = resample_custom_path_homotopy(triangle, 32, closed=True)
        self.assertEqual(len(res_single), 32)

        # 2. Pair homotopy alignment
        res_tri, res_sq = resample_custom_path_homotopy(
            triangle, square, num_points=48, closed=True
        )
        self.assertEqual(len(res_tri), 48)
        self.assertEqual(len(res_sq), 48)

        # 3. Inject into shape and check schema compliance (no leftover a:prstGeom)
        slide = _build_slide_xml(
            _make_sp_xml(2, "MorphBlob", 1000, 1000, 500000, 500000)
        )
        shape_node = extract_objects(slide)[0]["node"]
        self.assertIsNotNone(shape_node.find("p:spPr/a:prstGeom", NS))

        cust_geom = apply_custom_geometry_points(
            shape_node, res_tri, path_w=100000, path_h=100000, closed=True
        )
        self.assertIsNotNone(cust_geom)
        self.assertIsNone(shape_node.find("p:spPr/a:prstGeom", NS))
        self.assertIsNotNone(shape_node.find("p:spPr/a:custGeom", NS))

        move_to = cust_geom.findall(".//a:path/a:moveTo", NS)
        ln_to = cust_geom.findall(".//a:path/a:lnTo", NS)
        close_el = cust_geom.findall(".//a:path/a:close", NS)
        self.assertEqual(len(move_to), 1)
        self.assertEqual(len(ln_to), 47)
        self.assertEqual(len(close_el), 1)

    def test_audit_cognitive_motion_budget(self) -> None:
        """Verify cognitive motion budget passes within bounds and flags overload."""
        # Case 1: Clean transition (2 moving objects with moderate travel)
        s0_clean = _build_slide_xml(
            _make_sp_xml(2, "!!A", int(SLIDE_W * 0.1), int(SLIDE_H * 0.2), 1000000, 1000000)
            + _make_sp_xml(3, "!!B", int(SLIDE_W * 0.5), int(SLIDE_H * 0.2), 1000000, 1000000)
        )
        s1_clean = _build_slide_xml(
            _make_sp_xml(2, "!!A", int(SLIDE_W * 0.2), int(SLIDE_H * 0.2), 1000000, 1000000)
            + _make_sp_xml(3, "!!B", int(SLIDE_W * 0.6), int(SLIDE_H * 0.2), 1000000, 1000000)
        )
        clean_report = audit_cognitive_motion_budget(s0_clean, s1_clean, max_simultaneous=4)
        self.assertTrue(clean_report["passed"])
        self.assertEqual(clean_report["status"], "PASS")
        self.assertEqual(clean_report["simultaneous_count"], 2)
        self.assertEqual(len(clean_report["violations"]), 0)

        # Case 2: Overloaded transition (6 objects flying across the entire canvas)
        s0_heavy_shapes = "".join(
            _make_sp_xml(10 + i, f"!!Obj{i}", 0, 0, 500000, 500000)
            for i in range(6)
        )
        s1_heavy_shapes = "".join(
            _make_sp_xml(10 + i, f"!!Obj{i}", SLIDE_W, SLIDE_H, 500000, 500000)
            for i in range(6)
        )
        s0_heavy = _build_slide_xml(s0_heavy_shapes)
        s1_heavy = _build_slide_xml(s1_heavy_shapes)

        heavy_report = audit_cognitive_motion_budget(
            s0_heavy,
            s1_heavy,
            max_simultaneous=4,
            max_total_displacement=2.5,
        )
        self.assertFalse(heavy_report["passed"])
        self.assertEqual(heavy_report["status"], "FAIL")
        self.assertEqual(heavy_report["simultaneous_count"], 6)
        self.assertGreaterEqual(len(heavy_report["violations"]), 2)


if __name__ == "__main__":
    unittest.main()

4. Phác thảo Kiến trúc cho Bài toán 2 & Bài toán 3
Bài toán 2: Semantic Interactive Click Triggers (`<p:interactiveSeq>`)

Phản biện tên thẻ XML: Trong schema chuẩn ECMA-376, không có thẻ XML tên là `<p:interactiveSeq>`; thay vào đó, một chuỗi tương tác được định nghĩa bằng thẻ `<p:seq concurrent="1" nextAc="seek">` nằm ngang hàng với mainSeq bên trong `<p:timing>/<p:tnLst>`, nhưng mang thuộc tính định danh `<p:cTn id="..." nodeType="interactiveSeq">`.

Cấu trúc phân cấp chuẩn xác cần sinh tự động:

Node gốc tương tác: `<p:seq concurrent="1" nextAc="seek">` chứa `<p:cTn id="T_SEQ" dur="indefinite" restart="whenNotActive" nodeType="interactiveSeq">`.

Điều kiện kích hoạt (Trigger Binding):

Trong `<p:stCondLst>` của interactiveSeq (và lặp lại ở `<p:nextCondLst>` để hỗ trợ click nhiều bước kiểu Accordion/Tab):

XML
<p:cond evt="onClick" delay="0">
  <p:tgtEl>
    <p:spTgt spid="TRIGGER_SHAPE_ID"/>
  </p:tgtEl>
</p:cond>


Ràng buộc chống lỗi "Repair Presentation":

Bộ cấp phát TimeNode IDAllocator: Mọi thuộc tính @id của `<p:cTn>` trên toàn bộ slide (mainSeq + tất cả các interactiveSeq) phải tạo thành một dãy số nguyên dương tăng nghiêm ngặt (1, 2, 3, ...), tuyệt đối không trùng lặp.

Trước khi gắn spTgt làm trigger tương tác, phải quét và gỡ bỏ `<a:hlinkClick>` trong `<p:cNvPr>` của shape đó (nếu tồn tại cả hai, PowerPoint ưu tiên sự kiện Hyperlink và nuốt mất sự kiện onClick của interactiveSeq).

Bài toán 3: Cognitive Motion Budget & Cinematic Pacing

Mô hình toán học định lượng tải nhận thức (Optical Flow & FINST Budget):

Dựa trên lý thuyết Visual Indexing (Pylyshyn's FINST), mắt người chỉ theo dõi độc lập tối đa 4 vector chuyển động cùng lúc. Khi có nhiều hơn 4 phần tử di chuyển, hệ thống phải tự động gom nhóm (Grouping by Velocity Vector) hoặc chuyển sang chế độ Asymmetric Stagger (trễ pha bất đối xứng).

Công thức Chỉ số Năng lượng Chuyển động (Weighted Displacement Index - WDI):

WDI
=
∑
𝑖
=
1
𝑁
𝑤
role
,
𝑖
⋅
(
∥
Δ
𝑝
𝑖
∥
2
+
0.35
⋅
∣
ln
⁡
𝐴
𝑖
,
end
𝐴
𝑖
,
start
∣
+
0.20
⋅
∣
Δ
𝜃
𝑖
∣
180
∘
)
WDI=
i=1
∑
N
	​

w
role,i
	​

⋅(∥Δp
i
	​

∥
2
	​

+0.35⋅
	​

ln
A
i,start
	​

A
i,end
	​

	​

	​

+0.20⋅
180
∘
∣Δθ
i
	​

∣
	​

)

Ngưỡng an toàn: 
WDI
≤
2.5
WDI≤2.5 trên mỗi nhịp chuyển slide (dur từ 700ms đến 1100ms).

Bộ điều phối nhịp điệu điện ảnh (Cinematic Pacing Governor):

Phân tầng Vai trò (Role-Based Timing):

Hero Element: Chiếm 60% ngân sách thị giác, khởi chạy tại 
𝑡
=
0
ms
t=0ms, đường cong giảm tốc sâu (accel="10000" decel="80000").

Supporting Elements: Khởi chạy trễ pha theo hàm bậc hai 
Δ
𝑡
𝑘
=
65
ms
×
𝑘
0.85
Δt
k
	​

=65ms×k
0.85
 để tạo hiệu ứng làn sóng (Whip/Cascade) tự nhiên thay vì trễ tuyến tính cứng nhắc.

Background / Chrome: Chỉ biến đổi độ mờ (style.opacity) hoặc dịch chuyển vi mô (Parallax nhỏ hơn 4% chiều rộng slide).

Bạn có muốn triển khai luôn module sinh mã XML cho Bài toán 2 (interactiveSeq) kèm bộ cấp phát TimeNode ID tự động không?
Có