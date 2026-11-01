#!/usr/bin/env python3
"""Advanced docx blocks: equations, side-by-side media, rich tables, callouts."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.document_forge import build_document
from scripts.word_math import omml_from_latex

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover
    HAVE_PIL = False


def _png(path: Path) -> Path:
    if HAVE_PIL:
        Image.new("RGB", (400, 240), "#1F4E79").save(path)
    else:
        import base64
        path.write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="))
    return path


def _spec(tmp: Path) -> Path:
    img = _png(tmp / "icon.png")
    spec = {
        "meta": {"title": "Advanced report", "language": "en-US"},
        "sections": [{
            "heading": "Advanced",
            "blocks": [
                {"type": "figure_text", "path": str(img), "alt": "Icon alt", "caption": "Side figure.",
                 "heading": "Side heading", "text": "Text beside the figure.\n\nSecond paragraph.",
                 "image_width_mm": 60},
                {"type": "equation", "latex": r"g_t = \frac{Y_t - Y_{t-1}}{Y_{t-1}} \times 100",
                 "caption": "Growth."},
                {"type": "callout", "title": "Note", "text": "A callout body.", "fill": "EAF1F8"},
                {"type": "table", "advanced": True, "caption": "Rich table", "alt": "Rich table alt",
                 "columns": [{"header": "A", "width_mm": 40}, {"header": "B", "width_mm": 40},
                             {"header": "C", "width_mm": 40}],
                 "header_rows": [[{"text": "Group", "colspan": 2, "align": "center"},
                                  {"text": "Total", "rowspan": 2, "align": "center"}],
                                 [{"text": "A", "align": "left"}, {"text": "B", "align": "right"}]],
                 "rows": [[{"image": str(img), "width_mm": 10, "alt": "Cell icon"}, "1", "2"]],
                 "row_heights_mm": [8, 8, 14], "cell_margins_mm": 1.5},
            ],
        }],
    }
    path = tmp / "advanced.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class AdvancedDocumentTests(unittest.TestCase):
    def test_omml_parser(self):
        f = omml_from_latex(r"\frac{a}{b}")
        self.assertEqual(f[0].tag.split("}")[-1], "f")
        sup = omml_from_latex(r"x^{2}")
        self.assertEqual(sup[0].tag.split("}")[-1], "sSup")
        nary = omml_from_latex(r"\sum_{i=1}^{n} x_i")
        self.assertEqual(nary[0].tag.split("}")[-1], "nary")

    def test_advanced_blocks_are_real_ooxml(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "advanced.docx"
            report = build_document(_spec(tmp), out, update="none")
            self.assertTrue(report["ok"], report["audit"])
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("word/document.xml").decode("utf-8")
            self.assertIn("m:oMath", xml)
            self.assertIn("m:f", xml)
            self.assertIn("SEQ Equation", xml)
            self.assertIn("w:fill=\"EAF1F8\"", xml)
            # figure_text and the rich table both carry a drawing.
            self.assertGreaterEqual(xml.count("<w:drawing>"), 2)
            self.assertIn("descr=\"Icon alt\"", xml)
            self.assertIn("descr=\"Cell icon\"", xml)
            self.assertIn("w:gridSpan", xml)
            self.assertIn("w:vMerge", xml)


if __name__ == "__main__":
    unittest.main()
