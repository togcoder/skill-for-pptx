# Excel chart property matrix

One property, five places to change it. Use this when a library “supports
charts” but the result is still wrong.

- **GridCraft** — `gridcraft-cli run --in book.xlsx --cmd 'id={json}'`.
- **xlsxwriter** — `chart_forge.py` uses this for creation.
- **OOXML** — `xl/charts/chartN.xml` / `xl/drawings/drawingN.xml`.
- **Excel** — VBA/COM object model (`Chart`, `Axis`, `Series`, `PlotArea`).
- **Audit** — what `chart_audit.py` measures.

`—` means no first-class command/API; use OOXML or a library patch.

## Chart identity and data

| Property | GridCraft | xlsxwriter | OOXML | Excel COM/VBA | Audit |
|---|---|---|---|---|---|
| Chart type | `insert.chart={"type":"column"}`; `chart.changeType` | `add_chart({"type":"column"})` | `c:barChart`, `c:lineChart`, … | `Chart.ChartType` | `type` |
| Subtype | `insert.chart={"subtype":"stacked"}` | `add_chart({"subtype":"stacked"})` | `c:grouping`, `c:barDir`, `c:scatterStyle` | `Chart.ChartType` | type/grouping |
| Data range | `chart.selectData={"range":"Data!A1:C7"}` | `categories` / `values` | `c:cat`, `c:val` + `c:numRef/c:f` | `SetSourceData` | cache vs sheet |
| Series name | `chart.set` / `selectData` | `add_series({"name":"=Data!$B$1"})` | `c:ser/c:tx/c:strRef` | `Series.Name` | series names |
| Series values | `chart.selectData` | `add_series({"values":"=Data!$B$2:$B$7"})` | `c:val/c:numRef` | `Series.Values` | cache |
| Add/remove series | `chart.selectData={"removeSeries":[1]}` | one `add_series` per series | `c:ser` | `SeriesCollection.NewSeries/Delete` | count |
| Switch row/column | `chart.switchRowColumn` | `from_rows` / ranges | `c:ser/c:tx` | `PlotBy` | orientation |
| Combo | `insert.chart={"type":"combo"}` | `primary.combine(secondary)` | multiple chart groups in `c:plotArea` | `ChartType` per series | `combo:` |
| Secondary axis | `chart.set` (limited) | `y2_axis: True`; set axis on the secondary chart | second `c:valAx/c:catAx` pair | `Series.AxisGroup = xlSecondary` | axis count |
| Chart style | `chart.set={"style":10}` | `set_style(10)` | `c:style@val` | `Chart.ChartStyle` | style |
| Rounded corners | — | — | `c:roundedCorners@val` | `Chart.RoundedCorners` | not checked |
| Plot visible cells only | — | — | `c:plotVisOnly@val` | `PlotVisibleOnly` | not checked |
| Hidden data | — | `show_hidden_data()` | `c:plotVisOnly` | `PlotVisibleOnly` | not checked |
| Blanks | — | `show_blanks_as("gap")` | `c:dispBlanksAs@val` | `DisplayBlanksAs` | not checked |
| Chart cache | `check` | written automatically | `c:numCache`, `c:strCache` | refreshed on save | cache mismatch |

## Axes

| Property | GridCraft | xlsxwriter | OOXML | Excel COM/VBA | Audit |
|---|---|---|---|---|---|
| Axis title | `chart.addElement={"element":"axisTitles"}` | `set_x_axis({"name":"…"})` | `c:catAx/c:title`, `c:valAx/c:title` | `Axis.HasTitle`, `AxisTitle.Text` | title/unit |
| Min / max | not exposed | `set_y_axis({"min":0,"max":200})` | `c:scaling/c:min`, `c:max` | `Axis.MinimumScale/MaximumScale` | zero baseline, data cut |
| Major/minor unit | not exposed | `major_unit`, `minor_unit` | `c:majorUnit`, `c:minorUnit` | `MajorUnit/MinorUnit` | tick density |
| Log scale | not exposed | `set_y_axis({"log_base":10})` | `c:scaling/c:logBase@val` | `Axis.ScaleType = xlLogarithmic` | base/min |
| Number format | `chart.set` (limited) | `num_format` | `c:numFmt@formatCode` | `Axis.TickLabels.NumberFormat` | format |
| Gridlines | `chart.set={"gridlines":…}` | `major_gridlines` | `c:majorGridlines` | `HasMajorGridlines` | clutter |
| Tick marks | — | `major_tick_mark` | `c:majorTickMark@val` | `MajorTickMark` | — |
| Tick label position | — | `label_position` | `c:tickLblPos@val` | `TickLabelPosition` | — |
| Label rotation | — | `num_font={"rotation":-45}` | `c:txPr/a:bodyPr@rot` | `TickLabels.Orientation` | collision |
| Label font | — | `num_font` | `c:txPr/a:defRPr@sz` | `TickLabels.Font.Size` | ≥8 pt |
| Display units | — | `display_units` | `c:dispUnits/c:builtInUnit` | `DisplayUnit` | unit clarity |
| Date axis | — | `date_axis: True` | `c:dateAx` | `CategoryType = xlTimeScale` | date handling |
| Axis crossing | — | `crossing` | `c:crosses`, `c:crossesAt` | `Crosses`, `CrossesAt` | — |
| Reverse axis | — | `reverse: True` | `c:orientation@val="maxMin"` | `ReverseOrder` | — |
| Multi-level labels | — | — | `c:noMultiLvlLbl@val` | `HasMultiLevelLabels` | readability |

## Series

| Property | GridCraft | xlsxwriter | OOXML | Excel COM/VBA | Audit |
|---|---|---|---|---|---|
| Fill colour | `chart.formatSelection={"series":0,"color":"#…"}` | `fill` | `c:ser/c:spPr/a:solidFill` | `Format.Fill.ForeColor` | contrast |
| Line colour/width | `chart.formatSelection` | `line` | `c:spPr/a:ln` | `Format.Line` | contrast/width |
| Dash style | — | `line={"dash_type":"dash"}` | `a:prstDash@val` | `Line.DashStyle` | — |
| Marker type/size | — | `marker` | `c:marker/c:symbol`, `c:size` | `MarkerStyle/MarkerSize` | distinguishability |
| Marker fill/border | — | `marker.fill/border` | `c:marker/c:spPr` | `MarkerBackgroundColor` | contrast |
| Per-point colour | — | `points` | `c:dPt/c:spPr` | `Points(i).Format` | pie palette |
| Invert if negative | — | `invert_if_negative` | `c:invertIfNegative` | `InvertIfNegative` | — |
| Gap width | not exposed | `gap` | `c:barChart/c:gapWidth` | `GapWidth` | density |
| Overlap | not exposed | `overlap` | `c:barChart/c:overlap` | `Overlap` | stacked |
| Smooth line | — | `smooth` | `c:smooth@val` | `Smooth` | — |
| Trendline | `chart.addElement={"element":"trendline"}` | `trendline` | `c:trendline` | `Trendlines.Add` | presence |
| Trendline equation/R² | `chart.addElement` | `display_equation`, `display_r_squared` | `c:dispEq`, `c:dispRSqr` | `DisplayEquation/DisplayRSquared` | placement |
| Trendline label position | — | not exposed | `c:trendlineLbl/c:layout/c:manualLayout` | `DataLabel.Left/Top` | collision |
| Error bars | — | `y_error_bars` | `c:errBars` | `ErrorBars` | — |
| Data labels | `chart.addElement={"element":"dataLabels"}` | `data_labels` | `c:dLbls` | `HasDataLabels`, `DataLabels` | collision |
| Label position | — | `position` | `c:dLblPos@val` | `Position` | collision |
| Label number format | — | `num_format` | `c:numFmt@formatCode` | `NumberFormat` | units |
| Label separator | — | `separator` | `c:separator` | `Separator` | — |
| Leader lines | — | `leader_lines` | `c:showLeaderLines` | `ShowLeaderLines` | — |
| Pie explosion | — | `points`/`explosion`? | `c:explosion@val`, `c:dPt` | `Explosion` | — |

## Layout, print and accessibility

| Property | GridCraft | xlsxwriter | OOXML | Excel COM/VBA | Audit |
|---|---|---|---|---|---|
| Chart title | `chart.set={"title":"…"}` | `set_title` | `c:title/c:tx/c:rich` | `HasTitle`, `ChartTitle.Text` | insight/length |
| Title font | `chart.set` (limited) | `name_font` | `c:title/…/a:defRPr@sz` | `ChartTitle.Font` | ≥10 pt |
| Legend position | `chart.set={"legend":"bottom"}` | `set_legend({"position":"bottom"})` | `c:legend/c:legendPos@val` | `Legend.Position` | placement |
| Legend overlay | — | not exposed | `c:legend/c:overlay@val` | `Legend.IncludeInLayout` | covers plot |
| Legend font | — | `font` | `c:legend/c:txPr` | `Legend.Font` | ≥8 pt |
| Chart area fill/border | `chart.shapeFill` (shape) | `set_chartarea` | `c:chartSpace/c:spPr` | `ChartArea.Format` | — |
| Plot area fill/border | `chart.shapeFill` | `set_plotarea` | `c:plotArea/c:spPr` | `PlotArea.Format` | — |
| Plot area manual layout | — | `set_plotarea({"layout":{…}})` | `c:plotArea/c:layout/c:manualLayout` | `PlotArea.Left/Top/Width/Height` | overlap |
| Chart frame size | `insert.chart={"width":…,"height":…}` | `set_size` + insert scale | `xdr:ext@cx,@cy` | `ChartObject.Width/Height` | min/aspect |
| Anchor | — | insert at cell | `xdr:twoCellAnchor` / `oneCellAnchor` | `ChartObject.TopLeftCell` | two-cell warning |
| Alt text | — | — | `xdr:cNvPr@descr,@title` | `ChartObject.ShapeRange.AlternativeText` | required |
| Print area | `pageLayout.printArea` | `print_area` | `definedName _xlnm.Print_Area` | `PageSetup.PrintArea` | chart inside |
| Page setup | `pageLayout.pageSetup` | `set_landscape`, `fit_to_pages` | `pageSetup` | `PageSetup` | orientation/scale |
| Data table | `chart.addElement={"element":"dataLabels"}`? | `set_table` | `c:dTable` | `HasDataTable` | readability |
| Up/down bars | — | `set_up_down_bars` | `c:upDownBars` | `HasUpDownBars` | — |
| High-low lines | — | `set_high_low_lines` | `c:hiLowLines` | `HasHighLowLines` | — |
| Drop lines | — | `set_drop_lines` | `c:dropLines` | `HasDropLines` | — |
| 3-D | `insert.chart` may allow | `view3D`? | `c:view3D` | `ChartType` 3D | discouraged |
| Chart sheet | `chart.move` | `add_chart` + `set_chart`? | `xl/chartsheets/` | `Chart.Location` | — |
| Pivot chart | `insert.pivotChart` | not supported | `c:pivotSource` | `Chart.SetSourceData` | — |
| Sparkline | `insert.sparkline` | not supported | `x14:sparklineGroups` | `SparklineGroups` | — |

## Complex chart types

| Type | GridCraft | xlsxwriter | Raw OOXML | Notes |
|---|---|---|---|---|
| Waterfall | not exposed | not supported | `c:waterfallChart`, `c:subtotal` | Needs Excel 2016+; set subtotals and per-point fill. |
| Treemap | not exposed | not supported | `c:treemapChart`, `c:parentLabelLayout` | Multi-level `c:cat`; label only the top levels. |
| Sunburst | not exposed | not supported | `c:sunburstChart` | Same hierarchy rules as treemap. |
| Histogram | not exposed | not supported | `c:histogramChart`, `c:binning` | State bin width/count. |
| Box & whisker | not exposed | not supported | `c:boxWhiskerChart`, `c:quartileMethod` | State method, outliers, mean. |
| Funnel | not exposed | not supported | `c:funnelChart` | Ordered stages; no 3-D. |
| Stock | not exposed | `stock` | `c:stockChart`, `c:hiLowLines`, `c:upDownBars` | Needs Open-High-Low-Close order. |
| Surface | not exposed | `surface` | `c:surfaceChart`, `c:wireframe` | Rarely the right business chart. |
| Pareto | not exposed | combo (column + line) | bar + line on secondary | Sort descending, cumulative % on the second axis. |

For raw types, build the XML skeleton with the required child order and open the
file in Excel. A chart that Excel offers to repair is not done.

## The failure modes this matrix prevents

1. **Stretched chart:** `xdr:twoCellAnchor` → convert to `oneCellAnchor` with a
   fixed `xdr:ext`.
2. **Flat secondary series:** axis set on the primary chart instead of the
   combined secondary chart; the secondary axis stays 0..max.
3. **All pie slices one colour:** no `c:dPt` fills; apply a categorical palette.
4. **Equation over the axis title:** default trendline label position; set
   `c:trendlineLbl/c:layout/c:manualLayout`.
5. **Labels clipped:** data labels outside the plot at the chart edge; increase
   the plot margins or move labels inside.
6. **Wrong numbers:** stale `c:numCache`; recalculate/rebuild and compare.
7. **Chart missing from print:** no print area or chart outside it.
8. **Chart unreadable at 8 pt:** too many categories/series; rotate labels,
   sort, facet, or highlight one series.
