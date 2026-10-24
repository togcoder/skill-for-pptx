# -*- coding: utf-8 -*-
"""
PPTX Motion Lab — Semantic Interactive Click Triggers (Milestone T033 - Problem 2)
Module: scripts/interactive_triggers.py

Builds ECMA-376 compliant <p:seq> interactive trigger sequences
(nodeType="interactiveSeq"), strips conflicting <a:hlinkClick> nodes,
guarantees strictly increasing TimeNode IDs across mainSeq and interactiveSeq,
and provides round-trip inspection via read_interactive_triggers().
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from scripts.morph_playbook import (
    A_NS,
    NS,
    P_NS,
    _append_subelement,
    _get_cnvpr,
    _local_name,
    _qname,
)

VALID_ACTIONS = frozenset({"reveal", "hide", "highlight", "toggle"})
VALID_PRESETS = frozenset({"zoom", "fade", "float-in", "teeter"})

# Mapping of (action_phase, preset) -> (presetClass, presetID, presetSubtype)
PRESET_METADATA: Dict[Tuple[str, str], Tuple[str, str, str]] = {
    ("entr", "fade"): ("entr", "10", "0"),
    ("entr", "zoom"): ("entr", "23", "16"),
    ("entr", "float-in"): ("entr", "42", "0"),
    ("entr", "teeter"): ("entr", "10", "0"),
    ("exit", "fade"): ("exit", "10", "0"),
    ("exit", "zoom"): ("exit", "23", "32"),
    ("exit", "float-in"): ("exit", "42", "0"),
    ("exit", "teeter"): ("exit", "10", "0"),
    ("emph", "teeter"): ("emph", "14", "0"),
    ("emph", "zoom"): ("emph", "6", "0"),
    ("emph", "fade"): ("emph", "14", "0"),
    ("emph", "float-in"): ("emph", "14", "0"),
}


class TimeNodeIDAllocator:
    """
    Strictly monotonic integer allocator for <p:cTn id="..."> across an entire slide.
    Scans existing <p:cTn> elements so newly generated IDs never collide with mainSeq
    or previously created interactiveSeq nodes.
    """

    def __init__(self, slide_root: ET.Element) -> None:
        max_id = 0
        for ctn in slide_root.findall(".//p:cTn", NS):
            raw = ctn.attrib.get("id")
            if raw is not None:
                try:
                    val = int(raw)
                    if val > max_id:
                        max_id = val
                except ValueError:
                    pass
        self._current: int = max_id

    @property
    def current_max(self) -> int:
        return self._current

    def allocate(self) -> int:
        self._current += 1
        return self._current

    def allocate_str(self) -> str:
        return str(self.allocate())


def _index_slide_shapes(
    slide_root: ET.Element,
    external_map: Optional[Dict[str, Union[int, str]]] = None,
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, ET.Element]]:
    """
    Build lookup maps for shapes on the slide:
      - key_to_spid: maps shape name or stringified ID -> canonical spid string
      - spid_to_name: maps canonical spid string -> shape name
      - spid_to_cnvpr: maps canonical spid string -> p:cNvPr element
    """
    key_to_spid: Dict[str, str] = {}
    spid_to_name: Dict[str, str] = {}
    spid_to_cnvpr: Dict[str, ET.Element] = {}

    for elem in slide_root.iter():
        if _local_name(elem.tag) in ("sp", "pic", "grpSp", "cxnSp", "graphicFrame"):
            cnv = _get_cnvpr(elem)
            if cnv is not None:
                spid = str(cnv.attrib.get("id", "")).strip()
                name = cnv.attrib.get("name", "").strip()
                if spid:
                    key_to_spid[spid] = spid
                    spid_to_name[spid] = name
                    spid_to_cnvpr[spid] = cnv
                    if name:
                        key_to_spid[name] = spid

    if external_map:
        for k, v in external_map.items():
            spid_str = str(v).strip()
            key_to_spid[str(k).strip()] = spid_str
            key_to_spid[spid_str] = spid_str
            if spid_str not in spid_to_name:
                spid_to_name[spid_str] = str(k).strip()

    return key_to_spid, spid_to_name, spid_to_cnvpr


def _strip_hlink_click(cnvpr: Optional[ET.Element]) -> int:
    """
    Remove all <a:hlinkClick> (and <a:hlinkHover>) children from a trigger shape's
    <p:cNvPr> so PowerPoint routes onClick events to interactiveSeq instead of hyperlinks.
    Returns the number of removed hyperlink nodes.
    """
    if cnvpr is None:
        return 0
    removed = 0
    for child in list(cnvpr):
        if _local_name(child.tag) in ("hlinkClick", "hlinkHover"):
            cnvpr.remove(child)
            removed += 1
    return removed


def _ensure_timing_root_child_tn_lst(
    slide_root: ET.Element,
    allocator: TimeNodeIDAllocator,
) -> ET.Element:
    """
    Locate or create `<p:timing>/<p:tnLst>/<p:par>/<p:cTn nodeType="tmRoot">/<p:childTnLst>`
    and ensure a valid `mainSeq` exists so PowerPoint accepts appended `interactiveSeq` nodes.
    """
    timing = slide_root.find("p:timing", NS)
    if timing is None:
        timing = _append_subelement(slide_root, _qname(P_NS, "timing"))

    tn_lst = timing.find("p:tnLst", NS)
    if tn_lst is None:
        tn_lst = _append_subelement(timing, _qname(P_NS, "tnLst"))

    # Look for existing tmRoot cTn
    tm_root_ctn: Optional[ET.Element] = None
    for ctn in tn_lst.findall(".//p:cTn", NS):
        if ctn.attrib.get("nodeType") == "tmRoot":
            tm_root_ctn = ctn
            break

    if tm_root_ctn is None:
        root_par = _append_subelement(tn_lst, _qname(P_NS, "par"))
        tm_root_ctn = _append_subelement(
            root_par,
            _qname(P_NS, "cTn"),
            {
                "id": allocator.allocate_str(),
                "dur": "indefinite",
                "restart": "never",
                "nodeType": "tmRoot",
            },
        )

    child_tn_lst = tm_root_ctn.find("p:childTnLst", NS)
    if child_tn_lst is None:
        child_tn_lst = _append_subelement(tm_root_ctn, _qname(P_NS, "childTnLst"))

    # Ensure mainSeq exists before interactiveSeq siblings
    has_main_seq = any(
        ctn.attrib.get("nodeType") == "mainSeq"
        for ctn in child_tn_lst.findall("./p:seq/p:cTn", NS)
    )
    if not has_main_seq:
        main_seq = _append_subelement(
            child_tn_lst,
            _qname(P_NS, "seq"),
            {"concurrent": "1", "nextAc": "seek"},
        )
        main_ctn = _append_subelement(
            main_seq,
            _qname(P_NS, "cTn"),
            {
                "id": allocator.allocate_str(),
                "dur": "indefinite",
                "nodeType": "mainSeq",
            },
        )
        _append_subelement(main_ctn, _qname(P_NS, "childTnLst"))

        prev_lst = _append_subelement(main_seq, _qname(P_NS, "prevCondLst"))
        prev_cond = _append_subelement(
            prev_lst, _qname(P_NS, "cond"), {"evt": "onPrev", "delay": "0"}
        )
        prev_tgt = _append_subelement(prev_cond, _qname(P_NS, "tgtEl"))
        _append_subelement(prev_tgt, _qname(P_NS, "sldTgt"))

        next_lst = _append_subelement(main_seq, _qname(P_NS, "nextCondLst"))
        next_cond = _append_subelement(
            next_lst, _qname(P_NS, "cond"), {"evt": "onNext", "delay": "0"}
        )
        next_tgt = _append_subelement(next_cond, _qname(P_NS, "tgtEl"))
        _append_subelement(next_tgt, _qname(P_NS, "sldTgt"))

    return child_tn_lst


def _append_visibility_set_behavior(
    effect_child_tn_lst: ET.Element,
    allocator: TimeNodeIDAllocator,
    target_spid: str,
    visible: bool,
    delay_ms: int = 0,
) -> None:
    """Append a <p:set> behavior toggling style.visibility ('visible' or 'hidden')."""
    set_el = _append_subelement(effect_child_tn_lst, _qname(P_NS, "set"))
    c_bhvr = _append_subelement(set_el, _qname(P_NS, "cBhvr"))
    ctn = _append_subelement(
        c_bhvr,
        _qname(P_NS, "cTn"),
        {"id": allocator.allocate_str(), "dur": "1", "fill": "hold"},
    )
    st_lst = _append_subelement(ctn, _qname(P_NS, "stCondLst"))
    _append_subelement(st_lst, _qname(P_NS, "cond"), {"delay": str(max(0, delay_ms))})

    tgt_el = _append_subelement(c_bhvr, _qname(P_NS, "tgtEl"))
    _append_subelement(tgt_el, _qname(P_NS, "spTgt"), {"spid": target_spid})

    attr_lst = _append_subelement(c_bhvr, _qname(P_NS, "attrNameLst"))
    attr_name = _append_subelement(attr_lst, _qname(P_NS, "attrName"))
    attr_name.text = "style.visibility"

    to_el = _append_subelement(set_el, _qname(P_NS, "to"))
    _append_subelement(
        to_el,
        _qname(P_NS, "strVal"),
        {"val": "visible" if visible else "hidden"},
    )


def _append_preset_behaviors(
    effect_child_tn_lst: ET.Element,
    allocator: TimeNodeIDAllocator,
    target_spid: str,
    phase: str,
    preset: str,
    duration_ms: int,
) -> None:
    """
    Append concrete DrawingML/PresentationML animation behaviors for the requested
    (phase, preset) combination ('fade', 'zoom', 'float-in', 'teeter').
    """
    dur_str = str(max(1, int(duration_ms)))

    if phase in ("entr", "exit"):
        if phase == "entr":
            _append_visibility_set_behavior(
                effect_child_tn_lst, allocator, target_spid, visible=True, delay_ms=0
            )

        if preset == "zoom":
            anim_scale = _append_subelement(
                effect_child_tn_lst, _qname(P_NS, "animScale")
            )
            c_bhvr = _append_subelement(anim_scale, _qname(P_NS, "cBhvr"))
            _append_subelement(
                c_bhvr,
                _qname(P_NS, "cTn"),
                {
                    "id": allocator.allocate_str(),
                    "dur": dur_str,
                    "fill": "hold",
                    "accel": "10000",
                    "decel": "70000",
                },
            )
            tgt_el = _append_subelement(c_bhvr, _qname(P_NS, "tgtEl"))
            _append_subelement(tgt_el, _qname(P_NS, "spTgt"), {"spid": target_spid})
            from_el = _append_subelement(anim_scale, _qname(P_NS, "from"))
            to_el = _append_subelement(anim_scale, _qname(P_NS, "to"))
            if phase == "entr":
                _append_subelement(from_el, _qname(P_NS, "pt"), {"x": "1000", "y": "1000"})
                _append_subelement(to_el, _qname(P_NS, "pt"), {"x": "100000", "y": "100000"})
            else:
                _append_subelement(from_el, _qname(P_NS, "pt"), {"x": "100000", "y": "100000"})
                _append_subelement(to_el, _qname(P_NS, "pt"), {"x": "1000", "y": "1000"})

        elif preset == "float-in":
            # Fade transition + vertical slide on ppt_y
            anim_eff = _append_subelement(
                effect_child_tn_lst,
                _qname(P_NS, "animEffect"),
                {"transition": "in" if phase == "entr" else "out", "filter": "fade"},
            )
            c_bhvr_f = _append_subelement(anim_eff, _qname(P_NS, "cBhvr"))
            _append_subelement(
                c_bhvr_f,
                _qname(P_NS, "cTn"),
                {"id": allocator.allocate_str(), "dur": dur_str},
            )
            tgt_f = _append_subelement(c_bhvr_f, _qname(P_NS, "tgtEl"))
            _append_subelement(tgt_f, _qname(P_NS, "spTgt"), {"spid": target_spid})

            anim_y = _append_subelement(
                effect_child_tn_lst,
                _qname(P_NS, "anim"),
                {"calcmode": "lin", "valueType": "num"},
            )
            c_bhvr_y = _append_subelement(anim_y, _qname(P_NS, "cBhvr"))
            _append_subelement(
                c_bhvr_y,
                _qname(P_NS, "cTn"),
                {
                    "id": allocator.allocate_str(),
                    "dur": dur_str,
                    "fill": "hold",
                    "accel": "10000",
                    "decel": "75000",
                },
            )
            tgt_y = _append_subelement(c_bhvr_y, _qname(P_NS, "tgtEl"))
            _append_subelement(tgt_y, _qname(P_NS, "spTgt"), {"spid": target_spid})
            attr_lst = _append_subelement(c_bhvr_y, _qname(P_NS, "attrNameLst"))
            attr_y = _append_subelement(attr_lst, _qname(P_NS, "attrName"))
            attr_y.text = "ppt_y"

            tav_lst = _append_subelement(anim_y, _qname(P_NS, "tavLst"))
            tav0 = _append_subelement(tav_lst, _qname(P_NS, "tav"), {"tm": "0"})
            val0 = _append_subelement(tav0, _qname(P_NS, "val"))
            _append_subelement(
                val0,
                _qname(P_NS, "strVal"),
                {"val": "#ppt_y+0.08" if phase == "entr" else "#ppt_y"},
            )
            tav1 = _append_subelement(tav_lst, _qname(P_NS, "tav"), {"tm": "100000"})
            val1 = _append_subelement(tav1, _qname(P_NS, "val"))
            _append_subelement(
                val1,
                _qname(P_NS, "strVal"),
                {"val": "#ppt_y" if phase == "entr" else "#ppt_y+0.08"},
            )

        else:
            # Default to fade animEffect
            anim_eff = _append_subelement(
                effect_child_tn_lst,
                _qname(P_NS, "animEffect"),
                {"transition": "in" if phase == "entr" else "out", "filter": "fade"},
            )
            c_bhvr = _append_subelement(anim_eff, _qname(P_NS, "cBhvr"))
            _append_subelement(
                c_bhvr,
                _qname(P_NS, "cTn"),
                {"id": allocator.allocate_str(), "dur": dur_str},
            )
            tgt_el = _append_subelement(c_bhvr, _qname(P_NS, "tgtEl"))
            _append_subelement(tgt_el, _qname(P_NS, "spTgt"), {"spid": target_spid})

        if phase == "exit":
            _append_visibility_set_behavior(
                effect_child_tn_lst,
                allocator,
                target_spid,
                visible=False,
                delay_ms=max(0, duration_ms - 1),
            )
        return

    # Emphasis phase ('emph')
    if preset == "zoom":
        anim_scale = _append_subelement(
            effect_child_tn_lst, _qname(P_NS, "animScale")
        )
        c_bhvr = _append_subelement(anim_scale, _qname(P_NS, "cBhvr"))
        _append_subelement(
            c_bhvr,
            _qname(P_NS, "cTn"),
            {
                "id": allocator.allocate_str(),
                "dur": dur_str,
                "autoRev": "1",
                "fill": "hold",
            },
        )
        tgt_el = _append_subelement(c_bhvr, _qname(P_NS, "tgtEl"))
        _append_subelement(tgt_el, _qname(P_NS, "spTgt"), {"spid": target_spid})
        by_el = _append_subelement(anim_scale, _qname(P_NS, "by"))
        _append_subelement(by_el, _qname(P_NS, "pt"), {"x": "112000", "y": "112000"})
    else:
        # Teeter / rotational oscillation emphasis
        anim_rot = _append_subelement(effect_child_tn_lst, _qname(P_NS, "animRot"))
        c_bhvr = _append_subelement(anim_rot, _qname(P_NS, "cBhvr"))
        _append_subelement(
            c_bhvr,
            _qname(P_NS, "cTn"),
            {
                "id": allocator.allocate_str(),
                "dur": str(max(120, int(duration_ms // 2))),
                "repeatCount": "2000",
                "autoRev": "1",
                "fill": "hold",
            },
        )
        tgt_el = _append_subelement(c_bhvr, _qname(P_NS, "tgtEl"))
        _append_subelement(tgt_el, _qname(P_NS, "spTgt"), {"spid": target_spid})
        by_el = _append_subelement(anim_rot, _qname(P_NS, "by"), {"val": "180000"})


def _build_click_step_par(
    seq_child_tn_lst: ET.Element,
    allocator: TimeNodeIDAllocator,
    target_spids: Sequence[str],
    phase: str,
    action_label: str,
    preset: str,
    duration_ms: int,
    delay_ms: int,
) -> ET.Element:
    """
    Create one click-step <p:par> inside the interactiveSeq's <p:childTnLst>,
    containing inner effect nodes for all `target_spids`.
    """
    outer_par = _append_subelement(seq_child_tn_lst, _qname(P_NS, "par"))
    outer_ctn = _append_subelement(
        outer_par,
        _qname(P_NS, "cTn"),
        {"id": allocator.allocate_str(), "fill": "hold"},
    )
    outer_st = _append_subelement(outer_ctn, _qname(P_NS, "stCondLst"))
    _append_subelement(outer_st, _qname(P_NS, "cond"), {"delay": "indefinite"})
    outer_children = _append_subelement(outer_ctn, _qname(P_NS, "childTnLst"))

    group_par = _append_subelement(outer_children, _qname(P_NS, "par"))
    group_ctn = _append_subelement(
        group_par,
        _qname(P_NS, "cTn"),
        {"id": allocator.allocate_str(), "fill": "hold"},
    )
    group_st = _append_subelement(group_ctn, _qname(P_NS, "stCondLst"))
    _append_subelement(group_st, _qname(P_NS, "cond"), {"delay": "0"})
    group_children = _append_subelement(group_ctn, _qname(P_NS, "childTnLst"))

    preset_class, preset_id, preset_subtype = PRESET_METADATA.get(
        (phase, preset), (phase, "10", "0")
    )

    for idx, tgt_spid in enumerate(target_spids):
        eff_par = _append_subelement(group_children, _qname(P_NS, "par"))
        node_type = "clickEffect" if idx == 0 else "withEffect"
        eff_ctn = _append_subelement(
            eff_par,
            _qname(P_NS, "cTn"),
            {
                "id": allocator.allocate_str(),
                "presetID": preset_id,
                "presetClass": preset_class,
                "presetSubtype": preset_subtype,
                "fill": "hold",
                "nodeType": node_type,
                " customAction" if False else "grpId": "0",
            },
        )
        # Store semantic metadata inside @tmFilter or @evtFilter-compatible custom attr if needed,
        # and standard stCondLst for delay_ms
        eff_ctn.set("customAction", action_label)
        eff_ctn.set("customPreset", preset)
        eff_ctn.set("customDur", str(int(duration_ms)))

        eff_st = _append_subelement(eff_ctn, _qname(P_NS, "stCondLst"))
        _append_subelement(
            eff_st, _qname(P_NS, "cond"), {"delay": str(max(0, int(delay_ms)))}
        )
        eff_children = _append_subelement(eff_ctn, _qname(P_NS, "childTnLst"))

        _append_preset_behaviors(
            eff_children,
            allocator=allocator,
            target_spid=tgt_spid,
            phase=phase,
            preset=preset,
            duration_ms=duration_ms,
        )

    return outer_par


def apply_interactive_triggers(
    slide_root: ET.Element,
    triggers_plan: Sequence[Dict[str, Any]],
    shape_id_map: Optional[Dict[str, Union[int, str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Inject semantic interactive click sequences (<p:cTn nodeType="interactiveSeq">)
    into `slide_root`.

    Args:
        slide_root: Root <p:sld> XML element.
        triggers_plan: List of trigger specifications:
            [
                {
                    "trigger": "Button_1" or spid,
                    "action": "reveal" | "hide" | "highlight" | "toggle",
                    "targets": ["Card_A", ...],
                    "preset": "zoom" | "fade" | "float-in" | "teeter",
                    "duration_ms": 500,
                    "delay_ms": 0
                },
                ...
            ]
        shape_id_map: Optional explicit mapping of {shape_name: spid}.

    Returns:
        List of created trigger descriptors with allocated cTn IDs and resolved spids.
    """
    if not triggers_plan:
        return []

    key_to_spid, spid_to_name, spid_to_cnvpr = _index_slide_shapes(
        slide_root, external_map=shape_id_map
    )
    allocator = TimeNodeIDAllocator(slide_root)
    tm_root_children = _ensure_timing_root_child_tn_lst(slide_root, allocator)

    applied_records: List[Dict[str, Any]] = []

    for spec in triggers_plan:
        raw_trigger = spec.get("trigger")
        if raw_trigger is None:
            raise ValueError("Trigger specification is missing 'trigger' key.")

        trigger_key = str(raw_trigger).strip()
        trigger_spid = key_to_spid.get(trigger_key)
        if trigger_spid is None:
            if trigger_key.isdigit():
                trigger_spid = trigger_key
            else:
                raise KeyError(
                    f"Trigger shape '{trigger_key}' could not be resolved on slide."
                )

        # Strip conflicting <a:hlinkClick> on the trigger shape's p:cNvPr
        trigger_cnvpr = spid_to_cnvpr.get(trigger_spid)
        hlinks_removed = _strip_hlink_click(trigger_cnvpr)

        raw_targets = spec.get("targets", [])
        if isinstance(raw_targets, (str, int)):
            raw_targets = [raw_targets]

        target_spids: List[str] = []
        target_names: List[str] = []
        for t in raw_targets:
            t_key = str(t).strip()
            t_spid = key_to_spid.get(t_key)
            if t_spid is None:
                if t_key.isdigit():
                    t_spid = t_key
                else:
                    raise KeyError(
                        f"Target shape '{t_key}' could not be resolved on slide."
                    )
            target_spids.append(t_spid)
            target_names.append(spid_to_name.get(t_spid, t_key))

        if not target_spids:
            # Default to self-triggering if targets omitted
            target_spids = [trigger_spid]
            target_names = [spid_to_name.get(trigger_spid, trigger_key)]

        action = str(spec.get("action", "reveal")).strip().lower()
        if action not in VALID_ACTIONS:
            raise ValueError(
                f"Invalid action '{action}'. Must be one of {sorted(VALID_ACTIONS)}."
            )

        preset = str(spec.get("preset", "fade")).strip().lower()
        if preset not in VALID_PRESETS:
            raise ValueError(
                f"Invalid preset '{preset}'. Must be one of {sorted(VALID_PRESETS)}."
            )

        duration_ms = int(spec.get("duration_ms", 500))
        delay_ms = int(spec.get("delay_ms", 0))

        # Construct <p:seq concurrent="1" nextAc="seek">
        seq_el = _append_subelement(
            tm_root_children,
            _qname(P_NS, "seq"),
            {"concurrent": "1", "nextAc": "seek"},
        )
        seq_ctn_id = allocator.allocate()
        seq_ctn = _append_subelement(
            seq_el,
            _qname(P_NS, "cTn"),
            {
                "id": str(seq_ctn_id),
                "dur": "indefinite",
                "restart": "whenNotActive",
                "fill": "hold",
                "evtFilter": "cancelBubble",
                "nodeType": "interactiveSeq",
            },
        )

        # 1. Internal <p:stCondLst> inside <p:cTn> to wake sequence on first click
        st_cond_lst = _append_subelement(seq_ctn, _qname(P_NS, "stCondLst"))
        st_cond = _append_subelement(
            st_cond_lst,
            _qname(P_NS, "cond"),
            {"evt": "onClick", "delay": "0"},
        )
        st_tgt_el = _append_subelement(st_cond, _qname(P_NS, "tgtEl"))
        _append_subelement(st_tgt_el, _qname(P_NS, "spTgt"), {"spid": trigger_spid})

        # 2. <p:childTnLst> containing effect steps
        seq_child_tn_lst = _append_subelement(seq_ctn, _qname(P_NS, "childTnLst"))

        if action == "reveal":
            _build_click_step_par(
                seq_child_tn_lst,
                allocator,
                target_spids,
                phase="entr",
                action_label="reveal",
                preset=preset,
                duration_ms=duration_ms,
                delay_ms=delay_ms,
            )
        elif action == "hide":
            _build_click_step_par(
                seq_child_tn_lst,
                allocator,
                target_spids,
                phase="exit",
                action_label="hide",
                preset=preset,
                duration_ms=duration_ms,
                delay_ms=delay_ms,
            )
        elif action == "highlight":
            _build_click_step_par(
                seq_child_tn_lst,
                allocator,
                target_spids,
                phase="emph",
                action_label="highlight",
                preset=preset,
                duration_ms=duration_ms,
                delay_ms=delay_ms,
            )
        elif action == "toggle":
            # Two-step interactive cycle: Click 1 -> reveal (entr), Click 2 -> hide (exit)
            _build_click_step_par(
                seq_child_tn_lst,
                allocator,
                target_spids,
                phase="entr",
                action_label="toggle",
                preset=preset,
                duration_ms=duration_ms,
                delay_ms=delay_ms,
            )
            _build_click_step_par(
                seq_child_tn_lst,
                allocator,
                target_spids,
                phase="exit",
                action_label="toggle",
                preset=preset,
                duration_ms=duration_ms,
                delay_ms=delay_ms,
            )

        # 3. Sequence-level <p:nextCondLst> for click advancement
        next_cond_lst = _append_subelement(seq_el, _qname(P_NS, "nextCondLst"))
        next_cond = _append_subelement(
            next_cond_lst,
            _qname(P_NS, "cond"),
            {"evt": "onClick", "delay": "0"},
        )
        next_tgt_el = _append_subelement(next_cond, _qname(P_NS, "tgtEl"))
        _append_subelement(next_tgt_el, _qname(P_NS, "spTgt"), {"spid": trigger_spid})

        applied_records.append({
            "seq_ctn_id": seq_ctn_id,
            "trigger_spid": trigger_spid,
            "trigger_name": spid_to_name.get(trigger_spid, trigger_key),
            "action": action,
            "preset": preset,
            "target_spids": target_spids,
            "targets": target_names,
            "duration_ms": duration_ms,
            "delay_ms": delay_ms,
            "hlinks_removed": hlinks_removed,
            "seq_node": seq_el,
        })

    return applied_records


def read_interactive_triggers(slide_root: ET.Element) -> List[Dict[str, Any]]:
    """
    Inspect `slide_root` and extract all configured interactive click sequences
    (<p:seq> with <p:cTn nodeType="interactiveSeq">) for verification and auditing.
    """
    _, spid_to_name, _ = _index_slide_shapes(slide_root)
    extracted: List[Dict[str, Any]] = []

    for seq_el in slide_root.findall(".//p:seq", NS):
        ctn = seq_el.find("p:cTn", NS)
        if ctn is None or ctn.attrib.get("nodeType") != "interactiveSeq":
            continue

        try:
            seq_id = int(ctn.attrib.get("id", "0"))
        except ValueError:
            seq_id = 0

        # Read trigger spid from nextCondLst or stCondLst
        trig_sp_tgt = seq_el.find("p:nextCondLst/p:cond/p:tgtEl/p:spTgt", NS)
        if trig_sp_tgt is None:
            trig_sp_tgt = ctn.find("p:stCondLst/p:cond/p:tgtEl/p:spTgt", NS)

        trigger_spid = (
            trig_sp_tgt.attrib.get("spid", "") if trig_sp_tgt is not None else ""
        )
        trigger_name = spid_to_name.get(trigger_spid, trigger_spid)

        # Inspect effect nodes inside childTnLst
        child_tn_lst = ctn.find("p:childTnLst", NS)
        effect_ctns: List[ET.Element] = []
        target_spids: List[str] = []

        if child_tn_lst is not None:
            for sub_ctn in child_tn_lst.findall(".//p:cTn", NS):
                if sub_ctn.attrib.get("nodeType") in ("clickEffect", "withEffect"):
                    effect_ctns.append(sub_ctn)
            for sp_tgt in child_tn_lst.findall(".//p:tgtEl/p:spTgt", NS):
                spid_val = sp_tgt.attrib.get("spid", "")
                if spid_val and spid_val not in target_spids:
                    target_spids.append(spid_val)

        preset_classes = {
            ec.attrib.get("presetClass", "")
            for ec in effect_ctns
            if ec.attrib.get("presetClass")
        }

        # Determine semantic action
        custom_actions = [
            ec.attrib.get("customAction", "")
            for ec in effect_ctns
            if ec.attrib.get("customAction")
        ]
        if custom_actions:
            action = custom_actions[0]
        elif "entr" in preset_classes and "exit" in preset_classes:
            action = "toggle"
        elif "exit" in preset_classes:
            action = "hide"
        elif "emph" in preset_classes:
            action = "highlight"
        else:
            action = "reveal"

        # Determine preset name
        custom_presets = [
            ec.attrib.get("customPreset", "")
            for ec in effect_ctns
            if ec.attrib.get("customPreset")
        ]
        if custom_presets:
            preset = custom_presets[0]
        else:
            first_pid = effect_ctns[0].attrib.get("presetID", "10") if effect_ctns else "10"
            if first_pid in ("23", "6"):
                preset = "zoom"
            elif first_pid == "42":
                preset = "float-in"
            elif first_pid == "14":
                preset = "teeter"
            else:
                preset = "fade"

        # Determine duration_ms and delay_ms
        duration_ms = 500
        delay_ms = 0
        if effect_ctns:
            first_eff = effect_ctns[0]
            if "customDur" in first_eff.attrib:
                try:
                    duration_ms = int(first_eff.attrib["customDur"])
                except ValueError:
                    pass
            else:
                for bhvr_ctn in first_eff.findall(".//p:cBhvr/p:cTn", NS):
                    raw_dur = bhvr_ctn.attrib.get("dur", "")
                    if raw_dur.isdigit() and int(raw_dur) > 1:
                        duration_ms = int(raw_dur)
                        break

            st_cond = first_eff.find("p:stCondLst/p:cond", NS)
            if st_cond is not None:
                raw_delay = st_cond.attrib.get("delay", "0")
                if raw_delay.isdigit():
                    delay_ms = int(raw_delay)

        extracted.append({
            "seq_ctn_id": seq_id,
            "trigger": trigger_name or trigger_spid,
            "trigger_spid": trigger_spid,
            "trigger_name": trigger_name,
            "action": action,
            "preset": preset,
            "target_spids": target_spids,
            "targets": [spid_to_name.get(s, s) for s in target_spids],
            "duration_ms": duration_ms,
            "delay_ms": delay_ms,
        })

    return extracted
