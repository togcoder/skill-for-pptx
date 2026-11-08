"""T090 native evidence: open the shipped deck in desktop PowerPoint (COM) and
report what PowerPoint itself parsed -- slide count, transition entry effect per
slide (3954 = Morph, 3849 = Fade), transition duration, and click groups.

This is the rung-4 check (the target application parsed the exact file). Rung 5
is the CreateVideo render produced by ``scripts/powerpoint_render.ps1``.

    python inputs/verify_native.py artifacts/T090-triet-hoc-ch1.pptx -o artifacts/native_probe.json
"""
import argparse
import json
from pathlib import Path

MORPH = 3954
FADE = 3849


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    import win32com.client as win32

    deck = str(Path(args.deck).resolve())
    app = win32.Dispatch("PowerPoint.Application")
    was_open = app.Presentations.Count
    pres = app.Presentations.Open(deck, True, False, False)
    try:
        out = {"powerpoint": f"{app.Version} build {app.Build}", "deck": deck,
               "slides": []}
        for i in range(1, pres.Slides.Count + 1):
            slide = pres.Slides(i)
            tr = slide.SlideShowTransition
            out["slides"].append({
                "index": i,
                "entry_effect": int(tr.EntryEffect),
                "entry_is_morph": int(tr.EntryEffect) == MORPH,
                "entry_is_fade": int(tr.EntryEffect) == FADE,
                "duration_s": round(float(tr.Duration), 2),
                "effects": int(slide.TimeLine.MainSequence.Count),
            })
        pres.Close()
    finally:
        if not was_open:
            app.Quit()
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
