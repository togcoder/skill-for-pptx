"""Generate the 4 canonical Before/After PPTX test pairs for T086.

Pair 1: Collision & Safe Zone (Slide 2 defect from user screenshot)
- 01A_collision_before.pptx: Text at x=0.8" collides directly with emblem rings at xc=1.1".
- 01B_safezone_after.pptx: Text indented to x=2.35" with clean 0.35" safe-zone clearance.

Pair 2: Column Measure & Text-Fit (Slide 3 defect from user screenshot)
- 02A_pinched_before.pptx: 3 narrow columns (w=3.1", gap=0.5"), 18pt text wrapping 2 words/line.
- 02B_measure_after.pptx: 12-column grid 2-column split (Span 6+6, w=5.74", gap=0.25"), 5.14" text width with optimal 48-52ch measure.

Pair 3: Ghost Card vs. Clean Elevation (R10 & R11)
- 03A_ghostcard_before.pptx: Card with 2pt blue border + harsh black shadow + mismatched nested radii.
- 03B_elevation_after.pptx: Soft diffused ambient shadow (blurRad=200000, alpha=10000), concentric corner radii in EMUs.

Pair 4: Morph Shape & Velocity Discipline (R01, R02, R03)
- 04A_morph_deformed_before.pptx: Ellipse to roundRect cross-fade, text warped inside morphing shape.
- 04B_morph_clean_after.pptx: roundRect (cx==cy) to roundRect card, decoupled text fade, native Morph transition.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so we can import scripts.pptx_animator
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

from scripts import pptx_animator as anim

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "pairs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Theme Colors (Dark Slate Executive Palette)
DARK_BG = RGBColor(15, 23, 42)      # Slate 900 #0f172a
CARD_BG = RGBColor(30, 41, 59)      # Slate 800 #1e293b
CARD_BORDER = RGBColor(51, 65, 85)  # Slate 700 #334155
CYAN = RGBColor(6, 182, 212)        # Cyan 500 #06b6d4
PURPLE = RGBColor(168, 85, 247)     # Purple 500 #a855f7
ORANGE = RGBColor(249, 115, 22)     # Orange 500 #f97316
TEXT_WHITE = RGBColor(248, 250, 252)# Slate 50
TEXT_MUTED = RGBColor(148, 163, 184)# Slate 400


def create_base_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    return prs


def add_dark_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.500))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.fill.background()
    return bg


def set_shape_shadow(shape, blur_rad: int, dist: int, dir_angle: int, alpha_val: int):
    """Set outer shadow on a shape adhering strictly to DrawingML element sequence."""
    spPr = shape._element.spPr
    effectLst = spPr.get_or_add_effectLst()
    # Clear existing children
    for child in list(effectLst):
        effectLst.remove(child)
    shdw_xml = parse_xml(
        f'<a:outerShdw xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        f'blurRad="{blur_rad}" dist="{dist}" dir="{dir_angle}" algn="b" rotWithShape="0">'
        f'<a:srgbClr val="000000"><a:alpha val="{alpha_val}"/></a:srgbClr>'
        f'</a:outerShdw>'
    )
    effectLst.append(shdw_xml)


# ==============================================================================
# PAIR 1: Collision & Safe Zone (Slide 2 Problem)
# ==============================================================================

def build_pair_01():
    # 01A: Collision (Before)
    prs_a = create_base_deck()
    slide_a = prs_a.slides.add_slide(prs_a.slide_layouts[6])
    add_dark_background(slide_a)

    # Emblem rings at xc=1.1, yc=3.75
    # Outer cyan ring (d=1.8"), middle purple (d=1.3"), inner orange (d=0.8")
    xc, yc = Inches(1.1), Inches(3.75)
    r1 = slide_a.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.9), yc - Inches(0.9), Inches(1.8), Inches(1.8))
    r1.fill.background()
    r1.line.color.rgb = CYAN
    r1.line.width = Pt(3)

    r2 = slide_a.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.65), yc - Inches(0.65), Inches(1.3), Inches(1.3))
    r2.fill.background()
    r2.line.color.rgb = PURPLE
    r2.line.width = Pt(3)

    r3 = slide_a.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.4), yc - Inches(0.4), Inches(0.8), Inches(0.8))
    r3.fill.background()
    r3.line.color.rgb = ORANGE
    r3.line.width = Pt(3)

    # Collision Text starting at x=0.8" (directly overlapping emblem from x=0.8 to x=2.0)
    tb = slide_a.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(9.0), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "STRUCTURAL FRACTURE"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = CYAN

    p2 = tf.add_paragraph()
    p2.text = "THE 130-TOOL COLLAPSE"
    p2.font.size = Pt(44)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE

    p3 = tf.add_paragraph()
    p3.text = "Enterprises do not lack tools. They lack autonomous cohesion across isolated workflow silos."
    p3.font.size = Pt(18)
    p3.font.color.rgb = TEXT_MUTED

    prs_a.save(str(OUTPUT_DIR / "01A_collision_before.pptx"))

    # 01B: Safe Zone (After)
    prs_b = create_base_deck()
    slide_b = prs_b.slides.add_slide(prs_b.slide_layouts[6])
    add_dark_background(slide_b)

    # Emblem rings placed at xc=1.1, yc=3.75 (max x boundary is 1.1 + 0.9 = 2.0")
    r1 = slide_b.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.9), yc - Inches(0.9), Inches(1.8), Inches(1.8))
    r1.fill.background()
    r1.line.color.rgb = CYAN
    r1.line.width = Pt(2.5)

    r2 = slide_b.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.65), yc - Inches(0.65), Inches(1.3), Inches(1.3))
    r2.fill.background()
    r2.line.color.rgb = PURPLE
    r2.line.width = Pt(2.5)

    r3 = slide_b.shapes.add_shape(MSO_SHAPE.OVAL, xc - Inches(0.4), yc - Inches(0.4), Inches(0.8), Inches(0.8))
    r3.fill.background()
    r3.line.color.rgb = ORANGE
    r3.line.width = Pt(2.5)

    # Safe Zone Header starting at x=2.35" (clean 0.35" clearance margin from emblem edge at x=2.0")
    tb = slide_b.shapes.add_textbox(Inches(2.35), Inches(2.6), Inches(9.5), Inches(2.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "STRUCTURAL FRACTURE"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = CYAN

    p2 = tf.add_paragraph()
    p2.text = "THE 130-TOOL COLLAPSE"
    p2.font.size = Pt(44)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE

    p3 = tf.add_paragraph()
    p3.text = "Enterprises do not lack tools. They lack autonomous cohesion across isolated workflow silos."
    p3.font.size = Pt(18)
    p3.font.color.rgb = TEXT_MUTED

    prs_b.save(str(OUTPUT_DIR / "01B_safezone_after.pptx"))


# ==============================================================================
# PAIR 2: Column Measure & Text-Fit (Slide 3 Problem)
# ==============================================================================

def build_pair_02():
    # Identical clean text for both A and B (zero strawman tokens!)
    left_title = "PASSIVE CHATBOT WRAPPER"
    left_bullets = [
        "Waits passively for user prompts without continuous environmental sensing",
        "Zero persistent memory of enterprise compliance and security constraints",
        "Blind to workflow execution context and state transitions",
    ]
    right_title = "MISSION-CRITICAL WORKFLOW"
    right_bullets = [
        "Demands verifiable determinism and auditability across all execution stages",
        "Cannot delegate production access to unanchored probabilistic models",
        "Requires active guardrails against hallucinated parameter changes",
    ]

    # 02A: Pinched Columns (Before) - 3 columns / 3.1" wide, 0.5" gap, causing 2-word line wraps
    prs_a = create_base_deck()
    slide_a = prs_a.slides.add_slide(prs_a.slide_layouts[6])
    add_dark_background(slide_a)

    # Title
    tbox = slide_a.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.0))
    tbox.text_frame.paragraphs[0].text = "THE REASONING GAP IN ENTERPRISE AGENTS"
    tbox.text_frame.paragraphs[0].font.size = Pt(28)
    tbox.text_frame.paragraphs[0].font.bold = True
    tbox.text_frame.paragraphs[0].font.color.rgb = TEXT_WHITE

    # 3 narrow columns (w=3.1", gap=0.5")
    c1 = slide_a.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(3.1), Inches(4.8))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = CARD_BORDER
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = CYAN
    for b in left_bullets:
        p = tf1.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_MUTED

    # Trapped center ring
    c2 = slide_a.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.4), Inches(3.5), Inches(1.2), Inches(1.2))
    c2.fill.background()
    c2.line.color.rgb = ORANGE
    c2.line.width = Pt(3)

    # Right card
    c3 = slide_a.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.1), Inches(1.8), Inches(3.1), Inches(4.8))
    c3.fill.solid()
    c3.fill.fore_color.rgb = CARD_BG
    c3.line.color.rgb = CARD_BORDER
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = CYAN
    for b in right_bullets:
        p = tf3.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_MUTED

    prs_a.save(str(OUTPUT_DIR / "02A_pinched_before.pptx"))

    # 02B: 12-Column Grid Snapped 2-Column Split (After)
    # Span 6 + 6: Col 0-5 (x=0.80, w=5.74), Col 6-11 (x=6.79, w=5.74), G=0.25"
    prs_b = create_base_deck()
    slide_b = prs_b.slides.add_slide(prs_b.slide_layouts[6])
    add_dark_background(slide_b)

    # Title
    tbox = slide_b.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.0))
    tbox.text_frame.paragraphs[0].text = "THE REASONING GAP IN ENTERPRISE AGENTS"
    tbox.text_frame.paragraphs[0].font.size = Pt(28)
    tbox.text_frame.paragraphs[0].font.bold = True
    tbox.text_frame.paragraphs[0].font.color.rgb = TEXT_WHITE

    # Left card (w=5.74", text area 5.14", measure ~50ch)
    c1 = slide_b.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.80), Inches(1.8), Inches(5.74), Inches(4.8))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = CARD_BORDER
    c1.line.width = Pt(1)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.3)
    tf1.margin_right = Inches(0.3)
    p = tf1.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = CYAN
    for b in left_bullets:
        p = tf1.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(15)
        p.font.color.rgb = TEXT_MUTED

    # Right card (w=5.74", text area 5.14", measure ~50ch)
    c2 = slide_b.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.79), Inches(1.8), Inches(5.74), Inches(4.8))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = CARD_BORDER
    c2.line.width = Pt(1)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = Inches(0.3)
    tf2.margin_right = Inches(0.3)
    p = tf2.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = CYAN
    for b in right_bullets:
        p = tf2.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(15)
        p.font.color.rgb = TEXT_MUTED

    prs_b.save(str(OUTPUT_DIR / "02B_measure_after.pptx"))


# ==============================================================================
# PAIR 3: Ghost Card vs. Clean Elevation (R10 & R11)
# ==============================================================================

def build_pair_03():
    # 03A: Ghost Card (Before) - 2pt bright border + harsh default black shadow + mismatched nested radii
    prs_a = create_base_deck()
    slide_a = prs_a.slides.add_slide(prs_a.slide_layouts[6])
    add_dark_background(slide_a)

    tb = slide_a.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tb.text_frame.paragraphs[0].text = "ELEVATION ARCHITECTURE: GHOST CARD ANTI-PATTERN"
    tb.text_frame.paragraphs[0].font.size = Pt(24)
    tb.text_frame.paragraphs[0].font.bold = True
    tb.text_frame.paragraphs[0].font.color.rgb = TEXT_WHITE

    # Outer card with thick border AND harsh shadow
    c = slide_a.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.8))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = CYAN
    c.line.width = Pt(2.5)  # Heavy border
    c.adjustments[0] = 0.08

    # Harsh default shadow (blurRad=38100, dist=38100, alpha=50000)
    set_shape_shadow(c, blur_rad=38100, dist=38100, dir_angle=5400000, alpha_val=50000)

    # Nested inner badge with SAME adj=0.08 (mismatched, bulging optical pinch)
    b = slide_a.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(2.3), Inches(3.0), Inches(0.8))
    b.fill.solid()
    b.fill.fore_color.rgb = RGBColor(51, 65, 85)
    b.line.fill.background()
    b.adjustments[0] = 0.08  # Identical adj causes optical distortion
    b.text_frame.paragraphs[0].text = "CRITICAL METRIC"
    b.text_frame.paragraphs[0].font.size = Pt(13)
    b.text_frame.paragraphs[0].font.bold = True
    b.text_frame.paragraphs[0].font.color.rgb = CYAN

    prs_a.save(str(OUTPUT_DIR / "03A_ghostcard_before.pptx"))

    # 03B: Clean Soft Elevation & Concentric Radii (After)
    prs_b = create_base_deck()
    slide_b = prs_b.slides.add_slide(prs_b.slide_layouts[6])
    add_dark_background(slide_b)

    tb = slide_b.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tb.text_frame.paragraphs[0].text = "ELEVATION ARCHITECTURE: SOFT DIFFUSED AMBIENT SHADOW"
    tb.text_frame.paragraphs[0].font.size = Pt(24)
    tb.text_frame.paragraphs[0].font.bold = True
    tb.text_frame.paragraphs[0].font.color.rgb = TEXT_WHITE

    # Outer card: ZERO border, soft diffused shadow (blurRad=200000, alpha=10000)
    c = slide_b.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.8))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.fill.background()  # ZERO border!

    # Outer corner radius: R_outer = 0.20" = 182,880 EMU. Min dim = 4.8" = 4,389,120 EMU.
    # adj_outer = 182880 / 4389120 = 0.04166
    c.adjustments[0] = 0.04166

    # Soft diffused ambient shadow
    set_shape_shadow(c, blur_rad=200000, dist=50800, dir_angle=5400000, alpha_val=10000)

    # Nested inner badge with CONCENTRIC radius:
    # Padding = 0.50" horizontally, 0.50" vertically.
    # R_inner = max(0, R_outer - padding) -> Concentric radius!
    # Badge min dim = 0.8" = 731,520 EMU. If padding is 0.12" (109,728 EMU), R_inner = 73,152 EMU -> adj = 0.10
    b = slide_b.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(2.3), Inches(3.0), Inches(0.8))
    b.fill.solid()
    b.fill.fore_color.rgb = RGBColor(51, 65, 85)
    b.line.fill.background()
    b.adjustments[0] = 0.10  # Concentric radius calculated via EMU formula
    b.text_frame.paragraphs[0].text = "CRITICAL METRIC"
    b.text_frame.paragraphs[0].font.size = Pt(13)
    b.text_frame.paragraphs[0].font.bold = True
    b.text_frame.paragraphs[0].font.color.rgb = CYAN

    prs_b.save(str(OUTPUT_DIR / "03B_elevation_after.pptx"))


# ==============================================================================
# PAIR 4: Morph Shape & Velocity Discipline (R01, R02, R03)
# ==============================================================================

def build_pair_04():
    # 04A: Morph Deformed (Before) - 2 slides: Ellipse morphing to roundRect (cross-fade defect), text inside morphing shape
    prs_a = create_base_deck()
    # Slide 1
    s1 = prs_a.slides.add_slide(prs_a.slide_layouts[6])
    add_dark_background(s1)
    # Circle as ELLIPSE (cannot morph to roundRect!)
    c1 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.66), Inches(2.75), Inches(2.0), Inches(2.0))
    c1.name = "!!hero_actor"
    c1.fill.solid()
    c1.fill.fore_color.rgb = CYAN
    c1.line.fill.background()
    c1.text_frame.paragraphs[0].text = "LAUNCH"
    c1.text_frame.paragraphs[0].font.bold = True
    c1.text_frame.paragraphs[0].font.color.rgb = DARK_BG

    # Slide 2 (Morph target)
    s2 = prs_a.slides.add_slide(prs_a.slide_layouts[6])
    add_dark_background(s2)
    anim.add_morph_transition(s2._element, duration_ms=1000)

    # Expanded card as ROUNDED_RECTANGLE (mismatched geometry!) with dense text
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(2.0), Inches(9.33), Inches(3.5))
    c2.name = "!!hero_actor"
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = CYAN
    c2.line.width = Pt(1.5)
    tf = c2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EXPANDED PLATFORM EXECUTION"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p2 = tf.add_paragraph()
    p2.text = "When geometry primitives differ, PowerPoint cannot compute vector morphing and dissolves into an abrupt fade."
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_WHITE

    prs_a.save(str(OUTPUT_DIR / "04A_morph_deformed_before.pptx"))

    # 04B: Clean Morph (After) - roundRect cx==cy morphing to roundRect card, decoupled text
    prs_b = create_base_deck()
    # Slide 1
    s1 = prs_b.slides.add_slide(prs_b.slide_layouts[6])
    add_dark_background(s1)

    # Circle created as ROUNDED_RECTANGLE with adj=0.50 (full pill) and cx == cy
    # Size 2.0" x 2.0" = 1,828,800 x 1,828,800 EMU
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.66), Inches(2.75), Inches(2.0), Inches(2.0))
    c1.name = "!!hero_card_bg"
    c1.fill.solid()
    c1.fill.fore_color.rgb = CYAN
    c1.line.fill.background()
    c1.adjustments[0] = 0.50

    # Text in a separate decoupled frame
    t1 = s1.shapes.add_textbox(Inches(5.66), Inches(3.5), Inches(2.0), Inches(0.5))
    p = t1.text_frame.paragraphs[0]
    p.text = "LAUNCH"
    p.alignment = PP_ALIGN.CENTER
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = DARK_BG

    # Slide 2 (Morph target)
    s2 = prs_b.slides.add_slide(prs_b.slide_layouts[6])
    add_dark_background(s2)
    anim.add_morph_transition(s2._element, duration_ms=1000)

    # Expanded card as ROUNDED_RECTANGLE with adj=0.06 (same primitive!)
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(2.0), Inches(9.33), Inches(3.5))
    c2.name = "!!hero_card_bg"
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = CYAN
    c2.line.width = Pt(1.5)
    c2.adjustments[0] = 0.06

    # Decoupled text frame appearing cleanly over settled card
    t2 = s2.shapes.add_textbox(Inches(2.4), Inches(2.4), Inches(8.5), Inches(2.7))
    tf = t2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EXPANDED PLATFORM EXECUTION"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p2 = tf.add_paragraph()
    p2.text = "By maintaining identical roundRect primitives and decoupling text, vector interpolation glides seamlessly with zero font distortion."
    p2.font.size = Pt(18)
    p2.font.color.rgb = TEXT_WHITE

    prs_b.save(str(OUTPUT_DIR / "04B_morph_clean_after.pptx"))


if __name__ == "__main__":
    print("Building Pair 01 (Collision vs Safe Zone)...")
    build_pair_01()
    print("Building Pair 02 (Pinched vs Measure)...")
    build_pair_02()
    print("Building Pair 03 (Ghost Card vs Elevation)...")
    build_pair_03()
    print("Building Pair 04 (Morph Deformed vs Clean)...")
    build_pair_04()
    print("All 4 pairs generated successfully in:", OUTPUT_DIR.as_posix())
