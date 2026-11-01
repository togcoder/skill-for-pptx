#!/usr/bin/env python3
"""Multi-Domain Design Canons and Token Calculators.

Provides mathematical foundations, geometric tokens, and rule evaluators
for ArtCraft specialized domains:
  - Video (FilmCraft + SoundCraft)
  - Vector/SVG (VectorCraft + FigCraft)
  - 3D/Solid & PBR (SolidCraft + LightCraft)
  - Technical CAD (CADCraft - ISO 128 / 5457 / 7200)
  - Sound Mastering (SoundCraft - EBU R128)

Reference: lab/CHARTER.md, domains/
Consultation: Argon (Gemini 4) multi-domain canon specifications.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"


def _load_json(filename: str) -> Dict[str, Any]:
    path = KNOWLEDGE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Canon file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. Video Domain (FilmCraft + SoundCraft)
# ==============================================================================

def get_video_canon() -> Dict[str, Any]:
    """Load video design canons from knowledge/video_canon.json."""
    return _load_json("video_canon.json")


def calculate_action_safe_box(width: int, height: int, margin_percent: float = 3.5) -> Dict[str, int]:
    """Calculate SMPTE/EBU Action Safe bounding box (default 3.5% margin)."""
    dx = int(round(width * (margin_percent / 100.0)))
    dy = int(round(height * (margin_percent / 100.0)))
    return {
        "x_min": dx,
        "y_min": dy,
        "x_max": width - dx,
        "y_max": height - dy,
        "width": width - 2 * dx,
        "height": height - 2 * dy,
    }


def calculate_title_safe_box(width: int, height: int, margin_percent: float = 5.0) -> Dict[str, int]:
    """Calculate SMPTE/EBU Title Safe bounding box (default 5.0% margin)."""
    dx = int(round(width * (margin_percent / 100.0)))
    dy = int(round(height * (margin_percent / 100.0)))
    return {
        "x_min": dx,
        "y_min": dy,
        "x_max": width - dx,
        "y_max": height - dy,
        "width": width - 2 * dx,
        "height": height - 2 * dy,
    }


def is_in_vertical_9_16_dead_zone(x: float, y: float) -> Tuple[bool, Optional[str]]:
    """Determine if a coordinate in 1080x1920 falls within mobile UI dead zones."""
    # Top UI dead zone: y in [0, 220]
    if 0 <= y <= 220:
        return True, "top_ui_header"
    # Bottom caption / audio marquee dead zone: y in [1480, 1920]
    if 1480 <= y <= 1920:
        return True, "bottom_caption_audio"
    # Right action rail: x in [880, 1080] and y in [960, 1600]
    if 880 <= x <= 1080 and 960 <= y <= 1600:
        return True, "right_action_rail"
    return False, None


def validate_video_pacing(shot_duration_seconds: float, genre: str = "promo") -> Tuple[bool, str]:
    """Validate shot length against average shot length (ASL) canons."""
    if genre == "promo":
        if shot_duration_seconds < 1.2:
            return False, f"Shot duration {shot_duration_seconds:.2f}s is too fast (min 1.2s)"
        if shot_duration_seconds > 3.0:
            return False, f"Shot duration {shot_duration_seconds:.2f}s exceeds max static hold (3.0s)"
        return True, "OK"
    elif genre == "explainer":
        if shot_duration_seconds < 3.5:
            return False, f"Explainer shot {shot_duration_seconds:.2f}s is too brief (min 3.5s)"
        if shot_duration_seconds > 6.0:
            return False, f"Explainer shot {shot_duration_seconds:.2f}s exceeds maximum hold (6.0s)"
        return True, "OK (Ken Burns zoom recommended if > 4.0s)"
    return True, "OK"


def calculate_j_cut_frames(fps: float = 30.0) -> Tuple[int, int]:
    """Return recommended [min, max] lead frame count for J-cut audio lead."""
    return int(round(0.4 * fps)), int(round(0.8 * fps))


def calculate_l_cut_frames(fps: float = 30.0) -> Tuple[int, int]:
    """Return recommended [min, max] trail frame count for L-cut audio trail."""
    return int(round(0.5 * fps)), int(round(1.0 * fps))


def validate_audio_mastering(integrated_lufs: float, true_peak_dbtp: float, target: str = "web") -> Tuple[bool, List[str]]:
    """Verify integrated loudness and true peak against EBU R128 / ITU BS.1770-4."""
    issues = []
    target_lufs = -14.0 if target == "web" else -16.0
    tol = 1.0
    if abs(integrated_lufs - target_lufs) > tol:
        issues.append(f"Integrated loudness {integrated_lufs:.1f} LUFS outside target {target_lufs:.1f} ± {tol} LU")
    if true_peak_dbtp > -1.0:
        issues.append(f"True peak {true_peak_dbtp:.1f} dBTP exceeds ceiling of -1.0 dBTP")
    return len(issues) == 0, issues


# ==============================================================================
# 2. Vector / SVG Domain (VectorCraft + FigCraft)
# ==============================================================================

def get_vector_canon() -> Dict[str, Any]:
    """Load vector design canons from knowledge/vector_canon.json."""
    return _load_json("vector_canon.json")


def calculate_stroke_weight(
    target_size: float,
    base_size: float = 24.0,
    base_stroke: float = 2.0,
    exponent: float = 0.75
) -> float:
    """Calculate non-linear scaled stroke weight: W(S) = W0 * (S / S0)^0.75."""
    if target_size <= 0:
        raise ValueError("Target size must be positive")
    weight = base_stroke * math.pow(target_size / base_size, exponent)
    # Round to nearest 0.25 px for clean optical snapping
    return round(weight * 4.0) / 4.0


def calculate_bezier_circle_handle(radius: float) -> float:
    """Calculate cubic Bézier handle length kappa * radius for a 90-degree circular arc."""
    kappa = (4.0 / 3.0) * (math.sqrt(2.0) - 1.0)  # ~0.55228475
    return kappa * radius


def get_icon_optical_trim(shape: str = "circle") -> Dict[str, Any]:
    """Return standard 24x24 optical trim bounds."""
    canon = get_vector_canon()
    boxes = canon.get("icon_grid_24", {}).get("optical_trim_boxes", {})
    if shape not in boxes:
        raise KeyError(f"Unknown optical trim shape: {shape}. Valid: {list(boxes.keys())}")
    return boxes[shape]


def snap_node_coordinate(coord: float, stroke_weight: float) -> float:
    """Snap a coordinate to the pixel grid avoiding subpixel blur.
    
    If stroke weight is an even integer (e.g. 2.0), snap to whole integer.
    If stroke weight is an odd half-pixel (e.g. 1.5, 1.0), center on 0.5 boundary.
    """
    if abs(stroke_weight % 2.0) < 1e-4:
        return round(coord)
    else:
        return math.floor(coord) + 0.5


# ==============================================================================
# 3. 3D / Solid & PBR Domain (SolidCraft + LightCraft)
# ==============================================================================

def get_3d_canon() -> Dict[str, Any]:
    """Load 3D solid and rendering canons from knowledge/3d_solid_canon.json."""
    return _load_json("3d_solid_canon.json")


def calculate_micro_bevel_radius(width: float, height: float, depth: float) -> float:
    """Calculate minimum micro-bevel radius ensuring specular highlights.
    
    R = 0.005 * min(W, H, D), clamped to [0.2mm, 0.5mm].
    """
    min_dim = min(width, height, depth)
    r = 0.005 * min_dim
    return max(0.2, min(0.5, round(r, 3)))


def calculate_concentric_fillet(outer_radius: float, wall_thickness: float) -> float:
    """Calculate concentric inner fillet maintaining uniform wall thickness: R_in = max(0.5, R_out - T)."""
    return max(0.5, round(outer_radius - wall_thickness, 3))


def get_isometric_camera_angles() -> Dict[str, float]:
    """Return technical isometric projection angles."""
    # elevation = arctan(1 / sqrt(2)) ~ 35.264 degrees
    elevation = math.degrees(math.atan(1.0 / math.sqrt(2.0)))
    return {
        "azimuth_degrees": 45.0,
        "elevation_degrees": elevation,
    }


def calculate_three_point_lighting(bounding_radius_mm: float, style: str = "technical") -> Dict[str, Any]:
    """Calculate 3-point studio lighting rig positions and intensities."""
    rb = bounding_radius_mm
    fill_intensity = 0.50 if style == "technical" else 0.25
    return {
        "key_light": {
            "azimuth_deg": 40.0,
            "elevation_deg": 40.0,
            "distance_mm": round(3.5 * rb, 2),
            "intensity": 1.00,
            "source_radius_mm": round(0.8 * rb, 2),
            "color_temp_k": 5500,
        },
        "fill_light": {
            "azimuth_deg": -50.0,
            "elevation_deg": 20.0,
            "distance_mm": round(4.0 * rb, 2),
            "intensity": fill_intensity,
            "source_radius_mm": round(1.6 * rb, 2),
        },
        "rim_light": {
            "azimuth_deg": 140.0,
            "elevation_deg": 50.0,
            "distance_mm": round(2.5 * rb, 2),
            "intensity": 1.00,
        },
    }


def validate_pbr_material(metalness: float, roughness: float, albedo_rgb: Optional[Tuple[int, int, int]] = None) -> Tuple[bool, List[str]]:
    """Validate PBR physical plausibility rules."""
    issues = []
    if 0.2 < metalness < 0.8:
        issues.append(f"Ambiguous metalness {metalness:.2f}: uniform PBR materials must be dielectric (0.0) or conductor (1.0)")
    if not (0.0 <= roughness <= 1.0):
        issues.append(f"Roughness {roughness:.2f} out of valid [0.0, 1.0] range")
    if albedo_rgb:
        r, g, b = albedo_rgb
        # Luminance clamp check: min darks sRGB 30, max whites 243
        if r < 30 and g < 30 and b < 30:
            issues.append(f"Albedo RGB({r},{g},{b}) too dark for physical dielectric (min ~30 sRGB)")
        if r > 243 and g > 243 and b > 243:
            issues.append(f"Albedo RGB({r},{g},{b}) exceeds energy conservation ceiling (max 243 sRGB)")
    return len(issues) == 0, issues


# ==============================================================================
# 4. Technical CAD Domain (CADCraft - ISO 128 / 5457 / 7200)
# ==============================================================================

def get_cad_canon() -> Dict[str, Any]:
    """Load technical CAD drafting canons from knowledge/cad_iso_canon.json."""
    return _load_json("cad_iso_canon.json")


def get_iso_sheet_dimensions(sheet_format: str) -> Dict[str, Any]:
    """Return ISO 5457 sheet dimensions and margins in mm."""
    canon = get_cad_canon()
    sheets = canon.get("sheet_sizes_mm", {})
    fmt = sheet_format.upper()
    if fmt not in sheets:
        raise KeyError(f"Unknown sheet format: {sheet_format}. Valid: {list(sheets.keys())}")
    return sheets[fmt]


def get_iso_line_weight(layer_name: str, sheet_format: str = "A3") -> float:
    """Return ISO 128 line weight in mm for a given CAD layer and sheet format."""
    canon = get_cad_canon()
    fmt = sheet_format.upper()
    group_key = "group_0_7mm_a0_a1" if fmt in ("A0", "A1") else "group_0_5mm_a3_a4"
    group = canon.get("line_weight_hierarchy", {}).get(group_key, {})
    if layer_name not in group:
        raise KeyError(f"Unknown CAD layer: {layer_name}. Valid: {list(group.keys())}")
    return float(group[layer_name]["weight_mm"])


def calculate_dimension_offset_mm(tier_index: int = 1) -> float:
    """Calculate dimension line offset in mm from geometry outline (ISO 129)."""
    if tier_index < 1:
        raise ValueError("Tier index must be >= 1")
    if tier_index == 1:
        return 10.0  # Min 10mm for first tier
    return 10.0 + (tier_index - 1) * 7.0  # Min 7mm for each subsequent tier


def get_iso_7200_title_block_spec() -> Dict[str, Any]:
    """Return ISO 7200 title block geometric specifications."""
    canon = get_cad_canon()
    return canon.get("title_block_iso_7200", {})


# ==============================================================================
# 5. Sound Mastering Domain (SoundCraft)
# ==============================================================================

def get_sound_canon() -> Dict[str, Any]:
    """Load sound mastering canons from knowledge/sound_canon.json."""
    return _load_json("sound_canon.json")


def calculate_ducking_attenuation(dry_bgm_dbfs: float, delta_gain_db: float = -14.0) -> float:
    """Calculate resulting background music level during voiceover sidechain ducking."""
    return dry_bgm_dbfs + delta_gain_db
