# Review standard (peer critique)

Reviews keep a single line of thought from taking over. Every task that
changes code, data or a product path gets at least one review before merge.

- **Who:** an agent that did not author the task, preferably from a different
  model family than the author.
- **Where:** `research/reviews/<task ID>-<reviewer>-<date>.md`
  (template: `lab/templates/REVIEW.md`).
- **Rubric:** this file plus `lab/protocols/03_redteam_critique_rubric.md`.

## The reviewer must

1. **Reproduce** at least one main result from the REPORT's commands and write
   down what happened. A review without a reproduction attempt can only say
   `revise`.
2. **Check claims against rungs.** List each claim stated above its evidence
   rung.
3. **Check validity:**
   - schemas and real fixtures, not only synthetic tests;
   - whether the tests could pass while the feature is broken (circular tests).
4. **Check overlap:** does this duplicate a canonical module or a data set?
   Name the canonical one.
5. **Check domain fit:**
   - Does it use the target application's native model?
   - Were ideas imported from another domain without a test?
6. **Look for regressions:** before/after on existing inputs, using the
   domain's critic where one exists.
7. **Give a verdict and keep the dissent.**

## Verdicts

| Verdict | Meaning | Effect |
|---|---|---|
| `accept` | Claims hold at the stated rungs | Integrator may merge |
| `accept-with-fixes` | Small, listed fixes | Merge after the author fixes them; no new review needed |
| `revise` | Main claims not yet supported | Author responds; then a new review round |
| `quarantine` | Unsafe or invalid output, or overlap with no gain | Code stays labelled `EXPERIMENTAL` and out of product paths |
| `reject` | Hypothesis falsified, or not worth keeping | Report and negative result kept; code not merged |

Findings are numbered (R1, R2, …). Each finding gives:

- severity: blocking, major or minor;
- evidence, as a command and its output, or a file and line;
- the fix asked for.

Disagreements are written down, not voted away. The owner decides open
disputes.
