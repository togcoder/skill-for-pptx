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

- **Lifecycle.** Follow `lab/PROTOCOL.md`: orient → claim → frame → research →
  self-check → review → respond → merge → handoff.
- **Claim.** Take the next free ID in `research/tasks/INDEX.md`. The title
  carries the domain in brackets (`[docx] …`). Push the claim before
  expensive work, and never reuse an ID. One task = one domain; use `cross`
  for cross-domain work.
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
  - rewrite (do not append to) `HANDOFF.md` and `docs/STATUS.md` when
    lab-wide state changed.

Domain-specific rules live in the domain cards. The PowerPoint rules (source
inventory, script priority, preserving existing timing, click-beat rhythm,
object identity) are in `domains/pptx/DOMAIN.md`.
