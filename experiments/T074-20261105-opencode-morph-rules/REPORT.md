# T074 [pptx] — Morph matching rules, verified by experiment matrix

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max).
- **Date:** 2026-11-05. **Base:** `main` @ `bbdc3a3`. **Branch:**
  `work/T074-opencode-morph-rules`.
- **Capability:** `pptx.morph` (extended the canonical Morph understanding; no
  new script).
- **Status:** first pass, review requested. D001 applies: these are measured
  mechanics, not the owner's A/B judgement of whether a Morph is *good*.

## Frame

**Question.** PowerPoint Morph is "hard" because the object identity between two
slides is invisible in the file. Which properties make two objects one, and
which make a cross-fade?

**Hypothesis.** A 15-pair matrix of two-slide cases, rendered by PowerPoint, can
separate the rules that matter to a deck builder: name, shape type, text,
picture, group, rotation, entrance conflict, off-slide destination, z-order and
the `byWord`/`byChar` options.

**Falsifier.** If the frame tracker cannot tell one continuous object from a
cross-fade, the matrix is not evidence. The tracker was validated on the
`same-bang` positive and the `rect-ellipse` negative before the other cases were
read.

## Frozen input

- **Matrix deck:** `artifacts/morph-matrix.pptx` — 15 cases × (A, B, separator)
  = 45 slides, 16:9, synthetic shapes only.
- **PowerPoint:** 16.0 build 17932; `CreateVideo` 720p, 30 fps, 2 s/slide,
  1.2 s Morph; 109.395 s video.
- **Tracker:** colour per case; mid-frame blob count and centre at 320×180,
  then a full-resolution frame for the contact sheet.
- **Environment:** Windows 11, Python 3.13, python-pptx, lxml, Pillow, numpy,
  ffmpeg 8.1.1, pywin32.

## Method

1. `inputs/build_matrix.py` builds the 45-slide deck; each B slide carries
   `p159:morph` (1.2 s) and a separator follows on a cut.
2. `inputs/create_video.py` asks PowerPoint itself to render the deck. COM
   reports 15 Morph slides (EntryEffect 3954; `byWord`/`byChar` report 3955/3956).
3. `inputs/analyze_scan.py` scans the video at 10 fps, follows each case colour
   from A through the transition, and reports the mid-frame blob count/centre.
   Fixed per-slide timestamps were rejected: Morph adds 1.2 s per slide, so the
   video is 109.4 s, not 90 s (rule M-11).
4. `inputs/finalize_matrix.py` writes the final verdicts and the 11-rule
   proposal; the full-resolution mid frames are in `preview/states/`.

## Evidence

| Case | Setup | Mid-frame verdict | Rung |
|---|---|---|---|
| `same-bang` | same `!!track`, rect → rect | continuous, one blob at x≈164 px between 60 and 252 | 5 |
| `same-name` | same plain name, rect | continuous | 5 |
| `diff-name` | different names, same rect | continuous (name is not required) | 5 |
| `rect-ellipse` | same `!!track`, rect → ellipse | **two blobs**, cross-fade | 5 |
| `text-same` | same text box, moved | continuous | 5 |
| `text-diff` | different text, moved | continuous; content not measured | 5 |
| `picture-same` | same picture, moved | continuous | 5 |
| `picture-diff` | different media | **not measured** (colour changes; tracker loses it) | 1 |
| `group-same` | group moved | continuous | 5 |
| `rotate90` | 90° rotation | continuous | 5 |
| `entrance` | destination has Fade entrance | static; destination never appears | 5 |
| `byword` | Morph byWord | geometry continuous; glyphs not verified | 3 |
| `bychar` | Morph byChar | geometry continuous; glyphs not verified | 3 |
| `zorder` | foreground covers the actor | continuous but 11 visible px | 4 |
| `offslide` | B at x=14.5 in | empty B frame; no staging | 5 |

The 11 rules and the do/don't sheet are in `morph-rules.md`; the machine-readable
version is `artifacts/matrix-final.json` (`rules` + `cases`).

**The headline rule is M-02:** `!!` is a name hint, not a type override. A
rectangle with `!!track` and an ellipse with `!!track` still cross-fade into two
blobs. That is why T069a kept the same two cards and morphed their geometry,
rather than changing a card into a circle.

**The rule became an audit.** `scripts/morph_studio.py audit DECK.pptx` reports
`MORPH-TYPE-MISMATCH`, `MORPH-ENTRANCE`, `MORPH-OFFSLIDE` and
`MORPH-UNNAMED-PAIR` on every Morph pair. On the matrix it finds exactly the
three planted errors (slides 10→11, 31→32, 43→44); on T069a it is clean. The
audit is structural (rung 4), not a playback substitute.

**M-07 confirms T067:** an entrance effect on the destination actor blocks the
Morph completely. **M-08** says an off-slide B object is absent, not staged; a
fly-in must be authored, not assumed.

## Checks

- Full suite: **566 pass, 10 skipped** (includes `tests/test_morph_audit.py`).
- `python scripts/morph_studio.py audit morph-matrix.pptx` → exactly the three
  planted errors: `MORPH-TYPE-MISMATCH` 10→11, `MORPH-ENTRANCE` 31→32,
  `MORPH-OFFSLIDE` 43→44.
- The same audit on T069a → **0 errors**.
- `lab/tools/check_layout.py`: OK; `coord.py check`: OK.

## Negative results and limits

1. **15 of the 30 planned cells.** Charts, tables, SmartArt, 3D, connectors,
   gradient changes, flips, >180° rotation, ungrouping and different picture
   media are not measured. The report does not claim them.
2. **`picture-diff` is not measured.** The tracker follows colour; changing the
   media changes the colour, so the case cannot be classified by this method.
   It stays open.
3. **Text content is not measured word-by-word.** The frame tracker sees the
   text box as a moving blob; `byWord`/`byChar` glyph interpolation is rung 3.
4. **One video, synthetic shapes.** No human watched the 15 transitions
   (rung 6). The owner's eye remains the quality measure (D001).
5. **The product file is a proposal.** `knowledge/morph_rules.json` is not
   created because data entering `knowledge/` needs an accepted review. The
   proposal lives in this experiment and is ready to move after review.
6. **The audit is structural.** `morph_studio.py audit` catches the three
   high-risk cases, but `MORPH-UNNAMED-PAIR` is a heuristic; it can miss a pair
   that PowerPoint makes by a rule not in the matrix. The rendered video remains
   the rung-5 check.

## Rung 6: the owner watched T069a (2026-11-08)

The owner scored T069a's motion **6/10**: *"hơi bị đơn giản và quá gượng gạo"*,
with the composition also named. T069a passes this audit with **0 findings**.
So the matrix rules are necessary but not sufficient: they predict whether
PowerPoint will interpolate, not whether the cut reads as one idea. No rule in
the 11 was contradicted; the missing dimension is composition and intent, which
the audit cannot measure. The rulebook now carries that limit explicitly
(`morph-rules.md`, "What the audit cannot see"). T091 records the grade and the
human tests.

## Files

- `artifacts/morph-matrix.pptx` — 45-slide matrix deck.
- `artifacts/matrix.json` — raw tracker output.
- `artifacts/matrix-final.json` — final verdicts + 11 rules.
- `preview/morph-matrix.mp4` — PowerPoint video (git-ignored; local evidence).
- `preview/morph-matrix-evidence.png` — 15 mid-frames with verdicts.
- `preview/states/*.png` — full-resolution evidence frames.
- `inputs/build_matrix.py`, `create_video.py`, `analyze_scan.py`,
  `finalize_matrix.py`.
- `artifacts/matrix-audit.json`, `artifacts/t069a-audit.json`,
  `scripts/morph_studio.py audit`, `tests/test_morph_audit.py`.
- `morph-rules.md` — human do/don't sheet.

## Next

1. Add the remaining 15 cells: chart, table, SmartArt, 3D shared part, connector,
   gradient, flip, >180°, ungroup, different picture media.
2. Turn the 11 rules into a structural test in `morph_studio`/T075; fail a build
   when a `!!` object changes shape type or carries an entrance.
3. Run the rule sheet past the owner/lead and move the accepted subset to
   `knowledge/morph_rules.json`.
