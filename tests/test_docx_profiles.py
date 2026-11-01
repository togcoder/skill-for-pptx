"""T049 tests: named standard profiles and chapter-based captions."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from docx import Document
from docx.shared import Mm

from scripts.document_forge import build_document
from scripts.docx_profiles import apply_profile, check_docx, get_profile, load_profiles


def _mini_spec() -> dict:
    refs = [
        {"key": f"r{i}", "label": f"[{i}]", "text": f"Reference {i}. 2024. Example."}
        for i in range(1, 9)
    ]
    cites = " ".join("{{cite:r%d}}" % i for i in range(1, 9))
    return {
        "meta": {"title": "Profile test", "author": "Tester", "language": "vi-VN",
                 "student_id": "0001", "field": "Khoa học máy tính",
                 "supervisor": "TS. Test"},
        "front_matter": {
            "task": {"enabled": True, "title": "NHIỆM VỤ", "rows": [["A", "B"]]},
            "declaration": {"enabled": True, "title": "LỜI CAM ĐOAN", "text": "Cam đoan."},
            "acknowledgements": {"enabled": True, "title": "LỜI CẢM ƠN", "text": "Cảm ơn."},
            "abstract": {"enabled": True, "title": "TÓM TẮT",
                         "text": "Tóm tắt ngắn cho kiểm thử hồ sơ tiêu chuẩn. " * 30,
                         "keywords": ["a", "b"]},
            "toc": {"enabled": True, "levels": 3, "title": "MỤC LỤC"},
            "abbreviations": {"enabled": True, "title": "DANH MỤC KÝ HIỆU",
                              "rows": [["A", "Alpha"]]},
            "list_of_figures": {"enabled": True, "title": "DANH MỤC HÌNH",
                                "mode": "ref_pageref"},
            "list_of_tables": {"enabled": True, "title": "DANH MỤC BẢNG",
                               "mode": "ref_pageref"},
        },
        "sections": [
            {"heading": "Chương một", "level": 1, "blocks": [
                {"type": "heading", "text": "Mục", "level": 2},
                {"type": "heading", "text": "Mục con", "level": 3},
                {"type": "paragraph", "text": "Nội dung " + cites},
                {"type": "table", "advanced": True,
                 "columns": [{"header": "A", "width_mm": 50},
                             {"header": "B", "width_mm": 60}],
                 "rows": [["1", "2"]], "caption": "Bảng một", "alt": "Bảng một"},
                {"type": "equation", "latex": r"E = mc^2", "caption": "Công thức."},
            ]},
            {"heading": "Chương hai", "level": 1, "page_break_before": False, "blocks": [
                {"type": "paragraph", "text": "Nội dung hai."},
                {"type": "table", "advanced": True,
                 "columns": [{"header": "A", "width_mm": 50},
                             {"header": "B", "width_mm": 60}],
                 "rows": [["3", "4"]], "caption": "Bảng hai", "alt": "Bảng hai"},
            ]},
        ],
        "references": {"enabled": True, "title": "TÀI LIỆU THAM KHẢO", "items": refs},
    }


class ProfileTests(unittest.TestCase):
    def test_explicit_spec_wins_over_profile(self):
        profile = get_profile("hust-datn-2017")
        merged = apply_profile(
            {"page": {"margins_mm": {"left": 40}}, "typography": {"body_pt": 12}},
            profile,
        )
        self.assertEqual(merged["page"]["margins_mm"]["left"], 40)
        self.assertEqual(merged["page"]["margins_mm"]["top"], 20)
        self.assertEqual(merged["typography"]["body_pt"], 12)
        self.assertEqual(merged["typography"]["line_spacing"], 1.5)

    def test_profiles_have_sources_and_contracts(self):
        profiles = load_profiles()
        for key in ("hust-datn-2017", "vnu-uet-kl-2024", "iso-7144-thesis", "annual-report-gri"):
            profile = profiles[key]
            self.assertTrue(profile["source"]["url"].startswith("http"))
            self.assertIn("margins_mm", profile["page"])
            self.assertIn("body_font", profile["typography"])

    def test_build_with_profile_and_caption_numbering(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec_path = tmp / "spec.json"
            spec_path.write_text(json.dumps(_mini_spec(), ensure_ascii=False), encoding="utf-8")
            out = tmp / "out.docx"
            report = build_document(spec_path, out, update="none", profile="hust-datn-2017")
            self.assertTrue(report["ok"], report["audit"])
            self.assertTrue(report["conformance"]["ok"], report["conformance"])
            doc = Document(str(out))
            body = doc.sections[-1]
            self.assertAlmostEqual(body.left_margin.mm, 35, places=1)
            self.assertAlmostEqual(body.top_margin.mm, 20, places=1)
            normal = doc.styles["Normal"]
            self.assertEqual(normal.font.name, "Times New Roman")
            self.assertAlmostEqual(normal.font.size.pt, 13, places=1)
            self.assertAlmostEqual(float(normal.paragraph_format.line_spacing), 1.5, places=2)
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("word/document.xml").decode("utf-8")
            self.assertIn("Bảng 1.1", xml)
            self.assertIn("Bảng 2.1", xml)
            self.assertIn('STYLEREF "Heading 1"', xml)
            self.assertIn("SEQ Equation", xml)

    def test_conformance_flags_wrong_margin(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = {"meta": {"title": "Wrong", "language": "vi-VN"},
                    "sections": [{"heading": "A", "blocks": [
                        {"type": "paragraph", "text": "Body."}]}]}
            spec_path = tmp / "spec.json"
            spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = tmp / "wrong.docx"
            build_document(spec_path, out, update="none")
            report = check_docx(out, get_profile("hust-datn-2017"))
            self.assertFalse(report["ok"])
            ids = {c["id"] for c in report["checks"] if c["status"] == "fail"}
            self.assertIn("margins", ids)
            self.assertIn("body-font", ids)


if __name__ == "__main__":
    unittest.main()
