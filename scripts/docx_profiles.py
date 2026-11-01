"""Named standard profiles for DocumentCraft (T052).

A profile is a sourced presentation contract: page geometry, typography,
numbering, caption position, front-matter order, reference position and
limits.  A document spec may override any value; the profile is a default,
not a cage.

The conformance checker reads the produced DOCX and compares it with the
profile.  It never trusts the spec: it measures the file that Word will open.

CLI:
    python scripts/docx_profiles.py list
    python scripts/docx_profiles.py show hust-datn-2017
    python scripts/docx_profiles.py check report.docx --profile hust-datn-2017 --body-pages 34
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-docx is required: pip install python-docx") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES_PATH = ROOT / "domains" / "docx" / "data" / "standard_profiles.json"


# ---------------------------------------------------------------------------
# Loading and merging
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_profiles(path: str | Path | None = None) -> dict:
    path = Path(path) if path else DEFAULT_PROFILES_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("profiles", data)


def get_profile(profile_id: str, path: str | Path | None = None) -> dict:
    profiles = load_profiles(path)
    if profile_id not in profiles:
        raise KeyError(f"unknown profile {profile_id!r}; available: {', '.join(sorted(profiles))}")
    return copy.deepcopy(profiles[profile_id])


def profile_to_spec(profile: dict) -> dict:
    """Map a profile record onto the DocumentCraft spec surface."""
    return {
        "page": profile.get("page", {}),
        "typography": profile.get("typography", {}),
        "paragraph": profile.get("paragraph", {}),
        "numbering": profile.get("numbering", {}),
        "captions": profile.get("captions", {}),
        "cover": profile.get("cover", {}),
        "headers_footers": profile.get("headers_footers", {}),
        "front_matter": {"order": profile.get("front_matter_order", [])},
        "references": profile.get("references", {}),
        "_profile": {
            "id": profile.get("id"),
            "title": profile.get("title"),
            "short": profile.get("short"),
            "source": profile.get("source", {}),
            "limits": profile.get("limits", {}),
            "conformance": profile.get("conformance", {}),
        },
    }


def apply_profile(raw_spec: dict, profile: dict) -> dict:
    """Profile defaults + explicit spec values (spec wins)."""
    return _deep_merge(profile_to_spec(profile), raw_spec)


# ---------------------------------------------------------------------------
# Conformance
# ---------------------------------------------------------------------------

CAPTION_RE = re.compile(r"^(Hình|Bảng)\s+(\d+)(?:\.(\d+))?\.?\s*[—\-.]?\s*(.*)$")
CHAPTER_RE = re.compile(r"^\s*(?:Chương\s+)?(\d+)\s*$")


def _style_font_name(style) -> str | None:
    if style.font.name:
        return style.font.name
    rpr = style.element.find(qn("w:rPr"))
    if rpr is None:
        return None
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        return None
    return rfonts.get(qn("w:ascii")) or rfonts.get(qn("w:hAnsi"))


def _style_size(style):
    return style.font.size.pt if style.font.size is not None else None


def _effective_style_size(style):
    """Walk the basedOn chain; Heading 3/4 often inherit Normal's size."""
    seen = set()
    while style is not None and id(style) not in seen:
        seen.add(id(style))
        size = style.font.size
        if size is not None:
            return size.pt
        style = style.base_style
    return None


def _style_line_spacing(style):
    value = style.paragraph_format.line_spacing
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pstyle(p) -> str:
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        return ""
    node = ppr.find(qn("w:pStyle"))
    return node.get(qn("w:val")) if node is not None else ""


def _text(p) -> str:
    return "".join(node.text or "" for node in p.iter(qn("w:t"))).strip()


def _field_instrs(element) -> list[str]:
    return [(node.text or "").strip() for node in element.iter(qn("w:instrText"))]


def _has_page_field(footer) -> bool:
    return any(instr.upper().startswith("PAGE") for instr in _field_instrs(footer._element))


def _heading_depth(doc) -> int:
    depth = 0
    for p in doc.paragraphs:
        m = re.match(r"Heading (\d+)$", p.style.name or "")
        if m:
            depth = max(depth, int(m.group(1)))
    return depth


def _abstract_words(doc) -> int | None:
    capture = False
    words = 0
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        normalized = text.upper()
        if normalized in {"TÓM TẮT", "ABSTRACT", "TÓM TẮT ĐIỀU HÀNH"}:
            capture = True
            continue
        if capture:
            if p.style.name in {"Heading 1", "Heading 2", "Front Matter Heading", "TOC Heading"}:
                break
            words += len(text.split())
    return words or None


def _heading_num_id(p) -> int | None:
    element = p._p if hasattr(p, "_p") else p
    ppr = element.find(qn("w:pPr"))
    if ppr is None:
        return None
    numpr = ppr.find(qn("w:numPr"))
    if numpr is None:
        return None
    numid = numpr.find(qn("w:numId"))
    if numid is None:
        return None
    try:
        return int(numid.get(qn("w:val")))
    except (TypeError, ValueError):
        return None


def _caption_positions(doc, body_num_id: int | None = None):
    """Check table caption above the table and figure caption below the figure.

    Counts body and appendix separately so a body-caption total is not compared
    with an all-document table/figure total.
    """
    issues: list[str] = []
    counts = {"body_tables": 0, "body_figures": 0,
              "appendix_tables": 0, "appendix_figures": 0}
    in_appendix = False
    body = list(doc.element.body.iterchildren())
    for i, node in enumerate(body):
        if node.tag == qn("w:p") and _pstyle(node) == "Heading1":
            if body_num_id is not None and _heading_num_id(node) not in (None, 0, body_num_id):
                in_appendix = True
            elif _text(node).upper().startswith("PHỤ LỤC"):
                in_appendix = True
        if node.tag == qn("w:tbl"):
            tblpr = node.find(qn("w:tblPr"))
            captioned = tblpr is not None and tblpr.find(qn("w:tblCaption")) is not None
            if not captioned:
                continue
            counts["appendix_tables" if in_appendix else "body_tables"] += 1
            if i == 0 or body[i - 1].tag != qn("w:p") or _pstyle(body[i - 1]) != "Caption":
                issues.append("table caption is not the paragraph immediately above the table")
        elif node.tag == qn("w:p") and node.find(".//" + qn("w:drawing")) is not None:
            if _pstyle(node) == "Caption":
                continue
            counts["appendix_figures" if in_appendix else "body_figures"] += 1
            nxt = body[i + 1] if i + 1 < len(body) else None
            if nxt is None or nxt.tag != qn("w:p") or _pstyle(nxt) != "Caption":
                issues.append("figure caption is not the paragraph immediately below the figure")
    counts["issues"] = issues
    return counts


def _check(id: str, label: str, expected: Any, actual: Any, source: str,
           *, status: str | None = None) -> dict:
    if status is None:
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            ok = abs(float(expected) - float(actual)) <= 0.05
        else:
            ok = expected == actual
        status = "pass" if ok else "fail"
    return {"id": id, "label": label, "expected": expected, "actual": actual,
            "source": source, "status": status}


def _caption_sequence(doc, body_num_id: int | None = None):
    """Yield ``(chapter, caption)`` in body order, stopping at end matter."""
    rows = []
    chapter = 0
    body_started = False
    for node in doc.element.body.iterchildren():
        if node.tag != qn("w:p"):
            continue
        style = _pstyle(node)
        text = _text(node)
        if style in ("Heading1", "ChapterUnnumbered"):
            upper = text.upper()
            if upper.startswith("TÀI LIỆU THAM KHẢO") or upper.startswith("PHỤ LỤC"):
                break
            if (style == "Heading1" and body_num_id is not None
                    and _heading_num_id(node) not in (None, 0, body_num_id)):
                break  # first appendix heading
            if style == "ChapterUnnumbered":
                body_started = True
                continue
            chapter += 1
            body_started = True
        elif style == "Caption" and CAPTION_RE.match(text) and body_started:
            rows.append((chapter, text))
    return rows


def _equation_sequence(doc):
    """Return (chapter, number_tuple_or_None, paragraph) for Equation style."""
    rows = []
    chapter = 0
    for p in doc.paragraphs:
        style = p.style.name or ""
        if style == "Heading 1":
            chapter += 1
        elif style == "Equation":
            text = p.text.strip()
            m = re.search(r"\((\d+)\.(\d+)\)\s*$", text)
            rows.append((chapter, (int(m.group(1)), int(m.group(2))) if m else None, p))
    return rows


def check_docx(docx_path: str | Path, profile: dict, *, body_pages: int | None = None,
               total_pages: int | None = None) -> dict:
    """Measure the DOCX against the profile.  Warnings do not block delivery."""
    path = Path(docx_path)
    doc = Document(str(path))
    checks: list[dict] = []
    limits = profile.get("limits") or {}
    cfg = profile.get("conformance") or {}
    page = profile.get("page") or {}
    typo = profile.get("typography") or {}
    caption_cfg = profile.get("captions") or {}
    numbering = profile.get("numbering") or {}
    source = (profile.get("source") or {}).get("document", "")

    # 1. Page geometry (all sections).
    sections = list(doc.sections)
    widths = [round(s.page_width.mm, 1) for s in sections if s.page_width]
    heights = [round(s.page_height.mm, 1) for s in sections if s.page_height]
    checks.append(_check("page-size", "Khổ giấy A4 (210 × 297 mm)",
                         [210.0, 297.0], [min(widths), min(heights)],
                         source + " §trang", status="pass" if all(
                             abs(w - 210) <= 1 and abs(h - 297) <= 1 for w, h in zip(widths, heights)) else "fail"))
    margins = page.get("margins_mm", {})
    actual_margins = {
        "top": round(sections[-1].top_margin.mm, 1),
        "bottom": round(sections[-1].bottom_margin.mm, 1),
        "left": round(sections[-1].left_margin.mm, 1),
        "right": round(sections[-1].right_margin.mm, 1),
    }
    ok_margins = all(abs(actual_margins[k] - float(v)) <= 0.6 for k, v in margins.items())
    checks.append(_check("margins", "Lề trang (trên/dưới/trái/phải)",
                         {k: float(v) for k, v in margins.items()}, actual_margins,
                         source + " §trình bày", status="pass" if ok_margins else "fail"))

    # 2. Typography.
    normal = doc.styles["Normal"]
    checks.append(_check("body-font", "Phông chữ thân bài", typo.get("body_font"),
                         _style_font_name(normal), source + " §phông chữ"))
    checks.append(_check("body-size", "Cỡ chữ thân bài (pt)", typo.get("body_pt"),
                         _style_size(normal), source + " §cỡ chữ"))
    checks.append(_check("line-spacing", "Giãn dòng", typo.get("line_spacing"),
                         _style_line_spacing(normal), source + " §giãn dòng"))
    space_after = normal.paragraph_format.space_after
    checks.append(_check("space-after", "Khoảng cách sau đoạn (pt)",
                         typo.get("space_after_pt"),
                         round(space_after.pt, 1) if space_after is not None else 0,
                         source + " §đoạn văn"))
    expected_align = (profile.get("paragraph") or {}).get("alignment", "left")
    actual_align = normal.paragraph_format.alignment
    align_ok = (expected_align == "justify" and actual_align == WD_ALIGN_PARAGRAPH.JUSTIFY) or \
               (expected_align == "left" and actual_align in (None, WD_ALIGN_PARAGRAPH.LEFT))
    checks.append(_check("alignment", "Căn đoạn văn", expected_align,
                         str(actual_align), source + " §đoạn văn",
                         status="pass" if align_ok else "fail"))
    heading_sizes = typo.get("heading_sizes_pt") or []
    heading_actual = []
    for level in range(1, min(len(heading_sizes), 4) + 1):
        try:
            style = doc.styles[f"Heading {level}"]
        except KeyError:
            style = None
        heading_actual.append(round(_effective_style_size(style), 1) if style and _effective_style_size(style) else None)
    expected_heading = [float(v) for v in heading_sizes[:len(heading_actual)]]
    checks.append(_check("heading-sizes", "Cỡ chữ Heading 1–3 (pt)", expected_heading,
                         heading_actual, source + " §tiêu đề",
                         status="pass" if heading_actual and all(
                             a is not None and abs(a - e) <= 0.5
                             for a, e in zip(heading_actual, expected_heading)) else "fail"))
    try:
        caption_style = doc.styles["Caption"]
    except KeyError:
        caption_style = None
    checks.append(_check("caption-size", "Cỡ chữ chú thích (pt)", typo.get("caption_pt"),
                         round(_effective_style_size(caption_style), 1) if caption_style and _effective_style_size(caption_style) else None,
                         source + " §chú thích"))
    indent = normal.paragraph_format.first_line_indent
    checks.append(_check("first-line-indent", "Thụt đầu dòng (mm)",
                         (profile.get("paragraph") or {}).get("first_line_indent_mm", 0),
                         round(indent.mm, 1) if indent is not None else 0,
                         source + " §đoạn văn"))
    table_style = doc.styles["Table Text"] if "Table Text" in [s.name for s in doc.styles] else None
    if table_style is not None:
        checks.append(_check("table-size", "Cỡ chữ bảng (pt)", typo.get("table_pt"),
                             _style_size(table_style), source + " §bảng biểu"))

    # 3. Heading structure and numbering.
    depth = _heading_depth(doc)
    required_depth = int(cfg.get("require_heading_depth", 3))
    checks.append(_check("heading-depth", "Độ sâu heading tối thiểu",
                         f">= H{required_depth}", f"H{depth}",
                         "ISO 2145 / cấu trúc mục",
                         status="pass" if depth >= required_depth else "fail"))
    h1 = doc.styles["Heading 1"]
    h1_ppr = h1.element.find(qn("w:pPr"))
    has_num = h1_ppr is not None and h1_ppr.find(qn("w:numPr")) is not None
    checks.append(_check("heading-numbering", "Heading 1 có đánh số tự động",
                         True, has_num, "ISO 2145", status="pass" if has_num else "fail"))
    try:
        unnumbered = doc.styles["Chapter Unnumbered"]
    except KeyError:
        unnumbered = None
    if unnumbered is not None and numbering.get("captions") == "chapter":
        uppr = unnumbered.element.find(qn("w:pPr"))
        unum = uppr.find(qn("w:numPr")) if uppr is not None else None
        uoutline = uppr.find(qn("w:outlineLvl")) if uppr is not None else None
        valid = unum is None and uoutline is not None and (uoutline.get(qn("w:val")) or "") == "0"
        checks.append(_check("chapter-unnumbered", "Mở đầu không đánh số nhưng vẫn vào TOC",
                             "no numPr, outlineLvl 0", "ok" if valid else "invalid",
                             source + " §cấu trúc chương",
                             status="pass" if valid else "fail"))

    # 4. Captions.
    body_num_id = None
    try:
        body_num_id = _heading_num_id(doc.styles["Heading 1"].element)
    except KeyError:
        body_num_id = None
    if body_num_id in (None, 0):
        for p in doc.paragraphs:
            if p.style.name == "Heading 1":
                nid = _heading_num_id(p)
                if nid not in (None, 0):
                    body_num_id = nid
                    break
    captions = _caption_sequence(doc, body_num_id)
    chapter_mode = numbering.get("captions") == "chapter"
    if chapter_mode:
        counters = {"Hình": 0, "Bảng": 0}
        caption_errors: list[str] = []
        last_chapter = 0
        for chapter, text in captions:
            m = CAPTION_RE.match(text)
            if not m:
                caption_errors.append(f"caption not parseable: {text[:60]}")
                continue
            label = m.group(1)
            if chapter != last_chapter:
                counters = {"Hình": 0, "Bảng": 0}
                last_chapter = chapter
            if int(m.group(2)) != chapter:
                caption_errors.append(f"caption {text[:30]} uses chapter {m.group(2)}, expected {chapter}")
            counters[label] += 1
            local = m.group(3)
            if local is None or int(local) != counters[label]:
                caption_errors.append(
                    f"caption {text[:30]} local {local}, expected {counters[label]}")
        checks.append(_check("caption-numbering", "Hình/bảng đánh số theo chương",
                             "chapter.local, reset mỗi chương",
                             f"{len(captions)} caption; {len(caption_errors)} lỗi",
                             source + " §hình/bảng",
                             status="pass" if captions and not caption_errors else "fail"))
        if caption_errors:
            checks[-1]["details"] = caption_errors[:8]
    else:
        checks.append(_check("caption-numbering", "Hình/bảng đánh số liên tục",
                             "sequential", f"{len(captions)} caption",
                             source, status="pass" if captions else "warn"))

    pos = _caption_positions(doc, body_num_id)
    position_issues = pos["issues"]
    counts_text = (f"body {pos['body_tables']} bảng + {pos['body_figures']} hình; "
                   f"appendix {pos['appendix_tables']} bảng + {pos['appendix_figures']} hình; "
                   f"{len(position_issues)} lỗi")
    checks.append(_check("caption-position", "Vị trí chú thích bảng/hình",
                         "bảng trên, hình dưới", counts_text,
                         source + " §bảng/hình",
                         status="pass" if (pos["body_tables"] or pos["body_figures"]
                                           or pos["appendix_tables"] or pos["appendix_figures"])
                         and not position_issues else "fail"))
    if position_issues:
        checks[-1]["details"] = position_issues[:8]

    # 5. Page number in the body footer.
    body_section = sections[-1]
    footer_ok = _has_page_field(body_section.footer)
    footer_align = body_section.footer.paragraphs[0].alignment if body_section.footer.paragraphs else None
    center = footer_align == WD_ALIGN_PARAGRAPH.CENTER
    checks.append(_check("page-number", "Số trang ở chân trang",
                         "PAGE field, căn giữa" if (profile.get("headers_footers") or {}).get("page_number_align") == "center" else "PAGE field",
                         f"field={footer_ok}, align={footer_align}",
                         source + " §số trang",
                         status="pass" if footer_ok and center else "fail"))

    # 6. Front matter order.
    wanted = profile.get("front_matter_order") or []
    title_map = {
        "task": "NHIỆM VỤ",
        "declaration": "LỜI CAM ĐOAN",
        "acknowledgements": "LỜI CẢM ƠN",
        "abstract": "TÓM TẮT",
        "preface": "LỜI NÓI ĐẦU",
        "toc": "MỤC LỤC",
        "abbreviations": "DANH MỤC KÝ HIỆU",
        "list_of_tables": "DANH MỤC BẢNG",
        "list_of_figures": "DANH MỤC HÌNH",
    }
    positions = {}
    for i, p in enumerate(doc.paragraphs):
        if p.style.name in {"Heading 1", "Chapter Unnumbered"}:
            break  # front matter ends at the first body chapter
        upper = p.text.strip().upper()
        for key, title in title_map.items():
            if key not in positions and upper.startswith(title):
                positions[key] = i
    order_issues = []
    last = -1
    has_figures = any(p._p.find(".//" + qn("w:drawing")) is not None for p in doc.paragraphs)
    has_tables = bool(doc.tables)
    for key in wanted:
        if key not in title_map:
            order_issues.append(f"profile has unknown front-matter key {key!r}")
            continue
        if key == "list_of_figures" and not has_figures:
            continue
        if key == "list_of_tables" and not has_tables:
            continue
        if key not in positions:
            order_issues.append(f"thiếu {title_map[key]}")
            continue
        if positions[key] < last:
            order_issues.append(f"{title_map[key]} sai thứ tự")
        last = positions[key]
    actual_order = [title_map[k] for k in wanted if k in positions]
    checks.append(_check("front-matter-order", "Thứ tự front matter",
                         " → ".join(title_map.get(k, k) for k in wanted),
                         " → ".join(actual_order) or "không tìm thấy",
                         source + " §bố cục",
                         status="pass" if not order_issues else "fail"))
    if order_issues:
        checks[-1]["details"] = order_issues

    # 7. References and citations.
    ref_paras = []
    capture = False
    for p in doc.paragraphs:
        text = p.text.strip()
        style_name = (p.style.name or "").lower()
        if (text.upper().startswith("TÀI LIỆU THAM KHẢO")
                and not style_name.startswith("toc")):
            capture = True
            continue
        if capture and text.upper().startswith("PHỤ LỤC") and not style_name.startswith("toc"):
            break
        if capture and re.match(r"^\[\d+\]", text):
            ref_paras.append(text)
    checks.append(_check("references-count", "Số tài liệu tham khảo tối thiểu",
                         8, len(ref_paras), "ISO 690 / quy định khoa",
                         status="pass" if len(ref_paras) >= 8 else "fail"))
    # Reference position relative to the first appendix.
    ref_index = app_index = None
    for i, p in enumerate(doc.paragraphs):
        style_name = (p.style.name or "").lower()
        if style_name.startswith("toc"):
            continue
        text = p.text.strip().upper()
        if ref_index is None and text.startswith("TÀI LIỆU THAM KHẢO"):
            ref_index = i
        if (app_index is None and p.style.name == "Heading 1"
                and body_num_id is not None
                and _heading_num_id(p) not in (None, 0, body_num_id)):
            app_index = i
    expected_position = (profile.get("references") or {}).get("position", "after_appendix")
    if ref_index is not None and app_index is not None:
        actual_position = "before_appendix" if ref_index < app_index else "after_appendix"
        checks.append(_check("references-position", "Vị trí tài liệu tham khảo",
                             expected_position, actual_position,
                             source + " §tài liệu tham khảo",
                             status="pass" if actual_position == expected_position else "fail"))
    else:
        checks.append(_check("references-position", "Vị trí tài liệu tham khảo",
                             expected_position,
                             f"refs={ref_index is not None}, appendix={app_index is not None}",
                             source + " §tài liệu tham khảo", status="warn"))
    citation_refs = [i for i in _field_instrs(doc.element.body) if i.upper().startswith("REF REF-")]
    checks.append(_check("citation-links", "Trích dẫn động tới tài liệu",
                         ">= 8 REF ref-*", len(citation_refs), "ISO 690",
                         status="pass" if len(citation_refs) >= 8 else "warn"))

    # 8. Abstract length, when the profile specifies it.
    limits_abs = limits.get("abstract_words")
    if limits_abs:
        words = _abstract_words(doc)
        low, high = (limits_abs if isinstance(limits_abs, list) else [limits_abs, limits_abs])
        status = "pass" if words is not None and low <= words <= high else "warn"
        checks.append(_check("abstract-words", "Độ dài tóm tắt (từ)",
                             f"{low}–{high}", words, source + " §tóm tắt", status=status))

    # 9. Body page count.  The build passes Word's count; a standalone
    # `docx_profiles.py check` must pass --body-pages or it is reported as a
    # warning, never silently skipped.
    low, high = limits.get("body_pages_min"), limits.get("body_pages_max")

    def page_range() -> str:
        if low is None and high is not None:
            return f"≤ {high}"
        if low is not None and high is None:
            return f"≥ {low}"
        return f"{low}–{high}"

    if body_pages is None:
        checks.append(_check("body-pages", "Số trang phần thân",
                             page_range(), "not measured",
                             source + " §số trang", status="warn"))
    else:
        status = "pass"
        if low is not None and body_pages < low:
            status = "fail"
        if high is not None and body_pages > high:
            status = "fail"
        checks.append(_check("body-pages", "Số trang phần thân",
                             page_range(), body_pages,
                             source + " §số trang", status=status))
        checks[-1]["details"] = [
            "measured from the body start to the first end-matter heading; "
            "includes tables and figures, so a rule that excludes them is stricter"
        ]

    # 10. Equations (chapter numbering, when declared).
    eq_rows = _equation_sequence(doc)
    eq_issues: list[str] = []
    counters: dict[int, int] = {}
    chapter_mode_eq = numbering.get("equations") == "chapter"
    for chapter, nums, p in eq_rows:
        instrs = _field_instrs(p._p)
        has_seq = any(i.upper().startswith("SEQ EQUATION") for i in instrs)
        has_chapter = any(i.upper().startswith("STYLEREF") and "HEADING 1" in i.upper()
                          and "\\S" in i.upper() for i in instrs)
        if not has_seq:
            eq_issues.append("equation has no SEQ Equation field")
        if chapter_mode_eq:
            if chapter == 0:
                eq_issues.append("equation appears before the first numbered chapter")
                continue
            if not has_chapter:
                eq_issues.append("equation has no STYLEREF \"Heading 1\" \\s field")
            if nums is None:
                eq_issues.append("equation has no visible (chapter.local) number")
                continue
            if nums[0] != chapter:
                eq_issues.append(f"equation chapter {nums[0]} != {chapter}")
            counters[chapter] = counters.get(chapter, 0) + 1
            if nums[1] != counters[chapter]:
                eq_issues.append(
                    f"equation local {nums[1]} != {counters[chapter]} in chapter {chapter}")
    status = "pass"
    if not eq_rows:
        status = "warn"
    elif eq_issues:
        status = "fail"
    checks.append(_check("equation-numbering", "Phương trình có số hiệu",
                         "chapter.local, reset mỗi chương" if chapter_mode_eq else "sequential",
                         f"{len(eq_rows)} equations; {len(eq_issues)} lỗi",
                         source + " §công thức", status=status))
    if eq_issues:
        checks[-1]["details"] = eq_issues[:8]

    summary = {"pass": sum(c["status"] == "pass" for c in checks),
               "warn": sum(c["status"] == "warn" for c in checks),
               "fail": sum(c["status"] == "fail" for c in checks)}
    return {
        "ok": summary["fail"] == 0,
        "profile": {"id": profile.get("id"), "title": profile.get("title"),
                    "source": profile.get("source", {})},
        "summary": summary,
        "checks": checks,
        "stats": {
            "sections": len(sections),
            "paragraphs": len(doc.paragraphs),
            "captions": len(captions),
            "tables": len(doc.tables),
            "figures": sum(1 for p in doc.paragraphs if p._p.find(".//" + qn("w:drawing")) is not None),
            "headings": sum(1 for p in doc.paragraphs if (p.style.name or "").startswith("Heading ")),
            "max_heading_level": depth,
            "references": len(ref_paras),
            "citation_fields": len(citation_refs),
            "body_pages": body_pages,
            "total_pages": total_pages,
        },
    }


def to_markdown(report: dict) -> str:
    profile = report["profile"]
    lines = [f"# Conformance — {profile['title']}", "",
             f"- **Profile:** `{profile['id']}`",
             f"- **Source:** {profile.get('source', {}).get('document', '')}",
             f"- **URL:** {profile.get('source', {}).get('url', '')}",
             f"- **Accessed:** {profile.get('source', {}).get('accessed', '')}",
             f"- **Result:** {'PASS' if report['ok'] else 'FAIL'} "
             f"({report['summary']['pass']} pass, {report['summary']['warn']} warn, "
             f"{report['summary']['fail']} fail)", ""]
    lines.append("| # | Kiểm soát | Kỳ vọng | Thực tế | Trạng thái |")
    lines.append("|---|---|---|---|---|")
    for i, check in enumerate(report["checks"], start=1):
        lines.append(f"| {i} | {check['label']} | {check['expected']} | {check['actual']} | "
                     f"`{check['status']}` |")
    lines.append("")
    lines.append("> `warn` is a disclosed limitation or a range outside the regulation; "
                 "`fail` is a measured mismatch that must be fixed before delivery.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list", help="List named profiles")
    p.add_argument("--profiles", type=Path, default=None)
    p = sub.add_parser("show", help="Show one profile as JSON")
    p.add_argument("profile")
    p.add_argument("--profiles", type=Path, default=None)
    p = sub.add_parser("check", help="Check a DOCX against a profile")
    p.add_argument("docx", type=Path)
    p.add_argument("--profile", required=True)
    p.add_argument("--profiles", type=Path, default=None)
    p.add_argument("--body-pages", type=int, default=None)
    p.add_argument("--total-pages", type=int, default=None)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--md", type=Path, default=None)
    args = parser.parse_args()
    if args.cmd == "list":
        for key, profile in load_profiles(args.profiles).items():
            print(f"{key:22s} {profile.get('title')}")
        return
    if args.cmd == "show":
        print(json.dumps(get_profile(args.profile, args.profiles), ensure_ascii=False, indent=2))
        return
    report = check_docx(args.docx, get_profile(args.profile, args.profiles),
                        body_pages=args.body_pages, total_pages=args.total_pages)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.write_text(text, encoding="utf-8")
    if args.md:
        args.md.write_text(to_markdown(report), encoding="utf-8")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
