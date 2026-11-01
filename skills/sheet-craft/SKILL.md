---
name: sheet-craft
description: Build, repair and audit Excel workbooks and charts — formulas, tables, combo/secondary-axis charts, waterfall/treemap/histogram/box plots, data labels, axes, legends, print layout and accessibility — so charts do not come out stretched, clipped, colourless or broken. Use when the user asks for a spreadsheet/dashboard/chart, says an Excel chart is distorted or wrong, needs a complex chart type, or needs the workbook to survive editing with or without GridCraft.
---

# Sheet Craft

> **Status: EXPERIMENTAL — T041 [xlsx], review requested.** This skill is not a
> canonical product path until an independent review accepts it. Use it, test
> it, and report failures; do not cite it as lab canon yet.

You are the spreadsheet engineer. A chart is a controlled object, not a picture
that happens to sit on a sheet. The chart frame has a fixed size and anchor; the
plot area has a manual layout; axes, labels, series colours and number formats
are data; the chart cache is checked against the worksheet. A workbook that
looks right in a screenshot but has a two-cell anchor, a stale cache or a
truncated axis is not finished.

Scripts live two levels above this file: `ROOT=<this skill dir>/../..`.

- **Required:** Python 3, `lxml`.
- **Optional:** `xlsxwriter` (chart creation), `openpyxl` (post-edit),
  GridCraft (`gridcraft-cli`) for native inspection/formula evaluation/PDF,
  Excel via `pywin32` for recalculation and chart export, PyMuPDF/PdfCraft for
  rendering.

## Workflow

1. **State the question.** A chart answers one question: comparison, trend,
   part-to-whole, distribution, correlation, ranking, deviation, flow or
   hierarchy. Choose the chart from `references/chart-recipes.md`, not from
   decoration.
2. **Prepare the data.** One header row, one observation per row, numeric
   columns typed as numbers, units in the header, no merged cells in the data
   range. Decide how blanks/zeros are handled.
3. **Write the spec.** Use `domains/xlsx/schemas/chart_spec.schema.json`. Geometry, axes,
   labels, series and accessibility are fields in the spec, so the chart can be
   replayed and audited.
4. **Build.**
   - Preferred: `python3 $ROOT/scripts/chart_forge.py build spec.json -o out.xlsx`.
   - Existing workbook: `python3 $ROOT/scripts/chart_patch.py apply in.xlsx patch.json -o out.xlsx`.
   - Native: the GridCraft commands in `references/chart-properties.md`.
5. **Audit.** `python3 $ROOT/scripts/chart_audit.py out.xlsx --md audit.md`.
   Fix every error and every warning that belongs to the chart (not the source
   data's own colour choices).
6. **Render and look.** `--render` uses GridCraft → PDF → PNG; on Windows,
   export the chart with Excel `Chart.Export` and inspect that too. GridCraft's
   PDF font may not cover Vietnamese; Excel export is the native check.
7. **Deliver** the XLSX, the audit JSON/Markdown and the rendered image. Name
   the evidence: structural audit, GridCraft render, Excel render/export,
   human review. They are different rungs.

## Chart selection

| Question | Use | Avoid |
|---|---|---|
| Compare categories | Sorted bar/column, dot plot | Pie, 3-D, radar |
| Trend over time | Line (date axis), area for volume | Connecting unordered categories |
| Part of a whole | Stacked bar; pie/doughnut only for 2–5 slices | Pie with >7 slices, 3-D pie |
| Distribution | Histogram, box-and-whisker | Pie, line |
| Correlation | Scatter, bubble (size = third variable) | Line over categorical X |
| Ranking | Sorted horizontal bar, dot plot | Alphabetical order unless meaningful |
| Deviation +/- | Diverging bar, waterfall | Stacked bar that hides the sign |
| Flow / bridge | Waterfall | Pie |
| Hierarchy | Treemap, sunburst | 3-D pie |
| KPI vs target | Bullet, bar with target line | Gauge (low data-ink) |

## The non-negotiables

- **Zero baseline** for bar/column. A truncated axis is a lie unless the chart
  is a dot plot or the deviation is the point, and then you say so.
- **No 3-D.** It distorts area and hides values.
- **One message per chart.** Title states the insight, not “Chart 1”.
- **Axis titles with units**; a secondary axis always has its own title.
- **≤ 8 series**, ≤ 7 pie slices; highlight one series instead of a rainbow.
- **At least 3:1** series colour contrast against the background; 4.5:1 for
  text. Check deuteranopia distinctness.
- **Data labels only where they earn the space**; do not label every point on a
  dense line.
- **Fixed geometry:** one-cell anchor, explicit cm, manual plot layout. A
  two-cell anchor stretches when rows/columns change.
- **Inside the print area**, landscape/fit when needed.
- **Alt text** on the chart frame; a data table or direct labels as a non-visual
  alternative.
- **Fresh cache:** recalculate and compare the chart cache with the worksheet.

## Geometry and type defaults

From `$ROOT/domains/xlsx/data/spreadsheet_system.json`:

- Chart ≥ 10 × 6 cm; preferred aspect 1.4–2.0; pie/doughnut near square unless
  the legend is on the side.
- Plot area 55–85% of the frame; leave room for title, axis labels and legend.
- Chart text ≥ 8 pt; title 12–16 pt; axis title 9–11 pt; legend/labels 8–10 pt.
- Bar gap 40–80%; overlap 0 for clustered, -10 to 20 for stacked.
- Category width ≥ 0.55 cm; rotate labels at -45° when > 8 categories.
- Palette: navy `#1F4E79`, burnt orange `#C55A11`, blue `#2E75B6`, green
  `#548235`, purple `#7030A0`, grey `#7F7F7F`, olive `#7F6000`, dark red
  `#C00000`. These pass 3:1 against white for lines/markers; check fills.

## With or without GridCraft

**With GridCraft** (`gridcraft-cli`):
- Inspect: `gridcraft-cli info book.xlsx --json` (sheets, ranges, charts,
  tables, names).
- Create: `insert.chart`, `chart.set`, `chart.addElement`, `chart.quickLayout`,
  `chart.changeColors`, `chart.formatSelection`, `chart.selectData`,
  `chart.changeType`, `chart.switchRowColumn`.
- Formula/eval: `gridcraft-cli eval "SUM(B2:B10)" --in book.xlsx --json`,
  `gridcraft-cli check book.xlsx` for cached-value/round-trip fidelity.
- Page/print: `pageLayout.orientation`, `pageLayout.margins`,
  `pageLayout.printArea`, `pageLayout.scaleToFit`, `pageLayout.headerFooter`.
- Render: `gridcraft-cli convert book.xlsx book.pdf`, then PdfCraft/PyMuPDF to
  PNG. GridCraft gives a native-engine render, not Excel's.
- **Gap:** GridCraft's command surface does not expose every axis/label/layout
  property (axis min/max/log, manual plot layout, legend overlay, doughnut
  hole, pie rotation, trendline label position, per-point fills). Use
  `chart_patch.py` for those; do not claim the command API covers them.

**Without GridCraft**:
- Create with `xlsxwriter` (rich chart API) and/or `openpyxl` (workbook/style
  post-edit). Patch the remaining properties with `chart_patch.py`.
- Use raw OOXML (`xl/charts/chartN.xml`, `xl/drawings/drawingN.xml`) when a
  property has no library API. Keep child order; Excel rejects misordered
  chart elements.
- Recalculate/export with Excel COM on Windows (`CalculateFull`,
  `Chart.Export`, `ExportAsFixedFormat`) or LibreOffice headless. Record which
  engine produced the pixels.
- Validate with `chart_audit.py`: type, series, axes, fonts, colours, geometry,
  anchor, print area and data cache.

**Neither** replaces a visual check. The audit is structural; a clean audit
does not prove the chart is readable.

## Commands

```bash
# Build a chart from a semantic spec
python3 $ROOT/scripts/chart_forge.py build spec.json -o chart.xlsx \
  --render preview/ --report build.json

# Inspect every chart in a workbook
python3 $ROOT/scripts/chart_patch.py inspect book.xlsx
python3 $ROOT/scripts/chart_audit.py book.xlsx --md audit.md

# Patch an existing chart (axes, legend, labels, anchor, colours)
python3 $ROOT/scripts/chart_patch.py apply book.xlsx patch.json -o fixed.xlsx

# GridCraft native check
gridcraft-cli info book.xlsx --json
gridcraft-cli check book.xlsx --json
gridcraft-cli convert book.xlsx book.pdf
```

## Definition of done

- Chart type matches the question; title states the insight; axis titles carry
  units.
- One-cell anchor, fixed cm size, manual plot layout, inside the print area.
- Axes: zero baseline where required, explicit min/max/units, log only when
  justified and labelled.
- Series: ≤8, colour-blind-checked, markers/line widths consistent; no 3-D.
- Labels/legend: no collision, readable at 8 pt, outside the plot when dense.
- Data cache matches the worksheet; blanks/zeros handled explicitly.
- Alt text set; a data table or direct labels provide the non-visual fallback.
- Rendered in GridCraft and/or Excel and inspected; the report says which.
- Audit has no errors; warnings are fixed or explained.
