# Environment: what runs where

Run `python3 scripts/check_environment.py` from the repository root. It
reports what is present; it installs nothing and verifies no playback.

| Work | Needs | Notes |
|---|---|---|
| Director, Morph Studio, design system, critic (structure), tests | Python 3.10+, `lxml` | Tested with Python 3.11.15 and lxml 6.1.3 (cloud), and Python 3.12 (desktop) |
| Slide Forge build/QA, fixtures | + `python-pptx`, `Pillow` | Forge measures text with Pillow fonts. On Windows set `PYTHONUTF8=1` |
| Forge online assets | Network to Openverse/Iconify. `PEXELS_API_KEY` (optional) | Without network Forge uses generated art |
| Previews, storyboards, LibreOffice cross-check, `design_critic --render lo` | LibreOffice **Impress** (`libreoffice-impress`; `libreoffice-core` cannot open PPTX), poppler (`pdftoppm`) | ImageMagick `montage`/`convert` are optional; there is a Pillow fallback (T032). Tested with LibreOffice 24.2.7.2 |
| PowerPoint-parsed and -rendered evidence (rungs 4–5) | Windows, desktop PowerPoint (tested 16.0 build 17932), PowerShell | `scripts/powerpoint_render.ps1`, `slide_forge.py render` |
| Interactive playback (rung 6) | Same, plus a person or a COM click driver | `docs/POWERPOINT_NATIVE_HARNESS.md` |
| Knowledge-base rebuild | Windows + Office for presets and design kits; network for the Zenodo10K scan | See `knowledge/README.md`. Source decks stay in git-ignored `local-media/` |
| ISO 29500 schema check | `pml.xsd` from ISO/IEC 29500-4 (`design_critic.py --xsd`, or `PPTX_PML_XSD`) | Not shipped in the repository |

```bash
python3 -m venv .venv && . .venv/bin/activate
python -m pip install lxml python-pptx Pillow
python -m unittest discover -s tests          # 289 tests at T034
```

Cloud sessions (Claude Code on the web) have Python, LibreOffice and poppler,
but no PowerPoint. Their network policy may block academic hosts, so record
what you could not read.

The E001-era builder ran in the ChatGPT Work runtime (`CODEX_PRIMARY_RUNTIME_*`,
artifact-tool). It is frozen; see `docs/archive/` and the E001–E004 reports.
