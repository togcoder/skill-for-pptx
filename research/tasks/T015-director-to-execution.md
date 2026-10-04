# T015 — Director-to-Execution Compiler

Status: safe data-motion bridge implemented; mixed generic motion remains blocked.

## Goal

Remove the manual JSON gap between semantic Director v0.3 and low-level
existing-deck patch v0.4.

The compiler must preserve presenter click rhythm while converting supported
chart/KPI semantic beats into executable native timing effects.

## Implemented

`scripts/compile_data_motion_patch.py`:

- validates Director plan against the exact inventory;
- resolves source targets by stable inventory identity;
- chart data motion -> `chart_entrance`;
- KPI counter -> `number_counter`;
- carries Director click groups into patch click groups;
- chooses bounded chart stage duration from build density;
- records odometer -> stepped-text fallback explicitly;
- can forbid fallback;
- blocks a slide if any motion beat on that slide is unsupported/mixed.

## Safety rule

The compiler never removes unsupported beats and then pretends the click rhythm
is preserved.

A slide is compiled only when all its Director motion beats are supported by the
current bridge. Otherwise it is reported as blocked.

This is intentionally conservative until generic focus/move/diagram operations
also have a fully specified Director-to-stage mapping.

## Counter fallback

T012 semantic planning may prefer `odometer-proxy`, but T014 currently
implements only `stepped-text`.

The compiler records:

- requested implementation;
- effective implementation;
- fallback boolean;
- fallback reason.

If `allow_fallback=false`, compilation aborts rather than silently changing the
requested behavior.

## Integration evidence

Temporary GitHub Actions:

- first run 37238823694: one test failed because the test assumed the first
  `bldLst` entry must be the chart; adding counter proxy `bldP` entries makes
  build-list order heterogeneous. Production code was correct.
- repaired test locates `bldGraphic` by type/spid instead of list position.
- final run 37238859486:
  - Python compile pass;
  - **126 tests passed in 0.339 s**.

The end-to-end synthetic fixture proves:

`Director v0.3 -> patch v0.4 -> chart + counter writer -> timing read-back`

with two presenter click groups preserved.

## Boundary

This compiler currently supports complete data-motion slides only.

It does not yet compile arbitrary Director operations such as generic focus,
reposition, connector reveal or compound diagrams because those semantic beats
do not yet carry enough concrete geometry/effect parameters to generate a safe
low-level patch.

Do not guess those missing parameters in the compiler.

## Next

1. exact-file PowerPoint playback fixtures for chart + KPI;
2. add a concrete execution contract to generic Director operations before
   extending the compiler;
3. then run T009 no-script benchmark through the real bridge.
