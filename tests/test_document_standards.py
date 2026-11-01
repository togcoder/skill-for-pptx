import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.document_forge import build_document
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
                    "toc": {"enabled": True, "title": "Mục lục"},
                    "list_of_figures": {"enabled": False},
                    "list_of_tables": {"enabled": False},
                },
                "sections": [{"heading": "Body", "blocks": [{"type": "paragraph", "text": "Body."}]}],
                "appendix": [{"letter": "A", "title": "Dữ liệu", "blocks": [
                    {"type": "paragraph", "text": "Appendix."}]}],
                "references": {"enabled": True, "items": [
                    {"key": "x", "label": "[1]", "text": "Reference."}]},
            }
            path = tmp / "s.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = tmp / "o.docx"
            report = build_document(path, out, update="none")
            self.assertTrue(report["ok"], report["audit"])
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("word/document.xml").decode("utf-8")
            self.assertLess(xml.find("Tóm tắt"), xml.find("Lời nói đầu"))
            self.assertLess(xml.find("Lời nói đầu"), xml.find("Mục lục"))
            self.assertLess(xml.find("Phụ lục A"), xml.find("Tài liệu tham khảo"))


if __name__ == "__main__":
    unittest.main()
