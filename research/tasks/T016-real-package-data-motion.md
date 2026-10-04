# T016 — Real-Package Data-Motion Integration

Status: package-level integration passed; Microsoft PowerPoint playback pending.

## Goal

Move beyond isolated XML roots and prove the T012–T015 data-motion pipeline on a
real PPTX OPC/ZIP package with relationships, content types and unrelated slides.

## Fixture

`scripts/make_data_motion_fixture.py` starts from the repository's valid
`output/PPTX_Motion_Lab_H001.pptx` and modifies only what is required to add:

- one classic ChartML line chart named `Trend Chart`;
- two series;
- four categories;
- one standalone KPI textbox named `Hero KPI` with `98.5%`;
- the slide relationship to the chart part;
- the chart content-type override.

The fixture is not factory/business evidence. It is deterministic synthetic test
data embedded in a real PPTX package.

## Full path exercised

`real PPTX -> inspect_existing_deck -> Director v0.3 -> compile_data_motion_patch
-> patch_existing_timeline v0.4 -> real output PPTX -> inspect/read-back`

Slide 1 Director rhythm:

1. click 1 — reveal native line chart by series;
2. click 2 — stepped-text KPI counter ending on the untouched `98.5%` source
   textbox.

No extra slide is created.

## Real parser failure found

The first T016 CI run 37239157425 failed 1/129 tests.

The fixture used valid inline ChartML data:

- `c:strLit` for categories;
- `c:numLit` for values.

The inventory helper only counted referenced cache containers:

- `strCache`;
- `numCache`;
- `multiLvlStrCache`.

Therefore the chart was correctly recognized as a line chart with two series but
its `category_count` was incorrectly reported as null.

The test was not weakened.

The parser now counts points in both referenced caches and inline literal
containers, including `strLit`, `numLit` and multilevel data forms. A direct
regression was added.

## Final automated evidence

GitHub Actions run 37239255072:

- Python compile pass;
- **130 tests passed in 0.366 s**.

The real-package regression proves structurally:

- package inventory reports no errors;
- chart type = line;
- series count = 2;
- category count = 4;
- KPI numeric value = 98.5;
- Director -> patch compiler succeeds;
- output keeps two presenter click groups;
- chart build read-back = series, `animBg=0`;
- chart sub-targets read back series 0 then series 1;
- source KPI text remains exactly `98.5%`;
- generated counter proxies exist;
- source/output SHA-256 differ;
- source/output slide counts are equal;
- untouched slide 2 XML is byte-identical;
- chart data part is byte-identical after timing patch;
- slide 1 relationship part is byte-identical after timing patch.

## Evidence boundary

This is substantially stronger than isolated timing-unit evidence, but it is
still not Microsoft PowerPoint runtime evidence.

It does not prove:

- the chart plays in the expected visual sequence;
- entrance effects hide counter proxies before activation;
- the file opens in retail PowerPoint without repair;
- Animation Pane order matches our structural interpretation.

Those remain exact-file playback gates.

## Reusable rule

Never infer chart data dimensions only from `*Cache` nodes. Classic ChartML may
store data inline in `*Lit` containers. Inventory must support both.

## Next

With semantic, compiler, native writer and real-package integration connected,
the largest remaining gaps are:

1. Microsoft PowerPoint runtime QA;
2. execution contracts for non-data Director operations such as generic reveal,
   focus/emphasis and source-object movement;
3. T009 autonomous no-script evaluation on a real report.
