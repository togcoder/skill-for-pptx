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

## Data
- `knowledge/vector_canon.json`: 24x24 grid, optical trim bounds, scaling exponent 0.75, Bézier handles.

## Evidence ladder
| Rung | Tool | Meaning |
|---|---|---|
| 0 | Python test suite | Formula and token schema validation |
| 1 | `xml.etree` / `resvg` | SVG well-formedness and schema compliance |
| 3 | Chrome / Headless Browser | Visual rasterization check |
| 4 | `vectorcraft-cli.exe info` | VectorCraft native geometry and artboard verification |
| 5 | Inkscape / Illustrator | Multi-editor visual parity |

## State (2026-11-01)
- Canon tokens standardized in `knowledge/vector_canon.json`.
- Non-linear stroke scaling and Bézier geometry formulas implemented in `scripts/multi_domain_canons.py`.
- Native bridge available via `scripts/vectorcraft_bridge.py` connecting to `D:\artcraft\VectorCraft\vectorcraft-cli.exe`.
