# T005 — compound choreography and explicit intent

Date: 2026-10-04 UTC. Owner/reviewer: Codex/root. Source version: v0.7 research.
Frozen brief: BRIEF.md. Base remote: f3745118ca2334156038680747a3893397259470.
Claim commit: 13e4f6383a98b6127d0632c7c5c9aef741325107.
Compiler milestone: 091abc22ea738fb242737a31d79d5b05b04de5c0.
PR: https://github.com/togcoder/skill-for-pptx/pull/3.

## Outcome

Implemented a strict intent contract and reusable `scripts/choreography.py` for
one compound native recipe. It coordinates burst, ring orbit, target zoom,
layer separation, reassembly and return. Stable labels and preexisting layer
identities survive all states. AI translates language into the contract; this
is not a general NLP engine. Intent, assumption and unsupported-capability
handling are now explicit in the source skill.

| Exact output | Candidate | Transfer |
| --- | --- | --- |
| PPTX | output/T005_compound_candidate.pptx | output/T005_compound_transfer.pptx |
| States / transitions | 12 / 11 | 10 / 9 |
| Native objects per slide | 31 | 22 |
| Semantic nodes / target / layers | 12 / 3 / 4 | 8 / 6 / 3 |
| Orbit | 90° clockwise, six chords | 60° counterclockwise, four chords |
| Requirement categories | 7/7 geometry + package parity | 7/7 geometry + package parity |
| Final images individually inspected | 12/12 | 10/10 |
| PowerPoint playback / actual editing | unverified / unverified | unverified / unverified |

Candidate SHA-256: `05ddf33c89725dbb66083f5130c549d59d9aa291893321a34cc68c6cf9e9cf58`.
Transfer SHA-256: `e87d37db4a76f51c56dac893bade9c2966960cbc6bfc869ebb5bceb3d8cb5e16`.

The unchanged renderer emits rect/ellipse/textbox objects with unique stable
`!!` names, Morph byObject and a fade fallback. Orbit transitions declare
350 ms; other transitions declare 1000 ms. There is no single-slide timing or
auto-advance. Opening the exact file in a supported PowerPoint and advancing
each slide is still required to establish actual behavior. The intended layers
exist as adjacent rectangles before separation, honoring 1:1 identity rather
than inventing one-to-many Morph matching.

## Frozen comparison and measured results

Same candidate prompt and intent, changing only orbit_segments from 1 to 6:

| Geometric proxy | Endpoint-only ablation | Candidate |
| --- | --- | --- |
| Max deviation from radius 224 px | 65.608081 px | 1.916351 px |
| Label overlap intervals | 0 / 66 pairs | 0 / 396 pairs |
| Carrier overlap intervals | 0 / 66 pairs | 0 / 396 pairs |

This is a deliberate negative control, not a discovered rendering bug.
Additional waypoints reduce chord deviation by about 97.1% in this mathematical
model. They also increase slides/clicks. No measured improvement in real motion
smoothness follows from these numbers. Ablation plan/intent are saved; no
ablation PPTX was needed for this geometry-only comparison.

All 41 unit tests pass, including prior 34 tests unchanged. Candidate and
transfer reproduce exactly from their saved intents under the final compiler.
Package parity checks native names/types/text/geometry/rotation and ordered
Morph durations; no images or native animation timeline appear. This is not
full OOXML schema validation.

## Failure retained: insufficient waypoint oracle

The first mutation test moved label-1 at orbit-2 to normalized x=0.1. The original
checker summed signed angles across the orbit; intermediate deviations could
cancel, so it incorrectly returned passed. Initial suite: 39/40, independently
observed by the transfer agent before the parent fix. The faulty implementation
existed only during development; no successful release was claimed for it.

The parent corrected the oracle to check every label waypoint against the
requested polar coordinate, and expanded binding checks to carrier centers and
layer alignment. Preserved reproducer: test_geometry_mutations_are_detected.
Additional safety: compiler rejects orbit steps over 90°, preventing a requested
full revolution from collapsing to identical endpoints. These are regression
checks designed for specific risks, not independent reliability statistics.

## Static inspection and subjective ratings

Parent opened all 22 final PNGs individually at 1280×720. Launch nodes are
intentionally hidden behind the core. Ring poses preserve readable, upright
numbers with no observed clipping or unwanted wrapping. Focus/split states
clearly separate the selected node on the right; reassembly restores it. No
static repair was needed. Empty right space before focus is deliberate, but
makes those states visually sparse. The labels are numbers, not a rich semantic
diagram. No polished cinematic quality is claimed.

Frozen subjective scale 1–5, same reviewer, not blinded:

| Criterion | Candidate | Transfer | Rationale |
| --- | --- | --- | --- |
| Static readability | 4 | 4 | Clean numbers and titles; ring labels remain modest in size |
| Focus clarity | 4 | 4 | Color/size and right-side separation distinguish target |
| Static visual complexity | 3 | 3 | Multi-state hierarchy, but still primitive 2D geometry |
| Motion appeal/smoothness | null | null | Native playback not observed |
| Real PowerPoint editability | null | null | Only native object structure established |

No aggregate score and no claim that this meets the user's full advanced-motion
ambition. The useful advance is reusable compound intent handling and evidence
gates, not a proven impressive animation.

## Transfer integrity

Fresh agent `/root/choreography_forward` received only the source skill path,
new learning-diagram prompt, isolated directory and plan-only scope. It generated
8 nodes, counterclockwise 60°, target 6, 3 layers without parent repair. Parent
exported/rendered/inspected the PPTX. Per AGENTS, the agent read this experiment's
BRIEF, which exposed development prompt and criteria. It did not inspect other
plans/results. Therefore call this fresh-output recipe transfer, not fully blind
or end-to-end autonomous success. Preserve `transfer/trace.md` unchanged.

## Sources and usage conditions

1. Microsoft Support, “Morph transition: Tips and tricks”, accessed 2026-10-04:
   https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks.
   Read documented 1:1 forced-name matching and combined movement/resize/rotation.
2. Microsoft Support, “Add a motion path animation effect”, accessed 2026-10-04:
   https://support.microsoft.com/en-us/powerpoint/add-a-motion-path-animation-effect.
   Read predefined/custom paths and point editing; this documents a possible
   next mechanism, not a capability implemented in the current Morph backend.

Microsoft is the author/publisher. These are copyrighted documentation sources,
not an asset license. No media, templates or code were copied or redistributed.
Only text documentation was inspected; embedded source videos were not played.
Original native diagram geometry uses synthetic data. No third-party assets.

## Reproduction

From project root with the existing host runtime, follow Presentations marker
and runtime instructions, then use new build/output paths:

```bash
python3 scripts/choreography.py INTENT.json NEW_PLAN.json
python3 scripts/validate_plan.py NEW_PLAN.json
bash scripts/run_experiment.sh NEW_PLAN.json build/NEW_RUN output/NEW.pptx
RUNTIME_NODE_MODULES="$CODEX_PRIMARY_RUNTIME_NODE_MODULES" "$CODEX_PRIMARY_RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/render_presentation.mjs --input output/NEW.pptx --output_dir build/NEW_RENDER --scale 1
python3 experiments/T005-20261004-codex-choreography/collect_evidence.py
```

`collect_evidence.py` refreshes derived evidence for the committed output paths,
not PPTX files, images or manual review. Review hashes before interpreting it.
Environment and exact image hashes are in environment.json/render-manifest.json.
Finalizer receipts for both decks are retained in this experiment.

## Next highest-value experiment

T006: a native timed path/timeline that can play the orbit without one click per
waypoint, with an exact-hash PowerPoint playback gate. Keep T005 as a structural
reference. Design a genuinely different multi-track effect (not more ring nodes)
and accept it only after source mechanism inspection and evidence. T001 remains
the missing native verification gate. Do not promise arbitrary complex prompts,
actual 3D, fluid simulation or camera motion from this restricted recipe.
