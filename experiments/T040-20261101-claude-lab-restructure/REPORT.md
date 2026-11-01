# T040 [cross] — Multi-domain lab restructure: domains, agent protocol, standards

## Frame
- **Question.** The owner turned the project into a multi-domain design lab
  (several agents researching and critiquing design for many applications).
  Two problems remained:
  - agents working on any application kept following the one
    PowerPoint-shaped line of thought;
  - verification slides landed in the repository root.

  How should the repository and the agents' way of working be organised?
- **Hypothesis.** Domain cards, a fixed lifecycle with peer review, and
  explicit merge and placement standards, enforced by a layout check, give
  each domain its own line of thought and keep outputs out of the root. The
  hypothesis fails if:
  - new tasks still land without a domain;
  - files still land in the root without the check failing.
- **Domain lens.** Organisation only. No new design research, per the
  owner's instruction.

## Frozen input
- **Request.** 2026-11-01, budget about $12; "do not research further".
- **Base.** Research tip `work/T038-pptx-design-canon-tokens` (7e4a52d) plus
  the T039 claim, merged into `claude/blissful-pasteur-gmll59`.
- **Environment.** Cloud session: Python 3.11, no PowerPoint.

## What changed
| Area | Change |
|---|---|
| Lab operating system | `lab/CHARTER.md` (mission, structure, roles, principles), `lab/PROTOCOL.md` (orient → claim → frame → research → self-check → review → respond → merge → handoff; anti-monoculture rules) |
| Standards | `lab/standards/RESEARCH.md` (report sections, generic evidence rungs 0–6), `REVIEW.md` (who reviews, reproduction required, verdicts accept / revise / quarantine / reject), `MERGE.md` (one canonical module, data provenance, conflicts kept side by side), `OUTPUTS.md` (where every file goes; never the root) |
| Shared assets moved under `lab/` | `protocols/`, `schemas/`, `registry/`, `templates/`. Code paths in `artcraft_hub.py`, `sync_artcraft_capabilities.py` and `validate_handoff.py` updated. New templates for claim, review and report |
| Domains | `domains/README.md` registry and cards for pptx, docx, xlsx, svg and cross: scope, thesis, native canon, code status, evidence ladder, state, dissent. The PowerPoint-only rules moved out of `AGENTS.md` into the pptx card |
| Reviews | `research/reviews/` with README; reviews are mandatory before product paths |
| Placement | Root whitelist. `workspace/` git-ignored for scratch. `output/` frozen with `output/LEGACY.md`. `examples/` grouped by domain (`examples/pptx/`) |
| Enforcement | `lab/tools/check_layout.py` and `tests/test_lab_layout.py`. They fail on unexpected root entries, media or office files at the root, new files in `output/`, domains without a card, experiments without a registered ID, and tasks ≥ T040 without a REPORT |
| Agents | `AGENTS.md` rewritten lab-wide. `HANDOFF.md` rewritten (the T038 version is archived) |

## Evidence
| Claim | Rung | Evidence |
|---|---|---|
| The layout check catches stray outputs | 1 | A `demo.pptx` at the root and a new file in `output/` were each reported (exit 1), then removed |
| The current tree passes the check | 1 | `python3 lab/tools/check_layout.py` → `layout OK`; `tests/test_lab_layout.py` passes |
| Moving shared assets broke nothing | 1 | Full test suite: same result as before the move. The only failure, a WORD_BREAK on "Logo Watermark" in T038's `test_chrome_injection_progress_bar_and_logo` (font metrics), predates this task |

## Negative results and limitations
- **Code not moved.** Code still lives in `scripts/`. A domain-per-package
  move touches imports, skills, tests and frozen experiment reports, so it is
  queued as **T041** instead of being done under budget.
- **Rules untested in practice.** Review and anti-monoculture rules are
  documents plus one check. Whether agents follow them is untested.
- **Machine-checked vs not.**
  - Checked: placement, domain cards, registered IDs, and REPORT presence
    for new tasks.
  - Not checked: reviews before merge.
- **Unreviewed work.** T035–T038 were not reviewed here; they are marked as
  unreviewed in the domain cards.

## Next
- T041: per-domain code packages.
- Cross-reviews of T035–T038.
- T039 writes the docx and xlsx theses first.
- Add a check that a product-path import of a module requires an `accept`
  review file.

## Review response
(none yet)
