import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.document_forge import build_document
from scripts.word_field_kit import audit_docx
from scripts.word_math import omml_from_latex


class IsoFrontMatterTests(unittest.TestCase):
    def test_escaped_latex_is_literal(self):
        for expr in (r"22{,}3\%", r"24{,}73\ \text{tCO}_2", r"a\&b"):
            node = omml_from_latex(expr)
            self.assertGreater(len(node), 0)

    def test_iso7144_order_and_references_after_appendix(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = {
                "meta": {"title": "Order test", "language": "vi-VN"},
                "front_matter": {
                    "order": "iso7144",
                    "abstract": {"enabled": True, "title": "Tóm tắt", "text": "Abstract."},
                    "preface": {"enabled": True, "title": "Lời nói đầu",
                                "text": "Preface.",
                                "blocks": [{"type": "paragraph", "text": "Control."}]},
                    "toc": {"enabled": True, "title": "Mục lục", "levels": 3},
                    "list_of_figures": {"enabled": False},
                    "list_of_tables": {"enabled": False},
                },
                "sections": [{"heading": "Body", "blocks": [
                    {"type": "paragraph", "text": "Body cites {{cite:x}} and {{cite:y}}."},
                    {"type": "heading", "text": "Sub", "level": 2},
                    {"type": "heading", "text": "Subsub", "level": 3},
                    {"type": "equation", "latex": r"x^{2} + 1"},
                ]}],
                "appendix": [{"letter": "A", "title": "Dữ liệu", "blocks": [
                    {"type": "paragraph", "text": "Appendix."}]}],
                "references": {"enabled": True, "items": [
                    {"key": "x", "label": "[1]", "text": "Reference X."},
                    {"key": "y", "label": "[2]", "text": "Reference Y."},
                ]},
            }
            path = tmp / "s.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = tmp / "o.docx"
            report = build_document(path, out, update="none")
            self.assertTrue(report["ok"], report["audit"])
            audit = audit_docx(out)
            self.assertGreaterEqual(audit.stats["max_heading_level"], 3)
            self.assertGreaterEqual(audit.stats["display_equations"], 1)
            refs = [f for f in audit.fields if f["command"] == "REF" and "ref-" in f["instr"]]
            self.assertGreaterEqual(len({f["instr"] for f in refs}), 2)
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("word/document.xml").decode("utf-8")
            self.assertLess(xml.find("Tóm tắt"), xml.find("Lời nói đầu"))
            self.assertLess(xml.find("Lời nói đầu"), xml.find("Mục lục"))
            self.assertLess(xml.find("Phụ lục A"), xml.find("Tài liệu tham khảo"))


if __name__ == "__main__":
    unittest.main()
