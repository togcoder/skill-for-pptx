#!/usr/bin/env python3
"""Patch Excel chart OOXML directly (T041, xlsx).

Status: EXPERIMENTAL — T041 [xlsx], review requested.  Not a canonical module
until an independent review accepts it.


xlsxwriter/openpyxl cover the common chart API, but some properties are either
not exposed or are silently lost when a workbook is re-saved.  This module edits
``xl/charts/chartN.xml`` and the drawing anchor in place, preserving every other
part of the package.

Supported patches (all optional):
  title, legend, axes.{x,y,y2}, bar.{gap,overlap}, doughnut_hole, pie_rotation,
  data_labels, series[i], plot_layout, rounded_corners, plot_vis_only,
  disp_blanks, anchor.{mode,width_cm,height_cm,cell}

The XML child order follows ECMA-376 / ISO/IEC 29500-1 §21.2.  Excel is strict
about element order in several chart groups, so every insert goes through
``_ensure`` with an explicit order list.

CLI:
    python scripts/chart_patch.py inspect book.xlsx
    python scripts/chart_patch.py apply book.xlsx patch.json -o fixed.xlsx
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile
from typing import Any
from lxml import etree

C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
XDR_NS = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

CHART_TYPES = {
    "barChart", "bar3DChart", "lineChart", "line3DChart", "areaChart", "area3DChart",
    "pieChart", "pie3DChart", "doughnutChart", "scatterChart", "bubbleChart",
    "radarChart", "stockChart", "surfaceChart", "surface3DChart", "ofPieChart",
    "treemapChart", "sunburstChart", "histogramChart", "waterfallChart",
    "funnelChart", "boxWhiskerChart",
}

ORDER = {
    "chartSpace": ["date1904", "lang", "roundedCorners", "style", "clrMapOvr", "pivotSource",
                   "protection", "chart", "spPr", "txPr", "externalData", "printSettings",
                   "userShapes", "extLst"],
    "chart": ["title", "autoTitleDeleted", "pivotFmts", "view3D", "floor", "sideWall",
              "backWall", "plotArea", "legend", "plotVisOnly", "dispBlanksAs",
              "showDLblsOverMax", "extLst"],
    "plotArea": ["layout", "barChart", "bar3DChart", "lineChart", "line3DChart", "areaChart",
                 "area3DChart", "pieChart", "pie3DChart", "doughnutChart", "scatterChart",
                 "bubbleChart", "radarChart", "stockChart", "surfaceChart", "surface3DChart",
                 "ofPieChart", "treemapChart", "sunburstChart", "histogramChart",
                 "waterfallChart", "funnelChart", "boxWhiskerChart", "dTable", "spPr", "extLst"],
    "barChart": ["barDir", "grouping", "varyColors", "ser", "dLbls", "gapWidth", "overlap",
                 "serLines", "axId"],
    "lineChart": ["grouping", "varyColors", "ser", "dLbls", "dropLines", "hiLowLines",
                  "upDownBars", "marker", "smooth", "axId"],
    "scatterChart": ["scatterStyle", "varyColors", "ser", "dLbls", "axId"],
    "pieChart": ["varyColors", "ser", "dLbls", "firstSliceAng"],
    "doughnutChart": ["varyColors", "ser", "dLbls", "firstSliceAng", "holeSize"],
    "ser": ["idx", "order", "tx", "spPr", "invertIfNegative", "pictureOptions", "marker",
            "explosion", "dPt", "dLbls", "trendline", "errBars", "cat", "val", "xVal",
            "yVal", "bubbleSize", "bubble3D", "smooth", "shape", "extLst"],
    "dLbls": ["dLbl", "delete", "numFmt", "spPr", "txPr", "dLblPos", "showLegendKey",
              "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize",
              "separator", "showLeaderLines", "leaderLines", "extLst"],
    "scaling": ["logBase", "orientation", "max", "min", "extLst"],
    "valAx": ["axId", "scaling", "delete", "axPos", "majorGridlines", "minorGridlines",
              "title", "numFmt", "majorTickMark", "minorTickMark", "tickLblPos", "spPr",
              "txPr", "crossAx", "crosses", "crossesAt", "crossBetween", "majorUnit",
              "minorUnit", "dispUnits", "extLst"],
    "catAx": ["axId", "scaling", "delete", "axPos", "majorGridlines", "minorGridlines",
              "title", "numFmt", "majorTickMark", "minorTickMark", "tickLblPos", "spPr",
              "txPr", "crossAx", "crosses", "crossesAt", "auto", "lblAlgn", "lblOffset",
              "tickLblSkip", "tickMarkSkip", "noMultiLvlLbl", "extLst"],
    "dateAx": ["axId", "scaling", "delete", "axPos", "majorGridlines", "minorGridlines",
               "title", "numFmt", "majorTickMark", "minorTickMark", "tickLblPos", "spPr",
               "txPr", "crossAx", "crosses", "crossesAt", "auto", "lblOffset",
               "baseTimeUnit", "majorUnit", "majorTimeUnit", "minorUnit", "minorTimeUnit",
               "extLst"],
    "legend": ["legendPos", "legendEntry", "layout", "overlay", "spPr", "txPr", "extLst"],
    "title": ["tx", "layout", "overlay", "spPr", "txPr", "extLst"],
    "layout": ["manualLayout", "extLst"],
    "manualLayout": ["layoutTarget", "xMode", "yMode", "wMode", "hMode", "x", "y", "w", "h", "extLst"],
}

CM_TO_EMU = 360000
EMU_TO_CM = 1 / CM_TO_EMU
POSITION_MAP = {"bottom": "b", "top": "t", "left": "l", "right": "r", "top_right": "tr"}
LABEL_POS_MAP = {
    "center": "ctr", "inside_end": "inEnd", "outside_end": "outEnd",
    "inside_base": "inBase", "best_fit": "bestFit", "left": "l", "right": "r",
    "top": "t", "bottom": "b", "above": "t", "below": "b",
}
MARKER_MAP = {
    "circle": "circle", "square": "square", "diamond": "diamond", "triangle": "triangle",
    "x": "x", "star": "star", "dot": "dot", "dash": "dash", "none": "none",
    "auto": "auto",
}


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def c(tag: str) -> str:
    return f"{{{C_NS}}}{tag}"


def a(tag: str) -> str:
    return f"{{{A_NS}}}{tag}"


def xdr(tag: str) -> str:
    return f"{{{XDR_NS}}}{tag}"


def _local(el) -> str:
    return etree.QName(el).localname


def _ensure(parent, tag: str, order_key: str | None = None, *, index: int | None = None):
    existing = parent.find(c(tag))
    if existing is not None:
        return existing
    node = etree.Element(c(tag))
    order = ORDER.get(order_key or _local(parent), [])
    if tag in order:
        later = set(order[order.index(tag) + 1:])
        for child in list(parent):
            if _local(child) in later:
                child.addprevious(node)
                return node
    if index is not None:
        parent.insert(index, node)
    else:
        parent.append(node)
    return node


def _set_val(parent, tag: str, value: Any, order_key: str | None = None, *, attr: str = "val"):
    node = _ensure(parent, tag, order_key)
    node.set(attr, str(value))
    return node


def _remove(parent, tag: str):
    node = parent.find(c(tag))
    if node is not None:
        parent.remove(node)


def _solid_fill(parent, color: str):
    for old in parent.findall(a("solidFill")):
        parent.remove(old)
    fill = etree.Element(a("solidFill"))
    clr = etree.SubElement(fill, a("srgbClr"))
    clr.set("val", color.replace("#", "").upper())
    # In a:ln, the fill must precede prstDash/join/end-cap children.  Appending
    # after an existing dash makes Excel ignore the colour or offer a repair.
    if parent.tag == a("ln"):
        later = {"prstDash", "round", "bevel", "miter", "headEnd", "tailEnd", "extLst"}
        for child in list(parent):
            if _local(child) in later:
                child.addprevious(fill)
                return fill
    parent.append(fill)
    return fill


def _line(parent, color: str | None = None, width_pt: float | None = None):
    ln = parent.find(a("ln"))
    if ln is None:
        ln = etree.SubElement(parent, a("ln"))
    if width_pt is not None:
        ln.set("w", str(int(round(width_pt * 12700))))
    if color:
        _solid_fill(ln, color)
    return ln


def _text_body(parent, text: str, *, size: float | None = None, bold: bool | None = None,
               color: str | None = None):
    """Replace parent's c:tx with rich text."""
    _remove(parent, "tx")
    tx = etree.Element(c("tx"))
    rich = etree.SubElement(tx, c("rich"))
    etree.SubElement(rich, a("bodyPr"))
    etree.SubElement(rich, a("lstStyle"))
    p = etree.SubElement(rich, a("p"))
    r = etree.SubElement(p, a("r"))
    rpr = etree.SubElement(r, a("rPr"))
    rpr.set("lang", "en-US")
    if size:
        rpr.set("sz", str(int(round(size * 100))))
    if bold:
        rpr.set("b", "1")
    if color:
        _solid_fill(rpr, color)
    t = etree.SubElement(r, a("t"))
    t.text = text
    parent.insert(0, tx) if parent.tag == c("title") else parent.append(tx)
    return tx


def _set_title(parent, value, *, default_size: float = 14, color: str = "1A1A1A"):
    _remove(parent, "title")
    if value in (None, False):
        return
    if isinstance(value, str):
        value = {"text": value}
    node = etree.Element(c("title"))
    _text_body(node, value.get("text", ""), size=float(value.get("size", default_size)),
               bold=value.get("bold", True), color=value.get("color", color))
    overlay = etree.SubElement(node, c("overlay"))
    overlay.set("val", "0")
    _insert_ordered(parent, node, "title")


def _insert_ordered(parent, node, tag: str):
    order = ORDER.get(_local(parent), [])
    if tag in order:
        later = set(order[order.index(tag) + 1:])
        for child in list(parent):
            if _local(child) in later:
                child.addprevious(node)
                return
    parent.append(node)


def _set_txpr(parent, *, size: float | None = None, color: str | None = None,
              rotation_deg: float | None = None, bold: bool | None = None,
              order_key: str):
    _remove(parent, "txPr")
    txpr = etree.Element(c("txPr"))
    body = etree.SubElement(txpr, a("bodyPr"))
    if rotation_deg is not None:
        body.set("rot", str(int(round(rotation_deg * 60000))))
    etree.SubElement(txpr, a("lstStyle"))
    p = etree.SubElement(txpr, a("p"))
    ppr = etree.SubElement(p, a("pPr"))
    rpr = etree.SubElement(ppr, a("defRPr"))
    if size:
        rpr.set("sz", str(int(round(size * 100))))
    if bold:
        rpr.set("b", "1")
    if color:
        _solid_fill(rpr, color)
    etree.SubElement(p, a("endParaRPr")).set("lang", "en-US")
    _insert_ordered(parent, txpr, "txPr")


def _set_numfmt(parent, code: str, *, order_key: str):
    _remove(parent, "numFmt")
    node = etree.Element(c("numFmt"))
    node.set("formatCode", code)
    node.set("sourceLinked", "0")
    _insert_ordered(parent, node, "numFmt")


def _set_scaling(axis, *, minimum=None, maximum=None, log_base=None, reverse=False):
    scaling = _ensure(axis, "scaling", "valAx")
    for child in list(scaling):
        if _local(child) in {"min", "max", "logBase", "orientation"}:
            scaling.remove(child)
    if log_base is not None:
        node = etree.Element(c("logBase")); node.set("val", str(log_base)); scaling.append(node)
    if reverse:
        node = etree.Element(c("orientation")); node.set("val", "maxMin"); scaling.append(node)
    if maximum is not None:
        node = etree.Element(c("max")); node.set("val", str(maximum)); scaling.append(node)
    if minimum is not None:
        node = etree.Element(c("min")); node.set("val", str(minimum)); scaling.append(node)


def _set_axis(axis, options: dict):
    if not options:
        return
    if "title" in options:
        _set_title_value(axis, options["title"])
    if "min" in options or "max" in options or "log_base" in options or options.get("reverse"):
        _set_scaling(axis, minimum=options.get("min"), maximum=options.get("max"),
                     log_base=options.get("log_base"), reverse=bool(options.get("reverse")))
    if options.get("number_format"):
        _set_numfmt(axis, options["number_format"], order_key=_local(axis))
    if options.get("major_unit") is not None:
        _set_val(axis, "majorUnit", str(options["major_unit"]), _local(axis))
    if "visible" in options:
        _set_val(axis, "delete", "0" if options["visible"] else "1", _local(axis))
    if options.get("gridlines") is not None:
        _remove(axis, "majorGridlines")
        if options["gridlines"]:
            grid = _ensure(axis, "majorGridlines", _local(axis))
            sp = etree.SubElement(grid, c("spPr"))
            _line(sp, options.get("gridline_color", "D9D9D9"), options.get("gridline_width", 0.5))
    if options.get("label_rotation") is not None or options.get("label_size") or options.get("label_color"):
        _set_txpr(axis, size=options.get("label_size"), color=options.get("label_color"),
                  rotation_deg=options.get("label_rotation"), order_key=_local(axis))
    if options.get("tick_label_position"):
        _set_val(axis, "tickLblPos", options["tick_label_position"], _local(axis))


def _set_title_value(parent, value):
    if isinstance(value, str):
        value = {"text": value}
    _remove(parent, "title")
    node = etree.Element(c("title"))
    _text_body(node, value.get("text", ""), size=float(value.get("size", 10)),
               bold=value.get("bold", False), color=value.get("color", "404040"))
    _insert_ordered(parent, node, "title")


def _set_legend(chart, value):
    _remove(chart, "legend")
    if value in (None, False) or value.get("none"):
        return
    if isinstance(value, str):
        value = {"position": value}
    node = etree.Element(c("legend"))
    pos = etree.SubElement(node, c("legendPos"))
    pos.set("val", POSITION_MAP.get(value.get("position", "bottom"), "b"))
    if value.get("overlay"):
        overlay = etree.SubElement(node, c("overlay")); overlay.set("val", "1")
    if value.get("size") or value.get("color"):
        txpr = etree.Element(c("txPr"))
        body = etree.SubElement(txpr, a("bodyPr")); etree.SubElement(txpr, a("lstStyle"))
        p = etree.SubElement(txpr, a("p")); ppr = etree.SubElement(p, a("pPr"))
        rpr = etree.SubElement(ppr, a("defRPr"))
        if value.get("size"): rpr.set("sz", str(int(value["size"] * 100)))
        if value.get("color"): _solid_fill(rpr, value["color"])
        etree.SubElement(p, a("endParaRPr")).set("lang", "en-US")
        node.append(txpr)
    _insert_ordered(chart, node, "legend")


def _set_dlbls(parent, value, *, order_key: str):
    _remove(parent, "dLbls")
    if value in (None, False) or value.get("none"):
        return
    if isinstance(value, str):
        value = {"show": True}
    node = etree.Element(c("dLbls"))
    if value.get("number_format"):
        nf = etree.SubElement(node, c("numFmt"))
        nf.set("formatCode", value["number_format"]); nf.set("sourceLinked", "0")
    if value.get("position"):
        pos = etree.SubElement(node, c("dLblPos"))
        pos.set("val", LABEL_POS_MAP.get(value["position"], value["position"]))
    for key, tag in [("show_legend_key", "showLegendKey"), ("show_value", "showVal"),
                     ("show_category", "showCatName"), ("show_series", "showSerName"),
                     ("show_percent", "showPercent"), ("show_bubble_size", "showBubbleSize"),
                     ("show_leader_lines", "showLeaderLines")]:
        show = value.get(key)
        if show is None and key == "show_value":
            show = value.get("show", True)
        if show is not None:
            el = etree.SubElement(node, c(tag)); el.set("val", "1" if show else "0")
    if value.get("separator"):
        sep = etree.SubElement(node, c("separator")); sep.text = value["separator"]
    if value.get("size") or value.get("color") or value.get("bold"):
        txpr = etree.Element(c("txPr"))
        body = etree.SubElement(txpr, a("bodyPr")); etree.SubElement(txpr, a("lstStyle"))
        p = etree.SubElement(txpr, a("p")); ppr = etree.SubElement(p, a("pPr"))
        rpr = etree.SubElement(ppr, a("defRPr"))
        if value.get("size"): rpr.set("sz", str(int(value["size"] * 100)))
        if value.get("bold"): rpr.set("b", "1")
        if value.get("color"): _solid_fill(rpr, value["color"])
        etree.SubElement(p, a("endParaRPr")).set("lang", "en-US")
        _insert_ordered(node, txpr, "txPr")
    _insert_ordered(parent, node, "dLbls")


def _hide_series(series):
    """Make a series fully transparent (used for the Gantt start offset)."""
    sp = series.find(c("spPr"))
    if sp is None:
        sp = etree.Element(c("spPr"))
        _insert_ordered(series, sp, "spPr")
    for child in list(sp):
        if _local(child) in {"solidFill", "noFill", "ln", "gradFill", "pattFill"}:
            sp.remove(child)
    etree.SubElement(sp, a("noFill"))
    ln = etree.SubElement(sp, a("ln"))
    etree.SubElement(ln, a("noFill"))


def _set_series_style(series, options: dict, *, chart_type: str = ""):
    if not options:
        return
    sp = series.find(c("spPr"))
    if sp is None:
        sp = etree.Element(c("spPr"))
        _insert_ordered(series, sp, "spPr")
    # Rebuild fill/line in schema order instead of appending after an existing
    # a:ln (which Excel rejects or silently ignores).
    for child in list(sp):
        if _local(child) in {"solidFill", "noFill", "ln"}:
            sp.remove(child)
    line_type = chart_type in {"lineChart", "line3DChart", "scatterChart", "radarChart"}
    fill_color = options.get("color")
    line_color = options.get("line_color") or (fill_color if line_type else None)
    if fill_color and not line_type:
        _solid_fill(sp, fill_color)
    if line_color or options.get("line_width"):
        _line(sp, line_color, options.get("line_width"))
    if options.get("marker") or options.get("marker_size") or options.get("marker_color"):
        marker = series.find(c("marker"))
        if marker is None:
            marker = etree.Element(c("marker"))
            _insert_ordered(series, marker, "marker")
        symbol = marker.find(c("symbol"))
        if symbol is None:
            symbol = etree.SubElement(marker, c("symbol"))
        symbol.set("val", MARKER_MAP.get(options.get("marker", "auto"), "auto"))
        if options.get("marker_size"):
            size = marker.find(c("size"))
            if size is None:
                size = etree.SubElement(marker, c("size"))
            size.set("val", str(int(options["marker_size"])))
        if options.get("marker_color"):
            msp = marker.find(c("spPr"))
            if msp is None:
                msp = etree.SubElement(marker, c("spPr"))
            _solid_fill(msp, options["marker_color"])
    if options.get("data_labels") is not None:
        _set_dlbls(series, options["data_labels"], order_key="ser")
    if options.get("trendline_label_layout"):
        trend = series.find(c("trendline"))
        if trend is not None:
            lbl = trend.find(c("trendlineLbl"))
            if lbl is None:
                lbl = etree.SubElement(trend, c("trendlineLbl"))
            layout = lbl.find(c("layout"))
            if layout is None:
                layout = etree.Element(c("layout"))
                lbl.insert(0, layout)
            _remove(layout, "manualLayout")
            manual = etree.SubElement(layout, c("manualLayout"))
            box = options["trendline_label_layout"]
            for key in ("x", "y", "w", "h"):
                if box.get(key) is not None:
                    etree.SubElement(manual, c(f"{key}Mode")).set("val", "edge")
            for key in ("x", "y", "w", "h"):
                if box.get(key) is not None:
                    etree.SubElement(manual, c(key)).set("val", str(box[key]))


def _chart_groups(plot):
    return [child for child in plot if _local(child) in CHART_TYPES] if plot is not None else []


def _find_chart_group(plot):
    groups = _chart_groups(plot)
    return groups[0] if groups else None


def _find_axis(root, kind: str, position: str | None = None):
    tag = {"x": "catAx", "y": "valAx", "date": "dateAx"}[kind]
    for axis in root.iter(c(tag)):
        pos = axis.find(c("axPos"))
        value = (pos.get("val") if pos is not None else "") or ""
        if position is None or value == position:
            return axis
    return None


def chart_info(root) -> dict:
    plot = root.find(f".//{c('plotArea')}")
    groups = _chart_groups(plot)
    primary = groups[0] if groups else None
    title = ""
    if root.find(f".//{c('title')}") is not None:
        title = "".join(t.text or "" for t in root.find(f".//{c('title')}").iter(a("t")))
    series = []
    for group in groups:
        ax_ids = [ax.get("val") for ax in group.findall(c("axId")) if ax.get("val") is not None]
        for ser in group.findall(c("ser")):
            name = ""
            tx = ser.find(c("tx"))
            if tx is not None:
                name = "".join(t.text or "" for t in tx.iter(a("t"))) or "".join(
                    v.text or "" for v in tx.iter(c("v")))
            ref = ""
            val = ser.find(c("val"))
            if val is None:
                val = ser.find(c("yVal"))
            if val is not None:
                numref = val.find(c("numRef"))
                if numref is not None and numref.find(c("f")) is not None:
                    ref = numref.find(c("f")).text or ""
            series.append({"name": name, "values_ref": ref,
                           "group": _local(group), "ax_ids": ax_ids})
    return {
        "type": _local(primary) if len(groups) == 1 else ("combo:" + "+".join(_local(g) for g in groups) if groups else None),
        "types": [_local(g) for g in groups],
        "title": title,
        "series": series,
        "axes": [_local(ax) for ax in root.iter() if _local(ax) in {"catAx", "valAx", "dateAx", "serAx"}],
        "has_legend": root.find(f".//{c('legend')}") is not None,
    }


def list_charts(path: str | Path) -> list[dict]:
    path = Path(path)
    out = []
    with zipfile.ZipFile(path) as zf:
        names = sorted(n for n in zf.namelist() if re.fullmatch(r"xl/charts/chart\d+\.xml", n))
        for i, name in enumerate(names, start=1):
            root = etree.fromstring(zf.read(name))
            info = chart_info(root)
            info["index"] = i
            info["part"] = name
            out.append(info)
    return out


def _patch_anchor(root, patch: dict):
    """Convert a twoCellAnchor to a oneCellAnchor with a fixed size."""
    mode = patch.get("mode", "one_cell")
    if mode != "one_cell":
        return
    sizes = patch.get("sizes") or []
    alts = patch.get("alts") or []
    chart_pos = 0
    for anchor in list(root):
        if _local(anchor) not in {"twoCellAnchor", "oneCellAnchor", "absoluteAnchor"}:
            continue
        # Only chart frames are converted here.  Pictures (team photos) keep
        # their two-cell anchor and their xdr:pic child.
        if anchor.find(f".//{xdr('graphicFrame')}") is None:
            continue
        size = sizes[chart_pos] if chart_pos < len(sizes) else [patch.get("width_cm"), patch.get("height_cm")]
        alt = alts[chart_pos] if chart_pos < len(alts) else patch.get("alt")
        chart_pos += 1
        width = size[0] if size else None
        height = size[1] if size else None
        if _local(anchor) == "oneCellAnchor":
            if width and height:
                ext = anchor.find(xdr("ext"))
                if ext is not None:
                    ext.set("cx", str(int(width * CM_TO_EMU)))
                    ext.set("cy", str(int(height * CM_TO_EMU)))
            _set_anchor_alt(anchor, alt)
            continue
        frm = anchor.find(xdr("from"))
        if frm is None:
            continue
        # Compute existing size for a fallback.
        width = width or patch.get("width_cm")
        height = height or patch.get("height_cm")
        if not width or not height:
            ext = anchor.find(xdr("ext"))
            if ext is not None:
                width = int(ext.get("cx")) * EMU_TO_CM
                height = int(ext.get("cy")) * EMU_TO_CM
        if not width or not height:
            width, height = 16.0, 9.0
        new = etree.Element(xdr("oneCellAnchor"))
        new.append(frm)
        ext = etree.SubElement(new, xdr("ext"))
        ext.set("cx", str(int(width * CM_TO_EMU)))
        ext.set("cy", str(int(height * CM_TO_EMU)))
        for child in list(anchor):
            if _local(child) in {"graphicFrame", "clientData"}:
                new.append(child)
        _set_anchor_alt(new, alt)
        anchor.getparent().replace(anchor, new)


def _set_anchor_alt(anchor, alt: str | None):
    if not alt:
        return
    nv = anchor.find(f".//{xdr('cNvPr')}")
    if nv is not None:
        nv.set("descr", alt)
        nv.set("title", alt[:255])


def _patch_drawing(root, patch: dict):
    if patch.get("anchor"):
        _patch_anchor(root, patch["anchor"])


def patch_chart_xml(root, patch: dict) -> dict:
    """Apply a patch to one chart XML tree.  Returns a small change log."""
    changed = []
    chart = root.find(c("chart"))
    if chart is None:
        return {"changed": [], "error": "no c:chart"}
    if "title" in patch:
        _set_title(chart, patch["title"])
        changed.append("title")
    if "legend" in patch:
        _set_legend(chart, patch["legend"])
        changed.append("legend")
    if patch.get("rounded_corners") is not None:
        _set_val(root, "roundedCorners", "1" if patch["rounded_corners"] else "0", "chartSpace")
        changed.append("rounded_corners")
    if patch.get("plot_vis_only") is not None:
        _set_val(chart, "plotVisOnly", "1" if patch["plot_vis_only"] else "0", "chart")
        changed.append("plot_vis_only")
    if patch.get("disp_blanks"):
        _set_val(chart, "dispBlanksAs", patch["disp_blanks"], "chart")
        changed.append("disp_blanks")
    if patch.get("show_dlbls_over_max") is not None:
        _set_val(chart, "showDLblsOverMax", "1" if patch["show_dlbls_over_max"] else "0", "chart")
        changed.append("show_dlbls_over_max")

    plot = chart.find(c("plotArea"))
    if plot is not None:
        if patch.get("plot_layout"):
            layout = _ensure(plot, "layout", "plotArea")
            _remove(layout, "manualLayout")
            manual = etree.SubElement(layout, c("manualLayout"))
            target = etree.SubElement(manual, c("layoutTarget")); target.set("val", "inner")
            # CT_ManualLayout is a strict sequence: layoutTarget, xMode, yMode,
            # wMode, hMode, x, y, w, h.  Do not interleave mode and value.
            for key in ("x", "y", "w", "h"):
                if patch["plot_layout"].get(key) is not None:
                    mode = etree.SubElement(manual, c(f"{key}Mode")); mode.set("val", "edge")
            for key in ("x", "y", "w", "h"):
                if patch["plot_layout"].get(key) is not None:
                    val = etree.SubElement(manual, c(key)); val.set("val", str(patch["plot_layout"][key]))
            changed.append("plot_layout")
        groups = _chart_groups(plot)
        if groups:
            if patch.get("bar"):
                for group in groups:
                    if _local(group) not in {"barChart", "bar3DChart"}:
                        continue
                    if patch["bar"].get("gap") is not None:
                        _set_val(group, "gapWidth", patch["bar"]["gap"], _local(group))
                    if patch["bar"].get("overlap") is not None:
                        _set_val(group, "overlap", patch["bar"]["overlap"], _local(group))
                changed.append("bar")
            for group in groups:
                kind = _local(group)
                if patch.get("doughnut_hole") is not None and kind == "doughnutChart":
                    _set_val(group, "holeSize", patch["doughnut_hole"], "doughnutChart")
                    changed.append("doughnut_hole")
                if patch.get("pie_rotation") is not None and kind in {"pieChart", "doughnutChart"}:
                    _set_val(group, "firstSliceAng", patch["pie_rotation"], kind)
                    changed.append("pie_rotation")
                if patch.get("data_labels") is not None:
                    _set_dlbls(group, patch["data_labels"], order_key=kind)
            if patch.get("data_labels") is not None:
                changed.append("data_labels")
            # Flatten series across chart groups so series[1] of a combo
            # reaches the line series in the second group, not a missing index
            # in the bar group.
            series_refs = []
            for group in groups:
                for ser in group.findall(c("ser")):
                    series_refs.append((group, ser))
            for i, ser_patch in enumerate(patch.get("series") or []):
                if i < len(series_refs):
                    group, ser = series_refs[i]
                    _set_series_style(ser, ser_patch, chart_type=_local(group))
                    changed.append(f"series[{i}]")
            hide = {name.lower() for name in patch.get("hide_series") or []}
            if hide:
                for _, ser in series_refs:
                    tx = ser.find(c("tx"))
                    value = tx.find(f".//{c('v')}") if tx is not None else None
                    if value is not None and (value.text or "").strip().lower() in hide:
                        _hide_series(ser)
                        changed.append(f"hide_series:{value.text}")

        axes = patch.get("axes") or {}
        if axes:
            x_axis = _find_axis(plot, "x")
            if x_axis is None:
                # Scatter charts use a value axis on the bottom for X.
                x_axis = _find_axis(plot, "y", "b")
            y_axis = _find_axis(plot, "y", "l")
            y2_axis = _find_axis(plot, "y", "r")
            if axes.get("x") and x_axis is not None:
                _set_axis(x_axis, axes["x"]); changed.append("axis.x")
            if axes.get("y") and y_axis is not None:
                _set_axis(y_axis, axes["y"]); changed.append("axis.y")
            if axes.get("y2") and y2_axis is not None:
                _set_axis(y2_axis, axes["y2"]); changed.append("axis.y2")
            # Role-based selectors: bar charts put the value axis at the
            # bottom and the category axis at the left.
            if axes.get("value"):
                value_axis = _find_axis(plot, "y", "b")
                if value_axis is None:
                    value_axis = _find_axis(plot, "y")
                if value_axis is not None:
                    _set_axis(value_axis, axes["value"]); changed.append("axis.value")
            if axes.get("category"):
                category_axis = _find_axis(plot, "x", "l")
                if category_axis is None:
                    category_axis = _find_axis(plot, "x")
                if category_axis is not None:
                    _set_axis(category_axis, axes["category"]); changed.append("axis.category")
    return {"changed": changed}


def _sheet_drawing_index(members: dict[str, bytes]) -> dict[str, int]:
    """Map a worksheet name to its drawing part number (1-based)."""
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    workbook = members.get("xl/workbook.xml")
    wb_rels = members.get("xl/_rels/workbook.xml.rels")
    if not workbook or not wb_rels:
        return {}
    rel_target = {}
    for rel in etree.fromstring(wb_rels):
        rel_target[rel.get("Id")] = rel.get("Target")
    result = {}
    for sheet in etree.fromstring(workbook).iter():
        if not sheet.tag.endswith("}sheet"):
            continue
        rid = sheet.get(f"{{{rel_ns}}}id")
        target = rel_target.get(rid, "")
        sheet_part = "xl/" + target.lstrip("/").replace("xl/", "", 1) if target else ""
        if not sheet_part:
            continue
        rels_name = sheet_part.rsplit("/", 1)[0] + "/_rels/" + sheet_part.rsplit("/", 1)[1] + ".rels"
        rels = members.get(rels_name)
        if not rels:
            continue
        for rel in etree.fromstring(rels):
            if rel.get("Type", "").endswith("/drawing"):
                drawing = rel.get("Target", "").rsplit("/", 1)[-1]
                match = re.fullmatch(r"drawing(\d+)\.xml", drawing)
                if match:
                    result[sheet.get("name")] = int(match.group(1))
    return result


def patch_workbook(path: str | Path, patch: dict, out_path: str | Path | None = None) -> dict:
    """Patch chart XML parts and drawing anchors in a copy of an XLSX package."""
    path = Path(path)
    out_path = Path(out_path or path)
    patches = patch.get("charts") or [patch]
    anchors = patch.get("anchors") or []
    results = []
    with zipfile.ZipFile(path) as zin:
        members = {name: zin.read(name) for name in zin.namelist()}
        sheet_drawings = _sheet_drawing_index(members)
        chart_names = sorted(n for n in members if re.fullmatch(r"xl/charts/chart\d+\.xml", n))
        for i, chart_name in enumerate(chart_names, start=1):
            chart_patch = next((p for p in patches if int(p.get("index", i)) == i), None)
            if not chart_patch:
                continue
            root = etree.fromstring(members[chart_name])
            results.append({"chart": i, **patch_chart_xml(root, chart_patch)})
            members[chart_name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        # Anchors: apply the first anchor patch to every drawing, or per index/sheet.
        drawing_names = sorted(n for n in members if re.fullmatch(r"xl/drawings/drawing\d+\.xml", n))
        for i, name in enumerate(drawing_names, start=1):
            anchor_patch = next((p for p in anchors
                                 if p.get("sheet") and sheet_drawings.get(p["sheet"]) == i), None)
            if anchor_patch is None:
                anchor_patch = next((p for p in anchors if int(p.get("drawing", i)) == i), None)
            if anchor_patch is None and anchors and len(anchors) == 1 and not anchors[0].get("sheet"):
                anchor_patch = anchors[0]
            if not anchor_patch:
                continue
            root = etree.fromstring(members[name])
            _patch_drawing(root, anchor_patch)
            members[name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        # Ask Excel to recalculate on load.
        if "xl/workbook.xml" in members:
            root = etree.fromstring(members["xl/workbook.xml"])
            calc = root.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}calcPr")
            if calc is not None:
                calc.set("fullCalcOnLoad", "1")
                calc.set("forceFullCalc", "1")
                members["xl/workbook.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    tmp = out_path.with_suffix(".patch.xlsx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, blob in members.items():
            zout.writestr(name, blob)
    tmp.replace(out_path)
    return {"ok": True, "output": str(out_path), "charts": results}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("xlsx", type=Path)
    p = sub.add_parser("apply")
    p.add_argument("xlsx", type=Path)
    p.add_argument("patch", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "inspect":
        print(json.dumps(list_charts(args.xlsx), indent=2, ensure_ascii=False))
    else:
        patch = json.loads(args.patch.read_text(encoding="utf-8"))
        print(json.dumps(patch_workbook(args.xlsx, patch, args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
