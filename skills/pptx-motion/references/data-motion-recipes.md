# Data-motion recipes — charts and standalone KPI numbers

This reference defines semantic animation defaults for data-bearing objects.
Read it after deck inventory and before low-level timing authoring.

The goal is not to animate every chart or every number. Motion must preserve the
meaning of the encoding and the presenter click rhythm.

## Evidence

Microsoft PowerPoint exposes chart animation granularity separately from ordinary
shape animation. Reviewed sources:

- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.animationsettings.chartuniteffect
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.ppchartuniteffect
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.buildchart?view=openxml-3.0.1
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.animationchartonlybuildvalues?view=openxml-3.0.1

PowerPoint supports chart builds by series, category, series element and category
element. OOXML stores the build mode in `a:bldChart`; `animBg` controls whether
background elements such as grid lines / legend participate in the build.

For numeric counters, the reviewed PowerPoint APIs expose text/object animation
but no verified primitive that interpolates a text number from one numeric value
to another. Microsoft's own on-screen timer example uses multiple number text
boxes animated in sequence:

- https://support.microsoft.com/en-us/powerpoint/create-an-on-screen-timer

Therefore count-up/count-down is treated as a synthesized editable component
until a true native numeric interpolation mechanism is proven.

## Inventory semantics

`scripts/inspect_existing_deck.py` records:

For charts:

- `primary_type`;
- all detected chart types for combo charts;
- series count;
- category count;
- point count;
- bar/column orientation and grouping where available.

For text shapes:

- `data_semantics.standalone_number` when the entire visible text is essentially
  one numeric value with an optional prefix/suffix.

Examples accepted as counter candidates:

- `98.5%`
- `$12,345`
- `250 ppm`
- `3.2M`

Examples deliberately not accepted automatically:

- `OEE 98.5%`
- `Target: 95`
- table cells merely because they contain numbers;
- axis labels;
- dates/page numbers unless the Director explicitly reclassifies them.

A counter candidate is not automatically a hero metric.

## Chart recipe matrix

These are semantic defaults, not immutable visual presets.

| Chart type | Default recipe | Default internal build | Motion meaning |
| --- | --- | --- | --- |
| Column | `baseline-grow` | single series: category elements; multi-series: series | Magnitude grows from the value baseline |
| Bar | `baseline-grow` | single series: category elements; multi-series: series | Horizontal magnitude reveals from baseline |
| Line | `series-trace` | series | Preserve ordered x-axis progression |
| Area | `area-reveal` | series | Reveal ordered trend while preserving magnitude |
| Pie | `segment-sweep` | category elements | Reveal parts of the whole around the circle |
| Doughnut | `segment-sweep` | category elements | Same part-to-whole logic as pie |
| Scatter | `point-build` | single series: series elements; otherwise series | Reveal observations without inventing an ordered path |
| Bubble | `point-build` | single series: series elements; otherwise series | Pop/reveal points while preserving encoded position and bubble size |
| Radar | `radial-series-build` | series | Compare complete profiles, not isolated vertices |
| Stock | `ordered-category-build` | category | Preserve time/category order |
| Combo | `layered-series-build` | series | Reveal one encoding/layer before another |
| Unknown/extended | `semantic-build` | as whole | Conservative fallback until subtype-specific behavior is verified |

Default `animate_background=false`: axes, grid, legend and plot context should
normally establish the frame before the data marks animate.

A stronger script may override the default recipe/build, but the Director must
record `override_reason`.

## Standalone number counter

Use a counter only when the number is narratively important: a hero KPI, final
result, delta, achievement, target attainment, or another metric whose numeric
landing is itself part of the story.

Default plan:

- start at 0;
- count toward the exact source numeric value;
- preserve prefix, suffix, decimal precision and final visible source text;
- keep the whole count within the click beat that reveals/highlights the KPI;
- do not create extra presenter clicks for internal number steps.

### Preferred implementation: odometer proxy

For large hero metrics, synthesize editable digit/text proxies and move/change
them behind a mask-like surface so the number feels like a real counter rather
than a rapid list of text replacements.

This requires a component insertion backend and exact PowerPoint QA.

### Fallback implementation: stepped text

Create a small number of intermediate text states and sequence them automatically
inside one click beat, ending on the untouched source value.

This mirrors the general mechanism Microsoft documents for a countdown using
multiple number textboxes, but remains our synthesized count-up implementation,
not a built-in PowerPoint numeric tween.

## Click rhythm

Data-motion is subordinate to narrative click rhythm.

Examples:

- Click 1: establish axes + reveal the chart trend.
- Hold while presenter explains.
- Click 2: count the hero KPI to its final value.

But if the KPI is the conclusion of the chart reveal and should land immediately
with it, the chart and counter may share one click beat using after/with-previous.

Never use a long numeric animation delay as a substitute for presenter speech.

## Validation

Director v0.3 requires chart-targeting motion beats to declare `data_motion`
and validates chart type/build/recipe against inventory recommendations unless
an explicit override reason exists.

For KPI highlight operations, a standalone numeric target requires
`number-counter` data motion, and the counter target value must match the source
number exactly.

## Current implementation boundary

Implemented:

- chart subtype/dimension inventory for classic ChartML charts;
- standalone numeric candidate parsing;
- deterministic chart/counter recipe selector;
- Director v0.3 semantic validation.

Pending:

- native chart-build writer/fan-out and PowerPoint playback matrix;
- extended Office chart (`cx:chart`) subtype inventory;
- odometer component insertion;
- stepped-text counter writer;
- exact-file PowerPoint playback for both families.
