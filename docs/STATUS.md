> **Since T040 this page is the pptx domain's status.** Lab-wide state lives in
> `HANDOFF.md` and `domains/README.md`; how agents work is in `lab/PROTOCOL.md`.

# Status — current state (2026-11-04, after T058–T068)

This page is rewritten, not appended. History is in [CHANGELOG.md](CHANGELOG.md),
task IDs in [research/tasks/INDEX.md](../research/tasks/INDEX.md), and the
evidence vocabulary in [VERIFICATION.md](VERIFICATION.md). The lead review and
the briefs: [T057](../experiments/T057-20261104-claude-leader-review/REPORT.md).

## Where the code is

- **`main`**: **556 tests pass, 6 skipped**, with and without `PYTHONUTF8=1`
  (Windows Vietnamese, cp1258). `python lab/tools/check_layout.py` OK.
- **Merged programme:** T058 (interactive harness), T059 (DeckCraft fidelity),
  T060 (DeckCraft source study), T061 (canonical interaction writer), T062
  (native asset factory), T063 (Forge debt), T064 (T055 rebase + 3D Morph),
  T065 (lab hygiene), T066 (Chapter 1 deck, owner review), T067 (deck direction
  research, image choreography, `VisualStyle/1`), T068 (Deck Director compiler
  and narrative laws).
- **Unmerged:** `work/T054-opencode-vector-match` (vector only).
- **T055** is on `main` as **EXPERIMENTAL**: rebased by T064, review
  `accept-with-fixes`, R3/R4/R6/R7/R8 open.
- **No product path uses DeckCraft as the last writer.** T059 proved `convert`
  drops 149 behaviours; T062 uses DeckCraft only to build native assets.

## Product paths

| Path | Entry point | For | Skill / command |
|---|---|---|---|
| Deck Director | `scripts/deck_director.py` (`check → compile → ledger`) | New decks: direction file, two-pass screenplay, base state and object lifecycle | `skills/deck-director` |
| Motion Director | `scripts/motion_director.py` (`inspect → draft → apply/auto → preview → verify → critique`) | Existing decks: script-driven click rhythm, compound and layered motion, preserving the source | `skills/pptx-motion-director`, `/animate-deck` |
| Morph Studio | `scripts/morph_studio.py` (`propose → apply → preview`) | Cross-slide Morph: `!!` continuity, fly-in staging, camera, card expand, pan | same skill |
| Slide Forge | `scripts/slide_forge.py` (`schema → build → qa → render`) | New decks from a semantic spec: layout, type, themes, assets, motion | `skills/slide-forge`, `/forge-deck` |
| Interaction writer | `scripts/pptx_animator.py` | The one writer for `interactiveSeq`, triggers, click-hyperlink conflicts (T061) | — |
| Interactive harness | `scripts/interactive_show_harness.py` | Win32 click + capture in a windowed PowerPoint show; rung 5b (T058) | — |
| Design system + critic | `knowledge/design_system.json`, `scripts/design_critic.py` | One set of numbers for generating and judging beauty and technique | `docs/DESIGN_SYSTEM.md` |
| DeckCraft asset compiler | `experiments/T062-*/inputs/` | Native, part-editable PPTX art; EXPERIMENTAL, not wired into Forge | — |

The north star is unchanged: an AI Motion Director for existing decks
([PRODUCT_TARGET.md](PRODUCT_TARGET.md)). Forge is the second entry mode.

## Capability × evidence

The evidence ladder is defined in [VERIFICATION.md](VERIFICATION.md). Columns:
**Struct** (tests/XML), **Sim** (simulator/renderer), **PPT-parse** (COM reads the
exact file), **PPT-play** (COM drives/playback with machine assertions),
**Human** (a person reviewed the captures).

| Capability | Struct | Sim | PPT-parse | PPT-play | Human |
|---|---|---|---|---|---|
| Timing writer, click groups, after-previous, triggers | ✓ | ✓ | ✓ | ✓ T058 (click) | – |
| Canonical interaction writer (T061) | ✓ 500+ tests | – | ✓ T048b/T049 | ✓ T058 after T061 | – |
| Interactive mini-games/hubs (T048b/T049) | ✓ | – | ✓ | ✓ 25/25 steps, 9/9 edges | – |
| Forge type scale + MOT-SETTLE + count-ups (T063) | ✓ | ✓ | ✓ PDF/PNG | ✓ CreateVideo frames | – |
| 3D camera Morph (T064) | ✓ | – | ✓ | ✓ CreateVideo frames | – |
| DeckCraft static render (T059) | ✓ | ✓ | ✓ labelled fallback | – | – |
| DeckCraft Morph/round trip (T059) | ✓ | – | ✓ | **fails** as PowerPoint proxy | – |
| Lab hygiene: UTF-8/check_layout/CI (T065) | ✓ both locales | – | – | – | – |

“–” means no evidence. **Rung 6 has not been reached for any deck.** T058 reaches
5b: the harness asserts pixels, but no human reviewed every capture.

## Open problems (ranked)

1. **T055 fixes.** Review `accept-with-fixes`; R3 (claim “camera views + Morph” is
   not true of the original deck), R4/R6/R7/R8 open. The 3D deck is experimental.
2. **Template contract + generic patch.** T057 named this as the biggest gap:
   `CxyZyr/PPTX-Template-Skills`, `pptx-style`, `OfficeCLI`, `hands-on-deck`.
   The lab can generate new decks but cannot ingest an arbitrary brand deck or
   patch one byte-safely yet.
3. **Rung 6 / human review.** T058’s captures need a human pass; T063’s PDF and
   T064’s Morph frames need the same.
4. **4:3 / 40 slide / missing font.** 57/57 tracked decks are 16:9, ≤12 slides;
   `slide_forge.py` hard-codes 16:9.
5. **Design context.** Minimum type by viewing angle, WCAG AA + room lift, 134
   Vietnamese codepoints, `fontScale`; not yet a checker.
6. **DeckCraft dependency.** T060 prototype is not upstream; T059/T062 are
   experiments, not product paths.
7. **Repo weight.** T055/T059 added several MB; size cap warns only; Git LFS is
   an open owner decision.

## Experimental (not used by any product path)

- `scripts/interactive_show_harness.py` — Windows interactive desktop only.
- `scripts/deckcraft_fidelity.py` — fallback proposal, not wired.
- `experiments/T062-*/inputs/` — native asset compiler, not wired.
- T055 native 3D — on `main`, experimental, review fixes open.
- `morph_playbook.py`, `cognitive_pacing.py` — still quarantined.

## Next

1. Fix T055 R3/R4/R6/R7/R8; then decide whether it enters a product path.
2. Build the template contract + byte-safe patch layer (T067+).
3. Add 4:3/40-slide/missing-font/Vietnamese fixtures.
4. Turn the design-context rules into a checker.
5. Run one human review of T058/T063/T064 captures (rung 6).
