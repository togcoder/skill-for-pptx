# T053 [vector] — Semantic 2.5D reconstruction (supersedes the T051 edge trace)

## Frame

- **Question:** T051 was rejected. It extracted Canny edges and called the result
  a vector illustration; the owner saw "crude parameter lines", not a
  reconstruction. What does a real reconstruction require?
- **Hypothesis:** a product drawing must be a **model**, not a filtered photo:
  one projection, a part inventory, boxes/cylinders/plates in object
  coordinates, visible faces painted back-to-front, and materials chosen by a
  designer. Falsifiers: any Canny/edge-trace input; pixel coordinates used as
  geometry; parts that cannot be moved by changing a dimension; a group head
  that reads as a camera lens; a logo traced as a scribble.
- **Domain lens:** SVG 2.0, axonometric projection, technical product
  illustration, box/cylinder/plate primitives, painter's order, vector-native
  gradients and type.
- **Transfers:** the CC0 photo is the reference; the SVG is drawn with Python
  primitives and rendered/inspected by **VectorCraft**. No raster underlay, no
  generative image, no traced pixels.

## Frozen input

- **Task/claim:** T053 [vector], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T053-opencode-vector-reconstruction`, based on `main` (`b295d89`).
- **Request/date:** 2026-11-02; the owner paused Word/Excel and said the vector
  result was not acceptable: "you are only carelessly extracting edges from the
  source photo".
- **Source photo:** Wikimedia Commons, *File:Quick Mill Omre Espresso
  Machine.jpg*, **CC0**, 1531 × 1808 px.
  `https://commons.wikimedia.org/wiki/File:Quick_Mill_Omre_Espresso_Machine.jpg`,
  accessed 2026-11-02. Kept locally only as a reference.
- **Manual measurements (object units, width × height × depth):**
  base 104 × 7 × 74; lower body 94 × 35 × 69; tower 94 × 50 × 69; top panel
  92 × 4 × 63; drip tray 94 × 5 × 46; group head boss radius 12.5 × 11 deep;
  portafilter handle radius 5.6 → 4.8, 40 long; knobs radius 6.4 × 10 tall.
  These are proportions read from the photo, not a survey.
- **Environment:** Windows 10/11 x64; Python 3.13; VectorCraft
  `vectorcraft-cli.exe` (ArtCraft); no Illustrator/Inkscape run.
- **Could not access:** a second view of the machine; a measured drawing; a
  physical print; a human preference test.

## Method

```powershell
python experiments/T053-.../inputs/build_quickmill.py
vectorcraft-cli convert artifacts/quickmill-reconstruction.svg preview/quickmill-reconstruction.png --scale 2
vectorcraft-cli info artifacts/quickmill-reconstruction.svg
python experiments/T053-.../inputs/make_compare.py
python -m unittest tests.test_vector_reconstruct -v
```

1. **One projection.** Object coordinates: `x` width, `y` height, `z` depth.
   ```
   X = 400 + 4.6·x − 2.05·z
   Y = 900 − 5.5·y − 1.35·z
   ```
   The vertical scale is stretched to match the tall machine; front-plane
   circles are compensated (`ry = r·sx/sy`) so they stay round on screen.
2. **Part inventory.** Fourteen object parts were named before drawing: feet,
   base, lower body, tower, top panel, cup rails, drip tray, side panel, group
   head, portafilter, steam wand, top knobs, badge, controls. With the shadow
   and the highlight layer that is **16 groups** in the SVG.
3. **Primitives only.** `box()` paints left side, top, front. `cylinder_z()`
   builds the group head and portafilter from projected circles and a convex
   hull. `front_rounded()` / `front_circle()` build plates, knobs and the badge.
   `tube()` is used only for the steam wand. There is **no Canny, no contour,
   no RDP, no pixel coordinate** in the scene.
4. **Painter's order.** Base → lower body → tower → top panel → rails → tray →
   side panel → group head → portafilter → wand → knobs → badge → controls.
   Each part is drawn after the part it occludes.
5. **One light.** Front chrome is a light gradient, the left side is darker,
   the top is lightest; yellow uses the same convention. Two designed highlight
   bands sit on the lower front; they are polygons, not reflection traces.
6. **Designed type.** The badge is a cream disc, red ring and live
   `QUICK` / `MILL` text; the switch labels are small live text. Nothing is
   traced from the photo's lettering.
7. **Iterate on the render.** The first box scene had a camera-like group head,
   a tray that cut the yellow side, and a squat body. The fixes were structural:
   a cylindrical boss, a continuous side panel, a taller projection, a thinner
   top panel. The history is visible in the scene comments.

## What changed

- **`scripts/vector_reconstruct.py`** — reusable projection, box, rounded
  front, circle/ellipse, vertical/horizontal cylinder, tube, gradients, SVG
  document and `inspect` CLI.
- **`experiments/T053-.../inputs/build_quickmill.py`** — the Quick Mill scene:
  16 semantic groups, 105 primitive paths, 5 text elements.
- **`tests/test_vector_reconstruct.py`** — 16 tests: linear projection,
  rounded rect, circle, hull, box faces, round front circles, cylinder parts,
  tube, live text, well-formed SVG without raster, determinism, paper layer.
- **`skills/vector-craft/SKILL.md`** — rewritten around reconstruction; T051 is
  explicitly the negative example.
- **`experiments/T053-.../**` — SVG, 2× PNG, before/after sheet, `info.json`.

## Decision table

| Part | Primitive | Visible faces | Why this shape |
|---|---|---|---|
| Base | box 104×7×74 | left, top, front | black plinth with a chrome lip; brass feet below |
| Feet | 4 × vertical cylinder | side, top | two dark rear, two brass front |
| Lower body | box 94×35×69 | left, top, front | yellow side, chrome front, switch plate |
| Tower | box + split front faces | left, top, chrome lower, black upper | the upper black panel carries the badge |
| Top panel | box 96×4×71 | left, top, front | overhangs the tower; cup rails sit on it |
| Cup rails | 4 × thin chrome boxes | top, front | repeated bars, not a traced grid |
| Drip tray | box 94×5×46 + slot pattern | top, front | black tray with a fine repeated grid |
| Side panel | one yellow face | left | continuous from base to top; no tray cut |
| Group head | overhang box + vertical cylinder | front, side, top | a hanging group, not a camera lens |
| Portafilter | vertical basket + horizontal handle | side, cap | basket under the group; handle forward |
| Steam wand | screen-space tube | — | chrome tube + black grip; a hose, not an edge |
| Top knobs | 2 × vertical cylinder | side, top | black base ring + yellow body |
| Badge | front circle + text | front | cream disc, red ring, typeset wordmark |
| Controls | rounded black plate + 3 paddles + labels | front | three cream rockers, red light |

**Why this is not a trace.** Every coordinate is an object dimension or a
projection of one. Changing `tower width` from 94 to 88 moves the side panel,
top panel, badge and rails together; a trace would need to be redrawn. The SVG
has semantic groups (`base`, `tower`, `group-head`, `badge`), not one pile of
`path` elements. There is no `<image>`, no Canny, and no pixel coordinate in the
scene.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| The SVG is a real, editable vector document | 1 | XML parses; 16 groups; 105 paths; 5 text elements; viewBox `0 0 1000 1000` |
| It is rendered by the vector tool | 4 | VectorCraft `info`: 16 groups, 106 path objects, 5 types, 0 warnings; 2× PNG inspected |
| No raster underlay or trace | 1 | `build_quickmill.py` imports no OpenCV/Canny; SVG has no `<image>`/base64; scene uses object coordinates |
| Parts are semantic and independent | 1 | group IDs `base`, `lower-body`, `tower`, `top-panel`, `drip-tray`, `side-panel`, `group-head`, `portafilter`, `steam-wand`, `top-knobs`, `badge`, `controls` |
| Geometry is deterministic | 1 | two builds produce identical SVG; `test_scene_is_deterministic` |
| Front circles stay round under the tall projection | 1 | `front_circle` compensation; bbox test |
| The before/after is visible | 4 | `preview/before-after.png`: T051 trace (54 paths, 1,437 nodes, doubled contours) vs T053 reconstruction |
| Tests cover the primitives | 1 | 16 tests; full suite **448 tests OK** (8 skipped) |

**Before/after metrics:**

| Build | Method | Paths | Nodes / structure | Noise |
|---|---|---|---:|---|
| T051 line | Canny → RDP → Bézier | 54 | 1,437 nodes | doubled contours, traced reflections, badge C |
| **T053** | **semantic 2.5D primitives** | **105** | **16 groups, 105 primitive paths, 5 texts** | **none by construction** |

Path count is not the metric; structure is. T053 has more paths because each
box contributes three faces and each cylinder two, but every path is a named
part face, not an edge fragment.

**Files:** `artifacts/quickmill-reconstruction.svg`, `artifacts/info.json`,
`preview/quickmill-reconstruction.png`, `preview/before-after.png`.

## Negative results and limitations

1. **Single view, manual measurements.** The scene is a designed interpretation
   from one photo, not photogrammetry. Widths/depths are read by eye; a second
   view would change the hidden back faces.
2. **One camera.** The projection is fixed. Moving the camera means editing the
   projection and re-checking occlusion; there is no 3D model to orbit.
3. **Live text, not outlines.** The badge and switch labels use Arial live text.
   A machine without Arial will substitute a font; for a print master, convert
   the wordmark to paths or embed the font.
4. **Simplified internals.** The group head is a boss + gasket + handle, not the
   shower screen, solenoid or internal plumbing. The steam wand is a tube, not a
   valve assembly.
5. **Flat materials.** Chrome is a three-stop gradient; there are no photographic
   reflections, brushed-metal texture or scratches. That is intentional, but it
   is less literal than the photo.
6. **The yellow side panel reads as a folded plane** at the top/bottom edges
   because the panel is a parallelogram in this projection. A real sheet-metal
   panel has a return flange; adding one would remove the ambiguity.
7. **No print proof, no second editor, no human test.** VectorCraft is rung 4;
   Illustrator/Inkscape, PDF/X and a physical 120 mm print are still open.
8. **One product.** The primitive vocabulary is general, but the part inventory
   and proportions are Quick Mill-specific. A different machine needs a new
   scene, not a parameter tweak.
9. **No dimension annotations.** The SVG is an illustration, not an engineering
   drawing; do not use it to manufacture parts.

## Next

- Move the scene to a JSON scene graph (parts, dimensions, materials) so a
  non-programmer can change a dimension.
- Add a second view (front + 3/4) from the same object model; test occlusion.
- Convert the badge wordmark to paths and add a font-fallback check.
- Add a side-panel return flange and a group-head housing ring.
- Test three products: a boxy machine, a curved appliance, a fabric object.
- Run Illustrator/Inkscape parity, PDF/X and a 120 mm print.
- Ask Argon to review the reconstruction before merge.

## Review response (Argon, round 1)

Argon returned **revise** with three blockers. All are fixed in this revision;
the brief is unchanged, the scene was rebuilt.

| Finding | Response |
|---|---|
| Blocker: `cylinder_y` shadowed the `top` colour with the top point list, so knob tops rendered black | **Fixed.** `bottom_pts` / `top_pts`; test asserts the top fill is valid and no `fill="[` exists |
| Blocker: group head/portafilter were horizontal cylinders that read as a camera lens; drip tray pierced the front wall | **Fixed.** The group is an overhang + vertical cylinder + basket, with the handle forward. The tower starts at the tray top, so the tray no longer intersects the front wall |
| Blocker: report claimed “changing a dimension moves the part” while coordinates were hardcoded | **Fixed.** `Dimensions` dataclass; `build(Dimensions(width=88))` test; side panel, top, badge, rails and tray derive from it |
| Major: text labels were wrong (“MOL”, “FEENO”) and appeared missing | **Fixed.** “MILL”, “FERMO”; text is live and renders (2× crop verified); test checks the text contract |
| Major: top panel was offset (z8..71) and the wand went behind the front face | **Fixed.** Top panel is `z0-2..z1`, overhangs 1 unit; wand stays at `z <= 0`; bracket is drawn before the tube |
| Major: no `cylinder_z`/scene/CLI tests; docstring promised a `demo` command | **Fixed.** 16 tests cover `cylinder_z`, `inspect_svg`, the Quick Mill scene and width change; `demo` implemented |
| Minor: 14/15/16 counts, 100 vs 102 paths, pixel-space shadow, unused gradient/clip | **Fixed.** 16 groups (14 parts + shadow + highlights); 105 `<path>` + 1 `<rect>` + 5 `<text>`; VectorCraft reports 106 path objects; shadow uses `disc_y`; unused `yellowFront`/`clip` removed |
