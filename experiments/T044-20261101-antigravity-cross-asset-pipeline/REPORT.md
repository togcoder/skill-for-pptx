# T044 [cross] — Cross-Asset Pipeline Protocol, User Experience Maximization & Local Autonomy Charter

## Frame
- **Question:** How can agentic AI skills transcend isolated, single-resource generation to orchestrate cross-asset pre-processing pipelines, deeply fulfill human intent on the first pass ("đúng ý ngay từ lượt đầu"), and exercise local operational autonomy cleanly?
- **Hypothesis (and what would falsify it):** Codifying an official cross-asset pipeline protocol (`Protocol 04`), updating `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, and `README.md`, and providing an executable pre-processing validator (`scripts/cross_pipeline.py`) will guarantee that:
  1. Component assets are audited and polished via domain-specialized tools (image cropping/alpha masking, audio EBU R128 loudness mastering, spreadsheet data audit) before compound assembly.
  2. Deliverables are customized dynamically to user context rather than confined to rigid presets.
  3. Agents operating locally have full freedom to download fonts, models, and libraries, keeping workspaces clean.
  Falsified if raw assets fail resolution/audio thresholds, if protocol files are missing, or if `check_layout.py` fails.
- **Domain lens (native canon and sources used):**
  - Official Project Owner Directive (2026-11-01)
  - `domains/cross/DOMAIN.md`
  - EBU R128 (-14.0 LUFS, True Peak <= -1.0 dBTP) & ITU BS.1770-4 Audio Mastering
  - Edward Tufte Data-Ink & Cognitive Load Principles (Miller 7+-2)
  - WCAG 2.1 AA/AAA Relative Luminance & Contrast
- **Transfers from other domains (and how they are tested):**
  - Audio EBU R128 canon (T042 / SoundCraft) transferred into general cross-asset audio validation (`validate_audio_for_muxing`). Tested in `tests/test_cross_pipeline.py`.
  - PhotoCraft / Pillow image alpha analysis (T043) transferred into general cross-asset image validation (`validate_image_for_embedding`). Tested in `tests/test_cross_pipeline.py`.

## Frozen input
- Request / date: Official Project Owner Directive regarding cross-domain skill development, first-pass user intent fulfillment, and local resource autonomy (2026-11-01).
- Base commit: `0026dcef6b53665ca20470bf2c2965796f824266`
- Environment: Windows 11, Python 3.12, Pillow.

## Method
Commands to reproduce:
```powershell
$env:PYTHONUTF8=1
cd skill-for-pptx
python -m unittest tests/test_cross_pipeline.py -v
python -m unittest discover -s tests
python lab/tools/check_layout.py
```

## Evidence
| Claim | Rung (0–6) | Evidence (path, hash, output) |
|---|---|---|
| Protocol 04 Codification | Rung 0 | `lab/protocols/04_cross_asset_pipeline.md`: Defines 3 canonical pre-processing pipelines (Image, Audio, Chart) and local autonomy laws |
| Overarching Law Amendments | Rung 0 | `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, `README.md`, `domains/cross/DOMAIN.md` updated with official owner mandate |
| Image Pre-Processing Validator | Rung 0 | `scripts/cross_pipeline.py::validate_image_for_embedding`: Verifies 16:9/4:5 aspect ratio, resolution, alpha channel for art washes, and canvas mode luminance harmony |
| Broadcast Audio Mastering Validator | Rung 0 | `scripts/cross_pipeline.py::validate_audio_for_muxing`: Verifies EBU R128 (-14 LUFS), True Peak <= -1.0 dBTP ceiling, and BGM ducking |
| Chart Data Density Validator | Rung 0 | `scripts/cross_pipeline.py::validate_chart_data_for_presentation`: Verifies zero-error data integrity (no NaNs/nulls) and Miller cognitive load limit |
| Unit Test Suite Pass Rate | Rung 0 | `tests/test_cross_pipeline.py`: 5 tests pass; full lab test suite passes 359 tests 100% |
| Layout Conformance | Rung 0 | `lab/tools/check_layout.py` reports `layout OK` |

## Negative results and limitations
- While programmatic validators catch technical violations (aspect ratio, alpha channel, loudness, data integrity), ultimate aesthetic judgment still requires human or multi-agent red-team review (`lab/protocols/03`).
- Audio validation currently inspects extracted loudness and peak metrics; direct waveform analysis requires `ffmpeg` or `pydub` installed on the host.

## Next
- Synchronize with OpenCode (`work/T042-opencode-advanced-docx`, `work/T043-opencode-advanced-xlsx`) to utilize `validate_chart_data_for_presentation` and `validate_image_for_embedding` in Word and Excel document generation.
- Integrate `scripts/cross_pipeline.py` into Slide Forge (`scripts/slide_forge.py`) to pre-audit images before PPTX insertion.

## Review response
| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| (Pending peer review from OpenCode / Claude) | review requested |
