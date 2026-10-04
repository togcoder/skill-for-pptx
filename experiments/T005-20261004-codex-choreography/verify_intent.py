"""Independent geometry checks for the frozen T005 intent (no playback claim)."""
import argparse
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("frozen_paths", ROOT/"experiments/E003/path_diagnostic.py")
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)


def box(f):
    return [f["x"]*1280, f["y"]*720, f["w"]*1280, f["h"]*720]


def center(f):
    x,y,w,h = box(f)
    return x+w/2, y+h/2


def check(intent, plan):
    n, focus, count = intent["node_count"], intent["focus_node"], intent["layer_count"]
    states = {s["id"]:s["objects"] for s in plan["states"]}
    labels = [f"label-{i}" for i in range(1,n+1)]
    parts = [f"node-{focus}-layer-{j}" for j in range(1,count+1)]
    expected_order = ["core", "burst"] + [f"orbit-{i}" for i in range(1,intent["orbit_segments"]+1)] + ["focus","split","reassemble","restore"]
    flags = {"semantic_node_count": {o["id"] for o in plan["objects"] if o["id"].startswith("label-")} == set(labels),
             "operation_order": [s["id"] for s in plan["states"]] == expected_order}
    if any(s not in states for s in expected_order):
        return {"checks": flags, "passed":False, "error":"required states absent", "powerpoint_playback_verified":False}
    orbit = ["burst"] + [s for s in expected_order if s.startswith("orbit-")]
    expected_sign = 1 if intent["direction"] == "clockwise" else -1
    measured_angles = []
    radial_errors = []
    waypoint_error = []
    for index,label in enumerate(labels):
        for step,sid in enumerate(orbit):
            angle = math.radians(-90+index*360/n+expected_sign*intent["orbit_degrees"]*step/intent["orbit_segments"])
            expected = (420+224*math.cos(angle),407+224*math.sin(angle))
            waypoint_error.append(math.dist(center(states[sid][label]),expected))
        total = 0
        for a,b in zip(orbit,orbit[1:]):
            u,v = [tuple(t-c for t,c in zip(center(states[s][label]),(420,407))) for s in (a,b)]
            total += math.degrees(math.atan2(u[0]*v[1]-u[1]*v[0],u[0]*v[0]+u[1]*v[1]))
            radial_errors.append(224-math.hypot((u[0]+v[0])/2,(u[1]+v[1])/2))
        measured_angles.append(total)
    flags["orbit_angle_direction"] = all(abs(a-expected_sign*intent["orbit_degrees"]) < 1e-7 for a in measured_angles) and max(waypoint_error)<1e-7
    last = states[orbit[-1]]
    before = box(last[parts[0]])
    after = box(states["focus"][parts[0]])
    flags["focus_identity_scale"] = abs(after[2]/before[2]-4)<1e-8 and abs(after[3]/before[3]-4)<1e-8 and all(states["focus"][l] == last[l] for l in labels if l != f"label-{focus}")
    split = [box(states["split"][p]) for p in parts]
    actual_parts = {o["id"] for o in plan["objects"] if o["id"].startswith(f"node-{focus}-layer-")}
    flags["layer_count_separation"] = actual_parts == set(parts) and all(b[1]-(a[1]+a[3])>0 for a,b in zip(split,split[1:]))
    tracked = [o["id"] for o in plan["objects"] if o["id"] not in ("phase",)]
    flags["exact_reassembly"] = all(states["focus"][k]==states["reassemble"][k] and last[k]==states["restore"][k] for k in tracked)
    flags["upright_labels"] = all(s[l]["rotation_deg"]==0 for s in states.values() for l in labels)
    orbit_plan = dict(states=[s for s in plan["states"] if s["id"] in orbit])
    label_proxy = proxy.evaluate(orbit_plan, labels)
    # Collapse the selected node's contiguous layers into its carrier envelope.
    carrier_plan = {"states":[]}
    for sid in orbit:
        frames = {}
        for i in range(1,n+1):
            if i == focus:
                rects = [box(states[sid][p]) for p in parts]
                x,y = min(b[0] for b in rects),min(b[1] for b in rects)
                r,d = max(b[0]+b[2] for b in rects),max(b[1]+b[3] for b in rects)
                frames[f"node-{i}"] = dict(x=x/1280,y=y/720,w=(r-x)/1280,h=(d-y)/720,rotation_deg=0)
            else: frames[f"node-{i}"] = states[sid][f"node-{i}"]
        carrier_plan["states"].append(dict(id=sid,objects=frames))
    carrier_proxy = proxy.evaluate(carrier_plan,[f"node-{i}" for i in range(1,n+1)])
    binding = []
    for sid in orbit + ["focus","reassemble","restore"]:
        lx,ly = center(states[sid][f"label-{focus}"])
        for j,p in enumerate(parts):
            x,y,w,h=box(states[sid][p])
            expected_y=ly-count*h/2+j*h
            binding += [abs(x+w/2-lx),abs(y-expected_y)]
    return dict(checks=flags,passed=all(flags.values()),check_count=len(flags),
                orbit_measured_degrees=measured_angles,
                waypoint_max_error_px=max(waypoint_error),
                orbit_linear_proxy=dict(max_radial_deviation_px=max(radial_errors),
                    label_overlaps=label_proxy["overlapping_pairs"], carrier_overlaps=carrier_proxy["overlapping_pairs"],
                    pair_transition_count=len(label_proxy["pairs"]),
                    assumption=label_proxy["assumption"]),
                binding_max_error_px=max(binding),
                scope="7 semantic/geometry categories; package parity is category 8 and checked separately",
                powerpoint_playback_verified=False)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent",type=Path);parser.add_argument("plan",type=Path)
    args=parser.parse_args()
    result=check(json.loads(args.intent.read_text()),json.loads(args.plan.read_text()))
    print(json.dumps(result,indent=2));sys.exit(not result["passed"])
