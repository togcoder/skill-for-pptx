# T067 [pptx] — Motion dramaturgy for the Chapter 1 deck

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), subagent of the owner's
  T067 session.
- **Date:** 2026-11-04. **Base:** `7d3d9b8`. **Branch:**
  `work/T067-opencode-deck-director`.
- **Request:** the owner rejected T066's motion as tasteless: portraits appear
  last with no meaning, decoration is visible before the claim, and the deck
  was built before a script existed. Produce a beat sheet, audit every click,
  and rewrite the motion on a copy.
- **Deliverable:** `motion/artifacts/T066-deck-directed.pptx`,
  `motion/beat-sheet.md`, `motion/motion-audit.md`, `motion/motion-plan.json`,
  `motion/evidence-sheet.png`, before/after state PNGs.
- **Status:** complete; review requested. No product path was changed.
- **Evidence rung:** **4** for the exact-file COM counts, **5** for the
  PowerPoint-rendered stable states. **Not 6** — no human reviewed every click.

Paths below are relative to `experiments/T067-20261104-opencode-deck-director/`
unless they start with `experiments/`.

## Frame

- **Question.** Can the deck's motion be re-directed from a beat sheet so that
  the title, claim and key image are readable at t=0, the entrance order is
  the reading order, images are never a meaningless finale, and at most two
  things move at once?
- **Hypothesis.** T066's problem is not “too little motion” but **no artifact
  for direction**: 51 clicks, 144 effects and nine global Morphs were added
  after layout, from the geometry. A written beat sheet, applied as a new
  timing tree, will make the same deck read as one argument.
- **Falsifiers.**
  - the base state is still unreadable on any slide;
  - a picture still appears on the last click;
  - a title still enters on a click;
  - more than two movers still fire together;
  - a Morph still has no object/idea continuity;
  - the deck cannot be opened/played by PowerPoint 16.
- **Domain lens.** PowerPoint-native: `p:timing` click groups, native
  `p:transition`, COM `View.Next()` stable states. A deck is presented, not
  played like a film; the presenter is the soundtrack.

## Frozen input

- **Source deck:** `experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx`
  — SHA-256 `f4478f0edc9829c664caac4a16aa4f7710ef57843b4493a7c3f46886d3ed244d`,
  2 016 432 bytes.
- **Content:** *Giáo trình Triết học Mác – Lênin*, Chương 1; quotation from
  C. Mác, *Luận cương về Phoiơbắc* (1845). The deck is a summary, not a
  verbatim copy.
- **Images:** Wikimedia Commons, Public Domain / CC0; cut-out, duotone and
  circular mask from T066 (`inputs/SOURCES.md`). The directed copy does not
  touch the pixels.
- **Environment:** Windows 11, PowerPoint **16.0 build 17932**, Python 3.13,
  python-pptx, lxml, Pillow, pywin32.
- **Not available:** a human review of every slide; a projector/room; a second
  PowerPoint build; a complete proofread against the printed textbook.

## Method

1. **Read the script source.** T066 has speaker notes but no script artifact.
   The notes were rewritten as the beat sheet's spoken lines with `[nhấp]`
   cues; every click now has a sentence.
2. **Audit the timing.** `measure_narrative.py` (base words, picture click,
   title animation, lifecycles); `workspace/T067/audit_timing.py` (per-click
   effects, peak movers, static decorations); `design_critic.py`.
3. **Direct.** Wrote `motion-plan.json`: 10 slides, 27 beats, one hero per
   slide, ≤2 movers, 0 Morph. The plan names every shape, role and duration.
4. **Apply.** `inputs/build_directed.py` reads the frozen T066 file, retires
   the `!!` naming convention, deletes the dead `dialectic-foot`, replaces the
   whole timing with `pptx_animator.apply_timeline(mode="replace")`, writes
   the notes, and replaces the nine Morph transitions with a 350 ms Fade.
5. **Read back.** `finalize_plan.py` measures the built file and records
   `base_visible`, per-beat effect count, peak movers and duration.
6. **Verify.** `motion/com_verify.py` opens the exact file in PowerPoint 16
   and reads slide/effect/transition counts. `motion/capture_states.py` drives
   `View.Next()` and captures the settled states; `motion/make_evidence_sheets.py`
   composes `evidence-sheet.png` and `slide4-states.png`.
7. **Grade.** `design_critic.py` on the output; the remaining warnings are
   reported, not hidden.

```powershell
python experiments/T067-20261104-opencode-deck-director/inputs/build_directed.py
python experiments/T067-20261104-opencode-deck-director/inputs/finalize_plan.py
python experiments/T067-20261104-opencode-deck-director/motion/com_verify.py
python experiments/T067-20261104-opencode-deck-director/motion/capture_states.py `
  experiments/T067-.../motion/artifacts/T066-deck-directed.pptx `
  experiments/T067-.../motion/after 4 3 s04
python scripts/design_critic.py `
  experiments/T067-.../motion/artifacts/T066-deck-directed.pptx `
  -o experiments/T067-.../motion/critic-after.json
python experiments/T067-20261104-opencode-deck-director/motion/make_evidence_sheets.py
```

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Exact file opens in PowerPoint 16 | COM: 10 slides, read-only, no repair; `Build 17932` | 4 |
| Effects reduced, not inflated | COM `TimeLine.MainSequence.Count`: **144 → 116** | 4 |
| Morph removed | COM `EntryEffect`: **9 × 3954 (1.5 s) → 0**; **9 × 3849 Fade (0.35 s)** | 4 |
| Base state readable on every slide | `measure_narrative.py`: empty base `[1,3,5] → []`; base words `0–7 → 7–28` | 5 |
| Title/claim at t=0 | titles with an entrance `[1,2,3,4,5,6,7,8,10] → []` | 5 |
| Images at t=0 | pictures on last click `4 → 0`; every picture first click `0` | 5 |
| ≤ 2 simultaneous movers | shape-level audit: before peak **4**; after peak **2** (slides 6 and 8 only) | 1 + 5 |
| Clicks reduced | `measure_narrative.py`: **51 → 27** (26 presenter + 1 auto) | 1 |
| Stable states rendered | `View.Next()` captures: 21 before/after state frames + 10 static finals | 5 |
| Design critic | overall **4.03 → 4.02**; motion **4.99 → 4.94**; rhythm **4.48 → 4.50** | 1–3 |
| Human review | **not reached** | — |

The critic's motion score is slightly lower because the deck is quieter. The
critic measures activity, not direction; the owner's eye is the gate.

## What changed

| Metric | T066 | Directed copy |
|---|---:|---:|
| Click groups | 51 | **27** (26 presenter + 1 auto ring build) |
| Effects | 144 | **116** |
| Morph transitions | 9 × 1.5 s | **0** |
| Fade transitions | 0 | **9 × 0.35 s** |
| Empty base slides | 3 (1, 3, 5) | **0** |
| Titles with an entrance | 9 of 10 | **0** |
| Pictures on the last click | 4 | **0** |
| Peak simultaneous movers | 4 | **2** |
| Object lifecycles | 0 | 0 (deliberate; see below) |
| `!!` names | 52 | **0** |
| `dialectic-foot` | revealed under an opaque card | **removed** |
| Speaker notes | prose, no cues | **beat-sheet lines with `[nhấp]`** |

### The three worst defects and the fix

1. **The base states were unreadable.** Slide 1 opened on three empty gold
   rings; slide 2 on a red disc; slide 4 on an arc and three dots with no
   title; slide 7 on empty rings and floating dates; slide 9 on an empty deep
   red field. **Fix:** title, kicker, key image and margin rule are static on
   every slide; the first click adds evidence, never the claim.
   Evidence: `motion/evidence-sheet.png`, `motion/before/s0*-00-base.png`.
2. **Images arrived as the finale.** Slide 1's three portraits appeared on the
   last of four clicks; slide 2's Plato appeared on the seventh of seven
   clicks and the notes never mention it. **Fix:** all portraits and Plato are
   on the base plate; the clicks name them (slide 1: 0 clicks; slide 2: the
   definitions build in front of a present image; slide 7: names/dates build
   under present faces). Evidence: `before/s01-04-click4.png`,
   `before/s02-07-click7.png`, `after/s01-00-base.png`,
   `after/s02-00-base.png`, `after/s07-00-base.png`.
3. **Quantity replaced direction.** 51 clicks and 144 effects, up to four
   movers at once, and nine 1.5 s Morphs whose only continuous objects were
   the background/thread. **Fix:** 27 beats, 116 effects, ≤2 movers, one hero
   per slide, 0 Morph, 350 ms Fade. The decoration is static and renamed; no
   `!!` convention is left.

### Morph audit: 0 of 9 kept

The detailed table is in `motion-audit.md` §2.4 and `beat-sheet.md` §12. The
short version: no adjacent pair shares an object or an idea that survives the
cut. The only continuous object was the gold thread, which was decoration and
is now a static margin rule. The T066 hypothesis — a global Morph thread would
carry the eye — is falsified by the owner's eye and by the frame audit. The
nine Morphs became nine 350 ms Fades.

## The directed motion in one line per slide

| # | Base at t=0 | Clicks | Hero |
|---:|---|---:|---|
| 1 | title, subtitle, three portraits | 0 (1 auto) | three rings draw |
| 2 | title, Plato | 3 | three underlines 01–02–03 |
| 3 | title | 3 | question mark lands between the two answers |
| 4 | title, dialectical diagram | 3 | straight line draws and stops |
| 5 | title, period | 4 | timeline draws to 1848 |
| 6 | title, structure | 2 | three-card wave, then two connectors |
| 7 | title, three portraits | 4 | timeline draws through 1848/1867/1917 |
| 8 | title | 2 | two paired rows close a 2×2 |
| 9 | full quotation | 1 | attribution rule + author |
| 10 | title, credits | 4 | closing line rises out of the list |

The full spoken lines, roles and durations are in `motion/beat-sheet.md`.

## Artefacts

| Path | What |
|---|---|
| `motion/artifacts/T066-deck-directed.pptx` | the directed deck; SHA-256 `00c34c4cc8968ca107e75d291ad11ad7ed7713aae62014565d2ca69d77131734`, 2 014 494 bytes |
| `motion/beat-sheet.md` | 10 slides, 27 beats, spoken lines, roles, durations, heroes |
| `motion/motion-audit.md` | before/after audit, 5 defect classes, 9-Morph table |
| `motion/motion-plan.json` | machine-readable plan + measured base/effects/movers |
| `motion/evidence-sheet.png` | five before/after base-state pairs |
| `motion/slide4-states.png` | slide 4: t=0, click 1, click 2, click 3 |
| `motion/before/`, `motion/after/` | PowerPoint stable-state PNGs and static finals |
| `motion/com-verify.json` | exact-file COM counts |
| `motion/critic-after.json` | design-critic verdict |
| `motion/capture_states.py` | reproducible COM state capture |
| `motion/com_verify.py` | reproducible COM verification |

## Negative results and limitations

1. **No human review.** Rung 5: PowerPoint opened, played and captured the
   exact file; no person watched every click in a room. The owner's eye test
   is still the next gate.
2. **The critic prefers the old deck by 0.01 overall** (4.03 → 4.02) and by
   0.05 on motion (4.99 → 4.94). It rewards activity and effect count; the
   directed deck is deliberately quieter. It also flags `MOT-STAGGER` on
   slides 2 and 7 (250 ms between three underlines / three dates). Those are
   ordinal sequences the presenter speaks, not a simultaneous group; we keep
   the 250 ms beat and report the warning instead of compressing it to 150 ms.
3. **Object lifecycles remain 0.** Every effect is an entrance; nothing is
   moved, dimmed or exited after it appears. A dim of slide 10's rows after the
   closing line was considered and rejected (it would hide the takeaways); a
   move of slide 4's line away from the circle was rejected (it would cross the
   title and imply a false equivalence). This is a real open question, not a
   hidden success.
4. **The `dialectic-foot` shape was deleted.** It was revealed at the same
   click as the opaque `dialectic-card` that covers it; the audience never saw
   it. Deleting it is a content removal, justified by the frame audit. The card
   text (“liên hệ, vận động, phát triển”) still differs from the notes (“liên
   hệ, vận động, mâu thuẫn”); that is a content proofread item, not motion.
5. **Capture artefacts.** The windowed captures include PowerPoint's title bar
   and scrollbar; the fullscreen slide-4 capture has the show toolbar on the
   *before* frame. The state PNGs were taken from the direction build; the
   final rebuild changed two effect durations (200 → 250 ms; the two
   connectors now start together) and the zip metadata, not any stable frame.
   Static finals were re-exported from the final hash.
6. **Type and density are unchanged.** 21 type sizes and 8–10 pt captions from
   T066 remain; the critic still flags `TYP-SIZES`, `TYP-SMALL`, `DEN-WORDS`.
   This task is motion, not typography.
7. **No audio, no 4:3 cut, no interactive triggers.** The deck is a linear
   click build.

## Next

1. **Human review on a projector.** Specifically: do the 250 ms three-beat
   sequences on slides 2 and 7 feel like “01–02–03”, or rushed?
2. **One real lifecycle test.** Add a dim of slide 10's rows after the closing
   line and a `release` back; measure whether the room loses the list.
3. **Type pass.** Six sizes, body ≥18 pt where possible, captions ≥10–12 pt;
   re-run the critic and the PDF.
4. **Content proofread.** Reconcile “phát triển” vs “mâu thuẫn” and check the
   chapter summary against the printed textbook.
5. **Optional:** a 4:3 classroom cut, a handout-only PDF, a voice-over.

## Review response

Pending. The first review should check the beat sheet against the spoken
argument and the room, not only the critic score. No product code changed; the
only code added is in this experiment's `inputs/` and `motion/`, and none of it
is imported by a product path.
