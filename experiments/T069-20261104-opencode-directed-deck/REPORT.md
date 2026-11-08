# T069a [pptx] — Directed deck: four semantic Morphs, image blocks, state critic

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max).
- **Date:** 2026-11-04. **Base:** `main` @ `be53e81`. **Branch:**
  `work/T069-opencode-directed-deck`.
- **Status:** complete as research; no product path changed. New script
  `scripts/deck_state_critic.py` is **EXPERIMENTAL**.
- **Trigger:** T067 fixed T066's base states and image order but left **0 Morph**
  and **0 lifecycle**; T068 built the direction compiler but proved it on three
  slides. T069 combines both on the real 10-slide chapter: readable `t=0`,
  image blocks, **four state-pair Morphs**, and a critic that fails the old deck
  and passes this one.

## Frame

**Question.** Can the deck keep the visual language the owner liked (crimson
editorial, cut-out portraits, Palatino) while making motion carry the argument
instead of decorating the shapes?

**Hypothesis.** A Morph is legitimate only when the same object or idea
continues across the cut. Four pairs in this chapter do: the two answer cards,
the two worldviews, the three parts, and the quotation. If those pairs are
separated into stable states and joined by Morph, the deck needs **fewer**
clicks and reads better at `t=0`.

**Falsifiers.**
- Morph pairs share no object/idea, or a `!!` shape also has an entrance.
- A base state still needs a click to become readable.
- A picture or its frame arrives after the sentence that names it.
- The state critic passes a deck with an empty base or a coda image.
- PowerPoint does not report the Morph transitions or the file needs repair.
- The deck has no object lifecycle.

## Frozen input

- **Deck:** T067 directed copy
  `experiments/T067-20261104-opencode-deck-director/motion/artifacts/T066-deck-directed.pptx`
  (SHA-256 `00c34c4c…`, 2,014,494 bytes, 10 slides, 27 clicks, 116 effects).
- **Environment:** Windows 11, PowerPoint **16.0 build 17932**, Python 3.13,
  python-pptx, lxml, Pillow, pywin32.
- **Builder:** `inputs/build_directed_deck.py`.
- **Source images:** T066 `inputs/assets/` (Wikimedia Commons; public domain /
  CC0, recorded in T066).

## Method

1. **Strip the sequential timing** on slides 1, 3, 4, 6, 9 of the T067 copy, so
   each opens on its complete poster state (rings, cards, diagrams, quotation).
2. **Duplicate four B states** — after slides 3, 4, 6 and 9 — using
   `morph_studio.Package.duplicate_slide`. Each copy inherits the poster and
   carries no leftover timing.
3. **Name the continuing objects** with shared `!!` names (13, 16, 15 and 7
   pairs), then **redesign the B state**: the winner grows, the loser shrinks or
   dims; the three cards move into a triangle; the quotation shrinks into a
   citation while the thesis takes the frame.
4. **Set a 1.2 s `byObject` Morph** on each B slide, with a Fade fallback for
   clients that do not know `p159`.
5. **Reduce the remaining clicks**: slide 7 (orig. 5) still builds three
   conditions; slide 2 builds two definitions; slide 8 (orig. 6) opens with four
   functions and one click dims the first three; slide 10 (orig. 7) opens with
   all portraits/dates and one click draws the timeline; slide 14 (orig. 10)
   opens complete. Total **9 click groups**.
6. **Re-order slide 10** to Engels (1848) → Marx (1867) → Lenin (1917) and move
   the three timeline dots under the work each face carries.
7. **One type scale** for the deck: 12 / 16 / 24 / 36 / 54 pt. This removed 27
   distinct sizes (TYP-SIZES) without changing the hierarchy.
8. **Run the new state critic** on T066 and T069, then PowerPoint COM.

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Four Morph transitions are in the package | `p159:morph option="byObject"`, `p14:dur="1200"` on slides 4, 6, 9, 13 | 4 (XML) |
| PowerPoint parses them as Morph | COM `SlideShowTransition.EntryEffect = 3954` and duration 1.2 s on the same four slides; Fade (3849) elsewhere | 4 |
| Base state is readable everywhere | state critic: 0 `STATE-EMPTY-BASE`, 0 `STATE-NO-CLAIM`; every slide has a claim/title at `t=0` | 4 |
| Images are not a coda | 0 `STATE-IMAGE-CODA`, 0 `STATE-IMAGE-LAG`, 0 `STATE-DECOR-BEFORE-IMAGE` | 4 |
| Morph and entrance do not collide | 0 `MORPH-ENTRANCE-CONFLICT` (`!!` objects have no entrance) | 4 |
| Motion is smaller, not bigger | **9 clicks / 61 effects** vs T067 **27 / 116** and T066 **51 / 144** | 4 |
| Object lifecycle exists | **17 shape lifecycles** on slides 2 and 7; six function tiles were reduced to one focus | 4 |
| No wall of text | max active view **45 words** (was 80 in T066/T067); type scale 5 sizes (was 27) | 4 |
| Deck opens and renders | PowerPoint 16 opens 14 slides, 61 effects, 14 PNG + 14-page PDF, 0 repair | 4–5 |
| Critic | `design_critic.py` (with T069b narrative dimension): overall **4.33** (design 3.99, motion 5.0, rhythm 3.42, coherence 4.33, **narrative 4.92**), 0 errors; warnings: `MOT-STATIC`, `TYP-SMALL` note | 3 |
| State critic discriminates | T066: **FAIL**, 58 gates (51 fail, 7 warn) incl. empty base, title on click, rings before faces, coda images, Morph/entrance conflict; T069: **PASS**, 0 gates | 4 |
| A/B image order | slide 10 now 1848 Engels / 1867 Marx / 1917 Lenin; dots under the work, not the cast order | 5 (static render) |

**Artifacts.**
- `artifacts/T069-directed-morph.pptx` — 14 slides, 2,017,745 B,
  SHA-256 `7a3d45890fdeac380a468c2e0cd5d8f043619241245285048ecf27cb27c6948d`.
- `preview/slide-01..14.png`, `preview/T069-directed-morph.pdf` (14 pages),
  `preview/native_verify.json` (COM sequence and transitions).
- `preview/morph-pairs.png` — the four source/destination pairs.
- `artifacts/state-critic.json`, `artifacts/critic.json`.
- `beat-sheet.md` — 14 spoken beats, base states, images and Morph reasons.

## Positive results

1. **Four Morphs, four ideas.** Each pair shares 7–16 `!!` names; no background
   or thread is morphed. The Morph is the argument move, not an entrance.
2. **Base states do not wait for a click.** The cover has title + three faces;
   slide 3 has both answers; slide 5 has both worldviews; slide 8 has all three
   parts; slide 12 has the whole quotation; slide 14 has the whole summary.
3. **The timeline now argues.** Re-ordering the portraits to Engels 1848 →
   Marx 1867 → Lenin 1917 makes the three dots mean what they point at. The
   T066 defect (1848 under Marx, 1867 under Engels) is gone.
4. **The deck does more with less:** 9 clicks and 61 effects, down from 27/116;
   the extra effects are the dim lifecycles that keep the active view under the
   cap, not decoration.
   Four of the nine clicks are the two definition builds and the three
   conditions; everything else is a poster or a Morph.
5. **A critic that can say no.** `deck_state_critic.py` fails T066 on the exact
   defects the owner named and passes T069. It is the first gate in the lab that
   judges `t=0` and the per-click sequence rather than the final frame.

## Negative results and limits

1. **No Morph playback capture.** The Morph is verified by PowerPoint's
   transition object (3954, 1.2 s) and by the package XML, but no frame-by-frame
   video was captured. `preview/morph-pairs.png` shows the two stable endpoints;
   the interpolation between them is not visually verified. Rung 6 is not
   reached.
2. **The deck is 14 slides, not 10.** Four B states were added. That is the cost
   of state-pair Morphs; whether the extra advances feel right in a room is a
   human judgement.
3. **The B states were authored on the T067 copy, not compiled by
   `deck_director.py`.** T068 proves the compiler on three slides; T069 proves
   the state-pair craft on the real chapter. The two have not been joined into
   one pipeline run yet.
4. **Two build-first slides remain** (slide 2 definitions, slide 7 conditions).
   They open on a readable title + image/frame, not on a blank stage, but they
   still use 3–4 clicks.
5. **The critic needed T069b to see narrative.** T069a was measured with the
   design critic before the narrative dimension existed; after T069b the same
   deck scores **narrative 4.92**, overall **4.33**. Design 3.99 still trails
   T066's 4.03 because the critic weights per-slide checks. The state critic is
   the instrument that sees the improvement; the design score alone would not.
6. **`MOT-STATIC` warning** is expected: the deck intentionally has poster
   slides with no in-slide motion, because the change happens at the Morph.
7. **`deck_state_critic.py` is experimental** and not wired into
   `design_critic.py` or the build loop.

## Next

1. Capture a short PowerPoint `CreateVideo` excerpt (four pairs, 480p) and
   extract Morph frames, so the interpolation is evidence, not only the end
   states.
2. Run the four state pairs through `deck_director.py` as a `direction.json`
   scene plan; compare the compiled timing with this hand-built one.
3. Promote `deck_state_critic` into `slide_forge build` as a post-build gate
   after review.
4. Human review of the 9 clicks (rung 6) and a `liquid-glass` variant of the
   same content to test `VisualStyle/1` beyond specimens.

## Rung 6 owner review (2026-11-08)

The owner watched the four Morphs in PowerPoint and scored the motion **6/10**:
*"gu của motion này hơi bị đơn giản và quá gượng gạo kèm thêm bố cục sắp xếp
có phần hơi không ổn."*

This is the rung-6 result the report was missing, and it is negative. It does
not overturn the structural findings — the four pairs do share objects, the
base states are readable, `morph_studio audit` is clean — it says those
findings are not enough. Two causes, in the owner's order:

1. **Composition.** The B states were designed to demonstrate a state change,
   not to stand as posters. The design critic had already hinted at this:
   design 3.99 trails T066's 4.03. A Morph between two weak frames reads as two
   layouts swapping.
2. **Forced motion.** The cuts ask the audience to decode which shape became
   which. "Semantic" in the plan did not become "obvious" on screen.

Consequence: T067's "3–4 semantic Morphs" remains a hypothesis, but this deck
does not prove it at rung 6. The next attempt must pass the poster test on both
endpoints and the four forced-cut questions (T091) before a Morph is added.
Feedback: `research/feedback/2026-11-08-motion-grades.md` (F21).
