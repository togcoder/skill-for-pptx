#!/usr/bin/env python3
"""Cross-Asset Pre-Processing Pipeline & Contract Validator (Protocol 04 / T044).

Enforces official owner mandate:
1. Never embed raw, unprocessed assets into final deliverables.
2. Pre-process images (cropping, alpha-masking, color grading) before slide/doc embedding.
3. Master audio (EBU R128 -14 LUFS, True Peak <= -1.0 dBTP) before video/motion pairing.
4. Validate structured data before chart presentation.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class CrossAssetPipelineError(ValueError):
    """Raised when an asset fails pre-processing or quality standards."""
    pass


def validate_image_for_embedding(
    image_input: Union[str, Path, Any],
    slot_type: str = "hero_full_bleed",
    canvas_mode: str = "DARK_CANVAS",
    min_width: int = 400,
    min_height: int = 300,
) -> Dict[str, Any]:
    """Validate and audit a raster image before embedding into PPTX, DOCX, or XLSX.
    
    Checks:
    - Minimum resolution and aspect ratio conformance.
    - Alpha channel presence and translucency for art washes.
    - Color harmony / luminance compatibility with canvas mode.
    """
    from PIL import Image

    if isinstance(image_input, (str, Path)):
        im = Image.open(image_input)
    else:
        im = image_input

    w, h = im.size
    aspect_ratio = float(w) / float(h)
    area_mp = (w * h) / 1_000_000.0

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Resolution Check
    if w < min_width or h < min_height:
        errors.append(f"Image resolution ({w}x{h}) is below required minimum ({min_width}x{min_height}).")

    # 2. Aspect Ratio & Framing Conformance
    if slot_type == "hero_full_bleed":
        expected_ratio = 16.0 / 9.0  # ~1.778
        if abs(aspect_ratio - expected_ratio) > 0.25:
            warnings.append(
                f"Aspect ratio {aspect_ratio:.2f} deviates from 16:9 full-bleed standard ({expected_ratio:.2f}). "
                "Recommendation: Crop with PhotoCraft/Pillow before embedding."
            )
    elif slot_type in ("split_vertical_panel", "angled_mask_feature"):
        expected_ratio = 4.0 / 5.0  # 0.80
        if abs(aspect_ratio - expected_ratio) > 0.25:
            warnings.append(
                f"Aspect ratio {aspect_ratio:.2f} deviates from vertical portrait standard ({expected_ratio:.2f})."
            )
    elif slot_type == "translucent_art_wash":
        if "A" not in im.getbands():
            errors.append(
                "Slot 'translucent_art_wash' strictly requires an Alpha channel (RGBA). "
                "The provided image has no alpha band."
            )
        else:
            alpha = im.getchannel("A")
            hist = alpha.histogram()
            total_px = w * h
            translucent_px = sum(hist[1:255])
            transparent_px = hist[0]
            if (translucent_px + transparent_px) / float(total_px) < 0.20:
                warnings.append(
                    "Art wash has low transparency/translucency (<20% non-opaque pixels). "
                    "May obscure slide background text."
                )

    # 3. Canvas Harmony Check
    im_rgb = im.convert("RGB")
    avg_color = im_rgb.resize((1, 1)).getpixel((0, 0))
    # Relative luminance
    r, g, b = [x / 255.0 for x in avg_color]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

    if canvas_mode == "DARK_CANVAS" and lum > 0.85 and slot_type == "hero_full_bleed":
        warnings.append(
            f"Image average luminance ({lum:.2f}) is very bright for a DARK_CANVAS deck. "
            "Recommendation: Apply a 20-30% dark tint overlay or vignette."
        )
    elif canvas_mode == "WARM_PAPER" and lum < 0.15 and slot_type == "hero_full_bleed":
        warnings.append(
            f"Image average luminance ({lum:.2f}) is very dark for a WARM_PAPER deck. "
            "Recommendation: Apply editorial warm color grade."
        )

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "width": w,
        "height": h,
        "aspect_ratio": round(aspect_ratio, 3),
        "area_megapixels": round(area_mp, 2),
        "has_alpha": "A" in im.getbands(),
        "errors": errors,
        "warnings": warnings,
    }


def validate_audio_for_muxing(
    integrated_lufs: float,
    true_peak_dbtp: float,
    has_voiceover: bool = True,
    bgm_ducking_db: Optional[float] = None,
) -> Dict[str, Any]:
    """Validate broadcast audio mastering standards (EBU R128 / SoundCraft Canon).
    
    Standards:
    - Integrated Loudness target: -14.0 LUFS (+- 1.0 LUFS).
    - True Peak limit: <= -1.0 dBTP (prohibits inter-sample clipping).
    - Auto-ducking: If voiceover present, BGM ducking should be in [-18.0, -10.0] dB.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. True Peak Check (Safety ceiling)
    if true_peak_dbtp > -1.0:
        errors.append(
            f"True Peak ({true_peak_dbtp:.1f} dBTP) exceeds broadcast ceiling of -1.0 dBTP. "
            "High risk of digital distortion / clipping."
        )

    # 2. Integrated Loudness Check
    if integrated_lufs > -12.0:
        errors.append(
            f"Integrated Loudness ({integrated_lufs:.1f} LUFS) is too loud (violates loudness penalty). "
            "Target is -14.0 LUFS."
        )
    elif integrated_lufs < -16.0:
        warnings.append(
            f"Integrated Loudness ({integrated_lufs:.1f} LUFS) is quiet. Target is -14.0 LUFS."
        )

    # 3. Auto-Ducking Check
    if has_voiceover and bgm_ducking_db is not None:
        if bgm_ducking_db > -10.0:
            warnings.append(
                f"BGM ducking attenuation ({bgm_ducking_db:.1f} dB) is insufficient. "
                "Voiceover may be drowned out by music (recommend -14 dB)."
            )

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "integrated_lufs": integrated_lufs,
        "true_peak_dbtp": true_peak_dbtp,
        "target_lufs": -14.0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_chart_data_for_presentation(
    series_data: List[Dict[str, Any]],
    chart_type: str = "clustered_column",
) -> Dict[str, Any]:
    """Validate structured data integrity before rendering charts in PPTX or DOCX.
    
    Standards:
    - No NaN, null, or division-by-zero values.
    - Edward Tufte clarity: Data density check, category label alignment.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not series_data:
        errors.append("Chart series data is completely empty.")
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    category_counts = []
    for s_idx, s in enumerate(series_data):
        name = s.get("name", f"Series_{s_idx}")
        values = s.get("values", [])
        if not values:
            errors.append(f"Series '{name}' contains no values.")
            continue

        for v_idx, val in enumerate(values):
            if val is None:
                errors.append(f"Series '{name}' has null value at index {v_idx}.")
            elif isinstance(val, float) and (val != val or val in (float('inf'), float('-inf'))):
                errors.append(f"Series '{name}' has NaN/Inf at index {v_idx}.")

        category_counts.append(len(values))

    # Check uniformity
    if len(set(category_counts)) > 1:
        errors.append(f"Series have mismatched value counts: {category_counts}.")

    # Tufte Cognitive Load Check
    if len(series_data) > 6:
        warnings.append(
            f"Too many data series ({len(series_data)}). Exceeds Miller 7+-2 cognitive load limit. "
            "Recommendation: Group secondary series into 'Other' or use small multiples."
        )

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "series_count": len(series_data),
        "point_count": category_counts[0] if category_counts else 0,
        "errors": errors,
        "warnings": warnings,
    }
