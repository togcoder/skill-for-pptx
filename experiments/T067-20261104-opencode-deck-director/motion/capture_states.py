#!/usr/bin/env python3
"""Capture PowerPoint stable states for one slide (T067 evidence tool).

Usage:
  python motion/capture_states.py DECK.pptx OUT_DIR SLIDE CLICKS [PREFIX] [--windowed]

Fullscreen is the default (clean 1920x1080, no window chrome). `--windowed`
keeps the show in a window; the capture then includes PowerPoint's title bar
and scrollbar, which is useful when the desktop is shared.

The show is driven with `SlideShowView.Next()` rather than `GotoClick`:
T058 measured that GotoClick advances the click index but does not repaint.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import interactive_show_harness as h  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("out")
    ap.add_argument("slide", type=int)
    ap.add_argument("clicks", type=int)
    ap.add_argument("prefix", nargs="?", default="")
    ap.add_argument("--windowed", action="store_true")
    args = ap.parse_args()

    deck = Path(args.deck).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or f"s{args.slide:02d}"

    h.enable_dpi_awareness()
    h._user32.SetCursorPos(4, 4)
    time.sleep(0.2)
    session = h.ShowSession(deck, windowed=args.windowed, place_window=args.windowed)
    info = session.start()
    print("opened", {k: info[k] for k in ("slide_count", "pid", "version", "build")})
    try:
        session.goto_slide(args.slide)
        time.sleep(2.5)

        def shot(path: Path) -> None:
            if args.windowed:
                rect = h.window_rect(session.hwnd)
            else:
                rect = h.Rect(0, 0, 1920, 1080)
            h.capture_rect(rect).save(path)

        shot(out / f"{prefix}-00-base.png")
        print("base", session.click_index(), session.click_count())
        for k in range(1, args.clicks + 1):
            session.view.Next()
            time.sleep(1.4)
            shot(out / f"{prefix}-{k:02d}-click{k}.png")
            print("click", k, session.click_index(), session.click_count(),
                  session.current_slide())
    finally:
        print("closed", session.close())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
