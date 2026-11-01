#!/usr/bin/env python3
"""Dynamic Theme Engine for Presentations (T043).

Provides:
  1. Area-Weighted PPTX Reference Teardown (reverses color hierarchy, fonts, modular scale).
  2. Need-Based Dynamic Theme Synthesizer (maps topic/intent to OKLCH palettes & typography).
  3. AI Image Visual Harmonizer (formulates style prompts matching lighting, hue, and framing).

Standards:
  - OKLab / OKLCH perceptual color space (Björn Ottosson, 2020)
  - WCAG 2.1 relative luminance & contrast ratio
  - Area-weighted EMU clustering & Salience Scoring
Reference: domains/pptx/DOMAIN.md, research/tasks/INDEX.md
"""
from __future__ import annotations

import colorsys
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
import zipfile

# ==============================================================================
# 1. Perceptual Color Math (Pure Python: sRGB <-> Linear <-> OKLab <-> OKLCH)
# ==============================================================================

def normalize_hex(hex_str: str) -> str:
    """Normalize hex string to uppercase with leading '#' (#RRGGBB)."""
    s = hex_str.strip().lstrip("#").upper()
    if len(s) == 3:
        s = "".join([c * 2 for c in s])
    return f"#{s}"


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Parse #RRGGBB or RRGGBB to integer tuple (r, g, b) in [0, 255]."""
    s = hex_str.strip().lstrip("#")
    if len(s) == 3:
        s = "".join([c * 2 for c in s])
    if len(s) != 6:
        return (0, 0, 0)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Format (r, g, b) in [0, 255] to #RRGGBB uppercase."""
    r_c = max(0, min(255, int(round(r))))
    g_c = max(0, min(255, int(round(g))))
    b_c = max(0, min(255, int(round(b))))
    return f"#{r_c:02X}{g_c:02X}{b_c:02X}"


def srgb_to_linear(c: float) -> float:
    """De-gamma compress sRGB component in [0, 1] to linear RGB."""
    if c <= 0.04045:
        return c / 12.92
    return math.pow((c + 0.055) / 1.055, 2.4)


def linear_to_srgb(c_lin: float) -> float:
    """Re-apply gamma compression from linear RGB to sRGB in [0, 1]."""
    c_lin = max(0.0, min(1.0, c_lin))
    if c_lin <= 0.0031308:
        return c_lin * 12.92
    return 1.055 * math.pow(c_lin, 1.0 / 2.4) - 0.055


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Compute standard WCAG 2.1 relative luminance Y in [0, 1]."""
    r_lin = srgb_to_linear(rgb[0] / 255.0)
    g_lin = srgb_to_linear(rgb[1] / 255.0)
    b_lin = srgb_to_linear(rgb[2] / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def wcag_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Compute WCAG contrast ratio (1.0 to 21.0) between two colors."""
    y1 = relative_luminance(rgb1)
    y2 = relative_luminance(rgb2)
    l_max = max(y1, y2)
    l_min = min(y1, y2)
    return (l_max + 0.05) / (l_min + 0.05)


def rgb_to_oklab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert sRGB [0..255] to OKLab (L, a, b)."""
    r = srgb_to_linear(rgb[0] / 255.0)
    g = srgb_to_linear(rgb[1] / 255.0)
    b = srgb_to_linear(rgb[2] / 255.0)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_ = math.pow(max(0.0, l), 1.0 / 3.0)
    m_ = math.pow(max(0.0, m), 1.0 / 3.0)
    s_ = math.pow(max(0.0, s), 1.0 / 3.0)

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return (L, a, b_val)


def oklab_to_oklch(L: float, a: float, b: float) -> Tuple[float, float, float]:
    """Convert OKLab (L, a, b) to OKLCH (L, C, H degrees [0..360])."""
    C = math.sqrt(a * a + b * b)
    H_rad = math.atan2(b, a)
    H_deg = math.degrees(H_rad) % 360.0
    return (L, C, H_deg)


def oklch_to_oklab(L: float, C: float, H_deg: float) -> Tuple[float, float, float]:
    """Convert OKLCH (L, C, H degrees) to OKLab (L, a, b)."""
    H_rad = math.radians(H_deg)
    a = C * math.cos(H_rad)
    b = C * math.sin(H_rad)
    return (L, a, b)


def oklab_to_rgb(L: float, a: float, b_val: float) -> Tuple[int, int, int]:
    """Convert OKLab (L, a, b) to sRGB [0..255]."""
    l_ = L + 0.3963377774 * a + 0.2158037573 * b_val
    m_ = L - 0.1055613458 * a - 0.0638541728 * b_val
    s_ = L - 0.0894841775 * a - 1.2914855480 * b_val

    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_

    r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    r = int(round(linear_to_srgb(r_lin) * 255.0))
    g = int(round(linear_to_srgb(g_lin) * 255.0))
    b = int(round(linear_to_srgb(b_lin) * 255.0))
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def delta_e_oklab(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]) -> float:
    """Euclidean distance in OKLab color space."""
    dL = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return math.sqrt(dL * dL + da * da + db * db)


def classify_canvas_mode(hex_color: str) -> str:
    """Classify canvas mode: DARK_CANVAS, WARM_PAPER, LIGHT_CANVAS, or MID_TONE_CANVAS."""
    rgb = hex_to_rgb(hex_color)
    Y = relative_luminance(rgb)
    L, a, b = rgb_to_oklab(rgb)
    _, C, H = oklab_to_oklch(L, a, b)

    if Y < 0.18:
        return "DARK_CANVAS"
    if 0.72 <= Y <= 0.96 and 0.010 <= C <= 0.060 and 50.0 <= H <= 110.0:
        return "WARM_PAPER"
    if Y >= 0.72:
        return "LIGHT_CANVAS"
    return "MID_TONE_CANVAS"


# ==============================================================================
# 2. Reference Teardown Engine (PPTX Parser & Feature Extractor)
# ==============================================================================

class PPTXThemeExtractor:
    """Extracts design DNA (Area-weighted 60-30-10 palette, typography, modular scale) from PPTX."""

    NS = {
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }

    def __init__(self, pptx_path: str | Path):
        self.pptx_path = Path(pptx_path).resolve()
        if not self.pptx_path.is_file():
            raise FileNotFoundError(f"PPTX file not found: {self.pptx_path}")

    def extract(self) -> Dict[str, Any]:
        """Perform full teardown and return standardized ThemeSpec dictionary."""
        with zipfile.ZipFile(self.pptx_path, "r") as z:
            names = z.namelist()
            slide_files = sorted(
                [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
                key=lambda x: int(re.search(r"slide(\d+)\.xml", x).group(1)),
            )

            # 1. Slide Dimensions
            slide_cx, slide_cy = 9144000, 5143500  # Default 16:9 10x5.625in in EMU
            if "ppt/presentation.xml" in names:
                pres_root = ET.fromstring(z.read("ppt/presentation.xml"))
                sldSz = pres_root.find(".//p:sldSz", self.NS)
                if sldSz is not None:
                    slide_cx = int(sldSz.attrib.get("cx", slide_cx))
                    slide_cy = int(sldSz.attrib.get("cy", slide_cy))
            slide_area = float(slide_cx) * float(slide_cy)

            # 2. Theme clrScheme & fontScheme
            clr_map = {}
            major_font = "Arial"
            minor_font = "Arial"
            if "ppt/theme/theme1.xml" in names:
                theme_root = ET.fromstring(z.read("ppt/theme/theme1.xml"))
                clrScheme = theme_root.find(".//a:clrScheme", self.NS)
                if clrScheme is not None:
                    for child in clrScheme:
                        tag = child.tag.split("}")[-1]
                        srgb = child.find(".//a:srgbClr", self.NS)
                        sys = child.find(".//a:sysClr", self.NS)
                        if srgb is not None:
                            clr_map[tag] = srgb.attrib.get("val", "").upper()
                        elif sys is not None:
                            clr_map[tag] = sys.attrib.get("lastClr", "").upper()

                fontScheme = theme_root.find(".//a:fontScheme", self.NS)
                if fontScheme is not None:
                    mj = fontScheme.find("a:majorFont/a:latin", self.NS)
                    mn = fontScheme.find("a:minorFont/a:latin", self.NS)
                    if mj is not None and mj.attrib.get("typeface"):
                        major_font = mj.attrib.get("typeface")
                    if mn is not None and mn.attrib.get("typeface"):
                        minor_font = mn.attrib.get("typeface")

            # 3. Harvest Colors with Area Weights & Text Runs
            raw_colors: List[Dict[str, Any]] = []
            text_runs: List[Dict[str, Any]] = []
            shape_geometries: List[str] = []

            for s_file in slide_files:
                s_root = ET.fromstring(z.read(s_file))

                # Check relationships for images
                s_rel_file = s_file.replace("ppt/slides/slide", "ppt/slides/_rels/slide") + ".rels"
                rel_targets = {}
                if s_rel_file in names:
                    rel_root = ET.fromstring(z.read(s_rel_file))
                    for rel in rel_root:
                        r_id = rel.attrib.get("Id")
                        r_target = rel.attrib.get("Target", "")
                        if r_id and r_target:
                            rel_targets[r_id] = r_target.replace("../", "ppt/")

                # Background fill weight
                bg_found = False
                for bg in s_root.findall(".//p:bg", self.NS):
                    srgb = bg.find(".//a:srgbClr", self.NS)
                    sch = bg.find(".//a:schemeClr", self.NS)
                    hex_val = None
                    if srgb is not None:
                        hex_val = srgb.attrib.get("val")
                    elif sch is not None and sch.attrib.get("val") in clr_map:
                        hex_val = clr_map[sch.attrib.get("val")]
                    if hex_val:
                        raw_colors.append({
                            "hex": normalize_hex(hex_val),
                            "weight": slide_area * 0.8,
                            "is_bg": True,
                            "is_text": False,
                        })
                        bg_found = True

                # Shapes & Text
                for sp in s_root.findall(".//p:sp", self.NS) + s_root.findall(".//p:pic", self.NS):
                    # Geometry
                    prst = sp.find(".//a:prstGeom", self.NS)
                    if prst is not None:
                        shape_geometries.append(prst.attrib.get("prst", "rect"))
                    elif sp.find(".//a:custGeom", self.NS) is not None:
                        shape_geometries.append("custGeom")

                    # Shape Size
                    xfrm = sp.find(".//a:xfrm", self.NS)
                    if xfrm is None:
                        xfrm = sp.find(".//p:spPr/a:xfrm", self.NS)
                    ext = xfrm.find("a:ext", self.NS) if xfrm is not None else None
                    cx = int(ext.attrib.get("cx", 914400)) if ext is not None else 914400
                    cy = int(ext.attrib.get("cy", 914400)) if ext is not None else 914400
                    shape_area = float(cx) * float(cy)

                    # Check for Full-Slide Image Background (blipFill covering >= 70% of slide)
                    blip = sp.find(".//a:blip", self.NS)
                    if blip is not None and cx >= 0.7 * slide_cx and cy >= 0.7 * slide_cy:
                        embed_id = blip.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                        media_path = rel_targets.get(embed_id)
                        if media_path and media_path in names:
                            try:
                                from io import BytesIO
                                from PIL import Image
                                img_bytes = z.read(media_path)
                                im = Image.open(BytesIO(img_bytes)).convert("RGB")
                                avg_color = im.resize((1, 1)).getpixel((0, 0))
                                bg_hex = f"#{avg_color[0]:02X}{avg_color[1]:02X}{avg_color[2]:02X}"
                                raw_colors.append({
                                    "hex": bg_hex,
                                    "weight": slide_area * 1.5,
                                    "is_bg": True,
                                    "is_text": False,
                                })
                                bg_found = True

                                # Sample top chromatic accent from background image
                                im_small = im.resize((50, 50))
                                for px in im_small.getdata():
                                    L, a_c, b_c = rgb_to_oklab(px)
                                    _, C, _ = oklab_to_oklch(L, a_c, b_c)
                                    if C > 0.10:  # High chroma accent
                                        accent_h = rgb_to_hex(*px)
                                        raw_colors.append({
                                            "hex": accent_h,
                                            "weight": shape_area * 0.2,
                                            "is_bg": False,
                                            "is_text": False,
                                        })
                                        break
                            except Exception:
                                pass

                    # Shape Fill
                    spPr = sp.find(".//p:spPr", self.NS)
                    if spPr is not None:
                        srgb = spPr.find(".//a:solidFill/a:srgbClr", self.NS)
                        sch = spPr.find(".//a:solidFill/a:schemeClr", self.NS)
                        hex_val = None
                        if srgb is not None:
                            hex_val = srgb.attrib.get("val")
                        elif sch is not None and sch.attrib.get("val") in clr_map:
                            hex_val = clr_map[sch.attrib.get("val")]
                        if hex_val:
                            raw_colors.append({
                                "hex": normalize_hex(hex_val),
                                "weight": shape_area,
                                "is_bg": False,
                                "is_text": False,
                            })

                    # Text runs
                    for r_node in sp.findall(".//a:r", self.NS):
                        t_node = r_node.find("a:t", self.NS)
                        text_content = t_node.text if (t_node is not None and t_node.text) else ""
                        if not text_content.strip():
                            continue

                        rPr = r_node.find("a:rPr", self.NS)
                        sz_val = int(rPr.attrib.get("sz", 1400)) / 100.0 if rPr is not None else 14.0
                        font_face = minor_font
                        if rPr is not None:
                            latin = rPr.find("a:latin", self.NS)
                            if latin is not None and latin.attrib.get("typeface"):
                                tf = latin.attrib.get("typeface")
                                font_face = major_font if "+mj" in tf else (minor_font if "+mn" in tf else tf)

                        text_runs.append({
                            "text": text_content,
                            "len": len(text_content),
                            "size_pt": sz_val,
                            "font": font_face,
                        })

                        # Text color
                        if rPr is not None:
                            srgb = rPr.find(".//a:solidFill/a:srgbClr", self.NS)
                            sch = rPr.find(".//a:solidFill/a:schemeClr", self.NS)
                            hex_val = None
                            if srgb is not None:
                                hex_val = srgb.attrib.get("val")
                            elif sch is not None and sch.attrib.get("val") in clr_map:
                                hex_val = clr_map[sch.attrib.get("val")]
                            if hex_val:
                                text_weight = len(text_content) * (sz_val ** 2) * (12700.0 ** 2)
                                raw_colors.append({
                                    "hex": normalize_hex(hex_val),
                                    "weight": text_weight,
                                    "is_bg": False,
                                    "is_text": True,
                                })

            # 4. Cluster Colors in OKLab
            palette = self._cluster_colors(raw_colors, slide_area * len(slide_files))

            # 5. Extract Typography & Modular Scale
            typography = self._extract_typography(text_runs, major_font, minor_font)

            # 6. Synthesize Full ThemeSpec
            canvas_mode = classify_canvas_mode(palette["canvas_hex"])
            theme_spec = {
                "source_file": self.pptx_path.name,
                "canvas_mode": canvas_mode,
                "slide_count": len(slide_files),
                "palette_60_30_10": palette,
                "typography": typography,
                "shape_dna": {
                    "has_cust_geom_mask": "custGeom" in shape_geometries,
                    "dominant_shape": max(set(shape_geometries), key=shape_geometries.count) if shape_geometries else "rect",
                },
                "image_direct_prompt": self._generate_image_directive(canvas_mode, palette["accent_primary_hex"]),
            }
            return theme_spec

    def _cluster_colors(self, raw_colors: List[Dict[str, Any]], total_deck_area: float) -> Dict[str, Any]:
        """Radius-cluster colors in OKLab space weighted by bounding area."""
        if not raw_colors:
            return {
                "canvas_hex": "#0B1B3D",
                "surface_hex": "#162A52",
                "text_primary_hex": "#FFFFFF",
                "accent_primary_hex": "#3B82F6",
                "accent_secondary_list": ["#06B6D4"],
            }

        # Aggregate raw weights by exact hex
        weight_map: Dict[str, float] = {}
        text_weight_map: Dict[str, float] = {}
        bg_weight_map: Dict[str, float] = {}
        for item in raw_colors:
            h = item["hex"]
            weight_map[h] = weight_map.get(h, 0.0) + item["weight"]
            if item["is_text"]:
                text_weight_map[h] = text_weight_map.get(h, 0.0) + item["weight"]
            if item["is_bg"]:
                bg_weight_map[h] = bg_weight_map.get(h, 0.0) + item["weight"]

        # Sort distinct colors by weight
        sorted_hexes = sorted(weight_map.keys(), key=lambda x: weight_map[x], reverse=True)

        # Agglomerative clustering (threshold deltaE_OK < 0.035)
        clusters: List[Dict[str, Any]] = []
        for h in sorted_hexes:
            rgb = hex_to_rgb(h)
            lab = rgb_to_oklab(rgb)
            matched = False
            for cl in clusters:
                if delta_e_oklab(lab, cl["lab"]) < 0.035:
                    cl["total_weight"] += weight_map[h]
                    cl["text_weight"] += text_weight_map.get(h, 0.0)
                    cl["bg_weight"] += bg_weight_map.get(h, 0.0)
                    matched = True
                    break
            if not matched:
                clusters.append({
                    "seed_hex": h,
                    "rgb": rgb,
                    "lab": lab,
                    "total_weight": weight_map[h],
                    "text_weight": text_weight_map.get(h, 0.0),
                    "bg_weight": bg_weight_map.get(h, 0.0),
                })

        # Identify Canvas (largest background weight or largest total surface)
        canvas_cluster = max(clusters, key=lambda c: (c["bg_weight"] * 2.0 + c["total_weight"]))
        canvas_hex = canvas_cluster["seed_hex"]
        canvas_rgb = canvas_cluster["rgb"]

        # Identify Primary Text (highest text weight with WCAG contrast >= 4.5 against canvas)
        text_candidates = [c for c in clusters if c != canvas_cluster and wcag_contrast_ratio(c["rgb"], canvas_rgb) >= 4.5]
        if text_candidates:
            text_cluster = max(text_candidates, key=lambda c: c["text_weight"] * 3.0 + c["total_weight"])
            text_primary_hex = text_cluster["seed_hex"]
        else:
            # Fallback to pure white or pure dark depending on canvas luminance
            text_primary_hex = "#FFFFFF" if relative_luminance(canvas_rgb) < 0.5 else "#1A1A1A"

        # Identify Surface 30% (largest remaining cluster not Canvas or Text)
        surface_candidates = [c for c in clusters if c["seed_hex"] not in (canvas_hex, text_primary_hex)]
        if surface_candidates:
            surface_cluster = max(surface_candidates, key=lambda c: c["total_weight"])
            surface_hex = surface_cluster["seed_hex"]
        else:
            surface_hex = canvas_hex

        # Identify Accent 10% via Salience Scoring
        accent_candidates = [c for c in clusters if c["seed_hex"] not in (canvas_hex, surface_hex, text_primary_hex)]
        scored_accents: List[Tuple[str, float]] = []
        for c in accent_candidates:
            L, ok_a, ok_b = c["lab"]
            _, C, _ = oklab_to_oklch(L, ok_a, ok_b)
            dE = delta_e_oklab(c["lab"], canvas_cluster["lab"])
            ratio_area = c["total_weight"] / (total_deck_area + 1.0)
            score = C * 2.5 + dE * 1.5 + math.log(1.0 + ratio_area)
            scored_accents.append((c["seed_hex"], score))

        scored_accents.sort(key=lambda x: x[1], reverse=True)
        accent_primary_hex = scored_accents[0][0] if scored_accents else "#3B82F6"
        accent_secondary_list = [x[0] for x in scored_accents[1:4]]

        return {
            "canvas_hex": canvas_hex,
            "surface_hex": surface_hex,
            "text_primary_hex": text_primary_hex,
            "accent_primary_hex": accent_primary_hex,
            "accent_secondary_list": accent_secondary_list,
        }

    def _extract_typography(
        self, text_runs: List[Dict[str, Any]], default_major: str, default_minor: str
    ) -> Dict[str, Any]:
        """Analyze character distribution, body font, display font, and modular scale ratio."""
        if not text_runs:
            return {
                "font_display": default_major,
                "font_body": default_minor,
                "base_body_pt": 14.0,
                "modular_scale_ratio": 1.250,
                "hero_kpi_pt": None,
            }

        # Body font: Mode of characters in 9pt <= size <= 20pt
        body_runs = [r for r in text_runs if 9.0 <= r["size_pt"] <= 20.0]
        body_font_chars: Dict[str, int] = {}
        body_sizes: Dict[float, int] = {}
        for r in body_runs:
            f = r["font"]
            body_font_chars[f] = body_font_chars.get(f, 0) + r["len"]
            sz = round(r["size_pt"], 1)
            body_sizes[sz] = body_sizes.get(sz, 0) + r["len"]

        font_body = max(body_font_chars.keys(), key=lambda k: body_font_chars[k]) if body_font_chars else default_minor
        base_body_pt = max(body_sizes.keys(), key=lambda k: body_sizes[k]) if body_sizes else 14.0

        # Display font: Dominant font at >= P85 or size >= 24pt
        display_runs = [r for r in text_runs if r["size_pt"] >= 24.0]
        display_font_chars: Dict[str, int] = {}
        for r in display_runs:
            f = r["font"]
            display_font_chars[f] = display_font_chars.get(f, 0) + r["len"]

        font_display = (
            max(display_font_chars.keys(), key=lambda k: display_font_chars[k])
            if display_font_chars
            else default_major
        )

        # Detect Mammoth Hero KPI (size >= 96pt, e.g. 202pt)
        hero_runs = [r["size_pt"] for r in text_runs if r["size_pt"] >= 96.0]
        hero_kpi_pt = max(hero_runs) if hero_runs else None

        # Compute Geometric Modular Scale ratio r = (S_h1 / S_body) ^ (1/3)
        h1_runs = [r["size_pt"] for r in text_runs if 32.0 <= r["size_pt"] <= 72.0]
        s_h1 = max(h1_runs) if h1_runs else (base_body_pt * 2.0)
        raw_r = math.pow(s_h1 / max(10.0, base_body_pt), 1.0 / 3.0)

        # Snap to nearest canonical musical ratio
        canonical_ratios = [1.200, 1.250, 1.333, 1.414]
        best_ratio = min(canonical_ratios, key=lambda cr: abs(cr - raw_r))

        return {
            "font_display": font_display,
            "font_body": font_body,
            "base_body_pt": base_body_pt,
            "modular_scale_ratio": best_ratio,
            "hero_kpi_pt": hero_kpi_pt,
        }

    def _generate_image_directive(self, canvas_mode: str, accent_hex: str) -> Dict[str, str]:
        """Formulate AI image lighting and color grading directives matching canvas mode."""
        if canvas_mode == "DARK_CANVAS":
            return {
                "lighting": "dramatic rim lighting, cool-toned studio key light at 6500K, deep obsidian-navy shadows, subtle cyan/cobalt specular highlights",
                "color_grading": f"color graded with deep navy shadow floor and electric accent highlights ({accent_hex}), low-key exposure blending seamlessly into dark slide background",
            }
        elif canvas_mode == "WARM_PAPER":
            return {
                "lighting": "soft diffused natural morning window light at 3800K, warm golden-hour fill, gentle low-contrast roll-off",
                "color_grading": f"editorial film color grading on warm ecru paper tone, muted pastel accents ({accent_hex}), matte Kodak Portra aesthetic, zero harsh neon saturation",
            }
        else:
            return {
                "lighting": "clean high-key industrial studio lighting at 5500K, crisp shadow definition, razor-sharp optical focus",
                "color_grading": f"neutral daylight balance with subtle slate-metallic reflections ({accent_hex}) and high-contrast technical clarity",
            }


# ==============================================================================
# 3. Need-Based Dynamic Theme Synthesizer
# ==============================================================================

ARCHETYPES = {
    "INDUSTRIAL_QCC": {
        "keywords": ["qcc", "cải tiến", "chất lượng", "lỗi", "nhà máy", "kỹ thuật", "lean", "six sigma", "engineering", "industrial"],
        "canvas_oklch": (0.97, 0.005, 240.0),      # #F4F6F9
        "surface_oklch": (1.00, 0.000, 0.0),        # #FFFFFF
        "text_oklch": (0.20, 0.020, 250.0),         # #0F172A
        "accent1_oklch": (0.55, 0.160, 245.0),      # Cobalt
        "accent2_oklch": (0.62, 0.180, 35.0),       # Safety Amber
        "font_display": "Century Gothic Bold",
        "font_body": "Century Gothic",
        "modular_scale": 1.250,
        "shape_style": "SHARP_CHAMFER",
        "border_weight_pt": 1.0,
        "corner_radius_pt": 2,
    },
    "TECH_PITCH_DARK": {
        "keywords": ["pitch deck", "gọi vốn", "ai", "startup", "công nghệ", "hiện đại", "blue modern", "data", "cyber", "software"],
        "canvas_oklch": (0.21, 0.065, 262.0),      # #0B1B3D
        "surface_oklch": (0.27, 0.060, 260.0),     # #162A52
        "text_oklch": (0.99, 0.000, 0.0),          # #FFFFFF
        "accent1_oklch": (0.62, 0.190, 258.0),     # #3B82F6 Aero Blue
        "accent2_oklch": (0.78, 0.150, 195.0),     # #06B6D4 Cyan
        "font_display": "Aileron Bold",
        "font_body": "Aileron",
        "modular_scale": 1.333,
        "hero_kpi_pt": 202,
        "shape_style": "FREEFORM_ANGLED_AND_GLASS",
        "border_weight_pt": 1.0,
        "corner_radius_pt": 0,
    },
    "EDITORIAL_WARM_KEYNOTE": {
        "keywords": ["hội thảo", "văn hóa", "nội bộ", "webinar", "keynote", "nhân sự", "thương hiệu", "storytelling", "lifestyle", "ấm áp"],
        "canvas_oklch": (0.95, 0.016, 92.0),       # #F4F1E9
        "surface_oklch": (0.91, 0.022, 88.0),      # #EAE4D7
        "text_oklch": (0.21, 0.000, 0.0),          # #1A1A1A
        "accent1_oklch": (0.88, 0.075, 355.0),     # #FFD0E0 Rose
        "accent2_oklch": (0.76, 0.115, 58.0),      # #EAA86B Terracotta
        "font_display": "TAN Mon Cheri",
        "font_body": "TT Commons Pro",
        "modular_scale": 1.333,
        "shape_style": "SOFT_ORGANIC_PILL",
        "border_weight_pt": 0.0,
        "corner_radius_pt": 18,
    },
    "EXECUTIVE_STRATEGY": {
        "keywords": ["tài chính", "chiến lược", "hđqt", "board", "doanh thu", "ngân hàng", "báo cáo năm", "executive", "finance"],
        "canvas_oklch": (0.98, 0.003, 90.0),       # #FAF9F6
        "surface_oklch": (0.93, 0.010, 250.0),     # #E2E8F0
        "text_oklch": (0.18, 0.030, 255.0),        # #0F172A
        "accent1_oklch": (0.42, 0.110, 255.0),     # #1E3A8A Deep Blue
        "accent2_oklch": (0.65, 0.120, 75.0),      # #D97706 Muted Gold
        "font_display": "Trebuchet MS Bold",
        "font_body": "Calibri",
        "modular_scale": 1.200,
        "shape_style": "STRUCTURED_GRID",
        "border_weight_pt": 0.75,
        "corner_radius_pt": 0,
    },
    "SUSTAINABLE_BIO": {
        "keywords": ["esg", "xanh", "bền vững", "môi trường", "y tế", "năng lượng", "bio", "health", "green"],
        "canvas_oklch": (0.96, 0.015, 145.0),      # #F0F5F1
        "surface_oklch": (1.00, 0.000, 0.0),       # #FFFFFF
        "text_oklch": (0.22, 0.035, 155.0),        # #112A1E
        "accent1_oklch": (0.52, 0.130, 152.0),     # #15803D Forest
        "accent2_oklch": (0.72, 0.135, 85.0),      # #EAB308 Olive Amber
        "font_display": "Century Gothic Bold",
        "font_body": "Segoe UI",
        "modular_scale": 1.250,
        "shape_style": "ROUNDED_BENTO",
        "border_weight_pt": 1.0,
        "corner_radius_pt": 10,
    },
}


def synthesize_theme_from_need(
    query_text: str, custom_hue_deg: Optional[float] = None
) -> Dict[str, Any]:
    """Synthesize a complete ThemeSpec based on user intent keywords and optional custom hue."""
    q_lower = query_text.lower()

    # Score archetypes by keyword frequency
    best_id = "TECH_PITCH_DARK"
    best_score = -1
    for arch_id, arch in ARCHETYPES.items():
        score = sum(1 for kw in arch["keywords"] if kw in q_lower)
        if score > best_score:
            best_score = score
            best_id = arch_id

    arch = ARCHETYPES[best_id]

    def _render_oklch(ok_tuple: Tuple[float, float, float], override_h: Optional[float] = None) -> str:
        L, C, H = ok_tuple
        if override_h is not None and C > 0.05:  # Only rotate hue on chromatic elements
            H = override_h
        lab_L, lab_a, lab_b = oklch_to_oklab(L, C, H)
        rgb = oklab_to_rgb(lab_L, lab_a, lab_b)
        return rgb_to_hex(rgb[0], rgb[1], rgb[2])

    canvas_hex = _render_oklch(arch["canvas_oklch"])
    surface_hex = _render_oklch(arch["surface_oklch"])
    text_hex = _render_oklch(arch["text_oklch"])
    accent1_hex = _render_oklch(arch["accent1_oklch"], custom_hue_deg)
    accent2_hex = _render_oklch(arch["accent2_oklch"], (custom_hue_deg + 45.0) % 360 if custom_hue_deg else None)

    # Validate WCAG AA contrast
    c_rgb = hex_to_rgb(canvas_hex)
    t_rgb = hex_to_rgb(text_hex)
    cr = wcag_contrast_ratio(c_rgb, t_rgb)
    if cr < 4.5:
        text_hex = "#FFFFFF" if relative_luminance(c_rgb) < 0.5 else "#000000"

    canvas_mode = classify_canvas_mode(canvas_hex)

    return {
        "archetype_id": best_id,
        "canvas_mode": canvas_mode,
        "palette_60_30_10": {
            "canvas_hex": canvas_hex,
            "surface_hex": surface_hex,
            "text_primary_hex": text_hex,
            "accent_primary_hex": accent1_hex,
            "accent_secondary_list": [accent2_hex],
            "wcag_contrast_ratio": round(cr, 2),
        },
        "typography": {
            "font_display": arch["font_display"],
            "font_body": arch["font_body"],
            "modular_scale_ratio": arch["modular_scale"],
            "hero_kpi_pt": arch.get("hero_kpi_pt"),
        },
        "shape_dna": {
            "shape_style": arch["shape_style"],
            "border_weight_pt": arch["border_weight_pt"],
            "corner_radius_pt": arch["corner_radius_pt"],
        },
    }


# ==============================================================================
# 4. AI Image Visual Harmonizer (Image Generation Directive Formulator)
# ==============================================================================

def build_harmonized_image_prompt(
    subject: str, theme_profile: Dict[str, Any], slot_type: str = "hero_full_bleed"
) -> Dict[str, Any]:
    """Formulate an AI image generation brief that guarantees visual harmony with the slide theme.
    
    Returns:
      {
        "prompt": str,
        "aspect_ratio": "16:9" | "4:5" | "1:1",
        "lighting_kelvin": int,
        "color_grade": str,
        "negative_prompt": str
      }
    """
    canvas_mode = theme_profile.get("canvas_mode", "DARK_CANVAS")
    palette = theme_profile.get("palette_60_30_10", {})
    accent_hex = palette.get("accent_primary_hex", "#3B82F6")

    # 1. Framing & Aspect Ratio
    if slot_type == "hero_full_bleed":
        aspect_ratio = "16:9"
        framing = "cinematic wide composition, subject anchored on the right third, leaving 60% clean uncluttered negative space on the left for presentation typography overlay"
    elif slot_type in ("split_vertical_panel", "angled_mask_feature"):
        aspect_ratio = "4:5"
        framing = "tight vertical composition, centered subject with 25% clean breathing margin around all edges to withstand diagonal and geometric polygon mask cropping"
    else:  # bento_card_square, avatar_icon
        aspect_ratio = "1:1"
        framing = "centered isometric or macro product object framing on an elegant uniform studio background"

    # 2. Lighting & Kelvin
    if canvas_mode == "DARK_CANVAS":
        kelvin = 6500
        lighting = "dramatic directional rim lighting, cool-toned key light at 6500K, deep obsidian-navy shadows, subtle cyan/cobalt specular highlights"
        color_grade = f"color graded with deep navy shadow floor and electric highlights ({accent_hex}), low-key exposure blending seamlessly into dark slide background without white borders"
    elif canvas_mode == "WARM_PAPER":
        kelvin = 3800
        lighting = "soft diffused natural morning window light at 3800K, warm golden-hour fill, gentle low-contrast roll-off"
        color_grade = f"editorial film color grading on warm ecru paper tone, muted pastel accents ({accent_hex}), matte Kodak Portra aesthetic, zero harsh neon saturation"
    else:  # LIGHT_CANVAS
        kelvin = 5500
        lighting = "clean high-key industrial studio lighting at 5500K, crisp shadow definition, razor-sharp optical focus"
        color_grade = f"neutral daylight balance with subtle slate-metallic reflections ({accent_hex}) and high-contrast technical clarity"

    # 3. Assemble Prompt
    prompt_parts = [
        subject.strip(),
        framing,
        lighting,
        color_grade,
        "masterpiece commercial photography, 8k resolution, octane 3d render clarity",
    ]
    full_prompt = ", ".join(prompt_parts)

    negative_prompt = (
        "embedded text, letters, watermark, blurry, low resolution, random UI gibberish, "
        "harsh magenta/green color clash, oversaturated neon, cluttered background"
    )

    return {
        "prompt": full_prompt,
        "aspect_ratio": aspect_ratio,
        "lighting_kelvin": kelvin,
        "color_grade": color_grade,
        "negative_prompt": negative_prompt,
        "recommended_mask": "angled_chevron" if canvas_mode == "DARK_CANVAS" else ("soft_pill" if canvas_mode == "WARM_PAPER" else "rect_chamfer"),
    }
