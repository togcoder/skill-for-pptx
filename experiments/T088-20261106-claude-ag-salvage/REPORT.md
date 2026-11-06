# T088 [cross] Lead review of T081 and T086 (Antigravity): merge the useful parts

- **Agent / model:** Claude (Opus 5.5), lead. **Date:** 2026-11-06.
- **Branch:** `work/T088-claude-ag-salvage`.
- **Why:** the owner asked that Antigravity's two PRs be reviewed fairly, not closed unread,
  because the agent did research reputable design projects.

## Result

| PR | Verdict | Kept | Review |
|---|---|---|---|
| #66 T081 script-writer | accept in part | skill text (with lead note), `motion_script check` + tests, the attempt's record | `research/reviews/T081-claude-20261106.md` |
| #67 T086 crowd taste | accept as research notes | `sources.md`, 13 domain notes (moved to `notes/`), 4 pairs | `research/reviews/T086-claude-20261106.md` |

## Model check

The reports name "Gemini 2.5 Pro" and "Argon". The local Antigravity conversation databases
(`~/.gemini/antigravity/conversations/*.db`, table `gen_metadata`) record `gemini-3.8-flash` for
every session on 2026-11-05 and 2026-11-06. Only model names were read; no account files were
read. A model's statement of its own name is not evidence.

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| Kept code works | `pytest tests/test_script_writer.py`: 12 passed; full suite in the PR | 1 |
| Layout | `check_layout.py`: layout OK | 1 |
| T086 "after" slides are mostly empty | the lead looked at the 4 pair previews | 6 (lead's eye) |
