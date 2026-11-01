#!/usr/bin/env python3
"""Slide Navigator — Non-Linear Slide Navigation, Branching & Mini-Game State Machine (T048, pptx).

Empowers AI agents to build non-linear, interactive presentations and mini-games in PowerPoint:
1. Inter-Slide Named Hyperlinks: Jumps from any shape/card to a specific target slide (ISO/IEC 29500 DrawingML).
2. Dynamic Return Paths ("Quay về kể tiếp"): Action 'last_viewed' (ppaction://hlinkshowjump?jump=lastslideviewed)
   returning the presenter/viewer to the calling slide regardless of where the auxiliary slide was invoked.
3. Custom Show Branching: Named slide show sequences (p:custShowLst) with 'Show and Return'
   (action="ppaction://customshow?id=...&return=true") automatically returning after the branch ends.
4. Non-Linear Interaction Enforcement:
   - Slide transition lock: advClick="0" preventing accidental mouse-click advances.
   - Kiosk mode: <p:kiosk restart="4294967295"/> restricting presentation progression exclusively to interactive buttons.
5. Mini-Game State Machine: Branching quizzes, decision trees, escape rooms, and interactive dashboards.
6. Navigation Graph Inspection: Analyzes any PPTX, discovers all interactive links, detects dead ends,
   and outputs a directed graph (JSON + Mermaid).

CLI:
    python scripts/slide_navigator.py inspect deck.pptx
    python scripts/slide_navigator.py apply deck.pptx --recipe nav_recipe.json -o out.pptx
    python scripts/slide_navigator.py lock deck.pptx -o out.pptx
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import zipfile

from lxml import etree as ET

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

NAMESPACES = {
    "p": NS_P,
    "a": NS_A,
    "r": NS_R,
    "rel": NS_REL,
}

SPECIAL_ACTIONS = {
    "last_viewed": "ppaction://hlinkshowjump?jump=lastslideviewed",
    "next_slide": "ppaction://hlinkshowjump?jump=nextslide",
    "previous_slide": "ppaction://hlinkshowjump?jump=previousslide",
    "first_slide": "ppaction://hlinkshowjump?jump=firstslide",
    "last_slide": "ppaction://hlinkshowjump?jump=lastslide",
    "end_show": "ppaction://hlinkshowjump?jump=endshow",
}


def _natural_sort_key(s: str) -> list[int | str]:
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", s)]


def _find_shape_cnvpr(slide_tree: ET._Element, shape_identifier: str | int) -> ET._Element | None:
    """Locate the <p:cNvPr> element of a shape by its numeric ID, name, or text content."""
    for sp in slide_tree.findall(".//p:sp", namespaces=NAMESPACES):
        cnvpr = sp.find(".//p:nvSpPr/p:cNvPr", namespaces=NAMESPACES)
        if cnvpr is None:
            continue
        sp_id = cnvpr.get("id")
        sp_name = cnvpr.get("name", "")

        # Match by ID or Name
        if str(shape_identifier) == str(sp_id) or str(shape_identifier).lower() == sp_name.lower():
            return cnvpr

        # Match by text content inside shape
        texts = [t.text for t in sp.findall(".//a:t", namespaces=NAMESPACES) if t.text]
        full_text = " ".join(texts).strip()
        if str(shape_identifier).lower() in full_text.lower():
            return cnvpr

    return None


def inspect_navigation_graph(pptx_path: str | Path) -> dict[str, Any]:
    """Inspect and extract the full interactive navigation graph of a presentation.

    Returns nodes (slides), edges (interactive hyperlinks), dead ends, and Mermaid diagram.
    """
    p = Path(pptx_path)
    if not p.exists():
        raise FileNotFoundError(f"Presentation not found: {pptx_path}")

    with zipfile.ZipFile(p, "r") as z:
        namelist = z.namelist()

        # Find presentation properties
        kiosk_mode = False
        if "ppt/presProps.xml" in namelist:
            pp_tree = ET.fromstring(z.read("ppt/presProps.xml"))
            kiosk_node = pp_tree.find(".//p:kiosk", namespaces=NAMESPACES)
            kiosk_mode = kiosk_node is not None

        # Discover custom shows in presentation.xml
        custom_shows = []
        if "ppt/presentation.xml" in namelist:
            p_tree = ET.fromstring(z.read("ppt/presentation.xml"))
            for cs in p_tree.findall(".//p:custShow", namespaces=NAMESPACES):
                cs_name = cs.get("name")
                cs_id = cs.get("id")
                slide_rids = [s.get(f"{{{NS_R}}}id") for s in cs.findall(".//p:sld", namespaces=NAMESPACES)]
                custom_shows.append({
                    "id": cs_id,
                    "name": cs_name,
                    "slide_rids": slide_rids,
                })

        # Slide relationship map from ppt/_rels/presentation.xml.rels
        p_rels_tree = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
        rid_to_slide_file = {}
        for r in p_rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
            target = r.get("Target", "")
            if "slides/slide" in target:
                rid_to_slide_file[r.get("Id")] = target.split("/")[-1]

        # Order of slides from presentation.xml
        slide_order_files = []
        p_tree = ET.fromstring(z.read("ppt/presentation.xml"))
        for sld_id in p_tree.findall(".//p:sldIdLst/p:sldId", namespaces=NAMESPACES):
            rid = sld_id.get(f"{{{NS_R}}}id")
            if rid in rid_to_slide_file:
                slide_order_files.append(rid_to_slide_file[rid])

        slide_file_to_index = {fname: idx for idx, fname in enumerate(slide_order_files)}

        # Parse each slide
        nodes = []
        edges = []
        dead_ends = []

        for idx, slide_file in enumerate(slide_order_files):
            slide_path = f"ppt/slides/{slide_file}"
            s_tree = ET.fromstring(z.read(slide_path))

            # Slide transition
            trans = s_tree.find(".//p:transition", namespaces=NAMESPACES)
            adv_click = True
            if trans is not None and trans.get("advClick") == "0":
                adv_click = False

            # Slide title
            title_nodes = s_tree.xpath(".//p:sp[.//p:ph[@type='title' or @type='ctrTitle']]//a:t", namespaces=NAMESPACES)
            if not title_nodes:
                title_nodes = s_tree.xpath(".//p:sp//a:t", namespaces=NAMESPACES)
            title_node = title_nodes[0] if title_nodes else None
            slide_title = title_node.text.strip() if title_node is not None and title_node.text else f"Slide {idx + 1}"

            # Slide relationships
            rels_path = f"ppt/slides/_rels/{slide_file}.rels"
            slide_rels = {}
            if rels_path in namelist:
                s_rels_tree = ET.fromstring(z.read(rels_path))
                for r in s_rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
                    slide_rels[r.get("Id")] = r.get("Target")

            # Collect interactive links on this slide
            slide_buttons = []
            for sp in s_tree.findall(".//p:sp", namespaces=NAMESPACES):
                cnvpr = sp.find(".//p:nvSpPr/p:cNvPr", namespaces=NAMESPACES)
                if cnvpr is None:
                    continue
                hlink = cnvpr.find("a:hlinkClick", namespaces=NAMESPACES)
                if hlink is None:
                    # Also check paragraph/run level hyperlinks
                    hlink = sp.find(".//a:rPr/a:hlinkClick", namespaces=NAMESPACES)

                if hlink is not None:
                    action_uri = hlink.get("action", "")
                    target_rid = hlink.get(f"{{{NS_R}}}id")
                    sp_name = cnvpr.get("name", "Shape")
                    texts = [t.text for t in sp.findall(".//a:t", namespaces=NAMESPACES) if t.text]
                    label = " ".join(texts).strip() or sp_name

                    target_type = "unknown"
                    target_dest = None

                    if "hlinksldjump" in action_uri and target_rid:
                        target_file = slide_rels.get(target_rid)
                        if target_file:
                            base_target = Path(target_file).name
                            target_dest = slide_file_to_index.get(base_target)
                            target_type = "slide_jump"
                    elif "lastslideviewed" in action_uri:
                        target_type = "last_viewed"
                        target_dest = "LAST_VIEWED"
                    elif "firstslide" in action_uri:
                        target_type = "first_slide"
                        target_dest = 0
                    elif "lastslide" in action_uri:
                        target_type = "last_slide"
                        target_dest = len(slide_order_files) - 1
                    elif "nextslide" in action_uri:
                        target_type = "next_slide"
                        target_dest = idx + 1 if idx + 1 < len(slide_order_files) else None
                    elif "previousslide" in action_uri:
                        target_type = "previous_slide"
                        target_dest = idx - 1 if idx > 0 else None
                    elif "endshow" in action_uri:
                        target_type = "end_show"
                        target_dest = "END"
                    elif "customshow" in action_uri:
                        target_type = "custom_show"
                        m = re.search(r"id=(\d+)", action_uri)
                        show_id = m.group(1) if m else "0"
                        return_flag = "return=true" in action_uri
                        target_dest = f"SHOW_{show_id}_RETURN_{return_flag}"

                    btn_info = {
                        "shape_name": sp_name,
                        "label": label,
                        "action_type": target_type,
                        "target": target_dest,
                        "raw_action": action_uri,
                    }
                    slide_buttons.append(btn_info)

                    edges.append({
                        "from_slide": idx,
                        "from_title": slide_title,
                        "to_slide": target_dest,
                        "button_label": label,
                        "type": target_type,
                    })

            # Check if this slide is a dead end
            if not adv_click and not slide_buttons and idx < len(slide_order_files) - 1:
                dead_ends.append({
                    "slide_index": idx,
                    "title": slide_title,
                    "reason": "advClick is 0 and no interactive navigation buttons present",
                })

            nodes.append({
                "slide_index": idx,
                "file": slide_file,
                "title": slide_title,
                "advance_on_click": adv_click,
                "button_count": len(slide_buttons),
                "buttons": slide_buttons,
            })

    # Generate Mermaid diagram
    mermaid_lines = ["graph TD"]
    for n in nodes:
        clean_title = re.sub(r'["\(\)\[\]]', "", n["title"])[:25]
        mermaid_lines.append(f'  S{n["slide_index"]}["Slide {n["slide_index"] + 1}: {clean_title}"]')

    for e in edges:
        from_id = f'S{e["from_slide"]}'
        lbl = re.sub(r'["\(\)\[\]]', "", e["button_label"])[:20]
        if isinstance(e["to_slide"], int):
            to_id = f'S{e["to_slide"]}'
            mermaid_lines.append(f'  {from_id} -->|"{lbl}"| {to_id}')
        else:
            dest_node = str(e["to_slide"]).replace(" ", "_")
            mermaid_lines.append(f'  {from_id} -.->|"{lbl}"| {dest_node}')

    mermaid_str = "\n".join(mermaid_lines)

    return {
        "presentation": str(p),
        "total_slides": len(nodes),
        "kiosk_mode": kiosk_mode,
        "custom_shows": custom_shows,
        "nodes": nodes,
        "edges": edges,
        "dead_ends": dead_ends,
        "is_non_linear": len(edges) > 0 or not all(n["advance_on_click"] for n in nodes),
        "mermaid": mermaid_str,
    }


def configure_interactive_navigation(
    pptx_path: str | Path,
    recipe: dict[str, Any],
    *,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Apply a declarative interactive navigation recipe to a PPTX presentation.

    Supports:
    - Setting kiosk mode & advanceOnClick lock
    - Inter-slide jumps
    - Return paths ('last_viewed')
    - Custom show branching with automatic return
    """
    p = Path(pptx_path)
    if not p.exists():
        raise FileNotFoundError(f"Presentation not found: {pptx_path}")

    out_file = Path(output_path) if output_path else p

    with zipfile.ZipFile(p, "r") as zin:
        in_files = {name: zin.read(name) for name in zin.namelist()}

    # 1. Slide order and mapping
    p_rels_tree = ET.fromstring(in_files["ppt/_rels/presentation.xml.rels"])
    rid_to_slide_file = {}
    for r in p_rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
        target = r.get("Target", "")
        if "slides/slide" in target:
            rid_to_slide_file[r.get("Id")] = target.split("/")[-1]

    p_tree = ET.fromstring(in_files["ppt/presentation.xml"])
    slide_order_files = []
    slide_file_to_rid = {}
    for sld_id in p_tree.findall(".//p:sldIdLst/p:sldId", namespaces=NAMESPACES):
        rid = sld_id.get(f"{{{NS_R}}}id")
        if rid in rid_to_slide_file:
            sfile = rid_to_slide_file[rid]
            slide_order_files.append(sfile)
            slide_file_to_rid[sfile] = rid

    total_slides = len(slide_order_files)

    # 2. Configure Kiosk Mode in presProps.xml if requested
    if recipe.get("kiosk_mode", False):
        pp_xml = in_files["ppt/presProps.xml"]
        tree_pp = ET.fromstring(pp_xml)
        show_pr = tree_pp.find(".//p:showPr", namespaces=NAMESPACES)
        if show_pr is None:
            show_pr = ET.Element(f"{{{NS_P}}}showPr")
            # Insert before extLst (schema order!)
            extLst = tree_pp.find(".//p:extLst", namespaces=NAMESPACES)
            if extLst is not None:
                extLst.addprevious(show_pr)
            else:
                tree_pp.insert(0, show_pr)
        if show_pr.find("p:kiosk", namespaces=NAMESPACES) is None:
            ET.SubElement(show_pr, f"{{{NS_P}}}kiosk", restart="4294967295")
        if show_pr.find("p:sldAll", namespaces=NAMESPACES) is None:
            ET.SubElement(show_pr, f"{{{NS_P}}}sldAll")
        in_files["ppt/presProps.xml"] = ET.tostring(tree_pp, xml_declaration=True, encoding="UTF-8", standalone=True)

    # 3. Configure advanceOnClick on slides
    lock_all_clicks = recipe.get("lock_advance_on_click", False)
    per_slide_locks = recipe.get("slide_advance_locks", {})

    for idx, sfile in enumerate(slide_order_files):
        spath = f"ppt/slides/{sfile}"
        stree = ET.fromstring(in_files[spath])

        should_lock = lock_all_clicks or per_slide_locks.get(str(idx), False) or per_slide_locks.get(idx, False)
        if should_lock:
            trans = stree.find(".//p:transition", namespaces=NAMESPACES)
            if trans is None:
                timing = stree.find(".//p:timing", namespaces=NAMESPACES)
                trans = ET.Element(f"{{{NS_P}}}transition", advClick="0")
                if timing is not None:
                    timing.addprevious(trans)
                else:
                    stree.append(trans)
            else:
                trans.set("advClick", "0")
            in_files[spath] = ET.tostring(stree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # 4. Configure Custom Shows if present
    custom_shows_spec = recipe.get("custom_shows", [])
    if custom_shows_spec:
        custShowLst = p_tree.find(".//p:custShowLst", namespaces=NAMESPACES)
        if custShowLst is None:
            custShowLst = ET.Element(f"{{{NS_P}}}custShowLst")
            # Insert before defaultTextStyle according to schema sequence
            dts = p_tree.find(".//p:defaultTextStyle", namespaces=NAMESPACES)
            if dts is not None:
                dts.addprevious(custShowLst)
            else:
                extLst = p_tree.find(".//p:extLst", namespaces=NAMESPACES)
                if extLst is not None:
                    extLst.addprevious(custShowLst)
                else:
                    p_tree.append(custShowLst)

        for show_idx, cs_def in enumerate(custom_shows_spec):
            show_name = cs_def["name"]
            show_id = str(cs_def.get("id", show_idx))
            custShow = ET.SubElement(custShowLst, f"{{{NS_P}}}custShow", name=show_name, id=show_id)
            sldLst = ET.SubElement(custShow, f"{{{NS_P}}}sldLst")
            for target_idx in cs_def["slides"]:
                if target_idx < total_slides:
                    target_sfile = slide_order_files[target_idx]
                    target_rid = slide_file_to_rid[target_sfile]
                    ET.SubElement(sldLst, f"{{{NS_P}}}sld", {f"{{{NS_R}}}id": target_rid})

        in_files["ppt/presentation.xml"] = ET.tostring(p_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # 5. Wire navigation buttons
    nav_links = recipe.get("navigation", [])
    applied_links = []

    for item in nav_links:
        src_slide_idx = item["slide"]
        if src_slide_idx >= total_slides:
            continue
        src_file = slide_order_files[src_slide_idx]
        src_path = f"ppt/slides/{src_file}"
        src_rels_path = f"ppt/slides/_rels/{src_file}.rels"

        stree = ET.fromstring(in_files[src_path])
        cnvpr = _find_shape_cnvpr(stree, item["shape_identifier"])
        if cnvpr is None:
            continue

        # Remove existing hlinkClick if any
        existing_hlink = cnvpr.find("a:hlinkClick", namespaces=NAMESPACES)
        if existing_hlink is not None:
            cnvpr.remove(existing_hlink)

        action_type = item["action"]

        if action_type in SPECIAL_ACTIONS:
            action_uri = SPECIAL_ACTIONS[action_type]
            ET.SubElement(cnvpr, f"{{{NS_A}}}hlinkClick", action=action_uri)
            applied_links.append({
                "from_slide": src_slide_idx,
                "shape": item["shape_identifier"],
                "action": action_type,
                "uri": action_uri,
            })

        elif action_type == "jump_to_slide":
            target_slide_idx = item["target"]
            if target_slide_idx >= total_slides:
                continue
            target_file = slide_order_files[target_slide_idx]

            # Ensure relationship in slide rels
            if src_rels_path not in in_files:
                rels_tree = ET.Element(f"{{{NS_REL}}}Relationships")
            else:
                rels_tree = ET.fromstring(in_files[src_rels_path])

            rel_id = None
            for rel in rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
                if rel.get("Target") == target_file:
                    rel_id = rel.get("Id")
                    break

            if not rel_id:
                rel_id = f"rId{len(rels_tree) + 10}"
                ET.SubElement(
                    rels_tree,
                    f"{{{NS_REL}}}Relationship",
                    Id=rel_id,
                    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
                    Target=target_file,
                )
                in_files[src_rels_path] = ET.tostring(rels_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

            action_uri = "ppaction://hlinksldjump"
            ET.SubElement(cnvpr, f"{{{NS_A}}}hlinkClick", {f"{{{NS_R}}}id": rel_id}, action=action_uri)
            applied_links.append({
                "from_slide": src_slide_idx,
                "shape": item["shape_identifier"],
                "action": "jump_to_slide",
                "target_slide": target_slide_idx,
                "rel_id": rel_id,
            })

        elif action_type == "custom_show":
            show_id = str(item.get("show_id", 0))
            return_flag = "true" if item.get("return_after", True) else "false"
            action_uri = f"ppaction://customshow?id={show_id}&return={return_flag}"
            ET.SubElement(cnvpr, f"{{{NS_A}}}hlinkClick", action=action_uri)
            applied_links.append({
                "from_slide": src_slide_idx,
                "shape": item["shape_identifier"],
                "action": "custom_show",
                "show_id": show_id,
                "return_after": return_flag == "true",
            })

        in_files[src_path] = ET.tostring(stree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Save output
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in in_files.items():
            zout.writestr(name, content)

    # Re-inspect to produce audit
    audit = inspect_navigation_graph(out_file)

    return {
        "ok": True,
        "output_file": str(out_file),
        "kiosk_mode": audit["kiosk_mode"],
        "applied_links_count": len(applied_links),
        "applied_links": applied_links,
        "dead_ends": audit["dead_ends"],
        "mermaid": audit["mermaid"],
    }


def compile_hub_and_spoke_deck(
    pptx_path: str | Path,
    hub_slide_idx: int,
    spoke_mappings: list[dict[str, Any]],
    *,
    return_button_identifier: str = "Return",
    lock_linear_advance: bool = True,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Helper: wire a Hub-and-Spoke navigation structure across a deck."""
    nav = []
    for item in spoke_mappings:
        # Link from hub to topic
        nav.append({
            "slide": hub_slide_idx,
            "shape_identifier": item["hub_button"],
            "action": "jump_to_slide",
            "target": item["target_slide"],
        })
        # Link from topic back to hub
        nav.append({
            "slide": item["target_slide"],
            "shape_identifier": item.get("return_button", return_button_identifier),
            "action": "jump_to_slide",
            "target": hub_slide_idx,
        })

    recipe = {
        "kiosk_mode": lock_linear_advance,
        "lock_advance_on_click": lock_linear_advance,
        "navigation": nav,
    }
    return configure_interactive_navigation(pptx_path, recipe, output_path=output_path)


def compile_mini_game_state_machine(
    pptx_path: str | Path,
    game_spec: dict[str, Any],
    *,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Helper: compile an interactive educational/quiz mini-game state machine."""
    nav = []

    # Start button
    if "start" in game_spec:
        nav.append({
            "slide": game_spec["start"]["slide"],
            "shape_identifier": game_spec["start"]["button"],
            "action": "jump_to_slide",
            "target": game_spec["start"]["first_question"],
        })

    # Questions
    for q in game_spec.get("questions", []):
        q_slide = q["slide"]
        # Correct answer
        nav.append({
            "slide": q_slide,
            "shape_identifier": q["correct_button"],
            "action": "jump_to_slide",
            "target": q["correct_target"],
        })
        # Wrong answers
        for w_btn in q.get("wrong_buttons", []):
            nav.append({
                "slide": q_slide,
                "shape_identifier": w_btn,
                "action": "jump_to_slide",
                "target": q["wrong_target"],
            })

    # Handlers on Wrong Slide (Try again -> last_viewed)
    if "wrong_screens" in game_spec:
        for ws in game_spec["wrong_screens"]:
            if "try_again_button" in ws:
                nav.append({
                    "slide": ws["slide"],
                    "shape_identifier": ws["try_again_button"],
                    "action": "last_viewed",
                })
            if "quit_button" in ws:
                nav.append({
                    "slide": ws["slide"],
                    "shape_identifier": ws["quit_button"],
                    "action": "first_slide",
                })

    # Handlers on Correct / Victory Screens
    if "victory_screen" in game_spec:
        vs = game_spec["victory_screen"]
        if "restart_button" in vs:
            nav.append({
                "slide": vs["slide"],
                "shape_identifier": vs["restart_button"],
                "action": "first_slide",
            })
        if "end_button" in vs:
            nav.append({
                "slide": vs["slide"],
                "shape_identifier": vs["end_button"],
                "action": "end_show",
            })

    recipe = {
        "kiosk_mode": True,
        "lock_advance_on_click": True,
        "navigation": nav,
    }
    return configure_interactive_navigation(pptx_path, recipe, output_path=output_path)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Slide Navigator — Non-Linear Slide Navigation, Branching & Mini-Game State Machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # inspect
    p_ins = sub.add_parser("inspect", help="Inspect presentation navigation graph")
    p_ins.add_argument("pptx", type=Path)
    p_ins.add_argument("--mermaid", action="store_true", help="Print Mermaid diagram only")

    # apply
    p_app = sub.add_parser("apply", help="Apply navigation recipe to presentation")
    p_app.add_argument("pptx", type=Path)
    p_app.add_argument("--recipe", type=Path, required=True)
    p_app.add_argument("-o", "--output", type=Path, default=None)

    # lock
    p_lock = sub.add_parser("lock", help="Lock presentation into Kiosk Mode and disable blank clicks")
    p_lock.add_argument("pptx", type=Path)
    p_lock.add_argument("-o", "--output", type=Path, default=None)

    args = parser.parse_args()

    if args.cmd == "inspect":
        audit = inspect_navigation_graph(args.pptx)
        if args.mermaid:
            print(audit["mermaid"])
        else:
            print(json.dumps(audit, indent=2, ensure_ascii=False))
    elif args.cmd == "apply":
        recipe_data = json.loads(args.recipe.read_text(encoding="utf-8"))
        res = configure_interactive_navigation(args.pptx, recipe_data, output_path=args.output)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "lock":
        recipe = {"kiosk_mode": True, "lock_advance_on_click": True}
        res = configure_interactive_navigation(args.pptx, recipe, output_path=args.output)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
