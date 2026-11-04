#!/usr/bin/env python3
"""VisualStyle/1 — a machine-readable design-style system for native PPTX (T067).

The style is not a mood board. It is a set of *roles* (colour, type, geometry,
material, depth, texture, image, motion, density) with enumerated values, plus
resolved build tokens. The builder imports this module; it never hard-codes a
hex, a corner radius or a duration. `check` audits a .pptx against its declared
preset, so "does this deck look like the style?" becomes a measurement.

EXPERIMENTAL: lives in the experiment folder; no product path imports it yet.

Usage:
  python visual_style.py presets
  python visual_style.py show liquid-glass
  python visual_style.py tokens liquid-glass -o tokens.json
  python visual_style.py check styles.pptx --styles editorial-crimson,liquid-glass
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

SCHEMA = "visual-style/1"

# Design-system bands (knowledge/design_system.json) used by validation.
BANDS = {
    "enter_ms": (250, 700),
    "move_ms": (400, 1200),
    "emphasis_ms": (250, 600),
    "morph_ms": (1000, 1600),
    "stagger_ms": (60, 150),
    "body_pt": (18, 40),
    "title_to_body": (1.5, 2.6),
    "words": (0, 45),
    "sizes": (3, 6),
}
LIMITS = {
    "enter_ms": (150, 1000),
    "move_ms": (250, 2000),
    "emphasis_ms": (150, 1200),
    "morph_ms": (500, 3000),
    "stagger_ms": (0, 400),
    "body_pt": (12, 60),
    "words": (0, 80),
    "sizes": (2, 9),
    "title_to_body": (1.2, 4.0),
}

ENUMS = {
    "geometry.language": {"sharp", "rounded", "blob", "diagonal", "mixed"},
    "geometry.radius_mode": {"none", "preset", "squircle"},
    "material.kind": {"flat", "paper", "glass", "clay", "collage", "chrome"},
    "material.fill": {"solid", "gradient", "translucent", "pattern", "mixed"},
    "depth.kind": {"flat", "layered", "2.5D", "3D"},
    "depth.shadow": {"none", "soft-contact", "ambient", "hard-offset"},
    "texture.kind": {"none", "grain", "halftone", "paper", "pattern"},
    "image.treatment": {
        "cutout-duotone", "cool-glass", "posterized-clay", "bw-editorial",
        "halftone-collage",
    },
    "image.mask": {"circle", "rounded", "blob", "rect", "none"},
    "motion.language": {"editorial", "fluid", "bouncy", "mechanical", "kinetic"},
    "motion.easing": {"standard", "enter", "expressive", "linear"},
}

ROLES = ("canvas", "surface", "surface_alt", "text", "text_muted", "accent",
         "accent_2", "accent_text", "ink")


# --------------------------------------------------------------------------- #
# Colour maths (WCAG only; the palette is authored, not generated)
# --------------------------------------------------------------------------- #
def _rgb(hex_value: str) -> tuple[int, int, int]:
    s = hex_value.strip().lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_value: str) -> float:
    r, g, b = (v / 255 for v in _rgb(hex_value))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------- #
# The five presets
# --------------------------------------------------------------------------- #
PRESETS: dict[str, dict[str, Any]] = {
    "editorial-crimson": {
        "schema": SCHEMA,
        "id": "editorial-crimson",
        "label_vi": "Biên tập — đỏ son",
        "intent": "A printed journal page: one loud field, one serif voice, gold thread.",
        "color": {
            "roles": {
                "canvas": "#C1121F", "surface": "#7A0C14", "surface_alt": "#F7F1E8",
                "text": "#F7F1E8", "text_muted": "#E7C9C4", "accent": "#E8B04B",
                "accent_2": "#F2C9C9", "accent_text": "#FFD98A", "ink": "#1A0508",
            },
            "contrast_pairs": [["text", "canvas"], ["text", "surface"],
                               ["accent_text", "surface"], ["ink", "accent"]],
            "family": "warm-red",
            "canvas_mode": "DARK",
            "tint_rule": "only alpha on a role colour; no invented hex",
        },
        "type": {
            "display": {"family": "Palatino Linotype", "weight": 400, "case": "sentence",
                        "tracking_em": -0.01, "line_height": 1.02},
            "body": {"family": "Arial", "weight": 400, "line_height": 1.25},
            "label": {"family": "Arial", "weight": 700, "case": "upper",
                      "tracking_em": 0.16},
            "scale_pt": {"display": 42, "title": 34, "body": 20, "label": 12, "micro": 10},
        },
        "geometry": {
            "language": "sharp", "corner_radius_pt": 0, "radius_mode": "none",
            "stroke_pt": 1.0, "image_frame": "circle",
            "vocab": ["full-bleed field", "hairline rule", "gold thread", "circle crop"],
        },
        "material": {"kind": "flat", "fill": "solid", "alpha_range": [1.0, 1.0]},
        "depth": {"kind": "flat", "layers": 1, "shadow": "none", "bevel_pt": 0,
                  "specular": False},
        "texture": {"kind": "none", "native": "none", "opacity": 0.0},
        "image": {
            "treatment": "cutout-duotone", "mask": "circle", "edge_pt": 0,
            "grade": {"mode": "duotone", "shadow": "#5A0710", "highlight": "#F7F1E8",
                      "posterize": None},
            "overlay": {"kind": "none", "alpha": 0.0},
            "area_share_max": 0.34, "aspect": "1:1",
        },
        "motion": {
            "language": "editorial", "enter_ms": 420, "move_ms": 620,
            "emphasis_ms": 380, "morph_ms": 1200, "stagger_ms": 90,
            "easing": "standard", "overshoot": 0.0,
            "verbs": ["wipe-up", "wipe-left", "fade", "zoom"],
            "grammar": "type first, rule under it, facts as a pair, portrait last",
        },
        "density": {"words_max": 34, "elements_max": 14, "negative_space": 0.55},
        "native": {
            "effects": ["solid fill", "alpha", "1 pt line", "circle crop (baked alpha)"],
            "impossible": ["paper grain without a raster tile", "true letterpress ink"],
            "expensive": ["per-glyph optical alignment", "real foil"],
        },
        "do": ["one crimson field, no gradient", "cream type only, gold for small labels",
               "sharp 0 pt corners", "portrait cropped by a circle, never a rectangle"],
        "dont": ["drop shadows", "rounded cards", "more than 2 type families",
                 "gold for body text (contrast)"],
    },
    "liquid-glass": {
        "schema": SCHEMA,
        "id": "liquid-glass",
        "label_vi": "Kính lỏng",
        "intent": "Frosted panes floating over a dark, coloured light field.",
        "color": {
            "roles": {
                "canvas": "#070B1E", "surface": "#141B3A", "surface_alt": "#1E2750",
                "text": "#F2F6FF", "text_muted": "#AFC0E8", "accent": "#7CC7FF",
                "accent_2": "#B39DFF", "accent_text": "#DFF3FF", "ink": "#02040C",
            },
            "contrast_pairs": [["text", "canvas"], ["text", "surface"],
                               ["accent_text", "surface"], ["accent", "canvas"]],
            "family": "deep-indigo",
            "canvas_mode": "DARK",
            "tint_rule": "translucent white/role tints only; glow orbs are role colours",
        },
        "type": {
            "display": {"family": "Segoe UI Light", "weight": 300, "case": "sentence",
                        "tracking_em": -0.015, "line_height": 1.06},
            "body": {"family": "Segoe UI", "weight": 400, "line_height": 1.3},
            "label": {"family": "Segoe UI Semibold", "weight": 600, "case": "upper",
                      "tracking_em": 0.12},
            "scale_pt": {"display": 40, "title": 30, "body": 18, "label": 11, "micro": 10},
        },
        "geometry": {
            "language": "rounded", "corner_radius_pt": 26, "radius_mode": "preset",
            "stroke_pt": 0.75, "image_frame": "rounded",
            "vocab": ["rounded pane", "pill", "soft orb", "hairline rim", "specular line"],
        },
        "material": {"kind": "glass", "fill": "translucent", "alpha_range": [0.08, 0.34]},
        "depth": {"kind": "layered", "layers": 3, "shadow": "ambient", "bevel_pt": 1.5,
                  "specular": True},
        "texture": {"kind": "none", "native": "none", "opacity": 0.0},
        "image": {
            "treatment": "cool-glass", "mask": "rounded", "edge_pt": 0,
            "grade": {"mode": "duotone", "shadow": "#0A1030", "highlight": "#DCE9FF",
                      "posterize": None},
            "overlay": {"kind": "glass-sheet", "alpha": 0.28},
            "area_share_max": 0.32, "aspect": "4:5",
        },
        "motion": {
            "language": "fluid", "enter_ms": 620, "move_ms": 900,
            "emphasis_ms": 520, "morph_ms": 1500, "stagger_ms": 110,
            "easing": "expressive", "overshoot": 0.02,
            "verbs": ["fade", "float-in", "zoom"],
            "grammar": "panes fade up together; the image settles last; nothing snaps",
        },
        "density": {"words_max": 30, "elements_max": 18, "negative_space": 0.6},
        "native": {
            "effects": ["solidFill + alpha", "gradFill (radial)", "outerShdw",
                        "softEdge", "ln + alpha", "bevel (rim)"],
            "impossible": ["backdrop blur / true refraction", "chromatic dispersion",
                           "specular highlight that follows the cursor", "noise-free frosted blur"],
            "expensive": ["fake blur needs a pre-blurred raster copy per panel",
                          "glass over live text loses contrast"],
        },
        "do": ["one light source, top-left", "white rim at 35-45 % alpha",
               "panes at 8-20 % fill", "shadow large, low alpha"],
        "dont": ["glass on glass on glass", "opaque cards (kills the material)",
                 "hard 1 pt black outlines", "saturated glow behind body text"],
    },
    "clay-cartoon": {
        "schema": SCHEMA,
        "id": "clay-cartoon",
        "label_vi": "Đất sét — hoạt hình",
        "intent": "A chunky matte toy: squishy corners, thick rims, no sharp edge anywhere.",
        "color": {
            "roles": {
                "canvas": "#FFF3E2", "surface": "#FFE2C6", "surface_alt": "#FFD1AE",
                "text": "#3B2A22", "text_muted": "#7A5A4A", "accent": "#E2725B",
                "accent_2": "#1F7A6E", "accent_3": "#F2B24C",
                "accent_text": "#FFF8F0", "ink": "#2A1B14",
            },
            "contrast_pairs": [["text", "canvas"], ["text", "surface"],
                               ["accent_text", "accent_2"], ["ink", "canvas"]],
            "family": "cream-terracotta",
            "canvas_mode": "LIGHT",
            "tint_rule": "flat role colours only; no gradients inside clay",
        },
        "type": {
            "display": {"family": "Segoe UI Black", "weight": 900, "case": "sentence",
                        "tracking_em": -0.02, "line_height": 1.0},
            "body": {"family": "Segoe UI Semibold", "weight": 600, "line_height": 1.25},
            "label": {"family": "Segoe UI", "weight": 700, "case": "upper",
                      "tracking_em": 0.08},
            "scale_pt": {"display": 42, "title": 30, "body": 18, "label": 11, "micro": 10},
        },
        "geometry": {
            "language": "blob", "corner_radius_pt": 30, "radius_mode": "squircle",
            "stroke_pt": 6.0, "image_frame": "blob",
            "vocab": ["squircle", "blob", "pill", "sticker circle", "thick rim"],
        },
        "material": {"kind": "clay", "fill": "solid", "alpha_range": [1.0, 1.0]},
        "depth": {"kind": "2.5D", "layers": 2, "shadow": "soft-contact", "bevel_pt": 6,
                  "specular": False},
        "texture": {"kind": "none", "native": "none", "opacity": 0.0},
        "image": {
            "treatment": "posterized-clay", "mask": "blob", "edge_pt": 8,
            "grade": {"mode": "posterize", "shadow": "#5A3A2E", "highlight": "#FFE9CF",
                      "posterize": 6},
            "overlay": {"kind": "none", "alpha": 0.0},
            "area_share_max": 0.33, "aspect": "4:5",
        },
        "motion": {
            "language": "bouncy", "enter_ms": 300, "move_ms": 520,
            "emphasis_ms": 360, "morph_ms": 1000, "stagger_ms": 80,
            "easing": "expressive", "overshoot": 0.06,
            "verbs": ["zoom", "float-in", "pulse"],
            "grammar": "title pops, image squishes in, each fact lands on its own beat",
        },
        "density": {"words_max": 28, "elements_max": 16, "negative_space": 0.5},
        "native": {
            "effects": ["roundRect + adj", "custGeom squircle (DeckCraft smoothCorners)",
                        "bevelT + sp3d", "outerShdw", "thick ln"],
            "impossible": ["true soft-body deformation / squash animation",
                           "clay fingerprint texture without a raster tile",
                           "real ambient occlusion between touching shapes"],
            "expensive": ["each blob is a custGeom (~40 path points) to edit",
                          "3D bevel on text is heavy and hard to keep legible"],
        },
        "do": ["one thick cream rim on the hero object", "matte fill, no gradient",
               "shadows short and soft (dist 6-10 pt)", "rotate stickers 2-8 degrees"],
        "dont": ["thin hairlines", "glass transparency", "more than 3 object colours",
                 "long text in the display face"],
    },
    "swiss-minimal": {
        "schema": SCHEMA,
        "id": "swiss-minimal",
        "label_vi": "Thụy Sĩ — tối giản",
        "intent": "A grid, one red, and type doing all the work.",
        "color": {
            "roles": {
                "canvas": "#F7F7F5", "surface": "#FFFFFF", "surface_alt": "#EDEDEA",
                "text": "#111111", "text_muted": "#6B6B6B", "accent": "#E30613",
                "accent_2": "#111111", "accent_text": "#FFFFFF", "ink": "#000000",
            },
            "contrast_pairs": [["text", "canvas"], ["text", "surface"],
                               ["accent_text", "accent"], ["text_muted", "canvas"]],
            "family": "paper-black-red",
            "canvas_mode": "LIGHT",
            "tint_rule": "black, paper and one red; nothing else",
        },
        "type": {
            "display": {"family": "Arial", "weight": 700, "case": "sentence",
                        "tracking_em": -0.03, "line_height": 0.98},
            "body": {"family": "Arial", "weight": 400, "line_height": 1.3},
            "label": {"family": "Arial", "weight": 700, "case": "upper",
                      "tracking_em": 0.18},
            "scale_pt": {"display": 54, "title": 28, "body": 18, "label": 9, "micro": 9},
        },
        "geometry": {
            "language": "sharp", "corner_radius_pt": 0, "radius_mode": "none",
            "stroke_pt": 0.5, "image_frame": "rect",
            "vocab": ["12-column grid", "hairline rule", "flush-left type", "square crop"],
        },
        "material": {"kind": "paper", "fill": "solid", "alpha_range": [1.0, 1.0]},
        "depth": {"kind": "flat", "layers": 1, "shadow": "none", "bevel_pt": 0,
                  "specular": False},
        "texture": {"kind": "paper", "native": "solid tint", "opacity": 0.0},
        "image": {
            "treatment": "bw-editorial", "mask": "rect", "edge_pt": 0,
            "grade": {"mode": "grayscale", "shadow": "#000000", "highlight": "#FFFFFF",
                      "posterize": None},
            "overlay": {"kind": "none", "alpha": 0.0},
            "area_share_max": 0.16, "aspect": "1:1",
        },
        "motion": {
            "language": "mechanical", "enter_ms": 250, "move_ms": 400,
            "emphasis_ms": 250, "morph_ms": 1000, "stagger_ms": 60,
            "easing": "standard", "overshoot": 0.0,
            "verbs": ["fade", "wipe-left"],
            "grammar": "nothing moves for effect; text appears, rules draw, done",
        },
        "density": {"words_max": 18, "elements_max": 12, "negative_space": 0.7},
        "native": {
            "effects": ["solid fill", "hairline line", "image recolor (grayscale)"],
            "impossible": ["a true baseline grid locked to the type",
                           "optical kerning per pair", "hairline thinner than 0.25 pt"],
            "expensive": ["manual optical alignment of every numeral",
                          "grid that survives 4:3"],
        },
        "do": ["one axis, one alignment", "image small and quiet", "rules at 0.5-0.75 pt",
               "numbers as data, not decoration"],
        "dont": ["centred text", "shadows", "more than one accent use per slide",
                 "rounded anything"],
    },
    "maximalist-collage": {
        "schema": SCHEMA,
        "id": "maximalist-collage",
        "label_vi": "Cắt dán — cực đại",
        "intent": "A wall of torn paper, halftone and stickers that still reads in one pass.",
        "color": {
            "roles": {
                "canvas": "#F4E9D8", "surface": "#FFE9C9", "surface_alt": "#E8D5BC",
                "text": "#141414", "text_muted": "#5B4A3F", "accent": "#D7261B",
                "accent_2": "#1D4ED8", "accent_3": "#FFD400",
                "accent_text": "#FFF8EE", "ink": "#000000",
            },
            "contrast_pairs": [["text", "canvas"], ["text", "surface"],
                               ["accent_text", "accent"], ["accent_text", "accent_2"]],
            "family": "clash-paper",
            "canvas_mode": "LIGHT",
            "tint_rule": "roles only; pattern fills add black at <= 12 % alpha",
        },
        "type": {
            "display": {"family": "Arial", "weight": 700, "case": "upper",
                        "tracking_em": -0.02, "line_height": 0.92},
            "body": {"family": "Arial", "weight": 400, "line_height": 1.25},
            "label": {"family": "Arial", "weight": 700, "case": "upper",
                      "tracking_em": 0.1},
            "scale_pt": {"display": 58, "title": 30, "body": 18, "label": 10, "micro": 8},
        },
        "geometry": {
            "language": "mixed", "corner_radius_pt": 4, "radius_mode": "preset",
            "stroke_pt": 3.0, "image_frame": "rect",
            "vocab": ["torn strip", "sticker", "tape", "thick outline", "rotated card"],
        },
        "material": {"kind": "collage", "fill": "mixed", "alpha_range": [0.35, 1.0]},
        "depth": {"kind": "layered", "layers": 4, "shadow": "hard-offset", "bevel_pt": 0,
                  "specular": False},
        "texture": {"kind": "halftone", "native": "pattFill pct20", "opacity": 0.1},
        "image": {
            "treatment": "halftone-collage", "mask": "rect", "edge_pt": 0,
            "grade": {"mode": "posterize", "shadow": "#141414", "highlight": "#F4E9D8",
                      "posterize": 4},
            "overlay": {"kind": "halftone", "alpha": 0.18},
            "area_share_max": 0.28, "aspect": "4:5",
        },
        "motion": {
            "language": "kinetic", "enter_ms": 260, "move_ms": 460,
            "emphasis_ms": 300, "morph_ms": 1000, "stagger_ms": 60,
            "easing": "standard", "overshoot": 0.03,
            "verbs": ["wipe-up", "zoom", "fade"],
            "grammar": "three hits, then stop; collage must not keep moving",
        },
        "density": {"words_max": 40, "elements_max": 24, "negative_space": 0.35},
        "native": {
            "effects": ["pattFill (pct20/pct10)", "outerShdw blur=0 hard offset",
                        "thick ln", "rotation", "picture recolor"],
            "impossible": ["real torn-paper fibres", "multi-layer blend modes",
                           "true halftone screen on type", "clipping masks across shapes"],
            "expensive": ["one custGeom per tear (~20 points)", "many rotated text boxes"],
        },
        "do": ["anchor one straight horizontal rail", "keep 3 text sizes only",
               "rotate between -8 and +8 degrees", "one focal sticker per slide"],
        "dont": ["more than 4 accent blocks", "halftone over body text",
                 "symmetry", "clean vector icons"],
    },
}


# --------------------------------------------------------------------------- #
# Validation and resolution
# --------------------------------------------------------------------------- #
def _family_key(name: str) -> str:
    """Segoe UI Light/Semibold/Black are one superfamily, not three."""
    base = re.sub(r"\s+(Light|SemiLight|Semibold|SemiBold|Bold|Black|Heavy|Condensed)$",
                  "", name.strip())
    return base.lower()


def validate_preset(p: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warns: list[str] = []
    for role in ROLES:
        value = p.get("color", {}).get("roles", {}).get(role)
        if not value or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value or ""):
            errors.append(f"color.roles.{role}: expected #RRGGBB, got {value!r}")
    for path, allowed in ENUMS.items():
        node: Any = p
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if node not in allowed:
            errors.append(f"{path}: {node!r} not in {sorted(allowed)}")

    roles = p.get("color", {}).get("roles", {})
    for a, b in p.get("color", {}).get("contrast_pairs", []):
        if a not in roles or b not in roles:
            errors.append(f"contrast pair {a}/{b}: unknown role")
            continue
        ratio = contrast(roles[a], roles[b])
        need = 3.0 if (a in ("accent", "accent_2") and b == "canvas") else 4.5
        if ratio + 1e-9 < need:
            errors.append(f"contrast {a} on {b}: {ratio:.2f} < {need:.1f}")

    scale = p.get("type", {}).get("scale_pt", {})
    sizes = sorted({v for v in scale.values() if isinstance(v, (int, float))}, reverse=True)
    if not (LIMITS["sizes"][0] <= len(sizes) <= LIMITS["sizes"][1]):
        errors.append(f"type.scale_pt: {len(sizes)} distinct sizes outside {LIMITS['sizes']}")
    elif not (BANDS["sizes"][0] <= len(sizes) <= BANDS["sizes"][1]):
        warns.append(f"type.scale_pt: {len(sizes)} sizes outside band {BANDS['sizes']}")
    body = scale.get("body", 0)
    if not (LIMITS["body_pt"][0] <= body <= LIMITS["body_pt"][1]):
        errors.append(f"type.scale_pt.body {body} outside {LIMITS['body_pt']}")
    elif not (BANDS["body_pt"][0] <= body <= BANDS["body_pt"][1]):
        warns.append(f"type.scale_pt.body {body} pt below the 18 pt band")
    if scale.get("title") and body:
        ratio = scale["title"] / body
        if not (LIMITS["title_to_body"][0] <= ratio <= LIMITS["title_to_body"][1]):
            warns.append(f"title/body {ratio:.2f} outside {LIMITS['title_to_body']}")

    families = {p["type"][k]["family"] for k in ("display", "body", "label") if k in p["type"]}
    superfamilies = {_family_key(f) for f in families}
    if len(superfamilies) > 2:
        errors.append(f"type: {len(superfamilies)} families ({sorted(families)}), max 2")

    motion = p.get("motion", {})
    for key in ("enter_ms", "move_ms", "emphasis_ms", "morph_ms", "stagger_ms"):
        value = motion.get(key)
        if not isinstance(value, int):
            errors.append(f"motion.{key}: expected int ms")
        elif not (LIMITS[key][0] <= value <= LIMITS[key][1]):
            errors.append(f"motion.{key} {value} outside limit {LIMITS[key]}")
        elif not (BANDS[key][0] <= value <= BANDS[key][1]):
            warns.append(f"motion.{key} {value} outside band {BANDS[key]}")

    density = p.get("density", {})
    if not (0 <= density.get("negative_space", -1) <= 0.9):
        errors.append("density.negative_space outside 0..0.9")
    if not (LIMITS["words"][0] <= density.get("words_max", -1) <= LIMITS["words"][1]):
        errors.append("density.words_max outside limit")

    return {"ok": not errors, "errors": errors, "warnings": warns}


def resolve(preset: dict[str, Any]) -> dict[str, Any]:
    """Turn the style roles into the numbers a builder needs."""
    c = preset["color"]["roles"]
    t = preset["type"]
    s = t["scale_pt"]
    g = preset["geometry"]
    m = preset["material"]
    d = preset["depth"]
    x = preset["texture"]
    i = preset["image"]
    mo = preset["motion"]

    shadow_map = {
        "none": None,
        "soft-contact": {"color": c["ink"], "blur_pt": 18, "dist_pt": 8, "dir_deg": 90,
                         "transparency": 0.72},
        "ambient": {"color": c["ink"], "blur_pt": 48, "dist_pt": 22, "dir_deg": 90,
                    "transparency": 0.6},
        "hard-offset": {"color": c["ink"], "blur_pt": 0, "dist_pt": 6, "dir_deg": 45,
                        "transparency": 0.0},
    }
    return {
        "schema": SCHEMA,
        "id": preset["id"],
        "label_vi": preset["label_vi"],
        "palette": {k: v.lstrip("#").upper() for k, v in c.items()},
        "type": {
            "families": {role: t[role]["family"] for role in ("display", "body", "label")},
            "sizes_pt": dict(s),
            "tracking_em": {role: t[role].get("tracking_em", 0.0)
                            for role in ("display", "body", "label")},
            "line_height": {role: t[role].get("line_height", 1.2)
                            for role in ("display", "body", "label")},
        },
        "geometry": {
            "radius_pt": g["corner_radius_pt"], "smooth": g["radius_mode"] == "squircle",
            "stroke_pt": g["stroke_pt"], "image_frame": g["image_frame"],
        },
        "material": {"kind": m["kind"], "fill": m["fill"], "alpha": m["alpha_range"]},
        "depth": {"kind": d["kind"], "shadow": shadow_map[d["shadow"]],
                  "bevel_pt": d["bevel_pt"], "specular": d["specular"]},
        "texture": {"kind": x["kind"], "opacity": x["opacity"]},
        "image": i,
        "motion": {k: mo[k] for k in ("enter_ms", "move_ms", "emphasis_ms",
                                      "morph_ms", "stagger_ms", "easing", "overshoot")},
        "density": preset["density"],
        "contrast": {f"{a}/{b}": round(contrast(c[a], c[b]), 2)
                     for a, b in preset["color"]["contrast_pairs"]},
    }


def get(preset_id: str) -> dict[str, Any]:
    if preset_id not in PRESETS:
        raise SystemExit(f"unknown style {preset_id!r}; have {sorted(PRESETS)}")
    return PRESETS[preset_id]


# --------------------------------------------------------------------------- #
# Style lint: audit a built deck against its declared preset
# --------------------------------------------------------------------------- #
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def _slide_xml(pptx: Path, index: int) -> str:
    with zipfile.ZipFile(pptx) as z:
        return z.read(f"ppt/slides/slide{index + 1}.xml").decode("utf-8")


def check_deck(pptx: Path, style_ids: list[str]) -> dict[str, Any]:
    import xml.etree.ElementTree as ET

    out: dict[str, Any] = {"file": pptx.name, "bytes": pptx.stat().st_size, "slides": []}
    for idx, style_id in enumerate(style_ids):
        p = get(style_id)
        tokens = resolve(p)
        allowed = {v.upper() for v in tokens["palette"].values()}
        families = set(tokens["type"]["families"].values())
        xml = _slide_xml(pptx, idx)
        root = ET.fromstring(xml)

        colours = [c.attrib["val"].upper() for c in root.findall(".//a:srgbClr", NS)
                   if "val" in c.attrib]
        unknown = sorted({c for c in colours if c not in allowed})
        fonts = {f.attrib["typeface"] for f in root.findall(".//a:latin", NS)
                 if f.attrib.get("typeface")}
        known_fonts = {f for f in fonts if f in families}
        shapes = root.findall(".//p:sp", NS) + root.findall(".//p:pic", NS)
        pictures = root.findall(".//p:pic", NS)
        effects = root.findall(".//a:effectLst", NS)
        three_d = root.findall(".//a:sp3d", NS)
        gradient = root.findall(".//a:gradFill", NS)
        pattern = root.findall(".//a:pattFill", NS)

        # raster share: sum of picture extents / slide area
        slide_w = int(ET.fromstring(
            zipfile.ZipFile(pptx).read("ppt/presentation.xml")).find(".//p:sldSz", NS)
            .attrib.get("cx", 12192000))
        slide_h = int(ET.fromstring(
            zipfile.ZipFile(pptx).read("ppt/presentation.xml")).find(".//p:sldSz", NS)
            .attrib.get("cy", 6858000))
        area = 0
        for pic in pictures:
            ext = pic.find(".//a:xfrm/a:ext", NS)
            if ext is not None:
                area += int(ext.attrib.get("cx", 0)) * int(ext.attrib.get("cy", 0))
        share = area / (slide_w * slide_h) if slide_w and slide_h else 0

        out["slides"].append({
            "index": idx + 1,
            "style": style_id,
            "colours_used": len(set(colours)),
            "unknown_colours": unknown,
            "fonts_used": sorted(fonts),
            "unknown_fonts": sorted(fonts - known_fonts),
            "shapes": len(shapes),
            "pictures": len(pictures),
            "native_share": round((len(shapes) - len(pictures)) / max(1, len(shapes)), 3),
            "effect_lists": len(effects),
            "sp3d": len(three_d),
            "gradient_fills": len(gradient),
            "pattern_fills": len(pattern),
            "raster_area_share": round(share, 3),
            "raster_within_style": share <= p["image"]["area_share_max"] + 0.02,
            "palette_ok": not unknown,
            "fonts_ok": not (fonts - known_fonts),
        })
    out["pass"] = all(s["palette_ok"] and s["fonts_ok"] and s["raster_within_style"]
                      for s in out["slides"])
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("presets")
    show = sub.add_parser("show")
    show.add_argument("style")
    tok = sub.add_parser("tokens")
    tok.add_argument("style")
    tok.add_argument("-o", "--out")
    chk = sub.add_parser("check")
    chk.add_argument("pptx")
    chk.add_argument("--styles", required=True,
                     help="comma-separated style ids, one per slide, in order")
    chk.add_argument("-o", "--out")
    ns = ap.parse_args(argv)

    if ns.cmd == "presets":
        print(json.dumps({k: {"label_vi": v["label_vi"], "intent": v["intent"]}
                          for k, v in PRESETS.items()}, ensure_ascii=False, indent=2))
        return 0
    if ns.cmd == "show":
        p = get(ns.style)
        print(json.dumps({"preset": p, "validation": validate_preset(p),
                          "tokens": resolve(p)}, ensure_ascii=False, indent=2))
        return 0
    if ns.cmd == "tokens":
        tokens = resolve(get(ns.style))
        text = json.dumps(tokens, ensure_ascii=False, indent=2)
        if ns.out:
            Path(ns.out).write_text(text, encoding="utf-8")
            print(f"wrote {ns.out}")
        else:
            print(text)
        return 0
    if ns.cmd == "check":
        report = check_deck(Path(ns.pptx), [s.strip() for s in ns.styles.split(",")])
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if ns.out:
            Path(ns.out).write_text(text, encoding="utf-8")
            print(f"wrote {ns.out} pass={report['pass']}")
        else:
            print(text)
        return 0 if report["pass"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
