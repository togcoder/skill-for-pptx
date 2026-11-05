import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import design_critic as dc  # noqa: E402


def shape(name, text="", size=20, x=0.1, y=0.1, w=0.4, h=0.2, filled=False):
    return {
        "id": name, "name": name,
        "geometry": {"x": x, "y": y, "w": w, "h": h},
        "text": text or None,
        "max_font_pt": size if text else None,
        "paragraphs": [{"text": text, "font": "Arial", "size_pt": size, "bold": False}]
        if text else [],
        "filled": filled,
    }


def slide(*objects):
    return {"objects": list(objects)}


class VisualGateTests(unittest.TestCase):
    def codes(self, s, **kw):
        return [f["code"] for f in dc.visual_findings(s, **kw)]

    def test_clean_slide_has_no_visual_gate(self):
        s = slide(shape("Title", "Một câu tiêu đề ngắn", 40, y=0.1, h=0.2),
                  shape("Card", "Nội dung thật của thẻ", 20, y=0.4, h=0.3))
        self.assertEqual(self.codes(s), [])

    def test_vis_tiny_flags_body_not_kicker(self):
        body = shape("body", "Thân bài nhỏ", 10)
        kicker = shape("kicker", "NHÃN NHỎ", 10, y=0.5)
        self.assertIn("VIS-TINY", self.codes(slide(body)))
        self.assertNotIn("VIS-TINY", self.codes(slide(kicker)))

    def test_vis_placeholder_catches_scaffold_text(self):
        s = slide(shape("Title", "Chuyển Đổi Số Toàn Diện", 28))
        self.assertIn("VIS-PLACEHOLDER", self.codes(s))

    def test_vis_empty_card_needs_content(self):
        card = shape("Major Card", "", 20, w=0.5, h=0.4, filled=True)
        self.assertIn("VIS-EMPTY-CARD", self.codes(slide(card)))

    def test_vis_empty_card_accepts_child_text(self):
        card = shape("Major Card", "", 20, w=0.5, h=0.4, filled=True)
        child = shape("Major Content", "Bốn chữ nội dung thật", 20,
                      x=0.12, y=0.12, w=0.3, h=0.2)
        self.assertNotIn("VIS-EMPTY-CARD", self.codes(slide(card, child)))

    def test_vis_clipped_catches_overflow(self):
        long = shape("Title", "Một câu rất dài " * 4, 44, x=0.1, y=0.1, w=0.12, h=0.05)
        self.assertIn("VIS-CLIPPED", self.codes(slide(long)))

    def test_quote_mark_is_not_clipped(self):
        mark = shape("quote-mark", "“", 72, x=0.1, y=0.1, w=0.15, h=0.1)
        self.assertNotIn("VIS-CLIPPED", self.codes(slide(mark)))

    def test_vis_collide_from_frame_pair(self):
        a = shape("A", "", 20, x=0.1, y=0.1, w=0.4, h=0.4)
        b = shape("B", "", 20, x=0.2, y=0.2, w=0.4, h=0.4)
        found = dc.collision_findings([{"slide": 1, "a": a, "b": b, "click": 2}])
        self.assertEqual(found[0]["code"], "VIS-COLLIDE")

    def test_vis_style_drop(self):
        s = slide(shape("Title", "Một câu tiêu đề", 40))
        codes = self.codes(s, style={"fonts": ["Georgia"]},
                           theme_fonts={"mj": "Arial", "mn": "Arial"})
        self.assertIn("VIS-STYLE-DROP", codes)


if __name__ == "__main__":
    unittest.main()
