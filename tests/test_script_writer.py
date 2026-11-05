import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import motion_script as ms

GOLD_PATH = ROOT / "experiments" / "T078-20261104-claude-script-track" / "gold-script-triet-hoc-ch1.md"


class ScriptWriterTests(unittest.TestCase):
    def test_parse_gold_script_structure(self):
        self.assertTrue(GOLD_PATH.is_file(), f"Gold script not found at {GOLD_PATH}")
        text = GOLD_PATH.read_text(encoding="utf-8")
        parsed = ms.parse_script_full(text)
        self.assertEqual(parsed["format"], "gold")
        
        intent = parsed["intent"]
        self.assertIn("Sinh viên", intent["audience"])
        self.assertIn("cặp kính", intent["spine"])
        self.assertEqual(len(intent["persistent_actors"]), 11)
        self.assertIn("!!kinh", intent["persistent_actors"])
        self.assertIn("!!cau1", intent["persistent_actors"])
        
        scenes = parsed["scenes"]
        self.assertEqual(len(scenes), 13)
        self.assertEqual(scenes[0]["title"], "Bạn đã làm triết học sáng nay")
        self.assertEqual(len(scenes[0]["clicks"]), 1)
        self.assertIn("soi", scenes[0]["matched_verbs"])
        self.assertEqual(scenes[1]["morph_from"], 1)

    def test_check_gold_script_passes(self):
        text = GOLD_PATH.read_text(encoding="utf-8")
        res = ms.check_script(text)
        self.assertTrue(res["ok"], f"Gold script check failed: {res['errors']}")
        self.assertEqual(res["scenes_count"], 13)
        # Verify advisory warning for spine length
        self.assertTrue(any("SCRIPT-SPINE-RECOMMENDATION" in w for w in res["warnings"]))

    def test_check_catches_banned_placeholder(self):
        bad_text = (
            "# Test Deck\n\n## Phần 0. Ý đồ\n| Ô | Nội dung |\n|---|---|\n"
            "| Người nghe | Ban giám đốc |\n"
            "| Câu xương sống (≤ 20 từ) | Tự động hóa quy trình để tăng tốc độ. |\n\n"
            "## Cảnh 1. Tổng quan\n- **Lời nói:** Chuyển đổi số toàn diện **[CLICK]** là tất yếu khách quan.\n"
        )
        res = ms.check_script(bad_text)
        self.assertFalse(res["ok"])
        err_str = " ".join(res["errors"])
        self.assertIn("chuyển đổi số toàn diện", err_str)
        self.assertIn("tất yếu khách quan", err_str)

    def test_check_catches_long_spine(self):
        long_spine = "Một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba mười bốn mười lăm mười sáu mười bảy mười tám mười chín hai mươi hai mốt hai hai hai ba."
        bad_text = (
            f"# Test Deck\n\n## Phần 0. Ý đồ\n| Ô | Nội dung |\n|---|---|\n"
            f"| Người nghe | Ban giám đốc |\n"
            f"| Câu xương sống (≤ 20 từ) | {long_spine} |\n\n"
            "## Cảnh 1. Khởi đầu\n- **Lời nói:** Lời thoại một **[CLICK]** hai.\n"
        )
        res = ms.check_script(bad_text)
        self.assertFalse(res["ok"])
        self.assertTrue(any("SCRIPT-SPINE-LONG" in e for e in res["errors"]))

    def test_check_catches_missing_click(self):
        bad_text = (
            "# Test Deck\n\n## Phần 0. Ý đồ\n| Ô | Nội dung |\n|---|---|\n"
            "| Người nghe | Ban giám đốc |\n"
            "| Câu xương sống (≤ 20 từ) | Tự động hóa quy trình để tăng tốc độ. |\n\n"
            "## Cảnh 1. Không có click\n- **Lời nói:** Diễn giả nói rất nhiều câu ở đây nhưng quên đặt mốc bấm chuột.\n"
        )
        res = ms.check_script(bad_text)
        self.assertFalse(res["ok"])
        self.assertTrue(any("SCRIPT-NO-CLICK" in e for e in res["errors"]))

    def test_check_allows_intentional_hold_silence(self):
        text = (
            "# Test Deck\n\n## Phần 0. Ý đồ\n| Ô | Nội dung |\n|---|---|\n"
            "| Người nghe | Ban giám đốc |\n"
            "| Câu xương sống (≤ 20 từ) | Tự động hóa quy trình để tăng tốc độ. |\n\n"
            "## Cảnh 1. Câu hỏi treo\n"
            "- **Trên màn hình lúc mở:** Dấu chấm hỏi lớn.\n"
            "- **Lời nói:** Câu hỏi này đặt ra khoảng lặng suy ngẫm.\n"
            "- **Động từ → chuyển động:** *cân nhắc* → không click. Cảnh này là một khoảng lặng có chủ đích.\n"
        )
        res = ms.check_script(text)
        self.assertTrue(res["ok"], f"Expected pass for intentional hold: {res['errors']}")

    def test_check_catches_long_claim(self):
        long_claim = " ".join(["từ"] * 26)
        bad_text = (
            "# Test Deck\n\n## Phần 0. Ý đồ\n| Ô | Nội dung |\n|---|---|\n"
            "| Người nghe | Ban giám đốc |\n"
            "| Câu xương sống (≤ 20 từ) | Tự động hóa quy trình để tăng tốc độ. |\n\n"
            f"## Cảnh 1. Luận điểm\nclaim: {long_claim}\n- **Lời nói:** Câu mở **[CLICK]** câu tiếp.\n"
        )
        res = ms.check_script(bad_text)
        self.assertFalse(res["ok"])
        self.assertTrue(any("SCRIPT-CLAIM-LONG" in e for e in res["errors"]))

    def test_scaffold_has_zero_canned_prose(self):
        scaffold = ms.scaffold_script()
        self.assertIn("## Phần 0. Ý đồ", scaffold)
        self.assertIn("## Cảnh 1.", scaffold)
        self.assertIn("<!--", scaffold)
        # Ensure zero banned template phrases are emitted
        for phrase in ms.BANNED_PLACEHOLDERS:
            self.assertNotIn(phrase.lower(), scaffold.lower())
        # Ensure no canned filler sentences
        self.assertNotIn("hành động quyết liệt", scaffold)
        self.assertNotIn("chào mừng quý vị", scaffold.lower())

    def test_compile_to_scene_structure(self):
        text = GOLD_PATH.read_text(encoding="utf-8")
        scene_doc = ms.compile_to_scene(text)
        self.assertEqual(scene_doc["version"], 1)
        self.assertEqual(len(scene_doc["scenes"]), 13)
        self.assertEqual(len(scene_doc["actors"]), 11)
        
        s1 = scene_doc["scenes"][0]
        self.assertEqual(s1["id"], "s1")
        self.assertEqual(s1["title"], "Bạn đã làm triết học sáng nay")
        self.assertEqual(len(s1["clicks"]), 1)
        self.assertEqual(s1["clicks"][0]["verb"], "soi")
        self.assertEqual(s1["clicks"][0]["action"], "spotlight")
        self.assertIn("thấu kính", s1["verb_motion"])

    def test_compile_to_direction_backward_compatibility(self):
        text = GOLD_PATH.read_text(encoding="utf-8")
        dir_doc = ms.compile_to_direction(text)
        self.assertIn("brief", dir_doc)
        self.assertIn("beats", dir_doc)
        self.assertIn("shots", dir_doc)
        self.assertEqual(len(dir_doc["beats"]), 13)
        self.assertEqual(len(dir_doc["shots"]), 13)
        self.assertEqual(dir_doc["beats"][0]["id"], "b1")

    def test_verb_table_completeness(self):
        verbs = ms.VERB_TABLE
        required = [
            "soi", "gom thành hệ thống", "cân nhắc", "nghiêng về", "nối lại, vận động",
            "đứng ở / còn trống", "lộn ngược, ghép", "dâng lên, gặp nhau",
            "trở thành, thống nhất", "đi qua thời gian", "đi sâu, phóng to chi tiết",
            "nhưng", "song", "quay lại, nhớ lại", "loại bỏ, phủ định", "nhấn một trong nhiều"
        ]
        for v in required:
            self.assertIn(v, verbs, f"Missing required verb '{v}' in VERB_TABLE")
            self.assertIn("action", verbs[v])
            self.assertIn("type", verbs[v])


if __name__ == "__main__":
    unittest.main()
