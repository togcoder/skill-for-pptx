# Domain: xlsx (Excel workbooks and charts)

## Scope

Data workbooks and charts. "Done well" means correct data typing, readable
tables, honest charts, a fixed print layout, and a chart that keeps its shape
when the workbook is edited. The chart is a native Excel object, not a picture.

## Thesis

Spreadsheets are worked in. The native model comes first:

- cells, number formats, tables, named ranges and formulas;
- workbook calculation and cached values;
- the Excel chart object: chart type, series, axes, labels, legend, plot area,
  trendlines, error bars, markers, and the drawing anchor;
- print area, page setup and print scale;
- data integrity (the chart cache must match the worksheet).

Chart honesty follows data-visualisation research: zero baselines for bars, no
3-D distortion, sorted categories when rank is the message, direct labels when
they reduce eye travel, and a colour-vision-safe palette. Those are design
rules, not ISO clauses; they live in `domains/xlsx/data/spreadsheet_system.json`
with sources.

Do **not** import slide layout, motion tokens or PowerPoint chart builds. A
chart on a slide and a chart in a workbook have different native constraints.
No pptx→xlsx transfer is accepted yet.

## Native canon and sources

- ECMA-376 / ISO/IEC 29500-1 SpreadsheetML and DrawingML charts: `c:chartSpace`,
  `c:plotArea`, `c:barChart`, `c:ser`, `c:catAx`, `c:valAx`, `c:scaling`,
  `c:dLbls`, `c:trendline`, `c:layout/manualLayout`, `xdr:twoCellAnchor` /
  `xdr:oneCellAnchor`.
- The Excel object model: `Chart`, `ChartObject`, `Axis`, `Series`, `PlotArea`,
  `Legend`, `DataLabels`, `PageSetup`.
- Data-visualisation literature: Tufte, Few, Cleveland & McGill; WCAG 2.2
  non-text contrast and use of colour.
- ISO 80000 (units), ISO 8601 (dates), ISO 690 (source notes), ISO 12647/PDF/X
  for print.

## Code

| Module | Status | Tests |
|---|---|---|
| `scripts/gridcraft_bridge.py` | Experimental (T037): ArtCraft GridCraft bridge (Windows); unreviewed | `tests/test_craft_bridges.py` |
| `scripts/chart_forge.py` | Experimental (T041): build a workbook/chart from `domains/xlsx/schemas/chart_spec.schema.json` | `tests/test_sheet_craft.py` |
| `scripts/chart_patch.py` | Experimental (T041): patch an existing chart's OOXML/anchors | `tests/test_sheet_craft.py` |
| `scripts/chart_audit.py` | Experimental (T041): geometry/axes/cache/contrast audit | `tests/test_sheet_craft.py` |

No xlsx module is a product path until `research/reviews/` contains an accepted
review. The modules carry `Status: EXPERIMENTAL` in their headers.

## Data and skill

| Item | Path | Status |
|---|---|---|
| Chart/design data | `domains/xlsx/data/spreadsheet_system.json` | T041; provenance recorded; unreviewed |
| Spec schema | `domains/xlsx/schemas/chart_spec.schema.json` | T041; unreviewed |
| Skill | `skills/sheet-craft/` | T041; experimental |
| Example specs | `examples/xlsx/chart_*_spec.json` | T041; synthetic |

The data file contains chart selection, geometry/type/colour tokens, rules and
sources. Every threshold used by the audit reads a token; do not hard-code a new
one in a generator.

## Evidence ladder

| Rung | Tool | T041 evidence |
|---|---|---|
| 1 | schema / structural audit | `chart_audit.py`: 3 workbooks, combo/doughnut/scatter, no errors/warnings |
| 2 | library (xlsxwriter) | `chart_forge.py` builds; `chart_audit.py` re-reads the package in tests |
| 3 | GridCraft PDF render | Rendered; **font limitation**: Vietnamese diacritics clipped in the PDF |
| 4–5 | Excel COM open / chart export | Excel opened the exact workbooks and `Chart.Export` produced the PNGs; text and axes correct |
| 6 | human works with the file | Not run |

The T041 report is
`experiments/T041-20261101-opencode-sheet-craft/REPORT.md`.

## State (2026-11-01)

- **T041 [xlsx]**: Chart Forge, chart patch, chart audit, spreadsheet data, skill
  and report; tests pass; **review requested**. Not merged into a product path.
- Evidence reached: rung 1 structural, rung 3 GridCraft render, rung 4–5 Excel
  export. No rung 6 human edit; no LibreOffice Calc.
- Known limitation: GridCraft's PDF export dropped Vietnamese diacritics on the
  fixture; Excel `Chart.Export` rendered them correctly. Record the renderer.
- Known limitation: xlsxwriter/GridCraft do not expose waterfall, treemap,
  histogram, box-and-whisker or funnel. They are documented as raw OOXML
  recipes, not claimed as generated.
- Known limitation: the audit is structural, not a label-collision measurement.
  A render is still required.

## Open questions

1. Should `chart_forge` be the canonical builder, or should it merge into
   `gridcraft_bridge`? One canonical module per capability (MERGE.md).
2. Add raw-XML builders for waterfall, treemap, histogram, box-and-whisker and
   funnel, with Excel open/save fixtures.
3. Add a native Excel COM audit (rung 4) reading chart object properties and
   exporting every chart for the exact package.
4. Add a label-collision model from rendered glyph boxes.
5. Add a workbook-level dashboard audit (alignment grid, shared axes, card
   sizes, print pages) and a LibreOffice Calc rung 3.
