# Working on PPTX Motion Lab

Read HANDOFF.md, README.md, docs/PRODUCT_TARGET.md, docs/RESEARCH_PLAN.md, docs/STATUS.md, and the selected experiment before changing code.

For parallel research, follow docs/COLLABORATION.md. Check remote branches and open PR claims, use one branch/worktree and unique experiment ID per task, and preserve frozen baselines. Do not modify another agent's work or force-push main. The integrator updates the main checkpoint after review.

- The product goal is an AI Motion Director for existing PowerPoint decks. A short natural-language instruction is one input mode, not the destination. Read `docs/PRODUCT_TARGET.md`.
- This repository is research. Distinguish proposed, implemented, structurally checked, and PowerPoint playback verified.
- Preserve semantic object identity across states. Never equate slide-local numeric shape IDs with global identity.
- For an existing PPTX, inventory the source before planning edits. Explicit script > speaker notes > existing native choreography > visible narrative > inferred narrative > researched narrative. Existing timing is a source resource: preserve/extend it by default rather than rejecting or replacing it. Preserve slide count/order/content by default; generated components require a narrative role and design-system fit.
- North-star autonomy: the user may provide only a PPTX and a high-level goal. Do not require object-by-object animation instructions; independently build the report script, resource-gap plan and choreography unless factual/permission ambiguity truly requires user input.
- Read `docs/MOTION_PACKING.md` and `docs/CLICK_BEAT_CHOREOGRAPHY.md` before designing compound motion. A slide is a scene/execution container, not a motion frame; however one slide may contain several presenter-controlled click beats. Pack shared-resource motions into the slide, then preserve narrative rhythm: start a new click beat when the audience should pause at a meaningful stable state, use `with_previous` for concurrent motion, and `after_previous` only for automatic continuation within a beat. Never turn presenter speech time into a guessed animation delay.
- Prefer native editable elements. Label raster, video, and manual fallbacks explicitly.
- Never claim that XML checks, LibreOffice renders, or an HTML animation prove PowerPoint playback.
- Record source URL, date, tested environment, command, output and limitations for experiments.
- Keep reference media local unless the owner authorizes its redistribution. Use synthetic data for demos.
- Do not modify unrelated repositories, install personal skills, or publish a release as a side effect of research.
- Run `python3 -m unittest discover -s tests -v` and validate changed example plans.
- Update docs/STATUS.md after substantive work so another session can continue from evidence.
- Do not add dependencies or expand test scope without a concrete research need.

