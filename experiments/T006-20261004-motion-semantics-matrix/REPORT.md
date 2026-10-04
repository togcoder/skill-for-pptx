# T006 — Motion origin/fill semantics matrix

Date: 2026-10-04 UTC / 2026-10-05 Vietnam. Owner: Codex /root.
Base: ad707aa77408cae07c4e744598f7284c57c05ed9.
Branch: work/T006-motion-semantics-matrix-20261004, PR #12.

## Decision

Freeze the four-file matrix and its playback checklist. Do not change the
production timing writer yet. Static and structural evidence separates the two
variables cleanly, but no PowerPoint playback was available to identify a
correct native interpretation.

The leading repair hypothesis is authored-layout anchoring plus hold. It remains
a hypothesis, not the default backend.

## Controlled question

One native circle starts at A=(0.20,0.55), moves to B=(0.45,0.55) for 900 ms,
then moves to C=(0.70,0.55) for 900 ms. Both effects stay in one slide and one
packed click group. Visible target rings make a jump/reset easy to observe.

The 2×2 matrix changes only:

1. path coordinates relative to each stage start vs relative to the authored
   layout center; and
2. behavior time-node fill equal to remove vs hold.

All variants retain origin=layout, pathEditMode=relative, one clickEffect group,
delays 0/900 ms, durations 900/900 ms, the same target spid, timing IDs, shapes,
text, notes and package parts.

## Exact outputs

| Variant | Stage 2 path | Behavior fill | SHA-256 |
|---|---|---|---|
| local-remove | M 0 0 L 0.25 0 E | remove | eefbaab33d9e355462999dee123ac946e1c166a3db32524a49469a91f949b218 |
| local-hold | M 0 0 L 0.25 0 E | hold | dbe4807e308fdcb33744819f29a462a1198f3ce1eb1fa85c4b6a2a13edf2ecdc |
| anchored-remove | M 0.25 0 L 0.50 0 E | remove | 67b81d46adf74e6ab830b48685a6486bbb168e6b6f1876f18a21a6672b353a6d |
| anchored-hold | M 0.25 0 L 0.50 0 E | hold | 4ccab14b4b263cb35668f20e7e0a8047572790cc188db5af783120feaa0f1aad |

The files are under output/T006_motion_semantics_*.pptx.

## Machine evidence

- Four finalizers: package integrity pass, first-party import pass, zero layout
  findings and zero layout warnings.
- Exact-file audit: no findings.
- All non-slide package parts match across variants.
- After normalizing only p:animMotion@path and the corresponding behavior
  p:cTn@fill, canonical slide XML matches across all four.
- Four final PNGs have the identical SHA-256
  1c19f38221f708bb64d96100e4f8645b8a56847b90648c13ff18b37ca11b4e4e.
- Full repository suite: 83 tests passed. Python compile and Node syntax pass.

This proves experimental control and package loadability, not animated behavior.

## Static inspection

Viewed every exact final slide at 1280×720. The orange mover at A, blue B ring,
green C ring, title and labels are crisp and unclipped. The four initial views
are pixel-identical as intended. Static fixture clarity: 5/5, subjective author
review. Motion continuity/editability score: null. No overall score.

Static rendering shows only A. It cannot reveal the 900 ms endpoint, stage-2
start, final persistence or Animation Pane behavior.

## Primary sources

Microsoft sources inspected 2026-10-04 UTC:

- https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/498c3cfa-652c-49b3-a82c-33fd94468af8
  documents path commands, normalized slide coordinates and PowerPoint defaults.
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.animatemotion?view=openxml-3.0.1
  distinguishes the motion origin from path edit mode.
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.commonbehavior?view=openxml-3.0.1
  exposes additive/accumulation controls. This matrix deliberately leaves both
  unspecified to isolate path anchoring and time-node fill first.

Microsoft authored the documentation. It was read as mechanism evidence; no
Microsoft code or media was copied. Documentation copyright/terms apply. The
fixture, scripts and synthetic visuals are independently authored.

The documents do not establish the actual two-stage result of these generated
files. Native observation remains mandatory.

## Reproduce

Use fresh paths because all writers refuse overwrite. Run the host Presentations
marker once, then:

1. Run scripts/run_timeline_experiment.sh on plan.json to a fresh source build.
2. Run scripts/make_motion_semantics_matrix.py on the generated timeline.pptx.
3. Export RUNTIME_NODE_MODULES and run finalize_motion_semantics_matrix.mjs.
4. Run scripts/audit_motion_semantics_matrix.py on the output directory.
5. Run python3 -m unittest discover -s tests -v.

## Playback handoff

Use playback-checklist.json. Open each exact hash without resaving, record the
PowerPoint version and repair warning, start Slide Show, click once, and capture:

- near 900 ms: circle at B;
- stage-2 start: no jump back to A;
- near 1800 ms: circle at C;
- after waiting: circle remains at C;
- Animation Pane: both effects remain editable.

Record all four outcomes, including failures. A single passing variant may
justify a production-writer change, but the full T006 candidate must then be
rebuilt as a new revision and played again. Do not extrapolate native acceptance
from this minimal fixture.

## Useful failures and scope limits

Two host-pipeline wiring failures are kept in failures.md; both were corrected
without changing the PPTX hypothesis. No quota error occurred.

This experiment does not validate scale, rotation, entrance/exit, easing,
existing-timing merge, complex choreography, or a fresh prompt. It does not
update the source skill because no behavior improvement has PowerPoint evidence.
