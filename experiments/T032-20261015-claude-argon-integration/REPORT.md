# T032 — Evaluating and integrating Argon's research drop (2026-10-15)

## Input

The owner sent `skill-for-pptx-T024-final.zip`, a full repository copy from
Argon (a Gemini research agent). Argon could not read GitHub, so it worked on
the old `main` (`bb82c70`, before T024–T031) and reused the ID T024; its
claim is `research/claims/T024-gemini-20261014.md` and its report is
`experiments/T024-20261014-gemini-complex-motion-rigging/REPORT.md`.

The drop was committed verbatim on `import/argon-t024-20261014` (base
`bb82c70`, so the authorship and diff stay visible) and three-way merged into
the latest line (T031).

## Verdict per finding

| Argon finding | Verdict | Notes |
|---|---|---|
| Virtual rigging (`detect_virtual_rigs`, `expand_rig_tracks`, `follow_through_ms`) | **Adopted** | Auto-detects multi-part widgets (card + icon + label + badge) and moves them together, with optional per-part lag. It complements the cloud `attach`. It is on by default (`rigging: false` opts out); all 265 tests and 48/48 repository decks pass. |
| `orbit`, `orbit-3d`, `wave`, `explode-layers`, `cascade-flow` recipes | **Adopted** | PowerPoint 16.0 renders the 3D carousel (depth scale + dimming) and the packet cascade; see the PNGs here. |
| Multi-segment `animMotion` (`poly_path`, `via`) | **Adopted** | One path element instead of chained paths; coexists with cloud overshoot/anticipate. |
| Auto-arc collision avoidance (`auto_avoid`, `transient_warnings`) | **Adopted** | Opt-in. Mid-flight collision warnings now appear in apply reports. |
| `bounce_end` (`p14:bounceEnd`) | **Adopted** | PowerPoint's own "Bounce end" timing option. |
| Shape-click triggers (`interactiveSeq`, `trigger_spid`) | **Adopted, unverified natively** | CreateVideo cannot click a shape. Needs an interactive slideshow check. |
| Spotlight no longer snaps other objects home | **Adopted** (bug fix) | Combined with the cloud halo. |
| Anchor keyframe timestamp fix | **Adopted** (bug fix) | |
| `color` emphasis | **Adopted, corrected** | Argon wrote presetID 7 (= Change *Line* Color). It is now 1/2 = Change Fill Color, per the PowerPoint-harvested library (T027). |
| `teeter` emphasis | **Adopted, corrected** | Argon wrote presetID 14 (= Blast). It now uses PowerPoint's own Teeter template (32), and the reader is fixed. |
| `repeat`/`auto_reverse` top-level keys | **Translated** | This is the third loop representation in the repo. It is normalised into the single `loop: {repeat, auto_reverse}` model where effects are created. |
| Pillow-only GIF/storyboard fallback, `check_environment` fix | **Adopted** | Previews no longer need ImageMagick. |
| "PHASE 2-4" block: Morph homotopy, cognitive motion budget, cross-slide Morph twin staging | **Quarantined** | It broke `import motion_engine` (`NameError: SLIDE_W`; also undefined `ET`, `A`, `NS`, `extract_objects`), was never called and had no tests. The drop's "199 tests OK" predates it: the shipped tree fails 4 tests. It moved to `scripts/morph_playbook.py` with imports fixed and is marked experimental; `stage_cross_slide_morph_twins` still needs an `extract_objects` that does not exist. Cloud T028 Morph Studio already covers off-slide staging and camera scenes. |
| `cross-slide-morph-and-pacing.md` (6 Morph playbook techniques) | **Kept as reference** | It overlaps T028 `pro-techniques.md`. |

## Evidence

- `PYTHONUTF8=1 python -m unittest discover -s tests`: 265 tests, OK (4 skipped).
- Forge examples build with QA ok. Director `cinematic` draft+apply on 48/48 repository decks.
- Argon's showcase was rebuilt with the merged code and rendered by PowerPoint 16.0 build 17932. Effects parsed per slide: 89 / 356 / 68 / 14 / 27 (`argon_showcase_native_sequence.json`).

## Open

- Interactive slideshow check of shape triggers.
- A decision on the quarantined Morph playbook (finish it or drop it, given T028).
- The source showcase has a title/subtitle overlap on slide 1 (Argon's fixture).
