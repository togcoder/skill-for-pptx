# T016 — Real PPTX package data-motion integration

Date: 2026-10-05 Vietnam.

## Result

The chart + KPI path now works structurally through a real PPTX package, not only
through isolated synthetic slide XML.

A deterministic fixture derived from an existing valid repo deck adds a native
ChartML line chart and a standalone KPI, then runs the complete T012–T015 path.

## End-to-end chain

`PPTX package
-> intake inventory
-> semantic Director v0.3
-> semantic-to-execution compiler
-> patch v0.4
-> native chart fan-out + KPI proxy generation
-> output PPTX
-> package/timing read-back`

Presenter rhythm remains:

- click 1: chart;
- click 2: KPI.

## Bug discovered by package testing

The first run failed because the inspector only counted ChartML cache points.
The real fixture uses `c:strLit/c:numLit`, so category count was lost even
though the chart itself was otherwise valid.

This is a meaningful parser bug, not a test-fixture mistake.

The inventory now handles both cache-backed and inline-literal chart data.

## Preservation evidence

After patching:

- slide 2 XML remains byte-identical;
- chart data XML remains byte-identical;
- slide 1 relationship XML remains byte-identical;
- slide count remains unchanged;
- source KPI `98.5%` remains the final source object;
- only targeted slide XML gains counter proxies/timing.

This is the preservation behavior expected from the product target.

## Automated evidence

Initial run:
- 37239157425 — 128 pass / 1 fail;
- failure: literal ChartML category count not inventoried.

Final run:
- 37239255072;
- Python compile pass;
- **130/130 tests pass in 0.366 s**.

## Boundary

No claim of PowerPoint playback is made.

This checkpoint proves package integrity and our structural interpretation only.
A Windows host with Microsoft PowerPoint must still open and play the exact
hashed output before native behavior is promoted.

## Implication

The project has now crossed an important architecture threshold: chart/KPI
semantics are connected all the way to a real PPTX package with source
preservation.

The next research should not add more disconnected recipes. It should either
validate runtime behavior or expand the same semantic->execution discipline to
generic report motions.
