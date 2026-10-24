---
description: Add presenter-paced native animation to an existing PowerPoint deck
argument-hint: <deck.pptx> [goal / style]
---

Use the `pptx-motion-director` skill to motion-direct this deck: $ARGUMENTS

Work autonomously: find or write the presentation script first (a script the
user gave or pasted, speaker notes, or your own full narration drafted with
`motion_script.py draft` and rewritten), then inspect the deck, let the script
drive the clicks (`auto --script`), refine the choreography and motion layers
yourself, apply it to a new output file next to the
source (never overwrite the source), render the storyboard if LibreOffice is
available and look at it, then report the output path, the per-slide click
plan, and the honest verification status (not yet played in PowerPoint).
Ask the user only if a factual or permission question truly blocks the work.
