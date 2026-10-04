# T017 — Generic Report Motion Primitives

Status: structural existing-deck execution implemented; PowerPoint playback pending.

## Goal

Extend the semantic->execution path beyond charts/KPIs so ordinary report slides
can use a small, defensible motion vocabulary without inflating slide count.

## Director v0.4 vocabulary

Supported ordinary operations:

- `reveal`
- `stagger-reveal`
- `process-reveal`
- `focus`
- `emphasize`
- `move` with explicit path points
- `rotate` with explicit degrees

Charts remain data-motion resources and cannot fall back to generic reveal.

## Execution rules

### Reveal

Ordinary shapes/pictures/text default to Fade. Connectors default to a restrained
Wipe. Multiple reveal targets preserve target order and expand to sequential
`after-previous` stages inside the same presenter click.

### Focus

A focus/emphasis beat expands to two scale stages:

1. authored size -> conservative larger size;
2. automatically return to authored size.

The scale factor is bounded by slide-edge clearance and capped at 1.08.

### Move / rotate

The compiler does not invent destination geometry.

- move requires explicit normalized `motion_parameters.points`;
- rotate requires explicit finite `motion_parameters.by_deg`.

## Patch v0.5

Adds `shape_entrance` using native `p:animEffect`.

The low-level writer rejects chart targets for `shape_entrance`; charts must use
`chart_entrance`.

Microsoft Open XML documentation identifies `p:animEffect` as the element for
filter-based hidden/visible effects and `p:animScale` as object scale
animation. These mechanisms support the structural baseline. Playback remains a
separate gate.

## Transfer test

The repository H001 PPTX is used as a real existing-deck transfer:

- slide 1: one presenter click -> three staggered source-object reveals;
- slide 2: one presenter click -> focus scale-up -> scale-down;
- no slide inflation;
- existing transition preserved;
- original text and geometry preserved.

## Automated evidence

Temporary GitHub Actions run 37239720520:

- Python compile pass;
- **140 tests passed in 0.625 s**.

Coverage also checks:

- focus scale edge bounding;
- semantic beat -> multiple concrete stages;
- explicit move path requirement;
- unsupported operation blocks a slide instead of partial execution.

## Boundary

Entrance visibility and scale playback still require Microsoft PowerPoint.

This task establishes semantic planning, native timing structure, real-package
source preservation and transfer—not observed slideshow behavior.

## Next

The highest-value next task is a Windows/Microsoft PowerPoint QA harness that can
open an exact hashed artifact through the native application, inventory its
Animation Pane semantics via COM, run controlled slideshow clicks, and write a
machine-readable acceptance record.
