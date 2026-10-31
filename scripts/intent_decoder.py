#!/usr/bin/env python3
"""Intent & Empathy Decoder Engine (T037).

Implements Protocol 00: parses raw user prompts into structured, human-centric
5-dimensional ``IntentBrief`` documents complying with ``schemas/intent_brief.schema.json``.

Ensures AI agents decode audience psychology, cognitive budget, and viewing context
before touching any tool.

Usage:
    python scripts/intent_decoder.py "Tạo slide báo cáo Q3 cho ban giám đốc"
    python scripts/intent_decoder.py "Vẽ sơ đồ luồng hệ thống server" -o brief.json
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.validate_handoff import validate_dict, load_schema
except ImportError:
    from validate_handoff import validate_dict, load_schema


def decode_intent(prompt: str, intent_id: str | None = None) -> dict[str, Any]:
    if not intent_id:
        intent_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    text = prompt.lower()

    # 1. Audience Persona detection
    if any(k in text for k in ["giám đốc", "c-level", "ceo", "cfo", "cto", "lãnh đạo", "executive", "board", "hội đồng"]):
        audience = {
            "archetype": "executive_c_level",
            "primary_need": "Executive summary and high-level strategic/financial decision",
            "emotional_tone": "authoritative_minimal"
        }
        canonical = {
            "design_language": "swiss_grid",
            "base_grid_unit_px": 8,
            "modular_scale_ratio": 1.333
        }
        cognitive = {
            "max_visual_groups": 3,
            "max_words_per_view": 35,
            "eye_tracking_pattern": "z_pattern",
            "target_seconds_to_comprehend": 3.0
        }
    elif any(k in text for k in ["kỹ thuật", "kỹ sư", "engineer", "dev", "sơ đồ", "mặt cắt", "spc", "bug", "lỗi", "architecture"]):
        audience = {
            "archetype": "technical_engineer",
            "primary_need": "Technical accuracy, data traceability, and architectural clarity",
            "emotional_tone": "objective_scientific"
        }
        canonical = {
            "design_language": "edward_tufte_data",
            "base_grid_unit_px": 4,
            "modular_scale_ratio": 1.2
        }
        cognitive = {
            "max_visual_groups": 4,
            "max_words_per_view": 60,
            "eye_tracking_pattern": "f_pattern",
            "target_seconds_to_comprehend": 5.0
        }
    elif any(k in text for k in ["học sinh", "sinh viên", "giáo trình", "bài giảng", "student", "education"]):
        audience = {
            "archetype": "educational_student",
            "primary_need": "Concept comprehension and knowledge retention",
            "emotional_tone": "inspiring_human"
        }
        canonical = {
            "design_language": "material3_dynamic",
            "base_grid_unit_px": 8,
            "modular_scale_ratio": 1.25
        }
        cognitive = {
            "max_visual_groups": 3,
            "max_words_per_view": 50,
            "eye_tracking_pattern": "z_pattern",
            "target_seconds_to_comprehend": 4.0
        }
    elif any(k in text for k in ["khách hàng", "bán hàng", "pitch", "quảng cáo", "sale", "client", "commercial"]):
        audience = {
            "archetype": "commercial_client",
            "primary_need": "Value proposition and persuasive engagement",
            "emotional_tone": "premium_editorial"
        }
        canonical = {
            "design_language": "swiss_grid",
            "base_grid_unit_px": 8,
            "modular_scale_ratio": 1.414
        }
        cognitive = {
            "max_visual_groups": 3,
            "max_words_per_view": 40,
            "eye_tracking_pattern": "z_pattern",
            "target_seconds_to_comprehend": 3.0
        }
    else:
        audience = {
            "archetype": "general_public",
            "primary_need": "Immediate clarity and engagement",
            "emotional_tone": "inspiring_human"
        }
        canonical = {
            "design_language": "dieter_rams_minimal",
            "base_grid_unit_px": 8,
            "modular_scale_ratio": 1.25
        }
        cognitive = {
            "max_visual_groups": 4,
            "max_words_per_view": 45,
            "eye_tracking_pattern": "z_pattern",
            "target_seconds_to_comprehend": 3.5
        }

    # 2. Craft Routing
    if any(k in text for k in ["slide", "thuyết trình", "deck", "powerpoint", "pptx", "bài giảng"]):
        primary_craft = "deckcraft"
        supporting = []
        if any(k in text for k in ["sơ đồ", "icon", "vector", "logo"]):
            supporting.append("vectorcraft")
        if any(k in text for k in ["bảng", "doanh thu", "số liệu", "tài chính", "chart", "biểu đồ"]):
            supporting.append("gridcraft")
    elif any(k in text for k in ["văn bản", "tài liệu", "hợp đồng", "báo cáo dài", "word", "docx", "nghiên cứu"]):
        primary_craft = "wordcraft"
        supporting = ["gridcraft"] if "biểu đồ" in text or "số liệu" in text else []
    elif any(k in text for k in ["bảng tính", "excel", "xlsx", "tính toán", "kế toán", "bảng lương"]):
        primary_craft = "gridcraft"
        supporting = []
    elif any(k in text for k in ["vector", "vẽ", "logo", "icon", "sơ đồ khối", "svg"]):
        primary_craft = "vectorcraft"
        supporting = []
    else:
        # Default presentation
        primary_craft = "deckcraft"
        supporting = ["vectorcraft"]

    # 3. Viewing context
    if any(k in text for k in ["máy chiếu", "phòng họp", "hội trường", "projector"]):
        viewing = {
            "medium": "projector_bright_room",
            "resolution": "1920x1080",
            "safe_min_font_pt": 18.0,
            "lighting": "bright_ambient"
        }
    elif any(k in text for k in ["in", "in ấn", "a4", "paper", "print"]):
        viewing = {
            "medium": "print_a4_cmyk",
            "resolution": "2480x3508",
            "safe_min_font_pt": 9.0,
            "lighting": "bright_ambient"
        }
    else:
        viewing = {
            "medium": "laptop_desktop_screen",
            "resolution": "1920x1080",
            "safe_min_font_pt": 12.0,
            "lighting": "bright_ambient"
        }

    brief = {
        "intent_id": intent_id,
        "raw_user_prompt": prompt,
        "audience_persona": audience,
        "cognitive_budget": cognitive,
        "viewing_context": viewing,
        "canonical_system": canonical,
        "craft_routing": {
            "primary_craft": primary_craft,
            "supporting_crafts": supporting
        }
    }

    # Self-validate against schema
    schema = load_schema("brief")
    errors = validate_dict(brief, schema)
    if errors:
        raise ValueError(f"Generated IntentBrief violates schema: {errors}")

    return brief


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", type=str, help="Raw user prompt or brief requirement")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Save path for intent_brief.json")
    parser.add_argument("--id", type=str, default=None, help="Optional intent ID")

    args = parser.parse_args()
    brief = decode_intent(args.prompt, intent_id=args.id)
    text = json.dumps(brief, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"Saved IntentBrief to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
