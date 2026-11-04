# Sources and licences — T067 visual style specimens

## Content

- The claim “Không chỉ giải thích. Mà cải tạo thế giới.” paraphrases C. Mác,
  *Luận cương về Phoiơbắc* (1845), eleventh thesis. The two facts (1845; 11
  theses) are the standard bibliographic facts of that text.
- The specimen is a style calibration plate, not a lesson: it repeats the same
  content five times on purpose.

## Image

| File | Source | Licence | Changes |
|---|---|---|---|
| `inputs/assets/marx-*.png` | [Karl Marx 001.jpg](https://commons.wikimedia.org/wiki/File:Karl_Marx_001.jpg), Wikimedia Commons (photograph, 1875) | Public domain | background removed (`rembg` U2Net), cropped, duotone/posterized/grayscale, masked (circle / rounded / blob / rect), clay rim baked into alpha |

The raw download stays in the git-ignored `workspace/`; only the five treated
PNGs (58–183 KB each) are embedded. The treatments are design choices, not
claims about the original photograph. The photograph is used as a historical
portrait, not as an endorsement.

## Fonts

All fonts are installed Windows system fonts; none is redistributed.

| Style | Display | Body / label |
|---|---|---|
| editorial-crimson | Palatino Linotype | Arial |
| liquid-glass | Segoe UI Light | Segoe UI / Segoe UI Semibold |
| clay-cartoon | Segoe UI Black | Segoe UI Semibold / Segoe UI |
| swiss-minimal | Arial Bold | Arial |
| maximalist-collage | Arial Bold | Arial |

Vietnamese coverage was checked with fontTools against every non-ASCII
character used in the deck (claim, labels, caption): **0 missing glyphs** in
`pala.ttf`, `arial.ttf`, `segoeui.ttf`, `segoeuil.ttf`, `seguisb.ttf` and
`seguibl.ttf`. Arial Black, Georgia, Trebuchet MS, Franklin Gothic and Arial
Rounded MT Bold were rejected earlier: their Windows versions miss Vietnamese
precomposed characters.

## Tools

| Tool | Version | Licence / note |
|---|---|---|
| Microsoft PowerPoint | 16.0 build 17932 | COM render, PDF export, effect/timing read-back |
| python-pptx | 1.0.2 | MIT |
| Pillow | 13.0.0 | HPND |
| lxml | bundled with python-pptx | BSD |
| rembg | 2.0.86 | MIT; U2Net model (Apache-2.0) |
| fontTools | installed | MIT |
| pypdf | 6.13.0 | BSD |
| DeckCraft CLI | 0.15.0, `D:\artcraft\DeckCraft\deckcraft-cli.exe` | MIT/Apache (ArtCraft); used only as an effects writer |
| `scripts/pptx_animator.py` | lab code, T061 | native `p:timing` writer |

## Design references

- `knowledge/design_system.json` v1.1.0 (type bands, motion bands, contrast
  thresholds, density).
- `docs/DESIGN_SYSTEM.md`, `domains/pptx/DOMAIN.md`.
- T066 `experiments/T066-20261104-opencode-triet-hoc-ch1/` — the editorial
  language (read only; not modified).
- T059 report — DeckCraft is not a safe last writer for timing.
- T064 / T028 — Morph identity and settle rules (tokens only; not exercised in
  the specimen).

No template, theme file or stock asset was used. The deck is built from a blank
16:9 presentation with a blank layout.
