# Working on PPTX Motion Lab

Before changing code, read in this order:

1. HANDOFF.md
2. docs/STATUS.md
3. docs/PRODUCT_TARGET.md
4. docs/DESIGN_SYSTEM.md
5. docs/VERIFICATION.md
6. the skill for your area (`skills/pptx-motion-director/SKILL.md` or `skills/slide-forge/SKILL.md`)
7. the selected experiment

The latest research is on the branch HANDOFF.md names; `main` may be behind.

For parallel research, follow docs/COLLABORATION.md:

- Check remote branches and open PR claims.
- Take the next free task ID in `research/tasks/INDEX.md` and push the claim row before you start; never reuse an ID.
- Use one branch/worktree and a unique experiment folder per task, and preserve frozen baselines.
- Do not modify another agent's work or force-push main.

The integrator reviews and merges.

- The product goal is an AI Motion Director for existing PowerPoint decks. A short natural-language instruction is one input mode, not the destination; Slide Forge (new decks) is a second entry mode. Read `docs/PRODUCT_TARGET.md`.
- This repository is research. Name the evidence rung of every claim (docs/VERIFICATION.md): planned, structural, simulated, LibreOffice, PowerPoint-parsed, PowerPoint-rendered, interactive playback.
- Preserve semantic object identity across states. Never equate slide-local numeric shape IDs with global identity.
- For an existing PPTX, inventory the source before planning edits. Explicit script > speaker notes > existing native choreography > visible narrative > inferred narrative > researched narrative. Existing timing is a source resource: preserve/extend it by default rather than rejecting or replacing it. Preserve slide count/order/content by default; generated components require a narrative role and design-system fit.
- North-star autonomy: the user may provide only a PPTX and a high-level goal. Do not require object-by-object animation instructions; independently build the report script, resource-gap plan and choreography unless factual/permission ambiguity truly requires user input.
- Read `docs/MOTION_PACKING.md` and `docs/CLICK_BEAT_CHOREOGRAPHY.md` before designing compound motion. A slide is a scene/execution container, not a motion frame; however one slide may contain several presenter-controlled click beats. Pack shared-resource motions into the slide, then preserve narrative rhythm:
  - start a new click beat when the audience should pause at a meaningful stable state;
  - use `with-previous` for concurrent motion;
  - use `after-previous` only for automatic continuation within a beat.

  Never turn presenter speech time into a guessed animation delay.
- Beauty and technique share one source: `knowledge/design_system.json`. Never hard-code a new duration, easing, stagger, contrast or type threshold in a generator or checker; read or add a token, with evidence in `sources`. Run `scripts/design_critic.py` on outputs and act on its warnings.
- Prefer native editable elements. Label raster, video, and manual fallbacks explicitly.
- Never claim that XML checks, LibreOffice renders, simulated previews, critic scores or an HTML animation prove PowerPoint playback.
- Code from outside agents (for example Argon/Gemini drops) is evaluated before it is wired in. Check schema validity, real fixtures and overlap with canonical modules. Unproven modules stay labelled EXPERIMENTAL and out of product paths (see T032, T033).
- Record source URL, date, tested environment, command, output and limitations for experiments.
- Keep reference media local unless the owner authorizes its redistribution. Use synthetic data for demos.
- Do not modify unrelated repositories, install personal skills, or publish a release as a side effect of research.
- Run `python3 -m unittest discover -s tests -v` and validate changed example plans.
- After substantive work:
  - add an entry to `docs/CHANGELOG.md`;
  - rewrite (do not append to) `docs/STATUS.md` and `HANDOFF.md` so another session can continue from evidence;
  - update your row in `research/tasks/INDEX.md`.
- Do not add dependencies or expand test scope without a concrete research need.
