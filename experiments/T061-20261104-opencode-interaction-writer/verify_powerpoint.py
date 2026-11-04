#!/usr/bin/env python3
"""T061 — PowerPoint 16.0 COM parse check for the canonical interactive writer.

Builds a two-shape slide, writes one interactive trigger with
``pptx_animator.apply_timeline(trigger_spid=...)``, then asks PowerPoint what it
parsed. This is rung 4 (target-parsed): it proves PowerPoint accepts the
subtree and routes it to the trigger shape. It does NOT prove playback; that is
T058's click harness (rung 5/6).

A second deck reproduces the pre-T061 subtree (no onClick on the interactiveSeq
cTn, click step at delay="indefinite") so the report can say what a parse count
can and cannot distinguish.

    PYTHONUTF8=1 python experiments/T061-20261104-opencode-interaction-writer/verify_powerpoint.py

Writes artifacts/powerpoint_parse.json. Windows + PowerPoint only; exits 0 with
``{"ok": false, "reason": ...}`` when COM is unavailable.
"""
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_animator as anim  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.util import Inches  # noqa: E402

EXP = Path(__file__).resolve().parent
ARTIFACTS = EXP / "artifacts"
OUT = ARTIFACTS / "powerpoint_parse.json"
CANONICAL = ARTIFACTS / "t061_trigger_probe.pptx"
PRE_T061 = ARTIFACTS / "t061_trigger_probe_pre_t061.pptx"


def build_deck(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    button = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(3), Inches(1))
    button.name = "Inspect Button"
    button.text = "Inspect"
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5), Inches(1), Inches(4), Inches(3))
    panel.name = "Detail Panel"
    panel.text = "Detail"
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)


def _rewrite_slide(path: Path, mutate) -> dict:
    with zipfile.ZipFile(path) as zin:
        files = {name: zin.read(name) for name in zin.namelist()}
    root = E.fromstring(files["ppt/slides/slide1.xml"])
    shapes = anim.top_level_objects(root)
    by_name = {anim.shape_cnvpr(root, spid).get("name"): spid for spid in shapes}
    receipt = anim.apply_timeline(root, [{
        "id": "trig",
        "trigger_spid": by_name["Inspect Button"],
        "effects": [{"preset": "zoom", "spid": by_name["Detail Panel"],
                     "trigger": "click", "duration_ms": 500}],
    }])
    if mutate is not None:
        mutate(root)
    files["ppt/slides/slide1.xml"] = E.tostring(root, xml_declaration=True,
                                                encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    return {"receipt": receipt, "spids": by_name}


def degrade_to_pre_t061(root) -> None:
    """Rebuild the shape pptx_animator wrote before T061 (T049 1.3)."""
    ctn = root.find(".//p:cTn[@nodeType='interactiveSeq']", anim.NS)
    ctn.set("dur", "indefinite")
    for tag in ("p:stCondLst", "p:endSync"):
        node = ctn.find(tag, anim.NS)
        if node is not None:
            ctn.remove(node)
    step = ctn.find("p:childTnLst/p:par/p:cTn", anim.NS)
    st = step.find("p:stCondLst", anim.NS)
    for cond in list(st):
        st.remove(cond)
    E.SubElement(st, anim.q("cond"), delay="indefinite")
    cond = E.SubElement(st, anim.q("cond"), evt="onBegin", delay="0")
    E.SubElement(cond, anim.q("tn"), val=ctn.get("id"))


def probe(ppt, path: Path) -> dict:
    prs = ppt.Presentations.Open(str(path), ReadOnly=True, WithWindow=False)
    try:
        slide = prs.Slides(1)
        sequences = slide.TimeLine.InteractiveSequences
        result = {
            "ok": True,
            "interactive_sequences": sequences.Count,
            "main_sequence_effects": slide.TimeLine.MainSequence.Count,
            "effects": [],
        }
        for i in range(1, sequences.Count + 1):
            seq = sequences(i)
            for j in range(1, seq.Count + 1):
                eff = seq(j)
                result["effects"].append({
                    "trigger_shape": eff.Timing.TriggerShape.Name,
                    "target_shape": eff.Shape.Name,
                    "effect_type": eff.EffectType,
                    "duration_s": round(float(eff.Timing.Duration), 3),
                })
        return result
    finally:
        prs.Close()


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    build_deck(CANONICAL)
    canonical_written = _rewrite_slide(CANONICAL, None)
    build_deck(PRE_T061)
    legacy_written = _rewrite_slide(PRE_T061, degrade_to_pre_t061)
    payload = {
        "canonical": {"written": canonical_written, "path": CANONICAL.name},
        "pre_t061": {"written": legacy_written, "path": PRE_T061.name},
    }
    try:
        import win32com.client

        ppt = win32com.client.Dispatch("PowerPoint.Application")
        try:
            payload["canonical"]["parsed"] = probe(ppt, CANONICAL)
            payload["pre_t061"]["parsed"] = probe(ppt, PRE_T061)
        finally:
            ppt.Quit()
    except Exception as exc:  # COM unavailable on this host
        payload["canonical"]["parsed"] = {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}
        payload["pre_t061"]["parsed"] = {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload["canonical"]["parsed"], indent=2, ensure_ascii=False))
    print(json.dumps(payload["pre_t061"]["parsed"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
