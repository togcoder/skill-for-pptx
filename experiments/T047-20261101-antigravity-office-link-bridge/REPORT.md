# T047 [cross] — Office Link Bridge: Interactive Excel-to-PowerPoint/Word Linked Charts & Embedded Workbook Sync

## Frame
- **Question:** How can AI agents bridge the gap between isolated single-file outputs (Excel vs PowerPoint/Word) to mirror real human office workflows—where presentations and documents maintain live, interactive links to underlying spreadsheets, enabling users to click "Edit Data in Excel" to open full calculation models and allowing programmatic changes in Excel to propagate automatically into presentation charts?
- **Hypothesis (and what would falsify it):** By implementing an ISO/IEC 29500 DrawingML-compliant cross-office bridge (`scripts/office_link_bridge.py`), agents can:
  1. Construct true native linked charts (`TargetMode="External"`, `Type=oleObject`, `<c:autoUpdate val="1"/>`) that Microsoft PowerPoint and Word recognize natively as `chart.ChartData.IsLinked: True`.
  2. Inject rich, multi-sheet SheetCraft models into chart embeddings (`ppt/embeddings/` / `word/embeddings/`), preserving active formulas (`=SUM`, `=B2-B3`), formatting, and tabs, so clicking "Edit Data in Excel" launches the full model rather than an isolated dummy stub.
  3. Perform offline bi-directional cache synchronization (`<c:numCache>`, `<c:strCache>`), so spreadsheet updates propagate to slides without requiring desktop Microsoft Office to be open.
  Falsified if PowerPoint displays a repair/corruption prompt upon opening, if `ChartData.IsLinked` is false, if multi-sheet workbooks lose formulas, or if DeckCraft fails to render the updated chart data.
- **Domain lens (native canon and sources used):**
  - ISO/IEC 29500-1:2016 (Open Packaging Conventions & DrawingML Chart Drawing Markup Language)
  - Microsoft Office DrawingML Chart `<c:externalData>` and Relationship Architecture
  - Microsoft PowerPoint / Excel COM Automation Object Model (MSDN `PowerPoint.Chart`, `ChartData`, `Workbook`)
  - Project Owner Mandate (2026-11-01): Research and establish the interactive bridge between Excel models and PowerPoint/Word reporting decks.
- **Transfers from other domains (and how they are tested):**
  - SheetCraft / GridCraft domain knowledge (`domains/xlsx/DOMAIN.md` - T041/T046) transferred into presentation chart embedding. Tested via `embed_sheetcraft_workbook` in `tests/test_office_link_bridge.py`.
  - DeckCraft CLI rendering engine (T035/T038) used as a headless visual verification gate at 1920x1080. Tested via `D:\artcraft\DeckCraft\deckcraft-cli.exe render`.
  - DocumentCraft (`domains/docx/DOMAIN.md` - T039/T045) DrawingML chart compatibility. Tested via universal package handler in `office_link_bridge.py`.

## Frozen input
- Request / date: User directive on sequential agent collaboration and interactive linking between Excel and PowerPoint/Word (2026-11-01).
- Base commit: `f7185ae620b87dcdb22ab1ccfb63696ff19aa37a`
- Host environment: Windows 11, Python 3.12, Microsoft Office 16.0 (PowerPoint & Excel COM available), DeckCraft CLI (`D:\artcraft\DeckCraft\deckcraft-cli.exe`).

## Method
Commands to reproduce:
```powershell
$env:PYTHONUTF8=1
cd skill-for-pptx
python -m unittest tests/test_office_link_bridge.py -v
python experiments/T047-20261101-antigravity-office-link-bridge/make_artifacts.py
python lab/tools/check_layout.py
python -m unittest discover -s tests
```

## Evidence
| Claim | Rung (0–6) | Evidence (path, hash, output) |
|---|---|---|
| Native Linked Chart Relationship | Rung 4 | `ppt/charts/_rels/chart1.xml.rels` configured with `Type=".../relationships/oleObject"`, `TargetMode="External"`, `Target="file:///..."`. Verified via PowerPoint 16.0 COM: `chart.ChartData.IsLinked: True`. Zero repair prompts. |
| Embedded Multi-Sheet Workbook Preservation | Rung 4 | `ppt/embeddings/Microsoft_Excel_Worksheet1.xlsx` injected with full SheetCraft model (3 sheets: `DoanhThu_LoiNhuan`, `ChiTiet_VungMien`, `ChiSo_KPI`). Verified via PowerPoint COM: `chart.ChartData.Workbook.Worksheets.Count == 3`, formula in `C2` (`=B2*1.3`) 100% active. |
| Offline Cache Synchronization | Rung 2 | `scripts/office_link_bridge.py::sync_office_chart_data` updates DrawingML `<c:numCache>` and `<c:strCache>` using evaluated numbers from Excel via `openpyxl`. Produced `audit.json` recording exact series value diffs. |
| Visual Redraw Verification | Rung 3 | DeckCraft CLI rendered `executive_deck_embedded.pptx` and `executive_deck_synced.pptx` to 1920x1080 PNGs (`slide_embedded.png`, `slide_synced.png`), visually proving chart redraws with updated Q4 data. |
| Unit Test Suite Coverage | Rung 0 | `tests/test_office_link_bridge.py`: 6 tests passing in 0.37s. Full repository test suite passes 391/391 tests 100%. |
| Layout & Hygiene Conformance | Rung 0 | `lab/tools/check_layout.py` reports `layout OK`. |

## Key Findings: The 3 Office Link Bridge Modes
1. **Mode 1: Live External Link (`link_chart_to_external_excel`)**:
   - Relationship: `<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject" Target="file:///C:\path\to\model.xlsx" TargetMode="External"/>`
   - Chart space: `<c:externalData r:id="rId1"><c:autoUpdate val="1"/></c:externalData>`
   - Result: PowerPoint links live to the external Excel file on disk. When opened in Office desktop, clicking "Edit Data" launches the external file in Excel.
2. **Mode 2: Embedded Connected Model (`embed_sheetcraft_workbook`)**:
   - Relationship: `<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/package" Target="../embeddings/Microsoft_Excel_Worksheet1.xlsx"/>`
   - Replaces the minimal 1-sheet dummy stub generated by `python-pptx` with the complete multi-sheet, formula-rich SheetCraft workbook.
   - Result: 100% portable self-contained `.pptx`. When any recipient opens it in Office and clicks "Edit Data in Excel", Excel displays the full model with formulas, multiple tabs, and formatting.
3. **Mode 3: Offline Bi-directional Synchronizer (`sync_office_chart_data`)**:
   - Automatically reads updated values from the Excel workbook (`openpyxl`), evaluates formulas via native COM or cached formula results, and updates the XML `<c:numCache>` and `<c:strCache>` tags.
   - Result: Allows multi-agent pipelines (Excel agent -> Slide agent) to propagate data changes in 0.2s without regenerating slides or losing animations/Morph transitions.

## Negative results and limitations
- If an external linked file is moved or renamed, PowerPoint displays a "Linked file not found" notice when clicked. For maximum portability across machines and cloud viewers, **Mode 2 (Embedded Connected Model)** is recommended as the default, while **Mode 1 (Live External Link)** is ideal for local shared workstation workflows.
- `python-pptx`'s high-level `chart.replace_data()` cannot be used for multi-sheet workbooks because it unconditionally overwrites the embedded workbook with a blank single-sheet xlsxwriter stream. The OOXML-native bridge in `office_link_bridge.py` completely bypasses this limitation.

## Next
- Wire `office_link_bridge.py` directly into `scripts/slide_forge.py` so slide specs can declare `"source_excel": "path/to/model.xlsx"` with automatic embedding and cache binding.
- Provide a cross-domain CLI command `python scripts/cross_pipeline.py bridge --excel model.xlsx --deck presentation.pptx` for one-shot multi-agent handoffs.
- Submit T047 for peer review (Claude / OpenCode / Argon).

## Review response
| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| (Pending peer review) | review requested |
