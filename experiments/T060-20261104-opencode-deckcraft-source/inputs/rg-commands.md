# Commands run (T060)

All paths are relative to the worktree root. `workspace/` is git-ignored; the
DeckCraft source and the PowerPoint video stay there and are not vendored.

## Freeze and inspect the source

```powershell
git clone --depth 1 https://github.com/storytold/deckcraft workspace/deckcraft-src
git -C workspace/deckcraft-src rev-parse HEAD
# 23ac4f7efdbd1e538bd9a7869584d4adeb9039b0
git -C workspace/deckcraft-src log -1 --format="%H%n%ad%n%s" --date=iso
# 2026-11-03 20:39:57 -0500  Fonts: bound font-controlled work ...

# Is there a command that plays animations?
git -C workspace/deckcraft-src grep -n "render-animation" HEAD          # no output
git -C workspace/deckcraft-src grep -n "render-transition" HEAD -- apps crates
rg -n "Timeline|AnimState|timeline\." workspace/deckcraft-src/crates --glob "*.rs"
rg -n "pub fn state|pub fn steps|step_duration|step_is_auto" workspace/deckcraft-src/crates/anim/src/timeline.rs
rg -n "ShapeState|RenderOpts" workspace/deckcraft-src/crates/render/src/opts.rs
rg -n "shape_state|state_for|render_frame" workspace/deckcraft-src/crates/ui-egui/src/show
rg -n "presetID|preset_id|repeatCount|autoRev|accel|decel" workspace/deckcraft-src/crates/pptx/src/read/timing.rs
```

## Preset comparison

```powershell
python experiments/T060-20261104-opencode-deckcraft-source/inputs/analyze_presets.py --src workspace/deckcraft-src
```

Reads `knowledge/powerpoint_presets.json` (198 PowerPoint-authored presets) and
`crates/model/src/anim.rs::ANIMATIONS` (107 DeckCraft entries). Writes
`preset-coverage.csv`, `preset-summary.json`, `table-conflicts.csv`.

## Forge `dynamic` deck

```powershell
python scripts/slide_forge.py build examples/pptx/forge/coffee_office_dynamic.json -o workspace/coffee_dynamic.pptx
python experiments/T060-20261104-opencode-deckcraft-source/inputs/inspect_dynamic_deck.py --pptx workspace/coffee_dynamic.pptx
```

The Forge build prints its own QA verdict (14 type sizes, MOT-SETTLE on slides
1 and 6); the deck is used as-is, not repaired, because T060 studies the file
that Forge produces.

## PowerPoint native parse and CreateVideo (rung 4/5)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/powerpoint_render.ps1 `
  -Pptx workspace/coffee_dynamic.pptx -OutDir workspace/ppt_render -SecondsPerSlide 8
# transient RPC_E_CALL_REJECTED on a cold COM start; the retry wrapper was used:
powershell -NoProfile -ExecutionPolicy Bypass -File workspace/ppt_render_retry.ps1 `
  -Pptx workspace/coffee_dynamic.pptx -OutDir workspace/ppt_render -SecondsPerSlide 6
```

`workspace/ppt_render/native_sequence.json` is PowerPoint's own
`Slide.TimeLine.MainSequence` dump (118 effects); the MP4 is 77.58 s at 720p.
The probe deck uses the same script with `-SecondsPerSlide 3`.

```powershell
ffmpeg -v error -i workspace/ppt_render/native_render.mp4 -vf fps=4,scale=320:180 workspace/video_frames/f%04d.png -y
ffmpeg -v error -ss 15.0 -i workspace/ppt_render/native_render.mp4 -frames:v 1 frame.png -y
```

## Prototype build and test

```powershell
cd workspace/deckcraft-src
cargo build -p deckcraft-cli            # 7m 16s cold, then ~8s incremental
cargo test -p deckcraft-anim            # 98 passed
cargo test -p deckcraft-cli --test it   # 20 passed
```

Lab gates (run from the lab root):

```powershell
python -X utf8 -m unittest discover -s tests   # 461 tests, OK, 8 skipped
python lab/tools/check_layout.py                # layout OK
```

First cold build needed network for the `storytold/egui` and
`storytold/craft-libs` git patches. A stale concurrent cargo invocation
reported `unresolved import deckcraft_anim`; rerunning after the lock cleared
built cleanly.

## The command under study

```powershell
$cli = "workspace/deckcraft-src/target/debug/deckcraft-cli.exe"
& $cli render-animation workspace/coffee_dynamic.pptx --slide 2 --plan
& $cli render-animation workspace/coffee_dynamic.pptx --slide 2 --click 2 `
    --t 0,250,500,750,1000,1500 --width 640 workspace/dc-kpi/c2.png
```

`--slide N` is 0-based (same as `render`/`render-transition`); `--click K`
counts main steps already played (`0` = as the slide appears); `--t` is
milliseconds into step `K` (step index `K`, so the first physical click is
`K = 1` when the deck has an automatic first step).

## Step-duration comparison

```powershell
python experiments/T060-20261104-opencode-deckcraft-source/inputs/compare_steps.py `
  --cli workspace/deckcraft-src/target/debug/deckcraft-cli.exe `
  --pptx workspace/coffee_dynamic.pptx `
  --native workspace/ppt_render/native_sequence.json
```

## Probe deck (repeat / autoRev / easing / path)

```powershell
python experiments/T060-20261104-opencode-deckcraft-source/inputs/make_probe.py
powershell -NoProfile -ExecutionPolicy Bypass -File workspace/ppt_render_retry.ps1 `
  -Pptx workspace/probe.pptx -OutDir workspace/ppt_probe -SecondsPerSlide 3
# DeckCraft model:
$cli run --in workspace/probe.pptx --print `
  --cmd 'slide.go={"index":1}' --cmd animation.get
# frames:
$cli render-animation workspace/probe.pptx --slide 1 --click 0 `
  --t 0,250,500,750,1000,1250,1500,1750,2000,2500,3000 --width 640 out.png
```

Probe effects: `ppt:spin` 1000 ms (no autoRev reached the file), native `pulse`
500 ms with `repeat=3` (the writer puts `repeatCount="3000"` and `autoRev="1"`
on the behaviour `cTn`), `ppt:fly` 800 ms with effect-level accel 0.3 / decel
0.7, and a custom `path` 1000 ms with accel 0.2 / decel 0.6.
