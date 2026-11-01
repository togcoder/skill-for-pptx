# Dashboard recipes (T046)

Concrete OOXML/Excel patterns behind `scripts/sheet_forge.py`. Read this before
changing a dashboard block.

## KPI strip

```text
┌───────────┬───────────┬───────────┬───────────┐
│ Công việc │ Ngân sách │ Lợi ích   │ Rủi ro    │  label 9 pt, muted
│ 60        │ 8,4 tỷ    │ 12,1 tỷ   │ 3         │  value 20 pt, navy
│ +12 quý   │ 72%       │ 1,44×     │ 1 theo dõi│  delta 9 pt, state colour
└───────────┴───────────┴───────────┴───────────┘
```

- Each card = 3 merged columns × 3 rows. Equal widths; 6–8 pt gap between cards.
- Label, value, delta are three merged ranges; no single cell holds all three.
- The value is a **formula** (`=TaskCount`, `=COUNTIF(Data!…,"At risk")`,
  `=TEXT(TotalCost/1000,"0.00")&" tỷ"`), not a typed string; a cached value keeps
  the card readable before recalculation.
- Fill is a pale tint; value colour is the same navy as the dashboard title.
- Delta colour: green `#548235` for good, red `#C00000` for risk. Never colour
  the label.

## Chart anchors

`xdr:twoCellAnchor` stretches with rows/columns. After the workbook is written,
`chart_patch.patch_workbook` converts chart frames to `xdr:oneCellAnchor` with
an explicit `ext cx/cy`. It matches the drawing by **sheet name**, not by a
brittle drawing index:

```json
{"anchors": [{"sheet": "Dashboard", "anchor": {
  "mode": "one_cell",
  "sizes": [[18.0, 8.5], [13.2, 7.4]],
  "alts": ["Gantt chart", "Cost and benefit chart"]
}}]}
```

Only anchors that contain `xdr:graphicFrame` are converted. Pictures (team
photos) keep their two-cell anchor and their `xdr:pic`; converting them was the
cause of an earlier “Excel cannot open the file” bug.

## Gantt

- Data: `Task`, `Start` (date), `Days` (number), `End` formula `=Start+Days-1`,
  `Progress` (0–1, `0%`).
- Chart: stacked bar with two series:
  1. `Start` — fully transparent (`<a:noFill/>` on both fill and line); a bar
     chart has no date category axis, so the start offset is a value, not a date
     axis;
  2. `Duration` — accent fill.
- Value axis (horizontal): explicit serial `min`/`max` from the task dates,
  `num_format: "mmm-yy"`, major unit 30. Use `set_x_axis` in XlsxWriter — for
  bar charts the API's x/y are swapped relative to the visual position.
- Category axis (vertical): `reverse` so the first task is on top.
- Legend off: the colours are self-evident and the labels carry the tasks.
- Insert the same chart on the Gantt sheet and on the dashboard (two chart
  objects, not one shared object). GridCraft's pivot round-trip can drop axis
  settings; re-apply them with `chart_patch` after the pivot.

## Relationship matrix

- Nodes row/column headers; cell = weight (0 for no edge).
- 3-colour scale: `#EAF1F8` → `#9DC3E6` → `#1F4E79`; white cell borders.
- Keep the raw edge list (from, to, x1/y1, x2/y2) on the same sheet as
  provenance, outside the print area.
- **Do not** ship a node-link scatter built as one series per edge: in the T046
  fixture Excel/Graph did not render all series consistently, and the audit
  could not classify the hidden axes reliably. A matrix is the accepted visual.

## Image table

- One picture per row in column A; row height 32 pt; image ~29 pt after offsets.
- Alt text on `xdr:cNvPr@descr`.
- Text cells vertically centred; column widths fixed; print area A1:D<last>.
- A 160 px avatar at `x_scale 0.24` renders at 28.8 pt; do not rely on “it looks
  right” — check the shape width in Excel or the PDF.

## Pivot

GridCraft JSONL:

```json
{"command": "home.insertSheet", "params": {"name": "Pivot"}}
{"command": "insert.pivotTable", "params": {
  "source": "Data!A1:K61", "destination": "Pivot!A3",
  "rows": ["Workstream"], "columns": ["Status"],
  "values": [{"field": "Cost", "func": "sum"}]}}
```

- The destination sheet must exist before the pivot step.
- Without GridCraft, `sheet_forge` writes a `SUMIF`/`COUNTIF` summary on the
  `Pivot` sheet in the first pass; the `Model` sheet remains the cross-sheet
  check. Never rewrite the workbook with xlsxwriter to “add” a fallback — that
  destroys the dashboard.
- Verify with Excel: `PivotTables().Count`, `SourceData`, `TableRange1`.

## VBA

- Module: `Attribute VB_Name = "DashboardTools"`, `Option Explicit`, small
  procedures (`RefreshDashboard`, `FilterAtRisk`).
- Write the `.bas` always; inject with `wb.VBProject.VBComponents.Add(1)` only
  when trust access is enabled; save as `.xlsm` (`FileFormat=52`).
- If injection fails, report `injected: null` and keep the `.xlsx`. A `.bas`
  next to the workbook is honest; a fake “macro-enabled” claim is not.

## Print

- Dashboard: `A1:N38`, landscape, fit 1×1, margins 0.3–0.4.
- Data: `A1:K61`, landscape, fit 1 wide; 2 pages tall is acceptable.
- Team: `A1:D7`, 1×1.
- Gantt: table + chart stacked, `A1:L27`, landscape, fit 1×1.
- Relations: nodes + matrix block only; edge list outside the print area.
- Always export the exact sheet and count pages; do not assume.
