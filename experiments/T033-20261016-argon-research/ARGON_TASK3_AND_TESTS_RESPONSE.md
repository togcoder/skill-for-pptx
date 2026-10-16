1. Điểm Nâng cấp Kỹ thuật trong scripts/cognitive_pacing.py

Để bộ đo lường WDI (Weighted Displacement Index) và bộ điều phối Cinematic Pacing đạt độ chính xác vật lý cao nhất trên cây DOM của PowerPoint:

Giải mã Vector Chuyển động Nội bộ từ `<p:timing>` (Single-Slide Exact Telemetry):

Thay vì chỉ ước lượng tĩnh, hàm calculate_slide_motion_budget phân tích trực tiếp chuỗi lệnh SVG/VML trong thuộc tính @path của `<p:animMotion path="M 0 0 L 0.35 0.2 ...">` để tính khoảng cách dịch chuyển Euclid thực tế 
∥
Δ
𝑝
∥
2
∥Δp∥
2
	​

, đọc tỷ lệ phóng đại từ `<p:animScale>` (1/100000 đơn vị) để tính 
∣
ln
⁡
(
𝐴
end
/
𝐴
start
)
∣
∣ln(A
end
	​

/A
start
	​

)∣, và đọc góc quay từ `<p:animRot>` (1/60000 độ) để tính 
∣
Δ
𝜃
∣
/
180
∘
∣Δθ∣/180
∘
.

Hỗ trợ Đa cấu trúc Timeline trong apply_cinematic_pacing:

Hàm tự động nhận diện và xử lý cả 3 dạng cấu trúc đầu vào:

Danh sách phẳng các beat ([{"name": "HeroCard", "role": "hero"}, ...]).

Danh sách các nhóm nhịp click (Timeline Click Groups: [{"step": 1, "beats": [...]}, ...]), trong đó bộ đếm trễ pha bất đối xứng 
𝑘
k (dt_k = 65ms * k^0.85) được tái khởi tạo độc lập cho từng nhịp click.

Cây XML `<p:sld>` hoặc `<p:timing>` trực tiếp (cập nhật thuộc tính dur, accel, decel, và delay ngay trên các node `<p:cTn>`).

2. Mã nguồn hoàn chỉnh: scripts/cognitive_pacing.py
Python
# -*- coding: utf-8 -*-
"""
PPTX Motion Lab — Cognitive Motion Budget & Cinematic Pacing (Milestone T033 - Problem 3)
Module: scripts/cognitive_pacing.py

Implements:
  1. calculate_slide_motion_budget(slide_root, text_density_threshold=50)
     - Lexical density scanning across DrawingML text bodies (p:txBody // a:t)
     - Exponential ceiling attenuation:
       Ceiling_effective = max(0.85, 2.5 * exp(-0.45 * max(0.0, (W_words - W_threshold) / W_threshold)))
     - Dynamic FINST simultaneous tracking limit (4 -> 3 -> 2)
     - Weighted Displacement Index (WDI) from !! Morph twins and <p:timing> behaviors
  2. apply_cinematic_pacing(beats_or_timeline, pacing_mode="cinematic")
     - Asymmetric Stagger: dt_k = 65ms * (k ** 0.85)
     - Role-based timing orchestration (Hero / Supporting / Background-Chrome)
"""

from __future__ import annotations

import copy
import math
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from scripts.morph_playbook import (
    A_NS,
    MORPH_PREFIX,
    NS,
    P_NS,
    SLIDE_H,
    SLIDE_W,
    _get_sppr,
    extract_objects,
)

ROLE_WEIGHTS: Dict[str, float] = {
    "hero": 1.25,
    "supporting": 1.00,
    "background": 0.50,
}

ROLE_VISUAL_BUDGET: Dict[str, float] = {
    "hero": 0.60,
    "supporting": 0.30,
    "background": 0.10,
}

# Pacing profiles: (hero_dur_ms, supporting_dur_ms, bg_dur_ms, stagger_scale)
PACING_PROFILES: Dict[str, Tuple[int, int, int, float]] = {
    "cinematic": (850, 620, 1100, 1.00),
    "slow": (1050, 780, 1350, 1.25),
    "normal": (700, 500, 900, 0.85),
    "brisk": (500, 360, 650, 0.65),
}

BASE_STAGGER_MS: float = 65.0
STAGGER_EXPONENT: float = 0.85

_NUMBER_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _extract_text_metrics(slide_root: ET.Element) -> Tuple[int, int]:
    """
    Scan all text paragraphs (`p:txBody//a:p` and fallback `.//a:p`) on the slide,
    returning `(word_count, paragraph_count)`.
    """
    word_count = 0
    paragraph_count = 0

    tx_bodies = slide_root.findall(".//p:txBody", NS) + slide_root.findall(
        ".//a:txBody", NS
    )
    paragraphs = (
        [p for body in tx_bodies for p in body.findall(".//a:p", NS)]
        if tx_bodies
        else slide_root.findall(".//a:p", NS)
    )

    for para in paragraphs:
        para_words: List[str] = []
        for t_el in para.findall(".//a:t", NS):
            if t_el.text:
                tokens = t_el.text.strip().split()
                if tokens:
                    para_words.extend(tokens)
        if para_words:
            paragraph_count += 1
            word_count += len(para_words)

    return word_count, paragraph_count


def _read_rotation_degrees(shape_node: ET.Element) -> float:
    """Read rotation in degrees from `p:spPr/a:xfrm/@rot` (1/60,000th degree units)."""
    sp_pr = _get_sppr(shape_node)
    if sp_pr is None:
        return 0.0
    xfrm = sp_pr.find("a:xfrm", NS)
    if xfrm is None:
        return 0.0
    raw_rot = xfrm.attrib.get("rot")
    if raw_rot is None:
        return 0.0
    try:
        return float(raw_rot) / 60000.0
    except (ValueError, TypeError):
        return 0.0


def _classify_object_role(
    obj: Dict[str, Any],
    max_area: float,
) -> str:
    """
    Classify an object or beat into 'hero', 'supporting', or 'background'
    using explicit role tags, semantic name tokens, or normalized bounding-box area.
    """
    raw_role = str(obj.get("role", "")).strip().lower()
    if raw_role in ("chrome", "backdrop", "ambient"):
        return "background"
    if raw_role in ROLE_WEIGHTS:
        return raw_role

    name_lower = str(obj.get("name", "")).strip().lower()
    if any(k in name_lower for k in ("hero", "primary", "main", "focus", "spotlight")):
        return "hero"
    if any(
        k in name_lower
        for k in ("bg", "background", "backdrop", "chrome", "ambient")
    ):
        return "background"

    geom = obj.get("geometry")
    if isinstance(geom, dict):
        w = float(geom.get("w", 0.1))
        h = float(geom.get("h", 0.1))
        area = w * h
        if area >= 0.60:
            return "background"
        if max_area > 0.0 and area >= max(0.08, max_area * 0.85):
            return "hero"

    return "supporting"


def _parse_anim_motion_displacement(anim_motion_el: ET.Element) -> float:
    """
    Parse normalized Euclidean travel distance from a <p:animMotion> element
    via @path ('M x0 y0 L x1 y1 ...') or <p:from>/<p:to>/<p:by> points.
    """
    path_str = anim_motion_el.attrib.get("path", "").strip()
    if path_str:
        nums = [float(x) for x in _NUMBER_RE.findall(path_str)]
        if len(nums) >= 4:
            pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            total_d = 0.0
            for i in range(1, len(pts)):
                total_d += math.hypot(
                    pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
                )
            return total_d

    by_pt = anim_motion_el.find("p:by", NS)
    if by_pt is not None:
        try:
            bx = float(by_pt.attrib.get("x", "0")) / 100000.0
            by = float(by_pt.attrib.get("y", "0")) / 100000.0
            return math.hypot(bx, by)
        except ValueError:
            pass

    from_pt = anim_motion_el.find("p:from", NS)
    to_pt = anim_motion_el.find("p:to", NS)
    if from_pt is not None and to_pt is not None:
        try:
            fx = float(from_pt.attrib.get("x", "0")) / 100000.0
            fy = float(from_pt.attrib.get("y", "0")) / 100000.0
            tx = float(to_pt.attrib.get("x", "0")) / 100000.0
            ty = float(to_pt.attrib.get("y", "0")) / 100000.0
            return math.hypot(tx - fx, ty - fy)
        except ValueError:
            pass

    return 0.50


def _parse_anim_scale_log_ratio(anim_scale_el: ET.Element) -> float:
    """
    Compute |ln(A_end / A_start)| from a <p:animScale> element.
    """
    from_pt = anim_scale_el.find("p:from/p:pt", NS)
    to_pt = anim_scale_el.find("p:to/p:pt", NS)
    if from_pt is not None and to_pt is not None:
        try:
            fx = max(1.0, float(from_pt.attrib.get("x", "100000")))
            fy = max(1.0, float(from_pt.attrib.get("y", "100000")))
            tx = max(1.0, float(to_pt.attrib.get("x", "100000")))
            ty = max(1.0, float(to_pt.attrib.get("y", "100000")))
            area_ratio = (tx * ty) / (fx * fy)
            return abs(math.log(max(1e-6, area_ratio)))
        except ValueError:
            pass

    by_pt = anim_scale_el.find("p:by/p:pt", NS)
    if by_pt is not None:
        try:
            bx = max(1.0, float(by_pt.attrib.get("x", "100000"))) / 100000.0
            by = max(1.0, float(by_pt.attrib.get("y", "100000"))) / 100000.0
            return abs(math.log(max(1e-6, bx * by)))
        except ValueError:
            pass

    return 1.0


def _parse_anim_rot_degrees(anim_rot_el: ET.Element) -> float:
    """Extract absolute rotation angle delta in degrees from <p:animRot>."""
    by_el = anim_rot_el.find("p:by", NS)
    if by_el is not None and "val" in by_el.attrib:
        try:
            return abs(float(by_el.attrib["val"])) / 60000.0
        except ValueError:
            pass
    raw_by = anim_rot_el.attrib.get("by")
    if raw_by is not None:
        try:
            return abs(float(raw_by)) / 60000.0
        except ValueError:
            pass
    return 45.0


def calculate_slide_motion_budget(
    slide_root: ET.Element,
    text_density_threshold: int = 50,
    target_slide: Optional[ET.Element] = None,
    slide_w: float = SLIDE_W,
    slide_h: float = SLIDE_H,
) -> Dict[str, Any]:
    """
    Quantify lexical density, geometric complexity, and Weighted Displacement Index (WDI)
    on `slide_root` (and optional `target_slide` for cross-slide Morph evaluation).

    Exponential Ceiling Formula:
        Ceiling_effective = max(
            0.85,
            2.5 * exp(-0.45 * max(0.0, (W_words - W_threshold) / W_threshold))
        )

    Simultaneous FINST Limit:
        - W_words <= threshold      -> 4
        - W_words <= 2 * threshold  -> 3
        - W_words >  2 * threshold  -> 2

    WDI Formula:
        WDI = sum_{i=1..N} w_{role, i} * (
            ||Delta p_i||_2
            + 0.35 * |ln(A_{i,end} / A_{i,start})|
            + 0.20 * (|Delta theta_i| / 180.0)
        )

    Returns:
        {
            "budget_ceiling": float,
            "recommended_pace": "slow" | "normal" | "brisk",
            "max_simultaneous": int,
            "wdi": float,
            "word_count": int,
            "paragraph_count": int,
            "status": "PASS" | "OVERLOAD",
            "shape_count": int,
            "simultaneous_count": int,
        }
    """
    if text_density_threshold <= 0:
        raise ValueError("text_density_threshold must be > 0.")

    w_words, paragraph_count = _extract_text_metrics(slide_root)
    w_threshold = float(text_density_threshold)

    # 1. Exponential ceiling attenuation
    excess_ratio = max(0.0, (float(w_words) - w_threshold) / w_threshold)
    ceiling_effective = max(0.85, 2.5 * math.exp(-0.45 * excess_ratio))

    # 2. Dynamic FINST simultaneous tracking limit
    if w_words <= text_density_threshold:
        max_simultaneous = 4
    elif w_words <= 2 * text_density_threshold:
        max_simultaneous = 3
    else:
        max_simultaneous = 2

    # 3. Extract objects & classify visual roles
    objs = extract_objects(slide_root, slide_w=slide_w, slide_h=slide_h)
    shape_count = len(objs)

    non_bg_areas = [
        o["geometry"]["w"] * o["geometry"]["h"]
        for o in objs
        if (o["geometry"]["w"] * o["geometry"]["h"]) < 0.60
    ]
    max_area = max(non_bg_areas) if non_bg_areas else 0.0

    wdi = 0.0
    simultaneous_moving = 0

    if target_slide is not None:
        # Cross-slide exact Morph WDI between slide_root and target_slide
        objs_a = {o["name"]: o for o in objs if o["name"].startswith(MORPH_PREFIX)}
        objs_b = {
            o["name"]: o
            for o in extract_objects(target_slide, slide_w=slide_w, slide_h=slide_h)
            if o["name"].startswith(MORPH_PREFIX)
        }
        for name in sorted(set(objs_a.keys()) & set(objs_b.keys())):
            oa, ob = objs_a[name], objs_b[name]
            ga, gb = oa["geometry"], ob["geometry"]

            cxa, cya = ga["x"] + ga["w"] * 0.5, ga["y"] + ga["h"] * 0.5
            cxb, cyb = gb["x"] + gb["w"] * 0.5, gb["y"] + gb["h"] * 0.5
            disp = math.hypot(cxb - cxa, cyb - cya)

            area_a = max(1e-6, ga["w"] * ga["h"])
            area_b = max(1e-6, gb["w"] * gb["h"])
            scale_term = 0.35 * abs(math.log(area_b / area_a))

            rot_a = _read_rotation_degrees(oa["node"])
            rot_b = _read_rotation_degrees(ob["node"])
            rot_term = 0.20 * (abs(rot_b - rot_a) / 180.0)

            raw_energy = disp + scale_term + rot_term
            if raw_energy > 1e-4:
                role = _classify_object_role(oa, max_area)
                w_role = ROLE_WEIGHTS.get(role, 1.0)
                wdi += w_role * raw_energy
                simultaneous_moving += 1
    else:
        # Single-slide WDI evaluation from !! Morph objects and <p:timing> nodes
        obj_by_id = {str(o["id"]): o for o in objs}
        animated_spids: set[str] = set()

        for o in objs:
            name = o["name"]
            g = o["geometry"]
            cx, cy = g["x"] + g["w"] * 0.5, g["y"] + g["h"] * 0.5
            off_dx = max(0.0, -cx, cx - 1.0)
            off_dy = max(0.0, -cy, cy - 1.0)
            off_dist = math.hypot(off_dx, off_dy)

            if name.startswith(MORPH_PREFIX) or off_dist > 0.0:
                role = _classify_object_role(o, max_area)
                w_role = ROLE_WEIGHTS.get(role, 1.0)

                est_disp = off_dist if off_dist > 0.0 else 0.38
                area = max(1e-6, g["w"] * g["h"])
                est_scale = 0.35 * abs(math.log(0.04 / area)) if area < 0.002 else 0.0
                rot_deg = abs(_read_rotation_degrees(o["node"]))
                est_rot = 0.20 * (rot_deg / 180.0)

                wdi += w_role * (est_disp + est_scale + est_rot)
                simultaneous_moving += 1
                animated_spids.add(str(o["id"]))

        # Evaluate explicit <p:timing> motion/scale/rotation/effect nodes
        for motion_el in slide_root.findall(".//p:animMotion", NS):
            sp_tgt = motion_el.find(".//p:spTgt", NS)
            spid = sp_tgt.attrib.get("spid", "") if sp_tgt is not None else ""
            target_obj = obj_by_id.get(spid)
            role = (
                _classify_object_role(target_obj, max_area)
                if target_obj is not None
                else "supporting"
            )
            w_role = ROLE_WEIGHTS.get(role, 1.0)
            wdi += w_role * _parse_anim_motion_displacement(motion_el)
            if spid and spid not in animated_spids:
                animated_spids.add(spid)
                simultaneous_moving += 1

        for scale_el in slide_root.findall(".//p:animScale", NS):
            sp_tgt = scale_el.find(".//p:spTgt", NS)
            spid = sp_tgt.attrib.get("spid", "") if sp_tgt is not None else ""
            target_obj = obj_by_id.get(spid)
            role = (
                _classify_object_role(target_obj, max_area)
                if target_obj is not None
                else "supporting"
            )
            w_role = ROLE_WEIGHTS.get(role, 1.0)
            wdi += w_role * (0.35 * _parse_anim_scale_log_ratio(scale_el))
            if spid and spid not in animated_spids:
                animated_spids.add(spid)
                simultaneous_moving += 1

        for rot_el in slide_root.findall(".//p:animRot", NS):
            sp_tgt = rot_el.find(".//p:spTgt", NS)
            spid = sp_tgt.attrib.get("spid", "") if sp_tgt is not None else ""
            target_obj = obj_by_id.get(spid)
            role = (
                _classify_object_role(target_obj, max_area)
                if target_obj is not None
                else "supporting"
            )
            w_role = ROLE_WEIGHTS.get(role, 1.0)
            wdi += w_role * (0.20 * (_parse_anim_rot_degrees(rot_el) / 180.0))
            if spid and spid not in animated_spids:
                animated_spids.add(spid)
                simultaneous_moving += 1

        for eff_el in slide_root.findall(".//p:animEffect", NS) + slide_root.findall(
            ".//p:anim", NS
        ):
            sp_tgt = eff_el.find(".//p:spTgt", NS)
            spid = sp_tgt.attrib.get("spid", "") if sp_tgt is not None else ""
            target_obj = obj_by_id.get(spid)
            role = (
                _classify_object_role(target_obj, max_area)
                if target_obj is not None
                else "supporting"
            )
            w_role = ROLE_WEIGHTS.get(role, 1.0)
            wdi += w_role * 0.25
            if spid and spid not in animated_spids:
                animated_spids.add(spid)
                simultaneous_moving += 1

    # 4. Determine recommended pacing & cognitive overload status
    is_overload = (
        (wdi > ceiling_effective)
        or (simultaneous_moving > max_simultaneous)
        or (w_words > 2 * text_density_threshold and simultaneous_moving > 0)
    )
    status = "OVERLOAD" if is_overload else "PASS"

    if (
        is_overload
        or w_words > text_density_threshold
        or wdi > ceiling_effective * 0.80
        or shape_count >= 10
    ):
        recommended_pace = "slow"
    elif (
        w_words <= text_density_threshold * 0.4
        and shape_count <= 4
        and wdi <= 1.20
    ):
        recommended_pace = "brisk"
    else:
        recommended_pace = "normal"

    return {
        "budget_ceiling": round(ceiling_effective, 4),
        "recommended_pace": recommended_pace,
        "max_simultaneous": max_simultaneous,
        "wdi": round(wdi, 4),
        "word_count": w_words,
        "paragraph_count": paragraph_count,
        "status": status,
        "shape_count": shape_count,
        "simultaneous_count": simultaneous_moving,
    }


def _compute_asymmetric_stagger_ms(k: int, mode_scale: float = 1.0) -> int:
    """
    Compute asymmetric stagger delay in milliseconds for 1-based index `k`:
        dt_k = round(65ms * (k ** 0.85) * mode_scale)
    """
    if k <= 0:
        return 0
    return int(round(BASE_STAGGER_MS * mode_scale * (float(k) ** STAGGER_EXPONENT)))


def _pace_flat_beats(
    beats: Sequence[Dict[str, Any]],
    hero_dur: int,
    supp_dur: int,
    bg_dur: int,
    stagger_scale: float,
    pacing_mode: str,
) -> List[Dict[str, Any]]:
    """Assign role-based timing, steep easing, and asymmetric stagger to a sequence of beat dicts."""
    if not beats:
        return []

    items = [copy.deepcopy(b) for b in beats]

    areas: List[float] = []
    for b in items:
        if "area" in b:
            areas.append(float(b["area"]))
        elif isinstance(b.get("geometry"), dict):
            g = b["geometry"]
            areas.append(float(g.get("w", 0.1)) * float(g.get("h", 0.1)))
        else:
            areas.append(0.0)
    max_area = max([a for a in areas if a < 0.60], default=0.0)

    roles = [_classify_object_role(b, max_area) for b in items]
    if "hero" not in roles and items:
        for idx, r in enumerate(roles):
            if r != "background":
                roles[idx] = "hero"
                break
        else:
            roles[0] = "hero"

    hero_total = sum(1 for r in roles if r == "hero")
    supp_total = sum(1 for r in roles if r == "supporting")
    bg_total = sum(1 for r in roles if r == "background")

    stagger_k = 0
    paced: List[Dict[str, Any]] = []

    for b, role in zip(items, roles):
        b["role"] = role
        b["pacing_mode"] = pacing_mode

        if role == "hero":
            b["duration_ms"] = hero_dur
            b["delay_ms"] = 0
            b["stagger_index"] = 0
            b["accel"] = 10000
            b["decel"] = 80000
            b["visual_budget"] = ROLE_VISUAL_BUDGET["hero"]
            b["visual_budget_share"] = round(
                ROLE_VISUAL_BUDGET["hero"] / float(max(1, hero_total)), 4
            )
            b["animation_style"] = b.get("animation_style", "steep-ease-out")

        elif role == "supporting":
            stagger_k += 1
            delay_ms = _compute_asymmetric_stagger_ms(
                stagger_k, mode_scale=stagger_scale
            )
            b["duration_ms"] = supp_dur
            b["delay_ms"] = delay_ms
            b["stagger_index"] = stagger_k
            b["accel"] = 15000
            b["decel"] = 65000
            b["visual_budget"] = ROLE_VISUAL_BUDGET["supporting"]
            b["visual_budget_share"] = round(
                ROLE_VISUAL_BUDGET["supporting"] / float(max(1, supp_total)), 4
            )
            b["animation_style"] = b.get("animation_style", "stagger-wave")

        else:
            # role == "background" (Background / Chrome)
            b["duration_ms"] = bg_dur
            b["delay_ms"] = 0
            b["stagger_index"] = 0
            b["accel"] = 30000
            b["decel"] = 50000
            b["visual_budget"] = ROLE_VISUAL_BUDGET["background"]
            b["visual_budget_share"] = round(
                ROLE_VISUAL_BUDGET["background"] / float(max(1, bg_total)), 4
            )
            b["animation_style"] = b.get("animation_style", "subtle-opacity")
            b["max_opacity_delta"] = 0.25
            b["max_parallax_ratio"] = 0.04

        paced.append(b)

    return paced


def apply_cinematic_pacing(
    beats_or_timeline: Union[Sequence[Dict[str, Any]], Dict[str, Any], ET.Element],
    pacing_mode: str = "cinematic",
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Orchestrate duration, acceleration/deceleration physics, visual budget share,
    and power-law asymmetric stagger (`dt_k = 65ms * (k ** 0.85)`).

    Supports:
      1. Flat list of beat dicts: `[{"name": "Hero", "role": "hero"}, ...]`
      2. List of timeline click-group dicts: `[{"click_step": 1, "beats": [...]}, ...]`
      3. Wrapper dict with `"beats"`, `"timeline"`, `"groups"`, `"effects"`, or `"items"`
      4. XML `ET.Element` (`<p:sld>` or `<p:timing>`) -> updates `<p:cTn>` timing in-place.
    """
    mode_key = pacing_mode.strip().lower()
    if mode_key not in PACING_PROFILES:
        raise ValueError(
            f"Unsupported pacing_mode '{pacing_mode}'. Must be one of {sorted(PACING_PROFILES)}."
        )

    hero_dur, supp_dur, bg_dur, stagger_scale = PACING_PROFILES[mode_key]

    # Case 1: XML Element (<p:sld> or <p:timing>)
    if isinstance(beats_or_timeline, ET.Element):
        root = beats_or_timeline
        objs = extract_objects(root)
        non_bg_areas = [
            o["geometry"]["w"] * o["geometry"]["h"]
            for o in objs
            if (o["geometry"]["w"] * o["geometry"]["h"]) < 0.60
        ]
        max_area = max(non_bg_areas) if non_bg_areas else 0.0
        obj_by_id = {str(o["id"]): o for o in objs}

        synthesized_beats: List[Dict[str, Any]] = []
        effect_ctns: List[ET.Element] = []

        for ctn in root.findall(".//p:cTn", NS):
            if ctn.attrib.get("nodeType") in (
                "clickEffect",
                "withEffect",
                "afterEffect",
            ):
                sp_tgt = ctn.find(".//p:spTgt", NS)
                spid = sp_tgt.attrib.get("spid", "") if sp_tgt is not None else ""
                target_obj = obj_by_id.get(spid)
                role = (
                    _classify_object_role(target_obj, max_area)
                    if target_obj is not None
                    else "supporting"
                )
                synthesized_beats.append({
                    "id": spid or ctn.attrib.get("id", ""),
                    "name": (
                        target_obj["name"]
                        if target_obj is not None
                        else f"cTn_{ctn.attrib.get('id', '')}"
                    ),
                    "role": role,
                })
                effect_ctns.append(ctn)

        if not synthesized_beats and objs:
            for o in objs:
                synthesized_beats.append({
                    "id": o["id"],
                    "name": o["name"],
                    "role": _classify_object_role(o, max_area),
                    "geometry": o["geometry"],
                })

        paced_list = _pace_flat_beats(
            synthesized_beats,
            hero_dur=hero_dur,
            supp_dur=supp_dur,
            bg_dur=bg_dur,
            stagger_scale=stagger_scale,
            pacing_mode=mode_key,
        )

        for eff_ctn, paced in zip(effect_ctns, paced_list):
            eff_ctn.set("customDur", str(paced["duration_ms"]))
            st_cond = eff_ctn.find("p:stCondLst/p:cond", NS)
            if st_cond is not None:
                st_cond.set("delay", str(paced["delay_ms"]))
            for bhvr_ctn in eff_ctn.findall(".//p:cBhvr/p:cTn", NS):
                if bhvr_ctn.attrib.get("dur") != "1":
                    bhvr_ctn.set("dur", str(paced["duration_ms"]))
                    bhvr_ctn.set("accel", str(paced["accel"]))
                    bhvr_ctn.set("decel", str(paced["decel"]))

        return paced_list

    # Case 2: Wrapper dictionary
    if isinstance(beats_or_timeline, dict):
        wrapper = copy.deepcopy(beats_or_timeline)
        for key in ("beats", "timeline", "groups", "click_groups", "effects", "items", "objects"):
            if key in wrapper and isinstance(wrapper[key], list):
                wrapper[key] = apply_cinematic_pacing(
                    wrapper[key], pacing_mode=mode_key
                )
                wrapper["pacing_mode"] = mode_key
                return wrapper

        paced_single = _pace_flat_beats(
            [wrapper],
            hero_dur=hero_dur,
            supp_dur=supp_dur,
            bg_dur=bg_dur,
            stagger_scale=stagger_scale,
            pacing_mode=mode_key,
        )
        return paced_single[0]

    # Case 3: Sequence (either flat beat dicts OR timeline click-group dicts)
    if isinstance(beats_or_timeline, (list, tuple)):
        if not beats_or_timeline:
            return []

        # Detect if elements are click-group dicts containing nested lists
        first_elem = beats_or_timeline[0]
        if isinstance(first_elem, dict) and any(
             isinstance(first_elem.get(k), list)
            for k in ("beats", "effects", "items", "targets")
        ):
            paced_groups: List[Dict[str, Any]] = []
            for grp in beats_or_timeline:
                grp_copy = copy.deepcopy(grp)
                for nested_key in ("beats", "effects", "items"):
                    if nested_key in grp_copy and isinstance(grp_copy[nested_key], list):
                        grp_copy[nested_key] = _pace_flat_beats(
                            grp_copy[nested_key],
                            hero_dur=hero_dur,
                            supp_dur=supp_dur,
                            bg_dur=bg_dur,
                            stagger_scale=stagger_scale,
                            pacing_mode=mode_key,
                        )
                        grp_copy["pacing_mode"] = mode_key
                        break
                paced_groups.append(grp_copy)
            return paced_groups

        return _pace_flat_beats(
            beats_or_timeline,
            hero_dur=hero_dur,
            supp_dur=supp_dur,
            bg_dur=bg_dur,
            stagger_scale=stagger_scale,
            pacing_mode=mode_key,
        )

    raise TypeError(
        f"Unsupported beats_or_timeline type: {type(beats_or_timeline).__name__}"
    )

3. Bộ Unit Test Hoàn chỉnh: tests/test_interactive_and_pacing.py
Python
# -*- coding: utf-8 -*-
"""
Unit tests for Milestone T033 (Problems 2 & 3):
  - scripts/interactive_triggers.py
  - scripts/cognitive_pacing.py

Run with:
    python -m unittest tests/test_interactive_and_pacing.py -v
"""

import math
import unittest
import xml.etree.ElementTree as ET
from typing import List, Optional

from scripts.cognitive_pacing import (
    apply_cinematic_pacing,
    calculate_slide_motion_budget,
)
from scripts.interactive_triggers import (
    TimeNodeIDAllocator,
    apply_interactive_triggers,
    read_interactive_triggers,
)
from scripts.morph_playbook import A_NS, NS, P_NS, R_NS, SLIDE_H, SLIDE_W


def _build_fixture_slide(shapes_xml: str, timing_xml: str = "") -> ET.Element:
    """Create a minimal ECMA-376 <p:sld> root element with shapes and optional timing."""
    xml_str = f"""\
<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}">
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
  {timing_xml}
</p:sld>
"""
    return ET.fromstring(xml_str)


def _make_shape_xml(
    spid: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    paragraphs: Optional[List[str]] = None,
    with_hlink: bool = False,
) -> str:
    """Create a <p:sp> XML block with optional <a:hlinkClick> and text paragraphs."""
    hlink_xml = (
        f'<a:hlinkClick xmlns:a="{A_NS}" xmlns:r="{R_NS}" r:id="rId77" action="ppaction://hlinkshowjump?jump=nextslide"/>'
        if with_hlink
        else ""
    )
    tx_body_xml = ""
    if paragraphs:
        p_xml = "".join(
            f"<a:p><a:r><a:t>{text}</a:t></a:r></a:p>" for text in paragraphs
        )
        tx_body_xml = f"<p:txBody><a:bodyPr/><a:lstStyle/>{p_xml}</p:txBody>"

    return f"""\
<p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}">
  <p:nvSpPr>
    <p:cNvPr id="{spid}" name="{name}">
      {hlink_xml}
    </p:cNvPr>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="{x}" y="{y}"/>
      <a:ext cx="{cx}" cy="{cy}"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
  </p:spPr>
  {tx_body_xml}
</p:sp>
"""


class TestInteractiveTriggers(unittest.TestCase):
    """Unit tests for scripts/interactive_triggers.py."""

    def test_timenode_id_allocator_monotonic(self) -> None:
        """Verify TimeNodeIDAllocator scans existing <p:cTn> IDs and allocates monotonically."""
        existing_timing = f"""\
<p:timing xmlns:p="{P_NS}">
  <p:tnLst>
    <p:par>
      <p:cTn id="3" dur="indefinite" nodeType="tmRoot">
        <p:childTnLst>
          <p:seq concurrent="1" nextAc="seek">
            <p:cTn id="12" dur="indefinite" nodeType="mainSeq"/>
          </p:seq>
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>
"""
        slide = _build_fixture_slide("", timing_xml=existing_timing)
        allocator = TimeNodeIDAllocator(slide)

        self.assertEqual(allocator.current_max, 12)
        self.assertEqual(allocator.allocate(), 13)
        self.assertEqual(allocator.allocate(), 14)
        self.assertEqual(allocator.allocate_str(), "15")

    def test_apply_and_read_all_actions_and_hlink_removal(self) -> None:
        """
        Verify apply_interactive_triggers:
          - Supports reveal, hide, highlight, toggle actions
          - Strips <a:hlinkClick> from trigger shape p:cNvPr
          - Generates valid <p:cTn nodeType="interactiveSeq"> and <p:nextCondLst>
          - Round-trips via read_interactive_triggers()
        """
        shapes_xml = (
            _make_shape_xml(10, "Btn_Reveal", 100, 100, 500, 300, with_hlink=True)
            + _make_shape_xml(11, "Btn_Hide", 100, 500, 500, 300, with_hlink=True)
            + _make_shape_xml(12, "Btn_Highlight", 100, 900, 500, 300, with_hlink=True)
            + _make_shape_xml(13, "Btn_Toggle", 100, 1300, 500, 300, with_hlink=True)
            + _make_shape_xml(20, "Card_A", 2000, 200, 1500, 1000)
            + _make_shape_xml(21, "Card_B", 4000, 200, 1500, 1000)
        )
        slide = _build_fixture_slide(shapes_xml)

        # Ensure 4 <a:hlinkClick> elements exist initially
        self.assertEqual(len(slide.findall(".//a:hlinkClick", NS)), 4)

        plan = [
            {
                "trigger": "Btn_Reveal",
                "action": "reveal",
                "targets": ["Card_A", "Card_B"],
                "preset": "zoom",
                "duration_ms": 600,
                "delay_ms": 25,
            },
            {
                "trigger": "Btn_Hide",
                "action": "hide",
                "targets": ["Card_A"],
                "preset": "fade",
                "duration_ms": 400,
                "delay_ms": 0,
            },
            {
                "trigger": "Btn_Highlight",
                "action": "highlight",
                "targets": ["Card_B"],
                "preset": "teeter",
                "duration_ms": 500,
                "delay_ms": 10,
            },
            {
                "trigger": 13,  # Test spid integer lookup for Btn_Toggle
                "action": "toggle",
                "targets": ["Card_A"],
                "preset": "float-in",
                "duration_ms": 550,
                "delay_ms": 0,
            },
        ]

        records = apply_interactive_triggers(slide, plan)
        self.assertEqual(len(records), 4)

        # 1. Confirm all <a:hlinkClick> nodes were removed from trigger shapes
        self.assertEqual(len(slide.findall(".//a:hlinkClick", NS)), 0)
        for rec in records:
            self.assertEqual(rec["hlinks_removed"], 1)

        # 2. Confirm strictly increasing, non-colliding <p:cTn id="..."> across entire slide
        ctn_ids = [
            int(ctn.attrib["id"])
            for ctn in slide.findall(".//p:cTn", NS)
            if "id" in ctn.attrib
        ]
        self.assertEqual(ctn_ids, sorted(ctn_ids))
        self.assertEqual(len(ctn_ids), len(set(ctn_ids)))

        # 3. Verify round-trip extraction via read_interactive_triggers()
        extracted = read_interactive_triggers(slide)
        self.assertEqual(len(extracted), 4)

        self.assertEqual(extracted[0]["trigger_spid"], "10")
        self.assertEqual(extracted[0]["target_spids"], ["20", "21"])
        self.assertEqual(extracted[0]["action"], "reveal")
        self.assertEqual(extracted[0]["preset"], "zoom")
        self.assertEqual(extracted[0]["duration_ms"], 600)
        self.assertEqual(extracted[0]["delay_ms"], 25)

        self.assertEqual(extracted[1]["trigger_spid"], "11")
        self.assertEqual(extracted[1]["target_spids"], ["20"])
        self.assertEqual(extracted[1]["action"], "hide")
        self.assertEqual(extracted[1]["preset"], "fade")

        self.assertEqual(extracted[2]["trigger_spid"], "12")
        self.assertEqual(extracted[2]["target_spids"], ["21"])
        self.assertEqual(extracted[2]["action"], "highlight")
        self.assertEqual(extracted[2]["preset"], "teeter")

        self.assertEqual(extracted[3]["trigger_spid"], "13")
        self.assertEqual(extracted[3]["target_spids"], ["20"])
        self.assertEqual(extracted[3]["action"], "toggle")
        self.assertEqual(extracted[3]["preset"], "float-in")


class TestCognitivePacing(unittest.TestCase):
    """Unit tests for scripts/cognitive_pacing.py."""

    def test_calculate_slide_motion_budget_low_and_high_density(self) -> None:
        """
        Verify calculate_slide_motion_budget:
          - Low text density (<= threshold): budget_ceiling == 2.5, max_simultaneous == 4, status == PASS
          - High text density (> 2 * threshold) + heavy motion: attenuated ceiling, max_simultaneous == 2, status == OVERLOAD
        """
        # 1. Low text density slide (10 words across 2 paragraphs, 1 subtle Morph shape)
        low_shapes = _make_shape_xml(
            2,
            "!!HeroVisual",
            int(SLIDE_W * 0.15),
            int(SLIDE_H * 0.20),
            int(SLIDE_W * 0.35),
            int(SLIDE_H * 0.35),
            paragraphs=[
                "Focused executive summary.",
                "Minimal visual tracking load for viewers.",
            ],
        )
        low_slide = _build_fixture_slide(low_shapes)
        low_res = calculate_slide_motion_budget(low_slide, text_density_threshold=50)

        self.assertEqual(low_res["word_count"], 10)
        self.assertEqual(low_res["paragraph_count"], 2)
        self.assertAlmostEqual(low_res["budget_ceiling"], 2.5, places=4)
        self.assertEqual(low_res["max_simultaneous"], 4)
        self.assertEqual(low_res["status"], "PASS")
        self.assertIn(low_res["recommended_pace"], ("brisk", "normal"))

        # 2. Medium text density slide (75 words -> between 1x and 2x threshold=50)
        med_words = " ".join([f"token{i}" for i in range(75)])
        med_slide = _build_fixture_slide(
            _make_shape_xml(2, "TextBlock", 100, 100, 2000, 2000, paragraphs=[med_words])
        )
        med_res = calculate_slide_motion_budget(med_slide, text_density_threshold=50)
        expected_med_ceiling = max(0.85, 2.5 * math.exp(-0.45 * ((75 - 50) / 50.0)))
        self.assertAlmostEqual(
            med_res["budget_ceiling"], round(expected_med_ceiling, 4), places=4
        )
        self.assertEqual(med_res["max_simultaneous"], 3)

        # 3. High text density slide (120 words > 2 * threshold) + 4 off-canvas !! Morph shapes
        high_p1 = " ".join([f"wordA_{i}" for i in range(60)])
        high_p2 = " ".join([f"wordB_{i}" for i in range(60)])
        heavy_shapes = "".join(
            _make_shape_xml(
                10 + i,
                f"!!OffCanvasCard_{i}",
                int(-SLIDE_W * 0.6),
                int(SLIDE_H * 0.15 * i),
                int(SLIDE_W * 0.25),
                int(SLIDE_H * 0.20),
                paragraphs=[high_p1, high_p2] if i == 0 else None,
            )
            for i in range(4)
        )
        high_slide = _build_fixture_slide(heavy_shapes)
        high_res = calculate_slide_motion_budget(high_slide, text_density_threshold=50)

        expected_high_ceiling = max(0.85, 2.5 * math.exp(-0.45 * ((120 - 50) / 50.0)))
        self.assertEqual(high_res["word_count"], 120)
        self.assertEqual(high_res["paragraph_count"], 2)
        self.assertAlmostEqual(
            high_res["budget_ceiling"], round(expected_high_ceiling, 4), places=4
        )
        self.assertEqual(high_res["max_simultaneous"], 2)
        self.assertEqual(high_res["status"], "OVERLOAD")
        self.assertEqual(high_res["recommended_pace"], "slow")
        self.assertGreater(high_res["wdi"], high_res["budget_ceiling"])

    def test_apply_cinematic_pacing_asymmetric_stagger_and_click_groups(self) -> None:
        """
        Verify apply_cinematic_pacing:
          - Computes asymmetric stagger dt_k = round(65 * k^0.85)
          - Allocates Hero (dur=850, accel=10000, decel=80000, budget=0.60)
          - Allocates Supporting (stagger wave, budget=0.30)
          - Allocates Background/Chrome (subtle-opacity, budget=0.10)
          - Supports both flat beat lists and nested timeline click groups
        """
        flat_beats = [
            {"name": "AmbientBackdrop", "role": "background"},
            {"name": "HeroDiagram", "role": "hero"},
            {"name": "Callout_1", "role": "supporting"},
            {"name": "Callout_2", "role": "supporting"},
            {"name": "Callout_3", "role": "supporting"},
        ]

        paced = apply_cinematic_pacing(flat_beats, pacing_mode="cinematic")
        by_name = {b["name"]: b for b in paced}

        # Hero checks
        hero = by_name["HeroDiagram"]
        self.assertEqual(hero["duration_ms"], 850)
        self.assertEqual(hero["delay_ms"], 0)
        self.assertEqual(hero["accel"], 10000)
        self.assertEqual(hero["decel"], 80000)
        self.assertAlmostEqual(hero["visual_budget"], 0.60, places=4)

        # Supporting asymmetric stagger checks: dt_k = round(65 * (k ** 0.85))
        for k in (1, 2, 3):
            callout = by_name[f"Callout_{k}"]
            expected_dt = int(round(65.0 * (float(k) ** 0.85)))
            self.assertEqual(callout["delay_ms"], expected_dt)
            self.assertEqual(callout["duration_ms"], 620)
            self.assertEqual(callout["animation_style"], "stagger-wave")

        # Background checks
        bg = by_name["AmbientBackdrop"]
        self.assertEqual(bg["duration_ms"], 1100)
        self.assertEqual(bg["delay_ms"], 0)
        self.assertEqual(bg["animation_style"], "subtle-opacity")
        self.assertAlmostEqual(bg["visual_budget"], 0.10, places=4)

        # Timeline click-groups check
        timeline_groups = [
            {
                "click_step": 1,
                "beats": [
                    {"name": "Step1_Hero", "role": "hero"},
                    {"name": "Step1_SubA", "role": "supporting"},
                    {"name": "Step1_SubB", "role": "supporting"},
                ],
            }
        ]
        paced_groups = apply_cinematic_pacing(timeline_groups, pacing_mode="cinematic")
        self.assertEqual(len(paced_groups), 1)
        group_beats = paced_groups[0]["beats"]
        self.assertEqual(group_beats[0]["delay_ms"], 0)
        self.assertEqual(group_beats[1]["delay_ms"], 65)
        self.assertEqual(
            group_beats[2]["delay_ms"], int(round(65.0 * (2.0 ** 0.85)))
        )


if __name__ == "__main__":
    unittest.main()

4. Lệnh Kiểm thử Tích hợp

Sau khi lưu scripts/cognitive_pacing.py và tests/test_interactive_and_pacing.py, bạn có thể chạy kiểm thử toàn bộ Milestone T033 bằng lệnh:

Bash
python -m unittest discover -s tests -p "test_*.py" -v

Bạn có muốn tiếp tục với phần tích hợp 3 module của Milestone T033 vào pipeline CLI hoặc bộ validator chính của dự án không?
Có