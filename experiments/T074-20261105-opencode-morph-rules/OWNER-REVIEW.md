# Owner review — three short gradings (T069a / T072 / T074)

This is the **rung 6** request. No code reading is needed. The owner's eye is
the measure (D001); the critic scores are only technical checks.

## 1. The four Morphs in T069a (the important one)

Open:

`experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx`

Run the slideshow and watch these four cuts. Each is a 1.2 s Morph.

| Cut | Watch for | Score 1–3 |
|---|---|---|
| slide 3 → 4 | the two answer cards become the winning answer; does it read as **one idea changing**, or two cards cross-fading? | |
| slide 5 → 6 | the dialectic circle grows, the straight line recedes; one worldview winning, or two diagrams swapping? | |
| slide 8 → 9 | three parts move into one whole; does the triangle read as **one structure**, or three cards flying? | |
| slide 12 → 13 | quotation shrinks to a citation, “CẢI TẠO THẾ GIỚI” takes the frame; does the thesis land? | |

Scale: **1** = one object/idea, reads immediately; **2** = readable but I see
the trick; **3** = two objects/ghost, no meaning. Add one sentence per cut only
if the score is 2 or 3.

The question behind it: **is this “motion có gu”, or still effects with better
timing?** This is the original T066 complaint and the only judgement that can
close it.

## 2. T072 — did the visual gate see the right errors?

Open:

`experiments/T072-20261105-opencode-visual-gates/preview/t068-empty-cards.png`

The gate flagged two large content fields on T068 slide 2. Tell us:

- Are these the two errors **you** would point at? (yes / no)
- Is there a visible error in that frame the gate **missed**? (name it)

That is the calibration of the critic against your eye, not a design vote.

## 3. T074 — is any Morph rule wrong?

Read the 11-line table in:

`experiments/T074-20261105-opencode-morph-rules/morph-rules.md`

Mark only rules that contradict your experience. The two to check first:

- **M-02** — `!!` does not override shape type: rect → ellipse cross-fades.
- **M-08** — an object placed off-slide is absent, not flown in.

No need to agree with every rule; we need the wrong ones.

## Merge decision (separate from grading)

Both PRs are green after rebasing on T084:

- PR #63 — T072 visual gates
- PR #64 — T074 Morph rules + audit

Merging is the lead/owner decision (D008). Grading can happen before or after
the merge; the four Morphs are already on `main` in T069a.
