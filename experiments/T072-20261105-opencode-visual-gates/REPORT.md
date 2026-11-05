# T072 [pptx] — Visual error gates on rendered frames

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max).
- **Date:** 2026-11-05. **Base:** `main` @ `bbdc3a3`. **Branch:**
  `work/T072-opencode-visual-gates`.
- **Capability:** `pptx.critic` (extended the canonical `scripts/design_critic.py`;
  no new script, so no new registry entry).
- **Status:** prototype complete; review requested. D001 applies: these are
  technical gates, not evidence that the deck is better to the owner's eye.

## Frame

**Question.** The T070 evidence shows decks scoring 4.99 with empty cards,
clipped/scaffold text. Can a machine catch the errors a human sees immediately,
on the same PowerPoint frames, without inventing new taste?

**Hypothesis.** Six structural visual errors are measurable directly from the
native model plus the `Slide.Export` PNG:

| Code | Error |
|---|---|
| `VIS-CLIPPED` | text needs more height than its box, or crosses the 3 % safe margin |
| `VIS-EMPTY-CARD` | a large filled card with no content, or a large content field with only a label |
| `VIS-PLACEHOLDER` | scaffold text ("Chuyển Đổi Số Toàn Diện", "Bước hoàn thiện", "Chỉ số 1", …) |
| `VIS-TINY` | body text below 12 pt (kickers/captions/dates are metadata, not body) |
| `VIS-STYLE-DROP` | a declared style font is absent from the deck theme |
| `VIS-COLLIDE` | two movers overlap in the same frame (T073 supplies the frame pairs) |

**Falsifiers.**
- The gate misses the empty cards in the T070 evidence.
- The gate floods T066 with false positives.
- A code has no test.
- The gates change the critic's scores so much that the technical score becomes
  the quality claim (D001).

## Frozen input

- **T068 deck:** `experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx`
  and its PowerPoint render `preview/slide-01..03.png`.
- **T066 control:** `experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx`
  and `preview/slide-01..10.png`.
- **T069a control:** `experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx`
  and `preview/slide-01..14.png`.
- **T070 evidence:** `experiments/T070-20261104-claude-lead-synthesis/preview/critic-499-vs-eye.jpg`.

## Method

`scripts/design_critic.py` gained:

1. `visual_findings(slide, groups, style, theme_fonts)` — pure model checks for
   clipped, empty, placeholder, tiny and style-drop; returns code + measured +
   expected + fix, using `text_metrics.wrap_lines` for the text-height estimate.
2. `collision_findings(pairs)` — the `VIS-COLLIDE` gate for T073 frame pairs;
   not guessed from geometry, because cards contain their own content.
3. `--style PATH` — optional `VisualStyle/1` font list for `VIS-STYLE-DROP`.
4. All codes are in `DIMENSION` (`VIS-COLLIDE` in motion, the rest in design) and
   `FIX`, so they appear in the normal issue list and markdown report.

Run:

```powershell
python scripts/design_critic.py DECK.pptx --render PREVIEW_DIR -o out.json
```

The render directory is the PowerPoint `Slide.Export` PNG set, not a screenshot
montage. `VIS-COLLIDE` is intentionally **not** run on model geometry; T073's
frame sampler owns it.

## Evidence

| Deck | Visual gates | Critic overall | What it proves |
|---|---|---:|---|
| T068 directed | **2 × `VIS-EMPTY-CARD`** (`Major Content`, `Minor Content`, slide 2) | 4.92 | the gate sees the empty cards that the eye sees; the score still does not (D001) |
| T066 control | **10 × `VIS-TINY`** (body 10–11 pt on slides 6, 8, 10) | 3.74 | true body-size defect, no clipped/empty/placeholder false positive |
| T069a control | **0 visual gates** | 4.32 | the repaired deck does not trigger the gates |

The T068 empty cards are annotated in
`preview/t068-empty-cards.png`; the yellow boxes are the flagged content fields.

The T070 composite also shows a clipped title. That image is a **montage/crop**,
not a `Slide.Export` frame: the actual T068 slide-01 render does not clip the
title and the geometry is inside the safe margin, so `VIS-CLIPPED` correctly
does not fire. A screenshot crop is outside T072's frozen input; the gate runs on
the deck frame, not on the document that quoted it.

## Tests

`tests/test_visual_gates.py` — **9/9 pass**:

- clean slide → no gate;
- `VIS-TINY` flags body, not kicker;
- `VIS-PLACEHOLDER` catches a scaffold phrase;
- `VIS-EMPTY-CARD` flags an empty card and accepts a card with child text;
- `VIS-CLIPPED` flags overflow and ignores a quote mark;
- `VIS-COLLIDE` from an overlapping frame pair;
- `VIS-STYLE-DROP` from a declared font absent from the theme.

Full suite and `check_layout.py` are run before the commit; results are in the
final message and the changelog.

## Negative results and limits

1. **No frame sampler yet.** `VIS-COLLIDE` is a tested function but is not wired
   into a runtime frame source; T073 must supply the pairs. A geometry-only
   collision check produced false positives (title/card, card/content), so it is
   deliberately not used.
2. **`VIS-CLIPPED` is an estimate, not OCR.** It uses font metrics and box
   geometry; it cannot see a font substitution or a PowerPoint autofit decision.
   It catches gross overflow, not a one-pixel optical clip.
3. **`VIS-STYLE-DROP` needs a style manifest.** It is only as good as the
   `--style` JSON; no deck in this run declared one.
4. **Metadata exemption is a judgement.** Kickers, captions, dates and timeline
   labels are allowed below 12 pt. That is a rule choice, not a measurement; a
   reviewer should confirm it.
5. **T068 still scores 4.92** after the two errors. This is the D001 problem:
   the gate is visible in `issues`, but the aggregated score does not make the
   empty cards expensive enough. T071/T072 follow-up should weight error codes,
   not average them.
6. **No human review.** Rung 5 (PowerPoint render + structural gate), not rung 6.

## Files

- `scripts/design_critic.py` — visual gates, `--style`, `collision_findings`.
- `tests/test_visual_gates.py` — 9 tests.
- `experiments/T072-20261105-opencode-visual-gates/artifacts/*-visual.json`.
- `experiments/T072-20261105-opencode-visual-gates/preview/t068-empty-cards.png`.
- `experiments/T072-20261105-opencode-visual-gates/inputs/run_visual_gates.py`.
- `experiments/T072-20261105-opencode-visual-gates/inputs/annotate_t068.py`.

## Next

1. T073: wire `collision_findings` to real PowerPoint show frames; measure false
   positives on the gold deck set.
2. Weight `VIS-*` as errors in the score, or keep them out of the score and put
   them in a separate gate list (T071 decides).
3. Add a `VIS-CLIPPED` pixel-edge check on `Slide.Export` PNGs after T073.
