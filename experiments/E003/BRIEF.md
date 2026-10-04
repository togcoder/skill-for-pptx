# E003 — Cyclic three-mode routing

Frozen 2026-10-04 before candidate generation.

Use H002 as the frozen baseline, including its prompt, content, fonts, object
types, sizes, colors, 3 slides and 2 durations. H002 is an independent task;
E003 is a tuned follow-up and must not be called another unseen test.

Hypothesis: replacing reciprocal center/side swaps with a three-way cycle
over triangular slots eliminates label-box intersections under synchronized
linear interpolation. Keep center (640,320), move side slot centers to
(220,520) and (1060,520). Cycle all three modes clockwise between slots.
Keep labels centered on their rings. Do not add slides or change text sizes.

Freeze diagnostic before execution: continuous positive-area rectangle overlap
for each of the three label pairs across each transition; all selected boxes
unrotated. Baseline and candidate use the same diagnostic. Target: candidate
has zero overlap intervals for those selected label pairs; exact object count,
types, names, content, central/side diameters and durations remain unchanged.
Run finalizer, inspect all final static slides and preserve the H002 baseline.

This proxy does not reproduce PowerPoint easing, text morph, path scheduling,
ring-edge occlusion, native playback or perceived motion quality. No motion
score or compatibility claim follows from it. A PowerPoint test is still needed.
