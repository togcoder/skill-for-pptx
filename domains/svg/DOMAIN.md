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
| `scripts/photo_vector.py` | Experimental (T051): photo → GrabCut mask → flat colour → form/detail edge hierarchy → layered SVG; line and colour styles | `tests/test_photo_vector.py` |
| `skills/vector-craft/SKILL.md` | Experimental (T051): the working method and failure modes | — |

## Data
- `knowledge/vector_canon.json`: 24x24 grid, optical trim bounds, scaling exponent 0.75, Bézier handles.

## Photo-to-vector hierarchy (T051)
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

## State (2026-11-02)
- Canon tokens standardized in `knowledge/vector_canon.json`.
- Non-linear stroke scaling and Bézier geometry formulas implemented in `scripts/multi_domain_canons.py`.
- Native bridge available via `scripts/vectorcraft_bridge.py` connecting to `D:\artcraft\VectorCraft\vectorcraft-cli.exe`.
- **T051 photo-to-vector**: a CC0 espresso-machine photo → layered SVG. Line
  style: 34 form + 16 detail, 1,437 nodes, GrabCut IoU 0.959, 0 VectorCraft
  warnings; colour style: 5 tones, ΔE76 10.56. Full trace (58 + 133, 2,268 (colour 3,178)
  nodes) is the strawman. **Review requested.**
- Known limitation: the pipeline is not semantic (a human must curate logos and
  controls); the ground-shadow trim assumes a dark contact line; true
  through-holes are filled; no Illustrator/Inkscape or print proof; one product
  photo only.
