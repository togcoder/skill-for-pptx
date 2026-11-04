# T062 [pptx] Native asset factory: DeckCraft shapes vs SVG vs GLB

## Frame

- **Question.** For a PPTX-bound illustration that has to live inside a deck
  the Director will animate, which production route should Forge use —
  (A) DeckCraft shape commands producing native shapes, (B) one SVG picture
  (T053/T056), or (C) one GLB model (T055)? Measured on six axes: editability
  in PowerPoint, per-part targetability by the Director, file size, render
  diff, author effort, and the owner's eye test.
- **Hypothesis.** The native route wins editability and targetability, because
  in PowerPoint the object model *is* the shape list: a part that is a `p:sp`
  with a name can be selected, restyled and animated one part at a time. It
  should lose on author effort (there is no SVG import; every path is
  rebuilt from commands) and on effects PowerPoint applies at composite time
  (soft edges, glows). SVG should win author effort and lose identity; GLB
  should win depth and lose everything a Director needs.
- **Falsifier.** *After `convert`, the parts lose their identity, so the
  Director cannot target them* — names dropped, parts flattened into one
  shape, or animations lost. A second falsifier for the craft claim: the
  native render drifts further from the authored art than the SVG render
  does, so "native" buys identity by paying in fidelity.
- **Domain lens.** PresentationML's shape model (`p:sp`, `a:custGeom`,
  `a:effectLst`, `p:timing`), PowerPoint's object model through COM
  (`Shape.Name`, `TimeLine.MainSequence`), DeckCraft 0.13.1's command surface
  (Merge Shapes, Freeform, Effects, Animation), and the Director's identity
  rule in `domains/pptx/DOMAIN.md` ("never treat slide-local shape IDs as
  global identity" — a *name* contract is what makes a part addressable).
- **Transfers.**
  - From **T056 (vector)**: the part-table method — one table of named parts,
    one coordinate system, painter's order — is reused as the single source
    of truth for all three routes. That is what makes the comparison fair:
    the same 20 art parts are compiled three ways.
  - From **T055 (pptx 3D)**: `Shapes.Add3DModel`, the fixed camera and
    rotation properties, and the known material limits.
  - **Not imported:** T056's SVG-only painter's-order tricks (dash joins,
    `mix-blend-mode`) and T055's PBR material design. PowerPoint's light rig
    is fixed, so PBR tuning is not a property this route can carry.

## Frozen input

- **Task/claim:** T062 [pptx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T062-opencode-asset-factory`, base `ac5b45e` (`main` after T057).
  Brief: `experiments/T057-20261104-claude-leader-review/REPORT.md`,
  "Next research programme" → T062.
- **Request (2026-11-04):** "for a PPTX-bound illustration (icon set, badge,
  device mockup, product cut-out, diagram parts), compare three routes …
  Deliver a Forge `asset` spec, `{"native_art": …}`, compiled through
  DeckCraft commands on Windows and skipped with a coded error elsewhere.
  Falsifier: the parts lose their identity after `convert`."
- **Subject (chosen):** a **device mockup** — a handheld field terminal with a
  Q3 telemetry screen and a status badge. 26 parts: 20 art, 5 copy, 1 merge
  helper. It has the three things the routes differ on: flat parts that must
  stay separate (bars, badge ring, bolt), one merge (`ring − hole`), one
  freeform, and text that a 3D model cannot carry.
- **Environment:** Windows 10/11 x64; DeckCraft CLI **0.13.1**
  (`D:\artcraft\DeckCraft\deckcraft-cli.exe`); Microsoft PowerPoint **16.0**
  (COM); Python 3.13.5; python-pptx 1.0.2; Pillow 13.0.0; resvg_py; trimesh
  5.2.0; shapely 2.2.0; numpy 2.2.6. Design numbers read at build time from
  `knowledge/design_system.json` (v1.1.0) and the palette from
  `scripts/slide_forge.py` (`THEMES["midnight"]`), not hard-coded.
- **Could not access:** a human owner for the eye test (rung 6 is missing);
  an independent glTF renderer, so route C has no reference render of its own;
  a second PowerPoint build; Illustrator/Inkscape for a manual SVG round-trip.
- **Suite:** `python -m unittest discover -s tests` → 461 tests, OK, 8 skipped
  with `PYTHONUTF8=1`. Without it the Windows cp1258 locale makes 12
  pre-existing tests fail while decoding UTF-8 fixtures (`T005`, compound
  motion, script, textbox); none of them touch this task.
  `python lab/tools/check_layout.py` passes.

## Method

Run from the repository root (Windows, PowerPoint installed):

```powershell
python experiments/T062-20261104-opencode-asset-factory/inputs/run_experiment.py
```

That one command rebuilds every artifact below through these stages:

```powershell
# Route A - DeckCraft commands -> native shapes -> .deckcraft -> .pptx
python .../inputs/build_native_art.py .../inputs/native_art_spec.json --out <work>/native
deckcraft-cli render artifacts/field-terminal.pptx --all --scale 2 <work>/render

# Route B - same part table -> one SVG -> one picture (+ PNG fallback)
python .../inputs/build_svg_route.py .../inputs/native_art_spec.json <work>/svg

# Route C - same part table -> extruded prisms -> one GLB -> Add3DModel
python .../inputs/build_glb_route.py .../inputs/native_art_spec.json --out <work>/glb `
       --colour-scale 0.42 --frame-scale 1.0 --rot-y 0 --rot-x 0

# Evidence - OOXML + PowerPoint COM + render diffs
python .../inputs/verify_routes.py --spec ... --native ... --svg ... --glb ... --out artifacts
python .../inputs/make_sheet.py artifacts preview/compare-3up.png
```

Route A's compiler is three DeckCraft passes, because Merge Shapes re-ids its
result and DeckCraft does not error on a stale id:

1. create every part in z-order, rename it, set fill/line/effects
   (110 commands);
2. merge the badge ring (2 commands);
3. re-read `slide.inspect` for the **new** ids, then format text and add the
   animation sequence (116 commands). Total **228 commands**.

Structural facts the compiler had to absorb (all reproduced here):

| DeckCraft behaviour | Consequence |
|---|---|
| commands address shapes by numeric id only; `shape.insert` and `shape.merge` select their result | a compiler can name on creation, but any later command needs an id resolved from `slide.inspect` |
| `shape.merge` deletes the inputs and returns **new** ids, keeping the first shape's z and name slot | caching ids across a merge silently animates a ghost |
| `animation.add` on an id that no longer exists **succeeds** and is dropped at `convert` | first build produced 19 of 21 animations in PowerPoint; the fix is a re-inspect pass (now 21/21) |
| `shape.insert` writes a theme `<p:style>` | every unlined shape renders with a hairline until `shape.line {"none": true}` |
| `insert.textBox` autofits, so `rect` is not the final box | text needs `format.autofit none` + `format.margins 0` + `shape.setBounds` |

## Evidence

### The route comparison

One slide, one part table, three representations of the same 20 art parts.
"Addressable" = a PowerPoint shape with the part's name exists and can be
selected, restyled and animated by name.

| | **A native shapes** | **B one SVG picture** | **C one GLB model** |
|---|---|---|---|
| Command / build | 228 DeckCraft commands, 3 CLI passes | 1 SVG writer + 1 picture insert | extrude 13 prisms + `Add3DModel` |
| Build time (this box) | **0.95 s** | **0.82 s** | **3.66 s** (opens PowerPoint) |
| Author effort, this asset | 228 commands; 3 platform quirks found (merge re-id, theme hairline, text autofit) | 1 writer; no PowerPoint surprises | extrusion + camera tuning + a 0.42 colour fudge; 2 hard limits (text, soft shadow) |
| PowerPoint objects on the slide | 25 shapes (20 art + 5 copy) | 6 (1 picture + 5 copy) | 6 (1 model + 5 copy) |
| **Art parts addressable by name** | **20 / 20** | **0 / 20** | **0 / 20** |
| Per-part animation in the file | **21 effects, 20 movers, 4 clicks** | 0 | 0 |
| Editable operations | select, restyle, move, re-text, edit points, merge | crop, recolour, replace whole picture | camera, rotate, replace whole model |
| PPTX bytes | **25,126** | 101,678 | 223,995 |
| of which media | 0 | 80,593 PNG fallback + 2,464 SVG | 127,359 poster PNG + 60,956 GLB |
| Render vs its own reference | 0.23 % of pixels >24 | 0.31 % | no independent render |
| Render vs route A | — | 6.41 mean RGB, IoU 0.758 | 60.29 mean RGB, IoU 0.293 |
| Art bbox, measured silhouette (pt) | 277 × 408 | 294.5 × 450.5 | 275.5 × 419.5 |
| Lab design critic (`design_critic.py`) | **4.33** (design 3.0, motion 5.0, rhythm 5.0) | 3.0 (motion null, rhythm 1.0) | 3.0 (motion null, rhythm 1.0) |
| Owner eye test | see below | see below | see below |

Sources: `artifacts/route-evidence.json`, `artifacts/native-art-manifest.json`,
`preview/compare-3up.png`.

**Verdict.** Route **A** wins, and it is not close on the axis the task was
about: 20/20 parts addressable, 21 animations against 0, one quarter of route
B's bytes. Route B is the right fallback when the art is drawn elsewhere (or
the host is not Windows): it renders within 0.31 % of its own reference and
6.41 mean RGB of A, but it is one picture and can only be animated as one
object. Route C is not an illustration route for a deck: it costs 9× A's
bytes, drops 7 of 20 parts, washes the palette and cannot be turned to show
its depth without clipping. Ship A on Windows; fall back to B; keep C for
"rotate the real product" moments, not for infographics.

### What survives `convert` (the falsifier)

| Test | Result | Rung |
|---|---|---|
| 20 declared art parts still nameable after `convert` | **20/20**, each a separate `p:sp`, names byte-equal to the spec | 4 |
| Merged ring keeps a shape identity | yes, one shape named `art-badge-ring`, but it becomes `a:custGeom` (PowerPoint Type 5) and **gets a new id** | 4 |
| Freeform bolt keeps identity | yes, `art-badge-bolt`, Type 5, 6 vertices | 4 |
| Animations survive | 21/21 **after** re-resolving ids; 19/21 on the first build, silently | 4 |
| `convert` vs `run --save` agree | byte-identical PPTX (same SHA-256) | 1 |
| Rebuild is deterministic | two builds, same SHA-256 | 1 |

So the falsifier **does not hold for names** — the parts do keep their
identity and the Director can target them — but it **holds for object ids**:
identity in PowerPoint is a name, and any tool that treats a shape id as a
handle loses its target after a merge.

### Per-part animation, as PowerPoint sees it

The Director's view of route A, read back from `TimeLine.MainSequence`:
21 effects on 20 named movers, 4 click beats (4 `onClick`, 17
`withPrevious`), 5 effect kinds (fade ×7, wipe ×8, zoom ×3, float ×2,
pulse ×1). `p:timing` contains 80 `p:cTn` nodes. Routes B and C expose no
animatable parts: a picture and a model are one object each.

Design-system check: clicks 4 ≤ 6 ✓; effect kinds 5 ∈ [3, 10] ✓; effects per
click ≤ 7 ≤ 8 ✓; **movers per beat peaks at 7** — inside the hard limit (8)
but above the band (4). Kept deliberately: "the screen wakes" is one idea
built by seven concurrent parts, not seven ideas. Recorded rather than hidden.

### The owner eye test (builder judgement — rung 6 missing)

`preview/compare-3up.png` is the sheet for the owner. At 1:1 on a dark stage:

- **A** reads as the intended flat-vector device; the badge ring is a clean
  annulus, the glow is a soft halo, the shadow sits under the body, the
  in-screen type is live and crisp.
- **B** is nearly indistinguishable at deck scale (6.41 mean RGB over the art);
  the differences are craft-level: the SVG's baked glow is visibly stronger
  than PowerPoint's soft edge, and the shadow is darker. It is one picture.
- **C** is visibly a different rendering: the fixed light rig lifts every
  dark tone (the body's `#1E293B` measures `#3C4C6C` on a lit face), the soft
  shadow and the badge glow are gone, the five in-screen text parts are
  missing, and the phone reads as a plastic block. It is recognisable, not
  presentable next to A.

### DeckCraft capability matrix (for this asset)

| Capability | Verdict | Evidence |
|---|---|---|
| Round-rect / ellipse with real adjustment | works (`shape.adjust` → `a:avLst`) | `art-screen`, `art-notch` |
| Freeform polygon, closed and filled | works (`a:custGeom`) | `art-badge-bolt` |
| Merge Shapes (subtract) | works; **result is a freeform with a new id** | `art-badge-ring` |
| Named shapes → PowerPoint selection pane | works | 20/20 |
| Text boxes with font, size, bold, colour, tracking, line spacing | works, but needs select → format → autofit-off → bounds | 5 copy + 5 art text |
| Entrance/emphasis animation with `withPrevious`, delay, duration | works; 21/21 reach PowerPoint | `p:timing` |
| Shape effects: soft edges, transparency | works and is smooth (native composite) | `art-shadow`, `art-badge-glow` |
| 3D rotation of *one* shape to fake depth | not tested in this asset; `a:sp3d` is per shape, so a multi-part body cannot rotate as one | — |
| Export `.pptx` via `convert` | works, byte-stable, opens and exports in PowerPoint 16.0 (COM) without an error | rung 4/5 |
| Symbolic names in commands | **missing** — ids only | compiler joins on `slide.inspect` |
| Error on an unknown shape id | **missing** — silently dropped at convert | 19/21 first build |
| Import SVG / preserve SVG groups as shapes | **missing** — requires an extension | it is why route A costs 228 commands |
| 3D model: live text, soft shadows, any camera | **missing** | route C renders |

### Artifacts

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `artifacts/field-terminal.pptx` (A) | 25,126 | `d09720dc28a4af1a` |
| `artifacts/field-terminal.deckcraft` (A source) | 7,120 | `7953a5c92f5a7a77` |
| `artifacts/field-terminal-routeB.pptx` | 101,678 | `7c0bf87122ddece3` |
| `artifacts/field-terminal-art.svg` | 2,464 | `3ee5809a9590dcb8` |
| `artifacts/field-terminal-routeC.pptx` | 223,995 | `224f2cc0cca6efe6` |
| `artifacts/field-terminal-art.glb` | 53,052 | `30f466c6163ddbfa` |
| `artifacts/native-deckcraft-render.png` | 132,025 | `ed512b979c5c8ffe` |
| `artifacts/render-a.png` (PowerPoint) | 63,104 | `f49db5d30a3640a3` |
| `artifacts/render-b.png` | 86,486 | `7ef53dabc9716612` |
| `artifacts/render-c.png` | 152,000 | `9159a5d742418fac` |
| `artifacts/route-evidence.json` | 14,191 | `c7ad2519ec4e729e` |
| `artifacts/native-art-manifest.json` | 15,127 | `10097624ee4a04de` |
| `preview/compare-3up.png` | 197,724 | `895b9af37d0a781c` |
| `preview/route-c-rotated-clip.png` | 124,046 | `d964450b0392eba8` |

Total artifacts ≈ 1.2 MB (cap: 2 MB/file, 10 MB/task). Full hashes in
`artifacts/route-evidence.json`; commands in `inputs/commands/`. Route A's
files are stable across rebuilds; B and C are not (see limitations), so those
hashes belong to this build.

### The Forge spec proposal

`inputs/native_art_spec.json` is the reference instance. The field joins
Forge's existing `image` / `icon` / `chart` vocabulary as a sibling:

```json
{"slides": [{"layout": "statement",
  "native_art": {
    "compiler": "deckcraft",
    "stage": {"size": [960, 540], "theme": "midnight", "background": "bg"},
    "font": "Segoe UI",
    "parts": [
      {"name": "art-body", "role": "art", "kind": "roundRect",
       "rect": [596, 72, 186, 376], "radius_pt": 28, "fill": {"color": "surface"}},
      {"name": "art-badge-ring", "role": "art", "kind": "ellipse", "rect": [780, 40, 92, 92],
       "fill": {"color": "accent"}},
      {"name": "art-badge-bolt", "role": "art", "kind": "polygon",
       "polygon": [[834, 62], [812, 90], [824, 90], [818, 110], [840, 82], [828, 82]],
       "fill": {"color": "bg"}}
    ],
    "ops": [{"merge": {"op": "subtract", "ids": ["art-badge-ring", "art-badge-hole"], "name": "art-badge-ring"}}],
    "motion": [{"parts": ["art-body"], "effect": "float", "option": "d",
                "start": "withPrevious", "duration_ms": 500, "delay_ms": 120}]
  }}]}
```

Contract proposed to Forge:

- `parts[].role` ∈ `art | copy | helper | stage`. Only `art` counts as the
  asset, and only `art` is expected to be Director-addressable.
- `parts[].name` is the identity contract: `art-*` names are unique on the
  slide and travel into `p:cNvPr@name`.
- `kind` ∈ `rect | roundRect | ellipse | polygon | text`; `fill.color` is a
  theme role (`bg|surface|text|muted|accent|accent2`) or `RRGGBB`.
- `ops` are applied before `motion`; a merge re-ids, so consumers must
  re-read names, never ids.
- The compiler returns a **skip**, not an error, when the host cannot run it:

| Code | When | Forge behaviour |
|---|---|---|
| `SKIP_NATIVE_ART_PLATFORM` | not Windows | build the deck without the art, record the skip in the verdict |
| `SKIP_NATIVE_ART_NO_DECKCRAFT` | `deckcraft-cli` not found | same |
| `NATIVE_ART_COMPILE_FAILED` | a command failed | hard error with the failing command |

Verified here: on this box the first two return
`{"ok": false, "code": "SKIP_NATIVE_ART_PLATFORM"}` /
`…"SKIP_NATIVE_ART_NO_DECKCRAFT"` and `main()` exits 2 without writing a file.

## Negative results and limitations

- **The falsifier half-fired.** Names survive, ids do not. DeckCraft accepts
  an `animation.add` on a deleted id and only `convert` loses it, so the
  failure is silent: my first artifact had 2 of 21 animations missing and no
  warning anywhere. A compiler must re-inspect after every merge.
- **Native text inside the art is indistinguishable from slide copy to the
  deck-level critic.** `design_critic.py` on route A warns `TYP-SMALL`
  (most-used body 9 pt, smallest 7 pt) and `TYP-SIZES` (8 sizes) — but those
  sizes are the mockup's UI labels, not slide copy. Routes B and C hide the
  same labels behind one object and score clean. The native route therefore
  needs either an `art-*` exemption in the critic or alt-text `decorative`.
  This is a real cost of the route, not a bug in the art.
- **Movers per beat peaks at 7** (band 4, hard limit 8). Deliberate, but a
  reviewer may disagree; the sequence is 4 clicks and each click is one idea.
- **The native route cannot rotate its body in 3D.** `shape.effects.threeD`
  rotates each shape about its own centre, so a five-part device shears
  apart. Perspective has to be baked into the freeform coordinates, which is
  the same work the SVG route does. Only the bolt/ring could take a 3D effect
  and still look right.
- **Route B's soft glow is not the same effect.** resvg and PowerPoint both
  render the SVG faithfully (0.31 % delta to its own reference) but the baked
  Gaussian glow is brighter than PowerPoint's native soft edge, and an 8-bit
  alpha ramp over a large area bands. Forge should keep glows native even
  when the body is an SVG.
- **Route C's colour is not the palette.** The fixed light rig lifts the body
  from `#1E293B` to ≈ `#3C4C6C` (measured), and differently per face. I had to
  pre-multiply every base colour by 0.42 to land near the theme — a number
  that comes from trial, not from `design_system.json`, so it is not a
  design-system value. Without it the model is pastel.
- **Route C drops 7 of 20 parts**: 5 live-text parts (no glyph geometry), the
  soft shadow and the badge glow (no soft-alpha surface). The GLB keeps 13
  named meshes and 14 nodes, but PowerPoint exposes one shape, so those names
  are unreachable from the Director.
- **Route C clips at any Y rotation.** At `rotY = −12°` the badge was cut by
  the model's frame and the body ran off the bottom
  (`preview/route-c-rotated-clip.png`); the shipped route C therefore uses a
  front camera, where the 3D extrusion is invisible — the model is then a
  flat picture with worse colour. That is the honest best effort for this
  subject.
- **The silhouette IoU is colour-dependent.** Route A's dark body is within
  24 levels of the background, so a strict mask counts only the bright parts;
  route C's lifted body counts fully. IoU 0.293 therefore overstates the
  difference. The report leans on the mean RGB error over route A's dilated
  silhouette (60.29 vs 6.41) and on the near-identical art bboxes.
- **No rung 6.** The owner has not judged `preview/compare-3up.png`; the eye
  test above is the builder's. No claim of "mỹ mãn" is made.
- **Not tested:** groups as Director targets (a group is one animatable
  object with named children), Morph between two native assets, SmartArt, and
  DeckCraft's MCP surface. None of them changes the route ranking, but they
  are untested corners.
- **Byte stability:** route A rebuilds byte-identical; route B is
  content-identical but the zip container timestamps change; route C changes
  because PowerPoint rewrites the package on save. Record hashes, do not
  assert byte equality for B/C.

## Next

1. **Wire `native_art` into Forge behind a review.** The compiler is
   `EXPERIMENTAL` in `inputs/`; before it moves to `scripts/`, a reviewer
   must re-run the falsifier and the two skip codes. Sketch: `slide_forge.py`
   gains a `native_art` branch that calls the compiler, inserts the compiled
   slide's art shapes (or the whole compiled slide) and records
   `SKIP_NATIVE_ART_*` in the verdict.
2. **Feed the missing properties back to DeckCraft** (source domain, per
   `lab/standards/RESEARCH.md`): symbolic ids, an error on unknown ids,
   `merge` returning/keeping a stable id, an option to skip the theme
   `<p:style>` on insert, and a batch/session mode (228 commands cost 3
   process launches).
3. **Make the critic art-aware.** `design_critic.py` should skip shapes whose
   name starts with `art-` (or whose alt text is `decorative`) for type and
   density checks. Without it, every native illustration looks like a type
   violation and the route will keep losing reviews it should win.
4. **Retest with an icon set (8 small parts, no text).** 228 commands for one
   hero asset is acceptable; the same cost for a five-icon row is not.
   That test decides whether the route scales down or needs an SVG-to-shapes
   importer.
5. **Groups and Morph.** Put the 20 parts in one group to see whether the
   Director can still target children, and whether Morph interpolates named
   parts between two native assets — the only route that could make Morph
   shape-precise.

## Review response

Pending. No reviewer has accepted this report yet.
