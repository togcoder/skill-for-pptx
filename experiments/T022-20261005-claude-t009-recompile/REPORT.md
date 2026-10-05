# T022 — Recompile Codex's T009 no-script run through T019, fix text-deck direction

## Frozen input

- Continues Codex's T009 arm C (PR #22, branch `work/T009-codex-no-script-20261005`,
  unmerged by its own review). That review named the next step: repair the
  evidence and recompile through T019 before any native test.
- Does not touch Codex's in-progress T021 (draft PR #24) or the T009 branch.
- Base commit: `base-commit.txt` (main after PR #23). Claude Code cloud session.
- Hypotheses:
  1. Codex's narrative plan survives recompilation through the canonical
     writer unchanged, and the independent importer then reads its staged
     reveals as a sequence (it read the T009 candidate as concurrent).
  2. Codex scored motion meaningfulness 3/5 because dense two-paragraph bodies
     were one shape. T019 paragraph builds can split them into separate presenter
     clicks without editing content.
  3. The T019 autonomous draft generalises to a deck made only of text boxes.
     (It did not. See Failures.)

## Reproduction

Environment: Python 3.11.15, lxml 6.1.3, Pillow 12.3.0, LibreOffice 24.2.7.2
Impress, poppler `pdftoppm`. No PowerPoint.

Source reconstruction: the owner's original T009 source PPTX is not in the
repository. The T009 candidate (`6e18e4f2…1e727`) was rebuilt with every
`p:timing` removed from its 10 slide parts (10 removed). The reconstruction
matches Codex's `source-inventory.json` with 0 differences in id, name, text,
geometry or kind over 31 shapes, and has no timing. It still carries Codex's
stale-content-type repair, so its hash (`b9f4c97a…820d`) differs from the
original source (`6fe3cf60…8465`).

| Arm | Plan | Clicks | Effects | Output SHA-256 |
|---|---|---|---|---|
| T009 candidate | Codex v0.4, old patch writer | 12 | 21 | `6e18e4f2…1e727` |
| R1 | Codex v0.4 plan, source hash only changed | 12 | 21 | `d9a40a87…38d5` (committed in `output/`) |
| R2 | R1 + paragraph clicks on slides 3–9 (`r2-director.json`) | 19 | 28 | `f4247386…2af7` |
| auto (T019 heuristic) | `motion_director draft`, goal = T009 instruction | 40 | — | `9e5b3ff5…50a3` |
| auto2 (T022 heuristic) | same command after the fixes below | 18 | 25 | `f72011cc…2261` (committed in `output/`) |

Full hashes are in `hashes.txt`. Commands:

```bash
python3 scripts/motion_director.py draft SOURCE.pptx -o auto2-director.json \
  --goal "Làm bài thuyết trình này rõ ràng, mạch lạc và có chuyển động chuyên nghiệp."
python3 scripts/motion_director.py apply SOURCE.pptx PLAN.json -o OUT.pptx
python3 scripts/render_identity.py SOURCE.pptx OUT.pptx --json render-identity-*.json
python3 scripts/lo_timing_crosscheck.py OUT.pptx --output lo-crosscheck-*.json
```

## Evidence

### Hypothesis 1: same plan, read as a sequence

Data from LibreOffice's PPTX importer (`lo-crosscheck-*.json`):

| Deck | effects | preset recognised | visibility set | slide 2 block begins |
|---|---|---|---|---|
| T009 candidate | 21 | 0 | 0 | 0s, 0s, 0s, 0s |
| R1 | 21 | 21 | 21 | 0s, 0.32s, 0s, 0.32s |

On every arm, preservation checks passed. Slide count was 10/10, all 31 source
objects kept their text and geometry, and only the slide XML parts changed.

### Static render, RGB-aware

`scripts/render_identity.py` renders through LibreOffice to PDF and PNG, then
compares in RGB. A negative control shows the earlier T009 method missing a
real change: `ImageChops.difference(rgba_a, rgba_b).getbbox()` returns `None`
for a one-pixel colour change, because Pillow's RGBA getbbox looks at alpha
only. The RGB tool reports `((5,5,6,6), 1)` for the same pair (also covered by a
unit test).

Results: R1, R2 and auto2 are each 10/10 identical to the reconstructed source.
The T009 candidate is also 10/10 identical to it. This only shows that timing
did not alter layout relative to the reconstruction. The original claim, which
compared the candidate with the original source, cannot be re-run here because
the original source is not available.

### Hypothesis 2: paragraph clicks

In R2, slides 3–9 get one click per body paragraph, which adds 7 clicks. Slide 7
shows the effect most clearly. Click 1 shows the opposing view ("Mặc dù hậu quả
đã rõ ràng… vẫn tồn tại…"). Click 2 shows the rebuttal ("Tuy nhiên, quan điểm
ấy hoàn toàn sai lầm…"). The rebuttal no longer appears before it is argued.
Text and geometry are unchanged. This is the limitation Codex recorded when it
rated the run 3/5. No new subjective score is assigned.

## Failures and decision

The T019 heuristic draft failed on this deck. It produced 40 clicks against
Codex's 12, from three defects:

1. Slides built from text boxes have no title placeholder. Every slide title
   was therefore animated (10 needless clicks).
2. A title wrapped across two paragraphs ("TÌNH TRẠNG THIẾU NGUỒN" /
   "NƯỚC SẠCH HIỆN NAY") was split into two bullet clicks.
3. Labels such as "Cách 1: …" were revealed one click before their own paragraph.

Fixes in `scripts/motion_director.py`:

- implicit title: the topmost short text in the top 20% of the slide stays static;
- title-zone subheadings stay static;
- a text-only first slide stays static;
- short wrapped headings are never treated as bullets;
- a label is paired with the larger text block directly below it, and they
  reveal in one click (label first, then the first paragraph); later paragraphs
  of that block each get their own click.

A first version had no geometry tolerance and missed a label sitting exactly
on its body's edge in the synthetic fixture. A -0.02 slide-height tolerance
fixed it. The draft for the T009 deck was unchanged by this fix (verified
byte-identical).

Result for auto2: 18 clicks. It agrees with Codex's grouping on slides 2 and 10
(label + text per alternative, two clicks each, slide-10 subheading static) and
on the first click of slides 3, 8 and 9. It splits dense paragraphs like R2.
The one remaining disagreement is slide 1: Codex animates the title slide in
one click, while the heuristic keeps it static per the skill rule. This is a
design difference, not a defect.

Regression fixture: `tests/fixtures/essay_outline_deck.pptx` (synthetic
Vietnamese content with the same structure, built by
`scripts/make_essay_fixture.py`). New tests are in
`tests/test_text_deck_director.py`. The full suite now has **176 tests**, all
passing; the T019 report-deck expectations are unchanged.

## Reusable lesson and handoff

- A deck made of text boxes needs inferred titles and label–body pairing.
  Placeholder types are not enough.
- Compare renders in RGB, never with `getbbox()` on RGBA images.
- For a native test, play `output/T022_r1_codex_plan_canonical.pptx` (Codex's
  narrative) and `output/T022_auto2_heuristic_canonical.pptx` in PowerPoint
  with `docs/POWERPOINT_NATIVE_HARNESS.md`. They are the T009 deck's first
  candidates without the concurrent-stage defect.
- Arms A and B of T009 are still pending. Native playback is still null.
- The output PPTX files contain the owner's own deck content. They are
  committed under the same private-repo precedent as the T009 candidate.
