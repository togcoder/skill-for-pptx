# Native PowerPoint QA harness

Status: automated record checks tested. PowerPoint COM playback has not been run
in this project environment. This harness does not close the M1 playback gate.

## Entry points

- `make_powerpoint_qa_manifest.py`: freeze the exact PPTX SHA-256 and structural
  target/click expectations.
- `build_powerpoint_qa_fixture.py`: optional composite fixture using chart/KPI
  on slide 1 (two clicks) and focus on slide 2 (one click).
- `powerpoint_native_probe.ps1`: collect application, MainSequence, click API
  observations and optional screen captures on Windows with desktop PowerPoint.
- `verify_powerpoint_qa.py`: check record consistency and completeness.

Use a dedicated Windows desktop session with no other decks open. The probe
closes its presentation and calls PowerPoint Quit during cleanup. Screenshots
capture the primary display, so put the slideshow there and keep that display
clear of unrelated content. Do not install a runner or buy PowerPoint as a side
effect of running research.

## Run against an existing exact artifact

From the repository root, with Python and lxml available:

```powershell
python scripts/make_powerpoint_qa_manifest.py output/T006_motion_semantics_local_remove.pptx --output build/local-remove-manifest.json
& scripts/powerpoint_native_probe.ps1 -Pptx output/T006_motion_semantics_local_remove.pptx -Manifest build/local-remove-manifest.json -Output build/local-remove-evidence.json -RunSlideshow -CaptureScreenshots
python scripts/verify_powerpoint_qa.py build/local-remove-manifest.json build/local-remove-evidence.json --output build/local-remove-verification.json
```

Create the build directory first. Repeat for all four frozen T006 matrix files;
do not choose a winner from only one file. Do not resave before recording its
original hash. Keep video/manual observations of A/B/C positions with the
existing matrix checklist.

For the composite chart/counter/focus fixture, use fresh output names:

```powershell
python scripts/build_powerpoint_qa_fixture.py --output build/T018_fixture.pptx --manifest build/T018_manifest.json
```

The generated package is a diagnostic candidate. Apply the host Presentations
finalization/render workflow before distributing it as a presentation. If
finalization changes bytes, regenerate the manifest for the finalized file.

The manual `powerpoint-native-qa` workflow requires an already configured
self-hosted Windows runner labelled `powerpoint` with an interactive desktop.
Its existence does not establish that such a runner is connected. No native
workflow was dispatched during the evidence-integrity study.

## Interpretation

| Result | Meaning |
|---|---|
| Native parse verified | Recorded exact hash, named PowerPoint version, slide count and expected MainSequence targets pass checks |
| Native click index progression verified | Every expected click was recorded once, in order, with consistent before/after indices and a successful error-free probe |
| Animation completion verified | Always false here; click index does not establish completion |
| Visual state / playback verified | Always false here; requires actual capture review and the full POWERPOINT_QA checklist |

`native_click_execution_verified` is a retained compatibility alias for the
click-index claim, not a claim that effects reached the correct final geometry.
Raw PowerShell `claim_boundary` values remain false until the independent Python
verification. Its `observations` are provisional operational results only.

The verifier checks supplied JSON, not authenticity. Fabricated JSON can imitate
COM output. Synthetic tests in this repository must never be presented as native
PowerPoint evidence. `visual_capture_count` counts references only, not existing
or reviewed image files.

`ClickPauseMs` controls when a screenshot is sampled after GotoClick. It is not
an animation completion detector. Inspect pre-click, intermediate and stable
states separately, including whether KPI proxies overlap, whether the source
final value survives, and whether presenter pauses reveal content too early.

## Mechanism sources

Microsoft, read 2026-10-05. Documentation terms/copyright apply; no vendor code or
media was redistributed.

- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.gotoclick
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.getclickindex
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.getclickcount

GetClickIndex can describe an effect still running. Our conclusion is that a
matching index alone is insufficient to certify completion or appearance.
