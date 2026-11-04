# T046 [xlsx] — Advanced workbook: image table, Gantt, relationship matrix, pivot, VBA and dashboard

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
- **Domain lens:** SpreadsheetML (`table`, formulas, `definedName`,
  `conditionalFormatting`, `pivotTable`), DrawingML charts (`c:barChart`,
  `c:valAx`, `c:ser`), Excel object model, WCAG 2.2 non-text contrast, ISO
  8601 dates, ISO 690 source notes.
- **Transfers from other domains:** the native PivotTable is built by
  **GridCraft** (`insert.pivotTable`), then verified by Excel opening the exact
  workbook. The avatars are Pillow-generated fixture assets, not a claimed
  cross-craft transfer. A node-link scatter (a chart idea from graph/network
  tools) was tested and rejected — see negative results.

## Frozen input

- **Task/claim:** T046 [xlsx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T046-opencode-advanced-xlsx`, based on `main` (`db58b3d`, after
  T039/T041), merged with `main` (`c09b13b`) during the ID renumbering.
- **ID note:** this work started as T043; meanwhile `main` merged Antigravity's
  T042/T043. It was renumbered to **T046** on 2026-11-01 to respect the
  one-task-one-ID rule. The old T043 branch/PR is superseded.
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
cd experiments/T046-20261101-opencode-advanced-xlsx/inputs
python make_dashboard.py

# 2. Build the workbook, native pivot (GridCraft), VBA module + injection
cd ../../..
python scripts/sheet_forge.py build `
  experiments/T046-20261101-opencode-advanced-xlsx/inputs/dashboard_spec.json `
  -o experiments/T046-20261101-opencode-advanced-xlsx/artifacts/programme-dashboard.xlsx `
  --vba

# 3. Audit
python scripts/chart_audit.py `
  experiments/T046-20261101-opencode-advanced-xlsx/artifacts/programme-dashboard.xlsx `
  --md experiments/T046-20261101-opencode-advanced-xlsx/artifacts/audit.md

# 4. Open in Excel, read formulas/pivot/shapes/modules, export sheets
python experiments/T046-20261101-opencode-advanced-xlsx/inputs/verify.py

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
| Image table is a real table with pictures | 1 + 4 | `Team` has 6 `Picture` shapes with alt text (`Ảnh Lan Nguyễn` …), 32 pt rows, print A1:D7 on 1 page; package has 6 `xdr:pic` in a two-cell anchor |
| Gantt is native (not a visible start bar) | 1 + 4 | `Gantt!D2 = B2+C2-1`; `c:barChart` with a transparent `Start` series (`<a:noFill/>`), `Duration` = navy; `c:valAx` with explicit serial `min=46020`, `max=46212`, `mmm-yy`; reversed categories; 1-page render |
| Relationship view is a real matrix | 1 + 4 | `Relations!A10:G16` weights + `conditionalFormatting` colour scale; 1-page render; dashboard heatmap does not overlap |
| Pivot is a native PivotTable | 1 + 4 | `PivotTable1`, source `Data!R1C1:R61C11`, range `$A$3:$F$9`; built by GridCraft `insert.pivotTable` |
| VBA is real, not a claim | 1 + 4 | `programme-dashboard.bas` (`DashboardTools`, `Option Explicit`, `WorksheetExists`); injected `.xlsm` opens with `DashboardTools` in `VBProject.VBComponents` |
| Dashboard is designed, formula-driven and fixed | 1 + 4 | 4 KPI cards (formulas to `TaskCount`/`TotalCost`/`TotalBenefit`/`COUNTIF`), 2 charts, matrix, source note; print area 29.21 × 20.39 cm (≈93% of A4 landscape); 2 `xdr:oneCellAnchor`; 1-page PDF; audit clean |
| Chart audit accepts the workbook | 1 | `audit.json`: `ok: true`, 3 bar charts, 7 sheets; `gantt: true`, hidden `Start`, 0 errors/0 warnings/0 notes |
| Tests cover the new layer | 1 | `tests/test_sheet_craft_advanced.py` (5 tests: formulas, image/matrix, Gantt axis/noFill, print areas, pivot fallback, VBA); full suite 385 tests OK with `PYTHONUTF8=1` |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `programme-dashboard.xlsx` | `fb0a1fac6e31f19c60141742f458c7f3e3582f29dea61b550933fbe71544eb01` |
| `programme-dashboard.xlsm` | `6430f9602d59fa4d96adcbe4cbd9d167dbfe9d81e4cef19072e4cddbad76b0b3` |
| `programme-dashboard.bas` | `ae8b2f6e82a39f406b228d02d878b41da0330b346faff5516e653ec501543bda` |
| `audit.json` | `553368272de15999ef5327cf31011a2e095aa19a55957225a8f81b8e67a5ebd4` |

Preview: `preview/dashboard-page-1.png`, `data-page-1.png`, `team-page-1.png`,
`gantt-page-1.png`, `relations-page-1.png`.

## Negative results and limitations

1. **Node-link scatter rejected — structural reason first.** The matrix is
   preferred because a node-link built as one scatter series per edge has three
   native problems: the series count grows with the edges rather than the nodes,
   edge weights have no natural midpoint label, and a directed edge has no
   arrowhead in a plain scatter. The adjacency matrix is O(NÂ²), expands with the
   node table, and carries weights natively. A secondary observation: the
   experimental two-point scatter build did not render every edge series
   consistently in Excel/Graph; that is a reason not to ship it, not the main
   design argument. The pre-fix audit also could not classify hidden axes; that
   tooling gap is now fixed (`network`/`gantt` detection).
2. **Pivot depends on GridCraft.** The Python path cannot create a PivotTable.
   Without GridCraft, `sheet_forge` writes a `SUMIF`/`COUNTIF` summary on the
   `Pivot` sheet in the first pass; the `Model` sheet remains the cross-sheet
   check. Never rewrite the workbook with xlsxwriter to “add” a fallback — that
   destroys the dashboard.
3. **VBA injection is host-gated.** The `.bas` is always written; the `.xlsm`
   is produced only when Excel trusts the VBA project object model. On a locked
   host, ship the `.xlsx` + `.bas` and say “not injected”. The module guards a
   missing Dashboard/Data sheet, but it is still a demo helper, not signed
   production code.
4. **Image table row heights are explicit.** Excel does not always grow a row
   for a picture; the spec/generator sets 32 pt and a 0.24 scale. A different
   avatar source needs its own measurement.
5. **The dashboard is one page by design; the data sheet is two.** 60 rows at
   A4 landscape cannot be one readable page; fit-to-1-wide is intentional.
6. **No LibreOffice Calc and no human session (rung 6).** The render is Excel's
   own PDF/PNG; a second engine may lay out fonts differently.
7. **The audit is structural.** A clean audit is not a beauty or usability
   score; the dashboard page was inspected visually, but no user test ran.
8. **KPI cards are formula-driven, with a cached value.** A viewer that does not
   recalculate sees the cached string until Excel recalculates; the workbook
   sets `fullCalcOnLoad`, so Excel is correct.
9. **The Gantt is a view, not a scheduler.** Dependencies, milestones and
   critical path are not modelled; the stacked bar plus a date-formatted value
   axis is the supported scope.
10. **The VBA module is minimal.** Refresh and filter procedures only; no error
    handling beyond a message box, and no signature.

## Next

- Add a label-collision / overlap model to the dashboard audit (the current
  audit measures geometry, not text collisions).
- Add a real PivotTable fallback or keep the formula summary as the documented
  non-GridCraft path.
- Prove a native node-link chart (connected scatter/Graph) or close the
  relationship view to the matrix only.
- Add LibreOffice Calc rung 3 and a human edit/print session (rung 6).
- Add a VBA preflight that reports the trust gate before writing a `.xlsm`.
- Ask an independent agent to review this task; do not merge without
  owner/integrator approval.

## Review response

Argon review 2026-11-01 (chat `0:cf4bb6173adaaa34`), verdict **revise** in
round 1 and **approve T046** in round 2 (0 blockers). Full record:
`research/reviews/T046-argon-20261101.md`.

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| B1: Gantt over-claimed `c:dateAx`; value axis 0-based/General; `Start` not verifiably hidden | **Fixed, claim corrected.** Bar charts have no date category axis; the chart now uses `c:valAx` with `min=46020`, `max=46212`, `mmm-yy`, and the `Start` series is patched to `<a:noFill/>` on fill and line. `chart_audit` reports `gantt: true`, `hidden: true`, and does not apply zero-baseline to a Gantt. The old `c:dateAx` wording was wrong and is removed from report/docs. |
| B2: dashboard/Gantt print areas exceed A4; charts overlap | **Partly fixed, partly disputed.** Print areas are now Dashboard 29.21 × 20.39 cm and Gantt 28.55 × 14.29 cm (≈93% scale) — down from 29.21 × 26.21 and 40.4 × 10.58. The claimed chart2/chart3 x-overlap ignored their y bands; the rendered page and rects (`y=5.15..12.15` vs `13.09..19.69`) show no overlap. A label-collision audit remains open. |
| M1: node-link rejection reasoning was backwards | **Fixed.** The negative result now leads with the structural reasons (series count vs edges, no midpoint weight label, no arrowheads, O(NÂ²) adjacency that grows with nodes) and treats the inconsistent render as secondary evidence. |
| M2: evidence rungs over-claimed; audit did not check pics/pivot/VBA/fonts | **Clarified.** Rung 1 = package/tests; rung 4 = Excel COM open/recalculation/pivot/module read; rung 5 = Excel PDF/PNG export. Tests now assert images, matrix, print areas, pivot fallback and VBA; font extraction remains a known audit gap. |
| M3: KPI cards were typed strings and inconsistent with the data | **Fixed.** Cards are formulas: `=TaskCount`, `=SUBSTITUTE(TEXT(TotalCost/1000,"0.00"),".",",")&" tỷ"`, `=SUBSTITUTE(TEXT(TotalBenefit/1000,"0.0"),".",",")&" tỷ"`, `=COUNTIF(Data!$J$2:$J$61,"At risk")`; cached values keep the page readable. The synthetic values now agree with the model (9.45 / 15.1 tỷ, 15 at risk). |
| M4: images could detach; pivot fallback empty; VBA runtime | **Fixed / disputed.** Team pictures already use `xdr:twoCellAnchor` (checked in the package), not one-cell. GridCraft availability is checked before the first pass and a `SUMIF`/`COUNTIF` summary is written to `Pivot` when absent. VBA now checks `WorksheetExists`; `RefreshAll` is safe without a pivot. |
| m1: `w:table` typo; tests miss Gantt/print regressions | **Fixed.** Domain lens says `table`; tests assert `mmm-yy`, `min`, `noFill`, Dashboard/Gantt print areas, the pivot fallback and formula KPIs (5 tests). |
