# Working in this lab

This repository is a **multi-domain design research lab**. Agents research,
build and critique design for several applications: PowerPoint, Word, Excel,
vector graphics, and the orchestration between them. PowerPoint is the
oldest domain, not the only one.

## Read first

1. `HANDOFF.md`
2. `lab/CHARTER.md`
3. `lab/PROTOCOL.md`
4. the card of your domain: `domains/<domain>/DOMAIN.md` (list in
   `domains/README.md`)
5. the last two reports in that domain

The newest research may be on the branch HANDOFF.md names, not on `main`.
Fetch remote branches and read open claims first.

## Rules for every agent

- **First-Pass User Intent Fulfillment (Official Owner Mandate).** Skills and tools
  are not built to trap the user in one rigid, isolated use case, but to elevate
  the user experience to its peak. Decode human intent, audience, context and
  aesthetic requirements deeply so that the generated deliverable matches user
  vision on the first pass, eliminating repetitive trial-and-error regeneration.
- **Cross-Asset Pre-Processing Pipeline.** Never embed raw, unprocessed assets.
  Cross-domain skills orchestrate domain-specialized tools before composite assembly:
  - *Images:* Always crop, mask, remove background, and color-grade (Kelvin/tone)
    via dedicated tools (Pillow/PhotoCraft/ImageMagick) before embedding into
    PPTX, Word DOCX, or Excel XLSX.
  - *Audio:* Always normalize (EBU R128: -14.0 LUFS, True Peak <= -1.0 dBTP),
    filter noise, and auto-duck before muxing with video (FilmCraft) or slide
    choreo (DeckCraft).
  - *Data & Charts:* Verify zero-error formulas and render Tufte-grade vector
    charts in SheetCraft before embedding into slides or annual report docs.
- **Local Autonomy & Cleanliness Law.** When operating locally, agents have full
  operational authority to download any necessary resources (fonts, reference
  decks, sample media, models) and install any programming language, CLI, or
  library (pip, uv, npm, ffmpeg) required for peak craft.
  *Cleanliness constraint:* Transient downloads and scratch scripts belong strictly
  in git-ignored workspace/ or task scratch folders; delete temporary files when
  no longer needed so python3 lab/tools/check_layout.py always passes.
- **Lifecycle. Follow `lab/PROTOCOL.md`: orient → claim → frame → research →
  self-check → review → respond → merge → handoff.
- **Claim with the tool, never by hand (T083, D007).**
  - Run `python lab/tools/coord.py board` to see who is working on what.
  - Then run `python lab/tools/coord.py claim --agent <you> --slug <slug> --title "[pptx] …" [--id <reserved ID>] [--capability <id>]`.
  - The tool reserves the ID against `main` and every open branch. It creates your branch and
    your own worktree, pushes the claim, and prints the decisions, files and owner feedback
    that bind your task.
  - Work only in that worktree. One task = one domain; use `cross` for cross-domain work.
- **Binding decisions** are in `lab/DECISIONS.md`. **File ownership** is in
  `lab/capabilities.json`.
  - A new script must be registered there in the same PR (CI fails otherwise).
  - A second implementation of a registered capability needs the lead's decision first (D002).
- **Talk, don't guess.** When you need the owner's intent, write a question in
  `research/feedback/questions.md` and stop that part of the work until it is answered.
  The owner's open feedback items are printed by `coord.py`.
- **Think in your domain.** Start from the target application's native model
  and canon. Write every idea transferred from another domain into the
  REPORT, with its test. Shared "universal" layers become canonical only
  after accepted reviews in two domains.
- **Cross-craft assets.** When another ArtCraft tool owns the asset (VectorCraft
  for SVG, PhotoCraft for raster, WordCraft for equations/fields, GridCraft for
  pivots/formulas, DeckCraft for slides), use it, record tool/version/command
  and licence, and test the asset in the receiving domain. Feed a missing
  property back as a task in the source domain; a transfer is not canonical by
  itself (`lab/standards/RESEARCH.md`).
- **Placement.**
  - Every output goes into your task's `experiments/<ID>-<date>-<agent>-<slug>/`:
    `artifacts/`, `preview/`, `inputs/`.
  - Scratch goes into git-ignored `workspace/`.
  - Never write files to the repository root, and never add to the frozen
    `output/`.
  - `python3 lab/tools/check_layout.py` must pass.
- **Research.**
  - Follow `lab/standards/RESEARCH.md`: frame, frozen input, method,
    evidence, negative results.
  - Tag every claim with its evidence rung (0 planned … 6 human-verified).
  - Never present simulations, independent renders or critic scores as
    verification in the target application.
- **Review.**
  - Code or data entering a product path or `knowledge/` needs an accepted
    peer review by another agent (`lab/standards/REVIEW.md`), written to
    `research/reviews/`.
  - Do not review your own work.
  - Unreviewed or outside-agent code stays labelled `EXPERIMENTAL` and out
    of product paths.
- **Merge.**
  - Follow `lab/standards/MERGE.md`: one canonical module per capability.
  - Data carries provenance (source, date, licence, scope, confidence, task).
  - Conflicting values are kept side by side until a test decides.
  - Never overwrite another task's work silently, never force-push `main`,
    never modify another agent's branch.
- **Design numbers.** Durations, sizes, contrasts and thresholds come from
  the domain's design-system data, with sources; they are never hard-coded.
  PowerPoint's data is `knowledge/design_system.json`. Other domains keep
  their own in `domains/<d>/data/`.
- **Output format.** Prefer native, editable output in the target
  application. Label raster, video and manual fallbacks.
- **Records.**
  - Record source URLs or DOIs, access dates, environment, commands, outputs
    and limitations.
  - Keep reference media local unless the owner authorizes redistribution.
  - Use synthetic data in demos.
- **Scope.** Do not modify unrelated repositories, install personal skills,
  or publish releases as a side effect of research. Do not add dependencies
  or expand test scope without a concrete research need.
- **Before you stop:**
  - run `python3 -m unittest discover -s tests -v`;
  - add a `docs/CHANGELOG.md` entry;
  - rewrite your domain card's "State";
  - update your INDEX row;
  - run `python lab/tools/coord.py check` and `coord.py board` and resolve every collision with
    your branch, or name it in the PR description;
  - do **not** edit `HANDOFF.md`, `docs/ROADMAP.md`, `docs/SCRIPT_TRACK.md`,
    `lab/DECISIONS.md` or `lab/capabilities.json`. The lead writes those (D006); propose changes
    in your PR description.

Domain-specific rules live in the domain cards. The PowerPoint rules (source
inventory, script priority, preserving existing timing, click-beat rhythm,
object identity) are in `domains/pptx/DOMAIN.md`.
