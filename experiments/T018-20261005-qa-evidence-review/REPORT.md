# T018: native QA evidence integrity review

Date: 2026-10-05 UTC/Vietnam. Author: Codex /root. PR #21.
Main base: 405c170a8512b02f2f98b73b50788e24d6760aac.
Inherited unfinished harness: a00ea0391259985257853f19f36af37a2929adb6.
Own branch: work/T018-qa-evidence-review-20261005.

## Result

The unfinished native QA harness could accept missing click records, duplicate
records and failed probe runs. This study freezes 26 synthetic cases and repairs
the verifier without changing production motion writers or PPTX artifacts.

| Measured result on the same frozen cases | Baseline | Candidate |
|---|---:|---:|
| Correct parse/click decisions | 7/26 | 26/26 |
| False click passes | 18 | 0 |
| Crashes | 1 | 0 |

These are targeted synthetic software checks, not independent holdouts or a
PowerPoint success rate. No visual, motion or editability score is assigned.

## Changes

- Validate manifest identity, exact hash, counts, target names and click partition.
- Require a named PowerPoint version and recorded COM creation/opening.
- Reject duplicate/missing native and slideshow slide records.
- Require every click exactly once in order, with integer indices (not booleans),
  coherent before/after chains, a valid initial state and matching native counts.
- Require explicit successful slideshow completion and an empty probe error list.
- Reject malformed records without allowing empty-loop success.
- Keep raw PowerShell results provisional. Preserve the old click claim name as
  an alias for recorded index progression, while explicitly keeping animation
  completion and full playback claims false.
- Add Windows/manual workflow handoff. Preserve the original T018 branch.

## Why click position is insufficient

Microsoft's GetClickIndex documentation includes both currently running and
finished effects. Therefore, inferring final visual state solely from a matching
index would exceed the evidence. GotoClick initiates playback, while GetClickCount
reports defined click count. None of those records inspect the animated pixels.

Primary Microsoft sources, read 2026-10-05:

- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.getclickindex
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.gotoclick
- https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.getclickcount

Microsoft is the documentation author. Documentation terms/copyright apply;
no code/media copied. The verifier and synthetic cases are independently authored.

## Reproduce

Use the baseline verifier from a00ea03 (or its immutable Git blob
4efe11c221c4eb588e3642b1e1122a7a527998ff) with the same challenge runner:

```bash
git show a00ea0391259985257853f19f36af37a2929adb6:scripts/verify_powerpoint_qa.py > build/qa-baseline.py
python3 experiments/T018-20261005-qa-evidence-review/run_challenge.py build/qa-baseline.py --output build/baseline.json
python3 experiments/T018-20261005-qa-evidence-review/run_challenge.py scripts/verify_powerpoint_qa.py --output build/candidate.json
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
```

Full local suite: **150 tests passed**, including real-package temporary fixtures
for chart/KPI and generic motion. The 26 frozen cases execute as subtests.
No final PPTX was changed or exported in this study, so no new static render or
native playback claim is made. Host environment details are in environment.json.

GitHub Actions run 37248823323 succeeded on research commit
e6bb3ac6b17ede15318ec9acbcdf0fd41fe05de6: Python compile, PowerShell syntax parse
and full unit suite. This is Linux CI, not PowerPoint. The temporary CI workflow
is removed after validation; the manual Windows workflow remains undispatched.

## Useful failures

The original 18 false passes and one malformed-list crash remain in baseline.json.
Candidate results are in candidate.json. Acceptance was frozen before the repair.
One local apply_patch request was rejected because it tried delete/add of the same
path in a single patch; no files changed. A single update patch applied the change.

## Boundaries and next step

The verifier cannot authenticate JSON or infer appearance from capture filenames.
It does not compare per-click visual targets, paths, chart pixels, counter values
or elapsed animation completion. MainSequence target names are checked, not a
complete effect-semantic equivalence proof.

Next: use the documented harness in a dedicated Windows PowerPoint session on the
four exact T006 matrix hashes, then the composite chart/KPI/focus candidate.
Collect repair observations, video and pre/intermediate/stable states. Fill the
matrix checklist before changing path origin/fill. Full skill acceptance and M1
remain pending until that actual native evidence exists.
