# Verification: one evidence ladder

Every claim about motion names the highest rung it reached. Never describe a
lower rung as a higher one. In particular, XML checks, LibreOffice output,
storyboards and GIF previews are not PowerPoint playback (AGENTS.md).

| Rung | Name in reports | What it shows | What it does not show | Tool |
|---|---|---|---|---|
| 0 | planned | A plan passes its validator (`validate_director_plan`, Forge schema) | That a file exists | validators |
| 1 | structural | ZIP/XML well-formed, our invariants hold (source preserved, timing tree shape, no overlapping moves), optionally ISO 29500 schema-valid | That PowerPoint opens it without repair | `motion_director.verify`, `morph_studio.verify_scenes`, `forge_qa`, `design_critic --xsd` |
| 2 | simulated | The engine's own state model plays the timing (stable states, GIF previews, simulated Morph) | PowerPoint's interpretation of paths, easing or Morph pairing | `motion_director preview`, `morph_studio preview` |
| 3 | LibreOffice | An independent importer reads the effects and sequencing (`lo_timing_crosscheck`), and LibreOffice renders the static slides | PowerPoint behaviour: LibreOffice has no Morph and plays a subset of effects | `lo_timing_crosscheck.py`, `design_critic --render lo` |
| 4 | PowerPoint-parsed | PowerPoint opened the exact file (hash recorded) and listed its MainSequence: EffectType, timing, repeat | That the effects look right when played | `scripts/powerpoint_render.ps1`, `powerpoint_native_probe.ps1` |
| 5 | PowerPoint-rendered | PowerPoint's `CreateVideo` rendered the deck. Clicks advance automatically, so motion and transitions can be inspected frame by frame | Presenter-paced click behaviour, shape-click triggers, Presenter View | `scripts/powerpoint_render.ps1`, `slide_forge.py render` |
| 6 | interactive playback | A person or a COM driver played the slideshow click by click and the captures were reviewed | Other PowerPoint versions or operating systems | `docs/POWERPOINT_NATIVE_HARNESS.md` checklist |

Rungs 4–5 have been reached for parts of the system (see
[STATUS.md](STATUS.md)). Rung 6 has not been reached for any deck.

Reports use `"powerpoint_playback_verified": false` until rung 6, and they
name the rung that was reached. The design critic's scores are measurements
on rungs 1–3 (or 5 with PowerPoint render strips). They are not playback
evidence.

## Rung 3 vs rung 5 for layout metrics

On the T025 Forge coffee deck (10 slides), the critic compared the settled
frame of each PowerPoint CreateVideo strip with LibreOffice's static render
(T034):

| Metric | Median difference | Spearman |
|---|---|---|
| Background share | 0.022 | 0.99 |
| Balance | 0.014 | 0.88 |
| Colourfulness | 0.9 | 0.92 |

LibreOffice is good enough for *layout* metrics in a cloud session. It says
nothing about motion.

## Running a native session (rungs 4–6)

1. Record the SHA-256 of the exact PPTX, the OS, the PowerPoint build, the
   fonts and the screen size.
2. **Rungs 4–5:** run
   `powershell -File scripts/powerpoint_render.ps1 -Pptx deck.pptx -OutDir render/`.
   Keep `native_sequence.json` and the per-slide strips. `slide_forge.py render`
   wraps the same script.
3. **Rung 6:** follow `docs/POWERPOINT_NATIVE_HARNESS.md`:
   - freeze a manifest (`make_powerpoint_qa_manifest.py`);
   - probe click by click (`powerpoint_native_probe.ps1`);
   - verify the record (`verify_powerpoint_qa.py`).

   The harness checks click indices. Visual completion still needs a human
   to review the captures.
4. **Checklist when playing:**
   - Any repair prompt?
   - Does the Animation Pane show named effects, not "Custom"?
   - Are objects hidden before their click?
   - Do after-previous steps run in sequence?
   - Is easing visible?
   - Does Morph pair `!!` names along chains, with leaving objects behind or in front?
   - Do objects snap back at the start of Morph (MOT-SETTLE)?
   - Are generated helpers visible on dark themes?
5. Save the file once in PowerPoint and diff its timing XML with ours. Any
   normalisation PowerPoint applies is the next writer fix.

Report template:

```json
{"task": "T0xx", "pptx_sha256": "…", "application": "PowerPoint", "version": "16.0.x", "os": "…",
 "rung": 5, "structure_checked": true, "powerpoint_parsed": true, "powerpoint_rendered": true,
 "powerpoint_playback_verified": false, "repair_warning": "none|…", "evidence_files": ["…"],
 "observations": ["…"], "limitations": ["…"]}
```

The older four-level scheme (`planned`, `structure_checked`,
`layout_reviewed`, `playback_verified`) is archived in
[archive/POWERPOINT_QA.md](archive/POWERPOINT_QA.md). It maps to rungs 0, 1,
3 and 6.
