# Domain: svg (Vector Graphics, Icons & Illustrations)

## Scope
Vector graphics, icon grids, UI components, geometric diagrams, and print-ready assets (.svg, .ai, .eps, .pdf).

## Thesis
Vector graphic quality is governed by mathematical and optical balance:
1. Strict `24x24` icon grid alignment with optical trim compensation for circle, square, and rectangular primitives.
2. Non-linear stroke weight scaling ($W(S) = W_0 (S/S_0)^{0.75}$) to preserve visual density across disparate display scales.
3. $G^1$ / $G^2$ curvature continuity using cubic Bézier extrema anchoring and the canonical 90° circle handle ratio $\kappa = \frac{4}{3}(\sqrt{2}-1) \approx 0.55228$.
4. Sub-pixel snapping: integer grid coordinates for even stroke weights and half-pixel offsets for odd/fractional stroke weights.

## Native canon and sources
- W3C Scalable Vector Graphics (SVG) 2.0 Specification.
- Google Material Design Iconography Grid (24x24dp live area with 2dp padding).
- Apple Human Interface Guidelines: Squircle $G^2$ curvature continuous corners.
- `knowledge/vector_canon.json`: formal machine-readable specification.

## Owners and reviewers
- Author: Antigravity + Argon (Gemini 4).
- Peer reviewers: Claude, OpenCode.

## Code (canonical / experimental)
| Module | Status | Tests |
|---|---|---|
| `scripts/multi_domain_canons.py` | Canonical (T042): Stroke scaling, Bézier $\kappa$, optical trim | `tests/test_multi_domain_canons.py` |
| `scripts/vectorcraft_bridge.py` | Experimental (T037, T042): VectorCraft headless CLI runner | `tests/test_craft_bridges.py` |
| `scripts/photo_vector.py` | Experimental (T051, **negative result**): photo → edge hierarchy → layered SVG; rejected as a trace, kept for evidence | `tests/test_photo_vector.py` |
| `scripts/vector_reconstruct.py` | Experimental (T053): semantic 2.5D reconstruction — projection, box, cylinder, plate, tube, gradients, SVG scene | `tests/test_vector_reconstruct.py` |
| `skills/vector-craft/SKILL.md` | Experimental (T053): reconstruction method; T051 is the “do not trace” example | — |
| `skills/iso-vector-craft/**` | Experimental (T056): part-based isometric product illustration; vendored MIT Anatomy kit + export wrapper | `tests/test_iso_vector_skill.py` |

## Data
- `knowledge/vector_canon.json`: 24x24 grid, optical trim bounds, scaling exponent 0.75, Bézier handles.

## Semantic reconstruction (T053)

The owner rejected T051: edge tracing is not a reconstruction. T053 models the
object instead.

- **Object coordinates:** `x` width, `y` height, `z` depth; one axonometric
  projection for every part. The photo supplies proportions and materials, not
  line work.
- **Parts as primitives:** base/tower/top are boxes; knobs/feet are vertical
  cylinders; the group head/portafilter are cylinders along `z`; the badge and
  controls are front-plane circles/rectangles; the steam wand is a screen-space
  tube.
- **Painter's order:** base → body → tower → top → rails → tray → side →
  group head → portafilter → wand → knobs → badge → controls.
- **One light:** front lighter, left side darker, top lightest; chrome is a
  three-stop gradient, not a copy of reflections.
- **Type, not trace:** the badge wordmark and switch labels are live text.
- **Test:** changing a dimension moves the whole part; a trace cannot do that.
  The SVG has 16 semantic groups, no `<image>`, no Canny.

## Part-based isometric product illustration (T056)

T053 proved the model-not-trace idea; T056 turns it into a reusable product
method, built on the MIT Anatomy kit (vendored, commit `1482e84`).

- **Specific, not invented.** The drawing must be *this* product: real/derived
  dimensions, exact model/variant, identity features listed before geometry.
- **30–60 named parts.** Plinth, platter, record, label, well, bearing, gimbal,
  arm, counterweight, headshell, rest, controls, target light, marks. Every part
  sits on another; wrapping parts split back/front.
- **One camera.** 1 unit = 1 mm; azimuth 120–140 for a front-right 3/4, 40–60
  for front-left; avoid 45/135 (CAD corner); elevation 20–27 for a desktop
  object. The SL-1200 needed 24°, not 18°.
- **Four-tone materials, one light.** 4–6 materials; flat fills; one soft halo;
  no hard shadow polygons, no texture.
- **Detail budget.** Silhouette → mechanism → surface. Stop below 2 units at
  final size. 9 groove rings, 2 strobe rings, one logo.
- **Export-safe.** `product-svg.mjs` bakes the light palette into literal
  values, adds `<title>/<desc>` and pins a real font. CSS variables alone fail
  in resvg and several editors.
- **Evidence.** SL-1200 518 paths / 12 part groups / 0 VectorCraft warnings;
  Gale speaker 79 + 114 paths; Rolleiflex 217 paths (stress test, not
  showcase); 13 tests; resvg renders; owner accepted the V3 direction.

## Photo-to-vector hierarchy (T051 — negative result)
A camera photo is not a line drawing. The pipeline keeps three layers and
removes the fourth:

- **Silhouette** (outer body, base, handle): always kept; RDP 1.2 px + Bézier;
  weight 0.48% of object height.
- **Form** (part boundaries, panel edges, tray lip): length ≥ 5.5% of the object
  diagonal and turning ≤ 0.55°/px; weight 0.26%.
- **Detail** (buttons, knobs, vents, badge ring): short + strong; closed
  controls need a ≥ 3 mm bbox and circularity ≥ 0.28; weight 0.125%.
- **Texture** (reflections, dust, lettering, cast shadow): removed or flattened
  into 5 material tones. The badge is a shape, not traced lettering.

The **scale test** is the discipline: a detail shorter than 1.5 mm at the final
width is removed even when it is real. The **full trace** is kept as a strawman:
on the T051 photo it produces 58 form + 133 detail and 2,268 nodes (3,178 in colour), versus 34 +
16 and 1,437 nodes for the line drawing.

## Evidence ladder
| Rung | Tool | Meaning |
|---|---|---|
| 0 | Python test suite | Formula and token schema validation |
| 1 | `xml.etree` / `resvg` | SVG well-formedness and schema compliance |
| 3 | Chrome / Headless Browser | Visual rasterization check |
| 4 | `vectorcraft-cli.exe info` | VectorCraft native geometry and artboard verification |
| 5 | Inkscape / Illustrator | Multi-editor visual parity |

## State (2026-11-03)
- Canon tokens standardized in `knowledge/vector_canon.json`.
- Non-linear stroke scaling and Bézier geometry formulas implemented in `scripts/multi_domain_canons.py`.
- Native bridge available via `scripts/vectorcraft_bridge.py` connecting to `D:\artcraft\VectorCraft\vectorcraft-cli.exe`.
- **T056 iso-vector-craft**: part-based isometric product illustration. The
  Technics SL-1200 flagship is 518 paths / 12 part groups, 0 VectorCraft
  warnings; the Gale speaker is the easy front/rear example; the Rolleiflex is
  a labelled stress test. The MIT Anatomy kit is vendored with attribution and
  an export wrapper that bakes the palette. Owner accepted the direction and
  asked for `main`; Argon review `accept-with-fixes` (round 2) after the gimbal
  order, relative anchors, generic rules and DOM contract fixes.
- **T051 photo-to-vector**: a CC0 espresso-machine photo → layered SVG. Line
  style: 34 form + 16 detail, 1,437 nodes, GrabCut IoU 0.959, 0 VectorCraft
  warnings; colour style: 5 tones, ΔE76 10.56. Full trace (58 + 133, 2,268 (colour 3,178)
  nodes) is the strawman. **Review accepted (Argon); merged to main (PR #49).**
- Known limitation: the pipeline is not semantic (a human must curate logos and
  controls); the ground-shadow trim assumes a dark contact line; true
  through-holes are filled; no Illustrator/Inkscape or print proof; one product
  photo only.
