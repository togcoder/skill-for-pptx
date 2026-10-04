# T013 — Native chart motion execution

Date: 2026-10-05 Vietnam.

## Result

T012's chart semantics now have a low-level structural execution path for an
existing unanimated slide.

The writer does not rasterize or rebuild the chart. It targets the existing
chart graphicFrame by exact source ID + name.

For per-series/category builds it emits chart sub-targets under the animation
behavior:

`p:spTgt -> p:graphicEl -> a:chart`

with:

- `seriesIdx`
- `categoryIdx`
- `bldStep`

and emits the chart build policy under:

`p:bldLst -> p:bldGraphic -> p:bldSub -> a:bldChart`.

Microsoft documents these fields as chart animation build controls. citeturn791313search1turn791313search6

## Concrete filters

The structural prototype maps chart semantics to conservative entrance filters:

- column -> `wipe(up)`
- bar -> `wipe(right)`
- line/area/stock -> `wipe(right)`
- pie/doughnut -> `wheel(1)`
- scatter/bubble/combo -> `fade`
- radar -> `circle(in)`

These mappings are hypotheses to verify in PowerPoint, not final aesthetic
truth.

## Density guard

Point-level animation can explode in size. T013 defaults to a 24-subtarget
fan-out ceiling.

A 4-series × 100-category `series-elements` request therefore degrades to four
series targets rather than 400 point behaviors. The receipt exposes requested
build, effective build, degradation boolean and reason.

## Automated evidence

GitHub Actions run 37238145782:

- Python compile pass;
- **112 tests passed in 0.551 s**.

A synthetic chart slide test emits:

- one presenter click beat;
- six `p:animEffect` chart sub-target behaviors for 2×3 category-elements;
- `a:bldChart bld="categoryEl" animBg="0"`;
- `wipe(up)` for a column chart;
- read-back of all six series/category targets.

The same tests verify rejection when the target is not a chart.

## Evidence boundary

This is package/timing structure evidence only.

Actual PowerPoint playback remains pending. Exact-file native QA must establish:

- chart is hidden/revealed at the correct moment;
- sub-elements play in intended order;
- background/axes remain stable when `animBg=0`;
- presenter click count remains correct;
- Animation Pane reflects the intended build;
- file opens without repair.

## Next hypothesis

For KPI counters, prefer a stack of cloned source-style number text shapes above
the untouched final source value. The top value begins visible; automatic exit
animations reveal successive values below it, ending on the original source
shape.

This avoids pretending that PowerPoint has a native numeric tween and mirrors
Microsoft's documented multi-textbox countdown pattern. citeturn791313search0
