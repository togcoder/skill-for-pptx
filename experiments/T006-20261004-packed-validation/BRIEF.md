# Frozen brief — T006 packed candidate validation

Base: 0bd74645f554e73a238fba3a4dfac1b3b7f4f5dd. Frozen UTC: 2026-10-04T19:09:35Z.

Input: experiments/T005-20261004-codex-choreography/candidate.intent.json, unchanged. This is regression evidence, not a holdout.

Hypothesis: the merged pipeline produces one native slide with all 31 persistent source objects and six requested semantic stages, without losing intended geometry.

Machine criteria: one slide; six stages; stable shape identity and text; expected timing targets/delays/path points; positive finite geometry; finalizer and full unit suite pass; exact artifact SHA and final render saved. Compare encoded path locations with plan using independent initial-layout reconstruction where semantics permit; report assumptions separately from playback.

Human static rubric (subjective, same 1–5 clarity/readability scale): opening pose readable, no unintended clipping/wrapping, source identity retained. Do not score movement from still image. Dynamic phase text is already excluded by the packed-plan contract.

PowerPoint acceptance: exact hash, named PowerPoint version, no repair, one-click full sequence, return pose and editable Animation Pane. If unavailable, mark NOT TESTED. No native compatibility promotion.

Keep baseline artifacts if a failure requires a correction. Only retain production fixes with before/after evidence; do not change the frozen input or thresholds.
