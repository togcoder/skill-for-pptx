# Build and evidence log (T060)

## Environment

- Windows 11, PowerShell 5.1 / 7 shell.
- Rust 1.99.1 (`cargo 1.99.1`), edition 2024 workspace.
- Python 3.13 (miniconda), lxml, Pillow, matplotlib 3.10.6.
- PowerPoint 16.0, build 17932 (COM).
- ffmpeg 8.1.1.
- Local DeckCraft CLI 0.13.1 was present but **all frames and model checks here
  use the CLI built from source at 23ac4f7** (`target/debug/deckcraft-cli.exe`,
  report version 0.15.0).

## Frozen files and hashes (SHA-256)

| File | Bytes | SHA-256 |
|---|---|---|
| `inputs/coffee_dynamic.pptx` | 636,542 | `2d0d9798d31784416311a62b39c802f227623c6c174f3b361111452105f4d3b3` |
| `inputs/probe.pptx` | 32,900 | `33b81dd442fbb550fedee8af6a48d6538eb22cb990100ebb20430d1b0131bffb` |
| `inputs/powerpoint-native-sequence.json` | 80,790 | `2514a0841f03142f6b9f333748faffc7701bbbde213b185ae5ad1205fad767c2` |
| PowerPoint CreateVideo (workspace only) | 5,827,681 | `a5d16ee6a0cf6ead7a54a89a529732e92c2f847a81d4f3e02ebfd008de3932a0` |
| `artifacts/proto-render-animation.patch` | 21,654 | `205ea19ec3d1a76a800bb7ff3a565722fb7d5289b452bf5c9d11c7108f14052f` |
| `artifacts/compare-powerpoint-kpi-15-22s.png` | 120,548 | `f8cf238b82d36e60a96d8e7b1bf8db145de57fff5a8912507bd144ae96edef6e` |

The MP4 is 77.58 s, 1280×720, 30 fps, and is **not** committed (size; it can
be regenerated with the command in `rg-commands.md`). CreateVideo was run with
`SecondsPerSlide = 6`; the result gives each slide 7.5–10 s because PowerPoint
adds the build time.

## Forge build

```
python scripts/slide_forge.py build examples/pptx/forge/coffee_office_dynamic.json -o workspace/coffee_dynamic.pptx
```

The build printed its QA report: 10 slides, 14 type sizes (band 3–6),
`MOT-SETTLE` on slides 1 and 6, and no coded build error. The deck was not
repaired: T060 studies the file Forge actually emits.

## Prototype

Patch: `artifacts/proto-render-animation.patch`.

```
cargo build -p deckcraft-cli            # cold 7m 16s; incremental 6–9 s
cargo test -p deckcraft-anim            # 98 passed
cargo test -p deckcraft-cli --test it   # 20 passed after the patch
```

Lab tests (T060 does not change Python code):

```
python -X utf8 -m unittest discover -s tests   # 461 tests, OK, 8 skipped, 22.6 s
python lab/tools/check_layout.py                # layout OK
```

Without `-X utf8`, this machine's Python locale (cp1258) makes 12 existing tests
fail while decoding UTF-8 fixtures from other experiments (`test_choreography`,
`test_compound_motion`, `test_textbox_normalization`, `test_layers_and_script`).
That is a pre-existing Windows/locale issue, not a T060 change; the same suite
passes in UTF-8 mode.

The cold build printed "building without craft-fonts" (the sibling
`../craft-fonts` checkout is absent), which changes font fallback but not the
timing model. The first background build raced a second cargo invocation and
reported `unresolved import deckcraft_anim`; a clean rerun built.

## Commands that produced the frames

```
deckcraft-cli render-animation workspace/coffee_dynamic.pptx --slide 2 --plan
deckcraft-cli render-animation workspace/coffee_dynamic.pptx --slide 2 \
    --click 2 --t 0,250,500,750,1000,1500 --width 640 workspace/dc-kpi/c2.png
```

`--plan` on slide index 2 (the KPI slide) prints:

```
slide 2: 5 main steps
  step 0: auto  250ms, 1 effects
  step 1: click 800ms, 19 effects
  step 2: click 1001ms, 25 effects
  step 3: click 660ms, 3 effects
  step 4: click 600ms, 1 effects
```

## PowerPoint native parse

`inputs/powerpoint-native-sequence.json` is the raw dump of
`Slide.TimeLine.MainSequence` for the 10 slides (118 effects). Per-effect
comparison against the built deck's XML:

- 118/118 effects match PowerPoint's trigger type (`on click` / `with previous`
  / `after previous`).
- 118/118 match PowerPoint's duration (within 2 ms), except 12 persistent
  `style.opacity` states that PowerPoint reports as infinite; DeckCraft models
  them as 0 ms "done" states, which is what they show.
- Step counts: 37 in both (Per slide: 1,1,5,3,6,5,7,3,3,3).

## Probe deck

Built by `inputs/make_probe.py` with the lab's `pptx_animator`. Effects:

| Slide | Effect | Timing feature |
|---|---|---|
| 1 | `ppt:spin`, 1000 ms | auto-reverse / repeat requested but the lab writer put neither into the file; PowerPoint and DeckCraft both see none |
| 2 | native `pulse`, 500 ms, `repeat=3` | writer emits `repeatCount="3000"` and `autoRev="1"` on the **behaviour** `cTn` |
| 3 | `ppt:fly`, 800 ms, accel 0.3 / decel 0.7 | effect-level easing |
| 4 | custom path 0.25 slide right, 1000 ms, accel 0.2 / decel 0.6 | motion path + effect-level easing |

DeckCraft `animation.get` on slide 2 returns `durationMs: 500`, `repeat: 1`,
`autoReverse: true`. PowerPoint reports total duration 3.000 s; the
CreateVideo frames keep pulsing for the whole 3 s. DeckCraft's rendered frames
are static after 1 s. This is the one hard timing divergence found.

On slide 4, with the PowerPoint animation start fitted to the nearest 30 fps
frame (8.7 s + 0.36 s), the shape centre differs by at most
0.0078 slide widths (10 px at 1280) from DeckCraft across the 1 s path.
Endpoints are identical. See `inputs/path-positions.csv`.

## Caveats

- CreateVideo does not expose click timestamps. The KPI strips are aligned by
  scene inspection, not by a recorded click clock; they are qualitative
  evidence, not a pixel diff.
- PowerPoint's `Effect.Timing` reports per-effect duration, not a click-group
  duration. The step-duration comparison in `inputs/step-durations.csv` uses a
  flat "max(delay+duration) per click group" model, so six after-previous
  chains show DeckCraft as longer; those are the correct sequential sums
  (700+700, 300+450, 700+6000). Only the two −1 ms pairs are rounding.
- The probe's `ppt:spin` row is not a DeckCraft test: the lab writer did not
  write auto-reverse/repeat for a library preset. The `pulse` row is the real
  behaviour-level repeat test.
