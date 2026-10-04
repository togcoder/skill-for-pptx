# Working on PPTX Motion Lab

Read HANDOFF.md, README.md, docs/PRODUCT_TARGET.md, docs/RESEARCH_PLAN.md, docs/STATUS.md, and the selected experiment before changing code.

For parallel research, follow docs/COLLABORATION.md. Check remote branches and open PR claims, use one branch/worktree and unique experiment ID per task, and preserve frozen baselines. Do not modify another agent's work or force-push main. The integrator updates the main checkpoint after review.

- The product goal is an AI Motion Director for existing PowerPoint decks. A short natural-language instruction is one input mode, not the destination. Read `docs/PRODUCT_TARGET.md`.
- This repository is research. Distinguish proposed, implemented, structurally checked, and PowerPoint playback verified.
- Preserve semantic object identity across states. Never equate slide-local numeric shape IDs with global identity.
- For an existing PPTX, inventory the source before planning edits. Explicit script > speaker notes > inferred narrative > researched narrative. Preserve slide count/order/content by default; generated components require a narrative role and design-system fit.
- Read `docs/MOTION_PACKING.md` before designing compound motion. A slide is a scene/execution container, not a motion frame. When consecutive actions reuse the same resources, pack the maximum feasible number into one native slide timeline. Do not create waypoint/state slides merely because they are easier to implement; every extra slide boundary needs an explicit technical or semantic reason.
- Prefer native editable elements. Label raster, video, and manual fallbacks explicitly.
- Never claim that XML checks, LibreOffice renders, or an HTML animation prove PowerPoint playback.
- Record source URL, date, tested environment, command, output and limitations for experiments.
- Keep reference media local unless the owner authorizes its redistribution. Use synthetic data for demos.
- Do not modify unrelated repositories, install personal skills, or publish a release as a side effect of research.
- Run `python3 -m unittest discover -s tests -v` and validate changed example plans.
- Update docs/STATUS.md after substantive work so another session can continue from evidence.
- Do not add dependencies or expand test scope without a concrete research need.

