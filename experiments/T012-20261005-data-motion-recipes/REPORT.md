# T012 — Semantic data motion for charts and KPI numbers

Date: 2026-10-05 Vietnam.

## User requirement

Charts must not receive one generic animation. Their motion should depend on the
chart type and the meaning of its encoding.

Standalone numbers that are narratively important should have a dedicated
count-up/count-down treatment.

## External mechanism evidence

Microsoft PowerPoint exposes chart build granularity independently from ordinary
shape animation:

- by series;
- by category;
- by series elements;
- by category elements;
- all at once.

PowerPoint/Open XML stores chart build behavior through `a:bldChart`; the
`animBg` flag controls whether background chart elements participate.

Microsoft sources reviewed:

- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.animationsettings.chartuniteffect
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.ppchartuniteffect
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.buildchart?view=openxml-3.0.1
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.animationchartonlybuildvalues?view=openxml-3.0.1

For numeric counters, no reviewed PowerPoint animation API provides a verified
numeric text interpolation primitive. Microsoft's documented on-screen timer uses
multiple number text boxes animated in sequence:

- https://support.microsoft.com/en-us/powerpoint/create-an-on-screen-timer

Therefore numeric counting is treated as a synthesized editable component, not a
claim about a built-in PowerPoint number tween.

## Inventory upgrade

`scripts/inspect_existing_deck.py` now reads classic ChartML references and
records per chart:

- chart subtype(s);
- primary type;
- series count;
- category count;
- point count;
- bar direction and grouping where present.

It also records `data_semantics.standalone_number` for text that is essentially
one numeric value with optional prefix/suffix.

Examples:

- accepted: `98.5%`, `$12,345`, `250 ppm`;
- rejected: `OEE 98.5%`, `Target: 95`.

The rejection is intentional: parsing a numeric token inside ordinary prose is
not enough evidence that it is a hero KPI.

## Recipe selector

Added `scripts/data_motion_recipes.py`.

Defaults:

| Type | Recipe |
| --- | --- |
| Column | baseline-grow |
| Bar | baseline-grow |
| Line | series-trace |
| Area | area-reveal |
| Pie/Doughnut | segment-sweep |
| Scatter/Bubble | point-build |
| Radar | radial-series-build |
| Stock | ordered-category-build |
| Combo | layered-series-build |
| Unknown | semantic-build |

Each recipe also recommends chart internal build granularity.

Counter recipe preserves source:

- target value;
- prefix;
- suffix;
- decimal precision;
- final source text.

The output includes preferred `odometer-proxy` and fallback
`stepped-text` implementation choices.

## Director v0.3

The semantic Director now treats chart/KPI animation as first-class data motion.

Chart-targeting beats require:

- inventory chart type;
- type-specific recipe;
- chart build;
- background-animation policy;
- rationale.

A nonstandard recipe/build requires an explicit override reason.

Standalone numeric shapes remain only candidates. When the Director chooses one
as a hero metric via a KPI/highlight operation, a number-counter data-motion block
is required.

The counter target value must equal the source numeric value. An animation plan
cannot silently turn 98.5% into 99.9%.

Data motion stays inside the narrative click beat selected by T010/T011.

## Automated evidence

Temporary GitHub Actions run 37236839744:

- Python compile: pass;
- **103 tests passed in 0.713 s**.

New tests verify:

- numeric parsing with formatting;
- rejection of sentence-style numbers;
- counter format preservation;
- ChartML column chart inventory;
- distinct line/pie/scatter recommendations;
- conservative unknown-chart fallback;
- valid Director v0.3 data-motion plan;
- chart target without data-motion fails;
- wrong chart recipe fails without override;
- hero KPI without counter fails;
- counter source-value mutation fails.

## Current boundary

This experiment proves inventory, semantic selection and validation. It does not
yet prove native chart or counter playback.

Next execution research:

1. PowerPoint-authored-style chart build writer using `p:bldGraphic` /
   `a:bldChart`;
2. chart sub-element fan-out tests;
3. stepped-text counter component insertion;
4. odometer proxy after fallback is playback-safe;
5. exact-file PowerPoint matrix for column, line, pie, scatter and KPI counter.
