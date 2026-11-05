#!/usr/bin/env python3
"""Build blind A/B pairs for Cảnh 6 (Margin) and Cảnh 8 (Pillars) to test Morph vs Non-Morph."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

import pptx_animator as anim
import build_pitch_deck as bpd

OUT_DIR = ROOT / "experiments" / "T081-20261105-antigravity-script-writer" / "artifacts" / "pairs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_pair_margin():
    # Pair A: Standard Cut Transition between State 6A and 6B
    prs_a = Presentation()
    prs_a.slide_width, prs_a.slide_height = Inches(13.333), Inches(7.5)
    blank = prs_a.slide_layouts[6]
    
    # 6A
    s1 = prs_a.slides.add_slide(blank); bpd.set_bg(s1)
    bpd.add_header(s1, "Test Pair 1A", "UNIT ECONOMICS: 65% GPU COST VS MARGIN (CUT TRANSITION)")
    bpd.add_round_rect(s1, "col_gpu", 0.8, 2.6, 3.6, 3.8, fill_col=RGBColor(45, 20, 20), border_col=bpd.RED)
    bpd.add_round_rect(s1, "col_margin", 4.8, 2.6, 3.6, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.BORDER_COL)
    bpd.add_round_rect(s1, "col_cac", 8.8, 2.6, 3.6, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.BORDER_COL)

    # 6B (no morph, normal cut/fade)
    s2 = prs_a.slides.add_slide(blank); bpd.set_bg(s2)
    bpd.add_header(s2, "Test Pair 1A", "UNIT ECONOMICS: 82% GROSS MARGIN (CUT TRANSITION)")
    bpd.add_round_rect(s2, "col_gpu", 0.8, 5.2, 3.6, 1.2, fill_col=RGBColor(30, 25, 25), border_col=bpd.BORDER_COL)
    bpd.add_round_rect(s2, "col_margin", 4.6, 1.8, 4.0, 4.6, fill_col=RGBColor(6, 78, 59), border_col=bpd.EMERALD)
    bpd.add_round_rect(s2, "col_cac", 9.0, 2.6, 3.5, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.GOLD)

    out_a = OUT_DIR / "pair-01-margin-cut.pptx"
    prs_a.save(out_a)

    # Pair B: Morph Transition (State-to-State geometric resize)
    prs_b = Presentation()
    prs_b.slide_width, prs_b.slide_height = Inches(13.333), Inches(7.5)
    
    # 6A with !!ids
    sb1 = prs_b.slides.add_slide(blank); bpd.set_bg(sb1)
    bpd.add_header(sb1, "Test Pair 1B", "UNIT ECONOMICS: 65% GPU COST VS MARGIN (MORPH TRANSITION)")
    bpd.add_round_rect(sb1, "!!col_gpu", 0.8, 2.6, 3.6, 3.8, fill_col=RGBColor(45, 20, 20), border_col=bpd.RED)
    bpd.add_round_rect(sb1, "!!col_margin", 4.8, 2.6, 3.6, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.BORDER_COL)
    bpd.add_3rings(sb1, 6.6, 3.3, 0.45, 0.32, 0.20, exec_col=bpd.EMERALD, radius=0.5)
    bpd.add_round_rect(sb1, "!!col_cac", 8.8, 2.6, 3.6, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.BORDER_COL)

    # 6B with !!ids and Morph
    sb2 = prs_b.slides.add_slide(blank); bpd.set_bg(sb2)
    bpd.add_header(sb2, "Test Pair 1B", "UNIT ECONOMICS: 82% GROSS MARGIN (MORPH TRANSITION)")
    bpd.add_round_rect(sb2, "!!col_gpu", 0.8, 5.2, 3.6, 1.2, fill_col=RGBColor(30, 25, 25), border_col=bpd.BORDER_COL)
    bpd.add_round_rect(sb2, "!!col_margin", 4.6, 1.8, 4.0, 4.6, fill_col=RGBColor(6, 78, 59), border_col=bpd.EMERALD)
    bpd.add_3rings(sb2, 6.6, 2.5, 0.55, 0.40, 0.25, exec_col=bpd.EMERALD, radius=0.5)
    bpd.add_round_rect(sb2, "!!col_cac", 9.0, 2.6, 3.5, 3.8, fill_col=bpd.CARD_BG, border_col=bpd.GOLD)

    anim.add_morph_transition(sb2._element, duration_ms=1200)

    out_b = OUT_DIR / "pair-01-margin-morph.pptx"
    prs_b.save(out_b)
    print("Generated margin pair A and B")


if __name__ == "__main__":
    build_pair_margin()
