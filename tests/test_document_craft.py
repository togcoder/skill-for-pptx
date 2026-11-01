#!/usr/bin/env python3
"""Tests for Document Forge and the Word field kit (T039)."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.document_forge import build_document
from scripts.word_field_kit import audit_docx, read_fields

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover
    HAVE_PIL = False


def _figure(path: Path) -> Path:
    if HAVE_PIL:
        img = Image.new("RGB", (1200, 700), "#1F4E79")
        img.save(path)
    else:
        # 1×1 transparent PNG; enough for a structural build when Pillow is absent.
        import base64
        path.write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="))
    return path


def _spec(tmp: Path) -> Path:
    fig = _figure(tmp / "figure.png")
    spec = {
        "meta": {
            "title": "Báo cáo kiểm thử cấu trúc",
            "subtitle": "Kiểm tra trường, mục lục và phụ lục",
            "author": "QA",
            "organization": "Test Lab",
            "document_id": "QA-001",
            "version": "1.0",
            "date": "2026-11-01",
            "language": "vi-VN",
            "classification": "Nội bộ",
            "keywords": ["test", "docx"],
        },
        "page": {"size": "A4", "margins_mm": {"top": 25, "bottom": 25, "left": 30, "right": 25}},
        "front_matter": {
            "toc": {"enabled": True, "levels": 3},
            "list_of_figures": {"enabled": True},
            "list_of_tables": {"enabled": True},
            "abstract": {"enabled": True, "title": "Tóm tắt", "text": "Đoạn tóm tắt kiểm thử."},
        },
        "headers_footers": {"enabled": True, "page_numbers": True},
        "sections": [
            {
                "heading": "Giới thiệu",
                "level": 1,
                "blocks": [
                    {"type": "paragraph", "text": "Tham chiếu {{ref:fig-1}} và {{num:tbl-1}}."},
                    {"type": "figure", "path": str(fig), "alt": "Hình kiểm thử", "caption": "Hình kiểm thử.", "width_mm": 155},
                    {"type": "table", "caption": "Bảng kiểm thử", "columns": [
                        {"header": "Hạng mục", "width_mm": 80},
                        {"header": "Giá trị", "width_mm": 40, "align": "right"},
                    ], "rows": [["A", "10"], ["B", "20"]], "source": "QA"},
                ],
            },
            {
                "heading": "Kết luận",
                "level": 1,
                "blocks": [{"type": "paragraph", "text": "Kết thúc."}],
            },
        ],
        "references": {"enabled": True, "items": [
            {"key": "iso690", "label": "[1]", "text": "ISO. 2021. ISO 690:2021."},
        ]},
        "appendix": [{
            "letter": "A",
            "title": "Dữ liệu chi tiết",
            "blocks": [
                {"type": "table", "caption": "Dữ liệu phụ lục", "columns": [
                    {"header": "Mã", "width_mm": 30},
                    {"header": "Giá trị", "width_mm": 30, "align": "right"},
                ], "rows": [["A-01", "1"]], "source": "QA"},
            ],
        }],
    }
    path = tmp / "spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class DocumentForgeTests(unittest.TestCase):
    def test_build_has_real_fields_and_linked_bookmarks(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = _spec(tmp)
            out = tmp / "report.docx"
            report = build_document(spec, out, update="none")
            self.assertTrue(report["ok"], report["audit"])
            self.assertTrue(out.is_file())
            fields = read_fields(out)
            commands = {f.command for f in fields}
            self.assertIn("TOC", commands)
            self.assertIn("SEQ", commands)
            self.assertIn("REF", commands)
            self.assertIn("PAGEREF", commands)
            self.assertIn("PAGE", commands)
            self.assertTrue(all(f.complete for f in fields))
            audit = audit_docx(out)
            self.assertTrue(audit.ok, audit.errors)
            self.assertEqual(audit.stats["figures"], 1)
            self.assertEqual(audit.stats["tables"], 2)
            self.assertEqual(audit.stats["sections"], 3)
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("word/document.xml").decode("utf-8")
            self.assertIn('w:pgNumType w:fmt="lowerRoman"', xml)
            self.assertIn('w:pgNumType w:fmt="decimal"', xml)
            self.assertIn("w:tblHeader", xml)
            self.assertIn("Bảng A.", xml)
            self.assertIn('descr="Hình kiểm thử"', xml)

    def test_broken_cross_reference_is_an_error(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = _spec(tmp)
            out = tmp / "report.docx"
            build_document(spec, out, update="none")
            with zipfile.ZipFile(out) as zin:
                members = {n: zin.read(n) for n in zin.namelist()}
            xml = members["word/document.xml"].decode("utf-8")
            xml = xml.replace('w:name="fig-1"', 'w:name="fig-1-renamed"')
            members["word/document.xml"] = xml.encode("utf-8")
            broken = tmp / "broken.docx"
            with zipfile.ZipFile(broken, "w", zipfile.ZIP_DEFLATED) as zout:
                for name, blob in members.items():
                    zout.writestr(name, blob)
            audit = audit_docx(broken)
            self.assertFalse(audit.ok)
            self.assertTrue(any("target missing" in e for e in audit.errors), audit.errors)

    def test_table_grid_fits_text_column(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec_data = json.loads(_spec(tmp).read_text(encoding="utf-8"))
            spec_data["sections"][0]["blocks"][2]["columns"][0]["width_mm"] = 300
            spec_path = tmp / "wide.json"
            spec_path.write_text(json.dumps(spec_data, ensure_ascii=False), encoding="utf-8")
            out = tmp / "wide.docx"
            report = build_document(spec_path, out, update="none")
            self.assertTrue(report["ok"], report["audit"])
            with zipfile.ZipFile(out) as zf:
                root = zf.read("word/document.xml").decode("utf-8")
            self.assertNotIn("gridCol w:w=\"17008\"", root)

    def test_update_fields_via_wordcraft_when_available(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = _spec(tmp)
            out = tmp / "report.docx"
            report = build_document(spec, out, update="wordcraft")
            if report.get("updated_by") != "wordcraft":
                self.skipTest("WordCraft is not available on this host")
            self.assertTrue(report["ok"], report["audit"])
            fields = read_fields(out)
            self.assertTrue(any(f.command == "TOC" and not f.dirty for f in fields), [f.command for f in fields])


if __name__ == "__main__":
    unittest.main()
