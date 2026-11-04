# T058 [pptx] — Interactive slide-show harness: automated clicks + capture

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), parallel programme T058–T065.
- **Date:** 2026-11-04. **Base:** `main` @ `ac5b45e`.
- **Branch:** `work/T058-opencode-interactive-harness`.
- **Status:** complete; review requested (critic per T057: Argon).
- **Deliverable:** `scripts/interactive_show_harness.py`,
  `tests/test_interactive_show_harness.py`, this experiment.
- **Evidence rung reached:** **5b** (COM-driven live playback, machine pixel
  assertions, captures not human-reviewed). **Not 6**, and
  `powerpoint_playback_verified` stays `false`.

## Frame

- **Question:** can an agent click shapes in a live PowerPoint slide show,
  capture the result, and assert that the pixels changed inside the shape's
  box — without a human at the keyboard?
- **Hypothesis:** yes, if the harness (a) finds the *windowed* show window
  (not the fullscreen one), (b) is per-monitor DPI aware before it reads any
  geometry, (c) maps slide points through the measured content rectangle, and
  (d) drives the real Win32 input path rather than `SlideShowView.GotoClick`.
- **Falsifiers:**
  1. The shell has no interactive desktop, so no show window can be reached.
  2. `GotoClick` fires `interactiveSeq` triggers, making Win32 input unnecessary.
  3. A Win32 click changes pixels but not inside the target box (mapping is wrong).
  4. The show window cannot be brought to the foreground or is covered.
- **Domain lens:** PowerPoint's native model. Window classes (`PPTFrameClass`,
  `screenClass`), `SlideShowWindow`/`SlideShowView`, `Slide.Export`,
  per-monitor DPI, Win32 input and `GetWindowRect`. No renderer other than
  PowerPoint is used.
- **Transfers from other domains:** none. This is a pptx-native mechanism; the
  pixel-diff metric is generic but is applied only to PowerPoint's own output.

## Frozen input

- **Request:** T057 brief, section *T058 [pptx] Interactive slide-show harness
  (rung 6 without a human)*: start windowed, find the show window, map slide
  points with DPI awareness, click trigger shapes, capture before/after, assert
  pixel change; apply to T049 games, T048b hub and T032 triggers; `GotoClick`
  must be a no-op for interactive sequences. If no interactive desktop exists,
  write the manual protocol and a negative result instead of faking.
- **Base commit:** `ac5b45e` (`T058-T065: claim the next research programme`).
- **Environment:**
  - Windows 11 `10.0.26300`, session 1, `WinSta0\Default`, input desktop
    openable.
  - Display 1920×1080 physical, **120 DPI (125 %)**; work area 1920×1020.
  - PowerPoint 16.0, build **17932**, COM automation;
    `Application.Name = Microsoft PowerPoint`,
    `Application.Path = C:\Program Files\Microsoft Office\Root\Office16`.
  - Python 3.13.5 (Anaconda), Pillow 13.0.0, pywin32 311.
  - Shell: OpenCode subagent on the owner's interactive desktop (shared with
    other agents).
- **Inputs (hashes):**

  | File | SHA-256 (first 16) | Bytes |
  |---|---|---|
  | `experiments/T049-…/artifacts/one_slide_games_suite.pptx` | `f91531f87e381fa2` | 46 080 |
  | `experiments/T048-…/artifacts/executive_interactive_hub.pptx` | `c924c3b7e373a013` | 35 336 |
  | `artifacts/t032_trigger_fixture.pptx` (built here) | `bb34276c4e3ae322` | 29 376 |
  | `artifacts/animator_trigger_fixture.pptx` (built here) | `930aab4897d69abd` | 29 310 |
  | `artifacts/t049_main_control.pptx` (built here) | `111effc1b7e06dd8` | 43 742 |

- **Could not access:**
  - A T032 showcase deck. Only `argon_showcase_native_sequence.json` is in the
    repo; the deck itself is not. The T032 test therefore uses a synthetic
    deck built with the T032-adopted writer.
  - A second interactive desktop. All runs share one desktop and one cursor.
  - A CI runner. This remains a local, desktop-session gate.

## Method

### 1. Desktop capability and DPI awareness

`enable_dpi_awareness()` calls `SetProcessDpiAwarenessContext(-4)`
(per-monitor v2), with `SetProcessDpiAwareness(2)` and `SetProcessDPIAware()`
fallbacks. It must run before any window call.

Measured in this shell:

| Reading | Before awareness | After awareness |
|---|---|---|
| `GetSystemMetrics(0,1)` | 1536×864 | **1920×1080** |
| `GetDpiForSystem()` | 96 | **120** |

The 1536×864 reading is exactly 1920×1080 ÷ 1.25. This is the mechanism behind
the earlier "screen 1536×864" reports. `SlideShowWindow.Width` is also in
points at 96 DPI: 864 pt × 120/72 = 1440 px, the measured window width.

`desktop_capability()` reports session, window station, desktop,
`OpenInputDesktop`, foreground window and screen metrics. A non-interactive
shell raises `INFRA_NO_INTERACTIVE_DESKTOP`; it never fabricates a pass.

### 2. Finding the show window

T057 searched `EnumWindows("screenClass")` and got `HWND = 0`. This is the root
cause: **`screenClass` is the fullscreen show window; a windowed show is
`PPTFrameClass`** with a title beginning `PowerPoint Slide Show -`.

Measured window classes:

| Show mode | Top-level class | Title |
|---|---|---|
| Windowed (`ShowType = 2`) | `PPTFrameClass` | `PowerPoint Slide Show - [deck.pptx [Read-Only]]:2 - PowerPoint Preview` |
| Fullscreen (`ShowType = 1`) | `screenClass` | `PowerPoint Slide Show - [deck.pptx]` |

`find_show_window(pid, deck_stem)` filters by PowerPoint PID **and** by class
and title, so another agent's show on the same desktop is never touched. It
polls for 12 s.

### 3. Placing the window and proving it is unobstructed

PowerPoint restores the windowed show wherever it last was; in one run it
overlapped the taskbar, and the capture contained the taskbar. The harness:

1. reads `MonitorFromWindow` + `GetMonitorInfo` (work area excludes the taskbar);
2. resizes the client to the slide aspect inside the work area with
   `SetWindowPos`;
3. samples 9 points with `WindowFromPoint`; the root window of every point must
   be the show window, otherwise `INFRA_WINDOW_OBSTRUCTED`.

Measured placement (T049 run): window `[100, 8, 1819, 1012]`, client
`[109, 46, 1810, 1003]` = 1701×957 (16:9), fully inside the 1920×1020 work area.

### 4. Mapping slide points to screen pixels

`predict_mapping()` aspect-fits the slide into the client and centres it.
`calibrate_mapping()` then aligns a `Slide.Export` of the current slide against
the captured client frame: a coarse search (step 4 px) followed by a 1 px
refinement over ±48 px, ignoring the scrollbar columns.

Measured calibration on every run: **shift (0, 0)**; MAE 0.684 (T049) to
11.86 (synthetic fixture) on a 0–255 scale. The result is recorded in
`mapping.calibration` in every evidence file.

Two traps this handles:

- PowerPoint can leave a `NUIScrollbar` child over the right edge; clicks that
  would land on it are refused (`TARGET_UNDER_SCROLLBAR`).
- The show can render at a zoom that is not the client fit (observed in an
  early synthetic run: 1701×957 client, ~1470×830 content). The calibration
  search measures the offset instead of assuming it.

### 5. Foreground and input

`force_foreground()` tries, in order: attach to the foreground thread +
`SetForegroundWindow`; topmost nudge; Alt-key nudge; attach to the target
thread. Each attempt also probes `SetCursorPos` so an input-denied desktop is
reported as `INFRA_INPUT_DENIED`. If no strategy wins but the window has a
title bar, the harness clicks the title bar (no slide hit) and rechecks.

This was necessary: in one run the foreground was a hidden
`HwndWrapper[OmApSvcBroker.exe…]` window, and plain `SetForegroundWindow`
failed three times.

Clicks are `SetCursorPos` + `mouse_event(LEFTDOWN/LEFTUP)`. Before each click
the harness re-checks the foreground and the obstruction. After the click it
polls frames until two consecutive ones differ by ≤ 0.03 % (≤ 3 s), so the
assertion is made on a settled state, not mid-animation.

Every capture goes through `guarded_capture()`: it re-acquires the foreground
if the show lost it, re-checks the 9-point obstruction and verifies that the
client rect has not moved by more than 1 px. This is not theoretical: in one
run `GotoClick` raised the PowerPoint editor above the show window, the
unguarded "after" frame contained the editor, and the diff reported a false
74 %. With the guard the same step is stable and reports 0.000 %.

### 6. Assertions

For a `pixel_change` step the harness computes, against the **client-local**
frame:

- `inside.pct_changed` — pixels in the target box whose max channel delta > 24;
- `share_inside` — changed pixels inside the box ÷ all changed pixels;
- `outside.pct_changed` — the control region.

Defaults: `inside ≥ 1 %`, `share_inside ≥ 0.6`, `outside ≤ 5 %`; plans can
override. A `slide_change` step polls `CurrentShowPosition` until it changes,
waits 700 ms, then asserts the exact target index. A `goto_click` step supports
`noop` (index and pixels must not move) and `main_advance` (index must move;
listed boxes must or must not change).

### 7. Commands

From the repository root, with `PYTHONUTF8=1`:

```powershell
# capability report (desktop, DPI, PowerPoint windows)
python scripts/interactive_show_harness.py probe

# build the synthetic fixtures (T032 writer, animator writer, T049 control)
python experiments/T058-20261104-opencode-interactive-harness/make_fixtures.py

# open-check: does PowerPoint accept the exact file?
python scripts/interactive_show_harness.py open-check `
  --deck experiments/T058-20261104-opencode-interactive-harness/artifacts/t032_trigger_fixture.pptx `
  --json-out experiments/T058-20261104-opencode-interactive-harness/artifacts/negatives/t032_trigger_fixture.open-check.json

# reproduce the T032 writer failure on the known-good T049 deck
python experiments/T058-20261104-opencode-interactive-harness/probe_t032_writer_on_t049.py
python scripts/interactive_show_harness.py open-check `
  --deck experiments/T058-20261104-opencode-interactive-harness/artifacts/negatives/t049_plus_t032_writer.pptx `
  --json-out experiments/T058-20261104-opencode-interactive-harness/artifacts/negatives/t049_plus_t032_writer.open-check.json

# the four interaction plans
python scripts/interactive_show_harness.py run --plan experiments/T058-20261104-opencode-interactive-harness/inputs/t049_slide1.json `
  --out experiments/T058-20261104-opencode-interactive-harness/artifacts/runs/t049_slide1
python scripts/interactive_show_harness.py run --plan experiments/T058-20261104-opencode-interactive-harness/inputs/t049_slide2.json `
  --out experiments/T058-20261104-opencode-interactive-harness/artifacts/runs/t049_slide2
python scripts/interactive_show_harness.py run --plan experiments/T058-20261104-opencode-interactive-harness/inputs/t048b_hub.json `
  --out experiments/T058-20261104-opencode-interactive-harness/artifacts/runs/t048b_hub
python scripts/interactive_show_harness.py run --plan experiments/T058-20261104-opencode-interactive-harness/inputs/t049_main_control.json `
  --out experiments/T058-20261104-opencode-interactive-harness/artifacts/runs/t049_main_control

# negative control: animator trigger that fires at slide load
python scripts/interactive_show_harness.py run --plan experiments/T058-20261104-opencode-interactive-harness/inputs/animator_trigger_bug.json `
  --out experiments/T058-20261104-opencode-interactive-harness/artifacts/runs/animator_trigger_bug

# aggregate + previews
python experiments/T058-20261104-opencode-interactive-harness/summarize.py
python experiments/T058-20261104-opencode-interactive-harness/make_previews.py

# tests
python -m unittest tests.test_interactive_show_harness -v
```

Exit codes: `0` all assertions passed; `2` assertion failed; `3` infrastructure
failure (no desktop, no show window, foreground/input denied); `4` harness
error. An infrastructure failure is never reported as a product pass.

## Evidence

All runs: PowerPoint 16.0 build 17932, show class `PPTFrameClass`, 120 DPI,
calibration shift (0, 0). `artifacts/evidence_summary.json` aggregates
**5 runs / 25 steps / 25 passed / 0 failed**.

| # | Claim | Rung | Evidence |
|---|---|---|---|
| 1 | A windowed show is found on this desktop; `screenClass` is only the fullscreen window | 5b | `artifacts/runs/t049_slide1/evidence.json`: `show.class = PPTFrameClass`, `show.hwnd ≠ 0`, `show.client_rect = [109,46,1810,1003]` |
| 2 | Per-monitor DPI awareness changes the visible screen from 1536×864 to 1920×1080 and makes the click coordinates physical | 5 | `artifacts/runs/*/evidence.json`: `dpi.system_dpi = 120`, `show.dpi = 120`; `probe` output |
| 3 | Slide→screen mapping is measured, not assumed: export/screen calibration at shift (0,0) | 5 | `mapping.calibration` in each evidence file: MAE 0.684–11.86, `shift_px [0,0]` |
| 4 | T049 game 1: clicking `Cover_1/2/3` fires the exit trigger and reveals the reward inside the cover box | **5b** | `runs/t049_slide1`: inside 100.0 / 100.0 / 99.998 %, share 0.978, outside 0.322 % |
| 5 | T049 game 1: the Reset button re-enters all three covers | **5b** | `runs/t049_slide1` step 5: inside 86.39 %, share 0.982, outside 1.25 % |
| 6 | T049 game 2: `Choice_B` reveals `Feedback_2`; Reset hides all feedback; `Choice_A` reveals `Feedback_1` | **5b** | `runs/t049_slide2`: 100 % / 29.09 % / 100 %, share 0.972 / 0.994 / 0.965 |
| 7 | `GotoClick(1)` is a no-op for interactive sequences: index stays 0, pixels 0.000 % | 5 | `runs/t049_slide1` step 1: `index 0->0, pixels 0.000%` |
| 8 | `GotoClick(1)` advances the main-sequence index **without rendering**: 0→1, pixels 0.000 % | 5 | `runs/t049_main_control` step 1: `rendered=False`, both boxes 0.0 % |
| 9 | Win32 trigger clicks are invisible to the COM click counter: after a successful cover click, `GetClickCount/Index` are still 0 | 5 | `runs/t049_slide1` steps 2–5: `observed.click_count = 0`, `click_index = 0` |
| 10 | T048b hub: all 9 navigation edges work, including the dynamic `lastslideviewed` return 5→3 | **5b** | `runs/t048b_hub`: 9/9 `slide N -> expected N`; preview `preview/t048b-navigation.png` |
| 11 | After a trigger was clicked once, the same deck still responds to a second click (Reset) | 5b | `runs/t049_slide1` step 5 |
| 12 | **T032 writer defect:** `interactive_triggers.apply_interactive_triggers` produces a file PowerPoint refuses to open | 4 (negative) | `artifacts/negatives/t032_trigger_fixture.open-check.json`: `opened: false`, COM `0x80004005`; reproduced on the known-good T049 deck: `artifacts/negatives/t049_plus_t032_writer.open-check.json` |
| 13 | **Animator trigger defect:** `pptx_animator.apply_timeline(trigger_spid=…)` writes an `interactiveSeq` without `p:stCondLst`; the exit runs at slide start and the click changes nothing | 5 (negative) | `runs/animator_trigger_bug`: click `whole 0.000 %`; the first frame already lacks `TargetCard`; `scripts/pptx_animator.py:550-557` |
| 14 | The harness passes its offline test suite | 1 | 36 tests OK, 2 skipped (`tests/test_interactive_show_harness.py`) |

Numbered artifacts:

- `artifacts/runs/t049_slide1/evidence.json` +
  `preview/t049-trigger-before-after.png`
- `artifacts/runs/t049_slide2/evidence.json`
- `artifacts/runs/t048b_hub/evidence.json` +
  `preview/t048b-navigation.png`
- `artifacts/runs/t049_main_control/evidence.json` +
  `preview/gotoclick-index-without-render.png`
- `artifacts/runs/animator_trigger_bug/evidence.json`
- `artifacts/negatives/*.open-check.json`
- `artifacts/fixtures.json`
- `artifacts/evidence_summary.json` (SHA-256 `4adaf8b8e2e9972f…`)

Every evidence JSON records: deck SHA-256, PowerPoint version/build, show
window rect/client rect, focus attempts, placement before/after, calibration,
per-step click point, target box in screen and frame coordinates, before/after
PNG hashes, diff stats, stability series, COM click state, and teardown.

## Negative results and limitations

1. **Rung 6 is not reached.** Machine assertions on saved frames are rung 5b.
   A person still has to look at the captures and confirm that the *right*
   thing appeared. The previews and per-step frames exist for that review.
2. **Pixel change is not semantic proof.** The assertion shows that pixels
   changed inside the predicted box and mostly nowhere else. It cannot tell a
   reward card from any other card of the same size. `share_inside` and the
   outside control reduce false positives; they do not eliminate them.
3. **One desktop, one cursor.** The harness moves the physical cursor and takes
   the foreground. Parallel agents on the same desktop can steal focus or
   overwrite a capture. The obstruction check fails loudly in that case, but
   two agents cannot click at the same time. Runs here were serialised.
4. **Windowed show startup is flaky.** During development
   `SlideShowSettings.Run()` sometimes returned without a show
   (`show_windows: 0`) or threw `0xe0000002`; the harness retries three times
   and creates a fresh COM instance after a failed session. All five final
   runs, however, started on attempt 0.
5. **`app.Quit()` does not terminate PowerPoint here.** In all five final runs
   the presentation closed and `Quit()` returned, but `POWERPNT.EXE` was still
   alive after 6 s and was terminated by PID (`killed_pid` in every teardown).
   Only the PID this session started is killed; other agents' `POWERPNT`
   processes are never touched, and `remaining_powerpnt_pids` is recorded.
6. **Calibration searches translation only** (±48 px at the predicted scale).
   A zoom change between calibration and a later slide would invalidate the
   mapping. Not observed in these runs; the content filled the client in all
   final runs.
7. **Z-order is part of correctness.** A COM call can raise the editor above
   the show window. Without `guarded_capture` the harness would have recorded a
   false positive/negative from whatever was behind the rect. The guard now
   turns that into an infrastructure error or a recovery.
8. **The T032 writer failure is not fully root-caused.** `interactive_triggers`
   output is rejected with a generic `0x80004005`. Adding `p:bldLst` and
   `prevCondLst`/`nextCondLst` did not fix it. The failure reproduces on the
   known-good T049 deck (`artifacts/negatives/t049_plus_t032_writer.pptx`), so
   it is not an artefact of the synthetic base deck. T061 should bisect the
   timing subtree. The same writer is reported as "adopted, unverified natively"
   in T032; it is worse than unverified: its output does not open.
9. **The animator defect is localised but not fixed here.** `pptx_animator.py`
   does write `interactiveSeq` (T057 says it writes none), but
   `_interactive_sequence` never adds the `p:stCondLst` `onClick` condition, so
   PowerPoint runs the effect at slide load. This contradicts the "canonical
   writer" assumption and is a direct input to T061.
10. **Fullscreen (`screenClass`) is implemented but not exercised.** All runs
    are windowed by design. `--fullscreen` exists; no evidence yet.
11. **The T032 showcase deck is missing.** The T032 test uses a synthetic deck
    built with the T032 writer, not the original Argon showcase.
12. **`Shape.Rotation` is recorded but not used.** A rotated trigger's true
    hit area differs from its unrotated bounding box; no rotated trigger was
    tested.
13. **Security.** COM opens the deck with `AutomationSecurity = 3` and
    `ReadOnly = True`. Running a show still executes hyperlinks/actions; this
    was done only on lab-owned decks.
14. **No Morph/CreateVideo coverage.** This task is about click-driven
    interactivity; motion frames remain T059/T060 territory.

## Next

1. **T061 (one canonical interaction writer):**
   - add the `p:stCondLst` `onClick` to `pptx_animator._interactive_sequence`;
   - bisect the `interactive_triggers.py` open failure and either fix or retire
     the module;
   - make T058's trigger fixture the acceptance test: PowerPoint opens it and
     the click changes the target box.
2. **Human review for rung 6:** inspect
   `artifacts/runs/*/frames/*-crop-*.png` and the three previews; record the
   review in `research/reviews/`.
3. **Wire the harness into the native QA gate** only on an interactive runner:
   infrastructure failures (`INFRA_*`) must not fail a product build, assertion
   failures must.
4. **Extend the plan language** with `expect: hidden_until_click` (compare the
   frame against the static `Slide.Export`) so entrance effects are asserted
   before they are clicked, and add `--fullscreen` evidence.
5. **Apply to the Director's spotlight decks** (T057 brief) and to Morph
   triggers once T060 has a frame player.
6. **Feed the T032/T061 findings into `docs/POWERPOINT_NATIVE_HARNESS.md`**:
   document `PPTFrameClass`, DPI awareness, the scrollbar overlay and the
   calibration step.

## Review response

| Finding | Response |
|---|---|
| Pending review by Argon (T057 table). | — |
