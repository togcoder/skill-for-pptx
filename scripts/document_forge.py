#!/usr/bin/env python3
"""Document Forge — build a professional DOCX from a semantic spec (T039, docx).

Status: EXPERIMENTAL — T039 [docx], review requested.  Not a canonical module
until an independent review accepts it.


The output is a real Word document, not a PDF dressed as one:

* Heading 1..4 are built-in styles with a multilevel list linked to the styles
  (ISO 2145 numbering), so the navigation pane, TOC and accessibility tree work.
* The table of contents, list of figures/tables, page numbers, running chapter
  title, figure/table numbers and every "see Figure 3" are Word fields
  (``TOC``, ``PAGEREF``, ``STYLEREF``, ``SEQ``, ``REF``), not typed text.
* Figures are inline (no drifting anchors), centred, aspect-preserving, with
  alt text and a caption that stays with the image.
* Tables use a fixed grid that fits the text column, a repeating header row,
  right-aligned numeric columns and a caption above the table.
* Sections give the cover no header/footer, the front matter roman numerals and
  the body arabic numerals starting at 1.

Without WordCraft/Word the field *results* are placeholders; the fields and
bookmarks are still valid and ``w:updateFields`` asks Word to refresh them on
open.  ``--update wordcraft`` refreshes them before delivery and ``--render``
renders pages through WordCraft's layout engine.  Neither is required to build,
inspect or audit the file.

CLI:
    python scripts/document_forge.py build spec.json -o report.docx
    python scripts/document_forge.py build spec.json -o report.docx --update wordcraft --render preview/
    python scripts/document_forge.py audit report.docx --md audit.md
    python scripts/document_forge.py inspect report.docx
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
    from docx.image.image import Image as DocxImage
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt, RGBColor, Twips
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-docx is required: pip install python-docx") from exc

try:  # package import (tests) or script import (CLI)
    from .word_field_kit import (
        add_appendix_numbering, add_bookmark_start, add_bookmark_end,
        add_bookmark_to_paragraph, add_citation, add_cross_reference,
        add_field, add_heading_numbering, add_page_number, add_seq_caption,
        add_styleref, add_toc, add_toc_of, apply_numbering, audit_docx,
        set_even_odd_headers, set_page_numbering, set_update_fields,
    )
except ImportError:
    from word_field_kit import (
        add_appendix_numbering, add_bookmark_start, add_bookmark_end,
        add_bookmark_to_paragraph, add_citation, add_cross_reference,
        add_field, add_heading_numbering, add_page_number, add_seq_caption,
        add_styleref, add_toc, add_toc_of, apply_numbering, audit_docx,
        set_even_odd_headers, set_page_numbering, set_update_fields,
    )

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SYSTEM_PATH = ROOT / "domains" / "docx" / "data" / "document_system.json"

TWIPS_PER_MM = 56.69291338582677
EMU_PER_MM = 36000.0

DEFAULTS: dict[str, Any] = {
    "meta": {
        "title": "Untitled document",
        "subtitle": "",
        "author": "",
        "organization": "",
        "document_id": "",
        "version": "1.0",
        "date": "",
        "language": "vi-VN",
        "classification": "",
        "keywords": [],
    },
    "page": {
        "size": "A4",
        "orientation": "portrait",
        "margins_mm": {"top": 25, "bottom": 25, "left": 30, "right": 25},
        "header_distance_mm": 12,
        "footer_distance_mm": 12,
        "mirror_margins": False,
        "gutter_mm": 0,
    },
    "typography": {
        "body_font": "Calibri",
        "heading_font": "Calibri Light",
        "mono_font": "Consolas",
        "east_asia_font": "Microsoft YaHei",
        "body_pt": 11,
        "line_spacing": 1.15,
        "space_after_pt": 6,
        "heading_sizes_pt": [18, 15, 13, 12],
        "caption_pt": 9,
        "table_pt": 9,
        "header_pt": 8.5,
        "reference_pt": 9.5,
        "color_text": "1A1A1A",
        "color_muted": "595959",
        "color_accent": "1F4E79",
        "color_rule": "BFBFBF",
    },
    "cover": {"enabled": True, "logo": "", "logo_alt": ""},
    "front_matter": {
        "toc": {"enabled": True, "levels": 3, "title": ""},
        "list_of_figures": {"enabled": False, "title": ""},
        "list_of_tables": {"enabled": False, "title": ""},
        "abstract": {"enabled": False, "title": "", "text": "", "keywords": []},
    },
    "headers_footers": {
        "enabled": True,
        "odd_even": False,
        "document_id_in_header": True,
        "chapter_in_header": True,
        "classification_in_footer": True,
        "page_numbers": True,
    },
    "sections": [],
    "references": {"enabled": False, "title": "", "items": []},
    "appendix": [],
}

LABELS = {
    "vi": {
        "toc": "Mục lục", "figures": "Danh mục hình", "tables": "Danh mục bảng",
        "abstract": "Tóm tắt", "references": "Tài liệu tham khảo",
        "figure": "Hình", "table": "Bảng", "page": "Trang", "source": "Nguồn",
        "keywords": "Từ khóa", "appendix": "Phụ lục",
        "doc_id": "Mã tài liệu", "version": "Phiên bản", "date": "Ngày",
        "classification": "Mức độ",
    },
    "en": {
        "toc": "Contents", "figures": "List of figures", "tables": "List of tables",
        "abstract": "Abstract", "references": "References",
        "figure": "Figure", "table": "Table", "page": "Page", "source": "Source",
        "keywords": "Keywords", "appendix": "Appendix",
        "doc_id": "Document ID", "version": "Version", "date": "Date",
        "classification": "Classification",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _labels(spec: dict) -> dict:
    return LABELS["vi"] if str(spec["meta"].get("language", "vi")).lower().startswith("vi") else LABELS["en"]


def _mm_twips(value: float) -> int:
    return int(round(value * TWIPS_PER_MM))


def _set_rfonts(rpr, *, ascii_font: str, east_asia: str) -> None:
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), ascii_font)
    rfonts.set(qn("w:eastAsia"), east_asia)


def _set_style_font(style, name: str, size_pt: float, *, bold: bool | None = None,
                    color: str | None = None, east_asia: str = "Microsoft YaHei") -> None:
    style.font.name = name
    style.font.size = Pt(size_pt)
    if bold is not None:
        style.font.bold = bold
    if color:
        style.font.color.rgb = RGBColor.from_string(color)
    rpr = style.element.get_or_add_rPr()
    _set_rfonts(rpr, ascii_font=name, east_asia=east_asia)
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "vi-VN")
    lang.set(qn("w:eastAsia"), "vi-VN")


def _style(doc, name: str, *, style_type=WD_STYLE_TYPE.PARAGRAPH):
    try:
        return doc.styles[name]
    except KeyError:
        return doc.styles.add_style(name, style_type)


def _setup_styles(doc, spec: dict) -> None:
    typo = spec["typography"]
    ea = typo.get("east_asia_font", "Microsoft YaHei")
    body = typo["body_font"]
    heading = typo["heading_font"]

    normal = doc.styles["Normal"]
    _set_style_font(normal, body, typo["body_pt"], color=typo["color_text"], east_asia=ea)
    pf = normal.paragraph_format
    pf.line_spacing = typo["line_spacing"]
    pf.space_after = Pt(typo["space_after_pt"])
    pf.space_before = Pt(0)
    pf.widow_control = True
    # python-docx exposes widow_control through pPr; setting it twice is harmless.
    ppr = normal.element.get_or_add_pPr()
    wc = ppr.find(qn("w:widowControl"))
    if wc is None:
        wc = OxmlElement("w:widowControl")
        ppr.append(wc)
    wc.set(qn("w:val"), "true")

    for level, size in enumerate(typo["heading_sizes_pt"], start=1):
        style = doc.styles[f"Heading {level}"]
        _set_style_font(style, heading, size, bold=True, color=typo["color_accent"], east_asia=ea)
        p = style.paragraph_format
        p.space_before = Pt({1: 18, 2: 14, 3: 10, 4: 8}.get(level, 8))
        p.space_after = Pt({1: 8, 2: 6, 3: 4, 4: 4}.get(level, 4))
        p.keep_with_next = True
        p.keep_together = True
        p.line_spacing = 1.0
        p.left_indent = Mm(0)
        p.first_line_indent = Mm(0)

    caption = doc.styles["Caption"]
    _set_style_font(caption, body, typo["caption_pt"], bold=False, color=typo["color_muted"], east_asia=ea)
    caption.paragraph_format.space_before = Pt(4)
    caption.paragraph_format.space_after = Pt(8)
    caption.paragraph_format.line_spacing = 1.0
    caption.paragraph_format.keep_together = True

    for name, size in [("Header", typo["header_pt"]), ("Footer", typo["header_pt"])]:
        style = doc.styles[name]
        _set_style_font(style, body, size, color=typo["color_muted"], east_asia=ea)
        style.paragraph_format.space_after = Pt(0)
        style.paragraph_format.line_spacing = 1.0

    table_text = _style(doc, "Table Text")
    _set_style_font(table_text, body, typo["table_pt"], color=typo["color_text"], east_asia=ea)
    table_text.paragraph_format.space_before = Pt(0)
    table_text.paragraph_format.space_after = Pt(0)
    table_text.paragraph_format.line_spacing = 1.0

    toc_heading = _style(doc, "TOC Heading")
    # The built-in TOC Heading is based on Heading 1, so it inherits the
    # heading list and would print "1 Mục lục".  Break the inheritance: front
    # matter headings are unnumbered and stay out of the TOC.
    toc_heading.base_style = doc.styles["Normal"]
    _set_style_font(toc_heading, heading, 16, bold=True, color=typo["color_accent"], east_asia=ea)
    toc_heading.paragraph_format.space_before = Pt(0)
    toc_heading.paragraph_format.space_after = Pt(12)
    toc_heading.paragraph_format.keep_with_next = True
    ppr = toc_heading.element.get_or_add_pPr()
    numpr = ppr.find(qn("w:numPr"))
    if numpr is not None:
        ppr.remove(numpr)
    lvl = ppr.find(qn("w:outlineLvl"))
    if lvl is None:
        lvl = OxmlElement("w:outlineLvl")
        ppr.append(lvl)
    lvl.set(qn("w:val"), "9")  # body text -> not included in the TOC

    front_heading = _style(doc, "Front Matter Heading")
    front_heading.base_style = doc.styles["Normal"]
    _set_style_font(front_heading, heading, 16, bold=True, color=typo["color_accent"], east_asia=ea)
    front_heading.paragraph_format.space_before = Pt(0)
    front_heading.paragraph_format.space_after = Pt(12)
    front_heading.paragraph_format.keep_with_next = True
    ppr = front_heading.element.get_or_add_pPr()
    lvl = ppr.find(qn("w:outlineLvl"))
    if lvl is None:
        lvl = OxmlElement("w:outlineLvl")
        ppr.append(lvl)
    lvl.set(qn("w:val"), "9")

    # The stock Title style carries a bottom border and a decorative colour;
    # the cover draws its own single rule, so remove the inherited border.
    title_style = doc.styles["Title"]
    ppr = title_style.element.get_or_add_pPr()
    pbdr = ppr.find(qn("w:pBdr"))
    if pbdr is not None:
        ppr.remove(pbdr)

    for i, size in enumerate([11, 10, 10], start=1):
        # Word's built-in TOC styles are named "toc 1", "toc 2", ... (styleId
        # TOC1).  Creating "TOC 1" would leave the field result unstyled.
        name = f"toc {i}"
        if name not in [s.name for s in doc.styles]:
            style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        else:
            style = doc.styles[name]
        _set_style_font(style, body, size, color=typo["color_text"], east_asia=ea)
        style.paragraph_format.space_before = Pt(4 if i == 1 else 2)
        style.paragraph_format.space_after = Pt(2)
        style.paragraph_format.line_spacing = 1.0
        style.paragraph_format.left_indent = Mm((i - 1) * 6)
        style.paragraph_format.tab_stops.add_tab_stop(Mm(155), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    if "Quote" in [s.name for s in doc.styles]:
        quote = doc.styles["Quote"]
        _set_style_font(quote, body, typo["body_pt"], color=typo["color_muted"], east_asia=ea)


def _setup_page(section, spec: dict) -> None:
    page = spec["page"]
    sizes = {"A4": (210, 297), "Letter": (215.9, 279.4), "A5": (148, 210)}
    w, h = sizes.get(page.get("size", "A4"), sizes["A4"])
    if page.get("orientation") == "landscape":
        w, h = h, w
    section.page_width = Mm(w)
    section.page_height = Mm(h)
    m = page["margins_mm"]
    section.top_margin = Mm(m["top"])
    section.bottom_margin = Mm(m["bottom"])
    section.left_margin = Mm(m["left"])
    section.right_margin = Mm(m["right"])
    section.header_distance = Mm(page.get("header_distance_mm", 12))
    section.footer_distance = Mm(page.get("footer_distance_mm", 12))
    # Gutter and mirror margins are section/settings attributes python-docx
    # does not model directly; write them into pgMar/settings.
    pgmar = section._sectPr.find(qn("w:pgMar"))
    if pgmar is not None:
        pgmar.set(qn("w:gutter"), str(_mm_twips(page.get("gutter_mm", 0))))
    if page.get("mirror_margins"):
        settings = section._sectPr.getroottree().getroot()
        # mirrorMargins is a settings.xml element; set later in _set_mirror.
        pass


def _text_width_mm(section) -> float:
    return section.page_width.mm - section.left_margin.mm - section.right_margin.mm


def _text_height_mm(section) -> float:
    return section.page_height.mm - section.top_margin.mm - section.bottom_margin.mm


def _clear(part) -> None:
    for p in part.paragraphs:
        p.clear()
    for table in list(part.tables):
        table._element.getparent().remove(table._element)


def _paragraph_border(paragraph, *, edge: str = "bottom", color: str = "BFBFBF", sz: int = 4) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = ppr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        ppr.append(pbdr)
    node = OxmlElement(f"w:{edge}")
    node.set(qn("w:val"), "single")
    node.set(qn("w:sz"), str(sz))
    node.set(qn("w:space"), "4")
    node.set(qn("w:color"), color)
    pbdr.append(node)


def _write_header(section, spec: dict, width_mm: float, *, even: bool = False,
                  chapter: bool = True) -> None:
    hf = spec["headers_footers"]
    part = section.even_page_header if even else section.header
    part.is_linked_to_previous = False
    _clear(part)
    p = part.paragraphs[0]
    p.paragraph_format.tab_stops.add_tab_stop(Mm(width_mm), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if not hf.get("enabled", True):
        return
    meta = spec["meta"]
    if hf.get("document_id_in_header", True):
        p.add_run(meta.get("document_id") or meta.get("title", ""))
    if chapter:
        p.add_run("\t")
        if hf.get("chapter_in_header", True):
            add_styleref(p, "Heading 1", result="[Chương]")
    for run in p.runs:
        run.font.size = Pt(spec["typography"]["header_pt"])
        run.font.color.rgb = RGBColor.from_string(spec["typography"]["color_muted"])
    if p.text.strip() or chapter:
        _paragraph_border(p, edge="bottom", color=spec["typography"]["color_rule"], sz=4)


def _write_footer(section, spec: dict, width_mm: float, *, even: bool = False,
                  roman: bool = False) -> None:
    hf = spec["headers_footers"]
    labels = _labels(spec)
    part = section.even_page_footer if even else section.footer
    part.is_linked_to_previous = False
    _clear(part)
    p = part.paragraphs[0]
    p.paragraph_format.tab_stops.add_tab_stop(Mm(width_mm), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if not hf.get("enabled", True):
        return
    if hf.get("classification_in_footer", True) and spec["meta"].get("classification"):
        p.add_run(spec["meta"]["classification"])
    p.add_run("\t")
    if hf.get("page_numbers", True):
        p.add_run(f"{labels['page']} ")
        add_page_number(p, "PAGE", result="i" if roman else "1")
        if not roman:
            p.add_run(" / ")
            add_page_number(p, "NUMPAGES", result="1")
    for run in p.runs:
        run.font.size = Pt(spec["typography"]["header_pt"])
        run.font.color.rgb = RGBColor.from_string(spec["typography"]["color_muted"])


def _set_mirror_margins(doc, value: bool) -> None:
    settings = doc.settings.element
    node = settings.find(qn("w:mirrorMargins"))
    if value and node is None:
        settings.append(OxmlElement("w:mirrorMargins"))
    elif not value and node is not None:
        settings.remove(node)


def _set_core_properties(doc, spec: dict) -> None:
    meta = spec["meta"]
    cp = doc.core_properties
    cp.title = meta.get("title", "")
    cp.subject = meta.get("subtitle", "")
    cp.author = meta.get("author", "")
    cp.last_modified_by = meta.get("author", "")
    cp.keywords = "; ".join(meta.get("keywords", []) or [])
    cp.category = meta.get("classification", "")
    cp.comments = meta.get("organization", "")
    cp.language = meta.get("language", "vi-VN")
    try:
        cp.created = datetime.fromisoformat(meta["date"]) if meta.get("date") else datetime.now()
        cp.modified = cp.created
    except ValueError:
        cp.created = datetime.now()
        cp.modified = cp.created


# ---------------------------------------------------------------------------
# Inline text and blocks
# ---------------------------------------------------------------------------

_TOKEN = re.compile(r"\{\{(ref|num|page|cite):([A-Za-z0-9_.:-]+)\}\}|\*\*([^*]+)\*\*|\*([^*]+)\*")


def _add_text(paragraph, text: str, spec: dict, *, appendix: bool = False) -> None:
    """Add text with {{ref:bookmark}}, {{num:bookmark}}, {{page:bookmark}},
    {{cite:key}}, **bold** and *italic* tokens."""
    pos = 0
    for m in _TOKEN.finditer(text or ""):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        if m.group(1):
            kind, target = m.group(1), m.group(2)
            if kind == "ref":
                add_cross_reference(paragraph, target, kind="text", result="[X]")
            elif kind == "num":
                add_cross_reference(paragraph, f"{target}-num", kind="text", result="1")
            elif kind == "page":
                add_cross_reference(paragraph, target, kind="page", result="1")
            elif kind == "cite":
                add_citation(paragraph, f"ref-{target}-label", result="[1]")
        elif m.group(3):
            run = paragraph.add_run(m.group(3))
            run.bold = True
        elif m.group(4):
            run = paragraph.add_run(m.group(4))
            run.italic = True
        pos = m.end()
    if pos < len(text or ""):
        paragraph.add_run(text[pos:])


def _add_blocks(doc, blocks: list[dict], spec: dict, section, owner, counters: dict,
                *, appendix: bool = False, appendix_num_id: int | None = None,
                heading_level_start: int = 2) -> None:
    labels = _labels(spec)
    width_mm = _text_width_mm(section)
    for block in blocks or []:
        if isinstance(block, str):
            block = {"type": "paragraph", "text": block}
        kind = block.get("type", "paragraph")
        if kind in {"paragraph", "text"}:
            p = doc.add_paragraph()
            p.alignment = _align(block.get("align", "left"))
            _add_text(p, block.get("text", ""), spec, appendix=appendix)
        elif kind in {"bullets", "bullet"}:
            for item in block.get("items", []):
                p = doc.add_paragraph(style="List Bullet")
                _add_text(p, item, spec, appendix=appendix)
        elif kind in {"numbered", "number"}:
            for item in block.get("items", []):
                p = doc.add_paragraph(style="List Number")
                _add_text(p, item, spec, appendix=appendix)
        elif kind == "heading":
            level = int(block.get("level", heading_level_start))
            p = doc.add_heading(_strip_number(block.get("text", "")), level)
            if appendix and appendix_num_id is not None:
                apply_numbering(p, appendix_num_id, level - 1)
            p.paragraph_format.keep_with_next = True
        elif kind == "figure":
            _add_figure(doc, block, spec, section, owner, counters, appendix=appendix)
        elif kind == "table":
            _add_table(doc, block, spec, section, owner, counters, appendix=appendix)
        elif kind == "quote":
            p = doc.add_paragraph(style="Quote")
            _add_text(p, block.get("text", ""), spec, appendix=appendix)
        elif kind == "source":
            p = doc.add_paragraph()
            run = p.add_run(f"{labels['source']}: {block.get('text', '')}")
            run.italic = True
            run.font.size = Pt(spec["typography"]["caption_pt"])
            run.font.color.rgb = RGBColor.from_string(spec["typography"]["color_muted"])
        elif kind == "page_break":
            doc.add_page_break()
        elif kind == "spacer":
            doc.add_paragraph()
        elif kind == "key_values":
            rows = [[item.get("label", ""), item.get("value", "")] for item in block.get("items", [])]
            _add_table(doc, {"columns": [{"header": "", "width_mm": 45}, {"header": "", "width_mm": width_mm - 45}],
                             "rows": rows, "caption": block.get("caption", ""), "header": False,
                             "borders": "none"}, spec, section, owner, counters, appendix=appendix)
        else:
            raise ValueError(f"unknown block type: {kind!r}")


def _align(value: str):
    return {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}.get(value, WD_ALIGN_PARAGRAPH.LEFT)


def _strip_number(text: str) -> str:
    return re.sub(r"^\s*\d+(?:\.\d+)*[.)]?\s+", "", text or "").strip()


def _number_blocks(spec: dict) -> dict:
    """Assign stable figure/table numbers before the front matter is written.

    The list of figures/tables is built from REF/PAGEREF fields (not a
    ``TOC \\c`` caption cache), so it needs the bookmarks before the body is
    built.  Numbering order is the reading order: body sections first, then
    appendices.
    """
    counters = {"figure": 0, "table": 0}
    figures: list[dict] = []
    tables: list[dict] = []

    def walk(blocks, letter: str | None = None) -> None:
        for block in blocks or []:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "figure":
                counters["figure"] += 1
                block["_number"] = counters["figure"]
                block["_appendix_letter"] = letter
                figures.append({
                    "number": counters["figure"],
                    "bookmark": f"fig-{counters['figure']}",
                    "appendix_letter": letter,
                    "caption": block.get("caption", ""),
                })
            elif kind == "table" and block.get("caption"):
                counters["table"] += 1
                block["_number"] = counters["table"]
                block["_appendix_letter"] = letter
                tables.append({
                    "number": counters["table"],
                    "bookmark": f"tbl-{counters['table']}",
                    "appendix_letter": letter,
                    "caption": block.get("caption", ""),
                })
            elif kind == "table":
                block["_number"] = None
            walk(block.get("blocks"), letter)

    for section in spec.get("sections", []):
        walk(section.get("blocks"))
    for i, app in enumerate(spec.get("appendix", [])):
        letter = app.get("letter") or chr(65 + i)
        app["_letter"] = letter
        walk(app.get("blocks"), letter)
    return {"figures": figures, "tables": tables}


def _looks_numeric(value: Any) -> bool:
    if isinstance(value, (int, float)):
        return True
    s = str(value).strip().replace("%", "").replace(" ", "")
    s = s.replace(".", "").replace(",", ".") if s.count(",") else s
    try:
        float(s)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Figures and tables
# ---------------------------------------------------------------------------

def _add_figure(doc, fig: dict, spec: dict, section, owner, counters: dict, *, appendix: bool = False) -> None:
    path = Path(fig["path"])
    if not path.is_absolute():
        path = Path(fig.get("_base_dir", ".")) / path
    if not path.is_file():
        raise FileNotFoundError(f"figure not found: {path}")
    typo = spec["typography"]
    labels = _labels(spec)
    width_mm = float(fig.get("width_mm") or _text_width_mm(section))
    max_width = _text_width_mm(section)
    max_height = _text_height_mm(section) * float(fig.get("max_height_ratio", 0.55))
    try:
        img = DocxImage.from_file(str(path))
        aspect = img.px_height / img.px_width if img.px_width else 0.6
    except Exception:
        aspect = 0.6
    if width_mm > max_width:
        width_mm = max_width
    if width_mm * aspect > max_height:
        width_mm = max_height / aspect
        height_mm = max_height
    else:
        height_mm = width_mm * aspect

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(path), width=Mm(width_mm))
    inline = doc.inline_shapes[-1]
    alt = fig.get("alt", "")
    title = fig.get("title", alt[:200])
    docpr = inline._inline.docPr
    docpr.set("descr", alt)
    docpr.set("title", title)
    try:
        dpi = img.px_width / (inline.width.mm / 25.4)
    except Exception:
        dpi = None

    n = fig.get("_number")
    if n is None:
        counters["Figure"] = counters.get("Figure", 0) + 1
        n = counters["Figure"]
    letter = fig.get("_appendix_letter")
    prefix = f"{letter}." if letter else ""
    reset = False
    if letter:
        started = counters.setdefault("_appendix_figures", set())
        reset = letter not in started
        started.add(letter)
    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_together = True
    number_bookmark = f"fig-{n}-num"
    caption_bookmark = f"fig-{n}"
    add_seq_caption(cap, "Figure", fig.get("caption", ""),
                    number_bookmark=number_bookmark, caption_bookmark=caption_bookmark,
                    bookmark_owner=owner, display_label=labels["figure"],
                    display_prefix=prefix, reset=reset)
    if fig.get("source"):
        sp = doc.add_paragraph()
        sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = sp.add_run(f"{labels['source']}: {fig['source']}")
        run.italic = True
        run.font.size = Pt(typo["caption_pt"] - 0.5)
        run.font.color.rgb = RGBColor.from_string(typo["color_muted"])
        sp.paragraph_format.space_after = Pt(8)
    fig["_effective_dpi"] = dpi


def _set_table_borders(table, *, color: str = "BFBFBF", header_color: str = "7F7F7F",
                       kind: str = "booktabs") -> None:
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    edges = ["top", "left", "bottom", "right", "insideH", "insideV"]
    for edge in edges:
        node = OxmlElement(f"w:{edge}")
        if kind == "none":
            node.set(qn("w:val"), "nil")
        elif kind == "grid":
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), "4")
            node.set(qn("w:color"), color)
        else:  # booktabs: horizontal rules only
            if edge in {"top", "bottom"}:
                node.set(qn("w:val"), "single")
                node.set(qn("w:sz"), "8")
                node.set(qn("w:color"), "404040")
            elif edge == "insideH":
                node.set(qn("w:val"), "single")
                node.set(qn("w:sz"), "4")
                node.set(qn("w:color"), color)
            else:
                node.set(qn("w:val"), "nil")
        borders.append(node)
    tblpr.insert_element_before(
        borders,
        "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook",
        "w:tblCaption", "w:tblDescription",
    )


def _set_tbl_layout(table, total_twips: int, *, first_row: bool = True) -> None:
    tblpr = table._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.insert_element_before(
            tblw, "w:jc", "w:tblCellSpacing", "w:tblInd",
            "w:tblBorders", "w:shd", "w:tblLayout",
            "w:tblCellMar", "w:tblLook", "w:tblCaption",
            "w:tblDescription",
        )
    tblw.set(qn("w:type"), "dxa")
    tblw.set(qn("w:w"), str(total_twips))
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.insert_element_before(
        layout, "w:tblCellMar", "w:tblLook", "w:tblCaption",
        "w:tblDescription",
    )
    cellmar = OxmlElement("w:tblCellMar")
    for side, val in [("top", 40), ("left", 85), ("bottom", 40), ("right", 85)]:
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        cellmar.append(node)
    tblpr.insert_element_before(
        cellmar, "w:tblLook", "w:tblCaption", "w:tblDescription",
    )
    look = OxmlElement("w:tblLook")
    look.set(qn("w:val"), "04A0")
    look.set(qn("w:firstRow"), "1" if first_row else "0")
    look.set(qn("w:lastRow"), "0")
    look.set(qn("w:firstColumn"), "0")
    look.set(qn("w:lastColumn"), "0")
    look.set(qn("w:noHBand"), "0")
    look.set(qn("w:noVBand"), "1")
    tblpr.insert_element_before(look, "w:tblCaption", "w:tblDescription")


def _add_table(doc, table_spec: dict, spec: dict, section, owner, counters: dict, *, appendix: bool = False) -> None:
    typo = spec["typography"]
    labels = _labels(spec)
    columns = table_spec.get("columns") or []
    rows = table_spec.get("rows") or []
    if not columns:
        raise ValueError("table needs at least one column")
    ncols = len(columns)
    width_mm = _text_width_mm(section)
    widths = [float(c.get("width_mm", 0) or 0) for c in columns]
    if sum(widths) <= 0:
        widths = [width_mm / ncols] * ncols
    elif sum(widths) > width_mm:
        scale = width_mm / sum(widths)
        widths = [w * scale for w in widths]
    widths = [max(12.0, w) for w in widths]
    if sum(widths) > width_mm:
        widths = [w * width_mm / sum(widths) for w in widths]
    twips = [_mm_twips(w) for w in widths]
    total = sum(twips)
    caption = table_spec.get("caption", "")

    n = table_spec.get("_number")
    if caption and n is None:
        counters["Table"] = counters.get("Table", 0) + 1
        n = counters["Table"]
    if caption:
        letter = table_spec.get("_appendix_letter")
        prefix = f"{letter}." if letter else ""
        reset = False
        if letter:
            started = counters.setdefault("_appendix_tables", set())
            reset = letter not in started
            started.add(letter)
        cap = doc.add_paragraph(style="Caption")
        cap.paragraph_format.keep_with_next = True
        cap.paragraph_format.space_before = Pt(8)
        cap.paragraph_format.space_after = Pt(2)
        add_seq_caption(cap, "Table", caption,
                        number_bookmark=f"tbl-{n}-num", caption_bookmark=f"tbl-{n}",
                        bookmark_owner=owner, display_label=labels["table"],
                        display_prefix=prefix, reset=reset)

    has_header = bool(table_spec.get("header", True))
    table = doc.add_table(rows=(1 if has_header else 0) + len(rows), cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    tblpr = table._tbl.tblPr
    _set_tbl_layout(table, total, first_row=has_header)
    _set_table_borders(table, kind=table_spec.get("borders", "booktabs"),
                       color=typo["color_rule"])
    if caption:
        prefix = f"{table_spec.get('_appendix_letter')}." if table_spec.get("_appendix_letter") else ""
        capnode = OxmlElement("w:tblCaption")
        capnode.set(qn("w:val"), f"{labels['table']} {prefix}{n} — {caption}")
        tblpr.append(capnode)
    desc = OxmlElement("w:tblDescription")
    desc.set(qn("w:val"), table_spec.get("alt", caption or f"{labels['table']} {n or ''}".strip()))
    tblpr.append(desc)

    # grid + cell widths
    grid = table._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
        if i < len(twips):
            gc.set(qn("w:w"), str(twips[i]))
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(twips):
                cell.width = Twips(twips[i])

    if has_header:
        hdr = table.rows[0]
        trpr = hdr._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trpr.append(th)
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)
        h = OxmlElement("w:trHeight")
        h.set(qn("w:val"), "420")
        h.set(qn("w:hRule"), "atLeast")
        trpr.append(h)
        for i, col in enumerate(columns):
            cell = hdr.cells[i]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.style = doc.styles["Table Text"]
            p.alignment = _align(col.get("align", "left"))
            run = p.add_run(str(col.get("header", "")))
            run.bold = True
            run.font.size = Pt(typo["table_pt"])
            fill = table_spec.get("header_fill", "F2F2F2")
            tcpr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), fill)
            tcpr.append(shd)

    data_start = 1 if has_header else 0
    for r_index, row_values in enumerate(rows):
        row = table.rows[data_start + r_index]
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        for i, value in enumerate(row_values):
            if i >= ncols:
                break
            cell = row.cells[i]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = cell.paragraphs[0]
            p.style = doc.styles["Table Text"]
            align = columns[i].get("align")
            if align is None:
                align = "right" if _looks_numeric(value) and not _looks_numeric(rows[0][0] if rows and rows[0] else "") else "left"
            p.alignment = _align(align)
            text = str(value) if value is not None else ""
            parts = text.split("\n")
            _add_text(p, parts[0], spec, appendix=appendix)
            for extra in parts[1:]:
                p.add_run().add_break()
                _add_text(p, extra, spec, appendix=appendix)
            if table_spec.get("zebra") and r_index % 2 == 1:
                tcpr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "F7F7F7")
                tcpr.append(shd)

    if table_spec.get("source"):
        sp = doc.add_paragraph()
        run = sp.add_run(f"{labels['source']}: {table_spec['source']}")
        run.italic = True
        run.font.size = Pt(typo["caption_pt"] - 0.5)
        run.font.color.rgb = RGBColor.from_string(typo["color_muted"])
        sp.paragraph_format.space_after = Pt(8)


# ---------------------------------------------------------------------------
# Cover, front matter, body, appendix, references
# ---------------------------------------------------------------------------

def _add_cover(doc, spec: dict, section) -> None:
    meta = spec["meta"]
    cover = spec["cover"]
    typo = spec["typography"]
    labels = _labels(spec)
    logo = cover.get("logo")
    if logo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run()
        path = Path(logo)
        if not path.is_absolute():
            path = Path(cover.get("_base_dir", ".")) / path
        run.add_picture(str(path), width=Mm(32))
        inline = doc.inline_shapes[-1]
        inline._inline.docPr.set("descr", cover.get("logo_alt", "Logo"))
        inline._inline.docPr.set("title", cover.get("logo_alt", "Logo"))
    for _ in range(2):
        doc.add_paragraph()
    p = doc.add_paragraph(style="Title")
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(meta.get("title", ""))
    run.font.size = Pt(28)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(typo["color_text"])
    if meta.get("subtitle"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(meta["subtitle"])
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor.from_string(typo["color_muted"])
    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(18)
    _paragraph_border(rule, edge="bottom", color=typo["color_accent"], sz=12)
    info = [
        (labels["doc_id"], meta.get("document_id", "")),
        (labels["version"], meta.get("version", "")),
        (labels["date"], meta.get("date", "")),
        (labels["classification"], meta.get("classification", "")),
    ]
    for label, value in info:
        if not value:
            continue
        p = doc.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(Mm(_text_width_mm(section)), WD_TAB_ALIGNMENT.RIGHT)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(label)
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor.from_string(typo["color_muted"])
        p.add_run("\t")
        run = p.add_run(value)
        run.font.size = Pt(10)
        run.bold = True
    for _ in range(2):
        doc.add_paragraph()
    if meta.get("organization"):
        p = doc.add_paragraph()
        run = p.add_run(meta["organization"])
        run.font.size = Pt(11)
        run.bold = True
    if meta.get("author"):
        p = doc.add_paragraph()
        run = p.add_run(meta["author"])
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor.from_string(typo["color_muted"])


def _add_field_list(doc, entries: list[dict], spec: dict, section, *, kind: str,
                    title: str) -> None:
    """List of figures/tables built from REF + PAGEREF, not a caption cache.

    A ``TOC \\c "Figure"`` field is the standard Word switch, but Word's cached
    result can repeat the first SEQ number when captions are updated in the same
    pass (observed on T039).  REF/PAGEREF point at the caption bookmarks, so the
    label and page stay live and correct on every update.
    """
    if not entries:
        return
    labels = _labels(spec)
    width_mm = _text_width_mm(section)
    p = doc.add_paragraph(style="TOC Heading")
    p.add_run(title)
    for entry in entries:
        para = doc.add_paragraph(style="toc 1")
        para.paragraph_format.tab_stops.add_tab_stop(Mm(width_mm), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        prefix = f"{entry.get('appendix_letter')}." if entry.get("appendix_letter") else ""
        placeholder = f"{labels[kind]} {prefix}{entry['number']}"
        add_cross_reference(para, entry["bookmark"], kind="text", result=placeholder)
        if entry.get("caption"):
            para.add_run(f" — {entry['caption']}")
        para.add_run("\t")
        add_cross_reference(para, entry["bookmark"], kind="page", result="1")


def _add_front_matter(doc, spec: dict, section, owner, manifest: dict) -> None:
    fm = spec["front_matter"]
    labels = _labels(spec)
    toc = fm.get("toc", {})
    if toc.get("enabled", True):
        p = doc.add_paragraph(style="TOC Heading")
        p.add_run(toc.get("title") or labels["toc"])
        tp = doc.add_paragraph()
        add_toc(tp, levels=int(toc.get("levels", 3)))
        doc.add_page_break()
    for key, kind, label_key, entries in [
        ("list_of_figures", "figure", "figures", manifest.get("figures", [])),
        ("list_of_tables", "table", "tables", manifest.get("tables", [])),
    ]:
        cfg = fm.get(key, {})
        if not cfg.get("enabled"):
            continue
        if entries:
            _add_field_list(doc, entries, spec, section, kind=kind,
                            title=cfg.get("title") or labels[label_key])
            doc.add_page_break()
    abstract = fm.get("abstract", {})
    if abstract.get("enabled") or abstract.get("text"):
        p = doc.add_paragraph(style="Front Matter Heading")
        p.add_run(abstract.get("title") or labels["abstract"])
        p.paragraph_format.page_break_before = False
        for para in (abstract.get("text") or "").split("\n\n"):
            if para.strip():
                body = doc.add_paragraph()
                _add_text(body, para.strip(), spec)
        if abstract.get("keywords"):
            p = doc.add_paragraph()
            run = p.add_run(f"{labels['keywords']}: ")
            run.bold = True
            p.add_run(", ".join(abstract["keywords"]))
        doc.add_page_break()


def _add_references(doc, spec: dict, owner) -> None:
    refs = spec.get("references", {})
    if not refs.get("enabled") and not refs.get("items"):
        return
    labels = _labels(spec)
    p = doc.add_heading(refs.get("title") or labels["references"], 1)
    p.paragraph_format.page_break_before = True
    for i, item in enumerate(refs.get("items", []), start=1):
        if isinstance(item, str):
            item = {"text": item}
        key = re.sub(r"[^A-Za-z0-9_-]", "-", str(item.get("key") or f"ref{i}"))
        label = item.get("label") or f"[{i}]"
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Mm(8)
        p.paragraph_format.first_line_indent = Mm(-8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        label_bm = f"ref-{key}-label"
        full_bm = f"ref-{key}"
        full_start = add_bookmark_start(p, full_bm, owner)
        label_start = add_bookmark_start(p, label_bm, owner)
        p.add_run(label + " ")
        add_bookmark_end(p, label_start, owner)
        run = p.add_run(item.get("text", ""))
        run.font.size = Pt(spec["typography"]["reference_pt"])
        add_bookmark_end(p, full_start, owner)


def _add_appendix(doc, spec: dict, section, owner, counters: dict) -> None:
    appendices = spec.get("appendix") or []
    if not appendices:
        return
    labels = _labels(spec)
    appendix_num = add_appendix_numbering(doc, prefix=labels["appendix"])
    for i, app in enumerate(appendices):
        letter = app.get("_letter") or app.get("letter") or chr(65 + i)
        title = app.get("title") or f"{labels['appendix']} {letter}"
        p = doc.add_heading(_strip_number(title), 1)
        p.paragraph_format.page_break_before = True
        apply_numbering(p, appendix_num, 0)
        add_bookmark_to_paragraph(p, f"app-{letter.lower()}", owner)
        _add_blocks(doc, app.get("blocks", []), spec, section, owner, counters,
                    appendix=True, appendix_num_id=appendix_num, heading_level_start=2)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def _resolve_paths(spec: dict, base_dir: Path) -> None:
    def walk(node):
        if isinstance(node, dict):
            if "path" in node and isinstance(node["path"], str) and not Path(node["path"]).is_absolute():
                node["_base_dir"] = str(base_dir)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(spec)
    if spec["cover"].get("logo"):
        spec["cover"]["_base_dir"] = str(base_dir)


def build_document(spec_path: str | Path, out_path: str | Path, *,
                   system: dict | None = None, update: str = "none",
                   render_dir: str | Path | None = None) -> dict:
    spec_path = Path(spec_path)
    raw = json.loads(spec_path.read_text(encoding="utf-8"))
    spec = _deep_merge(DEFAULTS, raw)
    _resolve_paths(spec, spec_path.parent)
    if not spec["meta"].get("title"):
        raise ValueError("meta.title is required")
    if not spec["sections"]:
        raise ValueError("at least one section is required")
    manifest = _number_blocks(spec)

    doc = Document()
    doc._next_bookmark_id = 1000  # type: ignore[attr-defined]
    _setup_styles(doc, spec)
    set_update_fields(doc, True)
    set_even_odd_headers(doc, bool(spec["headers_footers"].get("odd_even")))
    _set_mirror_margins(doc, bool(spec["page"].get("mirror_margins")))
    add_heading_numbering(doc)
    _set_core_properties(doc, spec)

    cover_section = doc.sections[0]
    _setup_page(cover_section, spec)
    width = _text_width_mm(cover_section)
    if spec["cover"].get("enabled", True):
        _add_cover(doc, spec, cover_section)
        cover_section.different_first_page_header_footer = True
        _clear(cover_section.header)
        _clear(cover_section.footer)
        if spec["headers_footers"].get("odd_even"):
            _clear(cover_section.even_page_header)
            _clear(cover_section.even_page_footer)

    front_section = doc.add_section(WD_SECTION.NEW_PAGE)
    _setup_page(front_section, spec)
    _add_front_matter(doc, spec, front_section, doc, manifest)
    front_section.different_first_page_header_footer = False
    if spec["headers_footers"].get("enabled", True):
        _write_header(front_section, spec, width, chapter=False)
        _write_footer(front_section, spec, width, roman=True)
        if spec["headers_footers"].get("odd_even"):
            _write_header(front_section, spec, width, even=True)
            _write_footer(front_section, spec, width, even=True, roman=True)
    set_page_numbering(front_section, fmt="lowerRoman", start=1)

    body_section = doc.add_section(WD_SECTION.NEW_PAGE)
    _setup_page(body_section, spec)
    body_section.different_first_page_header_footer = False
    if spec["headers_footers"].get("enabled", True):
        _write_header(body_section, spec, width)
        _write_footer(body_section, spec, width)
        if spec["headers_footers"].get("odd_even"):
            _write_header(body_section, spec, width, even=True)
            _write_footer(body_section, spec, width, even=True)
    set_page_numbering(body_section, fmt="decimal", start=1)

    counters: dict[str, int] = {"Figure": 0, "Table": 0}
    for i, section_spec in enumerate(spec["sections"]):
        heading = section_spec.get("heading") or section_spec.get("title")
        level = int(section_spec.get("level", 1))
        if heading:
            p = doc.add_heading(_strip_number(heading), level)
            p.paragraph_format.page_break_before = bool(section_spec.get("page_break_before", i > 0))
            add_bookmark_to_paragraph(p, f"sec-{i + 1}", doc)
        _add_blocks(doc, section_spec.get("blocks", []), spec, body_section, doc, counters)

    _add_references(doc, spec, doc)
    _add_appendix(doc, spec, body_section, doc, counters)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)

    updated_by = None
    if update not in {"none", "auto", "wordcraft", "word"}:
        raise ValueError("update must be none|auto|wordcraft|word")
    if update in {"auto", "word"}:
        updated_by = _update_with_word(out_path)
    if update == "auto" and not updated_by:
        updated_by = _update_with_wordcraft(out_path)
    if update == "wordcraft":
        updated_by = _update_with_wordcraft(out_path)
    if updated_by == "wordcraft":
        _repair_alt_text(out_path)

    report = {
        "ok": True,
        "output": str(out_path),
        "sha256": hashlib.sha256(out_path.read_bytes()).hexdigest(),
        "bytes": out_path.stat().st_size,
        "updated_by": updated_by,
        "spec": str(spec_path),
    }
    audit = audit_docx(out_path, system=system)
    report["audit"] = audit.as_dict()
    report["ok"] = audit.ok
    if updated_by:
        audit2 = audit_docx(out_path, system=system)
        report["audit_after_update"] = audit2.as_dict()
        report["ok"] = audit2.ok
    if render_dir:
        report["rendered"] = _render_document(out_path, Path(render_dir))
    return report


def _update_with_wordcraft(docx_path: Path) -> str | None:
    try:
        try:
            from .wordcraft_bridge import find_wordcraft_cli
        except ImportError:
            from wordcraft_bridge import find_wordcraft_cli
    except Exception:
        return None
    cli = find_wordcraft_cli()
    if not cli:
        return None
    tmp = docx_path.with_name(docx_path.stem + ".fields.docx")
    try:
        res = subprocess.run([str(cli), "convert", str(docx_path), str(tmp), "--update-fields"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if res.returncode != 0 or not tmp.is_file():
            return None
        shutil.move(str(tmp), str(docx_path))
        return "wordcraft"
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _update_with_word(docx_path: Path) -> str | None:
    """Refresh every field with Microsoft Word itself (rung 4 evidence).

    The TOC is updated three times: Word updates fields in document order, so a
    ``TOC \\c "Figure"`` that appears before the captions can see an empty
    sequence on the first pass.  Repagination between passes makes the second
    and third pass stable.
    """
    try:
        import win32com.client as win32
    except ImportError:
        return _update_with_word_powershell(docx_path)
    word = None
    doc = None
    try:
        word = win32.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(docx_path.resolve()), False, False, False)
        for _ in range(3):
            doc.Repaginate()
            doc.Fields.Update()
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
        doc.Save()
        return "word"
    except Exception:
        return None
    finally:
        if doc is not None:
            try:
                doc.Close(0)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass


def _update_with_word_powershell(docx_path: Path) -> str | None:
    """Fallback when pywin32 is absent; same three-pass refresh."""
    if sys.platform != "win32":
        return None
    script = (
        "$ErrorActionPreference='Stop';$w=New-Object -ComObject Word.Application;"
        "$w.Visible=$false;$w.DisplayAlerts=0;"
        f"$d=$w.Documents.Open('{str(docx_path).replace(chr(39), chr(39)+chr(39))}',"
        "$false,$false,$false);"
        "for($i=0;$i -lt 3;$i++){$d.Repaginate();$d.Fields.Update()|Out-Null;"
        "foreach($t in $d.TablesOfContents){$t.Update()|Out-Null}};"
        "$d.Save();$d.Close(0);$w.Quit()"
    )
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                             capture_output=True, text=True, timeout=180, check=False)
        return "word" if res.returncode == 0 else None
    except Exception:
        return None


def _repair_alt_text(docx_path: Path) -> None:
    """WordCraft's converter drops wp:docPr@descr but keeps @title; restore it."""
    import zipfile
    import tempfile
    from lxml import etree
    try:
        with zipfile.ZipFile(docx_path) as zin:
            members = {name: zin.read(name) for name in zin.namelist()}
    except Exception:
        return
    changed = False
    for name, blob in list(members.items()):
        if not (name.startswith("word/") and name.endswith(".xml")):
            continue
        if not ("document" in name or "header" in name or "footer" in name):
            continue
        try:
            root = etree.fromstring(blob)
        except Exception:
            continue
        local = False
        for docpr in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"):
            if not docpr.get("descr") and docpr.get("title"):
                docpr.set("descr", docpr.get("title"))
                local = True
        if local:
            members[name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            changed = True
    if not changed:
        return
    tmp = docx_path.with_suffix(".alt.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, blob in members.items():
            zout.writestr(name, blob)
    tmp.replace(docx_path)


def _render_document(docx_path: Path, out_dir: Path) -> list[str]:
    """Render through Word -> PDF -> PNG when available, else WordCraft."""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        import win32com.client as win32
        import fitz  # PyMuPDF
        word = win32.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(docx_path.resolve()), False, True, False)
        pdf = out_dir / "document.pdf"
        doc.ExportAsFixedFormat(str(pdf), 17)
        doc.Close(0)
        word.Quit()
        paths = []
        with fitz.open(pdf) as pdf_doc:
            for i, page in enumerate(pdf_doc, start=1):
                target = out_dir / f"page-{i:02d}.png"
                page.get_pixmap(dpi=150).save(target)
                paths.append(str(target))
        return paths
    except Exception:
        return _render_wordcraft(docx_path, out_dir)


def _render_wordcraft(docx_path: Path, out_dir: Path) -> list[str]:
    try:
        try:
            from .wordcraft_bridge import inspect_document, render_page
        except ImportError:
            from wordcraft_bridge import inspect_document, render_page
    except Exception:
        return []
    try:
        info = inspect_document(docx_path)
        pages = int(info.get("pages") or 1)
    except Exception:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for page in range(1, pages + 1):
        target = out_dir / f"page-{page:02d}.png"
        try:
            render_page(docx_path, target, page=page, scale=2)
            paths.append(str(target))
        except Exception:
            break
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    try:  # Windows consoles often default to cp1258; JSON contains Vietnamese.
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("build", help="Build a DOCX from a JSON spec")
    p.add_argument("spec", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--update", choices=["none", "auto", "wordcraft", "word"], default="none")
    p.add_argument("--render", type=Path, default=None)
    p.add_argument("--report", type=Path, default=None)
    p.add_argument("--no-audit", action="store_true")

    p = sub.add_parser("audit", help="Structural audit of a DOCX")
    p.add_argument("docx", type=Path)
    p.add_argument("--md", type=Path, default=None)

    p = sub.add_parser("inspect", help="List fields, bookmarks and structural counts")
    p.add_argument("docx", type=Path)

    args = parser.parse_args()
    if args.cmd == "build":
        report = build_document(args.spec, args.output, update=args.update, render_dir=args.render)
        data = report if not args.no_audit else {k: v for k, v in report.items() if k != "audit"}
        text = json.dumps(data, indent=2, ensure_ascii=False)
        print(text)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text, encoding="utf-8")
            if not args.no_audit:
                md = ["# DOCX build report", "", f"**ok:** {report['ok']}", "",
                      f"- output: `{report['output']}`", f"- sha256: `{report['sha256']}`",
                      f"- updated_by: {report['updated_by']}", ""]
                audit = report["audit"]
                for label, items in [("Errors", audit["errors"]), ("Warnings", audit["warnings"]), ("Notes", audit["notes"])]:
                    md.append(f"## {label}")
                    md.extend(f"- {x}" for x in items) if items else md.append("- none")
                    md.append("")
                args.report.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
        raise SystemExit(0 if report["ok"] else 1)
    elif args.cmd == "audit":
        report = audit_docx(args.docx)
        print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
        if args.md:
            lines = ["# DOCX audit", "", f"**ok:** {report.ok}", ""]
            for label, items in [("Errors", report.errors), ("Warnings", report.warnings), ("Notes", report.notes)]:
                lines.append(f"## {label}")
                lines.extend(f"- {x}" for x in items) if items else lines.append("- none")
                lines.append("")
            args.md.write_text("\n".join(lines), encoding="utf-8")
        raise SystemExit(0 if report.ok else 1)
    else:
        from word_field_kit import field_summary
        print(json.dumps(field_summary(args.docx), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
