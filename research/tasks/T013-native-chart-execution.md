# T013 — Native Chart Motion Execution

Status: structural writer implemented; PowerPoint playback pending.

## Goal

Compile T012 semantic chart recipes into native PresentationML timing without
turning the chart into a bitmap or generic shape.

## Native mechanism

A chart entrance uses:

- existing chart graphicFrame shape ID;
- `p:animEffect` entrance behaviors;
- optional chart sub-target:
  `p:spTgt/p:graphicEl/a:chart`;
- `seriesIdx`, `categoryIdx`, `bldStep` for fan-out;
- `p:bldGraphic/p:bldSub/a:bldChart` for chart build policy.

Microsoft Open XML documentation confirms these chart-animation fields.

## Implemented

- `scripts/chart_native_timing.py`
  - build-mode normalization;
  - fan-out enumeration;
  - chart-type -> conservative entrance filter;
  - density guard.
- `existing-deck-timeline-patch` v0.3
  - `chart_entrance`;
  - chart-target validation;
  - native chart sub-target emission;
  - `bldGraphic/bldChart` emission;
  - requested/effective build receipt.
- existing-deck timing inventory reads back:
  - chart sub-target series/category/build step;
  - chart build mode;
  - animate-background flag.

## Density guard

PowerPoint can represent very large point-level chart builds, but generating one
behavior per point is not automatically good presentation design.

Default fan-out limit: 24.

When a requested element-level build exceeds the limit:

- element-level -> series where possible;
- otherwise -> as-whole.

The receipt must report degradation and reason.

## Evidence

Temporary GitHub Actions run 37238145782:

- Python compile pass;
- **112 tests passed in 0.551 s**.

New tests prove structurally:

- series/category-element fan-out ordering;
- density degradation;
- type-specific concrete filters;
- v0.3 patch validation;
- chart target rejection on a normal shape;
- six native sub-targets for a 2-series × 3-category chart;
- `bldGraphic/bldChart bld="categoryEl" animBg="0"`;
- read-back of series/category/build-step and build list;
- chart behavior count in receipt.

## Boundary

No exact Microsoft PowerPoint playback has been observed yet.

Do not claim that:

- `wipe(up)` on a chart behaves exactly like PowerPoint UI Wipe;
- chart sub-elements sequence exactly as intended;
- density-degraded output is visually superior;

until exact-file playback is captured.

## Next

1. Build real PPTX fixtures for column, line, pie and scatter.
2. Freeze file hashes.
3. Open exact files in PowerPoint and record Animation Pane + click behavior.
4. Then implement T014 counter components using stacked source-style text proxies
   and sequential exits inside one click beat.
