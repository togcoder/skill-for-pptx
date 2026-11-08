# Morph matching rules — T074 proposal

Status: **proposal**, not `knowledge/` canon. Evidence: a 15-pair matrix
(`artifacts/morph-matrix.pptx`), PowerPoint `CreateVideo` at 30 fps, and the
frames in `preview/states/`. Rung 5 for the colour-tracked cases; rung 3 for
`byWord`/`byChar`; `picture-diff` is not measured.

## The rules

| # | Rule | Evidence | What to do |
|---|---|---|---|
| M-01 | Same shape type + similar geometry pairs even when names differ. | `same-bang`, `same-name`, `diff-name` all one blob crossing the frame. | `!!` is a hint, not a requirement, for simple shapes. Do not rely on names alone to *prevent* a pair. |
| M-02 | `!!` cannot force a pair across shape types. | `rect-ellipse`: same `!!track`, two blobs in the middle. | Keep the same shape type across a Morph. Change geometry, not the preset shape, when continuity matters. |
| M-03 | Text boxes pair as shapes; different text does not break the geometry. | `text-same`, `text-diff`: one blob moving. | Use text Morph for a label that stays a label; do not expect the words themselves to be measured here. |
| M-04 | A picture frame pairs with the same picture frame. | `picture-same`: continuous. | Different media (`picture-diff`) is **not measured**; keep it out of automated claims. |
| M-05 | Groups pair as groups when the group name/geometry matches. | `group-same`: one blob. | Do not ungroup between the two states unless you accept a cross-fade. |
| M-06 | 90° rotation still pairs. | `rotate90`: one blob. | Rotations >180° and flips remain open. |
| M-07 | An entrance effect on the destination object blocks the Morph. | `entrance`: the object never leaves the A frame in the video. | Never put an entrance on a `!!` object. This confirms T067's Morph/entrance conflict rule. |
| M-08 | An off-slide destination is absent, not staged. | `offslide`: B at x=14.5 in; the B frame is an empty stage. | Stage the copy just outside the edge yourself, or keep the destination on-slide. |
| M-09 | `byWord` and `byChar` keep the frame continuous. | `byword`, `bychar`: one moving blob. | Geometry is safe; the glyph interpolation is not frame-verified. |
| M-10 | Z-order does not stop the pairing, but can hide the object. | `zorder`: one blob, 11 visible pixels under the foreground. | Order the destination objects deliberately; a covered actor is still morphing. |
| M-11 | A Morph adds its duration to the slide advance. | 45 × 2 s = 90 s expected; 109.4 s delivered with 15 × 1.2 s Morphs. | Budget the deck clock, not only the per-slide duration. |

## Audit a deck

```powershell
python scripts/morph_studio.py audit deck.pptx
```

Exit 1 when a `MORPH-TYPE-MISMATCH`, `MORPH-ENTRANCE` or `MORPH-OFFSLIDE` is
found. `MORPH-UNNAMED-PAIR` is a warning: two same-type objects with no `!!`
name that PowerPoint may pair by geometry.

## What the audit cannot see

T069a passes this audit with **0 findings**, yet the owner read its four Morphs
as *"quá gượng gạo"* (forced) and scored the motion 6/10 on 2026-11-08, naming
the composition as well. The audit checks type, name, entrance and off-slide
position; it cannot check whether the two frames compose or whether the cut
carries one idea. A clean audit is necessary, not sufficient.

The human tests are in
`experiments/T091-20261108-opencode-rung6-motion-law/skill-patch.md`: a poster
test on both endpoints, and four questions for a forced cut. Until those pass,
a structurally valid Morph is still a proposal.

## Do / do not**Do**

- keep the same shape type across the cut;
- use `!!name` when several same-type objects could pair ambiguously;
- keep all Morph actors on-slide and without entrance effects;
- stage an off-slide copy manually if the actor must fly in;
- check z-order before trusting a Morph.

**Do not**

- use `!!` to morph a rectangle into an ellipse;
- put a Fade/Appear on the destination actor;
- assume an off-slide B object will fly in;
- treat a name match as stronger than a shape-type match;
- claim picture-media morphing until it is measured.

## Open cells

Charts, tables, SmartArt, 3D, connectors, gradient changes, flips, >180°
rotation, ungrouping, different picture media, and `byWord`/`byChar` glyph
interpolation are not in this matrix. The 15 measured cases are the ones a deck
builder hits first; the rest need a second pass.
