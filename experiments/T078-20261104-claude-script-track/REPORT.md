# T078 [pptx] Script track: diagnosis, method and the first gold script

- **Agent / model:** Claude (Opus 5.5), lead, desktop session. **Date:** 2026-11-04.
- **Branch:** `work/T070-claude-lead-synthesis` (same PR as T070, because it corrects T070's
  roadmap).
- **Request (owner, 2026-11-04):** "My motion thinking is driven by the script. The script
  skill the agents made is too weak, or the agents are. I worry weak models cannot do this
  part. Can you help them, or does this part need its own direction?"

## Frame

- **Question:** why are agent-written scripts weak? How much of script writing can a weak model
  do with help? What should the script track research?
- **Hypothesis:**
  - Motion quality is set upstream by the script: motion is the story's verb, and Morph is one
    idea changing state.
  - The current skill teaches a form and prohibitions, not a way of thinking, and has no
    worked example.
  - Weak models can follow forms, libraries and examples. They are unreliable at judging intent
    and quality, which should be left to the owner or a strong model reading the script as text
    before anything is built.
- **Falsifiers:**
  - the owner judges the gold script no better than the T069a beat sheet;
  - T079 shows a weak model with the method matches a strong model without it, in which case
    no division of labour is needed.

## What was produced

- `docs/SCRIPT_TRACK.md`: a living direction for the script track. It holds:
  - the diagnosis (6 points);
  - a table of which script tasks a weak model can do;
  - a 6-step method;
  - a library of 8 narrative frames;
  - a **verb → motion table** (18 rows, hypotheses);
  - reserved briefs T079–T082.
- `gold-script-triet-hoc-ch1.md`: a full 13-scene gold script for the deck the owner already
  knows (T066/T069a). It covers:
  - intent;
  - a persistent metaphor (the lens) that becomes the Morph actor;
  - a 6-cell sheet per scene;
  - a motion map derived from the verbs;
  - a side-by-side comparison with T069a.

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| The skill teaches forms and prohibitions | `skills/deck-director/SKILL.md`: brief fields, 9 jobs, 5 prohibitive laws, checker. It has no audience-belief step, no frame library and no worked example. | 1 |
| The T069a script starts from the textbook outline and restates definitions | `experiments/T069-…/beat-sheet.md`: slide order follows the chapter headings; the spoken lines restate slide text ("Triết học là hệ thống tri thức…") | 1 |
| The gold script derives motion from verbs | Motion map in the gold script: 13 scenes, 11 verbs, about 6 reused motion types | 1 (text) |
| The gold script is better | **Not shown.** It needs the owner's reading (feedback item F9) and later the bench | — |

## Limits

- The gold script has not been built. Some moves (the 180° flip, the camera pan along the
  timeline) need T074/T076 evidence before they are promised.
- The content follows the national textbook's Chapter 1 from memory and must be proofread by
  someone who teaches the subject. Two facts are flagged in the script itself.
- The verb table is a hypothesis until T080.
