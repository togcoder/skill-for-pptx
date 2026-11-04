# T064 — decoupling T055 from T054: plan and execution

**Question.** Which parts of `work/T055-opencode-pptx-3d` actually need the
unmerged T054 branch, and can T055 be rebuilt on `main` without changing a
single byte of its evidence?

**Answer.** One file, one path. T055 depends on T054 only through reading
`experiments/T054-…/artifacts/blockout.json` at a hard-coded absolute path, and
on the five T054 commits that carry that file in its history. The geometry is
data, so it travels as a frozen input artifact. Rebuilding from the frozen copy
reproduces the committed GLB byte for byte, so the deck, the PDF, the audit and
the tests are untouched.

## 1. Dependency inventory

| Kind | Where | Real dependency? |
|---|---|---|
| Code | `experiments/T055-…/inputs/make_product_glb.py:33-37` — absolute `C:\…\skill-for-pptx-T054\…\blockout.json` | **Yes** — the only hard one |
| Artifact | `preview/glb-manifest.json` `"source"` / `"glb"` strings | Records the same absolute path (evidence hygiene, not a build dependency) |
| History | T055 branch contains T054 commits `2c6e089`, `dac65c3`, `26759ac`, `d1feb1f`, `b387146` | **Yes** — merge order |
| Tests | `tests/test_product_deck_3d.py` | No — reads only T055-local artifacts |
| Prose | T055 REPORT, claim, CHANGELOG, STATUS, DOMAIN, HANDOFF say "stacked on T054" | No, but they would keep the false merge order |
| Assets | none — no vector asset from T054 is used in the deck (the report says so) | No |

Checked with:

```powershell
Select-String -Path "experiments\T055-…\inputs\*.py","tests\test_product_deck_3d.py" `
  -Pattern "T054|blockout|skill-for-pptx-"
# -> only make_product_glb.py:2,8,33,34,37,254
```

## 2. Plan

1. Freeze the input: copy `blockout.json` to
   `experiments/T055-…/inputs/blockout.json` and record its SHA-256.
2. Point `make_product_glb.py` at `HERE / "blockout.json"`; write provenance
   (origin, origin commit, SHA-256) into `preview/glb-manifest.json` with
   relative paths.
3. Prove the change is inert: rebuild the GLB and compare its SHA-256 with the
   committed one. If it differs, stop — the decoupling changed the asset.
4. Rebase the five T055 commits onto `main` `ac5b45e`, dropping the five T054
   commits. Lab-state files (HANDOFF, CHANGELOG, STATUS, INDEX, DOMAIN) keep
   `main`'s current text; the T055 author rewrites them when T055 merges.
5. Re-run the T055 tests and the full suite; confirm no T054 path is left.

**Why not merge T054 first?** T054 is review-requested and unmerged, and it is
a vector task whose acceptance may fail the owner's eye test. T055's claim does
not depend on T054's verdict: it uses the blockout as a mesh source, not as a
design. Freezing the input lets the two tasks land independently and in either
order.

## 3. Execution

```powershell
git checkout -b work/T064-opencode-native-3d ac5b45e
# five T055 commits, one at a time
git cherry-pick -n 64d6d47   # claim
git cherry-pick -n e71e0aa   # deck + inputs + tests
git cherry-pick -n 1a309d5   # test path fix
git cherry-pick -n ec5bf8f   # audit + PDF refresh
git cherry-pick -n addd340   # tower colour + hashes
# conflicts: HANDOFF.md, docs/CHANGELOG.md, docs/STATUS.md, research/tasks/INDEX.md
git checkout --ours HANDOFF.md docs/CHANGELOG.md docs/STATUS.md research/tasks/INDEX.md
git add …
git commit -m "<original message>"   # per cherry-pick
```

| T055 (origin) | Rebased on `main` | Note |
|---|---|---|
| `64d6d47` | `49cfeee` | claim; INDEX conflict resolved to `main` (T064 must not edit INDEX) |
| `e71e0aa` | `bc7b3e9` | deck, inputs, preview, tests; DOMAIN auto-merged |
| `1a309d5` | `9dd7b62` | test path fix |
| `ec5bf8f` | `bdbcec5` | audit + PDF refresh |
| `addd340` | `6a60036` | tower colour + hashes |

Then the decoupling commit (T064): `inputs/blockout.json`, the script change,
the manifest provenance, and the report/claim wording.

**Conflicts and how they were resolved.** Every conflict was in lab-state prose
that T057 rewrote after T055 branched (`HANDOFF.md`, `docs/CHANGELOG.md`,
`docs/STATUS.md`, `research/tasks/INDEX.md`). `main`'s text was kept, because
T064 is forbidden to edit INDEX and because rewriting HANDOFF/STATUS is the
handoff step of the task that merges, not of the reviewer. No T055 evidence file
conflicted.

## 4. Verification

| Check | Result |
|---|---|
| GLB rebuilt from `inputs/blockout.json` | 56,544 B, SHA-256 `fd252d7c6e2470b9809766d9dcba0bbd546c8169209b7426ea6ceb363f959143` — identical to the committed GLB |
| T055 contract tests | 10 tests, OK |
| Full suite (`PYTHONUTF8=1`) | 471 tests, 8 skipped, 0 failures |
| T054 files in the branch | none (`git diff --name-only ac5b45e..HEAD` matches only `quickmill-blockout.glb`, a T055 artifact) |
| Absolute T054 path left | none |
| Commits from T054 | none |

## 5. Rollback

The rebase is a new commit range; the original branch is untouched. To undo,
reset the T064 branch to `ac5b45e` and keep using `work/T055-opencode-pptx-3d`.
Nothing was pushed to `origin` and no other worktree was modified.
