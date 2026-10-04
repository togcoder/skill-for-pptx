---
name: pptx-motion
description: Develop editable PowerPoint motion from short prompts using explicit scene states, stable object identity and evidence gates. Use for requests to prototype Morph, motion recipes, motion plans, or research and improve a PPTX motion generator. This repository contains an experimental source skill, with structural and static checks only until PowerPoint playback is supplied.
---

# PPTX Motion

Create a reviewable motion experiment from a short instruction. Read the project checkpoint before continuing. Treat this as research source; do not install the skill or publish a release as a side effect.

## Workflow

1. Freeze the short prompt and the intended slide count. Resolve routine design choices and record assumptions. Separate semantic message, object identity and motion.
2. Choose a recipe from [recipes.md](references/recipes.md). Record the original source URL, author, access date, evidence actually inspected and reuse conditions. Do not copy reference media into distributed artifacts.
3. Read [plan-contract.md](references/plan-contract.md). Draft ordered states and consecutive transitions. Use stable semantic IDs and unique names beginning with `!!`. Reuse the same names across states. Plan labels and their carriers separately so that both stay readable.
   Count visible states separately from transitions: N slides provide N−1 between-slide transitions. The first pose is already visible. For swapping labels or cycling focus, read [motion-paths.md](references/motion-paths.md) and inspect intermediate-path risks before exporting.
   Size paths for the actual label boxes. For equal labels on a symmetric three-slot cycle, use the clearance helper in that reference. Check labels and carriers separately; clear label paths do not imply clear carrier paths.
4. Check renderer capability before creating files. The current backend supports only 16:9, native `rect`, `ellipse`, and `textbox`, full opacity, and Morph transitions. It rejects unimplemented style fields. Do not silently drop unsupported effects, approximate them without disclosure, or mistake native chart cross-fade for geometric Morph.
5. Validate the plan with `python3 scripts/validate_plan.py PLAN.json`. Invoke the host Presentations workflow for runtime setup and its operation marker, then run from project root:
   `bash scripts/run_experiment.sh PLAN.json build/UNIQUE_RUN output/UNIQUE_NAME.pptx`
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

- `scripts/render_plan.mjs`: restricted native scene renderer
- `scripts/add_morph.py`: experimental transition insertion
- `scripts/normalize_textboxes.py`: plan-scoped native textbox declaration
- `scripts/validate_plan.py`: plan validator
- `scripts/inspect_pptx.py`: package inventory
- `docs/POWERPOINT_QA.md`: native playback acceptance
- `experiments/E001/`: frozen brief, baseline, rubric and regressions

Resolve these paths relative to the repository root (two parents above this skill directory). The source is not a self-contained installed package.
