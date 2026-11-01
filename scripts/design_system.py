#!/usr/bin/env python3
"""The design system, one source of truth for beauty and technique (T034).

``knowledge/design_system.json`` holds the bands every tool shares: motion
durations by role, easing roles, stagger, rhythm limits, type scale, contrast
and density. Generators read their defaults here; ``validate_director_plan``,
``motion_director.verify``, ``forge_qa`` and ``design_critic`` grade decks
against the same numbers, so what the tools make and what they check cannot
drift apart. Easing curves are fitted in ``motion_tokens`` (Carbon/Material
to PowerPoint accel/decel); this module maps roles onto them.

    design_system.py                 # print the system (bands, roles, rules)
    design_system.py --rule MOT-EASING
"""
import argparse
import functools
import json
from pathlib import Path

try:
    from . import motion_tokens as _mt
except ImportError:
    import motion_tokens as _mt

PATH=Path(__file__).resolve().parents[1]/"knowledge"/"design_system.json"


@functools.lru_cache(maxsize=None)
def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def duration(role):
    """{"band":[lo,hi], "limit":[lo,hi], "default":ms} for a motion role."""
    return load()["motion"]["duration_ms"][role]


def default_ms(role):
    return int(duration(role)["default"])


def grade(value,spec):
    """"good" inside the band, "note" outside it but inside the limit, else "warn"."""
    lo,hi=spec["band"]
    if lo<=value<=hi:
        return "good"
    lo,hi=spec.get("limit",spec["band"])
    return "note" if lo<=value<=hi else "warn"


def clamp(value,role):
    """Bring a duration into its role's band (generators use this for defaults)."""
    lo,hi=duration(role)["band"]
    return int(max(lo,min(hi,value)))


def easing(role):
    """(accel, decel) for a motion role ("move", "enter", "exit", ...) or a
    motion_tokens role/token name."""
    name=load()["motion"]["easing_roles"].get(role,role)
    if name=="linear":
        return (0.0,0.0)
    return _mt.ease(name)


def travel_ms(distance):
    """Duration of a move of ``distance`` slide widths (longer journeys take
    longer, inside the move band)."""
    t=load()["motion"]["travel"]
    return int(max(t["min_ms"],min(t["max_ms"],t["min_ms"]+t["per_slide_width_ms"]*max(0.0,distance))))


def rhythm(name):
    return load()["motion"]["rhythm"][name]


def rule(rule_id):
    return next(r for r in load()["rules"] if r["id"]==rule_id)


def luminance(hexcol):
    """WCAG relative luminance of an sRGB hex colour (``RRGGBB``)."""
    def ch(v):
        v/=255
        return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
    r,g,b=(int(hexcol[i:i+2],16) for i in (0,2,4))
    return 0.2126*ch(r)+0.7152*ch(g)+0.0722*ch(b)


def contrast(a,b):
    """WCAG contrast ratio between two hex colours."""
    hi,lo=sorted((luminance(a),luminance(b)),reverse=True)
    return (hi+0.05)/(lo+0.05)


def text_contrast_needed(size_pt,bold=False):
    """WCAG 2.2 SC 1.4.3: large text is >= 18 pt, or >= 14 pt bold."""
    c=load()["color"]
    large=size_pt is not None and (size_pt>=c["large_text_pt"] or (bold and size_pt>=c["large_bold_text_pt"]))
    return c["large_text_contrast"] if large else c["text_contrast"]


def graphic_contrast_needed():
    """WCAG 2.2 SC 1.4.11: meaningful graphics >= 3:1 against what is behind."""
    return load()["color"]["graphic_contrast"]




def chrome():
    """Deck chrome safe margins, logo, breadcrumbs, and progress bar specs."""
    return load().get("chrome", {})


def optical_icon_compensation(shape_type, base_size=32):
    """Calculate optically balanced dimensions (w, h, dx, dy, badge_size) for icons."""
    opt = load().get("optical_icons", {})
    mults = opt.get("compensation_multipliers", {})
    st = str(shape_type).lower()
    if st in ("square", "box", "rect"):
        factor = mults.get("square", 0.88)
        w, h, dx, dy = base_size * factor, base_size * factor, 0.0, 0.0
    elif st in ("wide", "horizontal"):
        w_fac = mults.get("wide", {}).get("x", 1.08)
        h_fac = mults.get("wide", {}).get("y", 0.82)
        w, h, dx, dy = base_size * w_fac, base_size * h_fac, 0.0, 0.0
    elif st in ("triangle", "apex", "cone"):
        scale = mults.get("triangle", {}).get("scale", 1.05)
        v_offset = mults.get("triangle", {}).get("vertical_offset_factor", 0.06)
        w, h = base_size * scale, base_size * scale
        dx, dy = 0.0, -base_size * v_offset
    else:  # circle / default
        factor = mults.get("circle", 1.00)
        w, h, dx, dy = base_size * factor, base_size * factor, 0.0, 0.0

    badge_scale = opt.get("badge", {}).get("scale_multiplier", 2.0)
    return {
        "width": round(w, 2),
        "height": round(h, 2),
        "dx": round(dx, 2),
        "dy": round(dy, 2),
        "badge_size": round(base_size * badge_scale, 2)
    }


def bento_grid_layout(content_box=None):
    """Return the 4 canonical bounding boxes for a Bento Grid layout."""
    grids = load().get("layout_grids", {})
    bento = grids.get("bento_grid", {})
    return {
        "hero": bento.get("hero_card", {"x": 48, "y": 108, "w": 496, "h": 396}),
        "top_right": bento.get("top_right_card", {"x": 564, "y": 108, "w": 348, "h": 188}),
        "bottom_right_1": bento.get("bottom_right_card_1", {"x": 564, "y": 316, "w": 164, "h": 188}),
        "bottom_right_2": bento.get("bottom_right_card_2", {"x": 748, "y": 316, "w": 164, "h": 188}),
        "gutter": bento.get("gutter_pt", 20)
    }


def asymmetric_golden_layout(reverse=False):
    """Return major and minor card bounding boxes using the Golden Ratio (61.8% / 38.2%)."""
    grids = load().get("layout_grids", {})
    asym = grids.get("asymmetric_golden_ratio", {})
    cbox = grids.get("content_box_pt", {"x": 48, "y": 108, "w": 864, "h": 396})
    maj_w = asym.get("major_w_pt", 522)
    min_w = asym.get("minor_w_pt", 322)
    gutter = asym.get("gutter_pt", 20)
    h = asym.get("card_h_pt", 396)

    if not reverse:
        major = {"x": cbox["x"], "y": cbox["y"], "w": maj_w, "h": h}
        minor = {"x": cbox["x"] + maj_w + gutter, "y": cbox["y"], "w": min_w, "h": h}
    else:
        minor = {"x": cbox["x"], "y": cbox["y"], "w": min_w, "h": h}
        major = {"x": cbox["x"] + min_w + gutter, "y": cbox["y"], "w": maj_w, "h": h}

    return {"major": major, "minor": minor, "gutter": gutter}


def duarte_break_positions(total_slides):
    """Return 1-based slide indices where Nancy Duarte pattern breaks should occur."""
    db = load().get("duarte_breaks", {})
    if total_slides < db.get("trigger_min_slides", 5):
        return []
    fractions = db.get("position_fractions", [0.33, 0.67])
    positions = sorted(list({max(1, min(total_slides, round(total_slides * f))) for f in fractions}))
    return positions


def modular_scale(step_name):
    """Return font size in points for a named modular scale token."""
    tokens = load().get("color_and_type_scales", {}).get("modular_scale", {}).get("tokens_pt", {})
    return tokens.get(step_name)


def background_layers():
    """Return Z0, Z1, Z2 background depth layer configurations."""
    return load().get("background_layers", {})


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rule")
    a=ap.parse_args()
    if a.rule:
        print(json.dumps(rule(a.rule),indent=1,ensure_ascii=False))
        return
    ds=load()
    out={"version":ds["version"],
         "easing":{role:easing(role) for role in ds["motion"]["easing_roles"]},
         "duration_ms":{k:v for k,v in ds["motion"]["duration_ms"].items()},
         "rules":[f"{r['id']}: {r['statement']}" for r in ds["rules"]]}
    print(json.dumps(out,indent=1,ensure_ascii=False))


if __name__=="__main__":
    main()
