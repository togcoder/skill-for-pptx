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
                "Focused executive summary report.",
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
