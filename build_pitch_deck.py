#!/usr/bin/env python3
"""Build the 12-slide Series A Pitch Deck (.pptx) with native PowerPoint Morph transitions.

Implements the gold script:
`experiments/T081-20261105-antigravity-script-writer/artifacts/gold-script-pitch-deck-series-a.md`
Conforms to:
- D009: Delivered as native .pptx for PowerPoint flipping (no video needed).
- D010: Researched crowd taste & Morph-first state transitions.
- T074 Morph Matrix:
  * M-01 (Continuous !!id pairing)
  * M-02 (Same shape type: roundRect corner_radius interpolation from 0.5 down to 0.08)
  * M-07 (No entrance on destination shapes)
  * 16:9 widescreen layout (13.333" x 7.5") with aspect-calibrated concentric geometry.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

import pptx_animator as anim

# Color Palette
BG = RGBColor(11, 15, 25)          # Deep Midnight Navy #0B0F19
CARD_BG = RGBColor(24, 32, 47)     # Card Dark Slate #18202F
BORDER_COL = RGBColor(45, 55, 72)  # Muted Slate Border #2D3748

CYAN = RGBColor(6, 182, 212)       # Observation #06B6D4
VIOLET = RGBColor(139, 92, 246)    # Reasoning #8B5CF6
GOLD = RGBColor(245, 158, 11)      # Execution Amber #F59E0B
EMERALD = RGBColor(16, 185, 129)   # Execution Green #10B981
RED = RGBColor(239, 68, 68)        # Loss / Pain Warning #EF4444
WHITE = RGBColor(255, 255, 255)
GRAY = RGBColor(148, 163, 184)     # Slate text #94A3B8
MUTED = RGBColor(71, 85, 105)      # Dimmed #475569


def set_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG


def add_round_rect(slide, name, x, y, w, h, fill_col=None, border_col=None, border_pt=1.5, radius=0.5):
    """Add a rounded rectangle with explicit corner radius and name for Morph."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    if fill_col:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill_col
    else:
        sh.fill.background()
    if border_col:
        sh.line.color.rgb = border_col
        sh.line.width = Pt(border_pt)
    else:
        sh.line.fill.background()
    if len(sh.adjustments) > 0:
        sh.adjustments[0] = radius
    return sh


def add_text_box(slide, name, x, y, w, h, lines, align=PP_ALIGN.CENTER):
    """Add a structured text box."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.clear()
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if isinstance(item, tuple):
            text, size, color, bold = item
            run = p.add_run()
            run.text = text
            run.font.size = Pt(size)
            run.font.color.rgb = color
            run.font.bold = bold
            run.font.name = "Segoe UI"
        else:
            run = p.add_run()
            run.text = str(item)
            run.font.size = Pt(14)
            run.font.color.rgb = WHITE
            run.font.name = "Segoe UI"
    return tb


def add_header(slide, tag_text, title_text, sub_text=None):
    """Consistent corporate header."""
    lines = [
        (tag_text.upper(), 10, CYAN, True),
        (title_text, 24, WHITE, True)
    ]
    if sub_text:
        lines.append((sub_text, 13, GRAY, False))
    add_text_box(slide, "header", 0.8, 0.45, 11.7, 1.2, lines, align=PP_ALIGN.LEFT)


def add_3rings(slide, xc, yc, robs_r, rreas_r, rexec_r,
               exec_col=GOLD, exec_fill=None, obs_col=CYAN, reas_col=VIOLET,
               radius=0.5, border_pt=2.0):
    """Add the 3 persistent rings with exact concentric center (xc, yc)."""
    # Outer ring
    sh_obs = add_round_rect(slide, "!!ring_obs",
                            xc - robs_r, yc - robs_r, robs_r * 2, robs_r * 2,
                            fill_col=None, border_col=obs_col, border_pt=border_pt, radius=radius)
    # Middle ring
    sh_reas = add_round_rect(slide, "!!ring_reason",
                             xc - rreas_r, yc - rreas_r, rreas_r * 2, rreas_r * 2,
                             fill_col=None, border_col=reas_col, border_pt=border_pt, radius=radius)
    # Inner ring
    sh_exec = add_round_rect(slide, "!!ring_exec",
                             xc - rexec_r, yc - rexec_r, rexec_r * 2, rexec_r * 2,
                             fill_col=exec_fill, border_col=exec_col, border_pt=border_pt + 0.5, radius=radius)
    return sh_obs, sh_reas, sh_exec


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: CẢNH 1 (State 1.0) — Mở Màn & Cú Đặt Cược Cấu Trúc
    # =========================================================================
    s1 = prs.slides.add_slide(blank); set_bg(s1)
    # 3 Rings at center (xc=6.666, yc=2.3)
    add_3rings(s1, 6.666, 2.3, 1.25, 0.90, 0.55, exec_col=GOLD, radius=0.5)
    # Title & Subtitle
    add_text_box(s1, "title_group", 1.5, 3.8, 10.333, 2.5, [
        ("SERIES A INVESTMENT MEMORANDUM · $12,000,000", 11, CYAN, True),
        ("AETHER COGNITION", 46, WHITE, True),
        ("The Autonomous Cognitive OS for Enterprise Work", 18, GOLD, False),
        ("", 8, WHITE, False),
        ("Confidential Pitch Deck · November 2026", 11, GRAY, False)
    ])

    # =========================================================================
    # SLIDE 2: CẢNH 2 (State 2.0) — Khủng Hoảng 130 Công Cụ SaaS
    # =========================================================================
    s2 = prs.slides.add_slide(blank); set_bg(s2)
    # 3 Rings travel to top-left anchor (xc=1.1, yc=1.0)
    add_3rings(s2, 1.1, 1.0, 0.45, 0.32, 0.20, exec_col=GOLD, obs_col=RGBColor(6, 182, 212), radius=0.5)
    add_header(s2, "Structural Fracture",
               "THE 130-TOOL SaaS CRISIS: HUMAN BEINGS AS MANUAL GLUE",
               "Enterprises do not lack tools. They lack a central cognitive brain to operate them.")
    # Silo Matrix (represented by neat 10-tool grid cards)
    silos_x, silos_y, silos_w, silos_h = 0.8, 2.0, 11.7, 4.8
    add_round_rect(s2, "!!silos_matrix", silos_x, silos_y, silos_w, silos_h,
                   fill_col=CARD_BG, border_col=BORDER_COL, border_pt=1.5, radius=0.03)

    # Mini silo badges inside matrix
    tool_names = ["Salesforce", "Workday", "SAP ERP", "Jira", "ServiceNow",
                  "HubSpot", "Zendesk", "Oracle NetSuite", "Snowflake", "Slack"]
    for i, name in enumerate(tool_names):
        col = i % 5
        row = i // 5
        bx = silos_x + 0.6 + col * 2.15
        by = silos_y + 0.6 + row * 1.5
        add_round_rect(s2, f"silo_{i}", bx, by, 1.9, 1.1, fill_col=RGBColor(18, 24, 38),
                       border_col=BORDER_COL, border_pt=1.0, radius=0.08)
        add_text_box(s2, f"silo_txt_{i}", bx, by + 0.3, 1.9, 0.6, [
            (name, 12, GRAY, True),
            ("Silo Data", 9, MUTED, False)
        ])

    # Loss Card in center
    add_round_rect(s2, "!!card_loss", 4.3, 2.8, 4.7, 2.8, fill_col=RGBColor(26, 18, 24),
                   border_col=RED, border_pt=2.0, radius=0.06)
    add_text_box(s2, "loss_content", 4.5, 3.1, 4.3, 2.2, [
        ("4.2 HOURS / DAY", 32, RED, True),
        ("Lost to manual copy-paste between fragmented windows", 13, WHITE, False),
        ("", 8, WHITE, False),
        ("THE MISSING COGNITIVE LAYER", 14, CYAN, True)
    ])
    add_round_rect(s2, "!!missing_layer", 4.5, 5.0, 4.3, 0.05, fill_col=CYAN, border_col=None)

    # =========================================================================
    # SLIDE 3: CẢNH 3 (State 3.0) — Vì Sao Chatbot LLM Thất Bại (Disarticulated)
    # =========================================================================
    s3 = prs.slides.add_slide(blank); set_bg(s3)
    add_header(s3, "Architectural Deadlock",
               "WHY COPILOTS & CHATBOT WRAPPERS INEVITABLY FAIL",
               "Passive assistants cannot operate autonomous business workflows.")

    # Left Container: Chatbot Mockup with !!ring_obs
    add_round_rect(s3, "!!chatbox_mockup", 0.8, 2.0, 5.6, 4.8, fill_col=CARD_BG,
                   border_col=BORDER_COL, border_pt=1.5, radius=0.04)
    # !!ring_obs placed here in disarticulated state
    add_round_rect(s3, "!!ring_obs", 2.9, 2.4, 1.4, 1.4, fill_col=None, border_col=MUTED, border_pt=2.0, radius=0.5)
    add_text_box(s3, "chatbox_txt", 1.2, 4.0, 4.8, 2.4, [
        ("PASSIVE CHATBOT WRAPPER", 16, GRAY, True),
        ("• Waits passively for user input", 12, MUTED, False),
        ("• Zero persistent context of internal enterprise rules", 12, MUTED, False),
        ("", 6, WHITE, False),
        ("!!err_obs: Blind to Workflow Context", 13, RED, True)
    ], align=PP_ALIGN.LEFT)

    # Middle Bridge: !!ring_reason floating warning
    add_round_rect(s3, "!!ring_reason", 6.2, 3.3, 0.95, 0.95, fill_col=None, border_col=RGBColor(249, 115, 22), border_pt=2.0, radius=0.5)
    add_text_box(s3, "reason_txt", 5.7, 4.4, 2.0, 1.5, [
        ("DISCONNECTED", 10, RGBColor(249, 115, 22), True),
        ("!!err_reason: Hallucination Risk", 11, RED, True)
    ])

    # Right Container: Enterprise Workflow Tree with !!ring_exec locked
    add_round_rect(s3, "!!process_tree", 6.9, 2.0, 5.6, 4.8, fill_col=CARD_BG,
                   border_col=BORDER_COL, border_pt=1.5, radius=0.04)
    add_round_rect(s3, "!!ring_exec", 9.3, 2.7, 0.75, 0.75, fill_col=None, border_col=MUTED, border_pt=2.0, radius=0.5)
    add_text_box(s3, "process_txt", 7.3, 4.0, 4.8, 2.4, [
        ("MISSION-CRITICAL WORKFLOW", 16, CYAN, True),
        ("• Requires 100% auditability & zero error tolerance", 12, GRAY, False),
        ("• Cannot delegate write access to probabilistic models", 12, GRAY, False),
        ("", 6, WHITE, False),
        ("!!err_exec: Zero Execution Authority", 13, RED, True)
    ], align=PP_ALIGN.LEFT)

    # =========================================================================
    # SLIDE 4: CẢNH 4 (State 4.0) — Kiến Trúc Bánh Đà Nhận Thức Tái Lập
    # =========================================================================
    s4 = prs.slides.add_slide(blank); set_bg(s4)
    add_header(s4, "The Solution Architecture",
               "AETHER: 3-TIER COGNITIVE FLYWHEEL (RE-CONVERGED)",
               "Probabilistic reasoning in the mind · Deterministic execution at the core.")

    # Re-converged Concentric Engine at center (xc=6.666, yc=4.2)
    xc, yc = 6.666, 4.2
    add_3rings(s4, xc, yc, 2.2, 1.5, 0.8,
               exec_col=EMERALD, exec_fill=RGBColor(6, 78, 59),
               obs_col=CYAN, reas_col=VIOLET, radius=0.5, border_pt=2.5)

    # 4 Agent Nodes on Middle Ring
    add_round_rect(s4, "!!agent_fin", xc - 0.45, yc - 1.7, 0.9, 0.45, fill_col=VIOLET, radius=0.08)
    add_text_box(s4, "agent_fin_t", xc - 0.45, yc - 1.65, 0.9, 0.4, [("Finance", 9, WHITE, True)])

    add_round_rect(s4, "!!agent_ops", xc + 1.25, yc - 0.22, 0.9, 0.45, fill_col=VIOLET, radius=0.08)
    add_text_box(s4, "agent_ops_t", xc + 1.25, yc - 0.17, 0.9, 0.4, [("Ops", 9, WHITE, True)])

    add_round_rect(s4, "!!agent_legal", xc - 0.45, yc + 1.25, 0.9, 0.45, fill_col=VIOLET, radius=0.08)
    add_text_box(s4, "agent_legal_t", xc - 0.45, yc + 1.30, 0.9, 0.4, [("Legal", 9, WHITE, True)])

    add_round_rect(s4, "!!agent_hr", xc - 2.15, yc - 0.22, 0.9, 0.45, fill_col=VIOLET, radius=0.08)
    add_text_box(s4, "agent_hr_t", xc - 2.15, yc - 0.17, 0.9, 0.4, [("HR", 9, WHITE, True)])

    # 3 API Connectors shooting out from Core
    add_round_rect(s4, "!!api_erp", 1.2, 3.9, 2.4, 0.6, fill_col=RGBColor(16, 40, 32), border_col=EMERALD, radius=0.08)
    add_text_box(s4, "api_erp_t", 1.2, 4.0, 2.4, 0.4, [("SAP / Oracle API", 11, EMERALD, True)])

    add_round_rect(s4, "!!api_crm", 9.7, 3.9, 2.4, 0.6, fill_col=RGBColor(16, 40, 32), border_col=EMERALD, radius=0.08)
    add_text_box(s4, "api_crm_t", 9.7, 4.0, 2.4, 0.4, [("Salesforce CRM API", 11, EMERALD, True)])

    add_round_rect(s4, "!!api_db", 5.4, 6.4, 2.5, 0.6, fill_col=RGBColor(16, 40, 32), border_col=EMERALD, radius=0.08)
    add_text_box(s4, "api_db_t", 5.4, 6.5, 2.5, 0.4, [("Audit-Verifiable DB", 11, EMERALD, True)])

    # =========================================================================
    # SLIDE 5: CẢNH 5 (State 5A) — Minh Chứng Tăng Trưởng (Baseline)
    # =========================================================================
    s5 = prs.slides.add_slide(blank); set_bg(s5)
    # 3 Rings at bottom-left launchpad (xc=1.8, yc=5.2)
    add_3rings(s5, 1.8, 5.2, 0.8, 0.55, 0.35, exec_col=EMERALD, radius=0.5)
    add_header(s5, "Market Traction & Growth",
               "PROVEN TRACTION: FROM PILOT TO PRODUCTION ENGINE",
               "Real revenue validated across 38 Fortune 500 enterprise deployments.")

    # Baseline milestone card
    add_round_rect(s5, "card_q1", 1.0, 2.2, 3.2, 1.8, fill_col=CARD_BG, border_col=BORDER_COL, radius=0.06)
    add_text_box(s5, "q1_txt", 1.2, 2.5, 2.8, 1.2, [
        ("Q1 / 2025 BASELINE", 11, GRAY, True),
        ("$1,100,000 ARR", 22, WHITE, True),
        ("Initial 8 Production Pilots", 11, CYAN, False)
    ])

    # Metric ARR bar sitting at BASELINE (y=6.0, h=0.4)
    add_round_rect(s5, "!!metric_arr", 5.2, 6.0, 2.5, 0.4, fill_col=BORDER_COL, border_col=GRAY, radius=0.04)
    add_text_box(s5, "arr_base_lbl", 5.2, 5.5, 2.5, 0.4, [("Baseline Level", 11, GRAY, False)])

    # =========================================================================
    # SLIDE 6: CẢNH 5 (State 5B) — Cột ARR $4.2M Vút Dâng & Thẻ 148% NRR
    # =========================================================================
    s6 = prs.slides.add_slide(blank); set_bg(s6)
    # 3 Rings still at bottom-left launchpad
    add_3rings(s6, 1.8, 5.2, 0.8, 0.55, 0.35, exec_col=EMERALD, radius=0.5)
    add_header(s6, "Market Traction & Growth",
               "PROVEN TRACTION: $4.2M ARR & 148% NET RETENTION RATE",
               "Land-and-expand flywheel: customers spend 48% more each subsequent year.")

    add_round_rect(s6, "card_q1", 1.0, 2.2, 3.2, 1.8, fill_col=CARD_BG, border_col=BORDER_COL, radius=0.06)
    add_text_box(s6, "q1_txt", 1.2, 2.5, 2.8, 1.2, [
        ("Q1 / 2025 BASELINE", 11, GRAY, True),
        ("$1,100,000 ARR", 22, WHITE, True),
        ("Initial 8 Production Pilots", 11, CYAN, False)
    ])

    # !!metric_arr expands to full height (y=2.0, h=4.4)
    add_round_rect(s6, "!!metric_arr", 5.2, 2.0, 2.5, 4.4,
                   fill_col=RGBColor(6, 78, 59), border_col=EMERALD, border_pt=2.5, radius=0.04)
    add_text_box(s6, "arr_top_lbl", 5.2, 2.3, 2.5, 2.0, [
        ("$4.2M ARR", 32, EMERALD, True),
        ("14 Months Hypergrowth", 11, WHITE, False),
        ("38 Enterprise Deals", 11, CYAN, False)
    ])

    # !!card_nrr appears on right
    add_round_rect(s6, "!!card_nrr", 8.4, 2.2, 4.1, 4.2, fill_col=CARD_BG, border_col=GOLD, border_pt=2.0, radius=0.06)
    add_text_box(s6, "nrr_lbl", 8.7, 2.6, 3.5, 3.4, [
        ("NET RETENTION RATE", 12, GOLD, True),
        ("148% NRR", 44, GOLD, True),
        ("Negative Churn Machine", 14, WHITE, True),
        ("", 10, WHITE, False),
        ("Once Aether orchestrates an enterprise workflow, teams actively expand licenses across departments.", 12, GRAY, False)
    ])

    # =========================================================================
    # SLIDE 7: CẢNH 6 (State 6A) — Đơn Vị Kinh Tế: 3 Cột Cân Bằng Ban Đầu
    # =========================================================================
    s7 = prs.slides.add_slide(blank); set_bg(s7)
    add_header(s7, "Unit Economics & Margins",
               "THE AI MARGIN SQUEEZE: COMMODITY GPU COSTS VS SLM EFFICIENCY",
               "How Aether defeats the 65% inference cost trap through local tiered models.")

    # 3 Columns equal height (h=3.8, y=2.6)
    add_round_rect(s7, "!!col_gpu", 0.8, 2.6, 3.6, 3.8, fill_col=RGBColor(45, 20, 20), border_col=RED, border_pt=1.5, radius=0.04)
    add_text_box(s7, "gpu_txt_a", 1.0, 2.9, 3.2, 3.0, [
        ("STANDARD AI APPS", 11, RED, True),
        ("65% GPU INFERENCE", 24, RED, True),
        ("", 8, WHITE, False),
        ("Cloud LLM API tokens destroy software margins as scale grows.", 12, GRAY, False)
    ])

    add_round_rect(s7, "!!col_margin", 4.8, 2.6, 3.6, 3.8, fill_col=CARD_BG, border_col=BORDER_COL, border_pt=1.5, radius=0.04)
    # 3 Rings inside Margin Column header
    add_3rings(s7, 6.6, 3.3, 0.45, 0.32, 0.20, exec_col=EMERALD, radius=0.5)
    add_text_box(s7, "margin_txt_a", 5.0, 4.2, 3.2, 2.0, [
        ("AETHER ARCHITECTURE", 11, CYAN, True),
        ("Tiered SLM Routing", 20, WHITE, True),
        ("80% tasks run on local models", 12, GRAY, False)
    ])

    add_round_rect(s7, "!!col_cac", 8.8, 2.6, 3.6, 3.8, fill_col=CARD_BG, border_col=BORDER_COL, border_pt=1.5, radius=0.04)
    add_text_box(s7, "cac_txt_a", 9.0, 2.9, 3.2, 3.0, [
        ("INDUSTRY BENCHMARK", 11, GRAY, True),
        ("14 MONTHS CAC", 24, GRAY, True),
        ("", 8, WHITE, False),
        ("Traditional SaaS customer acquisition payback cycle.", 12, MUTED, False)
    ])

    # =========================================================================
    # SLIDE 8: CẢNH 6 (State 6B) — Co Rút GPU & Nở Lớn Gross Margin 82%
    # =========================================================================
    s8 = prs.slides.add_slide(blank); set_bg(s8)
    add_header(s8, "Unit Economics & Margins",
               "THE AI MARGIN SQUEEZE: COMPRESSED GPU COST & 82% GROSS MARGIN",
               "Sustainable unit economics: cash-flow positive per account within 4.5 months.")

    # !!col_gpu shrinks to h=1.2 (y=5.2)
    add_round_rect(s8, "!!col_gpu", 0.8, 5.2, 3.6, 1.2, fill_col=RGBColor(30, 25, 25), border_col=BORDER_COL, border_pt=1.0, radius=0.04)
    add_text_box(s8, "gpu_txt_b", 1.0, 5.35, 3.2, 0.9, [
        ("18% GPU COST (SLM OPTIMIZED)", 13, GRAY, True),
        ("Compressed 3.6x via Local SLM routing", 10, MUTED, False)
    ])

    # !!col_margin expands to full dominance (h=4.6, w=4.0, y=1.8, x=4.6)
    add_round_rect(s8, "!!col_margin", 4.6, 1.8, 4.0, 4.6,
                   fill_col=RGBColor(6, 78, 59), border_col=EMERALD, border_pt=2.5, radius=0.04)
    # 3 Rings scale up inside crown
    add_3rings(s8, 6.6, 2.5, 0.55, 0.40, 0.25, exec_col=EMERALD, radius=0.5)
    add_text_box(s8, "margin_txt_b", 4.8, 3.4, 3.6, 2.8, [
        ("SOFTWARE-GRADE MARGINS", 12, CYAN, True),
        ("82% GROSS MARGIN", 32, WHITE, True),
        ("", 6, WHITE, False),
        ("Enterprise Contract: $120k/yr", 13, WHITE, False),
        ("Pure software cash generation profile", 11, CYAN, False)
    ])

    # !!col_cac highlights 4.5 months
    add_round_rect(s8, "!!col_cac", 9.0, 2.6, 3.5, 3.8, fill_col=CARD_BG, border_col=GOLD, border_pt=2.0, radius=0.04)
    add_text_box(s8, "cac_txt_b", 9.2, 3.0, 3.1, 3.0, [
        ("PAYBACK ACCELERATION", 11, GOLD, True),
        ("4.5 MONTHS", 34, GOLD, True),
        ("CAC Fully Recovered", 13, WHITE, True),
        ("", 6, WHITE, False),
        ("LTV / CAC = 6.8x", 14, EMERALD, True),
        ("Fastest capital recovery in enterprise AI", 11, GRAY, False)
    ])

    # =========================================================================
    # SLIDE 9: CẢNH 7 (State 7A) — Hào Lũy: Cân Bằng 50/50
    # =========================================================================
    s9 = prs.slides.add_slide(blank); set_bg(s9)
    add_header(s9, "Competitive Moat",
               "PROPRIETARY MOAT: COMMODITY MODELS VS DEEP PROCESS GRAPH",
               "Why Big Tech models can never replicate Aether's enterprise switching barrier.")

    # Left: Foundation Models
    add_round_rect(s9, "!!card_models", 0.8, 2.2, 5.6, 4.6, fill_col=CARD_BG, border_col=BORDER_COL, radius=0.04)
    add_text_box(s9, "models_txt_a", 1.2, 2.8, 4.8, 3.4, [
        ("PUBLIC FOUNDATION MODELS", 14, GRAY, True),
        ("GPT-4 · Claude · Gemini", 22, WHITE, True),
        ("", 10, WHITE, False),
        ("• Trained on public web data", 12, GRAY, False),
        ("• Rapidly commoditizing to near-zero margin", 12, GRAY, False),
        ("• Blind to enterprise internal execution pathways", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # Right: Proprietary Process Graph with 3 Rings inside
    add_round_rect(s9, "!!card_graph", 6.9, 2.2, 5.6, 4.6, fill_col=CARD_BG, border_col=CYAN, border_pt=1.5, radius=0.04)
    add_3rings(s9, 9.7, 3.3, 0.7, 0.5, 0.3, exec_col=GOLD, radius=0.5)
    add_text_box(s9, "graph_txt_a", 7.3, 4.4, 4.8, 2.2, [
        ("PROPRIETARY PROCESS GRAPH", 14, CYAN, True),
        ("Deterministic Knowledge Moat", 20, WHITE, True),
        ("Learned daily from 38 enterprise workflows", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # =========================================================================
    # SLIDE 10: CẢNH 7 (State 7B) — Swap Weights: Đồ Thị Độc Quyền Vươn Lớn
    # =========================================================================
    s10 = prs.slides.add_slide(blank); set_bg(s10)
    add_header(s10, "Competitive Moat",
               "SWAP WEIGHTS: COMMODITY UTILITY BECOMES AETHER'S CHEAPEST FUEL",
               "High switching costs: learned enterprise workflow graph cannot be exported to competitors.")

    # !!card_models shrinks to bottom-left (w=3.8, h=1.5, y=4.9)
    add_round_rect(s10, "!!card_models", 0.8, 4.9, 3.8, 1.5, fill_col=RGBColor(20, 25, 35), border_col=BORDER_COL, radius=0.04)
    add_text_box(s10, "models_txt_b", 1.0, 5.15, 3.4, 1.0, [
        ("COMMODITIZED INFRASTRUCTURE", 10, MUTED, True),
        ("Foundation models become cheap utility tokens", 11, GRAY, False)
    ])

    # !!card_graph expands to central dominance (w=7.6, h=4.6, x=4.9, y=2.0)
    add_round_rect(s10, "!!card_graph", 4.9, 2.0, 7.6, 4.6,
                   fill_col=RGBColor(24, 28, 44), border_col=GOLD, border_pt=2.5, radius=0.04)
    add_3rings(s10, 8.7, 3.2, 0.9, 0.65, 0.4, exec_col=GOLD, radius=0.5)
    add_text_box(s10, "graph_txt_b", 5.3, 4.4, 6.8, 2.0, [
        ("THE UNREPLICABLE DATA MOAT", 13, GOLD, True),
        ("Proprietary Workflow & State Graph", 24, WHITE, True),
        ("Every automated task hardens Aether's moat across 38 Fortune 500 accounts.", 13, CYAN, False),
        ("Switching cost is near-infinite once the operating system is deployed.", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # =========================================================================
    # SLIDE 11: CẢNH 8 (State 8A) — Kêu Gọi Đầu Tư ($12M Series A)
    # =========================================================================
    s11 = prs.slides.add_slide(blank); set_bg(s11)
    # 3 Rings at crown position (xc=6.666, yc=1.8)
    add_3rings(s11, 6.666, 1.8, 0.9, 0.65, 0.4, exec_col=EMERALD, radius=0.5)

    # Main Ask Card at center
    add_round_rect(s11, "!!ask_card", 2.5, 3.2, 8.333, 3.0, fill_col=CARD_BG, border_col=GOLD, border_pt=2.5, radius=0.05)
    add_text_box(s11, "ask_txt_a", 2.8, 3.6, 7.7, 2.4, [
        ("SERIES A FINANCING MEMORANDUM", 13, CYAN, True),
        ("$12,000,000 USD", 48, GOLD, True),
        ("Powering the Autonomous Cognitive OS for Enterprise Work", 16, WHITE, False),
        ("", 8, WHITE, False),
        ("Scaling Core Engineering & Expanding to Top 100 Financial Institutions", 13, GRAY, False)
    ])

    # =========================================================================
    # SLIDE 12: CẢNH 8 (State 8B) — Cú Morph Hóa Thân Thành 3 Trụ Cột Vốn
    # =========================================================================
    s12 = prs.slides.add_slide(blank); set_bg(s12)
    # !!ask_card shrinks into top crown banner (w=5.5, h=1.2, x=3.9, y=0.5)
    add_round_rect(s12, "!!ask_card", 3.9, 0.5, 5.5, 1.2, fill_col=CARD_BG, border_col=GOLD, border_pt=1.5, radius=0.04)
    add_text_box(s12, "ask_txt_b", 4.0, 0.65, 5.3, 0.9, [
        ("$12M SERIES A ALLOCATION", 12, GOLD, True),
        ("Capital Deployment Strategy", 16, WHITE, True)
    ])

    # Three Capital Pillars (The 3 Rings morphed into 3 vertical pillars)
    # !!ring_exec -> Pillar 1 (R&D)
    add_round_rect(s12, "!!ring_exec", 0.8, 2.2, 3.6, 4.4,
                   fill_col=RGBColor(6, 78, 59), border_col=EMERALD, border_pt=2.0, radius=0.06)
    add_text_box(s12, "p1_txt", 1.0, 2.6, 3.2, 3.6, [
        ("60% ALLOCATION", 12, EMERALD, True),
        ("$7,200,000", 30, WHITE, True),
        ("R&D COGNITIVE CORE", 14, EMERALD, True),
        ("", 8, WHITE, False),
        ("• On-premise SLM training & fine-tuning", 12, GRAY, False),
        ("• Multi-agent consensus engine", 12, GRAY, False),
        ("• Deterministic API compiler runtime", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # !!ring_reason -> Pillar 2 (GTM)
    add_round_rect(s12, "!!ring_reason", 4.8, 2.2, 3.6, 4.4,
                   fill_col=RGBColor(46, 16, 101), border_col=VIOLET, border_pt=2.0, radius=0.06)
    add_text_box(s12, "p2_txt", 5.0, 2.6, 3.2, 3.6, [
        ("30% ALLOCATION", 12, VIOLET, True),
        ("$3,600,000", 30, WHITE, True),
        ("ENTERPRISE GTM", 14, VIOLET, True),
        ("", 8, WHITE, False),
        ("• Direct enterprise sales in NYC & London", 12, GRAY, False),
        ("• Penetrate top 100 financial institutions", 12, GRAY, False),
        ("• Solution architect scaling", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # !!ring_obs -> Pillar 3 (Trust & Security)
    add_round_rect(s12, "!!ring_obs", 8.8, 2.2, 3.6, 4.4,
                   fill_col=RGBColor(8, 51, 68), border_col=CYAN, border_pt=2.0, radius=0.06)
    add_text_box(s12, "p3_txt", 9.0, 2.6, 3.2, 3.6, [
        ("10% ALLOCATION", 12, CYAN, True),
        ("$1,200,000", 30, WHITE, True),
        ("SECURITY & TRUST", 14, CYAN, True),
        ("", 8, WHITE, False),
        ("• SOC2 Type II & ISO27001 certifications", 12, GRAY, False),
        ("• Verifiable cryptographical audit logs", 12, GRAY, False),
        ("• Financial regulatory compliance", 12, GRAY, False)
    ], align=PP_ALIGN.LEFT)

    # Pedestal foundation bar at the bottom
    add_round_rect(s12, "!!pedestal", 0.8, 6.75, 11.6, 0.25, fill_col=RGBColor(15, 23, 42), border_col=BORDER_COL, radius=0.04)

    # =========================================================================
    # APPLY MORPH TRANSITIONS ACROSS ALL 11 SLIDE BOUNDARIES
    # =========================================================================
    for idx in range(1, len(prs.slides)):
        slide = prs.slides[idx]
        alt = anim.add_morph_transition(slide._element, duration_ms=1200)

    # Save outputs
    out_exp = ROOT / "experiments" / "T081-20261105-antigravity-script-writer" / "artifacts" / "aether-series-a-pitch-deck.pptx"
    out_exp.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_exp)
    print(f"Generated deck: {out_exp} ({out_exp.stat().st_size} bytes, {len(prs.slides)} slides)")
    return out_exp


if __name__ == "__main__":
    build_deck()
