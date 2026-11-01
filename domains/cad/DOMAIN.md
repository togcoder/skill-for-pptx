# Domain: cad (Technical Drawings & Mechanical Drafting)

## Scope
2D and 3D engineering technical drawings, standard drawing sheets, projection views, dimensioning geometry, line weight hierarchies, and title blocks (.dxf, .dwg, .svg, .pdf) using CADCraft.

## Thesis
Engineering drawings convey exact manufacturing intent through strict adherence to international drafting standards:
1. Standard sheet sizes and margins (ISO 5457): A4 to A0 with mandatory 20.0mm left binding margin and 10.0mm (A2-A4) or 20.0mm (A0-A1) outer margins.
2. Distinct line weight hierarchy (ISO 128): Ratio $\sqrt{2} \approx 1.414$ between adjacent weight classes. 0.50mm group for A3/A4: `VISIBLE_OUTLINE` (0.50mm continuous thick), `HIDDEN_EDGE` (0.25mm dashed), `CENTER_AXIS` (0.18mm chain thin), `DIMENSION_HATCH` (0.18mm continuous thin), `PHANTOM_BOUNDARY` (0.18mm double-dot).
3. Clear dimensioning hierarchy (ISO 129): Text height 3.5mm, 1st dimension line offset $\ge 10.0\text{ mm}$ from part geometry, parallel dimension line spacing $\ge 7.0\text{ mm}$, extension line origin offset 1.0mm, extension overshoot 2.0mm, and filled closed arrowheads ($15-20^\circ$ angle, 3:1 aspect ratio).
4. Standard title block (ISO 7200): Fixed 180.0mm width at the bottom-right border corner with mandatory metadata fields.

## Native canon and sources
- ISO 5457: Technical product documentation — Sizes and layout of drawing sheets.
- ISO 128: Technical product documentation — General principles of execution.
- ISO 129: Technical product documentation — Dimensioning and tolerancing.
- ISO 7200: Technical product documentation — Data fields in title blocks and document headers.
- `knowledge/cad_iso_canon.json`: formal machine-readable specification.

## Owners and reviewers
- Author: Antigravity + Argon (Gemini 4).
- Peer reviewers: Claude, OpenCode.

## Code (canonical / experimental)
| Module | Status | Tests |
|---|---|---|
| `scripts/multi_domain_canons.py` | Canonical (T042): ISO sheet dimensions, line weights, dimensioning offsets | `tests/test_multi_domain_canons.py` |
| `scripts/cadcraft_bridge.py` | Experimental (T042): CADCraft headless CLI runner | `tests/test_multi_domain_canons.py` |

## Data
- `knowledge/cad_iso_canon.json`: Sheet sizes, ISO line weights, dimensioning geometry, ISO 7200 title block.

## Evidence ladder
| Rung | Tool | Meaning |
|---|---|---|
| 0 | Python test suite | ISO mathematical calculation and token checks |
| 1 | `cadcraft-cli.exe info` | Entity counts, layer definitions, block catalog |
| 3 | `cadcraft-cli.exe convert <in> <out.png>` | Raster visual preview verification |
| 4 | `cadcraft-cli.exe convert <in> <out.svg>` / `pdf` | Vector drawing generation with accurate line weights |
| 5 | QCAD / LibreCAD / AutoCAD | Native DXF/DWG layer, dimension, and entity integrity |

## State (2026-11-01)
- ISO 128 / 5457 / 7200 drafting canon formalized in `knowledge/cad_iso_canon.json`.
- ISO geometric calculations implemented in `scripts/multi_domain_canons.py`.
- CADCraft native bridge operational in `scripts/cadcraft_bridge.py` connecting to `D:\artcraft\CADCraft\cadcraft-cli.exe`.
