# Domain: xlsx (Excel workbooks and charts)

## Scope
Data workbooks and charts. "Done well" means correct data typing, readable
tables and honest charts.

## Thesis (to be written by the first xlsx task)
Spreadsheets are worked in. Number formats, tables, named ranges, and the
native chart model (chart types, axes, series) come first. Chart honesty
follows data-visualisation research (zero baselines for bars, no 3D
distortion).

## Native canon and sources (start here)
- ECMA-376 SpreadsheetML and DrawingML charts.
- The Excel object model and chart types.
- Data-visualisation literature (Cleveland & McGill, and others).

## Code
| Module | Status | Tests |
|---|---|---|
| `scripts/gridcraft_bridge.py` | Experimental (T037): ArtCraft GridCraft bridge (Windows); unreviewed | `tests/test_craft_bridges.py` |

## Evidence ladder
| Rung | Tool |
|---|---|
| 1 | schema |
| 3 | LibreOffice Calc |
| 4–5 | Excel COM open / chart export |
| 6 | person works with the file |

## State (2026-11-01)
T039 claimed it ("full Excel chart control"). Nothing is reviewed.
