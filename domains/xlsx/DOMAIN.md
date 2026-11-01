# Domain: xlsx (Excel workbooks and charts)

## Scope

Data workbooks, dashboards and charts. "Done well" means correct data typing,
readable tables, honest charts, a fixed print layout, and a chart that keeps its
shape when the workbook is edited. The chart is a native Excel object, not a
picture. A dashboard is a designed sheet, not a pile of every chart the data can
produce.

## Thesis

Spreadsheets are worked in. The native model comes first:

- cells, number formats, tables, named ranges and formulas;
- workbook calculation and cached values;
- cross-sheet formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIF`, `INDEX`/`MATCH`)
  and named ranges;
- the Excel chart object: chart type, series, axes, labels, legend, plot area,
  trendlines, error bars, markers, and the drawing anchor;
- structured tables with images in cells, a fixed row height and alt text;
- native Gantt (stacked bar, transparent start series, date-formatted value
  axis);
- relationship matrices (conditional-format heatmap) and, where the renderer
  supports it, node-link scatter;
- PivotTables for summarising a large data range;
- VBA as a labelled `.bas` module, injected only with trust access;
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
| `scripts/sheet_forge.py` | Experimental (T046/T048): designed workbook/dashboard from a spec — tables, formulas, image table, Gantt, matrix, pivot, print, hidden sheets, input form | `tests/test_sheet_craft_advanced.py`, `tests/test_sheet_craft_ux.py` |
| `scripts/vba_forge.py` | Experimental (T046/T048): write a `.bas` module; optional Excel COM injection into `.xlsm`; normalize form-button macros | `tests/test_sheet_craft_advanced.py`, `tests/test_sheet_craft_ux.py` |
| `scripts/dashboard_forge.py` | Experimental (T050): 12-column dashboard composition from a spec; 4 native charts, KPI strip, hidden data, one-page print | `tests/test_dashboard_userform.py` |
| `scripts/userform_forge.py` | Experimental (T050): inject a real VBA UserForm (22 controls) + `FormTools` module; inspect controls/code | `tests/test_dashboard_userform.py` |

No xlsx module is a product path until `research/reviews/` contains an accepted
review. The modules carry `Status: EXPERIMENTAL` in their headers.

## Data and skill

| Item | Path | Status |
|---|---|---|
| Chart/design data | `domains/xlsx/data/spreadsheet_system.json` | T041; provenance recorded; unreviewed |
| Spec schema | `domains/xlsx/schemas/chart_spec.schema.json` | T041; unreviewed |
| Skill | `skills/sheet-craft/` | T041/T046/T048/T050; experimental |
| Example specs | `examples/xlsx/chart_*_spec.json`, `programme_dashboard_spec.json` | T041/T046; synthetic |

The data file contains chart selection, geometry/type/colour tokens, rules and
sources. Every threshold used by the audit reads a token; do not hard-code a new
one in a generator.

## Evidence ladder

| Rung | Tool | T041/T046 evidence |
|---|---|---|
| 1 | schema / structural audit | T041: 3 workbooks, combo/doughnut/scatter, no errors/warnings. T046: dashboard workbook audit clean; 3 bar charts, 7 sheets. T048: 9 sheets, 5 hidden + 2 veryHidden, 18 merges, 8 validations, 2 protections, 3 buttons. T050: 4 charts, 4 sheets, 3 hidden, 3 buttons, 22 form controls |
| 2 | library (xlsxwriter) | `chart_forge.py`/`sheet_forge.py` build; audits re-read the package in tests |
| 3 | GridCraft PDF render | T041 rendered; font limitation: Vietnamese diacritics clipped in the PDF. T046 pivot via GridCraft |
| 4–5 | Excel COM open / chart export | T041 charts exported. T046/T048: Excel opened the exact XLSX/XLSM, read pivot/formulas/buttons/validation; T048 exported Input and Dashboard (1 page each); macro execution blocked by host policy. T050: Excel opened the XLSM, read 4 charts, 3 buttons, 22 form controls, exported Dashboard (1 page); form not shown because macro policy blocks modal execution |
| 6 | human works with the file | Not run |

The T041 report is
`experiments/T041-20261101-opencode-sheet-craft/REPORT.md`; the T046 report is
`experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md`.

## State (2026-11-02)

- **T050 [xlsx] VBA UserForm + composed dashboard**: a 4-sheet workbook
  (Data/Trend/Model hidden, Dashboard visible), 4 native charts, 4 KPI cards,
  12-column grid, one A4 landscape page; real `frmEntry` UserForm with 22
  controls and `FormTools` module; 3 filter/form buttons; **review requested**.
- **T048 [xlsx] workbook UX**: a 9-sheet workbook with only Dashboard/Input
  visible; Data/Model/Team/Gantt/Relations hidden, Pivot/Lookups veryHidden;
  Input form with 18 merges, 8 validations, 3 macro buttons and sheet
  protection; tab colours; VBA `AddRecord`/`ClearForm`; **review requested**.
- **T046 [xlsx] advanced workbook**: a 7-sheet programme dashboard (Data,
  Pivot, Model, Team, Gantt, Relations, Dashboard) with cross-sheet formulas,
  named ranges, an image table, a native Gantt (transparent start, date-formatted
  value axis), a relationship matrix, formula-driven KPI cards, two fixed-anchor
  dashboard charts, a GridCraft pivot with a formula fallback and a VBA module;
  **review requested**.
- **T041 [xlsx]**: Chart Forge, chart patch, chart audit, spreadsheet data, skill
  and report; merged to `main` after owner approval, with the Argon review fixes
  applied.
- Evidence reached: rung 1 structural, rung 3 GridCraft render, rung 4–5 Excel
  export. No rung 6 human edit; no LibreOffice Calc.
- **Cross-craft.** T042 docx added a lab rule: use the ArtCraft tool that owns
  the asset, record tool/version/command/licence, and test in the receiving
  domain. T046 follows it for GridCraft (native PivotTable), tested by Excel
  opening the exact workbook. The avatars are Pillow-generated fixture assets,
  not a claimed cross-craft transfer.
- Known limitation: GridCraft's PDF export dropped Vietnamese diacritics on the
  T041 fixture; Excel `Chart.Export` rendered them correctly. Record the renderer.
- Known limitation: xlsxwriter/GridCraft do not expose waterfall, treemap,
  histogram, box-and-whisker or funnel. They are documented as raw OOXML
  recipes, not claimed as generated.
- Known limitation: the audit is structural, not a label-collision measurement.
  A render is still required.
- Known limitation: a one-cell anchor fixes the size but the top-left still
  depends on the from-cell; inserting rows/columns before the chart moves it.
- Known limitation: xlsxwriter may omit `c:numCache`; the audit falls back to
  worksheet values, but a reader without a calculation engine may show blank
  until Excel saves the file.
- Architecture boundary: `gridcraft_bridge` is the adapter to the external CLI
  (`info`/`eval`/`convert`); `chart_forge`/`chart_patch`/`chart_audit` are the
  native OOXML builder/patch/auditor; `sheet_forge` is the workbook/dashboard
  composer. The canonical-module decision is still open (MERGE.md).
- T046 negative result: a node-link scatter (one series per edge, hidden axes)
  was not rendered consistently by Excel/Graph and the audit could not classify
  it reliably; the relationship matrix heatmap is the deliverable, the scatter
  data stays on the Relations sheet. Do not claim a native node-link chart.
- T046 limitation: the pivot is generated by GridCraft when available; without
  GridCraft the generator writes a formula summary on the `Pivot` sheet in the
  same pass. The Python path still does not create a real PivotTable.
- T046 limitation: VBA injection needs Excel + "Trust access to the VBA project
  object model". The `.bas` is always written; injection produced a `.xlsm` on
  this host. Never claim a macro is embedded when the gate is closed.
- T046 review fix: GridCraft's pivot round-trip dropped chart axis scaling and
  number formats. `sheet_forge` re-applies the Gantt value axis and cost-axis
  number format after the pivot; the audit checks `mmm-yy`, explicit min/max and
  the transparent `Start` series.
- T048 limitation: hidden/veryHidden is not security; the password is empty.
  Merged cells are layout-only; the Data table stays unmerged. Input/ Dashboard
  are protected, but workbook structure is not.
- T048 limitation: macro execution is blocked by the host policy, so
  `AddRecord` was not run end-to-end; the `.xlsm` module, button OnAction and
  source contract are verified. Buttons are not printed by default.
- T048 limitation: the form validates types/lists, not duplicate IDs, owner
  capacity or date overlap; no UserForm, audit log or undo.
- T050 limitation: the form was not shown end-to-end; host macro policy blocks
  modal execution. The preview is a layout mock from the real 22 controls, not a
  runtime screenshot. Hidden ≠ secure; no audit log/undo; static chart ranges.
- T050 limitation: the dashboard has bottom whitespace and no slicers; filters
  are VBA buttons, not native slicers.

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
6. T046: decide whether `sheet_forge` and `chart_forge` share one workbook
   helper; currently each owns its format table.
7. T046: add a real PivotTable fallback (or keep the formula summary as the
   documented non-GridCraft path).
8. T046: test a native node-link chart with a connected-scatter or Graph
   approach; the matrix is the accepted fallback, not a replacement for every
   network need.
9. T046: VBA injection trust is host-specific; add a preflight that reports the
   gate before writing a `.xlsm`.
