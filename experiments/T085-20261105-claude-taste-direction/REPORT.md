# T085 [cross] Lead: owner's 2026-11-05 direction

- **Agent / model:** Claude (Opus 5.5), lead. **Date:** 2026-11-05.
- **Branch:** `work/T085-claude-taste-direction`.
- **Addresses:** `research/feedback/2026-11-05-taste-and-review.md`, items F10–F14.

## Visual review that led here (rung 6: lead's eye; owner scores in the ledger)

| Deck | What works | What does not |
|---|---|---|
| T066 Triết học, static (`experiments/T070-…/preview/t066-bespoke-deck.jpg`) | Red and cream palette, serif titles, red-toned round portrait cut-outs, the Marx quote slide | Three slides repeat the same 3–4 small-text card grid; the card text is too small for the back of the room; the "dialectics vs metaphysics" diagram (yellow disc and arrow) explains nothing; dead space |
| T066/T067 motion (`experiments/T067-…/motion/evidence-sheet.png`) | Each slide has a base state at t=0 | One verb only, **appear**: empty frames, then content fades in. Nothing transforms, and nothing carries from one slide to the next (the three portraits on slide 1 should travel into the slide 7 timeline) |
| T067 five styles (`experiments/T067-…/preview/all-styles.png`) | Shows range: editorial, glass, clay, Swiss, collage | No style chosen and pushed to the end |
| T081 pitch script (owner: 6/10) | Strong intent sheet; persistent actors named | Motion is written as stock effect names (Teeter, Descend, Wipe, Fly Out). It never says where the eye goes or which object becomes which |

## Outside reference: `jimliu/baoyu-design`

- **Where its taste lives:** in written craft rules with numbers, learned from rejected work.
  Its motion page states that each "don't" was shipped once and sent back. Taste also comes
  from a comment loop on the rendered artifact.
- **Ideas worth testing in PPTX** (our wording):
  - transform instead of cut between ideas;
  - one subject moves at a time;
  - no frozen frame on a hold;
  - staggered related entrances;
  - time for the eye to settle after a big move;
  - write the title outline before the slides.
- **Licence:** its reference docs are Anthropic material with no licence (its `NOTICE.md`),
  so we learn ideas and do not copy text (D010).

## Changes

- New feedback ledger file with F10–F14.
- Decisions:
  - D001 amended;
  - D009 added: the `.pptx` is the deliverable, and the owner needs no video;
  - D010 added: researched crowd taste, our own words, tested blind, never copied.
- ROADMAP:
  - new brief T086, crowd taste across at least 8 fields;
  - T071 outputs `.pptx` pairs;
  - T073 is a tool for agents;
  - the weekly release is reviewed by flipping through `.pptx` files.
- HANDOFF: T086 added to the next-task table.
- INDEX: T086 reserved; the next free ID is T087.

## Follow-up: F15, "a skill is not necessarily code"

The owner is right, and the lab's own numbers show it:

- **The lab is code-first.** It has 103 scripts. The 8 skills (2,055 lines) are mostly command
  manuals for those scripts (for example `pptx-motion`: "run `inspect_existing_deck.py`, validate
  with `validate_director_plan.py`"). They say almost nothing about how to design.
- **The best deck came from judgement.** T066 was made with taste and a bespoke script, not
  through the tool chain.

Changes:

- D011: a skill is written guidance; code is only its toolbox.
- New brief T087: one PPTX skill written as plain-language design guidance.
- T075 and T077 paused.
- T086 now outputs guidance text, not JSON.
- AGENTS.md: two new rules, "skill = guidance" and "talk to the owner in plain words".
