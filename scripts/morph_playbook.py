#!/usr/bin/env python3
"""Morph playbook helpers from the Argon (Gemini) research drop (T032 import).

EXPERIMENTAL and untested upstream: in the drop this code sat at the end of
motion_engine.py, referenced undefined names (ET, A, NS, SLIDE_W, SLIDE_H) and
broke the module import. It is kept here, with imports fixed, for later
evaluation: Morph custom-geometry homotopy (equal vertex count, clockwise
winding), a cognitive motion budget audit and cross-slide pre/post staging of
Morph twins (off-canvas, portal seed, telescopic stack, corner badge).
Nothing in the pipeline calls it yet.
"""
import copy
import math

from lxml import etree as ET

try:
    from .pptx_animator import A, NS, P
    from .motion_engine import authored, fresh_state
except ImportError:
    from pptx_animator import A, NS, P
    from motion_engine import authored, fresh_state

SLIDE_W,SLIDE_H=12192000,6858000  # 16:9 EMU default


# ==============================================================================
# T024 PHASE 2-4: KINEMATIC SOLVERS, HOMOTOPY & PRO MORPH PLAYBOOK STAGING
# ==============================================================================

def _polygon_signed_area(pts):
    """Signed area in Y-down slide coordinates (>0 means clockwise)."""
    n = len(pts)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return 0.5 * area


def _ensure_clockwise_ring(pts):
    """Ensure polygon vertices wind clockwise in Y-down slide space per MS Morph rules."""
    pts_list = list(pts)
    if len(pts_list) > 1 and math.hypot(pts_list[0][0] - pts_list[-1][0], pts_list[0][1] - pts_list[-1][1]) < 1e-6:
        pts_list = pts_list[:-1]
    if _polygon_signed_area(pts_list) < 0:
        pts_list.reverse()
    return pts_list


def _normalize_ring(pts, n_vertices=96):
    """Resample closed ring to n_vertices uniform arc-length points, clockwise, starting at 12 o'clock (-pi/2)."""
    ring = _ensure_clockwise_ring(pts)
    if not ring:
        return [(0.0, 0.0)] * n_vertices
    closed = ring + [ring[0]]
    dists = [0.0]
    for i in range(len(ring)):
        d = math.hypot(closed[i+1][0] - closed[i][0], closed[i+1][1] - closed[i][1])
        dists.append(dists[-1] + d)
    total = dists[-1] or 1.0
    sampled = []
    for k in range(n_vertices):
        target = (k / n_vertices) * total
        idx = 0
        while idx < len(ring) - 1 and dists[idx + 1] < target:
            idx += 1
        seg = (dists[idx + 1] - dists[idx]) or 1.0
        t = (target - dists[idx]) / seg
        x = closed[idx][0] + t * (closed[idx + 1][0] - closed[idx][0])
        y = closed[idx][1] + t * (closed[idx + 1][1] - closed[idx][1])
        sampled.append((x, y))
    cx = sum(p[0] for p in sampled) / len(sampled)
    cy = sum(p[1] for p in sampled) / len(sampled)
    best_i = min(
        range(len(sampled)),
        key=lambda i: abs(((math.atan2(sampled[i][1] - cy, sampled[i][0] - cx) + math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi)
    )
    return sampled[best_i:] + sampled[:best_i]


def resample_custom_path_homotopy(pts_a, pts_b, n_vertices=96):
    """Resample two custom polygons to identical N vertices, clockwise winding, aligned at 12 o'clock."""
    return _normalize_ring(pts_a, n_vertices), _normalize_ring(pts_b, n_vertices)


def apply_custom_geometry_points(shape_node, pts, coord_scale=100000):
    """Write normalized [0,1] polygon vertices into `<a:custGeom>` on `p:spPr`."""
    spPr = shape_node.find("p:spPr", NS)
    if spPr is None:
        return False
    for tag in ("a:prstGeom", "a:custGeom"):
        old = spPr.find(tag, NS)
        if old is not None:
            spPr.remove(old)
    cust = ET.SubElement(spPr, f"{{{A}}}custGeom")
    ET.SubElement(cust, f"{{{A}}}avLst")
    ET.SubElement(cust, f"{{{A}}}gdLst")
    ET.SubElement(cust, f"{{{A}}}ahLst")
    ET.SubElement(cust, f"{{{A}}}cxnLst")
    ET.SubElement(cust, f"{{{A}}}rect", {"l": "0", "t": "0", "r": str(coord_scale), "b": str(coord_scale)})
    pathLst = ET.SubElement(cust, f"{{{A}}}pathLst")
    path = ET.SubElement(pathLst, f"{{{A}}}path", {"w": str(coord_scale), "h": str(coord_scale)})
    if pts:
        mv = ET.SubElement(path, f"{{{A}}}moveTo")
        ET.SubElement(mv, f"{{{A}}}pt", {"x": str(int(round(pts[0][0] * coord_scale))), "y": str(int(round(pts[0][1] * coord_scale)))})
        for x, y in pts[1:]:
            ln = ET.SubElement(path, f"{{{A}}}lnTo")
            ET.SubElement(ln, f"{{{A}}}pt", {"x": str(int(round(x * coord_scale))), "y": str(int(round(y * coord_scale)))})
        ET.SubElement(path, f"{{{A}}}close")
    return True


def audit_cognitive_motion_budget(plan):
    """Enforce Cognitive Motion Budget across slides and transitions."""
    slides = plan.get("slides", [])
    warnings = []
    morph_count = 0
    clutter_slides = 0
    for s in slides:
        tr = s.get("transition") or {}
        if tr.get("type") == "morph":
            morph_count += 1
        beats = s.get("beats", [])
        simple_reveals = sum(1 for b in beats if b.get("preset") in ("appear", "fade", "rise-up", "float-in"))
        if simple_reveals > 4 and tr.get("type") == "morph":
            clutter_slides += 1
            warnings.append(f"Slide {s.get('slide')}: excessive simple reveals ({simple_reveals}) after Morph transition")
    return {
        "ok": len(warnings) == 0,
        "warnings": warnings,
        "metrics": {
            "total_slides": len(slides),
            "morph_transitions": morph_count,
            "simple_reveal_clutter_slides": clutter_slides,
        },
    }


def _set_shape_geometry_norm(node, x, y, w, h, slide_w=SLIDE_W, slide_h=SLIDE_H):
    xfrm = node.find(".//a:xfrm", NS)
    if xfrm is None:
        return
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is not None:
        off.set("x", str(int(round(x * slide_w))))
        off.set("y", str(int(round(y * slide_h))))
    if ext is not None:
        ext.set("cx", str(max(1, int(round(w * slide_w)))))
        ext.set("cy", str(max(1, int(round(h * slide_h)))))


def _set_shape_alpha(node, alpha):
    alpha_val = str(max(0, min(100000, int(round(alpha * 100000)))))
    spPr = node.find("p:spPr", NS)
    if spPr is None:
        return
    for sfill in spPr.findall(".//a:solidFill", NS):
        for clr in list(sfill):
            for old_a in clr.findall("a:alpha", NS):
                clr.remove(old_a)
            ET.SubElement(clr, f"{{{A}}}alpha", {"val": alpha_val})
    for gs in spPr.findall(".//a:gradFill//a:gs", NS):
        for clr in list(gs):
            for old_a in clr.findall("a:alpha", NS):
                clr.remove(old_a)
            ET.SubElement(clr, f"{{{A}}}alpha", {"val": alpha_val})


def _resolve_targets(objs, targets):
    matched = []
    seen = set()
    for t in targets:
        for o in objs:
            name = o.get("name") or ""
            if o["id"] in seen:
                continue
            if name in (t, f"!!{t}", f"!!__stage_{t}") or str(o["id"]) == str(t):
                matched.append(o)
                seen.add(o["id"])
            elif t.endswith(":*") and (name.startswith(t[:-1]) or name.startswith(f"!!{t[:-1]}") or name.startswith(f"!!__stage_{t[:-1]}")):
                matched.append(o)
                seen.add(o["id"])
    return matched


def stage_cross_slide_morph_twins(slide_roots, plan, slide_w=SLIDE_W, slide_h=SLIDE_H):
    """Automate the 6 Pro PowerPoint Morph Playbook pre-staging & post-staging techniques."""
    slides_cfg = {s.get("slide"): s for s in plan.get("slides", []) if isinstance(s, dict)}
    for s_idx in sorted(slides_cfg.keys()):
        if s_idx <= 1 or s_idx > len(slide_roots):
            continue
        s_cfg = slides_cfg[s_idx]
        tr = s_cfg.get("transition") or {}
        if tr.get("type") != "morph":
            continue
        prev_root = slide_roots[s_idx - 2]
        cur_root = slide_roots[s_idx - 1]
        prev_objs = [o for o in extract_objects(prev_root, slide_w, slide_h) if o.get("geometry")]
        cur_objs = [o for o in extract_objects(cur_root, slide_w, slide_h) if o.get("geometry")]

        # 1. PRE-STAGE: Clone incoming targets from cur_root onto prev_root
        for g_idx, rule in enumerate(tr.get("pre_stage", [])):
            targets = _resolve_targets(cur_objs, rule.get("targets", []))
            if not targets:
                continue
            mode = rule.get("mode", "off-left")
            scale = float(rule.get("scale", 1.0 if mode.startswith("off-") else 0.12))
            alpha = float(rule.get("alpha", 1.0 if mode.startswith("off-") else 0.02))
            margin = float(rule.get("margin", 0.18))
            stagger_dist = float(rule.get("stagger_dist", 0.0))
            stagger_parts = bool(rule.get("stagger_parts", False))

            min_x = min(o["geometry"]["x"] for o in targets)
            min_y = min(o["geometry"]["y"] for o in targets)
            max_x = max(o["geometry"]["x"] + o["geometry"]["w"] for o in targets)
            max_y = max(o["geometry"]["y"] + o["geometry"]["h"] for o in targets)
            grp_cx = 0.5 * (min_x + max_x)
            grp_cy = 0.5 * (min_y + max_y)
            grp_w = max_x - min_x
            grp_h = max_y - min_y

            portal_cx, portal_cy = grp_cx, grp_cy
            portal_name = rule.get("portal")
            if portal_name:
                p_matches = _resolve_targets(prev_objs, [portal_name])
                if p_matches:
                    pg = p_matches[0]["geometry"]
                    portal_cx = pg["x"] + 0.5 * pg["w"]
                    portal_cy = pg["y"] + 0.5 * pg["h"]

            prev_tree = prev_root.find(".//p:spTree", NS)
            max_id = max([int(c.get("id", "1")) for c in prev_root.findall(".//p:cNvPr", NS) if c.get("id", "").isdigit()] + [100])

            for i, o in enumerate(targets):
                orig_name = o["name"]
                m_name = orig_name if orig_name.startswith("!!") else f"!!__stage_{orig_name}"
                c_nv = o["node"].find(".//p:cNvPr", NS)
                if c_nv is not None:
                    c_nv.set("name", m_name)

                clone = copy.deepcopy(o["node"])
                max_id += 1
                c_nv_clone = clone.find(".//p:cNvPr", NS)
                if c_nv_clone is not None:
                    c_nv_clone.set("id", str(max_id))
                    c_nv_clone.set("name", m_name)

                g = o["geometry"]
                ocx = g["x"] + 0.5 * g["w"]
                ocy = g["y"] + 0.5 * g["h"]
                step = (i * stagger_dist) if (stagger_parts or len(targets) > 1) else 0.0

                if mode == "off-left":
                    shift_x = -(max_x + margin + step)
                    nx, ny, nw, nh = g["x"] + shift_x, g["y"], g["w"] * scale, g["h"] * scale
                elif mode == "off-right":
                    shift_x = (1.0 - min_x) + margin + step
                    nx, ny, nw, nh = g["x"] + shift_x, g["y"], g["w"] * scale, g["h"] * scale
                elif mode == "off-top":
                    shift_y = -(max_y + margin + step)
                    nx, ny, nw, nh = g["x"], g["y"] + shift_y, g["w"] * scale, g["h"] * scale
                elif mode == "off-bottom":
                    shift_y = (1.0 - min_y) + margin + step
                    nx, ny, nw, nh = g["x"], g["y"] + shift_y, g["w"] * scale, g["h"] * scale
                elif mode == "portal-seed":
                    nw, nh = g["w"] * scale, g["h"] * scale
                    ncx = portal_cx + (ocx - grp_cx) * scale
                    ncy = portal_cy + (ocy - grp_cy) * scale
                    nx, ny = ncx - 0.5 * nw, ncy - 0.5 * nh
                elif mode == "telescopic-stack":
                    nw, nh = g["w"] * scale, g["h"] * scale
                    nx, ny = portal_cx - 0.5 * nw, portal_cy - 0.5 * nh
                else:
                    nx, ny, nw, nh = g["x"], g["y"], g["w"], g["h"]

                _set_shape_geometry_norm(clone, nx, ny, nw, nh, slide_w, slide_h)
                if alpha < 0.999:
                    _set_shape_alpha(clone, alpha)
                if mode in ("portal-seed", "telescopic-stack"):
                    prev_tree.insert(min(3, len(prev_tree)), clone)
                else:
                    prev_tree.append(clone)

        # 2. POST-STAGE: Clone outgoing targets from prev_root onto cur_root
        prev_objs = [o for o in extract_objects(prev_root, slide_w, slide_h) if o.get("geometry")]
        for g_idx, rule in enumerate(tr.get("post_stage", [])):
            targets = _resolve_targets(prev_objs, rule.get("targets", []))
            if not targets:
                continue
            mode = rule.get("mode", "off-left")
            scale = float(rule.get("scale", 0.20 if mode == "corner-badge" else 1.0))
            alpha = float(rule.get("alpha", 0.42 if mode == "corner-badge" else 0.0))
            margin = float(rule.get("margin", 0.18))
            stagger_dist = float(rule.get("stagger_dist", 0.0))
            target_x = float(rule.get("target_x", 0.88))
            target_y = float(rule.get("target_y", 0.14))

            min_x = min(o["geometry"]["x"] for o in targets)
            min_y = min(o["geometry"]["y"] for o in targets)
            max_x = max(o["geometry"]["x"] + o["geometry"]["w"] for o in targets)
            max_y = max(o["geometry"]["y"] + o["geometry"]["h"] for o in targets)
            grp_cx = 0.5 * (min_x + max_x)
            grp_cy = 0.5 * (min_y + max_y)

            cur_tree = cur_root.find(".//p:spTree", NS)
            max_id = max([int(c.get("id", "1")) for c in cur_root.findall(".//p:cNvPr", NS) if c.get("id", "").isdigit()] + [100])

            for i, o in enumerate(targets):
                orig_name = o["name"]
                m_name = orig_name if orig_name.startswith("!!") else f"!!__stage_{orig_name}"
                c_nv = o["node"].find(".//p:cNvPr", NS)
                if c_nv is not None:
                    c_nv.set("name", m_name)

                clone = copy.deepcopy(o["node"])
                max_id += 1
                c_nv_clone = clone.find(".//p:cNvPr", NS)
                if c_nv_clone is not None:
                    c_nv_clone.set("id", str(max_id))
                    c_nv_clone.set("name", m_name)

                g = o["geometry"]
                ocx = g["x"] + 0.5 * g["w"]
                ocy = g["y"] + 0.5 * g["h"]
                step = i * stagger_dist

                if mode == "off-left":
                    shift_x = -(max_x + margin + step)
                    nx, ny, nw, nh = g["x"] + shift_x, g["y"], g["w"] * scale, g["h"] * scale
                elif mode == "off-right":
                    shift_x = (1.0 - min_x) + margin + step
                    nx, ny, nw, nh = g["x"] + shift_x, g["y"], g["w"] * scale, g["h"] * scale
                elif mode == "off-top":
                    shift_y = -(max_y + margin + step)
                    nx, ny, nw, nh = g["x"], g["y"] + shift_y, g["w"] * scale, g["h"] * scale
                elif mode == "off-bottom":
                    shift_y = (1.0 - min_y) + margin + step
                    nx, ny, nw, nh = g["x"], g["y"] + shift_y, g["w"] * scale, g["h"] * scale
                elif mode == "corner-badge":
                    nw, nh = g["w"] * scale, g["h"] * scale
                    ncx = target_x + (ocx - grp_cx) * scale
                    ncy = target_y + (ocy - grp_cy) * scale
                    nx, ny = ncx - 0.5 * nw, ncy - 0.5 * nh
                else:
                    nx, ny, nw, nh = g["x"], g["y"], g["w"], g["h"]

                _set_shape_geometry_norm(clone, nx, ny, nw, nh, slide_w, slide_h)
                if alpha < 0.999:
                    _set_shape_alpha(clone, alpha)
                if mode == "corner-badge":
                    cur_tree.append(clone)
                else:
                    cur_tree.insert(min(3, len(cur_tree)), clone)
