# T024 — Picture motion and motion-graphic intro (2026-10-07)

Owner report: with a short prompt, the AI made slides where only the text boxes
animated. Pictures never moved and there was no motion graphic.

## Cause (heuristic Director v0.1)

`draft_slide` in `scripts/motion_director.py`:

- skipped every picture below 8% of the slide;
- returned "single picture is the slide's content; kept static";
- kept title slides fully static;
- gave other pictures only a one-off Fade/Zoom entrance;
- skipped every text-free accent under 5% of the slide ("decorative").

SKILL.md also told the agent to leave decoration static, and nothing in the
recipe set gave a still picture motion after its entrance.

## Change

| Layer | Change |
|---|---|
| Writer `pptx_animator.py` | `repeat` (`indefinite` or count) and `auto_reverse` on the preset cTn (`repeatCount`, `autoRev`). Rejects loops that would jump each cycle and after-previous effects queued behind an endless loop. |
| Engine `motion_engine.py` | Recipes `ken-burns` (slow Grow/Shrink + drift path) and `float` (Until End of Slide bob). Simulates a loop as one auto-reversed cycle; reads `repeatCount`/`autoRev` back. Full-bleed backdrops are exempt from the off-slide warning. |
| Director draft | Hero pictures (backdrop ≥50%, or the only content) get `ken-burns` on slide start. Content pictures reveal, then `ken-burns` after-previous. Thin bars and lines (aspect ≥4:1, max 8 pieces) draw in at slide start, including on title slides. Pictures entering or leaving by Morph stay still. |
| Compile check | A later click may not move/scale/spin an object that is still looping. |
| Skill | Direction rules and recipe table updated. |

## Evidence

- Fixture `tests/fixtures/picture_deck.pptx` (generator
  `scripts/make_picture_deck_fixture.py`): text boxes + pictures + accent bars,
  no placeholders, no animation — the shape of a prompt-generated deck.
- `tests/test_picture_motion.py`: 12 tests. Full suite: **202 pass, 3 skipped**
  (`PYTHONUTF8=1 python -m unittest discover -s tests` on Windows; without
  UTF-8 mode, 11 older tests fail to read fixtures — pre-existing).
- Native: `native_probe.ps1` (now `scripts/powerpoint_render.ps1`) opened `picture_deck_motion.pptx` in **PowerPoint
  16.0 build 17932** (Windows 11), read the main sequence through the object
  model (`native/native_sequence.json`) and rendered an MP4 with
  `Presentation.CreateVideo` (9 s per slide, 720p).
  - PowerPoint parses every effect: Wipe (22), custom path (0), Grow/Shrink
    (59). The first slide effect is After Previous (auto start). The float
    loop has AutoReverse on and an indefinite repeat
    (`RepeatCount` reads back as −2147483648).
  - Pixel measurements on rendered frames:
    - Slide 1: the backdrop's right edge moves 930→964 px and its top edge
      144→126 px over 8 s.
    - Slide 2: the underline bobs y 134→128→134 px (amplitude 0.01 × 720 =
      7 px), so the loop plays.
    - Slide 3: the photo widens 868→904 px.
  - `native/contact_1fps.png`: one frame per second (rows = slides).

Limitations: CreateVideo is PowerPoint's own timeline renderer with clicks
auto-advanced. It is not an interactive slideshow, so presenter-click timing
and a click landing mid–Ken Burns (PowerPoint completes the running effect)
were not observed. The MP4 is not committed; rerun the probe to regenerate it.
Ken Burns scales the picture frame, not the crop, so a picture next to text
can grow over it. The occlusion warning catches this at stable states.

## Open-source references (checked 2026-10-07)

| Project | Licence | Takeaway |
|---|---|---|
| [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) (~58k★) | MIT | 203 PowerPoint-authored presets (53 entrance, 33 emphasis, 64 paths, 53 exit) plus repeat/auto-reverse/accel/decel. Best next source: port its preset table instead of hand-adding presets. |
| [atharva9167j/dom-to-pptx](https://github.com/atharva9167j/dom-to-pptx) | — | HTML→editable PPTX with native motion. A route for decks designed in HTML. |
| [presenton/presenton](https://github.com/presenton/presenton), [arcsin1/oh-my-ppt](https://github.com/arcsin1/oh-my-ppt) | — | Prompt→deck generators. Upstream of this Director, not motion engines. |
| [RythenGlyth/manim-pptx](https://github.com/RythenGlyth/manim-pptx) | — | Manim animation → PPTX as video. Raster fallback for true motion graphics; must be labelled non-native. |
| LibreOffice `sd/xml/effects.xml` | MPL-2.0 | Canonical XML for every PowerPoint preset; reference when adding presets. |

Next: port the ppt-master preset table (Fly In, Bounce, Teeter, Wave paths…)
and let `float`-style loops use emphasis presets. For a picture inside a
frame, try a crop-level Ken Burns via Morph between two crops.
