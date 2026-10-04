# T006 motion origin/fill semantics matrix

- Owner: Codex /root
- Started UTC: 2026-10-04T19:57:29Z
- Base: ad707aa77408cae07c4e744598f7284c57c05ed9
- Branch: work/T006-motion-semantics-matrix-20261004
- Experiment: experiments/T006-20261004-motion-semantics-matrix
- Status: completed (controlled fixture and handoff); native winner pending
- Scope: build a controlled two-stage, one-object native motion fixture. Compare stage-local vs authored-layout path coordinates and remove vs hold behavior fill. Own new fixture generator, audit, outputs and report. Do not change production writer without native playback evidence.
- Evidence boundary: structural checks and static renders are not PowerPoint playback.
- Checkpoint UTC: 2026-10-04T20:08Z. Four controlled files finalized and inspected; exact audit has no findings; 83 tests pass. Production writer and source skill unchanged.
- Next: fill playback-checklist.json from all four exact hashes in a named Microsoft PowerPoint version, then decide whether a writer change is supported.
