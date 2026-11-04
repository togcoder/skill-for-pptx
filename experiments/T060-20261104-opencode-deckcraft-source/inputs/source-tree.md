# DeckCraft source tree notes (T060)

Frozen snapshot: `storytold/deckcraft` @
`23ac4f7efdbd1e538bd9a7869584d4adeb9039b0` (2026-11-03), workspace version
`0.15.0`, MIT OR Apache-2.0. Cloned with `--depth 1` into git-ignored
`workspace/deckcraft-src`; no source is vendored into this repository.

## Language and shape

Pure Rust Cargo workspace (`resolver = "3"`, edition 2024). 27 crates under
`crates/` plus `apps/deckcraft` (egui desktop), `apps/deckcraft-cli` (headless)
and `apps/deckcraft-web` (wasm). The animation path is split in two:

- `deckcraft-model` (`crates/model/src/anim.rs`) - the flattened
  `Animation` list and the `ANIMATIONS` gallery (107 entries: 24 entrance,
  23 exit, 17 emphasis, 40 path, 3 media).
- `deckcraft-anim` (`crates/anim`) - timing tree player, pure logic, no UI.
- `deckcraft-pptx` (`crates/pptx/src/read/timing.rs`, `write/timing.rs`) -
  PresentationML timing tree <-> the flat list.
- `deckcraft-render` (`crates/render`) - CPU renderer. `RenderOpts.state`
  already accepts per-shape `ShapeState`, so an animated frame is a normal
  slide render with a state closure.
- `deckcraft-ui-egui` (`crates/ui-egui/src/show/`, `canvas/preview.rs`) -
  the only caller that turns the timeline into frames today. GPU/egui path,
  private.

## The player (answers "does it exist?")

| File | What it does |
|---|---|
| `crates/anim/src/timeline.rs` | `Timeline::with` (line ~180) flattens `slide.animations` into click steps. `Timeline::state_ordered` (~485) composes per-shape `AnimState` at `(step, t)`. `status` (~560) decides NotStarted/Active/Done, applies `repeat`, `autoRev`, `rewind`, `after` (hide/dim). `steps`, `step_duration`, `step_is_auto`, `locate`, `start_of`. |
| `crates/anim/src/effects.rs` | `EffectSpec::eval` (~96): entrance/exit/emphasis/path evaluation. `entrance` (~119), `emphasis` (~253), `motion` (~311). `exit_base` maps exits onto their entrance mirror. |
| `crates/anim/src/easing.rs` | `ease(p, accel, decel, bounce)` (~8): PowerPoint's three-phase velocity ramp plus bounce; `bounce_out`, `smooth` (smoothstep). |
| `crates/anim/src/path.rs` | `MotionPath::parse` (~75): SVG-like `M/L/C/Q/H/V/Z/E` in slide fractions, arc-length parameterisation. `default_path` (~244) for named presets. |
| `crates/anim/src/show.rs` | `ShowState` (~52): click steps, hidden slides, custom shows, timings, `next` (~246) / `prev` / `goto` / `follow`. `ShowState::timeline` (~183) is the headless entry point. |
| `crates/anim/src/interact.rs` | Click hit-testing and triggered sequences (`TriggerPlay`, `StepStamp`). |
| `crates/ui-egui/src/show/render.rs` | `render_frame` (~51): the show's frame. Calls `state_for` and `deckcraft_render::render_slide` with `RenderOpts.state`. |
| `crates/ui-egui/src/canvas/preview.rs` | `shape_state` (~13): `AnimState` -> `render::ShapeState`, including paragraph states. This is the mapping a headless command needs. |

## PPTX timing reader (what reaches the player)

`crates/pptx/src/read/timing.rs::animations` (~237) walks `p:tnLst` and emits a
flat `Animation` per effect node:

- class from `presetClass`, effect from `effect_for_preset(class, presetID)`
  (`crates/pptx/src/maps.rs` ~365), fallback `fade`/`fadeOut`/`pulse`/
  `customPath`/`play` for unknown ids;
- start from `nodeType` (`clickEffect` / `afterEffect` / else with-previous);
- duration = max numeric `dur` under the effect node (`max_dur`);
- delay from the effect's `p:stCondLst/p:cond/@delay`;
- `repeatCount` from the **effect** `cTn` (`/1000`, `indefinite` -> `u32::MAX`);
- `autoRev` from the effect `cTn`, or from every behaviour `cBhvr/p:cTn` for
  non-Color-Pulse effects (`behaviour_auto_reverses`, ~200);
- `rewind` = effect `fill="remove"`;
- `accel` / `decel` / `bounceEnd` from the **effect** `cTn`;
- `animMotion/@path` as the motion path string;
- `animRot/@by` (spin amount), first `animScale/by` (grow amount),
  first `animClr/to` (colour emphasis);
- paragraph builds collapsed to one `TextBuild::ByParagraph` when every
  paragraph has the same effect/start.

The writer (`write/timing.rs::effect_par`, ~458) writes these attributes back on
the effect `cTn` and rebuilds click/after groups (`group`, `click_pars`).

## What does not exist

- `git grep render-animation HEAD` returns nothing. The CLI has 11 subcommands
  (`info render render-transition convert run commands describe app mcp bench
  links`); `render` draws the slide at rest, `render-transition` draws only the
  slide transition frames.
- `crates/engine/src/gif_export.rs` says so in its header: "Transitions and
  build animations are not animated: a slide appears as it looks when its
  builds have finished."
- No headless command creates a `Timeline` or passes `RenderOpts.state`.
- The show's frame path (`ui-egui/src/show/render.rs`) is private to the GUI
  crate and returns an egui `ColorImage`; it is not callable from the CLI.
- Triggered sequences are modelled (`interact.rs`) but not addressable by a
  CLI flag; `--click K` would only cover the main sequence.
- `ShowState::timeline` uses `Timeline::new`: default colour scheme and slide
  `xfrm`, not the deck theme/layout boxes. For generated Forge shapes (explicit
  `xfrm`) this is fine; placeholder-only decks may place text differently from
  the show. The GUI uses the same function, so a headless frame matches
  DeckCraft's own show, not necessarily PowerPoint.

## Prototype

`artifacts/proto-render-animation.patch` (137 lines, 7 files) adds:

- `render::shape_state(timeline, shape, step, t)`: the `AnimState` ->
  `ShapeState` mapping moved out of the GUI (including paragraph states).
- `deckcraft-cli render-animation FILE --slide N [--click K] [--t MS,...]
  [--plan] [--width PX] OUT.png`: build `ShowState::timeline`, check `K`, and
  render each frame with `RenderOpts.state`. `--plan` prints click steps and
  durations.
- CLI help page, subcommand list, one `deckcraft-anim` dependency.

It is `EXPERIMENTAL`, lives only in the clone, and is not proposed as a
finished upstream change.
