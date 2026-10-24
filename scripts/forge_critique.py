#!/usr/bin/env python3
"""Compatibility entry point for the T031 critique (superseded in T034).

T031 (WIP) scored PPTEval-style dimensions from measurements. Its checks were
folded into ``design_critic.py``, which grades every measurement against the
shared design system (``knowledge/design_system.json``) that the generators
also read:

    T031 code        -> design_critic rule
    WORDY            -> DEN-WORDS
    TYPE_LEVELS      -> TYP-SIZES (deck scale, inherited sizes resolved)
    DENSITY/BALANCE  -> LAY-DENSITY / LAY-BALANCE (settled frame, --render)
    CLICK_FATIGUE    -> MOT-CLICKS
    BUSY_CLICK       -> MOT-EFFECTS / MOT-MOVERS
    STATIC_DECK      -> MOT-STATIC
    MONOTONE/CHAOTIC -> MOT-VOCAB
    FONTS            -> TYP-FAMILIES

    forge_critique.py deck.pptx [--render DIR|lo]
"""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import design_critic  # noqa: E402

critique=design_critic.critique

if __name__=="__main__":
    design_critic.main()
