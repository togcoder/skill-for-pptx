# T034 evaluation results

## Same inputs, two generator versions, one critic

| Input / style | base: overall | base: generator warnings | T034: overall | T034: generator warnings | codes fixed |
|---|---|---|---|---|---|
| fixture:essay_outline_deck / modern | 4.37 | 1 | 4.37 | 1 |  |
| fixture:essay_outline_deck / cinematic | 4.54 | 0 | 4.54 | 0 |  |
| fixture:motion_showcase_deck / modern | 4.69 | 0 | 4.69 | 0 |  |
| fixture:motion_showcase_deck / cinematic | 4.68 | 0 | 4.69 | 0 |  |
| fixture:picture_deck / modern | 5.0 | 0 | 5.0 | 0 |  |
| fixture:picture_deck / cinematic | 5.0 | 0 | 5.0 | 0 |  |
| fixture:report_deck / modern | 4.81 | 0 | 4.84 | 0 |  |
| fixture:report_deck / cinematic | 4.81 | 0 | 4.84 | 0 |  |
| forge:midnight / modern | 4.83 | 0 | 4.83 | 0 |  |
| forge:midnight / cinematic | 4.8 | 1 | 4.81 | 1 |  |
| forge:office_facet / modern | 4.83 | 0 | 4.83 | 0 |  |
| forge:office_facet / cinematic | 4.8 | 1 | 4.81 | 1 |  |
| forge:paper / modern | 4.83 | 0 | 4.83 | 0 |  |
| forge:paper / cinematic | 4.8 | 1 | 4.81 | 1 |  |
| forge:seed_amber_light / modern | 4.83 | 0 | 4.83 | 0 |  |
| forge:seed_amber_light / cinematic | 4.76 | 5 | 4.81 | 1 | COL-GRAPHIC |
| forge:seed_red_dark / modern | 4.83 | 0 | 4.83 | 0 |  |
| forge:seed_red_dark / cinematic | 4.76 | 5 | 4.81 | 1 | COL-GRAPHIC |

Generator-controlled warnings in total: base 14, T034 6.

## Landscape (existing decks, current critic)

| Deck | design | motion | rhythm | coherence | overall | warnings (top codes) |
|---|---|---|---|---|---|---|
| fixture: report (raw) | 4.38 | 5.0 | 3.0 | 3.67 | 4.01 | 5 (COL-TEXT 3, MOT-STATIC 1, MOT-VOCAB 1) |
| fixture: showcase (raw) | 4.5 | – | 1.0 | 4.0 | 3.17 | 1 (MOT-STATIC 1) |
| T019 director output | 4.38 | 4.88 | 5.0 | 5.0 | 4.81 | 3 (COL-TEXT 3) |
| T022 Codex T009 candidate | 3.75 | 4.91 | 5.0 | 3.67 | 4.33 | 10 (DEN-WORDS 9, MOT-VOCAB 1) |
| T024 Argon complex showcase | 2.71 | 4.76 | 3.75 | 3.67 | 3.72 | 64 (COL-TEXT 38, MOT-EFFECTS 10, MOT-MOVERS 9, DEN-WORDS 2) |
| T025 Forge coffee (EN) | 5.0 | 4.95 | 4.91 | 3.67 | 4.63 | 3 (MOT-SETTLE 2, TYP-SIZES 1) |
| T025 Forge chuyển đổi số (VI) | 5.0 | 4.93 | 4.96 | 3.67 | 4.64 | 2 (MOT-SETTLE 1, TYP-SIZES 1) |
| T028 report pro | 4.32 | 4.92 | 4.95 | 5.0 | 4.8 | 6 (COL-TEXT 5, MOT-SETTLE 1) |
| T028 showcase pro | 5.0 | 4.97 | 4.9 | 4.33 | 4.8 | 1 (MOT-SETTLE 1) |

## Render calibration: PowerPoint 16.0 frames vs LibreOffice 24.2 (same deck)

| Slide | background share PPT / LO | balance PPT / LO | colourfulness PPT / LO |
|---|---|---|---|
| 1 | 0.514 / 0.514 | 0.205 / 0.195 | 35.0 / 35.5 |
| 2 | 0.91 / 0.876 | 0.105 / 0.117 | 17.6 / 18.1 |
| 3 | 0.926 / 0.89 | 0.047 / 0.062 | 24.7 / 35.5 |
| 4 | 0.847 / 0.812 | 0.096 / 0.097 | 52.5 / 53.5 |
| 5 | 0.924 / 0.91 | 0.125 / 0.127 | 35.9 / 41.8 |
| 6 | 0.655 / 0.654 | 0.166 / 0.138 | 30.3 / 29.5 |
| 7 | 0.935 / 0.913 | 0.087 / 0.062 | 33.1 / 33.0 |
| 8 | 0.91 / 0.88 | 0.177 / 0.1 | 18.3 / 21.7 |
| 9 | 0.946 / 0.933 | 0.108 / 0.119 | 14.9 / 16.3 |
| 10 | 0.958 / 0.935 | 0.004 / 0.03 | 15.4 / 15.3 |
