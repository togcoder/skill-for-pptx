#!/usr/bin/env python3
"""Word field, bookmark, caption and cross-reference kit (T039, docx).

Status: EXPERIMENTAL — T039 [docx], review requested.  Not a canonical module
until an independent review accepts it.


The helpers here write *real* Word fields, not flattened text.  A TOC produced by
this module is a ``TOC`` field whose entries Word can refresh; a figure number is
a ``SEQ`` field; "see Figure 3" is a ``REF`` field pointing at a bookmark.

The module is deliberately dependency-light: python-docx for the package, lxml
for inspection.  It does not require WordCraft, Word, LibreOffice or network
access.  Field *results* (page numbers, caption numbers) are only placeholders
until a layout engine refreshes them; ``set_update_fields`` asks Word to do that
on open, and ``document_forge.py --update wordcraft|word`` can do it before
delivery.

OOXML references:
  * ISO/IEC 29500-1:2016 §17.16 (fields), §17.13 (bookmarks), §17.9 (headers),
    §17.18 (tables), §20.4 (drawings).
  * ECMA-376 Part 1, same clause numbers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from pathlib import Path
from typing import Iterable, Iterator
import zipfile

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W_NS, "wp": WP_NS, "a": A_NS, "r": R_NS}
SYSTEM_PATH = Path(__file__).resolve().parents[1] / "domains" / "docx" / "data" / "document_system.json"


def _load_system() -> dict:
    try:
        return json.loads(SYSTEM_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

# Word field instructions we write.  Keep them in one place so the auditor and
# the generator cannot drift apart.
FIELD_TOC = r'TOC \o "1-{levels}" \h \z \u'
FIELD_TOC_FIGURES = r'TOC \h \z \c "Figure"'
FIELD_TOC_TABLES = r'TOC \h \z \c "Table"'
FIELD_PAGE = r'PAGE \* MERGEFORMAT'
FIELD_NUMPAGES = r'NUMPAGES \* MERGEFORMAT'
FIELD_SECTIONPAGES = r'SECTIONPAGES \* MERGEFORMAT'
FIELD_STYLEREF = r'STYLEREF "{style}" \* MERGEFORMAT'
FIELD_SEQ = r'SEQ {label} \* ARABIC'
FIELD_SEQ_CHAPTER = r'SEQ {label} \* ARABIC \s {level}'
FIELD_REF = r'REF {bookmark} \h'
FIELD_PAGEREF = r'PAGEREF {bookmark} \h'
FIELD_REF_ABOVE_BELOW = r'REF {bookmark} \p \h'
FIELD_CITATION = r'REF {bookmark} \h'

# Word's UI discourages hyphens, but the OOXML bookmark name is a string and
# Word itself preserves hyphens written by other producers.  We allow them so
# semantic names such as ``fig-1-num`` stay readable; spaces and punctuation
# outside this set are rejected.
_BOOKMARK_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,39}$")


# ---------------------------------------------------------------------------
# Low-level XML helpers
# ---------------------------------------------------------------------------

def _el(tag: str, **attrs: str):
    node = OxmlElement(tag)
    for key, value in attrs.items():
        node.set(qn(f"w:{key}"), value)
    return node


def _run(child) -> object:
    run = OxmlElement("w:r")
    run.append(child)
    return run


def _text_run(text: str):
    run = OxmlElement("w:r")
    node = OxmlElement("w:t")
    node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    node.text = text
    run.append(node)
    return run


def _fld_char(kind: str, *, dirty: bool = False, lock: bool = False):
    node = OxmlElement("w:fldChar")
    node.set(qn("w:fldCharType"), kind)
    if dirty:
        node.set(qn("w:dirty"), "true")
    if lock:
        node.set(qn("w:lock"), "true")
    return node


def add_field(paragraph, instr: str, result: str = "", *, dirty: bool = True,
              lock: bool = False) -> None:
    """Append a complex field to a paragraph.

    The field has the canonical begin / instrText / separate / result / end
    runs.  ``dirty`` marks it for refresh; Word shows the cached ``result``
    until then.  A field with no result is still valid but Word displays
    nothing, so callers normally pass a readable placeholder.
    """
    p = paragraph._p
    p.append(_run(_fld_char("begin", dirty=dirty, lock=lock)))
    instr_run = OxmlElement("w:r")
    instr_el = OxmlElement("w:instrText")
    instr_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr_el.text = f" {instr} "
    instr_run.append(instr_el)
    p.append(instr_run)
    p.append(_run(_fld_char("separate")))
    if result:
        p.append(_text_run(result))
    p.append(_run(_fld_char("end")))


def add_toc(paragraph, *, levels: int = 3, hyperlinks: bool = True,
            result: str = "Mục lục sẽ được cập nhật trong Word (F9).") -> None:
    """Insert a TOC field.  ``levels`` is the number of heading levels."""
    instr = rf'TOC \o "1-{levels}" \h \z \u' if hyperlinks else rf'TOC \o "1-{levels}" \z \u'
    add_field(paragraph, instr, result=result, dirty=True)


def add_toc_of(paragraph, label: str, *, result: str = "") -> None:
    r"""Insert a table of figures/tables (``TOC \c "Figure"``)."""
    add_field(paragraph, rf'TOC \h \z \c "{label}"', result=result or f"Danh mục {label} sẽ được cập nhật.", dirty=True)


def add_page_number(paragraph, kind: str = "PAGE", *, result: str = "1") -> None:
    kind = kind.upper()
    instr = {"PAGE": FIELD_PAGE, "NUMPAGES": FIELD_NUMPAGES, "SECTIONPAGES": FIELD_SECTIONPAGES}.get(kind, kind)
    add_field(paragraph, instr, result=result, dirty=True)


def add_styleref(paragraph, style_name: str, *, result: str = "[Chương]") -> None:
    add_field(paragraph, FIELD_STYLEREF.format(style=style_name), result=result, dirty=True)


def add_seq_caption(paragraph, label: str, caption: str, *, chapter_level: int | None = None,
                    number_bookmark: str | None = None,
                    caption_bookmark: str | None = None,
                    bookmark_owner=None, display_label: str | None = None,
                    display_prefix: str = "", reset: bool = False) -> tuple[int | None, int | None]:
    r"""Write ``Figure <SEQ> — caption`` and bookmark the number and the caption.

    ``label`` is the SEQ identifier (``Figure``/``Table``, also used by
    ``TOC \c``); ``display_label`` is what the reader sees (``Hình``/``Bảng``).
    ``bookmark_owner`` is the document (or any object with a
    ``_next_bookmark_id`` integer attribute).  Returns
    ``(number_bookmark_id, caption_bookmark_id)``.
    """
    if chapter_level:
        instr = FIELD_SEQ_CHAPTER.format(label=label, level=chapter_level)
    else:
        instr = FIELD_SEQ.format(label=label)
    if reset:
        instr += r" \r 1"
    number_id = None
    caption_id = None
    if caption_bookmark or number_bookmark:
        owner = bookmark_owner
        if owner is None:
            raise ValueError("bookmark_owner is required when bookmarking a caption")
        if caption_bookmark:
            caption_id = add_bookmark_start(paragraph, caption_bookmark, owner)
        paragraph.add_run(f"{display_label or label} ")
        if number_bookmark:
            number_id = add_bookmark_start(paragraph, number_bookmark, owner)
        if display_prefix:
            paragraph.add_run(display_prefix)
        add_field(paragraph, instr, result="1", dirty=True)
        if number_bookmark:
            add_bookmark_end(paragraph, number_id, owner)
        if caption_bookmark:
            add_bookmark_end(paragraph, caption_id, owner)
        paragraph.add_run(" — ")
        paragraph.add_run(caption)
    else:
        paragraph.add_run(f"{display_label or label} ")
        if display_prefix:
            paragraph.add_run(display_prefix)
        add_field(paragraph, instr, result="1", dirty=True)
        paragraph.add_run(f" — {caption}")
    return number_id, caption_id


def _bookmark_id(owner) -> int:
    value = getattr(owner, "_next_bookmark_id", None)
    if value is None:
        raise ValueError("owner must expose _next_bookmark_id")
    owner._next_bookmark_id = int(value) + 1
    return int(value)


def add_bookmark_start(paragraph, name: str, owner) -> int:
    if not _BOOKMARK_NAME.match(name):
        raise ValueError(f"invalid bookmark name: {name!r}")
    bid = _bookmark_id(owner)
    node = OxmlElement("w:bookmarkStart")
    node.set(qn("w:id"), str(bid))
    node.set(qn("w:name"), name)
    paragraph._p.append(node)
    return bid


def add_bookmark_end(paragraph, bid: int, owner=None) -> None:
    node = OxmlElement("w:bookmarkEnd")
    node.set(qn("w:id"), str(bid))
    paragraph._p.append(node)


def add_bookmark_to_paragraph(paragraph, name: str, owner) -> int:
    """Bookmark the whole paragraph (after pPr, before the first run)."""
    if not _BOOKMARK_NAME.match(name):
        raise ValueError(f"invalid bookmark name: {name!r}")
    bid = _bookmark_id(owner)
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bid))
    start.set(qn("w:name"), name)
    ppr = paragraph._p.find(qn("w:pPr"))
    if ppr is not None:
        ppr.addnext(start)
    else:
        paragraph._p.insert(0, start)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bid))
    paragraph._p.append(end)
    return bid


def add_cross_reference(paragraph, bookmark: str, *, kind: str = "text",
                        result: str = "?", label: str | None = None) -> None:
    """Insert a REF/PAGEREF field.

    kind:
      * ``text``  – the bookmarked text (``REF bookmark \\h``)
      * ``page``  – page number (``PAGEREF bookmark \\h``)
      * ``aboveBelow`` – "above"/"below" (``REF bookmark \\p \\h``)
    """
    if kind == "page":
        instr = FIELD_PAGEREF.format(bookmark=bookmark)
        placeholder = result if result != "?" else "1"
    elif kind == "aboveBelow":
        instr = FIELD_REF_ABOVE_BELOW.format(bookmark=bookmark)
        placeholder = result if result != "?" else "above"
    else:
        instr = FIELD_REF.format(bookmark=bookmark)
        placeholder = result
    if label:
        paragraph.add_run(f"{label} ")
    add_field(paragraph, instr, result=placeholder, dirty=True)


def add_citation(paragraph, bookmark: str, *, result: str = "[1]") -> None:
    add_field(paragraph, FIELD_CITATION.format(bookmark=bookmark), result=result, dirty=True)


def set_update_fields(document, value: bool = True) -> None:
    """Set ``w:updateFields`` in settings.xml (Word refreshes fields on open)."""
    settings = document.settings.element
    existing = settings.find(qn("w:updateFields"))
    if value:
        if existing is None:
            node = OxmlElement("w:updateFields")
            node.set(qn("w:val"), "true")
            # It belongs after defaultTabStop and before compat.  Insert before
            # the first later sibling when one exists; append is accepted by
            # Word but this keeps the part closer to schema order.
            successors = [qn("w:compat"), qn("w:rsids"), qn("w:mathPr"), qn("w:themeFontLang"),
                          qn("w:clrSchemeMapping"), qn("w:shapeDefaults"), qn("w:decimalSymbol"),
                          qn("w:listSeparator")]
            for tag in successors:
                nxt = settings.find(tag)
                if nxt is not None:
                    nxt.addprevious(node)
                    return
            settings.append(node)
        else:
            existing.set(qn("w:val"), "true")
    elif existing is not None:
        settings.remove(existing)


def set_even_odd_headers(document, value: bool = True) -> None:
    settings = document.settings.element
    existing = settings.find(qn("w:evenAndOddHeaders"))
    if value and existing is None:
        node = OxmlElement("w:evenAndOddHeaders")
        settings.append(node)
    elif not value and existing is not None:
        settings.remove(existing)


def set_cell_language(cell, language: str = "vi-VN") -> None:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            rpr = run._r.get_or_add_rPr()
            lang = rpr.find(qn("w:lang"))
            if lang is None:
                lang = OxmlElement("w:lang")
                rpr.append(lang)
            lang.set(qn("w:val"), language)
            lang.set(qn("w:eastAsia"), language)


# ---------------------------------------------------------------------------
# Numbering
# ---------------------------------------------------------------------------

def _next_numbering_id(numbering, tag: str, attr: str) -> int:
    values = [int(n.get(qn(attr))) for n in numbering.findall(qn(tag)) if n.get(qn(attr)) is not None]
    return max(values, default=0) + 1


def _make_abstract_num(numbering, *, kind: str, start: int = 1, prefix: str = "Appendix") -> tuple[int, int]:
    """Create an abstractNum + num pair; return (abstract_id, num_id)."""
    abstract_id = _next_numbering_id(numbering, "w:abstractNum", "w:abstractNumId")
    num_id = _next_numbering_id(numbering, "w:num", "w:numId")
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(abstract_id))
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "multilevel")
    abstract.append(multi)

    for level in range(9):
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), str(level))
        start_el = OxmlElement("w:start")
        start_el.set(qn("w:val"), str(start if level == 0 else 1))
        lvl.append(start_el)
        fmt = OxmlElement("w:numFmt")
        if kind == "appendix" and level == 0:
            fmt.set(qn("w:val"), "upperLetter")
        else:
            fmt.set(qn("w:val"), "decimal")
        lvl.append(fmt)
        text = OxmlElement("w:lvlText")
        if kind == "appendix":
            text.set(qn("w:val"), f"{prefix} %1" if level == 0 else ".".join(f"%{i}" for i in range(1, level + 2)))
        else:
            text.set(qn("w:val"), ".".join(f"%{i}" for i in range(1, level + 2)))
        lvl.append(text)
        jc = OxmlElement("w:lvlJc")
        jc.set(qn("w:val"), "left")
        lvl.append(jc)
        suff = OxmlElement("w:suff")
        suff.set(qn("w:val"), "space")
        lvl.append(suff)
        ppr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "0")
        ind.set(qn("w:firstLine"), "0")
        ppr.append(ind)
        lvl.append(ppr)
        if level < 9:
            pstyle = OxmlElement("w:pStyle")
            pstyle.set(qn("w:val"), f"Heading{level + 1}")
            lvl.append(pstyle)
        abstract.append(lvl)

    # abstractNum elements precede num elements.
    first_num = numbering.find(qn("w:num"))
    if first_num is not None:
        first_num.addprevious(abstract)
    else:
        numbering.append(abstract)

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(num_id))
    an = OxmlElement("w:abstractNumId")
    an.set(qn("w:val"), str(abstract_id))
    num.append(an)
    numbering.append(num)
    return abstract_id, num_id


def add_heading_numbering(document, *, kind: str = "iso2145") -> int:
    """Link a multilevel list to Heading 1..9 and return the numId.

    ``kind='iso2145'`` writes 1, 1.1, 1.1.1 (no trailing dot).  Word's default
    is 1., 1.1., ...; ISO 2145 recommends no full stop after the final number.
    """
    numbering = document.part.numbering_part.element
    _abstract_id, num_id = _make_abstract_num(numbering, kind="body")
    for level in range(9):
        style = document.styles[f"Heading {level + 1}"]
        ppr = style.element.get_or_add_pPr()
        numpr = ppr.get_or_add_numPr()
        numpr.get_or_add_ilvl().val = level
        numpr.get_or_add_numId().val = num_id
    return num_id


def add_appendix_numbering(document, *, prefix: str = "Appendix") -> int:
    """Create an appendix list (Appendix A, A.1, ...) and return its numId."""
    numbering = document.part.numbering_part.element
    _abstract_id, num_id = _make_abstract_num(numbering, kind="appendix", prefix=prefix)
    return num_id


def apply_numbering(paragraph, num_id: int, level: int = 0) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    numpr = ppr.get_or_add_numPr()
    numpr.get_or_add_ilvl().val = level
    numpr.get_or_add_numId().val = num_id


def set_page_numbering(section, *, fmt: str = "decimal", start: int | None = 1) -> None:
    """Set section page-number format.  ``fmt``: decimal, lowerRoman, upperRoman."""
    sectpr = section._sectPr
    node = sectpr.find(qn("w:pgNumType"))
    if node is None:
        node = OxmlElement("w:pgNumType")
        # pgNumType sits after lnNumType and before cols.
        cols = sectpr.find(qn("w:cols"))
        if cols is not None:
            cols.addprevious(node)
        else:
            sectpr.append(node)
    node.set(qn("w:fmt"), fmt)
    if start is None:
        node.attrib.pop(qn("w:start"), None)
    else:
        node.set(qn("w:start"), str(start))


# ---------------------------------------------------------------------------
# Inspection / audit
# ---------------------------------------------------------------------------

@dataclass
class FieldRecord:
    part: str
    instr: str
    result: str = ""
    complete: bool = False
    dirty: bool = False
    locked: bool = False
    depth: int = 0

    @property
    def command(self) -> str:
        return (self.instr.strip().split() or [""])[0].upper()


@dataclass
class AuditReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    fields: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "notes": self.notes,
            "stats": self.stats,
            "fields": self.fields,
        }


def _read_xml(zf: zipfile.ZipFile, name: str):
    try:
        return etree.fromstring(zf.read(name))
    except KeyError:
        return None


def _field_records(root, part: str) -> list[FieldRecord]:
    records: list[FieldRecord] = []
    stack: list[FieldRecord] = []
    for run in root.iter(qn("w:r")):
        fld = run.find(qn("w:fldChar"))
        if fld is not None:
            kind = fld.get(qn("w:fldCharType"))
            if kind == "begin":
                rec = FieldRecord(part=part, instr="", dirty=fld.get(qn("w:dirty")) == "true",
                                  locked=fld.get(qn("w:lock")) == "true", depth=len(stack))
                stack.append(rec)
                records.append(rec)
            elif kind == "separate" and stack:
                stack[-1].result = ""
            elif kind == "end" and stack:
                stack.pop().complete = True
            continue
        instr = run.find(qn("w:instrText"))
        if instr is not None and stack:
            stack[-1].instr += instr.text or ""
            continue
        text = run.find(qn("w:t"))
        if text is not None and stack:
            stack[-1].result += text.text or ""
    # fldSimple is a one-run field
    for simple in root.iter(qn("w:fldSimple")):
        instr = simple.get(qn("w:instr")) or ""
        text = "".join(t.text or "" for t in simple.iter(qn("w:t")))
        records.append(FieldRecord(part=part, instr=instr, result=text, complete=True))
    return records


def read_fields(path: str | Path) -> list[FieldRecord]:
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.startswith("word/") and n.endswith(".xml")
                 and ("document" in n or "header" in n or "footer" in n or "footnote" in n or "endnote" in n)]
        out: list[FieldRecord] = []
        for name in sorted(names):
            root = _read_xml(zf, name)
            if root is not None:
                out.extend(_field_records(root, name))
        return out


def _text_of(node) -> str:
    return "".join(t.text or "" for t in node.iter(qn("w:t")))


def _style_outline(document_root, styles_root) -> dict[str, int]:
    outline: dict[str, int] = {}
    if styles_root is None:
        return outline
    for style in styles_root.findall(qn("w:style")):
        sid = style.get(qn("w:styleId")) or ""
        ppr = style.find(qn("w:pPr"))
        if ppr is None:
            continue
        lvl = ppr.find(qn("w:outlineLvl"))
        if lvl is not None:
            try:
                outline[sid] = int(lvl.get(qn("w:val")))
            except (TypeError, ValueError):
                pass
    return outline


def audit_docx(path: str | Path, *, system: dict | None = None) -> AuditReport:
    """Structural audit of a DOCX package.

    This is a rung-1 check: XML invariants, not a Word render.  It verifies the
    things that make TOC/caption/cross-reference links *real*:
      * balanced fields and a TOC when headings exist;
      * unique, valid bookmarks and resolvable REF/PAGEREF targets;
      * heading hierarchy and outline levels;
      * tables whose grid fits the text column and whose header repeats;
      * inline pictures with alt text and sane effective DPI;
      * A4/Letter page geometry and language metadata.
    """
    path = Path(path)
    system = system or _load_system()
    margin_min_mm = float(system.get("page", {}).get("margin_min_mm", 20))
    dpi_min = float(system.get("figure", {}).get("dpi_screen_min", 150))
    width_tolerance = int(system.get("table", {}).get("width_tolerance_twips", 20))
    max_jump = int(system.get("accessibility", {}).get("heading_hierarchy_max_jump", 1))
    toc_default = int(system.get("fields", {}).get("toc_levels", 3))
    alt_required = bool(system.get("accessibility", {}).get("alt_text_required", True))
    table_header_required = bool(system.get("accessibility", {}).get("table_header_required", True))
    report = AuditReport(ok=True)
    with zipfile.ZipFile(path) as zf:
        document = _read_xml(zf, "word/document.xml")
        styles = _read_xml(zf, "word/styles.xml")
        settings = _read_xml(zf, "word/settings.xml")
        core = _read_xml(zf, "docProps/core.xml")
        numbering = _read_xml(zf, "word/numbering.xml")
        if document is None:
            report.ok = False
            report.errors.append("word/document.xml is missing or unreadable")
            return report

        fields: list[FieldRecord] = []
        bookmarks: dict[str, int] = {}
        bookmark_ids: dict[str, str] = {}
        drawings: list[dict] = []
        tables: list[dict] = []
        sections: list[dict] = []
        paragraphs: list[dict] = []
        for part in ["word/document.xml"] + [n for n in zf.namelist()
                                              if n.startswith("word/") and (n.startswith("word/header") or n.startswith("word/footer"))]:
            root = _read_xml(zf, part)
            if root is None:
                continue
            fields.extend(_field_records(root, part))
            for start in root.iter(qn("w:bookmarkStart")):
                name = start.get(qn("w:name")) or ""
                bid = start.get(qn("w:id")) or ""
                if name in bookmarks:
                    report.errors.append(f"duplicate bookmark name: {name}")
                bookmarks[name] = bookmarks.get(name, 0) + 1
                bookmark_ids[bid] = name
            for drawing in root.iter(qn("wp:inline")):
                drawings.append(_drawing_info(drawing, "inline", part))
            for drawing in root.iter(qn("wp:anchor")):
                drawings.append(_drawing_info(drawing, "anchor", part))
            for tbl in root.iter(qn("w:tbl")):
                tables.append(_table_info(tbl))
            for sect in root.iter(qn("w:sectPr")):
                sections.append(_section_info(sect))
            for p in root.iter(qn("w:p")):
                ppr = p.find(qn("w:pPr"))
                style = None
                if ppr is not None:
                    ps = ppr.find(qn("w:pStyle"))
                    if ps is not None:
                        style = ps.get(qn("w:val"))
                paragraphs.append({"style": style, "text": _text_of(p)})

        # Resolve image parts so effective DPI is real, not guessed.  The
        # drawing extent is in EMU; pixels come from the related image blob.
        try:
            from docx.image.image import Image as _DocxImage
            _image_available = True
        except Exception:  # pragma: no cover - python-docx is a hard dependency elsewhere
            _image_available = False
        for d in drawings:
            rid = d.get("rid")
            part = d.get("part") or ""
            if not rid or not _image_available:
                continue
            rels_name = f"{part.rsplit('/', 1)[0]}/_rels/{part.rsplit('/', 1)[-1]}.rels"
            rels = _read_xml(zf, rels_name)
            if rels is None:
                continue
            target = None
            for rel in rels:
                if rel.get("Id") == rid:
                    target = rel.get("Target")
                    break
            if not target:
                continue
            # Targets are relative to word/ (e.g. media/image1.png) or already
            # package-absolute (/word/media/...).
            target = target.lstrip("/")
            candidate = target if target.startswith("word/") else f"word/{target}"
            try:
                blob = zf.read(candidate)
                img = _DocxImage.from_blob(blob)
                d["px_width"] = img.px_width
                d["px_height"] = img.px_height
                if d.get("width_emu"):
                    d["dpi"] = img.px_width / (d["width_emu"] / 914400)
            except Exception:
                continue

        # Field balance and commands.
        for f in fields:
            if not f.complete:
                report.errors.append(f"unbalanced field in {f.part}: {f.instr.strip()[:80] or '(no instruction)'}")
            if f.dirty:
                pass
        commands = {}
        for f in fields:
            commands[f.command] = commands.get(f.command, 0) + 1

        toc = [f for f in fields if f.command == "TOC"]
        refs = [f for f in fields if f.command in {"REF", "PAGEREF"}]
        seqs = [f for f in fields if f.command == "SEQ"]
        headings = [p for p in paragraphs if (p["style"] or "").startswith("Heading")]

        # Bookmark names and reference targets.
        for name in bookmarks:
            if not _BOOKMARK_NAME.match(name) and not name.startswith("_Toc"):
                report.errors.append(f"invalid bookmark name: {name!r}")
        for f in refs:
            target = _field_arg(f.instr, 1)
            if target and target not in bookmarks:
                report.errors.append(f"{f.command} target missing: {target}")

        # TOC / heading relationship.
        max_heading = 0
        for p in headings:
            m = re.match(r"Heading(\d+)", p["style"] or "")
            if m:
                max_heading = max(max_heading, int(m.group(1)))
        if headings and not toc:
            report.warnings.append("headings exist but no TOC field was found")
        for t in toc:
            if "\\o" in t.instr and max_heading:
                levels = _toc_levels(t.instr, default=toc_default)
                if levels < max_heading:
                    report.warnings.append(f"TOC covers {levels} levels but headings reach H{max_heading}")

        # Heading sequence.
        last = 0
        for p in paragraphs:
            m = re.match(r"Heading(\d+)", p["style"] or "")
            if not m:
                continue
            level = int(m.group(1))
            if last and level > last + max_jump:
                report.warnings.append(f"heading jumps from H{last} to H{level}: {p['text'][:60]!r}")
            last = level

        # updateFields.
        update = False
        if settings is not None:
            node = settings.find(qn("w:updateFields"))
            update = node is not None and (node.get(qn("w:val")) or "true") in {"true", "1", "on"}
        if fields and not update:
            if any(f.dirty for f in fields):
                report.warnings.append("fields are dirty and w:updateFields is not set; TOC/page numbers may be stale")
            else:
                report.notes.append("fields were refreshed before delivery; w:updateFields is no longer needed")

        # Sections and geometry.
        default_page = (system or {}).get("page", {})
        text_width_twips = None
        for s in sections:
            width = s.get("page_w_twips")
            left = s.get("margin_left_twips")
            right = s.get("margin_right_twips")
            if width and left is not None and right is not None:
                text_width_twips = width - left - right
            if s.get("page_w_twips") and s.get("page_h_twips"):
                mm_w = s["page_w_twips"] / 56.6929
                mm_h = s["page_h_twips"] / 56.6929
                if not ((abs(mm_w - 210) < 2 and abs(mm_h - 297) < 2) or (abs(mm_w - 216) < 2 and abs(mm_h - 279) < 2)):
                    report.notes.append(f"non-A4/Letter page: {mm_w:.0f}×{mm_h:.0f} mm")
            for key, label in [("margin_left_twips", "left"), ("margin_right_twips", "right"),
                               ("margin_top_twips", "top"), ("margin_bottom_twips", "bottom")]:
                value = s.get(key)
                if value is not None and value < (margin_min_mm * 56.6929):
                    report.warnings.append(f"{label} margin below {margin_min_mm:.0f} mm")

        # Tables.
        for i, t in enumerate(tables, start=1):
            grid = t.get("grid_twips") or []
            total = sum(grid)
            if total and text_width_twips and total > text_width_twips + width_tolerance:
                report.warnings.append(f"table {i} grid {total} twips exceeds text width {text_width_twips} twips")
            if (table_header_required and t.get("rows", 0) > 1 and
                    t.get("has_header_look", True) and not t.get("header_repeat")):
                report.warnings.append(f"table {i} has no repeating header row")
            if not t.get("fixed_layout"):
                report.notes.append(f"table {i} is not fixed-layout; columns may drift")

        # Drawings.
        for i, d in enumerate(drawings, start=1):
            if text_width_twips and d.get("width_emu"):
                width_twips = d["width_emu"] / 635
                if width_twips > text_width_twips + 20:
                    report.warnings.append(f"figure {i} is wider than the text column")
            if alt_required and not d.get("descr") and not d.get("decorative"):
                report.warnings.append(f"figure {i} has no alt text")
            if d.get("dpi") is not None and d["dpi"] < dpi_min:
                report.notes.append(f"figure {i} effective DPI is {d['dpi']:.0f} (< {dpi_min:.0f})")

        # Metadata / language.
        if core is not None:
            title = core.findtext("{http://purl.org/dc/elements/1.1/}title")
            if not title:
                report.notes.append("document title metadata is empty")
        lang = None
        for r in document.iter(qn("w:r")):
            rpr = r.find(qn("w:rPr"))
            if rpr is not None:
                l = rpr.find(qn("w:lang"))
                if l is not None:
                    lang = l.get(qn("w:val"))
                    break
        if not lang:
            report.notes.append("no explicit run language (w:lang); proofing/accessibility may guess")

        report.stats = {
            "fields": len(fields),
            "field_commands": commands,
            "bookmarks": len([b for b in bookmarks if not b.startswith("_Toc")]),
            "headings": len(headings),
            "max_heading_level": max_heading,
            "tables": len(tables),
            "figures": len(drawings),
            "sections": len(sections),
            "paragraphs": len(paragraphs),
            "text_width_twips": text_width_twips,
        }
        report.fields = [{"part": f.part, "command": f.command, "instr": f.instr.strip(),
                          "result": f.result.strip()[:120], "complete": f.complete,
                          "dirty": f.dirty} for f in fields]
        report.ok = not report.errors
    return report


def _field_arg(instr: str, index: int) -> str | None:
    """Return the index-th whitespace-separated argument (quotes respected)."""
    try:
        parts = re.findall(r'"[^"]*"|\S+', instr)
        value = parts[index]
        return value.strip('"')
    except (IndexError, AttributeError):
        return None


def _toc_levels(instr: str, default: int = 3) -> int:
    m = re.search(r'\\o\s+"?(\d)-(\d)"?', instr)
    if m:
        return int(m.group(2))
    return default


def _drawing_info(drawing, kind: str, part: str) -> dict:
    extent = drawing.find(qn("wp:extent"))
    docpr = drawing.find(qn("wp:docPr"))
    width = int(extent.get("cx")) if extent is not None and extent.get("cx") else None
    height = int(extent.get("cy")) if extent is not None and extent.get("cy") else None
    descr = docpr.get("descr") if docpr is not None else ""
    title = docpr.get("title") if docpr is not None else ""
    dpi = None
    if width and height:
        # The actual pixel dimensions live on the related image part; the
        # drawing extent alone cannot tell DPI.  document_audit fills this in
        # when it can resolve r:embed.
        dpi = None
    wrap = None
    if kind == "anchor":
        for child in drawing:
            if child.tag.endswith("wrapSquare") or child.tag.endswith("wrapTight") or child.tag.endswith("wrapThrough"):
                wrap = etree.QName(child).localname
                break
            if child.tag.endswith("wrapTopAndBottom"):
                wrap = "wrapTopAndBottom"
                break
            if child.tag.endswith("wrapNone"):
                wrap = "wrapNone"
                break
    blip = drawing.find(f".//{qn('a:blip')}")
    rid = blip.get(qn("r:embed")) if blip is not None else None
    return {"part": part, "kind": kind, "width_emu": width, "height_emu": height,
            "descr": descr, "title": title, "dpi": dpi, "wrap": wrap, "rid": rid}


def _table_info(tbl) -> dict:
    tblpr = tbl.find(qn("w:tblPr"))
    grid = [int(g.get(qn("w:w"))) for g in tbl.findall(f"{qn('w:tblGrid')}/{qn('w:gridCol')}") if g.get(qn("w:w"))]
    fixed = False
    header = False
    caption = ""
    first_row_look = True
    if tblpr is not None:
        layout = tblpr.find(qn("w:tblLayout"))
        fixed = layout is not None and layout.get(qn("w:type")) == "fixed"
        cap = tblpr.find(qn("w:tblCaption"))
        if cap is not None:
            caption = cap.get(qn("w:val")) or ""
        look = tblpr.find(qn("w:tblLook"))
        if look is not None:
            first_row_look = (look.get(qn("w:firstRow")) or "1") in {"1", "true", "on"}
    rows = tbl.findall(qn("w:tr"))
    if rows:
        trpr = rows[0].find(qn("w:trPr"))
        if trpr is not None:
            header = trpr.find(qn("w:tblHeader")) is not None
    return {"rows": len(rows), "cols": len(grid), "grid_twips": grid,
            "fixed_layout": fixed, "header_repeat": header, "caption": caption,
            "has_header_look": first_row_look}


def _section_info(sect) -> dict:
    pg = sect.find(qn("w:pgSz"))
    mar = sect.find(qn("w:pgMar"))
    out = {}
    if pg is not None:
        out["page_w_twips"] = int(pg.get(qn("w:w")) or 0)
        out["page_h_twips"] = int(pg.get(qn("w:h")) or 0)
    if mar is not None:
        for key, attr in [("margin_top_twips", "top"), ("margin_right_twips", "right"),
                          ("margin_bottom_twips", "bottom"), ("margin_left_twips", "left")]:
            out[key] = int(mar.get(qn(f"w:{attr}")) or 0)
    out["header_refs"] = len(sect.findall(qn("w:headerReference")))
    out["footer_refs"] = len(sect.findall(qn("w:footerReference")))
    out["title_page"] = sect.find(qn("w:titlePg")) is not None
    return out


def field_summary(path: str | Path) -> dict:
    fields = read_fields(path)
    counts: dict[str, int] = {}
    for f in fields:
        counts[f.command] = counts.get(f.command, 0) + 1
    return {"count": len(fields), "commands": counts,
            "unbalanced": sum(1 for f in fields if not f.complete),
            "fields": [{"command": f.command, "instr": f.instr.strip(), "result": f.result.strip()[:120]} for f in fields]}


def main() -> None:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Inspect Word fields and bookmarks")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fields")
    p.add_argument("docx", type=Path)
    p = sub.add_parser("audit")
    p.add_argument("docx", type=Path)
    p.add_argument("--md", type=Path)
    args = parser.parse_args()
    if args.cmd == "fields":
        print(json.dumps(field_summary(args.docx), indent=2, ensure_ascii=False))
    else:
        report = audit_docx(args.docx)
        data = report.as_dict()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        if args.md:
            lines = ["# DOCX audit", "", f"**ok:** {report.ok}", ""]
            for label, items in [("Errors", report.errors), ("Warnings", report.warnings), ("Notes", report.notes)]:
                lines.append(f"## {label}")
                lines.extend(f"- {x}" for x in items) if items else lines.append("- none")
                lines.append("")
            args.md.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
