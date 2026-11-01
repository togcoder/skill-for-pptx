# Merge standard (code, data, knowledge)

## Code

- Every capability has **one canonical module**, named in its domain card. A
  second implementation is either merged into the canonical one (keeping the
  better parts, with tests) or labelled `EXPERIMENTAL`. Two live
  implementations of the same thing are not allowed.
- Product paths import only reviewed modules.
  `tests/test_lab_layout.py` and domain tests guard this.
- Merge through branches and PRs. Merge commits keep other agents' history;
  never rebase or force-push someone else's branch, and never force-push
  `main`.

## Data and knowledge

Every merged datum in `knowledge/` or a domain's data folder carries:

| Field | Meaning |
|---|---|
| `source` | URL, DOI, or file plus tool that derived it |
| `accessed` | date |
| `licence` | for anything stored or derived from third-party material |
| `scope` | the domain(s) it applies to; `cross` only after two domain reviews |
| `confidence` | `measured` (with experiment ID) / `published` / `judgement` |
| `task` | the task ID that introduced or changed it |

## Conflicts

When two tasks give different values or rules:

1. Keep both, side by side, with their provenance (the value plus an
   `alternatives` list).
2. Open a task to decide them with a test or a measurement.
3. The integrator picks the winner from the evidence and records the decision
   and the losing value in the CHANGELOG.
4. Never overwrite another task's value silently.

## Design systems

- Each domain owns its design-system data. PowerPoint's is
  `knowledge/design_system.json`. A new domain starts `domains/<d>/` data and
  must not add domain-specific keys to another domain's file.
- A value enters a shared cross-domain system only after accepted reviews in
  two domains.

## Docs after a merge

- One `docs/CHANGELOG.md` entry per task, appended.
- The domain card's "State" section is rewritten.
- `HANDOFF.md` and `docs/STATUS.md` are rewritten, not appended, when
  lab-wide state changes.
