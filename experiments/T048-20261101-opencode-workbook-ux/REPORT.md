# T048 [xlsx] — Workbook UX: hidden data, VBA data entry, tab colour, merges, protection

## Frame

- **Question:** can a workbook behave like an application rather than a raw
  grid — data sheets hidden, a visible Input form, validation, tab colours,
  sheet protection, and a VBA add-record workflow — while the dashboard still
  updates and the package stays auditable?
- **Hypothesis:** yes, if visibility, protection, validation and the macro
  contract are treated as workbook-level data (a `ux` block in the spec), not as
  manual steps after generation. Falsifiers: a hidden sheet that a user cannot
  reach even through the form; a form whose merged cells do not match the VBA
  addresses; a button that points at the source `.xlsx` after SaveAs; a
  validation list that refers to an unprotected/visible helper sheet; a
  protected sheet that blocks the macro.
- **Domain lens:** SpreadsheetML worksheet `state` (`hidden`/`veryHidden`),
  `sheetProtection`, `dataValidation`, `mergeCell`, `tabColor`, VML form
  controls (`FmlaMacro`), Excel object model and VBA.
- **Transfers:** none required; the workbook is native Excel. The project
  illustration/controls are xlsx objects, not images.

## Frozen input

- **Task/claim:** T048 [xlsx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T048-opencode-workbook-ux`, based on `main` (`f7185ae`, after
  T045/T046).
- **Request/date:** 2026-11-01; the owner asked what happens if data sheets are
  hidden, data is entered through VBA/forms, tab colours are changed, cells are
  merged, and sheets are protected — the next workbook-UX research topic.
- **Environment:** Windows 10/11 x64; Python 3.13; XlsxWriter 3.2.9; lxml
  6.1.1; Microsoft Excel 16 with VBA object-model trust enabled. The host's
  macro security policy **blocks macro execution** from COM (recorded below).
- **Could not access:** a host policy that allows macro execution; a signed
  macro; a second machine for a clean-policy test.

## Method

```powershell
python experiments/T048-.../inputs/make_ux.py
python scripts/sheet_forge.py build inputs/workbook_ux_spec.json `
  -o artifacts/workbook-ux.xlsx --no-pivot --vba
python experiments/T048-.../inputs/verify_ux.py
# Excel COM: open XLSX/XLSM, inspect sheets/buttons/validation,
# export Input and Dashboard to PDF/PNG
$env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

The fixture is synthetic: 24 tasks, 4 workstreams, 6 owners, 4 team members,
6 Gantt tasks, a 6-node relation graph, 4 KPI cards. It is built on T046 Sheet
Forge; T048 adds the UX layer.

## What changed

- **`ux` spec block** — `input_form`, per-sheet `hidden` / `very_hidden`,
  `tab_color`, `protect`.
- **Visible Input form** — merged title, section band, labels and input cells
  (`C6:D6`, `F6:G6`, …), auto Task ID (`T025`), 8 data validations, 3 buttons.
- **Hidden data** — Data, Model, Team, Gantt, Relations are `hidden`; Pivot and
  Lookups are `veryHidden`. Only Dashboard and Input are visible.
- **Tab colours** — Dashboard navy `1F4E79`, Input burnt orange `C55A11`, data
  sheets grey `7F7F7F`.
- **Protection** — Input and Dashboard are protected; input cells are unlocked,
  the rest locked; `select_locked_cells`/`select_unlocked_cells` remain on.
- **VBA** — `DashboardTools.AddRecord`, `ClearForm`,
  `RefreshDashboard`, `SetStatus`, `WorksheetExists`; buttons use
  `[0]!DashboardTools.*` in the `.xlsm`.
- **`normalize_button_macros`** — rewrites XlsxWriter's source-workbook
  `FmlaMacro` to `[0]!` after SaveAs, so buttons do not point at
  `workbook-ux.xlsx` from the `.xlsm`.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| Data sheets are hidden, not just far away | 1 + 4 | `workbook.xml`: Data/Model/Team/Gantt/Relations `hidden`, Pivot/Lookups `veryHidden`; Excel `Visible` values `0`/`2`; only Dashboard/Input `-1`; `firstSheet=5` (Dashboard) and `activeTab=8` (Input) |
| Input is the active sheet | 1 + 4 | `activeTab="8"`, `firstSheet="5"`; Excel opens on Input |
| Input is a real form, not a grid | 1 + 5 | 18 merged ranges, 8 data validations, title/section fills, auto ID `T025`; 1-page landscape PDF |
| Tab colours are set | 1 + 4 | `<tabColor rgb="FF1F4E79">` Dashboard, `FFC55A11` Input; Excel `Tab.Color` 7949855 / 1137349 |
| Sheets are protected | 1 + 4 | `<sheetProtection` on Input/Dashboard; Excel `ProtectContents = True`; input cells unlocked |
| Buttons point to the macro in the `.xlsm` | 1 + 4 | VML has `AddRecord`/`ClearForm`/`RefreshDashboard`; xlsm OnAction = `DashboardTools.AddRecord`; 3 buttons |
| VBA module exists | 4 | `.xlsm` `VBProject` has `DashboardTools`; code contains `AddRecord`, `ClearForm`, `SetStatus`, `WorksheetExists` |
| Dashboard still works with data hidden | 4 + 5 | Excel opens XLSM, Dashboard 1 page; 24 tasks, 3.49 tỷ cost, 5.3 tỷ benefit, 6 risks |
| Audit is clean | 1 | `build-report.json`: `ok: true`, 0 errors/warnings/notes; 3 charts, 9 sheets |
| Tests cover the UX contract | 1 | `tests/test_sheet_craft_ux.py` (2 tests); full suite 387 tests OK |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

Preview: `preview/input-page-1.png`, `preview/dashboard-page-1.png`.

## Negative results and limitations

1. **Macro execution is blocked on this host.** The `.xlsm` contains the
   module and the buttons are mapped, but `Application.Run` returns “macros may
   be disabled”. `AddRecord` was therefore **not executed end-to-end**; its
   contract is tested by source inspection, not by a row append. Enable macros
   in a trusted location or sign the project to complete rung 4.
2. **Buttons are form controls, not printed.** The Input PDF does not show the
   three buttons (Excel `PrintObject=False` by default); they are visible when
   the workbook is opened. A print-first form needs a text/button strip or
   `PrintObject=True`.
3. **Hidden is not security.** `hidden`/`veryHidden` only hide tabs; anyone can
   unhide them or read the XML. Workbook structure protection/password and
   information rights are separate. The password is empty in this fixture.
4. **Merged cells are for layout only.** The form uses merges; the Data table
   does not. Merged cells break sorting/filtering and only the top-left cell
   holds a value; VBA must address the top-left. The spec's `mergeCell` count
   is a warning sign, not a quality metric.
5. **The form has only layout validation.** It checks lists/date/integer/>=0;
   it does not check duplicate task IDs, owner capacity, date overlap or
   cross-field rules. Those belong in VBA or a model sheet.
6. **The data range has 6 spare rows.** `data_last_row=30` with 24 records
   means AddRecord can append ~6 rows before the dashboard ranges need to grow.
   A production workbook should use a structured table or dynamic named range.
7. **No UserForm.** The input surface is a worksheet form with buttons, not a
   VBA UserForm; a UserForm would be better for modal validation and multi-row
   entry but harder to audit in the package.
8. **No audit log/undo.** `AddRecord` writes directly to Data; there is no
   changelog, no undo, and no “recent records” view. A real workbook needs an
   append-only audit sheet (veryHidden) and a restore path.
9. **The PDF page is one page by design.** Input is landscape fit 1×1;
   Dashboard is 1 page. Hiding sheets also hides their print output; that is
   intended, but the printed package contains only two sheets.

## Next

- Run `AddRecord` on a host with macros enabled or a signed project; verify the
  appended row, ID and status line.
- Replace the worksheet form with a UserForm or keep the form but add an
  append-only audit log and undo.
- Use a structured table/dynamic named range so new rows extend the dashboard
  automatically.
- Add workbook-structure protection and a real password policy; document that
  hidden ≠ secure.
- Add a “recent records” list and duplicate/overlap validation.
- Ask an independent agent to review this task before merge.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
