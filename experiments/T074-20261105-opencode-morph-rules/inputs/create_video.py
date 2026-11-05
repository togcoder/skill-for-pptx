"""T074: export the matrix deck with PowerPoint CreateVideo at 2 s/slide."""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/T074-20261105-opencode-morph-rules"
SRC = EXP / "artifacts/morph-matrix.pptx"
TIMED = EXP / "artifacts/morph-matrix-timed.pptx"
MP4 = EXP / "preview/morph-matrix.mp4"
SECONDS = 2
FPS = 30
HEIGHT = 720

ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Open(str(SRC.resolve()), WithWindow=False)
    info = {"powerpoint": ppt.Version, "build": ppt.Build, "slides": pres.Slides.Count,
            "entry_effect": []}
    for i in range(1, pres.Slides.Count + 1):
        slide = pres.Slides(i)
        tr = slide.SlideShowTransition
        info["entry_effect"].append(int(tr.EntryEffect))
        tr.AdvanceOnTime = True
        tr.AdvanceTime = SECONDS
    pres.SaveAs(str(TIMED.resolve()))
    MP4.parent.mkdir(parents=True, exist_ok=True)
    pres.CreateVideo(str(MP4.resolve()), True, SECONDS, HEIGHT, FPS, 80)
    deadline = time.time() + 900
    status = None
    while time.time() < deadline:
        status = pres.CreateVideoStatus
        if status in (3, 4):
            break
        time.sleep(2)
    info["video_status"] = status
    info["mp4_bytes"] = MP4.stat().st_size if MP4.exists() else 0
    info["morph_slides"] = [i + 1 for i, e in enumerate(info["entry_effect"]) if e == 3954]
    (EXP / "preview").mkdir(parents=True, exist_ok=True)
    (EXP / "preview/create-video.json").write_text(
        json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps({k: info[k] for k in ("slides", "video_status", "mp4_bytes",
                                           "morph_slides")}, indent=1))
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass
