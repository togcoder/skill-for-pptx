#!/usr/bin/env python3
"""T064: export the two probe decks with PowerPoint CreateVideo (rung 5).

The earlier T055 attempt passed CreateVideo's arguments in the wrong order:
(T055) pres.CreateVideo(path, 3, 3, 30, 85)
maps to UseTimingsAndNarrations=3, DefaultSlideDuration=3, VertResolution=30,
FramesPerSecond=85 -- a 30-pixel-tall video. The documented order used here is
(FileName, UseTimingsAndNarrations, DefaultSlideDuration, VertResolution,
FramesPerSecond, Quality), as in scripts/powerpoint_render.ps1.

Run:  python experiments/T064-.../inputs/create_video.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"

DECKS = {
    "morph": ART / "camera-morph.pptx",
    "fade": ART / "camera-fade.pptx",
    "shared": ART / "camera-morph-shared.pptx",
    "modelonly": ART / "camera-morph-modelonly.pptx",
    "dup": ART / "camera-morph-duplicated.pptx",
}
SECONDS_PER_SLIDE = 4
VERT_RESOLUTION = 1080
FPS = 30
QUALITY = 95


def export(key: str, src: Path) -> dict:
    timed = ART / f"camera-{key}-timed.pptx"
    mp4 = PREVIEW / f"camera-{key}.mp4"
    for stale in (timed, mp4):
        stale.unlink(missing_ok=True)
    info = {"source": str(src), "mp4": str(mp4)}
    ppt = pres = None
    try:
        ppt = win32.DispatchEx("PowerPoint.Application")
        ppt.Visible = 1
        pres = ppt.Presentations.Open(str(src.resolve()), WithWindow=False)
        info["slide_count"] = pres.Slides.Count
        info["entry_effect"] = []
        info["advance"] = []
        for i in range(1, pres.Slides.Count + 1):
            slide = pres.Slides(i)
            tr = slide.SlideShowTransition
            info["entry_effect"].append(int(tr.EntryEffect))
            tr.AdvanceOnTime = True
            tr.AdvanceTime = SECONDS_PER_SLIDE
            info["advance"].append([bool(tr.AdvanceOnTime), float(tr.AdvanceTime)])
        pres.SaveAs(str(timed.resolve()))
        pres.CreateVideo(str(mp4.resolve()), True, SECONDS_PER_SLIDE,
                         VERT_RESOLUTION, FPS, QUALITY)
        deadline = time.time() + 600
        status = None
        while time.time() < deadline:
            status = pres.CreateVideoStatus
            if status in (3, 4):  # 3 done, 4 failed
                break
            time.sleep(2)
        info["create_video_status"] = status
        info["mp4_bytes"] = mp4.stat().st_size if mp4.exists() else 0
    finally:
        if pres is not None:
            try: pres.Close()
            except Exception: pass
        if ppt is not None:
            try: ppt.Quit()
            except Exception: pass
    return info


def probe(mp4: Path) -> dict:
    import subprocess
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,avg_frame_rate,nb_frames",
         "-show_entries", "format=duration", "-of", "json", str(mp4)],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main() -> dict:
    import sys
    keys = [a for a in sys.argv[1:] if a in DECKS] or list(DECKS)
    info = {"params": {"seconds_per_slide": SECONDS_PER_SLIDE,
                       "vert_resolution": VERT_RESOLUTION, "fps": FPS,
                       "quality": QUALITY}, "decks": {}}
    for key in keys:
        rec = export(key, DECKS[key])
        rec["ffprobe"] = probe(Path(rec["mp4"]))
        info["decks"][key] = rec
    out = PREVIEW / "create-video.json"
    if out.exists():
        old = json.loads(out.read_text(encoding="utf-8"))
        old["decks"].update(info["decks"])
        old["params"] = info["params"]
        info = old
    out.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    main()
