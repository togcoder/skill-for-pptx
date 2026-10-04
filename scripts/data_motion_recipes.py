#!/usr/bin/env python3
"""Semantic motion recipes for charts and standalone KPI numbers.

This module recommends choreography primitives from PPTX inventory semantics.
It does not write OOXML. Low-level chart/counter compilation must preserve the
chosen click-beat and pass exact-file PowerPoint playback QA.
"""

CHART_RULES={
    "column":{
        "recipe":"baseline-grow",
        "effect_family":"wipe-up",
        "single_series_build":"category-elements",
        "multi_series_build":"series",
        "reason":"Columns encode magnitude from a baseline; grow/reveal from that baseline preserves the reading direction.",
    },
    "bar":{
        "recipe":"baseline-grow",
        "effect_family":"wipe-right",
        "single_series_build":"category-elements",
        "multi_series_build":"series",
        "reason":"Horizontal bars read from the value baseline; reveal left-to-right instead of flying the chart as a block.",
    },
    "line":{
        "recipe":"series-trace",
        "effect_family":"wipe-left-to-right",
        "single_series_build":"series",
        "multi_series_build":"series",
        "reason":"A line chart communicates progression; a directional trace preserves x-axis order.",
    },
    "area":{
        "recipe":"area-reveal",
        "effect_family":"wipe-left-to-right",
        "single_series_build":"series",
        "multi_series_build":"series",
        "reason":"Area charts encode an ordered trend plus magnitude; reveal along the x direction while keeping chart background stable.",
    },
    "pie":{
        "recipe":"segment-sweep",
        "effect_family":"wheel",
        "single_series_build":"category-elements",
        "multi_series_build":"category-elements",
        "reason":"Pie slices encode parts of one whole; reveal segments around the circle rather than translating the whole chart.",
    },
    "doughnut":{
        "recipe":"segment-sweep",
        "effect_family":"wheel",
        "single_series_build":"category-elements",
        "multi_series_build":"category-elements",
        "reason":"Doughnut segments encode composition; radial segment reveal matches the geometry.",
    },
    "scatter":{
        "recipe":"point-build",
        "effect_family":"fade-or-zoom",
        "single_series_build":"series-elements",
        "multi_series_build":"series",
        "reason":"Scatter plots are sets of observations; build points/series without implying a false sequential path.",
    },
    "bubble":{
        "recipe":"point-build",
        "effect_family":"zoom",
        "single_series_build":"series-elements",
        "multi_series_build":"series",
        "reason":"Bubble size is data; a restrained zoom/pop can reveal observations without moving their encoded positions.",
    },
    "radar":{
        "recipe":"radial-series-build",
        "effect_family":"fade",
        "single_series_build":"series",
        "multi_series_build":"series",
        "reason":"Radar charts compare profiles around a common center; reveal whole series rather than individual vertices by default.",
    },
    "stock":{
        "recipe":"ordered-category-build",
        "effect_family":"wipe-left-to-right",
        "single_series_build":"category",
        "multi_series_build":"category",
        "reason":"Stock charts are ordered by time/category; preserve that ordering during reveal.",
    },
    "combo":{
        "recipe":"layered-series-build",
        "effect_family":"fade-or-wipe",
        "single_series_build":"series",
        "multi_series_build":"series",
        "reason":"Combo charts layer different encodings; reveal by series/layer so the audience can parse one encoding before the next.",
    },
}

ALIASES={
    "bar-or-column":"column",
    "bar-or-column-3d":"column",
    "line-3d":"line",
    "pie-3d":"pie",
    "area-3d":"area",
    "surface":"area",
    "surface-3d":"area",
    "pie-of-pie":"pie",
}


def chart_motion_recipe(chart_summary):
    if not isinstance(chart_summary,dict):
        return None
    primary=chart_summary.get("primary_type") or "unknown"
    key=ALIASES.get(primary,primary)
    rule=CHART_RULES.get(key)
    if rule is None:
        return {
            "semantic_kind":"chart",
            "chart_type":primary,
            "recipe":"semantic-build",
            "effect_family":"fade",
            "preferred_build":"as-whole",
            "animate_background":False,
            "reason":"Unknown or unsupported chart subtype; use a conservative whole-chart build until a type-specific recipe is verified.",
            "requires_native_playback":True,
        }

    series_count=chart_summary.get("series_count")
    build_key="single_series_build" if series_count in (None,0,1) else "multi_series_build"
    return {
        "semantic_kind":"chart",
        "chart_type":primary,
        "recipe":rule["recipe"],
        "effect_family":rule["effect_family"],
        "preferred_build":rule[build_key],
        "animate_background":False,
        "reason":rule["reason"],
        "requires_native_playback":True,
    }


def _decimal_places(raw):
    if not isinstance(raw,str):
        return 0
    number=raw.replace(",","")
    if "." not in number:
        return 0
    return len(number.rsplit(".",1)[1])


def number_counter_recipe(number_semantics):
    if not isinstance(number_semantics,dict) or not number_semantics.get("counter_candidate"):
        return None
    target=number_semantics.get("numeric_value")
    if not isinstance(target,(int,float)):
        return None
    magnitude=abs(target)
    if magnitude < 100:
        duration=900
        steps=10
    elif magnitude < 10000:
        duration=1100
        steps=12
    else:
        duration=1300
        steps=14
    raw_number=number_semantics.get("raw","")
    prefix=number_semantics.get("prefix","")
    suffix=number_semantics.get("suffix","")
    numeric_token=raw_number
    if prefix and numeric_token.startswith(prefix):
        numeric_token=numeric_token[len(prefix):].lstrip()
    if suffix and numeric_token.endswith(suffix):
        numeric_token=numeric_token[:-len(suffix)].rstrip()

    return {
        "semantic_kind":"number-counter",
        "recipe":"count-up" if target>=0 else "count-down",
        "from_value":0,
        "to_value":target,
        "duration_ms":duration,
        "steps":steps,
        "decimal_places":_decimal_places(numeric_token),
        "prefix":prefix,
        "suffix":suffix,
        "preferred_implementation":"odometer-proxy",
        "fallback_implementation":"stepped-text",
        "preserve_final_text":raw_number,
        "requires_narrative_highlight":True,
        "requires_native_playback":True,
    }
