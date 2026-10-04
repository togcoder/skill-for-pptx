# T006 packed candidate validation

- Owner: Codex /root
- Started/checkpoint UTC: 2026-10-04T19:09:35Z
- Base: 0bd74645f554e73a238fba3a4dfac1b3b7f4f5dd
- Branch: work/T006-packed-validation-20261004
- Experiment: experiments/T006-20261004-packed-validation
- Status: completed (bounded build/audit experiment); native acceptance still pending
- Scope: run existing packed pipeline on frozen T005 intent; verify exact PPTX, inspect final static render; audit timing geometry. Own experiment/output and evidence checker; no competing T007 work.
- Earlier PR #5 only claimed a now-superseded alternative compiler. Close it as superseded; preserve branch/brief history. This experiment uses merged writer.
- Checkpoint UTC: 2026-10-04T19:16:13Z. Final candidate hash and report saved; 79 tests pass. Opening-text fix retained, timing writer unchanged. Conditional coordinate risk retained as negative evidence.
- Next: exact-file PowerPoint playback and authored two-stage fixture for origin/fill/trigger semantics. See experiment REPORT.md and playback-checklist.json.
