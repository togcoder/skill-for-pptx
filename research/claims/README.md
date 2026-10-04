# Active research claims

No active claim has been created by this handoff. Before taking a task, check
open branches and draft PRs. Follow docs/COLLABORATION.md. Add one file per
task/agent/run, using this content:

```yaml
task: T001
agent: actual-agent-name
status: in_progress
started_at_utc: actual-time
updated_at_utc: actual-time
base_commit: actual-sha
branch: work/T001-agent-date
scope: exact-experiment-and-files
next_step: concrete-action
```

Record completed/paused/blocked/failed on exit. A claim is coordination evidence,
not an atomic lock. Resolve conflicting claims before expensive work.
