#!/usr/bin/env python3
"""OOXML helpers for native PowerPoint chart animation fan-out.

This module only builds chart-target animation fragments. It does not claim
PowerPoint playback correctness; exact-file playback remains the acceptance gate.
"""

A="http://schemas.openxmlformats.org/drawingml/2006/main"

BUILD_TO_OOXML={
    "as-whole":"asWhole",
    "series":"series",
    "category":"category",
    "series-elements":"seriesEl",
    "category-elements":"categoryEl",
}

VALID_FILTERS={
    "fade",
    "wipe(up)",
    "wipe(down)",
    "wipe(left)",
    "wipe(right)",
    "wedge",
    "wheel(1)",
    "circle(in)",
}

FANOUT_LIMIT_DEFAULT=24


def concrete_chart_filter(chart_type):
    """Map semantic chart type to a conservative verified entrance filter."""
    if chart_type=="column":
        return "wipe(up)"
    if chart_type=="bar":
        return "wipe(right)"
    if chart_type in ("line","area","stock"):
        return "wipe(right)"
    if chart_type in ("pie","doughnut","pie-of-pie","pie-3d"):
        return "wheel(1)"
    if chart_type in ("scatter","bubble"):
        return "fade"
    if chart_type=="radar":
        return "circle(in)"
    if chart_type=="combo":
        return "fade"
    return "fade"


def _positive_int(value):
    return isinstance(value,int) and not isinstance(value,bool) and value>0


def chart_fanout(build,series_count,category_count):
    """Return chart sub-target tuples: (seriesIdx, categoryIdx, bldStep)."""
    if build not in BUILD_TO_OOXML:
        raise ValueError(f"unsupported chart build: {build}")
    if build=="as-whole":
        return []
    if not _positive_int(series_count):
        raise ValueError("series_count must be positive for chart fan-out")
    if build in ("category","series-elements","category-elements") and not _positive_int(category_count):
        raise ValueError(f"category_count must be positive for chart build {build}")

    if build=="series":
        return [(s,-4,"series") for s in range(series_count)]
    if build=="category":
        return [(-4,c,"category") for c in range(category_count)]
    if build=="series-elements":
        return [
            (s,c,"ptInSeries")
            for s in range(series_count)
            for c in range(category_count)
        ]
    if build=="category-elements":
        return [
            (s,c,"ptInCategory")
            for c in range(category_count)
            for s in range(series_count)
        ]
    raise AssertionError(build)


def guard_chart_fanout(build,series_count,category_count,limit=FANOUT_LIMIT_DEFAULT):
    """Reduce overly dense element fan-out while preserving chart meaning."""
    steps=chart_fanout(build,series_count,category_count)
    if len(steps)<=limit:
        return {
            "requested_build":build,
            "effective_build":build,
            "fanout_count":len(steps),
            "degraded":False,
            "reason":None,
        }

    if build in ("series-elements","category-elements") and _positive_int(series_count):
        fallback="series"
    elif build=="category" and _positive_int(series_count) and series_count>1:
        fallback="series"
    else:
        fallback="as-whole"

    fallback_steps=chart_fanout(fallback,series_count,category_count)
    return {
        "requested_build":build,
        "effective_build":fallback,
        "fanout_count":len(fallback_steps),
        "degraded":True,
        "reason":f"fan-out {len(steps)} exceeds limit {limit}",
    }


def ooxml_build_token(build):
    try:
        return BUILD_TO_OOXML[build]
    except KeyError as exc:
        raise ValueError(f"unsupported chart build: {build}") from exc
