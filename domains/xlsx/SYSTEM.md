# Spreadsheet system: chart control, not chart decoration

Status: EXPERIMENTAL — T041 [xlsx], review requested (2026-11-01). Evidence
reached: structural (rung 1), GridCraft PDF render (rung 3) and Microsoft Excel
chart export (rung 4–5 for the exact files in
`experiments/T041-20261101-opencode-sheet-craft/artifacts/`). No LibreOffice
Calc rung 3, no human rating; the audit is not a beauty score.

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
| `skills/sheet-craft/` | Workflow, chart property matrix, recipes, audit guide |
| `tests/test_sheet_craft.py` | Structural build/patch/audit tests |

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
| CHART-DATA-CACHE | xlsxwriter cache; recalc | first cache point vs sheet |
| CHART-PIE | `points` palette | ≤7 slices, positive, >0, ≥3 colours |
| CHART-3D | 2-D types only | 3D warning |
| CHART-TITLE | `chart.title` | ≤90 chars |
| CHART-AXIS-TITLE | `axes.*.title` | y/y2 title |
| CHART-FONT | `fonts` | ≥8 pt, title ≥10 |
| CHART-SERIES-COUNT | series list | ≤8 |
| CHART-PRINT | `print_area` | chart inside print area |
| CHART-ALT | `chart.alt`/title | `cNvPr@descr` |

## Using it

```bash
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
- **Cache check** compares the first point, not every formula result.
- **Raw chart types** (waterfall/treemap/histogram/box/funnel) need an Excel
  open/save test; the audit's type parser recognizes them, but the generator
  does not yet build them from a spec.
- **No human calibration.** The rules are anchored to Tufte/Few/WCAG and
  observed failures, not a user study. Treat them as a floor, not a taste score.
- **Excel repair** is not detected by the audit; open the exact file in Excel.

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
