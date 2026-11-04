# T061 [pptx] — One canonical interaction writer (interactiveSeq / triggers / hyperlinks)

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), parallel programme T058–T065.
- **Date:** 2026-11-04. **Base:** `main` @ `ac5b45e`. **Branch:**
  `work/T061-opencode-interaction-writer`.
- **Brief:** `experiments/T057-20261104-claude-leader-review/REPORT.md`,
  section "Next research programme", row T061.
- **Environment:** Windows 11, Python 3.13.5 (Anaconda), lxml, python-pptx,
  Microsoft PowerPoint 16.0 (COM). `D:\artcraft\DeckCraft\deckcraft-cli.exe`
  present but not used: no slide content changed, so a render would be a
  restatement of the T048 previews.
- **Status:** complete, review requested. Code stays on the branch; nothing was
  merged or pushed.

## Frame

**Question.** Can `interactiveSeq`, its trigger conditions and the
hyperlink-vs-trigger conflict live in one module, with
`interactive_triggers.py`, `advanced_interactivity.py` and
`slide_navigator.py` as thin callers, without changing what PowerPoint parses
or what the committed T048b/T049 artifacts contain?

**Hypothesis (and falsifiers).**

- *H1 — ownership.* `pptx_animator.py` can own the writer and the three modules
  can delegate to it. Falsified if a committed T048 deck no longer rebuilds to
  identical slide XML, or if the T049 artifact parses to different sequence
  counts.
- *H2 — no duplicate writer.* Falsified if any script besides
  `pptx_animator.py` still constructs `nodeType="interactiveSeq"`, or if an
  existing T049 test must change.
- *H3 — target parser accepts it.* PowerPoint 16.0 COM reads the canonical
  subtree as one interactive sequence with the right trigger and target.
  Falsified if COM reports 0 sequences, the wrong trigger, or drops the effect.

**Domain lens.** ECMA-376 PresentationML timing (`p:timing` > `p:seq` >
`p:cTn`), the Office 16.0 COM capture that T049 recorded, and the lab rule
"one canonical module per capability" (`AGENTS.md`, `lab/standards/MERGE.md`).
Every design number used here (durations 0/300/350/500 ms) is an input value,
not a new threshold.

**Transfers from other domains.** None. This is pptx-internal consolidation:
no token, hub or decoder crosses a domain boundary, so the two-domain review
rule for "universal" layers does not apply.

## Frozen input

| Input | Hash / identity |
|---|---|
| Base commit | `ac5b45e` (T058–T065 programme claim); `git merge-base HEAD main` = `ac5b45e` |
| T048b game deck | `experiments/T048-20261101-antigravity-slide-branching/artifacts/interactive_adventure_game.pptx` — `eea43de7497182a78a21e5e35767bb2ca33066023834b387889ffdd6f0097616` |
| T048b hub deck | `…/executive_interactive_hub.pptx` — `c924c3b7e373a013de19a1d3c530f55d00eb924bb01e5c29048c806f5a7f4cf9` |
| T049 suite | `experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/one_slide_games_suite.pptx` — `f91531f87e381fa2f84a02a1bb14f918ddf4d9d3c816098a223a3d22211bab3f` |
| T049 stored audit | `…/audit_one_slide_games.json` — `6e4f9e3874fca61175b3dd464c71835e7112140eca4e1641e4e0ba0188fdd01c` |
| Pre-refactor code output | `inputs/` — produced at `ac5b45e` by `make_evidence.py --label before` (frozen; not regenerated after the refactor) |
| Code diff | `inputs/CODE_DIFF.patch` — `git diff ac5b45e -- scripts tests` (95 KB) |

**Not accessible / not attempted.** A live slide-show click (T058 is a separate
task and its harness does not exist yet). DeckCraft render: no content change,
so no new render. Two PowerPoint COM runs are recorded (rung 4), but nothing
was played.

## Method

```powershell
$env:PYTHONUTF8=1
# before (run at ac5b45e; the committed inputs/ folder)
python experiments/T061-20261104-opencode-interaction-writer/make_evidence.py --label before --out inputs
# after
python experiments/T061-20261104-opencode-interaction-writer/make_evidence.py --label after  --out artifacts
python experiments/T061-20261104-opencode-interaction-writer/verify_powerpoint.py
python -m unittest discover -s tests -v
python lab/tools/check_layout.py
```

`make_evidence.py` does four things and writes one JSON/XML per item:

1. Writes one interactive trigger onto a minimal slide with the trigger shape
   carrying an `<a:hlinkClick>`; serialises the `p:timing` tree.
2. Calls `advanced_interactivity.build_canonical_interactive_seq(...)` and
   hashes the pretty-printed subtree.
3. Rebuilds the two T048 decks into a temporary directory with the committed
   `make_artifacts.py` and compares every zip member with the committed deck,
   excluding `docProps/*` (build timestamp). The zip container itself is not
   compared.
4. Re-reads the committed T049 deck with `inspect_interactivity` and compares
   sequence counts and per-sequence trigger/animated spids with the stored
   audit.

`artifacts/DELTA.md` is generated from `inputs/summary.json` by the `after`
run, so the diff table cannot drift from the measured values.

**What moved.**

| Before | After |
|---|---|
| `pptx_animator._interactive_sequence` (seq shell without `stCondLst`/`endSync`, child at `indefinite`) | `pptx_animator` "Interactive triggers" section: `interactive_sequences`, `sequence_trigger_spid`, `shape_trigger_spids`, `_interactive_sequence` (canonical shell), `strip_click_hyperlinks`, `set_click_action`, `InteractionConflict`, `apply_interactive_actions`, `read_interactive_actions`, `interactive_summary`, `build_interactive_sequence`, `max_ctn_id` |
| `interactive_triggers.py` — 833 lines, own `p:seq` builder, non-schema `customAction/customPreset/customDur`, one seq per plan item | 139 lines: plan vocabulary + name resolution; calls `apply_interactive_actions` / `read_interactive_actions` |
| `advanced_interactivity.py` — own `build_canonical_interactive_seq` body and own parser | `build_canonical_interactive_seq` delegates to `build_interactive_sequence`; `inspect_interactivity` uses `interactive_summary`; COM game builder and WAV synthesis stay |
| `slide_navigator.py` — `ET.SubElement(cnvpr, a:hlinkClick, …)` in three branches | one call to `set_click_action` per branch, trigger shapes reported in `conflicts` instead of being wired into a dead button |

`advanced_interactivity.compile_one_slide_games_suite` still lets PowerPoint
COM write the timing. That is the target application writing its own file, not
a fourth writer; the code only issues COM commands.

## Evidence

### Acceptance

| Claim | Rung | Evidence |
|---|---|---|
| T048b decks rebuild byte-identically (43 zip members each, `docProps/*` excluded) | 1 | `artifacts/t048_rebuild.json` — `different_members: []` for both decks; same run at base (`inputs/`) also 0 |
| T048b navigation parse counts unchanged (11 edges game, 8 edges hub) | 1 + 4 | `tests/test_interaction_writer.py::CommittedArtifactTests::test_t048b_navigation_parse_counts`; T048's own rung-4 COM claims stand |
| T049 artifact unchanged and parses to 8 sequences (4 + 4) | 1 + 4 | `artifacts/t049_artifact.json`, `stored_counts_match: true`; file hash unchanged `f91531f8…` |
| T049 per-sequence animated spids now include self-triggered effects | 1 | before `[0,0,0,3,1,1,1,3]`, after `[1,1,1,3,1,1,1,3]` (`artifacts/DELTA.md`) |
| Canonical reader recovers the timings PowerPoint COM authored in T049 | 4 + 1 | 3×hide/zoom/350 ms + reveal/zoom/300 ms (slide 1), 3×reveal/fade/250 ms + hide/fade/200 ms (slide 2); pinned by `test_t049_native_timings_read_back`; matches the T049 report's 0.35/0.30/0.25/0.20 s |
| `build_canonical_interactive_seq` output byte-identical | 1 | `inputs/canonical_seq.sha256` = `artifacts/canonical_seq.sha256` = `d1f76b7b…`; pinned by `test_canonical_builder_is_byte_stable` |
| PowerPoint 16.0 COM parses the canonical subtree as 1 interactive sequence, trigger "Inspect Button", target "Detail Panel", effect 48, 0.5 s | 4 | `artifacts/powerpoint_parse.json` (`canonical.parsed`) |
| Only `pptx_animator.py` constructs `nodeType="interactiveSeq"`; the three callers import it | 1 | `test_only_pptx_animator_builds_interactive_seq`, `test_former_writers_import_the_canonical_module` (AST scan of `scripts/*.py`) |
| Full suite | 1 | 476 tests, 8 skipped, OK (base 461 + 15 new) |

### The documented diff (T049 findings)

`artifacts/DELTA.md` carries the unified diff. Summary:

| Aspect | Before | After |
|---|---|---|
| interactiveSeq `cTn` attributes | `id, dur="indefinite", restart, fill, evtFilter, nodeType` | `id, restart, fill, evtFilter, nodeType` (no `dur`, as COM writes it) |
| start condition | none on the seq `cTn` | `<p:stCondLst><p:cond evt="onClick"><p:tgtEl><p:spTgt spid="10"/>` |
| end | none | `<p:endSync evt="end"><p:rtn val="all"/>` |
| click step | `delay="indefinite"` + `onBegin`/`tn` indirection | `delay="0"` |
| trigger shape hyperlink | kept (`<a:hlinkClick>` swallows the click) | stripped, `hyperlinks_stripped: 1` in the receipt |
| one shape, one trigger | a second call appended a second `p:seq` for the same shape | reuses the existing sequence |
| T033 plan metadata | `customAction`, `customPreset`, `customDur` (not in ECMA-376) | not written; reader infers from `presetClass`/`presetID` |
| toggle | two click steps, one seq | unchanged semantics, now through the same writer |

### Why PowerPoint parse counts are not the proof of the fix

`verify_powerpoint.py` builds a second deck that reproduces the *pre-T061*
subtree (no onClick on the seq `cTn`, click step at `indefinite`). COM reports
the same thing for both:

```
canonical: 1 interactive sequence, trigger "Inspect Button", target "Detail Panel", effect 48, 0.5 s
pre-T061 : 1 interactive sequence, trigger "Inspect Button", target "Detail Panel", effect 48, 0.5 s
```

So the T049 1.3 diagnosis ("the old child delay makes PowerPoint wait") cannot
be confirmed or refuted by a parse count. The new shape matches COM's own
output and the structural argument holds, but the behavioural claim still
needs the T058 click harness. This refines the T057 finding: the T049 claim
"100% working" is rung 4 at most, and rung 4 does not separate the two shapes.

## Negative results and limitations

1. **Parse counts cannot verify playback.** Both the canonical and the
   pre-T061 subtree parse identically in COM (above). The fix is justified by
   COM's own authored shape plus the T049 diagnosis, not by a passing click.
2. **Two effect-body paths remain inside the one module.** `_behaviours` writes
   main-sequence effects from the preset library; `build_interactive_sequence`
   still mirrors COM's narrow zoom/fade body byte-for-byte. They live in one
   file but are not one function. Unifying them changes the T049 builder output
   and was deferred until playback evidence exists — the byte freeze is the
   honest option for now.
3. **The T033 semantic vocabulary is lossy.** `read_interactive_actions` infers
   the preset from `presetID`: emphasis zoom and grow are both preset 6, and an
   entrance "teeter" collapses to fade. The four combinations covered by the
   T033 test round-trip exactly; the other eight in the old `PRESET_METADATA`
   table do not. Documented in `_ACTION_EFFECT` / `_PRESET_BY_ID`.
4. **`inspect_interactivity` output changed for self-triggered sequences.** It
   used `list(set(...))`, so `animated_spids` was unordered and *empty* whenever
   the trigger animated itself (the T049 chests). The stored T049 audit is
   therefore not reproducible run-to-run; the canonical reader fixes both
   (effect order, trigger included). Sequence counts are unchanged.
5. **T048 conflict guard is untested against a real recipe.** No committed T048
   deck puts a hyperlink on a trigger shape, so the skip path only has the unit
   test. It is a guard, not exercised production behaviour.
6. **No visual evidence.** Slide content is untouched and the T048 decks
   rebuild member-identically, so a render would repeat T048's previews. This is
   inference, not a fresh rung-3 render.
7. **`docs/CHANGELOG.md` tail is mojibake** (T065 scope). The T061 entry is at
   the top in UTF-8; the damaged legacy tail was not touched.
8. **PowerPoint COM is flaky under repeated dispatch.** Three of six
   full-suite runs failed `test_compile_one_slide_games_suite` with
   `RPC server is unavailable` / an OLE exception after several
   `Dispatch`/`Quit` cycles, and passed on the next run with no code change.
   This is environmental, but it matters to T058: a click harness must own one
   PowerPoint instance and must not let a crashed instance poison the next
   test. The final passing run was `476 tests, 8 skipped, OK`.

## Next

1. **T058** (interactive slide-show harness): click the T049 chests/quiz, the
   T048 hub buttons and `artifacts/t061_trigger_probe.pptx`, then compare with
   `t061_trigger_probe_pre_t061.pptx`. That is the only way to promote the
   T049 delay finding above rung 4.
2. **Follow-up after T058:** fold `build_interactive_sequence` into
   `_effect_par`/`_behaviours` and delete the COM-mirror path; keep the frozen
   hash test only until then.
3. **T063-adjacent:** the T033 vocabulary (`interactive_triggers.py`) is still
   labelled EXPERIMENTAL. If a product path wants declarative triggers, promote
   `apply_interactive_actions` (in `pptx_animator`) and retire the T033 module
   rather than keeping the shim forever.
4. **Review:** an independent critic (Claude, per the T057 table) should try the
   falsifiers itself: rebuild T048, re-read T049, run the COM probe, and inspect
   the AST test for loopholes.

## Review response

Pending independent review.
