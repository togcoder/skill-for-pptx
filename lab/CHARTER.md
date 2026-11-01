# Lab charter — multi-domain design research

This repository is a **research lab where several agents (different models and
sessions) research and critique design for many applications**. It began as
PPTX Motion Lab; PowerPoint is now one domain among several.

## Goals

1. Every agent produces design that looks professional and is technically
   correct in the application it targets.
2. Knowledge is tested before it is trusted. Ideas, code and data pass
   research → review → merge, and every claim names its evidence rung.
3. No single line of thought dominates. Each domain keeps its own thesis,
   sources, design system and evidence ladder. Shared ideas move into the
   cross-domain core only after review in at least two domains.

## Structure

| Place | What lives there |
|---|---|
| `lab/` | Domain-agnostic operating system: this charter, `PROTOCOL.md`, `standards/`, shared `protocols/`, `schemas/`, `registry/`, `templates/`, `tools/` |
| `domains/<domain>/DOMAIN.md` | One card per domain: scope, thesis, owners, code, data, evidence ladder, open questions |
| `research/tasks/INDEX.md` | The only place to take a task ID (each row names its domain) |
| `research/claims/`, `research/reviews/` | Claims of work in progress; peer reviews |
| `experiments/<ID>-<date>-<agent>-<slug>/` | One folder per task: REPORT, inputs, artifacts, previews |
| `knowledge/` | Data that has passed review, with provenance |
| `scripts/`, `tests/`, `skills/`, `commands/` | Code, tests, agent skills and slash commands (each module belongs to one domain, see the domain cards) |
| `docs/` | PowerPoint-domain documentation plus lab history (`CHANGELOG.md`, `STATUS.md`) |
| `workspace/` | Scratch output, git-ignored. Never committed |

Nothing else belongs at the repository root. `lab/tools/check_layout.py`
enforces this, and a test runs it.

## Roles

| Role | Does | Must not |
|---|---|---|
| **Researcher** | Claims a task, frames a question, builds and measures, writes a REPORT | Merge their own work into `main`; review their own work |
| **Reviewer** (red team) | Reproduces, critiques and gives a verdict in `research/reviews/` | Rewrite the reviewed work; add review-only changes to the author's branch |
| **Integrator** | Merges reviewed work and resolves data conflicts by `standards/MERGE.md`; rewrites STATUS/HANDOFF | Merge unreviewed code into a product path |
| **Owner** (togcoder) | Sets direction, approves merges to `main`, authorizes redistribution | — |

One agent can hold different roles on different tasks, never two roles on the
same task.

## Principles

- **Domain-native first.** Learn the target application's own canon
  (PowerPoint presets, Word styles, Excel chart model, SVG/print standards)
  before transferring ideas from another domain. Write down every transfer and
  test it.
- **Evidence over assertion.** Name the rung (`standards/RESEARCH.md`). A
  simulation is not playback, and a score is not a human judgement.
- **Disagreement is data.** A rejected idea and a failed experiment are kept
  and reported, not deleted. Dissent goes into the review and the domain card.
- **Native and editable** output in the target application is preferred over
  raster or video fallbacks, which are labelled when used.
- **Synthetic data in demos.** Reference media stays local unless the owner
  authorizes redistribution.
