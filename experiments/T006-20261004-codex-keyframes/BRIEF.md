# T006 keyframe packing: frozen experiment

Frozen 2026-10-04T14:59:22Z, before implementation.
Base main 801f841067426dac9f2bc3498bdd4aa4e1fbb5bc.
Follow the user's one-slide resource-reuse direction and the concurrently
authored docs/MOTION_PACKING.md policy. Do not alter the T005 baselines.

Hypothesis: native p:anim tracks for ppt_x/ppt_y/ppt_w/ppt_h can encode the same
geometry checkpoints of T005 in one physical slide. Internal keyframes are
timing data, not new slides. This is a first implementation hypothesis, not
proof of correct rendering/animation in PowerPoint.

Candidate: same 31 native objects and core->burst->orbit->focus->split->
reassemble->restore geometry as T005 candidate. Six semantic motion events,
one scene, one slide, one resource set, no slide boundary. Rotation stays zero.
One requested start click, then synchronized numeric tracks over the existing
7100 ms transition budget. No easing, added hold, 3D, sound or video. Replace
the changing phase caption with a single static subject caption because this
experiment animates geometry only; record that semantic-caption reduction.

Frozen checks: one physical/ordered slide; exact names/types/count; unique
time-node IDs and real target IDs; monotone keyframe times spanning 0..100000;
center/size values match every T005 pose within 0.001 px and timing within
0.1 ms after serialization; complete six-event coverage; no duplicate assets;
no transition/Morph in packed output; no unexpected ZIP part changes during
insertion; reject already-timed input/unsupported changes/identity mismatch;
fresh destinations and no partial output after failure. Compare 12 -> 1 slides,
packing ratio 6/12 -> 6/1. This diagnostic is not a quality percentage.

Use Microsoft primary documentation for the timing/property mechanism. Native
playback and full OOXML schema validation remain separate gates. Read-only
package re-import/render does not prove playback. Source motion video observation
is still missing; log this instead of claiming T006 fully accepted.

Transfer scope this run: pack the preexisting T005 learning plan (10->1); this
is known-plan portability, not a fresh-prompt generalization test. A genuinely
different multi-track effect and fresh prompt remain the next phase.

Static review: inspect the final single slide of each file; sample states are
already validated T005 geometry, but packed playback needs native inspection.
Subjective readability 1..5 may be rated for the static launch pose only;
motion smoothness, appeal and native editability stay null.
