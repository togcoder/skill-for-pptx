# T012 — Semantic Data Motion: Charts and KPI Counters

Status: semantic/inventory implementation complete; native execution pending.

## User requirement

When the deck contains charts, animation must depend on the **chart type and data
encoding**, not treat the chart as a generic rectangle.

When a standalone number is narratively important and needs highlighting, it
should use a dedicated count-up/count-down animation.

## Architecture

`Inventory -> Data Semantics -> Director Recipe -> Click Beat -> Native Execution`

Data motion is subordinate to presenter click rhythm.

## Implemented in T012

- classic ChartML subtype inventory:
  - column/bar;
  - line;
  - pie/doughnut;
  - area;
  - scatter/bubble;
  - radar/stock/surface;
  - combo when more than one chart encoding is present;
- series/category/point counts where cached data exists;
- standalone numeric candidate parser with prefix/suffix/value preservation;
- deterministic recipe selector in `scripts/data_motion_recipes.py`;
- Director contract v0.3;
- validator requiring chart-specific data motion and protected KPI counter values;
- recipe documentation in `skills/pptx-motion/references/data-motion-recipes.md`.

## Default chart semantics

- column/bar -> baseline-grow;
- line -> series-trace;
- pie/doughnut -> segment-sweep;
- area -> area-reveal;
- scatter/bubble -> point-build;
- combo -> layered-series-build;
- unknown -> conservative semantic-build.

PowerPoint supports chart internal builds by series/category/elements. The
recommended chart build is chosen separately from visual effect family.

## Counter semantics

Standalone numeric text is only a candidate. The Director decides whether it is
a hero metric.

When highlighted:

- preserve exact source final value;
- preserve prefix/suffix/decimal precision;
- default from 0 toward the source value;
- keep intermediate numeric steps inside one presenter click;
- preferred implementation: odometer proxy;
- fallback: stepped text.

## Acceptance reached

GitHub Actions run 37236839744:

- Python compile pass;
- **103 tests pass**.

Tests cover:

- standalone number parsing and rejection of labeled sentences;
- column chart XML inventory;
- different line/pie/scatter recipes;
- counter formatting;
- Director v0.3 valid plan;
- chart data-motion requirement;
- type-recipe mismatch rejection unless explicitly overridden;
- hero KPI counter requirement;
- source-value protection.

## Remaining execution work

T012 does not yet claim final native chart/counter playback.

Next:

1. implement PowerPoint-authored-style `p:bldGraphic/a:bldChart` chart builds;
2. build a chart fan-out fixture by series/category/elements;
3. implement stepped-text counter insertion first;
4. implement odometer proxy after stepped-text exact-file playback is known;
5. run a matrix across at least column, line, pie and scatter;
6. exact-file Microsoft PowerPoint playback before promoting any recipe.
