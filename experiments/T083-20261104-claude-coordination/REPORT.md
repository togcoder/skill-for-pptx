# T083 [cross] Coordination layer: registry, binding decisions, claim/board/check

- **Agent / model:** Claude (Opus 5.5), lead, desktop session. **Date:** 2026-11-04.
- **Branch:** `work/T083-claude-coordination`, stacked on `work/T070-claude-lead-synthesis`.
- **Request (owner):** "Skills grow in parallel and independently across agents, so the last
  version is not necessarily final. We need something that lets agents and humans communicate
  better, so they stop stepping on each other."

## Frame

- **Question:** why do agents step on each other although `lab/standards/MERGE.md` already
  says "one canonical module per capability"? What is the smallest mechanism that makes the
  collisions we have seen impossible, or at least visible before merge?
- **Hypothesis:** the rules exist only as prose. Nothing checks them, and the shared state lives
  in places that are invisible or have many writers:
  - claims sit on unpushed or unmerged branches;
  - HANDOFF is rewritten by whichever agent finishes last;
  - module ownership is a table in several domain cards;
  - the owner's feedback stays in one agent's session.

  The fix is a machine-readable owner per file, checked in CI. It needs a claim tool that sees
  every branch, a single writer for lab-wide documents, and one written place for decisions and
  for questions to the owner.
- **Falsifier:** `coord.py board` on today's repository finds no live collision. If so, the
  problem is behavioural only, and tooling would not help.

## Evidence of the problem (before)

| Collision | Where | Rung |
|---|---|---|
| Duplicate task IDs | T042, T043, T047, T048, T049, T069a/b | 1 |
| Parallel implementations of one capability | three `interactiveSeq` writers (until T061); two style systems (`theme_engine.py` T043, VisualStyle/1 T067); two script systems (`motion_script.py`, `deck_director.py`); two deck-state critics (`deck_state_critic.py`, the narrative dimension of `design_critic.py`) | 1 |
| A proposal ignored by the next agent | T067 asked T068 to reuse `motion_script`'s format; T068 did not | 1 |
| Scripts owned by no domain card | 27 of 103 | 1 |
| HANDOFF overwritten with other priorities | after T069 the agent's HANDOFF planned a "T070" that collided with the lead's T070 | 1 |
| Shared checkout edited by an agent | `scripts/deck_director.py` uncommitted in the owner's checkout while other agents worked there | 1 |
| `main` unprotected | `gh api …/branches/main/protection` → 404 "Branch not protected"; T043/T047–T049 were pushed straight to `main` | 1 |

## What was built

- `lab/capabilities.json`: 19 capabilities. All 103 scripts have **one** owner and one role
  (canonical, support, experimental, shim, tool, fixture, frozen). The file also records the
  known overlaps, the related reserved tasks, the lead and the single-writer files.
- `lab/DECISIONS.md`: eight binding decisions (D001–D008), each with its evidence.
- `lab/tools/coord.py`:
  - `claim`: computes the ID from `main` **and every open branch's INDEX and branch name**, so a
    reservation in an unmerged PR still counts. It then makes the branch and a worktree, writes
    the row and the claim file, pushes, and prints the briefing (capability files and roles,
    overlaps, binding decisions, other branches on the same capability, open owner feedback).
  - `board`: shows active branches, file and capability collisions between them, uncommitted
    edits in the shared checkout, and open owner feedback and questions.
  - `check`: unregistered or missing scripts and double owners are errors; a non-lead branch
    editing a single-writer file is an error; a product module importing experimental code is a
    warning.
- `lab/tools/check_layout.py` runs the checks in CI. `tests.yml` fetches full history so the
  branch can be compared with `origin/main`.
- `tests/test_coordination.py`: 8 tests.
- `AGENTS.md` and `lab/PROTOCOL.md`: claim with the tool; do not edit HANDOFF; ask the owner in
  `research/feedback/questions.md`.

## Evidence (after)

| Claim | Evidence | Rung |
|---|---|---|
| Every script registered, one owner each | `coord.py check` → "coordination OK"; test `test_every_script_has_exactly_one_owner` | 1 |
| The board finds live collisions today | `coord.py board`: 3 collisions. T054 × T055 both edit `HANDOFF.md`, `domains/svg/DOMAIN.md`, `skills/vector-craft/SKILL.md` and two tests; both also edit `HANDOFF.md` against T070. It also reports the uncommitted `deck_director.py` in the shared checkout. **The falsifier did not hold.** | 1 |
| The claim tool sees reservations on unmerged branches | dry run `--id T074` accepted, because the row exists only on the T070 branch; `--id T050` refused; the next free ID came out as T083 while `main` still said T070 | 1 |
| Product code importing experimental bridges is visible | 4 warnings: `design_critic` → `deckcraft_bridge`; `chart_forge` and `sheet_forge` → `gridcraft_bridge`; `document_forge` → `wordcraft_bridge` | 1 |
| Full suite | see the PR | 1 |

## Limits

- **All agents push with the owner's GitHub account.** GitHub cannot tell them apart, so the
  single-writer rule keys on the agent name in the branch. An agent can lie about its branch
  name. The check stops accidents, not bad faith.
- **Claims are race-free only up to seconds.** Two claims within the same few seconds can pick
  the same ID. The second push then fails loudly: the branch name differs but the INDEX rows
  conflict at merge.
- **Branch protection is the owner's decision** (Q1 in `research/feedback/questions.md`).
  Without it, a direct push to `main` is still possible.
- **The registry still needs a review.** Its roles are my reading of the domain cards, docstrings
  and imports. Some roles are judgement calls, for example `photo_vector` as experimental.
