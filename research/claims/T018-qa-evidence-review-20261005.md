# T018 QA evidence review

- Owner: Codex /root
- Started UTC: 2026-10-05
- Main base: 405c170a8512b02f2f98b73b50788e24d6760aac
- Inherited T018 head: a00ea0391259985257853f19f36af37a2929adb6
- Branch: work/T018-qa-evidence-review-20261005
- Experiment: experiments/T018-20261005-qa-evidence-review
- Status: completed (evidence-integrity repair and handoff); native execution pending
- Scope: review and integrate the unfinished native QA harness on a separate branch. Freeze malformed-evidence cases; prevent missing/error/duplicate click records from producing a native execution claim. Preserve source effect writers and all historical artifacts.
- Native PowerPoint unavailable in this Linux environment. No playback claim will be made. Synthetic evidence validates the verifier only.
- Checkpoint: 26/26 candidate decisions correct, 18 -> 0 false click passes, 1 -> 0 crashes; 150 local tests and CI 37248823323 pass. Original T018 branch preserved.
- Next: run the existing exact-hash matrix in Windows PowerPoint, then chart/KPI/focus visual capture. Do not treat synthetic evidence or native click indices as full playback.
