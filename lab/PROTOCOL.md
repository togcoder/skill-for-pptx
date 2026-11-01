# Agent protocol — how every agent works here

The same lifecycle applies in every domain. Standards are in `lab/standards/`.

```
0 ORIENT → 1 CLAIM → 2 FRAME → 3 RESEARCH/BUILD → 4 SELF-CHECK → 5 REVIEW → 6 RESPOND → 7 MERGE → 8 HANDOFF
```

**0. Orient (read before writing).** Read:

- `AGENTS.md`;
- `HANDOFF.md`;
- `lab/CHARTER.md`;
- this file;
- the card of your domain, `domains/<domain>/DOMAIN.md`;
- the last two reports in that domain.

Run the tests. Fetch remote branches: the newest research may not be on `main`.

**1. Claim.**

- Take the next free ID in `research/tasks/INDEX.md`.
- Add a row with the **domain** in brackets in the title (e.g. `[xlsx] Chart
  axis canon`), the agent and the branch, with status `claimed`.
- Create `research/claims/<ID>-<agent>-<date>.md` from
  `lab/templates/CLAIM.md`.
- Push both before expensive work. One task = one domain. A cross-domain
  task uses domain `cross`.

**2. Frame.** At the top of the REPORT, before building anything, write:

- the question;
- the hypothesis and how it could be shown false;
- the domain lens: which native sources and canon you will use;
- what you are deliberately **not** importing from another domain, and why.

If the idea comes from another domain, name the transfer, e.g. "pptx motion
tokens → docx?", and plan a test of it.

**3. Research / build.** Work on your branch, in
`experiments/<ID>-<date>-<agent>-<slug>/`. Every file you make goes there or
into code. Placement rules: `lab/standards/OUTPUTS.md`. Verification decks,
documents, sheets and renders go into the experiment's `artifacts/`, **never
the repository root**. Use `workspace/` for scratch.

**4. Self-check.**

- Tests pass.
- `python3 lab/tools/check_layout.py` passes.
- Each claim in the REPORT has an evidence rung.
- Negative results and limitations are written down.
- New code is not wired into a product path until a review accepts it.
  Mark it `EXPERIMENTAL` in its header until then.

**5. Review (peer critique).**

- Ask for a review by adding `review requested` to your INDEX row.
- A different agent writes it, preferably a different model family:
  `research/reviews/<ID>-<reviewer>-<date>.md`, following
  `lab/standards/REVIEW.md`.
- Only reviewed work can be merged into product paths and `knowledge/`.

**6. Respond.**

- The author answers each finding in the REPORT's "Review response" section
  as fixed, disputed (with evidence) or deferred (with a new task row).
- No silent edits after review: a new review round covers new commits.

**7. Merge.** The integrator merges by `lab/standards/MERGE.md`:

- code into the canonical module;
- data into `knowledge/` with provenance;
- conflicts kept side by side until a test decides.

The owner approves merges to `main`.

**8. Handoff.**

- Add a `docs/CHANGELOG.md` entry.
- Rewrite your domain card's "State" section.
- Rewrite `HANDOFF.md` if lab-wide state changed.
- Update the INDEX row.

## Anti-monoculture rules

- Before reusing a module from another domain, check the target domain's
  native model first. Example: do not lay out a Word document with slide
  grids. Write down the decision.
- At most one task in three may be in the domain that already has the most
  merged work, unless the owner says otherwise. Check the INDEX.
- Cross-domain "universal" layers (hubs, decoders, shared tokens) need
  accepted reviews from at least two domains before they become canonical.
