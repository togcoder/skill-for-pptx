#!/usr/bin/env python3
"""Compile a restricted radial drill-down intent into native Morph scene states.

AI supplies the intent; this is not an NLP parser or a PowerPoint playback engine.
No third-party dependencies. See source skill references/compound-choreography.md.
"""
import argparse
import json
import math
from pathlib import Path

OPS = ["burst", "orbit", "focus", "split", "reassemble", "restore"]
KEYS = {"version", "recipe", "prompt", "title", "node_count", "focus_node",
        "layer_count", "orbit_degrees", "orbit_segments", "direction",
        "keep_labels_upright", "operations", "assumptions", "requirements"}
REF = "https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks"


def validate_intent(intent):
    if not isinstance(intent, dict):
        return ["intent must be an object"]
    errors = [f"unsupported field: {k}" for k in sorted(intent.keys() - KEYS)]
    errors += [f"missing field: {k}" for k in sorted(KEYS - intent.keys())]
    if errors:
        return errors
    for key, value in (("version", "0.1"), ("recipe", "radial-drilldown"),
                       ("operations", OPS), ("keep_labels_upright", True)):
        if intent[key] != value or (key == "keep_labels_upright" and type(intent[key]) is not bool):
            errors.append(f"unsupported {key}: {intent[key]!r}")
    for key, low, high in (("node_count", 6, 12), ("layer_count", 3, 5),
                           ("focus_node", 1, 12), ("orbit_segments", 1, 24)):
        if type(intent[key]) is not int or not low <= intent[key] <= high:
            errors.append(f"{key} must be integer {low}..{high}")
    if not errors and intent["focus_node"] > intent["node_count"]:
        errors.append("focus_node exceeds node_count")
    angle = intent["orbit_degrees"]
    if type(angle) not in (int, float) or not math.isfinite(angle) or not 15 <= angle <= 360:
        errors.append("orbit_degrees must be finite 15..360")
    elif type(intent["orbit_segments"]) is int and intent["orbit_segments"] > 0 and angle/intent["orbit_segments"] > 90:
        errors.append("orbit step exceeds 90 degrees; add waypoints to preserve direction")
    if intent["direction"] not in ("clockwise", "counterclockwise"):
        errors.append("direction must be clockwise or counterclockwise")
    for key in ("prompt", "title"):
        if not isinstance(intent[key], str) or not intent[key].strip():
            errors.append(f"{key} must be nonempty text")
    if isinstance(intent["title"], str) and len(intent["title"]) > 45:
        errors.append("title exceeds 45 characters; shorten without dropping the subject")
    for key in ("assumptions", "requirements"):
        if not isinstance(intent[key], list) or not intent[key] or any(not isinstance(x, str) or not x.strip() for x in intent[key]):
            errors.append(f"{key} must be a nonempty text list")
    return errors


def frame(cx, cy, w, h):
    return dict(x=(cx-w/2)/1280, y=(cy-h/2)/720, w=w/1280, h=h/720,
                rotation_deg=0, opacity=1)


def compile_intent(intent):
    errors = validate_intent(intent)
    if errors:
        raise ValueError("; ".join(errors))
    n, focus, layers = (intent[k] for k in ("node_count", "focus_node", "layer_count"))
    objects = []
    def add(oid, geometry, fill="none", text=None, font=28, stroke="none"):
        obj = dict(id=oid, kind="text" if geometry == "textbox" else "shape",
                   persistent=True, morph_name="!!"+oid, geometry=geometry,
                   fill=fill, stroke=stroke, stroke_width=1.5 if stroke != "none" else 0)
        if text is not None:
            obj.update(text=text, font_size=font, text_color="#F6F2E8", bold=True)
        objects.append(obj)
    for i in range(1, n+1):
        if i == focus:
            for k in range(layers):
                add(f"node-{i}-layer-{k+1}", "rect", ["#56C4AE", "#409C9B", "#307C8D", "#245B79", "#304866"][k])
        else:
            add(f"node-{i}", "ellipse", "#2B2A35", stroke="#696674")
        add(f"label-{i}", "textbox", text=f"{i:02}", font=26)
    # Explicit occluder: hides the stacked launch nodes. Its order is stable.
    add("core", "ellipse", "#C37745")
    add("core-label", "textbox", text="CORE", font=25)
    add("title", "textbox", text=intent["title"], font=44)
    add("phase", "textbox", text="", font=28)

    direction = 1 if intent["direction"] == "clockwise" else -1
    theta = direction*intent["orbit_degrees"]
    phases = [("core", 0, 0, "Lõi hệ thống") , ("burst", 0, 224, f"{n} nút thành một vòng")]
    phases += [(f"orbit-{j}", theta*j/intent["orbit_segments"], 224,
                f"Xoay {'thuận' if direction == 1 else 'ngược'} chiều kim đồng hồ")
               for j in range(1, intent["orbit_segments"]+1)]
    phases += [("focus", theta, 224, f"Phóng nút {focus:02}"),
               ("split", theta, 224, f"{layers} lớp bên trong nút {focus:02}"),
               ("reassemble", theta, 224, f"Ghép lại nút {focus:02}"),
               ("restore", theta, 224, "Trở về hệ thống")]
    states = []
    for sid, angle, radius, caption in phases:
        frames = {}
        for i in range(1, n+1):
            a = math.radians(-90 + (i-1)*360/n + angle)
            x, y = 420 + radius*math.cos(a), 407 + radius*math.sin(a)
            w, h = 62, 48
            active = i == focus and sid in ("focus", "split", "reassemble")
            if active:
                x, y, w, h = 940, 407, 248, 192
            if i == focus:
                gap = 22 if sid == "split" else 0
                layer_h = h/layers
                total_h = h + gap*(layers-1)
                for k in range(layers):
                    ly = y-total_h/2 + layer_h/2 + k*(layer_h+gap)
                    frames[f"node-{i}-layer-{k+1}"] = frame(x, ly, w, layer_h)
            else:
                frames[f"node-{i}"] = frame(x, y, w, h)
            label_y = y-(h+22*(layers-1))/2-30 if sid == "split" and i == focus else y
            frames[f"label-{i}"] = frame(x, label_y, 60, 42)
        frames["core"] = frame(420, 407, 126, 126)
        frames["core-label"] = frame(420, 407, 112, 46)
        frames["title"] = frame(640, 64, 1160, 74)
        frames["phase"] = frame(640, 125, 1160, 52) | {"text": caption}
        states.append(dict(id=sid, message=caption, objects=frames))
    ids = [o["id"] for o in objects]
    transitions = [dict(**{"from": a["id"], "to": b["id"]}, kind="morph",
                        duration_ms=350 if b["id"].startswith("orbit-") else 1000, track=ids)
                   for a,b in zip(states, states[1:])]
    step = intent["orbit_degrees"]/intent["orbit_segments"]
    return dict(version="0.1", brief=intent["prompt"],
                canvas=dict(width=16, height=9, units="normalized"), data_provenance="synthetic",
                objects=objects, states=states, transitions=transitions,
                research_metadata=dict(recipe="radial-drilldown", intent=intent,
                    references=[REF], approximation="piecewise linear orbit; click-through Morph; native playback unverified",
                    orbit_radius_px=224, orbit_step_degrees=step,
                    chord_radial_error_px=224*(1-math.cos(math.radians(step/2))),
                    launch_occlusion="node shapes and labels stack behind core shape",
                    focus_scale=4, native_playback_verified=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plan = compile_intent(json.loads(args.intent.read_text(encoding="utf-8")))
    # Protect historical evidence and parallel runs.
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(plan, out, ensure_ascii=False, indent=2)
        out.write("\n")
    print(json.dumps({"states":len(plan["states"]), "objects":len(plan["objects"]),
                      "output":str(args.output), "playback_verified":False}))


if __name__ == "__main__":
    main()
