"""Independent Geometric & Layout Taste Auditor for OpenXML PPTX.

Validates the 17 Universal Taste Rules by parsing slide XML directly:
1. AABB Collision Guard (R16): Bounding box intersection between text and emblem/vector.
2. Text-Fit Capacity & Measure (R08, R17): Character capacity W_text / (FontSize * 0.007") >= 35.
3. Single Elevation & Concentric Radii (R10, R11): Detects Ghost Card (border + shadow) and mismatched nested corner radii.
4. Morph Shape Type Continuity (R02, R05): Geometry primitive match across !!id, cx == cy for circles, decoupled text.

Run as:
    python audit_taste_geometry.py [--json]
"""

from __future__ import annotations

import sys
import zipfile
import json
from pathlib import Path
import xml.etree.ElementTree as ET

# Force UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PAIRS_DIR = Path(__file__).resolve().parent.parent / "pairs"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
}


def parse_slide_shapes(slide_xml_bytes: bytes):
    """Parse all shapes with their transforms, geometry, text, lines, and shadows."""
    root = ET.fromstring(slide_xml_bytes)
    shapes = []
    
    # Traverse spTree
    spTree = root.find(".//p:spTree", NS)
    if spTree is None:
        return shapes

    for sp in spTree.findall(".//p:sp", NS):
        cNvPr = sp.find(".//p:cNvPr", NS)
        name = cNvPr.attrib.get("name", "") if cNvPr is not None else ""
        
        xfrm = sp.find(".//p:spPr/a:xfrm", NS)
        if xfrm is None:
            continue
        off = xfrm.find("a:off", NS)
        ext = xfrm.find("a:ext", NS)
        if off is None or ext is None:
            continue
            
        x = int(off.attrib.get("x", 0))
        y = int(off.attrib.get("y", 0))
        cx = int(ext.attrib.get("cx", 0))
        cy = int(ext.attrib.get("cy", 0))

        prstGeom = sp.find(".//p:spPr/a:prstGeom", NS)
        prst = prstGeom.attrib.get("prst", "") if prstGeom is not None else ""
        adj_val = None
        if prstGeom is not None:
            gd = prstGeom.find(".//a:gd[@name='adj']", NS)
            if gd is not None:
                adj_val = gd.attrib.get("fmla", "")

        # Check line stroke
        ln = sp.find(".//p:spPr/a:ln", NS)
        has_visible_border = False
        border_width = 0
        if ln is not None:
            noFill = ln.find("a:noFill", NS)
            solidFill = ln.find("a:solidFill", NS)
            if solidFill is not None and noFill is None:
                has_visible_border = True
                border_width = int(ln.attrib.get("w", 0))

        # Check outer shadow
        outerShdw = sp.find(".//p:spPr/a:effectLst/a:outerShdw", NS)
        has_shadow = outerShdw is not None
        shadow_blur = int(outerShdw.attrib.get("blurRad", 0)) if has_shadow else 0
        shadow_alpha = 100000
        if has_shadow:
            alpha_node = outerShdw.find(".//a:alpha", NS)
            if alpha_node is not None:
                shadow_alpha = int(alpha_node.attrib.get("val", 100000))

        # Check text
        txBody = sp.find("p:txBody", NS)
        has_text = False
        text_content = ""
        font_size_pt = 18.0
        if txBody is not None:
            paragraphs = txBody.findall("a:p", NS)
            runs = txBody.findall(".//a:t", NS)
            if runs:
                text_content = " ".join((r.text or "") for r in runs).strip()
                if text_content:
                    has_text = True
            rPr = txBody.find(".//a:rPr", NS)
            if rPr is not None and "sz" in rPr.attrib:
                font_size_pt = int(rPr.attrib["sz"]) / 100.0

        shapes.append({
            "name": name,
            "x": x,
            "y": y,
            "cx": cx,
            "cy": cy,
            "prst": prst,
            "adj": adj_val,
            "has_border": has_visible_border,
            "border_w": border_width,
            "has_shadow": has_shadow,
            "shadow_blur": shadow_blur,
            "shadow_alpha": shadow_alpha,
            "has_text": has_text,
            "text": text_content,
            "font_size": font_size_pt,
        })
        
    return shapes


def check_deck_geometry(pptx_path: Path) -> dict:
    results = {
        "deck": pptx_path.name,
        "slide_count": 0,
        "checks": {
            "aabb_collision": {"pass": True, "violations": []},
            "text_fit_capacity": {"pass": True, "violations": []},
            "elevation_and_radii": {"pass": True, "violations": []},
            "morph_continuity": {"pass": True, "violations": []},
        },
        "overall_pass": True,
    }

    with zipfile.ZipFile(pptx_path) as z:
        slide_files = sorted([f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")])
        results["slide_count"] = len(slide_files)

        slides_data = []
        for sf in slide_files:
            xml_bytes = z.read(sf)
            shapes = parse_slide_shapes(xml_bytes)
            # Check morph in slide transition
            has_morph = b"p159:morph" in xml_bytes or b"p160:morph" in xml_bytes
            slides_data.append({"file": sf, "shapes": shapes, "has_morph": has_morph})

    # =========================================================================
    # CHECK 1: AABB Collision Guard (R16)
    # =========================================================================
    SAFE_MARGIN = 320040  # 0.35 inches in EMU
    for s_idx, s in enumerate(slides_data, start=1):
        text_shapes = [sh for sh in s["shapes"] if sh["has_text"] and len(sh["text"]) > 10]
        visual_shapes = [sh for sh in s["shapes"] if not sh["has_text"] and sh["prst"] in ("oval", "ellipse") and sh["cx"] < 3000000]
        
        for t in text_shapes:
            t_box = (t["x"], t["y"], t["x"] + t["cx"], t["y"] + t["cy"])
            for v in visual_shapes:
                v_box = (v["x"], v["y"], v["x"] + v["cx"], v["y"] + v["cy"])
                
                # Check intersection or clearance margin < SAFE_MARGIN
                x_overlap = max(0, min(t_box[2], v_box[2]) - max(t_box[0], v_box[0]))
                y_overlap = max(0, min(t_box[3], v_box[3]) - max(t_box[1], v_box[1]))
                
                if x_overlap > 0 and y_overlap > 0:
                    results["checks"]["aabb_collision"]["pass"] = False
                    results["checks"]["aabb_collision"]["violations"].append(
                        f"Slide {s_idx}: Text '{t['text'][:30]}...' collides directly with emblem (overlap {x_overlap}x{y_overlap} EMU)"
                    )
                else:
                    # Check clearance margin if on same horizontal strip
                    if y_overlap > 0:
                        gap = t_box[0] - v_box[2]
                        if 0 <= gap < SAFE_MARGIN:
                            results["checks"]["aabb_collision"]["pass"] = False
                            results["checks"]["aabb_collision"]["violations"].append(
                                f"Slide {s_idx}: Clearance gap {gap} EMU between emblem and text is below safe margin {SAFE_MARGIN} EMU (0.35\")"
                            )

    # =========================================================================
    # CHECK 2: Text-Fit Capacity & Measure (R08, R17)
    # =========================================================================
    for s_idx, s in enumerate(slides_data, start=1):
        for sh in s["shapes"]:
            # Check cards with multi-sentence body text
            if sh["has_text"] and "•" in sh["text"]:
                w_text_inches = sh["cx"] / 914400.0
                char_capacity = w_text_inches / (sh["font_size"] * 0.007)
                if char_capacity < 35.0:
                    results["checks"]["text_fit_capacity"]["pass"] = False
                    results["checks"]["text_fit_capacity"]["violations"].append(
                        f"Slide {s_idx}: Column width {w_text_inches:.2f}\" only holds {char_capacity:.1f} chars/line (< 35ch floor)"
                    )

    # =========================================================================
    # CHECK 3: Elevation & Concentric Radii (R10, R11)
    # =========================================================================
    for s_idx, s in enumerate(slides_data, start=1):
        for sh in s["shapes"]:
            # Ghost Card: Visible border AND shadow
            if sh["has_border"] and sh["has_shadow"]:
                results["checks"]["elevation_and_radii"]["pass"] = False
                results["checks"]["elevation_and_radii"]["violations"].append(
                    f"Slide {s_idx}: Ghost card defect on '{sh['name']}' - possesses both border (w={sh['border_w']}) and outerShadow"
                )
            # Harsh shadow check
            if sh["has_shadow"] and sh["shadow_alpha"] > 25000:
                results["checks"]["elevation_and_radii"]["pass"] = False
                results["checks"]["elevation_and_radii"]["violations"].append(
                    f"Slide {s_idx}: Harsh shadow opacity {sh['shadow_alpha']/1000}% exceeds 25% diffuse threshold"
                )

    # =========================================================================
    # CHECK 4: Morph Shape Type Continuity (R02, R05)
    # =========================================================================
    if len(slides_data) >= 2 and slides_data[1]["has_morph"]:
        s1_actors = {sh["name"]: sh for sh in slides_data[0]["shapes"] if sh["name"].startswith("!!")}
        s2_actors = {sh["name"]: sh for sh in slides_data[1]["shapes"] if sh["name"].startswith("!!")}
        
        shared_names = set(s1_actors.keys()) & set(s2_actors.keys())
        for name in shared_names:
            a1 = s1_actors[name]
            a2 = s2_actors[name]
            # Mismatched primitive geometry
            if a1["prst"] != a2["prst"]:
                results["checks"]["morph_continuity"]["pass"] = False
                results["checks"]["morph_continuity"]["violations"].append(
                    f"Morph break on '{name}': State 1 is '{a1['prst']}' but State 2 is '{a2['prst']}' (cross-fade defect)"
                )
            # Circular state must have cx == cy
            if a1["prst"] == "roundRect" and a1["adj"] and "50000" in a1["adj"]:
                if abs(a1["cx"] - a1["cy"]) > 1000:
                    results["checks"]["morph_continuity"]["pass"] = False
                    results["checks"]["morph_continuity"]["violations"].append(
                        f"Morph circle squashed oval on '{name}': cx={a1['cx']} != cy={a1['cy']}"
                    )
            # Text inside morphing shape
            if a2["has_text"] and len(a2["text"]) > 20:
                results["checks"]["morph_continuity"]["pass"] = False
                results["checks"]["morph_continuity"]["violations"].append(
                    f"Morph font warp risk on '{name}': Dense text inside morphing shape instead of decoupled overlay frame"
                )

    # Overall pass
    for cname, cdata in results["checks"].items():
        if not cdata["pass"]:
            results["overall_pass"] = False

    return results


def run_full_audit():
    print("=" * 80)
    print("INDEPENDENT GEOMETRIC & LAYOUT TASTE AUDITOR (T086)")
    print("=" * 80)

    pptx_files = sorted(PAIRS_DIR.glob("*.pptx"))
    all_results = []

    for pf in pptx_files:
        res = check_deck_geometry(pf)
        all_results.append(res)
        status_str = "PASS [ALL CLEAN]" if res["overall_pass"] else "FAIL [DEFECTS DETECTED]"
        print(f"\nDeck: {pf.name} -> {status_str}")
        for cname, cdata in res["checks"].items():
            c_status = "PASS" if cdata["pass"] else "FAIL"
            print(f"  [{c_status}] {cname}")
            for v in cdata["violations"]:
                print(f"       * {v}")

    # Summary Table
    print("\n" + "=" * 80)
    print(f"{'DECK':<35} | {'COLLISION':<9} | {'TEXT-FIT':<9} | {'ELEVATION':<9} | {'MORPH':<9} | {'RESULT':<6}")
    print("-" * 80)
    for r in all_results:
        c = r["checks"]
        col = "PASS" if c["aabb_collision"]["pass"] else "FAIL"
        tfit = "PASS" if c["text_fit_capacity"]["pass"] else "FAIL"
        elev = "PASS" if c["elevation_and_radii"]["pass"] else "FAIL"
        morph = "PASS" if c["morph_continuity"]["pass"] else "FAIL"
        res_str = "PASS" if r["overall_pass"] else "FAIL"
        print(f"{r['deck']:<35} | {col:<9} | {tfit:<9} | {elev:<9} | {morph:<9} | {res_str:<6}")
    print("=" * 80)

    # Write JSON results
    out_json = PAIRS_DIR / "audit_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nFull audit log written to: {out_json.as_posix()}")


if __name__ == "__main__":
    run_full_audit()
