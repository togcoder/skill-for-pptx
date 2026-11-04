"""Render T069 in desktop PowerPoint and record what PowerPoint itself parsed."""
import json
import sys
from pathlib import Path

import win32com.client

ROOT = Path(r"C:\Users\COMPUTER\AppData\Local\Temp\opencode\skill-for-pptx-T069")
PPTX = ROOT / "experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx"
OUT = ROOT / "experiments/T069-20261104-opencode-directed-deck/preview"
OUT.mkdir(parents=True, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(str(PPTX), ReadOnly=True, WithWindow=False)
try:
    info = {
        "powerpoint_version": app.Version,
        "powerpoint_build": app.Build,
        "slides": [],
    }
    for slide in pres.Slides:
        effects = []
        for eff in slide.TimeLine.MainSequence:
            effects.append({
                "shape": eff.Shape.Name,
                "effect_type": int(eff.EffectType),
                "exit": int(eff.Exit),
                "trigger": int(eff.Timing.TriggerType),
                "duration_s": round(float(eff.Timing.Duration), 3),
            })
        info["slides"].append({
            "index": slide.SlideIndex,
            "effects": len(effects),
            "morph_transition": int(slide.SlideShowTransition.EntryEffect),
            "transition_duration_s": round(float(slide.SlideShowTransition.Duration), 3),
            "effect_list": effects,
        })
    (OUT / "native_verify.json").write_text(
        json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")

    pres.Export(str(OUT / "T069-directed-morph.pdf"), "PDF")
    for slide in pres.Slides:
        png = OUT / f"slide-{slide.SlideIndex:02d}.png"
        slide.Export(str(png), "PNG", 1280, 720)
    print(json.dumps({
        "slides": len(info["slides"]),
        "effects": sum(s["effects"] for s in info["slides"]),
        "morphs": sum(1 for s in info["slides"] if s["morph_transition"] == 3954),
        "morph_entry_effect": 3954,
        "entry_effects": [s["morph_transition"] for s in info["slides"]],
    }, indent=1))
finally:
    pres.Close()
    app.Quit()
