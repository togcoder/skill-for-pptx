# T092 [pptx] Guidance fixes from the T090 cross-family review

- **Agent / model:** DSH (DeepSeek V4.1 Flash), DeepSeek Harness. **Date:** 2026-11-08.
- **Base:** `origin/main` @ `aaa33b9` (T090 merged, PR #70). **Branch:**
  `work/T092-dsh-skill-guidance-fixes`.
- **Trigger:** the owner asked for the review findings to be turned into a patch for the lead
  ("làm ý 1"), after T087 (#69) and T090 (#70) were merged.
- **Status:** review requested. Guidance text only; no code, no product-path code.

## Frame

**Question.** Which of the ten findings of `research/reviews/T087-dsh-20261108.md` can be applied as
guidance text without a code change, and does applying them keep the lab green?

**Hypothesis.** The eight findings about wording, examples and missing rules are pure guide edits;
R2 (the toolbox/critic contradiction) and R9/R10 (image-export overlap, missing zoom test) need a
lead decision or code, so they stay in the review.

**Falsifier.** A guidance edit contradicts the critic or the toolbox (e.g. telling the model to do
something `pptx_tools` cannot write), or the patch breaks tests/`check_layout`.

## Applied (guidance only)

| Review finding | File | Change |
|---|---|---|
| R1 Morph text wrap | `skills/pptx/guides/7-morph.md` | New rule 9: a Morph actor must break its text lines identically on both slides; a different wrap ghosts the text mid-Morph. |
| R6 `UNNAMED-PAIR` | `skills/pptx/guides/7-morph.md` | Same-position titles/eyebrows/frames will be reported; that is normal, do not break guide 3 to silence it. |
| R5 decorative glyph size | `skills/pptx/guides/4-chu-va-mau.md` | Decorative type glyphs must use a size from the deck scale (`TYP-SIZES` counts them). |
| R7 t=0 check | `skills/pptx/guides/8-tu-kiem-tra.md` | Run the t=0 check **before** writing motion: subtract clicked shapes and see whether the slide stands alone. |
| R8 `DEN-WORDS` | `skills/pptx/guides/8-tu-kiem-tra.md` | The 45-word band is for narrative slides; tables/maps may exceed it — record it, do not cut content. |
| R2 known limit | `skills/pptx/guides/6-chuyen-dong.md` + guide 8 | State honestly that `pptx_tools` writes entrances only, so `NAR-LIFECYCLE` is a known toolbox limit, not a slide defect. The actual fix (dim/exit vs critic exemption) is left for the lead. |
| R4 speaker notes | `skills/pptx/guides/9-do-nghe.md` | Notes template `[T=0]`, `[CLICK 1]`, `[CLICK 2]` … with the count matching the slide's clicks (`NAR-ALIGN`). |
| R3 legacy entry | `skills/slide-forge/SKILL.md`, `skills/pptx-motion-director/SKILL.md`, `skills/deck-director/SKILL.md` | D011 banner: the PPTX entry point is `skills/pptx/`; the file is the old command manual. |

**Not changed on purpose:** R2 code decision; R9 (canonical image export); R10 (zoom test). They are
listed in the review for the lead.

## Checks

- `python lab/tools/check_layout.py` → `layout OK`.
- `python -m unittest discover -s tests` → **582 tests OK, 10 skipped**.
- No script or `lab/capabilities.json` change; therefore no registry update needed.

## Limits

- The new rules are words; the next model still has to follow them. T090's own deck showed the ghost
  bug, and this patch is the "fix the guidance first" step D011 asks for.
- The `NAR-LIFECYCLE` contradiction is documented, not solved: a deck built with `pptx_tools` will
  still show the warning until the lead chooses dim/exit or a critic exemption.

## Next

1. Lead (or owner) reads the diff and merges; then the next T087-style run should not repeat R1/R4.
2. Lead decision on R2, then either extend `pptx_tools.motion` with `dim`/`exit` or add the critic
   exemption.
3. Add the zoom case to `tests/test_pptx_tools.py` (R10) when the toolbox is touched next.
