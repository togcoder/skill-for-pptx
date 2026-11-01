# Chart audit: rules, fixes and evidence

`scripts/chart_audit.py` reads the XLSX package, not a screenshot. It answers
“is this chart structurally sane?” It does **not** answer “is it beautiful?” —
that needs a render and a human.

## What it measures

| Rule | Measurement | Default | Fix |
|---|---|---|---|
| CHART-GEOMETRY | anchor rect in cm | ≥10×6 cm | resize; use one-cell anchor |
| CHART-ANCHOR | anchor type | oneCellAnchor | patch `xdr:twoCellAnchor` → one-cell |
| CHART-ZERO-BASELINE | value-axis min for bar/column | 0 | set min 0 or use a dot plot |
| CHART-LOG | `c:logBase`, scaling min | base >1, min >0 | fix scaling or use linear |
| CHART-CATEGORY-DENSITY | chart width / categories | ≥0.55 cm | rotate labels, shorten names, split |
| CHART-LABELS | label font / count | ≥8 pt | label fewer points, move legend |
| CHART-LEGEND | legend present/overlay | overlay off >4 series | move legend below/right |
| CHART-COLOR-CONTRAST | WCAG ratio vs white | ≥3:1 | darken or add a border/marker |
| CHART-COLOR-DISTINCT | RGB + deuteranopia distance | 40 / 25 | change palette or add markers |
| CHART-DATA-CACHE | `c:numCache` vs worksheet | 1e-6 | refresh/rebuild chart |
| CHART-PIE | slices, negative, sum, palette | ≤7, positive, >0, ≥3 colours | use sorted bar |
| CHART-3D | chart type contains 3D | none | switch to 2-D |
| CHART-TITLE | title length | ≤90 chars | rewrite the insight |
| CHART-AXIS-TITLE | y/y2 title | present | add units |
| CHART-FONT | smallest explicit font | ≥8 pt (title 10) | increase size or reduce content |
| CHART-SERIES-COUNT | series count | ≤8 | facet/highlight/combine |
| CHART-PRINT | print area / anchor | chart inside print area | set print area, landscape |
| CHART-ALT | `cNvPr@descr` | present | set alt text and a data table |

## Reading the JSON

```json
{
  "ok": true,
  "errors": [],
  "warnings": ["chart 1: series colour #ED7D31 is below 3:1 against white"],
  "notes": [],
  "stats": {"charts": 1, "types": ["combo:barChart+lineChart"]},
  "charts": [
    {"type": "combo:barChart+lineChart", "width_cm": 16.5, "height_cm": 9.2,
     "anchor_kind": "oneCellAnchor", "alt": "…", "axes": [...], "series": [...]}
  ]
}
```

- `errors` mean the chart is structurally wrong (too small, summary axis cuts
  data, negative pie, log base invalid, no cache match).
- `warnings` mean a reader will struggle (low contrast, two-cell anchor, no alt
  text, truncation, no secondary-axis title).
- `notes` are context (no print area, no title, no explicit font).
- `ok` is only `not errors`; a chart with warnings can still be `ok`.

## Fix patterns

### Stretched / distorted
Convert the anchor:

```json
{"anchors":[{"drawing":1,"anchor":{"mode":"one_cell","width_cm":16,"height_cm":9}}]}
```

The anchor becomes `xdr:oneCellAnchor` with a fixed `xdr:ext`. Row/column edits
no longer change the chart size.

### Secondary axis flat
Set the axis on the **combined** chart, not the primary. In xlsxwriter:

```python
secondary = wb.add_chart({"type": "line"})
secondary.add_series({..., "y2_axis": True})
secondary.set_y2_axis({"min": 0, "max": 240, "major_unit": 20})
primary.combine(secondary)
```

In OOXML, `c:valAx` with `c:axPos="r"` and a matching `c:crossAx` must exist;
the series in the second chart group references that axis pair.

### Pie slices all one colour
Add `c:dPt` entries per point with `c:spPr/a:solidFill/a:srgbClr`. xlsxwriter:
`series["points"] = [{"fill": {"color": ...}}, ...]`.

### Trendline equation over the axis title
Set a manual layout on `c:trendlineLbl`:

```json
{"series":[{"trendline_label_layout":{"x":0.55,"y":0.62,"w":0.4,"h":0.14}}]}
```

Values are fractions of the chart area. Pick the corner with no data.

### Labels clipped at the plot edge
Increase the right/bottom plot margin in `plot_layout`, move labels inside end,
or place the legend outside. Excel does not auto-fit outside-end labels at the
chart frame.

### Chart missing from print
Set `print_area` to include the chart; set landscape/fit; check the anchor's
`to` cell is inside the area.

### Cache says 10, sheet says 12
`c:numCache` is a snapshot. Rebuild the chart or run Excel `CalculateFull` and
save. The audit compares the first cache point with the worksheet; a mismatch
means the chart is lying.

## False positives and limits

- **Pie aspect:** a wide frame is fine when the legend is on the side; the
  audit allows up to 2.2 in that case.
- **Fonts:** if the chart has no explicit `a:defRPr@sz`, the audit cannot see
  the inherited size; it notes rather than fails.
- **Colours:** theme colours (`a:schemeClr`) are not resolved to RGB; only
  explicit `srgbClr` values are contrast-checked.
- **Collision:** label/legend overlap is estimated from counts and sizes, not
  measured glyph boxes. A render is still required.
- **Data cache:** only the first point is compared; a full comparison would
  need to resolve formulas.
- **GridCraft render:** its PDF font may drop Vietnamese diacritics (observed:
  “Thực tế” → “Thc t”). Use Excel `Chart.Export` on Windows for the native
  check; record which renderer produced the image.
- **Excel repair:** the audit cannot prove Excel will not show a repair dialog.
  Open the exact file in Excel and save it once; a repair prompt is a failure.

## Evidence ladder for charts

| Rung | What it proves | Tool |
|---|---|---|
| 0 planned | Spec passes schema | `jsonschema` |
| 1 structural | ZIP/XML valid; chart/axis/series/anchor invariants | `chart_audit.py` |
| 2 library | xlsxwriter/openpyxl reopened the file without error | `openpyxl.load_workbook` |
| 3 GridCraft | GridCraft parsed/rendered the chart | `gridcraft-cli info/convert` |
| 4 Excel-rendered | Excel opened the exact file and exported the chart | `pywin32` `Chart.Export` |
| 5 human | A person reviewed the rendered chart and the data | review note |

Do not call rung 1 “the chart works”. Do not call a GridCraft render “Excel
playback”. They are different evidence.

## Commands

```bash
python3 scripts/chart_audit.py book.xlsx --md audit.md
python3 scripts/chart_patch.py inspect book.xlsx
python3 scripts/chart_patch.py apply book.xlsx patch.json -o fixed.xlsx
```

For the full build/audit/render loop, see `skills/sheet-craft/SKILL.md`.
