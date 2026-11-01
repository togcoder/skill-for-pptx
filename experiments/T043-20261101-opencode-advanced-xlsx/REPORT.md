# T043 [xlsx] — Advanced workbook: image table, Gantt, relationship matrix, pivot, VBA and dashboard

## Frame

- **Question:** can the SheetCraft pipeline produce a professional workbook —
  not a chart demo — where the data table, cross-sheet model, image table,
  Gantt, relationship view, native pivot, VBA helper and dashboard print page
  all agree, and the dashboard still looks designed rather than “everything the
  data can draw”?
- **Hypothesis:** yes, if the workbook is composed layer by layer (data → model
  → views → summary → dashboard), each layer uses a native Excel object, every
  chart gets a fixed one-cell anchor, and the print page is designed rather
  than inherited. Falsifiers: a picture that overflows its cell; a Gantt that
  is a stacked bar with visible start; a “relationship chart” that does not
  render; a pivot that does not open; a dashboard that overlaps or stretches;
  a macro claim without a module.
- **Domain lens:** SpreadsheetML (`w:table`, formulas, `definedName`,
  `conditionalFormatting`, `pivotTable`), DrawingML charts (`c:barChart`,
  `c:dateAx`, `c:ser`), Excel object model, WCAG 2.2 non-text contrast, ISO
  8601 dates, ISO 690 source notes.
- **Transfers from other domains:** the native PivotTable is built by
  **GridCraft** (`insert.pivotTable`), then verified by Excel opening the exact
  workbook. The avatars are Pillow-generated fixture assets, not a claimed
  cross-craft transfer. A node-link scatter (a chart idea from graph/network
  tools) was tested and rejected — see negative results.

## Frozen input

- **Task/claim:** T043 [xlsx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T043-opencode-advanced-xlsx`, based on `main` (`db58b3d`, after
  T039/T041).
- **Request/date:** 2026-11-01; the owner asked for image tables, relationship
  charts, Gantt, very complex cross-sheet formulas, pivot, VBA and a designed
  dashboard: “a huge database does not mean it is good; it needs intelligent
  management”.
- **Environment:** Windows 10/11 x64; Python 3.13; XlsxWriter 3.2.9; lxml
  6.1.1; Pillow 11.3.0; PyMuPDF 1.28.0; Microsoft Excel 16; GridCraft from
  `D:\artcraft`; VBA object-model trust enabled on this host.
- **Could not access:** LibreOffice Calc; a human usability session (rung 6);
  a second machine without Excel for the pivot/VBA paths.

## Method

```powershell
# 1. Synthetic programme data, avatars, spec
cd experiments/T043-20261101-opencode-advanced-xlsx/inputs
python make_dashboard.py

# 2. Build the workbook, native pivot (GridCraft), VBA module + injection
cd ../../..
python scripts/sheet_forge.py build `
  experiments/T043-20261101-opencode-advanced-xlsx/inputs/dashboard_spec.json `
  -o experiments/T043-20261101-opencode-advanced-xlsx/artifacts/programme-dashboard.xlsx `
  --vba

# 3. Audit
python scripts/chart_audit.py `
  experiments/T043-20261101-opencode-advanced-xlsx/artifacts/programme-dashboard.xlsx `
  --md experiments/T043-20261101-opencode-advanced-xlsx/artifacts/audit.md

# 4. Open in Excel, read formulas/pivot/shapes/modules, export sheets
python experiments/T043-20261101-opencode-advanced-xlsx/inputs/verify.py

# 5. Tests
$env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

The fixture is synthetic: 60 tasks across 4 workstreams, 6 team members, 10
Gantt rows, a 6-node relationship graph, 4 KPI cards, and a designed dashboard.
No customer data or brand assets are redistributed.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| The workbook opens in Excel without repair | 4 | `verify.py`: 7 sheets `Data, Pivot, Model, Team, Gantt, Relations, Dashboard`; no repair prompt |
| Cross-sheet formulas calculate | 4 | `Model!B2:E5` = 15 / 2,460 / 3,930 / 0.51 for “Dữ liệu”; `SUMIF`, `COUNTIF`, `AVERAGEIF`, `INDEX` recalculated by Excel |
| Named ranges evaluate | 4 | `TaskCount = 60`, `TotalCost = 9450` via `excel.Evaluate` |
| Image table is a real table with pictures | 1 + 5 | `Team` has 6 `Picture` shapes with alt text (`Ảnh Lan Nguyễn` …), 32 pt rows, print A1:D7 on 1 page; `audit.json`/package also has 6 `xdr:pic` |
| Gantt is native | 1 + 5 | `Gantt!D2 = B2+C2-1` (formula), date axis `c:dateAx`, hidden `Start` series, reversed categories; chart on the Gantt sheet and on Dashboard; 1-page render |
| Relationship view is a real matrix | 1 + 5 | `Relations!A10:G16` weights + `conditionalFormatting` colour scale; 1-page render; dashboard heatmap no longer overlaps |
| Pivot is a native PivotTable | 1 + 4 | `PivotTable1`, source `Data!R1C1:R61C11`, range `$A$3:$F$9`; built by GridCraft `insert.pivotTable` |
| VBA is real, not a claim | 1 + 4 | `programme-dashboard.bas` (`DashboardTools`, `Option Explicit`); injected `.xlsm` opens with `DashboardTools` in `VBProject.VBComponents` |
| Dashboard is designed and fixed | 1 + 5 | 4 KPI cards, 2 charts, matrix, one source note; 2 `xdr:oneCellAnchor` charts with explicit sizes; 1-page PDF; audit clean (3 charts, 0 errors/0 warnings) |
| Chart audit accepts the workbook | 1 | `audit.json`: `ok: true`, 3 bar charts, 7 sheets; `audit.md` written |
| Tests cover the new layer | 1 | `tests/test_sheet_craft_advanced.py` (4 tests); full suite 336 tests OK with `PYTHONUTF8=1` |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `programme-dashboard.xlsx` | `1882ac2af3ee67daae75d6183ebd844a4014541a79485048be7ca8f47b461813` |
| `programme-dashboard.xlsm` | `ed74e5a41173acb131bf29ef45d32a3741514bb3228a69f72cf705d0b5547c2a` |
| `programme-dashboard.bas` | `ddd89c0420ce55f118c253541dd51920d5963895a534044db09b085621a346af` |
| `audit.json` | `db3187a6db99ab9272d2b4742ef3127f88b0852ef27ba2185531b2bcc8064217` |

Preview: `preview/dashboard-page-1.png`, `data-page-1.png`, `team-page-1.png`,
`gantt-page-1.png`, `relations-page-1.png`.

## Negative results and limitations

1. **Node-link scatter rejected.** A scatter with one series per edge and hidden
   axes did not render every series consistently in Excel/Graph, and the audit
   could not classify the hidden value axes reliably. The matrix heatmap is the
   accepted relationship view; the edge coordinates remain on the sheet as
   provenance. Do not claim a native node-link chart from this task.
2. **Pivot depends on GridCraft.** The Python path cannot create a PivotTable.
   Without GridCraft, `Model` (`SUMIFS`/`COUNTIFS`) is the summary; do not
   rewrite the workbook with xlsxwriter to “add” a fallback, because that
   destroys the dashboard.
3. **VBA injection is host-gated.** The `.bas` is always written; the `.xlsm`
   is produced only when Excel trusts the VBA project object model. On a locked
   host, ship the `.xlsx` + `.bas` and say “not injected”.
4. **Image table row heights are explicit.** Excel does not always grow a row
   for a picture; the spec/generator sets 32 pt and a 0.24 scale. A different
   avatar source needs its own measurement.
5. **The dashboard is one page by design; the data sheet is two.** 60 rows at
   A4 landscape cannot be one readable page; fit-to-1-wide is intentional.
6. **No LibreOffice Calc and no human session (rung 6).** The render is Excel's
   own PDF/PNG; a second engine may lay out fonts differently.
7. **The audit is structural.** A clean audit is not a beauty or usability
   score; the dashboard page was inspected visually, but no user test ran.
8. **KPI values are typed strings.** They match the synthetic data but are not
   linked to cells; a production dashboard should drive cards from formulas.
9. **The Gantt is a view, not a scheduler.** Dependencies, milestones and
   critical path are not modelled; the stacked bar plus date axis is the
   supported scope.
10. **The VBA module is minimal.** Refresh and filter procedures only; no error
    handling beyond a message box, and no signature.

## Next

- Add a label-collision / overlap model to the dashboard audit.
- Make KPI cards formula-driven and add a real static pivot fallback.
- Prove a native node-link chart (connected scatter/Graph) or close the
  relationship view to the matrix only.
- Add LibreOffice Calc rung 3 and a human edit/print session (rung 6).
- Add a VBA preflight that reports the trust gate before writing a `.xlsm`.
- Ask an independent agent to review this task; do not merge without
  owner/integrator approval.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
