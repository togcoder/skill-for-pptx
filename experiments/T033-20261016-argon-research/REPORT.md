# T033 — Argon's second research drop: evaluation (written in T034, 2026-10-19)

## Input

On 2026-10-16 the owner integrated three answers from Argon, a Gemini
research agent. The verbatim answers are in this folder:
`ARGON_T033_FULL_RESPONSE.md`, `ARGON_TASK2_3_RESPONSE.md` and
`ARGON_TASK3_AND_TESTS_RESPONSE.md`. The resulting code arrived in two
commits on `work/T033-argon-morph-staging`:

- `8217d99`: `scripts/morph_playbook.py` rewritten (extract_objects with
  group transforms, alpha, `stage_cross_slide_morph_twins` with 7 staging
  modes, arc-length resampling, custom geometry), plus
  `tests/test_morph_playbook.py`;
- `d57f4a1`: `scripts/interactive_triggers.py` (semantic trigger API) and
  `scripts/cognitive_pacing.py` (motion budget, "FINST" limit, "WDI",
  cinematic pacing), plus `tests/test_interactive_and_pacing.py`.

At the time the commit message said 274 tests pass. There was no REPORT,
claim, STATUS or HANDOFF entry; this report fills that gap. It follows T032's
evaluation format.

## How it was evaluated

- **Audit.** A read-only audit agent in session T034 ran each module on the
  repository fixtures and on a `motion_director auto` output. It checked the
  XML against ISO/IEC 29500-4 `pml.xsd` (lxml 6.1.3) and opened the files in
  LibreOffice 24.2. LibreOffice opening a file proves nothing about
  PowerPoint.
- **Reproduction.** One finding was reproduced independently: a
  `cognitive_pacing`-paced slide fails the schema on 9 `customDur`
  attributes, and the director's output for the same slide validates.

## Verdict per module

| Module | Verdict | Reasons |
|---|---|---|
| `morph_playbook.py` | **Quarantined (experimental)** | **Parser.** It uses the standard-library parser, so its `isinstance` checks fail on the product's lxml trees and its audit passes with 0 objects. **Objects.** It skips placeholders without their own `xfrm` (0 objects where `deck_model` finds 2) and ignores group rotation and flip. **Morph.** It renames only the source slide's shape, which breaks existing Morph pairs. `morph_studio.rename_chain` renames the whole chain. It never writes a Morph transition. **Staging clones.** Post-stage clones cascade onto later slides. Clones keep the source `r:embed`, which leaves a dangling rel; `_stage_copy` remaps it. **Schema.** A `noFill` shape gets a second `solidFill`, and `alphaModFix` is placed after `a:extLst`. Both are schema-invalid. **Other.** It appends after `spTree/extLst` and assumes a 16:9 slide. |
| `cognitive_pacing.py` | **Quarantined (experimental)** | **Schema.** It writes `customDur`, which is outside ISO 29500; the schema check fails, as reproduced. **Preserve rule.** It overwrites every effect's duration and easing, breaking the preserve-timing rule, and does not move the visibility `set`: an exit that becomes longer still hides at its old time. **Counting.** The stagger counter is global across clicks. "Simultaneous" counts the whole slide, not a click. The scale parser never matches real XML. Every `!!` object counts as moving, even on a static slide. **Library mismatch.** It raises a TypeError on lxml input. **Sources.** Its constants (2.5 ceiling, exp(−0.45), 0.35/0.20 weights, 65·k^0.85 ms) have none. **Naming.** It names a profile "cinematic" that collides with the director style. |
| `interactive_triggers.py` | **Not adopted.** `pptx_animator.apply_timeline(trigger_spid)` stays canonical | **Invalid XML.** Made-up `customAction/customPreset/customDur` attributes, and the tests round-trip through them. Invalid `p:from/p:by` children on scale and rotate. An empty `mainSeq` `childTnLst`. **Wrong presets.** Teeter is written as Blast (14), the error T032 had already corrected to 32. **Validation.** It accepts a missing trigger shape. **User content.** It deletes the user's `hlinkClick` and `hlinkHover`, citing no evidence. |

## What is worth keeping

- **Research basis for the motion budget.** About four objects can be
  tracked at once (Pylyshyn & Storm 1988, FINST), and capacity varies with
  speed and spacing (Alvarez & Franconeri 2007). This is now rule
  **MOT-MOVERS** in `knowledge/design_system.json`. `design_critic.py`
  measures it per click, counting objects that move along one path once.
- **Staging modes.** `portal-seed`, `telescopic-stack` and `corner-badge`
  could become extra `morph_studio._stage_copy` modes after a PowerPoint
  render.
- **Trigger start condition.** An `onClick` start condition on the
  `interactiveSeq` may match how PowerPoint saves triggers. Compare it with a
  PowerPoint-saved file before porting it to `pptx_animator`.

## What changed in T034

- **Headers.** Each of the three modules starts with an EXPERIMENTAL header
  that names its findings and the canonical module.
- **Isolation.** `tests/test_design_system.py` fails if a product path
  imports any of them.
- **Skill claim removed.** The director skill no longer claims that director
  plans accept `transition.pre_stage/post_stage`; nothing reads those keys.
- **Tests unchanged.** The modules' own tests are kept, so the code still
  runs. They are circular, testing the modules' own formulas and made-up
  attributes, so they are not evidence of correctness.

Native playback: null. Nothing in this drop was rendered or played in
PowerPoint.
