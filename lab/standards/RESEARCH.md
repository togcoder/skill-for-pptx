# Research standard

A REPORT (`lab/templates/EXPERIMENT_REPORT.md`) must contain these sections:

1. **Frame:**
   - the question;
   - the hypothesis, and what would falsify it;
   - the domain lens;
   - the transfers from other domains.
2. **Frozen input:**
   - the request;
   - the base commit;
   - the environment (OS, application and build, libraries);
   - what you could not access.
3. **Method:** the commands, so that another agent can rerun them.
4. **Evidence:**
   - tables and artifacts, with paths and hashes;
   - every claim tagged with its rung (below).
5. **Negative results and limitations.** This section is required; write
   "none found" only if you looked.
6. **Next:** concrete, with task suggestions.
7. **Review response:** filled in after review.

## Evidence rungs (generic; each domain card maps them to its tools)

| Rung | Meaning |
|---|---|
| 0 planned | A plan or spec passes its validator |
| 1 structural | The file is well-formed, the tool's invariants hold, it is schema-valid if a schema exists |
| 2 simulated | The tool's own model renders or predicts the result (previews, layout engine) |
| 3 independent reader | Another implementation reads or renders it: LibreOffice, a browser, a second parser |
| 4 target-parsed | The target application opened the exact file (hash recorded) and reported its model |
| 5 target-rendered | The target application rendered or exported it (video, PDF, image) |
| 6 human-verified | A person used it in the target application as intended (played it, edited it, printed it) and the captures were reviewed |

Never write a lower rung as a higher one. Scores from a critic are rung
1–3 measurements, not human judgement.

## Sources

Give the URL or DOI and the access date. Mark "summary only" when the primary
text was unreachable. Note the licence for anything stored. Derived numbers
only; reference media stays local.

## Code

- Code from outside agents or imported drops starts as `EXPERIMENTAL`. It
  enters product paths only after an accepted review.
- New numbers (durations, sizes, contrasts, thresholds) go into the domain's
  design-system data with their source, never hard-coded.
