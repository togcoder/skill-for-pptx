#!/usr/bin/env python3
"""Conservative generic report-motion recipes.

These recipes are semantic defaults for ordinary source objects. They are
deliberately small: reveal, stagger-reveal and in-place focus pulse. Operations
that alter layout require explicit geometry instead of guessing.
"""

SUPPORTED_GENERIC_OPERATIONS={
    "reveal",
    "stagger-reveal",
    "process-reveal",
    "focus",
    "emphasize",
    "move",
    "rotate",
}

def reveal_filter(shape):
    kind=(shape or {}).get("kind")
    if kind=="connector":
        return "wipe(right)"
    return "fade"


def focus_scale(shape):
    """Return a conservative in-place pulse scale, bounded by slide edges."""
    geom=(shape or {}).get("geometry") or {}
    x,y,w,h=(geom.get(k) for k in ("x","y","w","h"))
    if not all(isinstance(v,(int,float)) for v in (x,y,w,h)) or w<=0 or h<=0:
        return 1.06
    cx=x+w/2
    cy=y+h/2
    if cx<=0 or cy<=0 or cx>=1 or cy>=1:
        return 1.02
    max_x=min(cx/(w/2),(1-cx)/(w/2)) if w else 1.0
    max_y=min(cy/(h/2),(1-cy)/(h/2)) if h else 1.0
    edge_cap=max(1.0,min(max_x,max_y))
    return round(max(1.02,min(1.08,edge_cap*0.98)),3)


def generic_motion_recipe(operation,shapes,motion_parameters=None):
    if operation not in SUPPORTED_GENERIC_OPERATIONS:
        return None
    motion_parameters=motion_parameters or {}
    if operation in ("reveal","stagger-reveal","process-reveal"):
        if not shapes:
            raise ValueError("reveal operation requires targets")
        return {
            "kind":"reveal",
            "operation":operation,
            "filters":[reveal_filter(shape) for shape in shapes],
            "duration_ms":320,
            "stagger_ms":140 if operation!="reveal" or len(shapes)>1 else 0,
        }
    if operation in ("focus","emphasize"):
        if len(shapes)!=1:
            raise ValueError("focus/emphasize requires exactly one target")
        return {
            "kind":"focus-pulse",
            "operation":operation,
            "scale":focus_scale(shapes[0]),
            "up_duration_ms":360,
            "down_duration_ms":300,
        }
    if operation=="move":
        points=motion_parameters.get("points")
        if not isinstance(points,list) or len(points)<2:
            raise ValueError("move requires explicit motion_parameters.points")
        return {"kind":"motion-path","points":points,"duration_ms":motion_parameters.get("duration_ms",650)}
    if operation=="rotate":
        by_deg=motion_parameters.get("by_deg")
        if not isinstance(by_deg,(int,float)):
            raise ValueError("rotate requires motion_parameters.by_deg")
        return {"kind":"rotate","by_deg":by_deg,"duration_ms":motion_parameters.get("duration_ms",500)}
    raise AssertionError(operation)
