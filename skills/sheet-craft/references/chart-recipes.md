# Chart recipes

Each recipe states the question, the data shape, the settings and the failure
check. Values are starting points; tune within the bands in
`domains/xlsx/data/spreadsheet_system.json`.

## 1. Column + line, secondary axis (actual vs target)

**Question:** how does actual compare with target over time, when the two
series are on different scales?

**Data:** month | actual | target.

**Settings:**

```json
{
  "type": "combo",
  "axes": {
    "x": {"title": "Tháng", "label_rotation": -45, "label_size": 9},
    "y":  {"title": "Thực tế (index)", "min": 0, "max": 240, "major_unit": 20, "number_format": "#,##0"},
    "y2": {"title": "Mục tiêu (index)", "min": 0, "max": 240, "major_unit": 20, "number_format": "#,##0"}
  },
  "series": [
    {"type": "column", "column": 1, "color": "#1F4E79", "gap": 55},
    {"type": "line", "column": 2, "axis": "secondary", "color": "#C55A11",
     "marker": "circle", "line_width": 2.5}
  ]
}
```

**Why:** a line on the same axis would be flattened by the bars; a second
column chart would be unreadable. Title both axes, otherwise the reader cannot
tell the units.

**Fail:** secondary axis starts at 0 while the primary starts at 100 (set y2 on
the **combined** chart, not the primary); line labels collide with bars (label
only the endpoints or use a table).

## 2. Sorted horizontal bar (ranking)

**Question:** which categories lead?

**Data:** category | value. Sort descending before charting.

**Settings:** horizontal bar; value axis min 0; category axis reverse order so
the largest is on top; data labels outside end; no legend; gridlines off;
category width ≥ 1 cm.

**Fail:** alphabetical order; a 3-D bar; labels clipped at the right edge
(increase the plot width or place labels inside end).

## 3. Line (trend over time)

**Question:** how did the value change over time?

**Data:** ISO date | value(s). Use a date axis, not text categories.

**Settings:** line, 2.5 pt, markers only for ≤12 points; y-axis title with unit;
major unit chosen from the data range (5–8 gridlines); no data labels on every
point; highlight one series with colour and keep the rest grey.

**Fail:** connecting unordered categories; a smoothed line that invents values
between points; 12 series in 8 colours.

## 4. 100% stacked bar (composition over time)

**Question:** how did the mix change?

**Data:** period | segment A | segment B | …; values sum to 100 or are converted.

**Settings:** stacked 100; one categorical palette; legend bottom; data labels
only for segments >5%; 3–6 segments max; direct labels if the segments are
stable.

**Fail:** too many thin segments; a rainbow; no total/percentage context.

## 5. Doughnut (part of a whole, small N)

**Question:** what are the shares of 2–5 parts?

**Settings:** doughnut hole 50–60; categorical `c:dPt` fills; labels show
percent only; legend right; no 3-D; title states the total.

```json
{"type": "doughnut", "post": {"doughnut_hole": 55, "pie_rotation": 0},
 "series": [{"data_labels": {"show_percent": true, "position": "best_fit"}}]}
```

**Fail:** all slices one colour; value + percent duplicated; >7 slices; slices
not summing to 100%; a legend that repeats every label.

## 6. Scatter + trendline (correlation)

**Question:** is X associated with Y?

**Data:** numeric X | numeric Y (not text categories). For bubble, add size.

**Settings:** markers 6–8 pt; x/y axis titles with units; min/max chosen from
the data (not always 0); trendline only when the relationship is the message;
equation/R² in a free corner, not over the axis title; no connecting line
unless the points are ordered.

```json
{"type": "scatter", "subtype": "markers",
 "series": [{"column": 2, "x_column": 1, "marker": "circle",
             "trendline": {"type": "linear", "display_equation": true,
                           "display_r_squared": true},
             "trendline_label_layout": {"x": 0.55, "y": 0.62, "w": 0.4, "h": 0.14}}]}
```

**Fail:** text categories on X (points collapse to 1..N); a trendline implying
causation; R² hidden behind the y-axis title.

## 7. Waterfall (bridge)

**Question:** which contributions moved the total from A to B?

**Data:** step | delta, with the start/end as totals.

**Settings:** `c:waterfallChart`; `c:subtotal` on the totals; increase colour
`#548235`, decrease `#C00000`, total `#1F4E79`; data labels; no 3-D.

**Raw OOXML:** xlsxwriter does not create waterfall charts. Build
`c:waterfallChart`, `c:ser` with `c:cat`/`c:val`, and set `c:subtotal` for the
total points; validate by opening in Excel.

**Fail:** totals treated as deltas; no colour legend; a bridge that does not
close to the stated end value.

## 8. Histogram (distribution)

**Question:** how are values distributed?

**Data:** one numeric column.

**Settings:** `c:histogramChart`; state bin width/count; no gaps; y-axis
“Số quan sát”; x-axis the measured variable with unit; do not use it for
categories.

**Raw OOXML:** `c:histogramChart` + `c:binning` (`c:binWidth` or `c:binCount`,
`c:underflow`, `c:overflow`).

**Fail:** using a bar chart of pre-binned counts without saying so; unequal bin
widths without labels; a log axis with no note.

## 9. Box & whisker (distribution comparison)

**Question:** how do groups compare in median, spread and outliers?

**Settings:** `c:boxWhiskerChart`; `c:quartileMethod` exclusive/inclusive;
show outliers; show mean marker if the mean matters; category labels with units.

**Fail:** hiding outliers to make the chart look clean; not stating the
quartile method; using it for 3 points.

## 10. Bullet (KPI vs target)

**Question:** is the KPI on target?

**Data:** actual | target | bands (optional).

**Settings:** horizontal bar for the actual, a target marker/line, band fills
in light grey; value axis starts at 0; one number label; no gauge.

**Fail:** a speedometer/gauge with a needle that is harder to read than a bar;
a truncated axis.

## 11. Small multiples (many series)

**Question:** how does the pattern differ across groups?

**Settings:** one small chart per group, identical axes and colour scale, 2×3
or 3×2 grid, shared title. Do not put 20 series in one chart.

**Fail:** inconsistent scales; too many panels; a legend repeated 6 times.

## 12. Pareto (80/20)

**Question:** which few causes explain most of the effect?

**Settings:** sorted column (descending) + cumulative % line on a secondary
axis fixed 0–100%; mark the 80% line; show the cumulative label only at the
crossing.

**Fail:** unsorted bars; a cumulative line on the same 0..max scale; no 80%
reference.
