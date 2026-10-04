# T006 — Full packed candidate, opening-text repair and coordinate audit

Date: 2026-10-04 UTC / 2026-10-05 Vietnam. Owner: Codex /root.
Base: `0bd74645f554e73a238fba3a4dfac1b3b7f4f5dd`.
Branch: `work/T006-packed-validation-20261004`, PR #11.

## Decision

Keep the narrow opening-text preservation fix. It changes the full pipeline
from an observed abort to a finalized, renderable one-slide PPTX on the same
frozen input. Keep the independent audit and negative evidence.

**Do not promote the timing writer to native-compatible.** Actual PowerPoint
playback is untested, and the coordinate diagnostic flags later-stage origins.
No production timing semantics were changed in this experiment.

## Input and scope

Frozen T005 candidate intent: burst 12 nodes, orbit the ring 90 degrees clockwise,
focus node 3, split into 4 layers, reassemble and restore; labels upright.
The same 31 persistent objects and six operations are retained. This is a
regression of a known prompt, not a fresh/independent holdout. The old intent's
click-per-state assumption belongs to its legacy Morph backend; packed T006
attempts one-click sequencing. Actual trigger behavior remains unverified.

One scene, one final slide, six planned semantic events, packing ratio 6,
zero resource-set changes and zero extra scene boundaries. These are structural
packing metrics, not six successfully played effects.

## First full run failed

`pack_timeline._geom` discarded the initial state-local text override.
The `phase` object has empty default text, so its rendered shape had no text body.
The strict normalizer then raised `Planned textbox has no native text body`.
The old 75-test suite passed despite this failure.

Evidence: `candidate.timeline.json`, `failed-missing-text.pptx`, `failure.txt`.
The failed raw package is intentionally retained; it is not a deliverable.

Repair: `_initial_frame` preserves opening `text` in addition to geometry.
Later phase-caption changes remain unsupported, as the packed contract already
declares. No dummy text, normalizer bypass or relaxed acceptance was introduced.
Regression coverage compares resolved opening text for every object on both
existing T005 candidate and transfer inputs. Transfer was not rebuilt as a new
PPTX and is not presented as new generalization evidence.

## Exact final artifact

`output/T006_packed_candidate.pptx`

SHA-256: `41c4fb7865ea587e0d426fccf4de2c82fc1db731147a92a4fba28926b0e52094`

| Measured item | Result |
|---|---|
| Final slides / native objects | 1 / 31 |
| Planned stages | 6 |
| Encoded behaviors / clickEffect groups | 82 / 1 |
| Planned packed duration | 7,100 ms |
| ZIP/relationships/finalizer import | pass |
| Independent identity, opening text, effect keys, durations and segment deltas | no errors |
| Full unit suite after repair and audit tests | 79 passed |
| Full OOXML schema validation | not performed |
| Exact-file PowerPoint playback | not performed |

`hashes.json` freezes both plan variants, failed raw package, final PPTX and final
PNG. `validation.json` contains the host finalizer receipt; the exact output was
then independently read by `scripts/audit_packed_candidate.py`.

## Static review

Rendered the exact final PPTX and viewed its sole slide at 1280 × 720.
Title, opening phase caption and CORE are readable, with no clipping/wrapping.
The 78 overlap warnings refer to intentional stacked, occluded node labels in
the opening pose. They are not evidence that intermediate motion is safe.
The core sits left of center to reserve the right side for the intended detail
view. Static opening readability: **4/5, subjective, author review**. Motion
quality and native editing scores: **null**. No overall quality score.

Only the opening pose is rendered by this static importer. No later stage pose
or animated playback was observed. The phase caption stays at its opening text
because phase-text animation is outside the current backend.

## New coordinate risk

The writer emits every path as `M 0 0` and subtracts the **stage's starting
center**, while encoding `origin="layout"`. It also gives every behavior
`fill="remove"`. The audit therefore compares the encoded points against the
plan under an explicit model: path coordinates offset the original authored
layout center, with no implicit accumulation between stages.

| Stage | Delay / duration ms | Behaviors | Paths differing under that model | Maximum difference px |
|---|---|---|---|---|
| burst | 0 / 1000 | 27 | 0 | 0 |
| orbit | 1000 / 2100 | 27 | 27 | 224.001 |
| focus | 3100 / 1000 | 9 | 5 | 224.000 |
| split | 4100 / 1000 | 5 | 5 | 522.796 |
| reassemble | 5100 / 1000 | 5 | 5 | 543.766 |
| restore | 6100 / 1000 | 9 | 5 | 522.796 |

All relative segment displacements match the intended paths within serialization
tolerance. The concern is the path's location, not its local shape. The 47 path
mismatches are **conditional geometric measurements, not observed PowerPoint
jumps**. Fill behavior, property stacking and one-click start semantics still
need native evidence. The audit is deliberately not a timing emulator and does
not validate scale composition, rotation stacking, easing or intermediate overlap.

## Sources and rights

Microsoft is the author of all technical references below; accessed 2026-10-04
UTC. Documentation read as mechanism evidence, no reference code/media copied
or redistributed. Microsoft documentation/copyright terms apply; our audit and
test fixtures are independently authored. No external visual assets were used.

- https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/498c3cfa-652c-49b3-a82c-33fd94468af8
  describes path commands, normalized slide-size coordinates and defaults.
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.animatemotion?view=openxml-3.0.1
  distinguishes path origin from pathEditMode (editing behavior). The audit's
  authored-center interpretation is an inference requiring native confirmation.
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.commonbehavior?view=openxml-3.0.1
  describes additive and accumulation controls, neither explicitly emitted here.
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.commontimenode?view=openxml-3.0.1
  documents common timing attributes. A separate attempted fill-enum URL was
  inaccessible; no new claim about PowerPoint fill behavior is drawn from it.

## Reproduce

Use a fresh build/output path, as the scripts deliberately refuse overwrite:

```bash
python3 scripts/pack_timeline.py experiments/T005-20261004-codex-choreography/candidate.intent.json build/new-plan.json
bash scripts/run_timeline_experiment.sh build/new-plan.json build/new-packed output/new-packed.pptx
python3 scripts/audit_packed_candidate.py output/new-packed.pptx build/new-plan.json
python3 -m unittest discover -s tests -v
```

Follow host Presentations marker/finalizer/render instructions. This run used
Work runtime Python 3.12.14, Node 24.19.0, artifact-tool 2.8.77, Bitstream Charter.
No PowerPoint executable was found on PATH and no native session was used.

## Next experiment / handoff

1. Open the exact frozen candidate in Microsoft PowerPoint and record version,
   repair status, click count, stage positions and Animation Pane editability.
   Use `playback-checklist.json`; do not fill results without observation.
2. Inspect a minimal PowerPoint-authored two-stage path on one object to resolve
   layout anchoring, fill retention and stage trigger hierarchy. Compare that
   evidence with this candidate before changing the production writer.
3. If needed, test absolute offsets from the authored center with explicit
   retention/additive behavior on the same one-slide input; preserve this file
   as baseline. Do not fall back to waypoint slides.
4. After the native semantics gate, add a fresh different multi-track prompt and
   the existing-deck T007/T008 workflow. This experiment does not satisfy the
   unseen-prompt or 18-run benchmark goals.

PR #5's stale compiler-only claim was closed as superseded, without deleting its
branch. No skill installation, release or quota purchase occurred.
