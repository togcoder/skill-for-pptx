# T065 [cross] — Lab hygiene: encoding repair, duplicate-ID and size checks

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max), parallel programme T058–T065.
- **Date:** 2026-11-04. **Base:** `main` @ `ac5b45e` ("T058-T065: claim the next research programme").
- **Branch:** `work/T065-opencode-hygiene`.
- **Environment:** Windows 11, Python 3.13.5 (Miniconda), locale **`cp1258`**
  (a Vietnamese Windows install), git 2.x, no `PYTHONUTF8` in the shell unless
  stated. PowerPoint 16.0 is installed but not used: nothing here needs it.
- **Domain:** `cross` (lab process). The pptx product paths are named because
  they are the owner's goal, not because this task changes them.

## Frame

### Question

Which lab-wide defects stop the next agent from doing correct work, and can
each be made machine-detectable without touching product code?

The T057 review named three (finding 3, "process hygiene broke under parallel
agents"): the first file every agent reads was corrupt and pointed at the wrong
next ID; five task IDs were used twice; pptx code reached `main` without PR or
review. It also measured repo weight (116 MB, ~25k lines per vector/3D task).
T065 covers the parts a tool can check: encoding, duplicate IDs, size.

### Hypothesis and falsifiers

**Hypothesis.** The mojibake is one deterministic damage, a UTF-8 file decoded
once through the machine's `cp1258`/`cp1252` code page, so it is reversible
byte-for-byte; the 12 test errors are `Path.read_text()` without
`encoding="utf-8"`; and both can be kept from returning by a check that CI runs.

Falsified if:

1. some damaged text cannot be restored from its bytes or from git history
   (a byte the code page never had is unrecoverable);
2. a marker rule reports correct Vietnamese (false positive), which would make
   the rule unusable on this repository;
3. the suite still fails on a machine without `PYTHONUTF8=1`;
4. the size cap would fail the current tree instead of warning.

### Domain lens

The native material is the repository itself: commit history as the source of
truth for the original text, and the existing `lab/standards/` and
`lab/tools/check_layout.py` as the place rules are enforced. Nothing here is a
new dependency, a new service, or a new format.

### Deliberately not imported

- **No Git LFS.** The cap could be enforced with LFS, but that changes every
  clone, needs a quota and a migration of 392 office/media files. The owner
  decides; T065 only records the question and writes the cap as a warning.
- **No rewrite of another task's artifacts.** The JSON/MD artifacts of T039,
  T041, T045–T047 and T052 contain damage and non-UTF-8 bytes (see
  "Negative results"). They are frozen evidence with recorded SHA-256 values;
  rewriting them would invalidate their own `SHA256SUMS.txt`. They are listed,
  not touched.
- **No rewrite of `HANDOFF.md` or `docs/STATUS.md`.** Both are being edited by
  the parallel T058–T064 branches; the integrator rewrites them once after the
  programme lands (see Next).

## Frozen input

| Item | Value |
|---|---|
| Brief | `experiments/T057-20261104-claude-leader-review/REPORT.md`, section "T065 [cross] Lab hygiene" |
| Claim | `research/claims/T065-opencode-20261104.md` |
| Base commit | `ac5b45e` |
| Damaged files (brief) | `docs/CHANGELOG.md`, `domains/README.md`, "four experiment reports" |
| Damaged files (measured) | `docs/CHANGELOG.md` (812 markers), `domains/README.md` (3), `experiments/T045-…/REPORT.md` (5, plus BOM), `experiments/T046-…/REPORT.md` (26, plus BOM), `research/claims/T050-…md` (1) |
| Tests at base | 455 ran, **12 errors**, 7 skipped, 23.6 s — `artifacts/tests-before.txt` |
| Layout check at base | `layout OK` — the damage was invisible to it |
| Tracked files | 1 314 files, 64.1 MB total — `artifacts/size-report.json` |

**The brief said four reports; a marker scan finds two.** The other two the
lead reviewer probably counted are T039 and T041, whose mojibake is inside
`artifacts/*.json` (extraction output), not in the prose. This report measures
what is there rather than assuming the count.

**Could not access:** the other branches' reports (T058–T064) were not read, to
avoid touching work in progress. Nothing needed the network.

## Method

Every command runs from the repository root.

```bash
# 1. Locate the damage and its commits
python experiments/T065-20261104-opencode-hygiene/inputs/encoding_audit.py --rev ac5b45e \
  --out experiments/T065-20261104-opencode-hygiene/artifacts/encoding-audit.json
git log --format=%h --follow -- docs/CHANGELOG.md      # find the clean revision
git show 318f748:docs/CHANGELOG.md | head              # verify it has no markers

# 2. Restore line by line where a clean blob exists (exact damage simulation)
python experiments/T065-20261104-opencode-hygiene/inputs/restore_from_git.py \
  docs/CHANGELOG.md 318f748 459852d \
  --report experiments/T065-20261104-opencode-hygiene/artifacts/restore-changelog.json

# 3. Reversibly repair what is left
python experiments/T065-20261104-opencode-hygiene/inputs/repair_mojibake.py \
  docs/CHANGELOG.md domains/README.md \
  experiments/T045-20261101-opencode-advanced-docx/REPORT.md \
  experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md \
  research/claims/T050-opencode-20261102.md

# 4. Prove the repair and idempotency
python experiments/T065-20261104-opencode-hygiene/inputs/replay_repair.py --rev ac5b45e
python experiments/T065-20261104-opencode-hygiene/inputs/replay_repair.py --worktree

# 5. The rules
python lab/tools/check_layout.py
python experiments/T065-20261104-opencode-hygiene/inputs/rule_against_rev.py --rev ac5b45e

# 6. The suite, both ways
$env:PYTHONUTF8="1"; python -m unittest discover -s tests
Remove-Item Env:\PYTHONUTF8; python -m unittest discover -s tests
```

### How the repair works

**Damage.** A UTF-8 file read with a single-byte code page and saved as UTF-8
turns each non-ASCII byte into one character of that page:

| Original | UTF-8 bytes | Read as `cp1258` | Read as `cp1252` |
|---|---|---|---|
| `—` U+2014 | `E2 80 94` | `â€”` | `â€”` | <!-- allow-mojibake -->
| `đ` U+0111 | `C4 91` | `Ä‘` | `Ä‘` |
| `ú` U+00FA | `C3 BA` | `Ăº` | `Ãº` | <!-- allow-mojibake -->
| `ả` U+1EA3 | `E1 BA A3` | `áº£` | `áº£` |

The repository has both variants because two tools did it: `cp1258` on this
machine and `cp1252` on a Western one. That is why the brief's four markers
miss `áº` and `Ă`, which are the same damage seen through the other page.

**Repair, step 1 (reversible).** Walk the text looking for the *shape* of a
UTF-8 sequence made of single-byte-code-page characters: a lead byte
(`C2`–`F4`) and the right number of continuation bytes (`80`–`BF`), turn them
back into bytes and decode as UTF-8. Correct text cannot match the shape — a
genuine `ă` is the single byte `A3`, a continuation byte, so it never starts a
sequence. Two code pages are tried because `€`, `‰` and `™` only exist in
`cp1252`, and `Ă`, `Đ`, `Ơ`, `Ư` only in `cp1258`. C1 controls
(`U+0081`, `U+008D`, `U+008F`, `U+0090`, `U+009D`) are the bytes the page
could not name, so their code point *is* the byte.

**Repair, step 2 (from git).** A few lines cannot be reversed because the byte
was not merely renamed but dropped. Git has the original: the damage landed in
three commits on 2026-11-01 and their parents are clean. `restore_from_git.py`
pairs a damaged line with its closest undamaged line and accepts the pair only
when *the damage can be simulated exactly* — encode the candidate as UTF-8,
decode each byte through a code page, drop the bytes the page lacks, and compare
with the damaged line character for character. A line that also received a real
edit cannot pass that test, so no content update is reverted.

**Why not just re-encode the whole file?** Because these files mix correct and
damaged text: `docs/CHANGELOG.md` had 812 marker occurrences in 161 of 1 169
lines. A whole-file reversal would corrupt the 1 008 correct lines.

## Evidence

### Provenance of the damage

| Commit | Date (+07) | File | Markers in parent → in commit |
|---|---|---|---|
| `459852d` "T046 [xlsx]: update suite count after main merge" | 2026-11-01 12:56:03 | `docs/CHANGELOG.md` | 0 → 1 648 |
| `459852d` | 12:56:03 | `experiments/T046-…/REPORT.md` | 0 → 32 |
| `bc7a071` "T045 [docx]: update suite count after main merge" | 12:56:07 | `experiments/T045-…/REPORT.md` | created damaged (6) |
| `f7185ae` merge of PR #42 | 13:26:43 | `domains/README.md` | 0 → 4 |
| `0449022` T057 | 2026-11-04 12:42 | `HANDOFF.md` | repaired by T057 (0 now) |

All four are OpenCode/DeepSeek commits from this machine, whose Python opens
text as `cp1258`. The damage is not in the git object store — the blobs are
valid UTF-8 — it is in the *content* those tools wrote.

### Repair results

| File | Markers before → after | Other damage before → after | Rung |
|---|---|---|---|
| `docs/CHANGELOG.md` | 812 → 0 | C0/C1 controls `U+0007 U+0081 U+008D U+008F U+0090 U+009D` → none | 1 |
| `domains/README.md` | 3 → 0 | — | 1 |
| `experiments/T045-…/REPORT.md` | 5 → 0 | BOM → none | 1 |
| `experiments/T046-…/REPORT.md` | 26 → 0 | BOM, `U+009D` → none | 1 |
| `research/claims/T050-…md` | 1 → 0 | — | 1 |
| `lab/standards/OUTPUTS.md` | 4 added, **0 flagged** | the four marker names as documentation, inside backticks | 1 |

Rung 1: the bytes are valid UTF-8 and every intended character is present;
a human read the diff, but no external reader parsed it (rung 3 would be a
Markdown renderer, rung 6 the owner reading the files).

Volume: `restore_from_git.py` verified **61** line pairs in the CHANGELOG
(60 applied; one had already been repaired by T057) and **11** in the T046
report. `repair_mojibake.py` fixed **1 862** sequences across the five files on
the base blobs and **0** on the working tree, so the repair is idempotent
(`artifacts/repair-replay.json`).

The `≈` trap: `docs/CHANGELOG.md` line 214 held `(â‰ˆ93% A4)`. `‰` is the byte
`0x89`, which `cp1258` does not define, and `cp1252` does. A one-code-page
repair silently leaves it. The dual-page pass is why it now reads `(≈93% A4)`.

### The rule catches the old tree

`inputs/rule_against_rev.py --rev ac5b45e` applies the new check to the base
blobs: **18 findings in 286 Markdown files**, including both BOMs, the
`U+0007` in the CHANGELOG and every marker line (`artifacts/rule-at-base.txt`).
On the repaired tree the same check reports **0**
(`artifacts/check-layout-after.txt`).

### Tests on a cp1258 machine

| Run | Command | Result |
|---|---|---|
| Base, before the fix | `python -m unittest discover -s tests` | 455 ran, **12 errors**, 7 skipped, 23.6 s |
| After, no env var | same, locale `cp1258`, `PYTHONUTF8` unset | **476 ran, OK**, 8 skipped, 25.3 s |
| After, `PYTHONUTF8=1` | `$env:PYTHONUTF8="1"; …` | **476 ran, OK**, 8 skipped, 28.7 s |

12 → 0 errors with the locale still `cp1258` — `artifacts/tests-no-pythonutf8.txt`
opens with `preferred encoding: cp1258` and `PYTHONUTF8: <unset>`, and ends with
`OK (skipped=8)`.

The test *count* differs from the base because a failing `setUpClass` drops its
class from unittest's count: the base run never reached the 6
`DirectorCompoundTests` methods, and T065 adds 15 (461 + 15 = 476, matching the
T057 count of 461). Both modes run the same tests: sorting the verbose logs of
the two runs and comparing them with `Compare-Object` gives no difference, so
no test silently disappears without the env var.

Files changed: 12 `read_text()` calls in six test modules got
`encoding="utf-8"` — `test_choreography` (1), `test_compound_motion` (4),
`test_design_system` (1), `test_layers_and_script` (3), `test_morph_studio` (1),
`test_textbox_normalization` (2). The T046 report's `CafĂ©s` failure is the
tell: on `cp1252` the read *succeeds* and silently produces mojibake, so the
test fails on a *target name* rather than an exception. A missing `encoding=`
is therefore both a crash and a silent corruption, depending on the page.

### The check (`lab/tools/check_layout.py`)

New failures:

| Rule | Message | Test |
|---|---|---|
| Markdown not valid UTF-8 | `<file>:<line>: not utf-8: byte N: …` | `test_invalid_utf8_is_flagged` |
| Leading BOM | `<file>:1: bom: file starts with a byte-order mark` | `test_bom_is_flagged` |
| C0/C1 control | `<file>:<line>: control: U+0007` | `test_control_characters_are_flagged` |
| Mojibake marker | `<file>:<line>: mojibake: â€` | `test_mojibake_is_flagged_with_a_line_number` | <!-- allow-mojibake -->
| Duplicate task ID | `INDEX.md: task ID T042 is used twice (rows 71 and 72)` | `test_duplicate_ids_are_reported` |

New warnings (never change the exit code):

| Rule | Message | Test |
|---|---|---|
| File > 2 MB | `warning: <path>: 3.0 MB committed (cap 2 MB/file)` | `test_file_over_two_megabytes_warns` |
| Task > 10 MB | `warning: experiments/T900: 11.0 MB committed (cap 10 MB/task)` | `test_task_over_ten_megabytes_warns_once` |

**False positives on correct Vietnamese: none.** The markers are not vowels —
`Ã`, `Ä‘`, `á»`, `â€` never occur in Vietnamese words, only as the Latin-letter
shadow of a UTF-8 byte pair. The one place they legitimately appear is a
sentence *about* the markers (this report, the T057 brief, `OUTPUTS.md`, the
CHANGELOG entry). The rule therefore ignores a code span only when the span
contains nothing but markers and separators (`` `Ã` `` is exempt;
`` `Hình 1 â€” doanh thu` `` is still reported). The cost is measured: 2 of the <!-- allow-mojibake -->
5 T045 markers and 3 of the 26 T046 markers were inside code spans and would
not have been flagged — the repair fixed them anyway.

`_index_ids()` reads the ID cell of `research/tasks/INDEX.md` only, so a task ID
quoted in a title or an evidence column ("superseded by T019") is not a
duplicate. `T047`/`T047b`, `T048`/`T048b` and `T024a`/`b`/`c` are distinct IDs
and pass — that is how the historical duplicates were papered over, and the
rule keeps that record rather than re-litigating it.

### Size cap

Measured on the branch: 1 314 tracked files, 64.1 MB; **0 files over 2 MB**;
largest task `T024` at 9.6 MB; **0 warnings**. So the cap as a warning is a
no-op on today's tree and starts talking only when a task commits heavy media
— which is what T054 (24.8k lines) and T055 (27.8k lines) would have done.
The owner decision "LFS or not" is recorded as open in
`lab/standards/OUTPUTS.md`; T065 creates no LFS pointer.

### Rules written down

| Rule | Where |
|---|---|
| Committed artifacts: 2 MB/file, 10 MB/task; bigger stays local with a hash; LFS decision open | `lab/standards/OUTPUTS.md` |
| pptx product paths change only through a PR with a review of the diff | `domains/pptx/DOMAIN.md` ("Product paths change only through a pull request with a review") and a pointer in `lab/standards/MERGE.md` |
| Text files are UTF-8 without BOM; pass `encoding="utf-8"`; CI sets `PYTHONUTF8=1` | `docs/ENVIRONMENT.md`, "Text encoding (T065)" |
| CI exports UTF-8 mode | `.github/workflows/tests.yml` (new), `.github/workflows/powerpoint-native-qa.yml` |

The new workflow runs on `ubuntu-latest` and `windows-latest`: compile,
`check_layout.py`, then the suite. The Windows job is the one that would have
caught this class of defect, because only it defaults to `cp1258`.

## Negative results and limitations

1. **63 marker occurrences could not be repaired by decoding alone** and were
   restored from git instead (`restore_from_git.py`). Without a clean blob the
   damage would have been permanent for those lines — the falsifier "some
   damage is lossy" is therefore **partly true**: the byte is gone, only
   history recovers it. A file damaged before its first commit would stay
   broken.
2. **`experiments/*/artifacts/*.json` are not covered by the rule and are not
   repaired.** 4 files are not valid UTF-8 (`T051/artifacts/line-info.json`,
   `T052/artifacts/conformance-hust.json`, `conformance-vnu.json`,
   `T053/artifacts/info.json`) and 11 more carry 1 100+ markers (`T039`, `T041`,
   `T045`, `T047`, `T052`). They are raw extraction output with recorded
   hashes; rewriting them would break their `SHA256SUMS.txt` and their reports'
   rung-1 claims. A follow-up task must re-extract and re-hash, not text-edit.
3. **16 files still start with a BOM**, 14 of them JSON artifacts written by
   Windows PowerShell `Out-File`. Only the two Markdown files (T045/T046
   reports) were cleaned. JSON readers tolerate a BOM; Markdown renderers show
   it as text.
4. **The rule reads Markdown only.** `.json`, `.txt`, `.yml` and `.py` are not
   scanned for markers, so a damaged `knowledge/*.json` would pass. Widening
   the rule needs the artifact decision above first.
5. **`docs/CHANGELOG.md` line 308 still has a tab where a letter belongs**
   (`\	ests/test_multi_domain_canons.py\`). It is a different lossy damage (a
   byte replaced by `0x09`), outside the marker set, and recorded here rather
   than guessed.
6. **`experiments/T057-…/REPORT.md` deliberately contains the markers** as a
   specification. It passes only because of the marker-only code-span
   exemption. The same exemption means a damaged sentence *inside* a code span
   with other words is still caught, but a sole damaged word in backticks is
   not.
7. **The new CI workflow has never run.** T065 may not push. Its YAML parses
   locally and the same commands pass on this machine, but rung 0 (plan) is the
   honest rung for it until the owner's first push.
8. **`HANDOFF.md` and `docs/STATUS.md` were not rewritten.** Both are edited by
   the parallel T058–T064 branches; rewriting them here guarantees a conflict.
   `docs/STATUS.md` is still stale from before T057.
9. **The 8 skipped tests are unchanged** (PowerPoint COM and LibreOffice
   fixtures absent in this shell). T065 did not add or remove a skip.
10. **One run failed on a PowerPoint COM flake.** `test_advanced_interactivity`
    raised `pywintypes.com_error: (-2147023170, 'The remote procedure call
    failed.')` during a full run; the same suite passed on the next two runs.
    That test drives live PowerPoint through COM and is load-sensitive. It is
    not an encoding failure and it is not caused by T065, but a CI job on a
    Windows runner will see it from time to time.

## Next

1. **[cross] Repair the JSON artifacts.** Re-extract `T039`, `T041`, `T045`,
   `T047`, `T051`, `T052`, `T053` artifacts with UTF-8 tooling, regenerate
   `SHA256SUMS.txt`, and state which numbers in those reports change. Do not
   text-edit them: the reports cite them by hash.
2. **[cross] Widen the rule to JSON product data** (`knowledge/`, `examples/`,
   `domains/*/data/`) once (1) lands, and make the size cap a hard failure
   after one cycle.
3. **Owner: decide Git LFS.** If yes, migrate `experiments/*/artifacts/*.pptx`
   and stop capping; if no, the 2 MB/10 MB warning becomes an error. The
   decision belongs in `lab/standards/OUTPUTS.md`.
4. **Integrator: rewrite `HANDOFF.md` and `docs/STATUS.md`** after T058–T064
   land, so the first file an agent reads is true again (the T057 review's
   finding 3 is only half fixed until then).
5. **Add a pre-commit hook** (`python lab/tools/check_layout.py`) so the
   damage is caught at the writing machine, not in review. This is the only
   way to stop the *cause*: a tool that writes UTF-8 through `cp1258`.
6. **Run `.github/workflows/tests.yml` once** on the first push and record the
   run URL here; promote it from rung 0.

## Review response

Not reviewed yet. The T057 table assigns T065 to the owner (`any → owner`);
the report is ready for that review. Findings will be answered here as fixed,
disputed (with evidence) or deferred (with a task row).
