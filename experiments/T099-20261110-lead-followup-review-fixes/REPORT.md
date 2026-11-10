# T099 [pptx] Follow-up fixes from T096/T097 review findings

Agent: lead · 2026-11-10 · review source: `research/reviews/T096-claude-20261110.md` and
`research/reviews/T097-claude-20261110.md` (both now in main).

## What was worth fixing now

The reviews were not just praise: they left concrete correctness hazards in the canonical toolbox. The high-value
ones are now fixed and regression-tested:

| Finding | Risk | Fix |
|---|---|---|
| T096 R2 | Vietnamese `1.200` was parsed as `1.2`, so a number gate could fail to notice a missing 1,200 | `_key_numbers` treats dot/comma groups of three digits as thousands; decimals such as `1.2%` remain decimals |
| T096 R3 | `sample --pages 99` or an empty PDF ended in a traceback | `sample` raises a short `ValueError` naming page count and bad pages |
| T096 R4 | A long PDF retained every thumbnail in memory | `sample` renders sheets in batches of 20 |
| T097 R4 | A diagonal table border could appear after the fill in the XML order | `style_table` inserts fill after all border/3D nodes, preserving diagonal borders |
| T097 R6 | Pillow deprecated `getdata`, and palette images could hash inconsistently | `_dhash` normalizes palette images and uses `get_flattened_data` when available |
| T097 R7 | An external/linked video could crash `extract` while looking for an embedded relationship | `_media` skips linked media cleanly; the manifest still has the slide, but no false embedded file |

## Guidance follow-up

The reviews also say the agent was told to "open the slide show". That is not an agent operation. The canonical
workflow already has `look`; T073's `watch` is still a separate open PR. I did not invent a command here: after T073
merges, guide 10/11 should name `watch --slides` for click-by-click playback, with `look` as the static fallback.

R5 (retable's project palette and lost phase colours) is deliberately not silently fixed here: changing the default
palette affects existing decks. It needs a separate decision/API: default header/rule colours from the source deck's
resolved theme, report every old fill replaced, and require explicit mapping for semantically different phase bands.
That is the next proposed task, not an untested default change.

## Evidence

- Focused original toolbox suite: 26 tests pass.
- Full suite: **604 tests pass, 10 skipped**.
- `check_layout.py`: expected lead-only HANDOFF warning only; no layout defect after the report is added.
- `coord.py check`: expected to pass after the T099 row/report are present.

## Scope and limits

No deck was modified. Changes are canonical `pptx_tools.py` correctness fixes plus tests; all numeric parsing,
PDF validation, table XML order, image hashing and linked-media behavior remain in the same toolbox. The review's
visual/owner-level concerns (small text, motion taste, sample quality) still require rendered or PowerPoint review;
these code changes do not claim to make a deck beautiful.
