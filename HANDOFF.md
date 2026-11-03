# Handoff — Design Research Lab

Updated 2026-11-03, after T055. This file is rewritten at each handoff, not
appended. History: [docs/CHANGELOG.md](docs/CHANGELOG.md). Previous handoff:
[docs/archive/HANDOFF-T038-2026-11-01.md](docs/archive/HANDOFF-T038-2026-11-01.md).

Repo: <https://github.com/togcoder/skill-for-pptx> (private). Owner: togcoder.

## What the lab is now

A **cross-domain design research lab**: several agents research, critique and
chain results for PowerPoint, Word, Excel, vector, 3D, CAD, video and audio.
PowerPoint is the oldest domain, not the only one. Each domain has its own
thesis, sources, design data and evidence ladder; the shared working rules are
in `lab/standards/` and `lab/protocols/`.

- How agents work: [lab/PROTOCOL.md](lab/PROTOCOL.md).
- Standards: [lab/standards/](lab/standards/).
- Domains: [domains/README.md](domains/README.md).
- Cross-asset pipeline and local autonomy:
  [lab/protocols/04_cross_asset_pipeline.md](lab/protocols/04_cross_asset_pipeline.md).

## Start here

1. Fetch the remote branches and read the open claims in
   `research/tasks/INDEX.md` first. The newest work is **not** on `main`.
2. Read `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, then your domain card
   (`domains/<domain>/DOMAIN.md`).
3. Run `python -m unittest discover -s tests -v` and
   `python lab/tools/check_layout.py`. The current tree is 469 tests OK,
   8 skipped, layout OK.
4. Take the next free ID in `research/tasks/INDEX.md` (currently **T056**),
   put the domain in brackets (`[pptx]`, `[docx]`, `[xlsx]`, `[vector]`,
   `[cross]`), and push the claim before expensive work.

## Current branches and state

| Branch | Tip | State |
|---|---|---|
| `main` | `f648ace` | T053 merged; 448 tests passed at that point |
| `work/T054-opencode-vector-match` | `b387146` | **review requested**, not merged |
| `work/T055-opencode-pptx-3d` | claim `64d6d47` + T055 work | **review requested**, stacked on T054 |

T055 is stacked on T054 because it reuses the T054 CSG blockout as its depth
source. Merge order must be T054 first, or rebase T055 onto the accepted T054
state.

## Latest results

### T055 [pptx] Native 3D product explainer

- **What it proves.** PowerPoint can carry a real 3D model: `Shapes.Add3DModel`
  inserts an embedded GLB, keeps it as shape Type 30, and preserves camera,
  look-at, rotation and FOV after save/reopen. The deck has three slides, one
  native model per slide, editable callout/spec/focus-box objects, and a PDF
  export from the exact file.
- **Deck.** `experiments/T055-20261103-opencode-pptx-3d/artifacts/quickmill_native_product_tour_v3.pptx`
  (456,861 bytes). Source GLB 56,500 bytes, Y-up metres, 400 × 553 × 326 mm,
  34 non-metallic material regions. Three embedded `model3d*.glb` copies.
- **Native findings.** Metallic PBR renders as a white mirror; `COLOR_0` is
  ignored when a material exists (split colour regions into meshes instead);
  a black horizontal face renders grey under the fixed light rig; patching the
  `am3d` light XML does not change the render.
- **Morph.** The COM enum rejects `EntryEffect=384`. The real
  `mc:AlternateContent` + `p159:morph` structure is accepted (`EntryEffect`
  3954) and survives a save, but 3D camera interpolation was not visually
  verified. **No Morph claim.**
- **Limits.** The model is a massing study, not final product fidelity. No
  human rung 6 yet.
- Report: `experiments/T055-20261103-opencode-pptx-3d/REPORT.md`.

### T054 [vector] Comparison-first match

- **Result.** 0.806 W/H against the photo's 0.800; six landmark deltas
  0.000–0.001; 117 paths; 3D CSG blockout (24 bodies, recessed 228 × 121 × 211 mm
  bay, 380 × 300 × 80 mm top housing). VectorCraft 0 warnings.
- **Limit.** Still axonometric, not perspective; no calibrated perspective
  camera. Review requested.
- Report: `experiments/T054-20261102-opencode-vector-match/REPORT.md`.

### T053 [vector] Semantic 2.5D reconstruction

- Merged to `main` at `f648ace`; 448 tests passed at that point.
- Report: `experiments/T053-20261102-opencode-vector-reconstruction/REPORT.md`.

## Next (ranked)

1. **Peer review T054 and T055**, following `lab/standards/REVIEW.md`. The
   reviewer should check the native reopen evidence, the massing-study label,
   and the Morph negative result. Do not merge T055 before T054.
2. **Replace the T055 blockout with a proper product mesh** (bevels, group-head
   detail, portafilter, knobs) and re-run the same compiler; then test a
   12-landmark constrained camera.
3. **Verify Morph playback in a clean PowerPoint session.** If the 3D camera
   interpolates, record it as a separate claim with a full-resolution capture.
4. **Human review of the T055 deck.** The owner has not accepted it as
   "mỹ mãn"; the model is still a massing study.

## Working prompt

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx.
Fetch the remote branches. Read AGENTS.md, lab/CHARTER.md, lab/PROTOCOL.md and
domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.
Take the next free ID in research/tasks/INDEX.md with the domain in brackets and
push the claim. Frame your question from the domain's native canon before
building. Follow lab/protocols/04_cross_asset_pipeline.md to pre-process assets
before embedding. Put every output into experiments/<ID>-<date>-<agent>-<slug>/
(never the repo root). Tag claims with evidence rungs. Ask another agent to
review per lab/standards/REVIEW.md before anything enters a product path.
```
