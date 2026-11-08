# T091 [pptx] — Rung-6 grades: simple-but-fit motion, composition first

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash).
- **Date:** 2026-11-08. **Branch:** `work/T091-opencode-rung6-motion-law`.
- **Status:** research plus a **guidance change** in `skills/pptx` (six short
  blocks, no code). No product path or dependency changed.
- **Addresses:** F2 ("motion has no gu"), F20 (T087 demo 7/10), F21 (T069a
  6/10). Related: F8 (Morph is hard), D001 (the eye is the measure), D011
  (guidance before code).

## Open first

Two decks, both already built. Watch the same cuts the owner watched:

- T087 demo, 5 slides:
  `experiments/T087-20261106-claude-pptx-guidance-skill/artifacts/demo-triet-hoc.pptx`
  — slide 1 → 2, the three portraits slide into the timeline.
- T069a, 14 slides:
  `experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx`
  — the four Morphs: 3→4, 5→6, 8→9, 12→13.

The question: why does the **simpler** deck read better?

## Frame

**Question.** What separates "simple and fitting" (7/10) from "simple and
forced" (6/10), when both decks use few effects and one obvious continuity?

**Hypothesis.** Not complexity. Two conditions decide the grade:

1. **Composition.** Both endpoints of a cut must stand as posters. A Morph
   between two weak frames reads as two layouts swapping, not one idea
   changing.
2. **Visible continuity.** One object the audience can see must travel the cut.
   If the audience has to decode which shape became which, the cut is forced.

**Falsifiers.**

- The two decks differ mainly in length/context, and the grades say nothing
  about motion.
- T069a's frames are compositionally sound by the lab's own design measure.
- The owner's "gượng gạo" cannot be turned into observable questions.
- The T087 demo passes because it is short, not because its motion fits.

## Frozen input

| Deck | SHA-256 | Slides | Motion |
|---|---|---|---|
| T087 demo | `D1A05FF6E1FE9945FD1CDE7303C657A056985C8CE1AF8B509FF31E6EA03D2DE8` | 5 | simple fades/rise + 1 cover→timeline Morph |
| T069a | `7A3D45890FDEAC380A468C2E0CD5D8F043619241245285048ECF27CB27C6948D` | 14 | 9 clicks, 61 effects, 4 `byObject` Morphs (1.2 s) |

The grades are the owner's, given after opening both files in PowerPoint on
2026-11-08 (rung 6). The quotes are in
`research/feedback/2026-11-08-motion-grades.md` (F20/F21).

## Method

1. Re-read the two reports and the skill guides the demos were built from
   (T087's `SKILL.md`, guides 3, 6, 7, 8).
2. Compare the owner's words with the artifacts and with the lab's own
   measures (design critic, state critic, Morph audit).
3. Turn "gượng gạo" into four questions an agent can ask before adding a cut.
4. Write the smallest guidance patch that would have stopped T069a's weak
   cuts, in the guides' own voice.
5. Record the grades; do not touch T087/T090 branches.

## Findings

### 1. The grades are a vote for fit, not for less motion

T087 has **one** Morph and a handful of fades; it scored **7/10**. T069a has
**four** "semantic" Morphs and 61 effects; it scored **6/10**. If the lesson
were "less motion", the gap would run the other way. The owner's words name the
difference: T087's effects are "rất phù hợp với môi trường 1 bài thuyết trình
trên trường" — they fit a classroom. T069a's are "quá gượng gạo" — they try to
prove something the frames do not support.

So the target is **the right amount**, set by the idea and the room, not a
quota. T067's "3–4 semantic Morphs" was a useful hypothesis; it is not a rule
that survives contact with the eye.

### 2. T069a's composition was already weak by the lab's own measure

T069a's report records **design 3.99**, below T066's 4.03, while the narrative
score is 4.92. The team read the narrative score as the win. The owner watched
the deck and named the composition first. The design critic had already seen
it; nobody treated it as a blocker because the Morphs were the headline.

This is D001 repeating in a new place: a high narrative score is a technical
check, not evidence that the deck reads well. A Morph cannot repair a weak
poster; it animates the weakness.

### 3. The Morph audit is structural, and T069a proves the gap

`morph_studio.py audit` reports **0 findings** on T069a. Every rule in T074 is
satisfied: same shape types, shared `!!` names, no entrance on the destination,
no off-slide destination. The owner still reads the cuts as forced.

The audit answers "will PowerPoint interpolate these two objects?" It does not
answer "will the audience read one idea?" Those are different questions, and
the second one is the one the owner grades. T074's report already warned that
the audit is structural; T069a is the first human datum that shows how large
the gap can be.

### 4. T087's guidance had the right instinct but no stop

The skill already says "bản tĩnh phải đẹp trước" and "ít chuyển động mà đúng
tốt hơn nhiều chuyển động mà sai". Those instincts produced the 7/10. What was
missing is operational:

- no **room scale** — the same deck is judged against a classroom, a thesis
  defence, a conference stage, or a reader alone;
- no **poster test** specific to Morph endpoints — the static check exists per
  slide, but not "both ends of this cut must stand without the cut";
- no **forced-cut test** — a question that catches a "semantic" pair the
  audience cannot decode.

### 5. The patch is six short blocks, now applied

`skill-patch.md` records the blocks; the same text is in `skills/pptx`:

| File | Addition |
|---|---|
| `guides/6-chuyen-dong.md` | room table; four forced-cut questions |
| `guides/3-bo-cuc.md` | poster test before motion |
| `guides/8-tu-kiem-tra.md` | poster and forced-cut questions in the self-check |
| `guides/7-morph.md` | "Morph does not fix composition"; audit limit |
| `SKILL.md` | choose motion level by room, not by effect count |

No code is added. The toolbox already writes and audits the cuts; the missing
piece is a written reason to stop.

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| T087 demo reads better than T069a | Owner opened both in PowerPoint and graded 7/10 vs 6/10 | 6 |
| T069a's motion is "gượng gạo" and its composition is weak | Owner's words, same session; T069a design 3.99 < T066 4.03 | 6 |
| T069a passes the structural Morph audit | `morph_studio.py audit`: 0 findings (T074 report) | 4 |
| The skill's existing instincts are sound | T087 demo built from the skill, 7/10 | 6 |
| Room scale + poster test + four questions would prevent this class of failure | **not measured**; applied in this branch, to be graded in T090/T071 | 0 |

## Negative results and limits

1. **One owner, two decks, one session.** This is not a controlled A/B: the
   decks differ in length, content and purpose. The grade gap is consistent
   with the fit/composition hypothesis, not proof of it.
2. **The T087 demo was built by the skill's author.** It shows the guidance can
   be followed by its writer; T090 (a different model family) is the test that
   is still missing.
3. **The patch is applied but not measured.** It is six text blocks in
   `skills/pptx`; no deck has been rebuilt against them yet. The next
   measurement is T090's rebuild and the owner's grade.
4. **"Gượng gạo" is the owner's word.** The four questions are our
   operationalization; the owner has not graded them.
5. **No Morph rule was contradicted.** The owner did not mark any of the 11
   rules wrong; the missing dimension is composition and intent, which the
   rules do not cover.
6. **The 6/10 is not "delete the deck".** T069a still has the readable base
   states, the corrected timeline, and the lifecycle work. The negative finding
   is specific to the four cuts and the composition that carries them.

## Next

1. **Review this branch.** The six blocks are in `skills/pptx`; T087 merged as
   `5976663`. Keep T090's R1–R6 fixes (`research/reviews/T087-dsh-20261108.md`,
   merged in `aaa33b9`) alongside them; they cover different faults (line-wrap
   ghosting, entrance-only toolbox, legacy entry points) and are still open.
2. **T090 (DSH session):** rebuild the 7-slide deck against the patched skill;
   the owner grades the slide-3 Morph again.
3. **T071 bench:** add a classroom brief and a conference brief. The same
   content should choose different motion levels; that is the room-scale test.
4. **T075/T076:** make the poster test a precondition for compiling a scene;
   a scene whose endpoints do not stand should fail before timing is written.
5. **T074 rulebook:** keep the 11 rules; add the audit limit (done in this
   branch) so a clean audit is never read as "the cut is good".

## Files

- `skill-patch.md` — the six blocks and why they were chosen; the same text is
  now applied in `skills/pptx`.
- `skills/pptx/SKILL.md`, `guides/3-bo-cuc.md`, `guides/6-chuyen-dong.md`,
  `guides/7-morph.md`, `guides/8-tu-kiem-tra.md`, `examples.md` — the applied
  guidance and the approved demo.
- `../../research/feedback/2026-11-08-motion-grades.md` — F20/F21, owner's words.
- Appended rung-6 notes:
  `experiments/T069-20261104-opencode-directed-deck/REPORT.md`,
  `experiments/T074-20261105-opencode-morph-rules/REPORT.md`,
  `experiments/T074-20261105-opencode-morph-rules/morph-rules.md`.
