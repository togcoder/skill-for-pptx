# Claim — T019 canonical timing + one-command Motion Director

- Task: research/tasks/T019-canonical-timing-motion-director.md
- Agent: Claude Code (cloud session), for owner togcoder
- Branch: claude/blissful-pasteur-gmll59 (assigned by the session)
- Base commit: see experiments/T019-20261005-claude-motion-director/base-commit.txt
- Scope: new files scripts/pptx_animator.py, scripts/motion_director.py,
  scripts/lo_timing_crosscheck.py, scripts/make_report_fixture.py,
  tests/test_motion_director.py, tests/fixtures/report_deck.pptx,
  skills/pptx-motion-director/, .claude-plugin/, commands/; additive v0.5 gate in
  scripts/validate_director_plan.py; docs.
- Frozen baselines untouched: patch v0.1–v0.5 writers and their tests.
- Status: completed (structural + LibreOffice cross-check); PowerPoint playback pending.
