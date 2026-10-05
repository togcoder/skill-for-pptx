---
name: pptx-motion
description: Develop editable PowerPoint motion from short prompts using explicit scene states, stable object identity and evidence gates. Use for requests to prototype Morph, motion recipes, motion plans, or research and improve a PPTX motion generator. This repository contains an experimental source skill, with structural and static checks only until PowerPoint playback is supplied.
---

# PPTX Motion

Create or augment a reviewable PowerPoint motion artifact. The preferred product path is to motion-direct an existing PPTX; generating a fresh motion experiment is a supporting path. Read `../../docs/PRODUCT_TARGET.md` and the project checkpoint before continuing. Treat this as research source; do not install the skill or publish a release as a side effect.

## Product path (T019)

For directing an existing deck, prefer `skills/pptx-motion-director/SKILL.md` and
`scripts/motion_director.py`. Its writer (`scripts/pptx_animator.py`) uses the
PowerPoint-canonical timing tree. The patch v0.2–v0.5 click-beat writer below
runs `after-previous` stages concurrently and lacks entrance visibility; keep it
only to reproduce T010–T017 evidence.

## Existing-deck entry path

When the user supplies an existing PPTX:

1. Run `python3 scripts/inspect_existing_deck.py SOURCE.pptx --output INVENTORY.json`.
2. Read [existing-deck-director.md](references/existing-deck-director.md) and [data-motion-recipes.md](references/data-motion-recipes.md).
3. Use an explicit script if supplied. Otherwise prefer speaker notes, then infer
   the report sequence from the deck. Research externally only when appropriate
   and clearly separate researched structure/facts from user data.
4. Draft an `existing-deck-motion-director` v0.3 plan and validate it with
   `python3 scripts/validate_director_plan.py PLAN.json INVENTORY.json`. Separate
   motion beats from presenter click beats: every click beat must state the audience
   purpose, stable state and why a later click boundary is needed. If inventory
   exposes charts or standalone numeric KPI candidates, classify their semantic
   role before choosing motion; chart targets require chart data-motion, while a
   hero metric requires a counter recipe rather than generic Fade/Zoom.
5. Preserve source slide count/order/content by default. Create helper components
   only for a justified narrative role and match the existing visual system.
6. For Director v0.4, compile supported generic + data motion with `python3 scripts/compile_director_patch.py DIRECTOR.json INVENTORY.json --output PATCH.json`, then apply the v0.5 patch path. The compiler may expand one semantic motion beat into multiple automatic stages but must preserve presenter click groups. Unknown/mixed unsupported slides are blocked rather than silently dropping beats. Use the older data-only compiler only for frozen T015 reproduction. Never invent missing move/rotate geometry.  For arbitrary source objects, read [existing-deck-timeline-patch.md](references/existing-deck-timeline-patch.md) and target the exact source slide-local ID + name. Patch v0.2 supports multiple click groups on one fresh source slide. Do not rebuild or rename existing resources merely because the generator path is easier.

## Workflow for fresh motion experiments

1. Freeze the short prompt and the requested outcome. Resolve routine design choices and record assumptions. Separate semantic message, object identity and motion. Read `../../docs/MOTION_PACKING.md` and `../../docs/CLICK_BEAT_CHOREOGRAPHY.md`: do **not** treat slide count as motion count, and do **not** treat one slide as one click. Partition the request into semantic scenes and motion events, cluster adjacent events that reuse the same resource set, and target the minimum slide count by packing the maximum feasible number of motions into each slide timeline.
   For a compound request, read [compound-choreography.md](references/compound-choreography.md). Extract every explicit action, target, quantity, order and constraint before choosing a recipe. Keep design assumptions separate. Use its strict intent contract when the radial drill-down recipe fits; report unsupported demands instead of silently simplifying them.
2. Choose a recipe from [recipes.md](references/recipes.md). Record the original source URL, author, access date, evidence actually inspected and reuse conditions. Do not copy reference media into distributed artifacts.
3. Read [plan-contract.md](references/plan-contract.md). For the current Morph-only backend, draft ordered states and consecutive transitions only as a fallback/structural representation. For packed motion, read [native-timeline.md](references/native-timeline.md) and use `scripts/pack_timeline.py` for the radial-drilldown planning path. For v0.2, explicitly partition each slide into click beats before authoring timing. The target architecture is resource-local motion packing: multiple actions on the same objects belong on one slide timeline whenever the native backend supports them. Use stable semantic IDs and unique names beginning with `!!`. Reuse the same names across states. Plan labels and their carriers separately so that both stay readable.
   Count visible states separately from transitions: N slides provide N−1 between-slide transitions. The first pose is already visible. For swapping labels or cycling focus, read [motion-paths.md](references/motion-paths.md) and inspect intermediate-path risks before exporting.
   Size paths for the actual label boxes. For equal labels on a symmetric three-slot cycle, use the clearance helper in that reference. Check labels and carriers separately; clear label paths do not imply clear carrier paths.
   For parts that separate and reassemble, read [layer-separation.md](references/layer-separation.md). Derive attached detail positions from carrier-local offsets; the flat native objects are not PowerPoint groups.
4. Before rendering, apply the stable-state test from `../../docs/CLICK_BEAT_CHOREOGRAPHY.md`: if the presenter may need an unknown speaking pause after a stage, start a new click beat instead of inserting a guessed delay. Check renderer capability before creating files. The legacy renderer supports 16:9 native `rect`, `ellipse`, `textbox`, full opacity and Morph. T006 adds a separate packed-timeline research backend for `motion_path`, `scale`, and `rotate`; `visibility` is deliberately unsupported until a playback-safe representation is proven. Do not silently drop unsupported effects, approximate them without disclosure, or mistake structural timing XML for verified PowerPoint playback.
5. For a Morph plan, validate with `python3 scripts/validate_plan.py PLAN.json` and run `bash scripts/run_experiment.sh PLAN.json build/UNIQUE_RUN output/UNIQUE_NAME.pptx`. For a packed timeline plan, validate with `python3 scripts/validate_timeline.py PLAN.json` and run `bash scripts/run_timeline_experiment.sh PLAN.json build/UNIQUE_RUN output/UNIQUE_NAME.pptx`. Invoke the host Presentations workflow for runtime setup and its operation marker before either path.
6. Render the final PPTX with the host presentation renderer and inspect every slide. The builder's PNGs show scene states before final packaging, so they alone are insufficient.
7. Inventory the final package with `python3 scripts/inspect_pptx.py FILE.pptx`. Compare names and duration against the plan. Read ordered slide relationships; never infer presentation order from filenames or numeric shape IDs.
   Reuse `inspect_pptx.inspect()` for ordered parts in custom checks instead of reimplementing relationship-path resolution.
8. Score with [evaluation.md](references/evaluation.md), keeping unobserved properties null. Only set native playback verified after opening and playing the exact deck in a named PowerPoint version with captured evidence.
9. When a failure occurs, preserve the baseline, reproduce the failure and derive one reusable rule. Rerun the same input after changing the rule or implementation, then use a different prompt to check transfer.
10. Update `docs/STATUS.md` and the experiment evidence. Save research source and results through the user's authorized project route. Skill installation remains a separate operation.

## Package safeguards learned in E001

Require equal plan and deck slide counts and exact planned `!!` names per slide before patching. Reject a deck with existing transitions or timing. Do not reuse a partially written failed output: preflight all slides, then publish a completed file without overwriting an existing destination. Reject noninteger duration rather than silently truncating it.

## Evidence boundaries

Do not describe XML checks, LibreOffice rendering or an HTML simulation as PowerPoint motion playback. The fallback in unsupported viewers is fade, and its timing need not match Morph. Native rectangles and text prove editable object types structurally; confirm real editing in PowerPoint separately. Do not claim novelty or broad success from a single demo.

Check native text content and formal textbox type separately. The pipeline normalizes `txBox` only for objects explicitly planned as textboxes, before adding Morph. Never reclassify every text-bearing shape: a carrier can contain text without being a textbox. Read the H001/E002 evidence in the plan contract. Preserve historical failures and verify the exact final output; normalization does not establish real-application editing or playback.

## Current source layout

- `scripts/inspect_existing_deck.py`: read-only PPTX intake inventory including chart subtype/dimensions and standalone numeric candidates
- `scripts/validate_director_plan.py`: validates director plans including click rhythm and v0.3 semantic data motion
- `scripts/data_motion_recipes.py`: deterministic chart/KPI recipe selector
- `scripts/compile_data_motion_patch.py`: strict Director v0.3 chart/KPI → existing-deck patch v0.4 compiler
- `scripts/compile_director_patch.py`: Director v0.4 generic+data → patch v0.5 compiler
- `scripts/patch_existing_timeline.py`: patches native timing onto exact existing source objects without requiring `!!` names
- `scripts/render_plan.mjs`: restricted native scene renderer
- `scripts/add_morph.py`: experimental transition insertion
- `scripts/normalize_textboxes.py`: plan-scoped native textbox declaration
- `scripts/validate_plan.py`: plan validator
- `scripts/inspect_pptx.py`: package inventory
- `scripts/pack_timeline.py`: T006/T010 one-slide timeline compiler with v0.2 click-beat partition
- `scripts/add_timeline.py`: restricted native timing XML writer for motion/scale/rotate; playback pending
- `scripts/normalize_timeline_textboxes.py`: timeline-plan native textbox declaration
- `scripts/render_timeline.mjs`: artifact-tool source renderer + timing pipeline
- `scripts/run_timeline_experiment.sh`: one-command packed-timeline experiment runner
- `docs/POWERPOINT_QA.md`: native playback acceptance
- `experiments/E001/`: frozen brief, baseline, rubric and regressions

Resolve these paths relative to the repository root (two parents above this skill directory). The source is not a self-contained installed package.
