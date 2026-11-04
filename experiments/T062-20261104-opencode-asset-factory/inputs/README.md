# T062 inputs — the native-art compiler and its three routes

All files here are **EXPERIMENTAL** (T062, unreviewed). Nothing is imported by
`scripts/` or wired into Forge; see the REPORT's "Next" section for the review
gate that has to pass first.

| File | What it is |
|---|---|
| `native_art_spec.json` | The frozen input: the Forge `asset` spec proposal, one part table for all three routes. |
| `build_native_art.py` | Route A. Compiles `{"native_art": …}` to DeckCraft commands, runs `deckcraft-cli`, writes `.deckcraft` + `.pptx` + a manifest. Raises `NativeArtUnavailable` with `SKIP_NATIVE_ART_PLATFORM` / `SKIP_NATIVE_ART_NO_DECKCRAFT` off Windows. |
| `route_stage.py` | The shared stage (background + native copy) that routes B and C add their art to. |
| `build_svg_route.py` | Route B. Same part table → one SVG → one picture (SVG blip + PNG fallback, the Slide Forge icon pattern). |
| `build_glb_route.py` | Route C. Same part table → extruded prisms → one GLB → `Shapes.Add3DModel`. |
| `verify_routes.py` | Opens each PPTX in PowerPoint, records shapes/animations, exports PNG, computes the render metrics. |
| `make_sheet.py` | 3-up review sheet for the owner eye test. |
| `run_experiment.py` | Rebuilds everything in order into `artifacts/` and `preview/`. |
| `commands/` | The 228 DeckCraft commands route A actually ran, one per line. |

## Run it

```powershell
# whole experiment (Windows, PowerPoint, deckcraft-cli)
python experiments/T062-20261104-opencode-asset-factory/inputs/run_experiment.py

# just the platform contract
python experiments/T062-20261104-opencode-asset-factory/inputs/build_native_art.py --check

# just the commands, no deckcraft run
python .../build_native_art.py .../native_art_spec.json --out /tmp/x --emit-only
```

`--check` prints `{"ok": true, "cli": "...", ...}` on Windows and
`{"ok": false, "code": "SKIP_NATIVE_ART_PLATFORM" | "SKIP_NATIVE_ART_NO_DECKCRAFT"}`
elsewhere. `compile_spec()` raises the same codes, so a caller can skip the
art instead of failing the deck.

## The spec, in one paragraph

`asset.native_art.parts[]` are named parts in z-order. `role` is
`art | copy | helper | stage`; `kind` is `rect | roundRect | ellipse | polygon |
text`; geometry is slide points on a 960×540 stage; `fill.color` is a theme
role (`bg|surface|text|muted|accent|accent2`) or `RRGGBB`. `ops` run before
`motion` (a merge re-ids its result, so consumers must re-read names).
`motion[]` is `{parts, effect, option?, start?, duration_ms, delay_ms?}` and
its durations are checked against `knowledge/design_system.json` bands.

The palette comes from `scripts/slide_forge.py` (`THEMES`) and the motion
durations from the design system — this directory holds no second copy of
either.

## Known sharp edges (all reproduced in the REPORT)

- Merge Shapes re-ids the result; DeckCraft accepts an `animation.add` on the
  dead id and drops it at `convert` without a warning. The compiler merges
  first, re-inspects, then animates.
- `shape.insert` writes a theme `<p:style>`, so every shape needs an explicit
  `shape.line {"none": true}` or it renders with a hairline.
- Text boxes autofit: `format.autofit none` + `format.margins 0` +
  `shape.setBounds` are needed for the authored box.
- Route C needs base colours pre-multiplied by ≈0.42 to survive PowerPoint's
  fixed light rig, and has no live text or soft shadows.
