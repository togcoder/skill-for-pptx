#!/usr/bin/env python3
"""Tests for Intent & Empathy Decoder Engine (T037)."""
from __future__ import annotations

import unittest

from scripts.intent_decoder import decode_intent
from scripts.validate_handoff import validate_dict, load_schema


class IntentDecoderTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema("brief")

    def test_decode_executive_presentation_prompt(self):
        prompt = "Báo cáo tiến độ quý 3 cho ban giám đốc chiếu tại phòng họp"
        brief = decode_intent(prompt)
        self.assertEqual(brief["audience_persona"]["archetype"], "executive_c_level")
        self.assertEqual(brief["viewing_context"]["medium"], "projector_bright_room")
        self.assertEqual(brief["craft_routing"]["primary_craft"], "deckcraft")
        self.assertEqual(validate_dict(brief, self.schema), [])

    def test_decode_technical_document_prompt(self):
        prompt = "Soạn thảo văn bản tài liệu kiến trúc kỹ thuật chi tiết cho kỹ sư"
        brief = decode_intent(prompt)
        self.assertEqual(brief["audience_persona"]["archetype"], "technical_engineer")
        self.assertEqual(brief["craft_routing"]["primary_craft"], "wordcraft")
        self.assertEqual(validate_dict(brief, self.schema), [])

    def test_decode_spreadsheet_prompt(self):
        prompt = "Lập bảng tính excel tính toán bảng lương nhân viên"
        brief = decode_intent(prompt)
        self.assertEqual(brief["craft_routing"]["primary_craft"], "gridcraft")
        self.assertEqual(validate_dict(brief, self.schema), [])


if __name__ == "__main__":
    unittest.main()
