#!/usr/bin/env python3
"""Post-process motion-plan.json with the facts read back from the built deck:
actual visible-at-entry shapes, per-beat effect count, peak movers, duration."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_animator as pa  # noqa: E402

EXP = ROOT / "experiments/T067-20261104-opencode-deck-director/motion"
DECK = EXP / "artifacts/T066-deck-directed.pptx"
PLAN = EXP / "motion-plan.json"


def names(root):
    out = {}
    for sid, node in pa.top_level_objects(root).items():
        props = node.find("./*/p:cNvPr", pa.NS)
        out[sid] = props.get("name") if props is not None else None
    return out


def effect_times(effects):
    end = 0
    block_start = 0
    out = []
    for i, e in enumerate(effects):
        if i == 0:
            block_start = 0
        elif e.get("node_type") in ("afterEffect", "clickEffect"):
            block_start = end
        start = block_start + (e.get("delay_ms") or 0)
        finish = start + (e.get("duration_ms") or 0)
        end = max(end, finish)
        out.append({**e, "start": start, "end": finish})
    return out


def main():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    import zipfile, re
    z = zipfile.ZipFile(DECK)
    slide_parts = sorted(
        [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        key=lambda s: int(re.search(r"(\d+)\.xml", s).group(1)),
    )
    for spec, part in zip(plan["slides"], slide_parts):
        root = ET.fromstring(z.read(part))
        nm = names(root)
        groups = pa.read_main_sequence(root)
        first_click = {}
        for gi, g in enumerate(groups, 1):
            for e in g["effects"]:
                if e.get("visibility") == "visible":
                    first_click.setdefault(e["spid"], gi)
        visible = [nm.get(sid) for sid in nm if sid not in first_click]
        spec["base_visible"] = visible
        spec.pop("base", None)
        for beat, group in zip(spec["beats"], groups):
            effs = effect_times(group["effects"])
            movers = [e for e in effs if (e.get("duration_ms") or 0) > 50
                      and e.get("class") in ("entr", "emph", "path")]
            peak = 0
            for t in sorted({e["start"] for e in movers}):
                peak = max(peak, len([e for e in movers if e["start"] <= t < e["end"]]))
            beat["measured"] = {
                "effects": len(group["effects"]),
                "peak_movers": peak,
                "duration_ms": max((e["end"] for e in effs), default=0),
                "auto": group.get("auto", False),
            }
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "plan": str(PLAN),
        "slides": len(plan["slides"]),
        "beats": sum(len(s["beats"]) for s in plan["slides"]),
        "max_peak": max(b["measured"]["peak_movers"] for s in plan["slides"] for b in s["beats"]),
        "base_visible": {s["slide"]: len(s["base_visible"]) for s in plan["slides"]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
