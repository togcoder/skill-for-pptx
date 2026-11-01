# Spreadsheet system: chart control, not chart decoration

Status: EXPERIMENTAL — T041 [xlsx], review requested (2026-11-01). Evidence
reached: structural (rung 1), GridCraft PDF render (rung 3) and Microsoft Excel
chart export (rung 4–5 for the exact files in
`experiments/T041-20261101-opencode-sheet-craft/artifacts/`; `--render` prefers
Excel and falls back to GridCraft). No LibreOffice Calc, no human rating; the
audit is not a beauty score.

## Why

AI spreadsheets usually get formulas roughly right and charts wrong:

- charts stretch when a column width changes (two-cell anchor);
- a secondary-axis series sits on 0..max because the axis was set on the wrong
  chart object;
- pie slices are all one colour;
- the trendline equation is printed over the y-axis title;
- data labels are clipped at the chart edge;
- the chart is outside the print area;
- the chart cache still shows last month's numbers;
- a 3-D chart distorts the values;
- a bar chart starts at 40 and exaggerates a 5% difference.

T041 treats every one of those as a measurable property:

```
domains/xlsx/data/spreadsheet_system.json   geometry/type/colour tokens, rules, sources
        │ read by                         │ graded by
        ▼                                  ▼
chart_forge.py                      chart_audit.py
chart_patch.py  (existing XLSX)      (geometry, axes, cache, contrast)
        │                                  │
        └──────── build/patch → audit → render → fix ──────────┘
```

## Files

| File | Role |
|---|---|
| `domains/xlsx/data/spreadsheet_system.json` | Chart selection, geometry/type/colour tokens, rules, sources |
| `domains/xlsx/schemas/chart_spec.schema.json` | Semantic input for the chart generator |
| `scripts/chart_forge.py` | Build a workbook + chart from a spec |
| `scripts/chart_patch.py` | Patch an existing chart's OOXML/anchors |
| `scripts/chart_audit.py` | Structural audit: geometry, axes, labels, colours, cache |
| `scripts/sheet_forge.py` | Workbook/dashboard composer: tables, formulas, image table, Gantt, matrix, pivot, print |
| `scripts/vba_forge.py` | Write a `.bas` module; inject into `.xlsm` only with Excel trust access |
| `skills/sheet-craft/` | Workflow, chart property matrix, recipes, audit guide |
| `tests/test_sheet_craft.py` | Chart build/patch/audit tests |
| `tests/test_sheet_craft_advanced.py` | Dashboard package: formulas, image table, Gantt, matrix, anchors, VBA |

## Workbook and dashboard (T046)

A chart-only tool produces a chart; a professional workbook needs the data, the
model, the summary and the page to agree.

| Layer | What it means | Native object |
|---|---|---|
| Data | Typed table, frozen header, filter, percent/number formats | `w:table`, `numFmt` |
| Model | Cross-sheet formulas and named ranges | `SUMIFS`, `COUNTIFS`, `AVERAGEIF`, `INDEX`/`MATCH`, `definedName` |
| Image table | Team/product rows with a picture in the cell, fixed row height, alt text | `xdr:pic` + row height |
| Gantt | Stacked bar, transparent start series, date-formatted value axis, reversed categories | `c:barChart`, `c:valAx` (`numFmt` + explicit serial min/max) |
| Relationship matrix | Pairwise weights + 3-colour scale | `conditionalFormatting` |
| Pivot | Native PivotTable over the data range | `pivotTable` part |
| VBA | Refresh/filter module, labelled `.bas`; injection optional | `vbaProject` |
| Dashboard | KPI cards, shared palette, fixed chart anchors, print area | merged cells + `xdr:oneCellAnchor` |

**Dashboard design rules.** A large dataset is not a deliverable. The dashboard
carries ≤4 KPI cards, one scheduling view, one relationship view and one
comparison chart; the rest stays on data sheets. Keep one accent per KPI state
(neutral/positive/warning), one chart title that states the insight, and one
source note. A matrix is used for pairwise relationships because a native
node-link scatter was not reliable in Excel (T046 negative result).

## Workbook UX (T048)

A delivered workbook often shows two sheets, not nine. The UX layer is data:

| Concern | Native mechanism | Rule |
|---|---|---|
| Hide data | `sheet state="hidden"` / `veryHidden` | Hide Data/Model/Team/Gantt/Relations; `veryHidden` for Pivot/Lookups. Hidden is not security. |
| Input surface | merged layout cells + locked/unlocked formats + `sheetProtection` | Merge only layout cells; Data table stays unmerged. Unlock only input cells. |
| Validation | `dataValidation` list/date/integer/decimal | Lists point to a veryHidden Lookups sheet; do not rely on free text. |
| Tab colour | `tabColor` | Dashboard navy, Input orange, data grey. |
| VBA entry | `.bas` module + form buttons (`FmlaMacro`) | Buttons use `[0]!DashboardTools.AddRecord`; `SaveAs(.xlsm)` must not leave the source `.xlsx` name. |
| Status | inline cell (not MsgBox) | A status line (`B20`) avoids blocking the macro/COM test. |

**Do not print the form buttons by default.** Excel form controls have
`PrintObject=False`; a print-first form needs a text strip or explicit
`PrintObject=True`. A worksheet form is not a UserForm; say which one is used.

**Merged-cell contract.** Only the top-left cell holds a value; VBA must write
that cell; sorting/filtering a merged range is unsafe. The generated data table
never uses merges.

**Macro gate.** The module can be injected with VBA trust, but execution can
still be blocked by macro security. Report module present vs macro executed as
separate evidence.

## What the tools control

- **Chart types:** column/bar, line, area, pie, doughnut, scatter, bubble, radar,
  stock, combo. Waterfall, treemap, sunburst, histogram, box-and-whisker and
  funnel are documented as raw OOXML recipes because xlsxwriter/GridCraft do not
  expose them; do not claim support until the XML is opened in Excel.
- **Axes:** title, min/max, major/minor unit, log base, number format, gridlines,
  tick label position/rotation/size, display units, date axis, reverse, crossing.
- **Series:** values/categories, name, type, primary/secondary axis, fill, line
  width/dash, marker, per-point colour, gap/overlap, trendline, error bars.
- **Labels/legend:** show value/category/series/percent, position, number format,
  separator, size/colour, leader lines; legend position/overlay/font.
- **Layout:** title, chart area/plot area fill/border, manual plot layout,
  chart size in cm, one-cell anchor with fixed extent, print area/orientation.
- **Integrity:** chart cache vs worksheet, palette contrast/distinctness,
  truncated axes, pie slice count/sign/sum, 3-D, density, font floor.

## Rules → generator → checker

| Rule | Generator | Checker |
|---|---|---|
| CHART-GEOMETRY | `position.width_cm/height_cm` | anchor rect ≥10×6 cm |
| CHART-ANCHOR | `post.anchor=one_cell` | `xdr:oneCellAnchor` |
| CHART-ZERO-BASELINE | axis min 0 for bars | min >0 warning |
| CHART-LOG | log base/min | base >1, min >0 |
| CHART-CATEGORY-DENSITY | width/category | ≥0.55 cm |
| CHART-LABELS | label size/position | ≥8 pt; collision heuristic |
| CHART-LEGEND | position/overlay | overlay off >4 series |
| CHART-COLOR-CONTRAST | palette | WCAG 3:1 vs white |
| CHART-COLOR-DISTINCT | palette | RGB 40 / deuteranopia 25 |
| CHART-DATA-CACHE | xlsxwriter cache; recalc | all cached points vs sheet |
| CHART-PIE | `points` palette | ≤7 slices, positive, >0, ≥3 colours |
| CHART-3D | 2-D types only | 3D warning |
| CHART-TITLE | `chart.title` | ≤90 chars |
| CHART-AXIS-TITLE | `axes.*.title` | y/y2 title |
| CHART-FONT | `fonts` | ≥8 pt, title ≥10 |
| CHART-SERIES-COUNT | series list | ≤8 |
| CHART-PRINT | `print_area` | chart inside print area |
| CHART-ALT | `chart.alt`/title | `cNvPr@descr` |
| WB-CROSS-SHEET | formulas reference `Data!$A$2:$A$n` | Excel recalculation; formula XML |
| WB-NAMED-RANGE | `define_name` | `definedName` in workbook.xml |
| WB-IMAGE-CELL | picture in a cell, row height fixed | `xdr:pic` + `wp:docPr@descr` |
| WB-GANTT | transparent start + duration + date-formatted `valAx` | `c:barChart`, `c:valAx`; Excel render |
| WB-MATRIX | pairwise weights + 3-colour scale | `conditionalFormatting`/`colorScale` |
| WB-PIVOT | GridCraft `insert.pivotTable` | PivotTable count/source in Excel |
| WB-VBA | `.bas` written; injection gated | `vbaProject` module in `.xlsm` |
| WB-DASHBOARD | KPI cards, fixed anchors, print area | `mergeCell`; `oneCellAnchor` count |
| WB-PRINT | one sheet = one readable page | Excel `ExportAsFixedFormat` pages |

## Using it

```bash
# A designed dashboard from a semantic spec (tables, formulas, Gantt, matrix)
python3 scripts/sheet_forge.py build spec.json -o dashboard.xlsx \
  --render preview/          # Excel COM when available
python3 scripts/sheet_forge.py build spec.json -o dashboard.xlsx --vba

# Chart-only workbook
python3 scripts/chart_forge.py build spec.json -o chart.xlsx \
  --render preview/ --report build.json
python3 scripts/chart_audit.py chart.xlsx --md audit.md
python3 scripts/chart_patch.py inspect existing.xlsx
python3 scripts/chart_patch.py apply existing.xlsx patch.json -o fixed.xlsx
```

Native checks:

```bash
gridcraft-cli info chart.xlsx --json
gridcraft-cli check chart.xlsx --json
gridcraft-cli convert chart.xlsx chart.pdf
```

Excel COM (Windows, exact file):

```powershell
$excel = New-Object -ComObject Excel.Application
$wb = $excel.Workbooks.Open("C:\path\chart.xlsx")
$wb.Worksheets(1).ChartObjects(1).Chart.Export("C:\path\chart.png", "PNG")
$wb.Close($false); $excel.Quit()
```

## Limits

- **Structural audit ≠ visual quality.** A clean report means the chart is
  structurally sane; it does not mean the labels do not collide. Inspect the
  render.
- **GridCraft PDF font coverage.** GridCraft's PDF export dropped Vietnamese
  diacritics in the T041 fixture ("Thực tế" → "Thc t"). Excel `Chart.Export`
  rendered them correctly. Record which engine produced the image.
- **Theme colours** are not resolved to RGB; only explicit `srgbClr` values are
  contrast-checked.
- **Cache check** compares every cached point; it does not recalculate
  formulas. If xlsxwriter omitted `c:numCache`, the audit uses worksheet values
  and notes the absence.
- **Raw chart types** (waterfall/treemap/histogram/box/funnel) need an Excel
  open/save test; the audit's type parser recognizes them, but the generator
  does not yet build them from a spec.
- **No human calibration.** The rules are anchored to Tufte/Few/WCAG and
  observed failures, not a user study. Treat them as a floor, not a taste score.
- **Excel repair** is not detected by the audit; open the exact file in Excel.
- **Pivot without GridCraft.** The Python path cannot create a PivotTable; the
  generator writes a `SUMIF`/`COUNTIF` summary on the Pivot sheet, and the Model
  sheet is the cross-sheet check.
- **Node-link scatter.** A one-series-per-edge scatter did not render all series
  consistently in Excel/Graph; use the matrix unless a working native
  connected-scatter path is proven.
- **VBA trust.** Injection needs Excel and the VBA object-model trust setting;
  the `.bas` is the portable artifact.
- **Excel print pagination.** A 60-row data sheet prints on 2 pages; the
  dashboard is one page. Count pages in the render; do not assume fit-to-1x1
  means one page for every sheet.

## Next

1. Add raw-XML builders for waterfall, treemap, histogram, box-and-whisker and
   funnel, with Excel open/save fixtures.
2. Add a native Excel COM audit that reads `Chart` object properties and exports
   every chart (rung 4) for the exact package.
3. Add a label-collision model from rendered glyph boxes, not just counts.
4. Add a colour-vision simulation report (protanopia/deuteranopia/tritanopia)
   with palette suggestions.
5. Add a workbook-level dashboard audit (alignment grid, shared axes, card
   sizes, print pages).
6. Add a LibreOffice Calc rung 3 for the T046 dashboard.
7. Add a real PivotTable fallback (or keep the formula summary as the
   documented non-GridCraft path).
8. Prove a native node-link chart (connected scatter/Graph) or document the
   matrix as the only supported relationship view.
9. Add a VBA preflight that reports the trust gate before writing a `.xlsm`.
