#!/usr/bin/env python3
"""Tests for Universal ArtCraft Hub, Capability Registry and Schemas (T036)."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.artcraft_hub import list_tools, get_tool, is_tool_available, load_capabilities
from scripts.sync_artcraft_capabilities import sync_capabilities, find_artcraft_root
from scripts.validate_handoff import validate_dict, load_schema


class ArtCraftHubTests(unittest.TestCase):
    def test_sync_capabilities_finds_artcraft_suite(self):
        root = find_artcraft_root()
        if not root:
            self.skipTest("ArtCraft directory not found on this machine")

        manifest = sync_capabilities(root)
        self.assertIn("tools", manifest)
        self.assertGreaterEqual(manifest["tool_count"], 8)
        self.assertIn("deckcraft", manifest["tools"])
        self.assertIn("wordcraft", manifest["tools"])
        self.assertIn("gridcraft", manifest["tools"])
        self.assertIn("vectorcraft", manifest["tools"])

    def test_artcraft_hub_list_and_get(self):
        root = find_artcraft_root()
        if not root:
            self.skipTest("ArtCraft directory not found on this machine")

        tools = list_tools()
        self.assertGreater(len(tools), 0)

        dc = get_tool("deckcraft")
        self.assertIsNotNone(dc)
        self.assertEqual(dc["name"], "DeckCraft")
        self.assertTrue(is_tool_available("deckcraft"))

        wc = get_tool("wordcraft")
        self.assertIsNotNone(wc)
        self.assertEqual(wc["name"], "WordCraft")

    def test_intent_brief_schema_validation(self):
        schema = load_schema("brief")
        sample_brief = {
            "intent_id": "INT-20261101-001",
            "raw_user_prompt": "Create Q3 executive summary deck",
            "audience_persona": {
                "archetype": "executive_c_level",
                "primary_need": "Quarterly capital allocation decision",
                "emotional_tone": "authoritative_minimal"
            },
            "cognitive_budget": {
                "max_visual_groups": 3,
                "max_words_per_view": 40,
                "eye_tracking_pattern": "z_pattern",
                "target_seconds_to_comprehend": 3.0
            },
            "viewing_context": {
                "medium": "projector_bright_room",
                "resolution": "1920x1080",
                "safe_min_font_pt": 18.0,
                "lighting": "bright_ambient"
            },
            "canonical_system": {
                "design_language": "swiss_grid",
                "base_grid_unit_px": 8,
                "modular_scale_ratio": 1.25
            },
            "craft_routing": {
                "primary_craft": "deckcraft",
                "supporting_crafts": ["gridcraft", "vectorcraft"]
            }
        }
        errors = validate_dict(sample_brief, schema)
        self.assertEqual(errors, [], f"Schema validation failed: {errors}")

    def test_handoff_contract_schema_validation(self):
        schema = load_schema("contract")
        sample_contract = {
            "contract_id": "DEL-20261101-001",
            "intent_id": "INT-20261101-001",
            "from_craft": "deckcraft",
            "to_craft": "vectorcraft",
            "requested_asset": {
                "kind": "svg_diagram",
                "spec": {"diagram_type": "network_topology"}
            },
            "constraints": {
                "palette_hex": ["#1A1A24", "#3D5AFE", "#F4F5F8"],
                "stroke_width_px": 2.0,
                "bounding_box": [100.0, 100.0, 400.0, 300.0]
            },
            "delivery": {
                "expected_format": "svg",
                "target_path": "build/assets/topo.svg"
            },
            "iteration_count": 0,
            "max_iterations": 2
        }
        errors = validate_dict(sample_contract, schema)
        self.assertEqual(errors, [], f"Schema validation failed: {errors}")


if __name__ == "__main__":
    unittest.main()
