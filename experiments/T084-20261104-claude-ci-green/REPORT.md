# T084 [cross] Green CI: test deps, host-only and network tests, logo box fit

- **Agent / model:** Claude (Opus 5.5), lead. **Date:** 2026-11-04.
- **Branch:** `work/T084-claude-ci-green`.
- **Why:** `main` had been red on both runners since before T070. The T083 coordination
  checks run in CI, so a red CI hid every real signal.

## Causes and fixes

| Failure (runner) | Cause | Fix |
|---|---|---|
| 7 test modules fail to import (both) | `tests.yml` installed only lxml, python-pptx and Pillow | install `python-docx openpyxl numpy pytest` too |
| `test_compile_one_slide_games_suite` (both) | builds the deck through PowerPoint COM | skip when `win32com` is missing; still runs on the owner's machine |
| `test_cli_binaries_discovery` (both) | expects ArtCraft CLIs installed on the host | skip when they are not found |
| `TypeScaleTests` setup (windows) | `coffee_report_photos.json` searches Openverse online and hit an HTTP error | skip that one example on `URLError`; the other examples still run |
| `test_chrome_injection_progress_bar_and_logo` (ubuntu) | the logo box was a fixed 1.3 in; with the wider Linux fallback font, "ARTCRAFT" did not fit (`WORD_BREAK`) | **product fix:** `slide_forge` sizes the logo box from the measured text, at least 1.3 in |

The logo fix is the only change to product code. With the measured width 30 % wider (to
simulate the fallback font) the chrome test still passes; before the fix that test failed on
ubuntu.

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| Full suite passes locally | `python -m unittest discover -s tests`: 564 tests, OK, 10 skipped | 1 |
| Layout and coordination checks pass | `python lab/tools/check_layout.py`: layout OK | 1 |
| CI green on both runners | see the PR checks | 1 |
