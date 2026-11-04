#!/usr/bin/env python3
"""Export a short video of the Morph deck so the transition can be inspected."""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
SRC = ART / "morph-3d.pptx"
TIMED = ART / "morph-3d-timed.pptx"
MP4 = PREVIEW / "morph-3d.mp4"

info = {}
ppt = pres = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    ppt.Visible = 1
    pres = ppt.Presentations.Open(str(SRC.resolve()), WithWindow=False)
    for i in range(1, pres.Slides.Count + 1):
        tr = pres.Slides(i).SlideShowTransition
        tr.AdvanceOnTime = True
        tr.AdvanceTime = 3
        info[f"advance_{i}"] = [tr.AdvanceOnTime, tr.AdvanceTime]
    pres.SaveAs(str(TIMED.resolve()))
    pres.CreateVideo(str(MP4.resolve()), 3, 3, 30, 85)
    deadline = time.time() + 300
    status = None
    while time.time() < deadline:
        status = pres.CreateVideoStatus
        if status in (3, 4):  # 3 = done, 4 = failed
            break
        time.sleep(2)
    info["create_video_status"] = status
    info["mp4"] = str(MP4)
    info["exists"] = MP4.exists()
    info["bytes"] = MP4.stat().st_size if MP4.exists() else 0
finally:
    if pres is not None:
        try: pres.Close()
        except Exception: pass
    if ppt is not None:
        try: ppt.Quit()
        except Exception: pass

(PREVIEW / "morph-video.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
print(json.dumps(info, indent=2))
