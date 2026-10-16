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
