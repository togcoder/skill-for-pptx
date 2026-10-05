# T018: Native PowerPoint QA

Status: harness integrated and evidence verifier tested; actual native execution
pending. First harness branch remains work/T018-powerpoint-native-qa-20261005.
Review/repair branch: work/T018-qa-evidence-review-20261005 (PR #21).

Read docs/POWERPOINT_NATIVE_HARNESS.md and
experiments/T018-20261005-qa-evidence-review/REPORT.md before continuing.

Completed: exact-artifact manifest, Windows COM probe, composite fixture builder,
record verifier, 26 synthetic evidence cases and 150-test full suite.
False click passes in those frozen cases fell from 18 to 0. This is verifier
quality evidence only. No PowerPoint playback has been recorded.

Next acceptance:

1. Run four existing T006 semantics artifacts unchanged in named PowerPoint.
2. Preserve hashes, repair observations, native click records and video.
3. Verify stable A/B/C states and select a path/fill variant only with evidence.
4. Exercise chart reveal, single-visible-value counter and generic focus while
   preserving presenter click pauses. Check intermediate and final states.
5. Rebuild broader candidates only after an observed failure supports a repair.

Do not regenerate the same matrix or interpret a click API pass as full playback.
