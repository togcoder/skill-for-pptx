"""T089 acceptance: rebuild a QCC-style theme deck and list every default that
used to be wrong. Prints a plain report; no JSON to the owner."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import motion_director as md
import slide_forge as sf
from pptx import Presentation

here = Path(__file__).resolve().parents[1]
spec = json.loads((here / "inputs" / "qcc-theme.json").read_text(encoding="utf-8"))
out = here / "artifacts" / "qcc-theme.pptx"
verdict = sf.build(spec, out)

print("build ok:", verdict["ok"])
print("errors:", [(e["code"], e.get("object")) for e in verdict["errors"]])
print("warnings:", [(w["code"], w.get("object"), w.get("detail")) for w in verdict["warnings"]])
print("metrics:", verdict["metrics"])

prs = Presentation(str(out))
names = [sh.name for slide in prs.slides for sh in slide.shapes]
print("decoration:", sorted({n for n in names if n.startswith("!!")}))
print("logo shapes:", [n for n in names if "logo" in n.lower()])
sizes = {}
for slide in prs.slides:
    for sh in slide.shapes:
        if sh.name in ("Major Heading", "Minor Heading", "Hero Title", "TopRight Title") and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        sizes.setdefault(sh.name, set()).add(r.font.size.pt)
print("card title sizes:", sizes)

model = md.deck_model(here / "artifacts" / "qcc-theme.static.pptx")
plan = md.draft(model, style="modern", morph=True)
for s in plan["slides"][:2]:
    first = next(b for b in s["beats"] if b["id"] == s["click_beats"][0]["motion_beats"][0])
    print(f"slide {s['source_index']}: {len(s['click_beats'])} click group(s), first beat {first['timing_intent']}")
print("morph transitions:", verdict["metrics"]["morph_transitions"])
