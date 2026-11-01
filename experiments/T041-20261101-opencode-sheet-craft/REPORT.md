# T041 [xlsx] — SheetCraft: controlled standard DrawingML charts and OOXML patch

## Frame

- **Question:** can a semantic chart spec plus a small OOXML patch layer produce
  a controlled Excel chart (standard DrawingML types: column/bar, line, area,
  pie/doughnut, scatter, bubble, radar, stock, combo) whose geometry, axes,
  labels, legend, palette and print layout survive editing — including
  combo/secondary-axis, doughnut and scatter charts that commonly come out
  stretched, flat, colourless or broken?
- **Hypothesis:** yes, if the chart is created with an explicit type/series/axis
  spec, converted to a one-cell anchor with a fixed extent, audited against
  geometry/axis/cache/contrast rules, and rendered in Excel.
  Falsifiers: a secondary axis that stays 0..max; a chart that stretches when a
  column changes; a pie/doughnut with one colour; a trendline label over the
  axis title; a chart outside the print area; a cache that disagrees with the
  sheet.
- **Domain lens:** Excel's native chart model (ECMA-376 SpreadsheetML +
  DrawingML charts; Excel object model), data-visualisation research
  (Tufte/Few/Cleveland & McGill), WCAG 2.2 non-text contrast, ISO 80000 units,
  ISO 8601 dates, ISO 690 source notes.
- **Transfers from other domains:** the T034 “tokens + critic” method is reused,
  but no PowerPoint layout/motion value is imported. The transfer is tested by
  using Excel's chart OOXML and `Chart.Export`, not a slide render.

## Frozen input

- **Task/claim:** T041 [xlsx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T041-opencode-xlsx`, based on `claude/blissful-pasteur-gmll59` (T040).
- **Request/date:** 2026-11-01; user asked for full control of Excel charts —
  complex charts, distorted/broken output, every chart property — with or
  without GridCraft.
- **Environment:** Windows 10/11 x64; Python 3.13; xlsxwriter 3.2.9; lxml 6.1.1;
  openpyxl 3.1.5; PyMuPDF 1.28.0; Microsoft Excel 16; GridCraft/PdfCraft from
  `D:\artcraft`.
- **Could not access:** LibreOffice Calc (not installed); a human workbook
  editing session; native Excel inspection of every chart type beyond the three
  fixtures. No external customer data; the three fixtures are synthetic.

## Method

```powershell
$e = "experiments/T041-20261101-opencode-sheet-craft"
python scripts/chart_forge.py build "$e/inputs/chart_combo_spec.json"    -o "$e/artifacts/chart-combo.xlsx"
python scripts/chart_forge.py build "$e/inputs/chart_doughnut_spec.json" -o "$e/artifacts/chart-doughnut.xlsx"
python scripts/chart_forge.py build "$e/inputs/chart_scatter_spec.json"  -o "$e/artifacts/chart-scatter.xlsx"

python scripts/chart_audit.py "$e/artifacts/chart-combo.xlsx"    --md "$e/artifacts/chart-combo-audit.md"
python scripts/chart_audit.py "$e/artifacts/chart-doughnut.xlsx" --md "$e/artifacts/chart-doughnut-audit.md"
python scripts/chart_audit.py "$e/artifacts/chart-scatter.xlsx"  --md "$e/artifacts/chart-scatter-audit.md"

# `--render` now tries native Excel Chart.Export first (rung 4–5) and falls
# back to GridCraft → PDF → PNG (rung 3).

# GridCraft render (rung 3)
gridcraft-cli convert "$e/artifacts/chart-combo.xlsx" "$e/preview/workbook.pdf"
```

The three specs are synthetic: a 9-month actual/target combo, a 5-slice cost
doughnut, and an 8-point cost/satisfaction scatter. The spec schema is
`domains/xlsx/schemas/chart_spec.schema.json`.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| The three workbooks are structurally sane | 1 | `chart_audit.py`: all `ok: true`, no errors/warnings; 1 chart each; one-cell anchors; alt text present |
| Combo has a real secondary axis | 1 + 4–5 | `c:barChart` + `c:lineChart`, second `c:valAx` at `axPos="r"`; Excel export shows 0–240 on both axes, titled |
| Doughnut has five categorical fills and percent labels | 1 + 4–5 | 5 `c:dPt` fills; labels show `42%`, `24%`, `18%`, `9%`, `7%`; hole 55; Excel export inspected |
| Scatter uses numeric X/Y and a placed trendline label | 1 + 4–5 | X = column B, Y = column C; 8 points; trendline equation/R² in a manual layout at `x=0.55, y=0.62`; Excel export inspected |
| Charts do not stretch with cells | 1 | `xdr:oneCellAnchor` with fixed `xdr:ext` (16.5×9.2, 13.5×9.0, 15.5×9.0 cm) |
| Charts print | 1 | `definedName _xlnm.Print_Area` includes the chart; landscape/fit set |
| Alt text is present | 1 | `xdr:cNvPr@descr` on each chart frame |
| The patch layer controls existing charts | 1 | `chart_patch.py apply` on `proto.xlsx` changed title/legend/axes/bar/labels and converted the anchor; audit then clean |
| Tests cover build/patch/audit and the failure modes | 1 | `tests/test_sheet_craft.py`: 10 tests (combo, patch second series, per-axis max, print-area rejection, stale cache, manualLayout order, small chart, doughnut palette, schema, audit) |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `chart-combo.xlsx` | `2e36cc6cd561cfc49c9b1f63f5c21988a702f30746e36a91f5396b3335ccd53f` |
| `chart-doughnut.xlsx` | `2a005a133eaed3d86bcf1c2d54d7c4c642fb890a26c49329828be8073188b826` |
| `chart-scatter.xlsx` | `70811a053b22d04b5618684530b8a5c40f841f868cdbffc33189dcf32a18b61f` |

Rendered evidence: `preview/chart-combo.png`, `chart-doughnut.png`,
`chart-scatter.png` (Excel `Chart.Export`). GridCraft PDF was also produced, but
its font dropped Vietnamese diacritics; it is not the primary visual evidence.

## Negative results and limitations

1. **GridCraft PDF lost Vietnamese diacritics.** “Thực tế” rendered as “Thc t”
   in the PDF; Excel `Chart.Export` rendered it correctly. The XLSX strings are
   fine; the renderer is not. Always record which engine produced the pixels.
2. **GridCraft's command surface is narrower than the spec.** It does not expose
   axis min/max/log, manual plot layout, legend overlay, doughnut hole, pie
   rotation, trendline label position or per-point fills. `chart_patch.py`
   writes those at the OOXML layer; do not claim the native commands cover them.
3. **xlsxwriter cannot create every chart type.** Waterfall, treemap, sunburst,
   histogram, box-and-whisker and funnel are documented as raw-OOXML recipes,
   not generated. The audit recognizes them but the generator does not build
   them yet.
4. **The audit is structural, not a pixel judgement.** It cannot measure glyph
   collision; the label/legend checks are heuristics. A render is required.
5. **Cache check compares the first point only.** A full formula-result
   comparison would need a calculation engine.
6. **Theme colours are not resolved.** Only explicit `srgbClr` values are
   contrast-checked; theme colours would need a theme-map resolver.
7. **No LibreOffice Calc (rung 3) and no human workbook edit (rung 6).** Excel
   COM export is rung 4–5 for our files, not a human session. `--render` can
   now produce that export automatically when Excel is available.
8. **Excel repair is not detected.** The audit cannot prove Excel will not offer
   to repair the package; the exact files were opened/exported by Excel, but a
   save round-trip was not diffed.
9. **One-cell anchor position still depends on the from-cell.** The size is
   fixed, but inserting/deleting rows or columns before the chart moves the
   anchor. The next step is a drawing anchor that is independent of the cell
   grid, or a rebuild after structural edits.
10. **xlsxwriter may omit `c:numCache`.** The audit falls back to worksheet
    values, but a third-party reader without a calculation engine may show an
    empty chart until Excel saves it. A full formula-result cache is future work.
11. **Label collision is a heuristic.** The audit measures counts, font sizes
    and geometry, not rendered glyph boxes; a visual check is still required.

## Next

- Peer review by another agent (`review requested`); fix findings.
- Add raw-XML builders for waterfall/treemap/histogram/box/funnel with Excel
  open/save fixtures.
- Add a native Excel COM audit that reads every `Chart` object and exports it
  (rung 4–5) for the exact package.
- Add a label-collision model from rendered glyph boxes.
- Add a workbook-level dashboard audit (alignment grid, shared axes, card
  sizes, print pages) and a LibreOffice Calc rung 3.
- Decide the canonical xlsx builder with the integrator
  (`chart_forge` vs `gridcraft_bridge`) per MERGE.md.

## Review response

Review: `research/reviews/T041-argon-20261101.md` (Argon, 2026-11-01; code/report
review only, no repo/test run). Verdict `revise`; responses below are fixes in
this branch, not a new review round.

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| R4 combo series/axis blind spots | **Fixed:** `chart_info`/`patch_chart_xml` flatten `c:ser` across every chart group and attach `ax_ids`; `chart_audit` checks `axis maximum` only against series on that axis. Tests: patch second series of a combo; two different y/y2 scales. |
| R5 XML order in manualLayout and a:ln | **Fixed:** `plot_layout` and trendline label emit `layoutTarget, xMode, yMode, wMode, hMode, x, y, w, h`; `_solid_fill` inserts before `prstDash`/join/end-cap. |
| R6 print-area and cache checks were stubs | **Fixed:** chart rect is compared with the print-area rect; cache is compared point-by-point; when `numCache` is absent the audit uses worksheet values. Tests: chart outside print area; stale cache after editing a cell. |
| R7 rung 4–5 manual / “full control” overclaim | **Fixed/clarified:** `--render` now tries Excel `Chart.Export` first, then GridCraft; title/scope narrowed to standard DrawingML chart types, with ChartEx listed as recipes. |
| R8 hard-coded ArtCraft path / overlap | **Fixed:** `chart_forge._render_gridcraft` uses `gridcraft_bridge.find_gridcraft_cli/convert_sheet`, no `D:\artcraft` literal. Domain card defines bridge = adapter, forge/patch/audit = native builder. |
| R9 limitations incomplete | **Fixed:** limitations 9–11 added (anchor from-cell dependency, missing numCache, heuristic label collision). |
