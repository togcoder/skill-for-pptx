# T017 — Generic report motion on an existing deck

Date: 2026-10-05 Vietnam.

## Result

The existing-deck pipeline now supports a first generic semantic vocabulary in
addition to chart/KPI data motion.

The important architectural result is not the effect gallery. It is that one
semantic Director beat can compile to several native stages while preserving the
presenter click boundary.

Examples:

- `stagger-reveal(A,B,C)` -> one click, three automatic entrance stages;
- `focus(A)` -> one click, scale-up then scale-down.

## Native basis

Microsoft documents:

- `p:animEffect` for filter/image transition effects between hidden/visible
  states, including Fade and Wipe; citeturn661394search0turn661394search1
- `p:animScale` for object scale animation. citeturn661394search5

These establish the OOXML mechanisms, not the final PowerPoint playback result.

## Safety decisions

- Charts cannot use generic `shape_entrance`; data semantics remain mandatory.
- Focus is in-place and bounded rather than moving the source object.
- Move/rotate require explicit concrete parameters.
- Unknown operations block their slide.
- Generic compiler does not create helper components implicitly.

## H001 transfer

The real H001 deck is used without rebuilding slide content.

Slide 1:
- existing process resources;
- one presenter click;
- three source-object entrance stages.

Slide 2:
- one presenter click;
- source focus object scale-up;
- automatic return to authored size;
- pre-existing slide transition remains present.

Source inventory vs output inventory confirms original source objects retain text
and normalized geometry.

## Evidence

GitHub Actions run 37239720520:

- Python compile pass;
- **140 tests passed in 0.625 s**.

## Remaining uncertainty

As with T013/T014, XML structure is not PowerPoint playback evidence.

The next bottleneck is native-app validation, not adding another dozen generic
effect names.
