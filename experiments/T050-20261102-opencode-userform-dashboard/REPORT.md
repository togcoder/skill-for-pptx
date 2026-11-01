# T050 [xlsx] — VBA UserForm + composed dashboard

## Frame

- **Question:** the owner does not want to type into a worksheet. Can a real
  **VBA UserForm** own data entry, and can a dashboard with many charts be
  composed so it is readable, interactive and not crowded?
- **Hypothesis:** yes, if the workbook is designed as two surfaces — a modal
  form for input and a 12-column dashboard for reading — with one palette, one
  reading order, native charts and a hidden data layer. Falsifiers: a "UserForm"
  that is still a worksheet range; a form whose controls do not match the VBA
  addresses; a dashboard whose charts overlap or are cut off; a chart with no
  source/legend; a macro button that points at the source `.xlsx`; a printed
  page that spills to two pages.
- **Domain lens:** Excel object model, VBA UserForm controls, SpreadsheetML
  drawings/VML, xlsxwriter native charts, A4 landscape print composition.
- **Transfers:** none; the dashboard and form are native Excel.

## Frozen input

- **Task/claim:** T050 [xlsx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T050-opencode-userform-dashboard`, based on `main` after the T049 pptx
  merge.
- **Request/date:** 2026-11-02; the owner asked for a VBA UserForm instead of a
  sheet form, and for a dashboard that composes many data points/charts without
  crowding, with good interaction and visual quality.
- **Environment:** Windows 10/11 x64; Python 3.13; XlsxWriter 3.2.9; Pillow
  11.3.0; Microsoft Excel 16 with VBA project trust enabled. The host's macro
  security policy blocks execution (same as T048).
- **Could not access:** a policy that allows macro execution; a human usability
  test; a second machine for a clean-policy run.

## Method

```powershell
python experiments/T050-.../inputs/make_dashboard.py
python scripts/dashboard_forge.py build inputs/dashboard_spec.json `
  -o artifacts/dashboard.xlsx --userform
# builds the XLSX, injects DashboardTools, adds frmEntry + FormTools,
# normalizes the VML buttons to [0]!FormTools.*
python scripts/userform_forge.py inspect artifacts/dashboard.xlsm
python experiments/T050-.../inputs/make_form_preview.py
# Excel COM: export Dashboard to PDF/PNG; inspect sheets/buttons/form
$env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

The fixture is synthetic: 24 tasks, 4 workstreams, 6 owners, 12 monthly trend
points, 4 model groups, 4 KPI cards, 4 charts.

## Composition rules

1. **One grid.** A:L (12 columns), every card and chart snapped to it. KPI cards
   are 3 columns wide; charts are 7/5 columns.
2. **One reading order.** Title → KPI strip → trend/composition → comparison/
   status → source line. A reader can stop after the KPI strip or go deeper.
3. **One palette.** Navy `#1F4E79` for the primary series, orange `#C55A11` for
   attention, blue `#9DC3E6` for context, green `#548235` for benefit, grey for
   secondary text. No rainbow.
4. **Native charts.** Four xlsxwriter charts (line, column, bar, doughnut) with
   titles, legends where needed, data labels only on the column chart, light
   gridlines, and a source line.
5. **Hidden data.** Data/Trend/Model are `hidden`; only Dashboard is visible.
   The dashboard is one A4 landscape page (`A1:L39`, fit 1×1).
6. **Interaction.** Three form buttons: `Nhập liệu` opens `frmEntry`; `Rủi ro`
   filters `At risk`; `Tất cả` clears the filter. The form is modal and owns
   validation.

## UserForm

- **22 controls**: title/hint, 8 labels, 4 combo boxes, 4 text boxes, 3 command
  buttons, 1 status line.
- **Fields**: workstream, owner, start date, days, cost, benefit, status,
  priority.
- **Validation**: required lists, ISO date, days 1–365, numeric cost/benefit.
- **Write path**: `btnSave_Click` finds the last Data row, writes `T###`, start/
  end dates, days, cost, benefit, status, priority; clears the form; refreshes.
- **Module**: `FormTools.ShowEntryForm`, `FilterRisk`, `FilterAll`.
- **Buttons**: VML `FmlaMacro` is `[0]!FormTools.*`; Excel resolves it to the
  current workbook.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| Dashboard is a composed 12-column surface | 1 + 4 | 4 charts, 4 KPI cards, A:L grid, `A1:L39` print area; Excel exports **1 page**; PNG inspected |
| Charts are native, not a screenshot collage | 1 | 4 chart parts (`xl/charts/chart1..4.xml`), line/column/bar/doughnut; audit 0 errors/warnings |
| Data layer is hidden | 1 + 4 | Data/Trend/Model `Visible=0`; Dashboard `Visible=-1`; only Dashboard visible |
| Dashboard has interaction | 1 + 4 | 3 form buttons; OnAction `FormTools.ShowEntryForm/FilterRisk/FilterAll`; VML `[0]!` |
| Dashboard is live, not a static picture | 1 + 4 | Data has a `Visible` SUBTOTAL column; Model uses `SUMIFS`/`COUNTIFS` over `Data`; KPI/status use formulas. Excel filter `At risk` changes 24→4 tasks and 3,492→668 cost; appending one row changes 24→25 and 3,492→3,592 (`formula-check.json`) |
| Build pipeline is one command | 1 | `python scripts/dashboard_forge.py build spec.json -o dashboard.xlsx --userform` builds the XLSX, injects `DashboardTools`, adds `frmEntry`/`FormTools`, normalizes `[0]!FormTools.*` |
| A real UserForm exists | 1 + 4 | `frmEntry` in `VBProject`; **22 controls**; code has `btnSave_Click`, `ClearForm`, `ws.Cells(nextRow, 1).Value = nextId` |
| Form is not a worksheet range | 1 | `VBComponents.Add(3)` (MSForm), controls `Forms.ComboBox.1`, `Forms.TextBox.1`, `Forms.CommandButton.1` |
| Macro execution is blocked | — | `Application.Run` would hang on the modal form; **not executed**; host policy, same as T048 |
| Audit is clean | 1 | `dashboard_forge.audit_dashboard`: `ok: true`, 0 errors, 0 warnings; 4 charts, 4 sheets |
| Tests cover the contract | 1 | `tests/test_dashboard_userform.py` (3 tests); full suite **407 tests OK** (8 skipped) on this branch |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

Preview: `preview/dashboard.png` (1-page dashboard),
`preview/userform-layout.png` (layout rendered from the real 22 controls),
`preview/userform-controls.json` (control inventory).

## Negative results and limitations

1. **The form was not shown end-to-end.** The host macro policy blocks
   `Application.Run`; a modal `frmEntry.Show` would hang COM. The form/controls/
   code are inspected, and the data path is validated by appending the same row
   shape with Excel COM (`formula-check.json`), but a human has not typed a
   record through the form.
2. **The form preview is a layout mock, not a runtime screenshot.** It is drawn
   from the actual control positions/captions and labelled as such. It is not
   evidence that the form rendered.
3. **The dashboard is one page with bottom whitespace.** The charts end around
   row 36; the print area includes row 39 for the source/buttons. A future
   revision can enlarge the bottom charts or move the footer up.
4. **No slicers.** The filters are VBA buttons, not native slicers. The filter
   changes the hidden `Data` sheet and the dashboard formulas recalculate; the
   user does not see the filtered table itself, only the recalculated cards and
   charts.
5. **Ranges are wide but static.** Data/Model formulas cover rows 2–200; adding
   rows beyond 200 will not auto-expand. A structured table or dynamic named
   range is next. The trend chart is a plan curve, not a live aggregation of
   `Data`; the KPI/status/composition charts are live.
6. **Hidden ≠ secure.** Data/Trend/Model are hidden; anyone can unhide them or
   read the XML. Workbook structure protection is not set.
7. **No audit log/undo.** `btnSave_Click` writes directly to Data; there is no
   append-only log, no undo and no duplicate check.
8. **No human study.** "Beautiful" is a design judgement, not a measured
   usability result. The owner's review is the next test.

## Next

- Run the form on a macro-enabled/signed host; verify a real record append.
- Replace the static ranges with a structured table/dynamic named range.
- Add an audit log (veryHidden), undo and duplicate/overlap validation.
- Add native slicers or a filter panel with visible state.
- Reduce the bottom whitespace or add a detail table.
- Ask an independent agent to review this task before merge.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
