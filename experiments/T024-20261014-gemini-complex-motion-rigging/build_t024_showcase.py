#!/usr/bin/env python3
"""Build the T024 high-complexity 5-slide architectural showcase deck (~175 native shapes).

Demonstrates:
- Slide 1: Auto-start (`on-slide-start`) 22-shape Silicon Wafer & 6-Core Neural
  Constellation radial assembly with `follow_through_ms` + Click 1 360-deg `orbit` & counter-spin.
- Slide 2: 3D Perspective Elliptical Carousel (`orbit-3d`) on 5 multi-part Subsystem
  Pods (6 rigged shapes per pod = 30 shapes) with `follow_through_ms`, depth-modulated
  scale/opacity, crimson `spotlight`, and `release`.
- Slide 3: 43-shape Exploded 5-Layer Silicon-to-Cloud Stack (`explode-layers` with
  isometric separation + rigged sub-tiles), 4-Packet Concurrent Multi-Hop Swarm
  (`cascade-flow` with synchronized arrival `pulse` + `p:animClr` color flash),
  and `auto_avoid` obstacle-clearing cubic Bezier routing + `teeter`.
- Slide 4 -> Slide 5: 18-object deterministic `!!` Cross-Slide Morph transforming a
  2x3 Regional Cluster Mesh into a 6-row Latency Swimlane Dashboard, followed by
  series-by-series native `chart-build`, synchronized `wave`, `number-counter`
  odometer, and two independent `p:interactiveSeq` shape-triggered drill-down panels.
"""
import json
import math
from pathlib import Path
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import motion_director as md
from lo_timing_crosscheck import crosscheck
from motion_preview import render_slide_motion
from render_identity import compare

# Palette: Deep Space Dark Mode
BG_BOOKEND = RGBColor(0x0B, 0x11, 0x20)
BG_CONTENT = RGBColor(0x0F, 0x17, 0x2A)
SURFACE_1  = RGBColor(0x1E, 0x29, 0x3B)
SURFACE_2  = RGBColor(0x33, 0x41, 0x55)
BORDER_DIM = RGBColor(0x47, 0x55, 0x69)
CYAN       = RGBColor(0x06, 0xB6, 0xD4)
TEAL       = RGBColor(0x0D, 0x94, 0x88)
EMERALD    = RGBColor(0x10, 0xB9, 0x81)
VIOLET     = RGBColor(0x8B, 0x5C, 0xF6)
AMBER      = RGBColor(0xF5, 0x9E, 0x0B)
ROSE       = RGBColor(0xE1, 0x1D, 0x48)
BLUE       = RGBColor(0x25, 0x63, 0xEB)
WHITE      = RGBColor(0xF8, 0xFA, 0xFC)
MUTED      = RGBColor(0x94, 0xA3, 0xB8)


def set_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def style_tf(shape, text, size=14, color=WHITE, bold=True, align=PP_ALIGN.LEFT):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    tf.text = text
    for p in tf.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.name = "DejaVu Sans"
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color


def sh(slide, kind, x, y, w, h, fill, name, text="", size=13, color=WHITE, bold=True,
       align=PP_ALIGN.CENTER, border=None):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if border:
        s.line.color.rgb = border
        s.line.width = Pt(1.2)
    else:
        s.line.fill.background()
    if text:
        style_tf(s, text, size=size, color=color, bold=bold, align=align)
    return s


def tb(slide, x, y, w, h, name, text, size=13, color=WHITE, bold=True, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    style_tf(box, text, size=size, color=color, bold=bold, align=align)
    return box


def add_header_band(slide, idx, kicker, title):
    tb(slide, 0.65, 0.32, 8.5, 0.32, f"S{idx} Kicker", kicker, size=11, color=CYAN, bold=True)
    tb(slide, 0.65, 0.62, 11.8, 0.55, f"S{idx} Title", title, size=24, color=WHITE, bold=True)


def build_source_deck(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Animated Hero Cover — Silicon Wafer & 6-Core Neural Constellation
    # =========================================================================
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, BG_BOOKEND)
    sh(s1, MSO_SHAPE.ROUNDED_RECTANGLE, 0.70, 0.65, 3.80, 0.36, SURFACE_1,
       "Cover Kicker Pill", "AUTONOMOUS SILICON & FABRIC · 2027", size=11, color=CYAN, border=CYAN)
    tb(s1, 0.70, 1.18, 6.20, 1.15, "Cover Main Title",
       "Optical Tensor Architecture\n& Self-Healing Mesh", size=30, color=WHITE, bold=True)
    tb(s1, 0.70, 2.52, 6.00, 0.85, "Cover Subtitle",
       "Multi-layer compound choreography: transitive virtual rigging,\n3D perspective orbits, exploded strata, and interactive OOXML.",
       size=15, color=MUTED, bold=False)

    # 3 Bottom Telemetry Mini-Cards (each is a 4-shape composite rig = 12 shapes)
    kpis = [
        ("Card BW", "14.4 TB/s", "Co-Packaged Optical Ring", CYAN),
        ("Card E",  "1.8 pJ/bit", "Photonic Waveguide Bus", EMERALD),
        ("Card SLA","99.995%",   "Zero-Drop Failover Mesh", VIOLET),
    ]
    for i, (cname, val, sub_lbl, accent) in enumerate(kpis):
        cx = 0.70 + i * 2.15
        cy = 4.55
        sh(s1, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, 1.98, 1.85, SURFACE_1, cname, border=BORDER_DIM)
        sh(s1, MSO_SHAPE.RECTANGLE, cx + 0.12, cy + 0.12, 1.74, 0.10, accent, f"{cname} Bar")
        tb(s1, cx + 0.12, cy + 0.38, 1.74, 0.58, f"{cname} Val", val, size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        tb(s1, cx + 0.12, cy + 1.08, 1.74, 0.58, f"{cname} Sub", sub_lbl, size=11, color=MUTED, bold=False, align=PP_ALIGN.CENTER)

    # Right half: Multi-Ring Silicon Wafer Constellation (20 shapes)
    wcx, wcy, wr = 9.85, 3.75, 2.10
    sh(s1, MSO_SHAPE.DONUT, wcx - 2.55, wcy - 2.55, 5.10, 5.10, SURFACE_1, "Wafer Outer Ring", border=CYAN)
    sh(s1, MSO_SHAPE.HEXAGON, wcx - 0.95, wcy - 0.95, 1.90, 1.90, BLUE, "Wafer Core Die", border=CYAN)
    tb(s1, wcx - 0.75, wcy - 0.38, 1.50, 0.42, "Wafer Core Title", "NPU-X9", size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s1, wcx - 0.75, wcy + 0.05, 1.50, 0.35, "Wafer Core Sub", "4.8 PFLOPS", size=11, color=CYAN, bold=True, align=PP_ALIGN.CENTER)

    core_specs = [
        ("C1", "640 TFLOPS", CYAN),
        ("C2", "HBM3e Ctrl", EMERALD),
        ("C3", "KV Router",  VIOLET),
        ("C4", "Optical TX", AMBER),
        ("C5", "RDMA DMA",   CYAN),
        ("C6", "Guardrail",  ROSE),
    ]
    for i, (cid, cspec, col) in enumerate(core_specs):
        ang = -math.pi / 2 + i * math.pi / 3
        nx = wcx + wr * math.cos(ang)
        ny = wcy + wr * math.sin(ang)
        sh(s1, MSO_SHAPE.ROUNDED_RECTANGLE, nx - 0.72, ny - 0.52, 1.44, 1.04, SURFACE_2, f"Core Tile {cid}", border=col)
        sh(s1, MSO_SHAPE.DIAMOND, nx - 0.58, ny - 0.36, 0.34, 0.34, col, f"Core Gem {cid}", cid, size=9, color=BG_BOOKEND)
        tb(s1, nx - 0.18, ny - 0.38, 0.82, 0.36, f"Core Name {cid}", f"Tile {cid}", size=12, color=WHITE, bold=True)
        tb(s1, nx - 0.58, ny + 0.06, 1.16, 0.34, f"Core Spec {cid}", cspec, size=10, color=MUTED, bold=False, align=PP_ALIGN.CENTER)
    s1.notes_slide.notes_text_frame.text = "Auto-assemble the 6 multi-part NPU tiles on slide start, then orbit all 6 tiles 360 degrees while counter-spinning the wafer ring."

    # =========================================================================
    # SLIDE 2: 3D Perspective Elliptical Carousel (orbit-3d + 6-Part Rigs)
    # =========================================================================
    s2 = prs.slides.add_slide(blank)
    set_bg(s2, BG_CONTENT)
    add_header_band(s2, 2, "3D PERSPECTIVE ELLIPTICAL CAROUSEL · TRANSITIVE VIRTUAL RIGGING",
                    "Five 6-Part Autonomous Pods Orbiting in Simulated 3D Depth")

    ecx, ecy, erx, ery = 6.67, 4.35, 4.15, 1.75
    # Central Policy Kernel (4 shapes)
    sh(s2, MSO_SHAPE.OCTAGON, ecx - 1.15, ecy - 0.85, 2.30, 1.70, SURFACE_1, "Kernel Hub", border=CYAN)
    sh(s2, MSO_SHAPE.OVAL, ecx - 0.32, ecy - 0.68, 0.64, 0.52, CYAN, "Kernel Badge", "AI", size=13, color=BG_BOOKEND)
    tb(s2, ecx - 0.95, ecy - 0.10, 1.90, 0.40, "Kernel Title", "Policy Kernel", size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s2, ecx - 0.95, ecy + 0.30, 1.90, 0.36, "Kernel Sub", "Global State Loop", size=11, color=CYAN, bold=False, align=PP_ALIGN.CENTER)

    pods = [
        ("Pod Telemetry", "S1", "Telemetry Fabric",  "eBPF + Optical Probes", "4.8M msg/s", CYAN,    -math.pi / 2),
        ("Pod WorldModel","S2", "World-Model Graph", "Causal Topology Twin",  "120k nodes", VIOLET,  -math.pi / 2 + 2 * math.pi / 5),
        ("Pod RiskSolver","S3", "Stochastic Solver", "Counterfactual Rollout","0.4 ms p99", EMERALD, -math.pi / 2 + 4 * math.pi / 5),
        ("Pod Shaper",    "S4", "Traffic Shaper",    "Dynamic QoS Pacing",    "Zero Drop",  AMBER,   -math.pi / 2 + 6 * math.pi / 5),
        ("Pod SelfHeal",  "S5", "Self-Heal Actuator","Hot-Swap Optical Lane", "99.999%",    ROSE,    -math.pi / 2 + 8 * math.pi / 5),
    ]
    for pname, code, title_txt, spec_txt, pill_txt, accent, ang in pods:
        px = ecx + erx * math.cos(ang)
        py = ecy + ery * math.sin(ang)
        pw, ph = 2.36, 1.42
        x0, y0 = px - pw / 2, py - ph / 2
        sh(s2, MSO_SHAPE.ROUNDED_RECTANGLE, x0, y0, pw, ph, SURFACE_1, pname, border=accent)
        sh(s2, MSO_SHAPE.RECTANGLE, x0 + 0.08, y0 + 0.07, pw - 0.16, 0.10, accent, f"{pname} Hdr")
        sh(s2, MSO_SHAPE.HEXAGON, x0 + 0.12, y0 + 0.25, 0.44, 0.44, accent, f"{pname} Icon", code, size=11, color=BG_BOOKEND)
        tb(s2, x0 + 0.62, y0 + 0.24, pw - 0.72, 0.38, f"{pname} Title", title_txt, size=13, color=WHITE, bold=True)
        tb(s2, x0 + 0.14, y0 + 0.70, pw - 0.28, 0.32, f"{pname} Spec", spec_txt, size=10, color=MUTED, bold=False)
        sh(s2, MSO_SHAPE.ROUNDED_RECTANGLE, x0 + 0.22, y0 + 1.04, pw - 0.44, 0.28, SURFACE_2, f"{pname} Pill", pill_txt, size=10, color=accent)
    s2.notes_slide.notes_text_frame.text = "Assemble the 5 composite pods with 30ms follow-through inertia, rotate twice in 3D elliptical depth, spotlight Pod RiskSolver, then restore."

    # =========================================================================
    # SLIDE 3: Exploded 5-Layer Stack, 4-Packet Swarm & Auto-Arc Obstacle Bypass
    # =========================================================================
    s3 = prs.slides.add_slide(blank)
    set_bg(s3, BG_CONTENT)
    add_header_band(s3, 3, "EXPLODED STRATA · CONCURRENT SWARM · AUTO-ARC OBSTACLE SOLVER",
                    "5-Layer Silicon-to-Cloud Stack & 4-Packet Braided Telemetry Flow")

    layers = [
        ("Layer L1", "L1", "Optical PHY Interconnect", "800G Co-Packaged Silicon Photonics", "1.6 Tbps/lane", CYAN),
        ("Layer L2", "L2", "HBM3e Crossbar Fabric",    "Non-Blocking 3D Mesh Switch",       "14.4 TB/s",     TEAL),
        ("Layer L3", "L3", "Systolic Tensor Array",    "FP8 / INT4 Sparse Matrix Units",    "4.8 PFLOPS",    VIOLET),
        ("Layer L4", "L4", "Zero-Trust DPI Guardrail", "Inline Cryptographic Attestation",  "0.15 ms",       AMBER),
        ("Layer L5", "L5", "Speculative Token Router", "Multi-Draft Verification Engine",   "3.4x Speedup",  EMERALD),
    ]
    # Compact stack in left column so isometric explosion stays 100% clear of middle/right columns
    for i, (lname, lcode, ltitle, lsub, lmetric, col) in enumerate(layers):
        lx = 0.65
        ly = 2.35 + i * 0.72
        lw, lh = 5.40, 0.62
        sh(s3, MSO_SHAPE.ROUNDED_RECTANGLE, lx, ly, lw, lh, SURFACE_1, lname, border=col)
        sh(s3, MSO_SHAPE.CHEVRON, lx + 0.10, ly + 0.10, 0.58, 0.42, col, f"{lname} Tag", lcode, size=11, color=BG_BOOKEND)
        tb(s3, lx + 0.76, ly + 0.06, 2.55, 0.28, f"{lname} Title", ltitle, size=12, color=WHITE, bold=True)
        tb(s3, lx + 0.76, ly + 0.32, 2.55, 0.24, f"{lname} Sub", lsub, size=10, color=MUTED, bold=False)
        sh(s3, MSO_SHAPE.ROUNDED_RECTANGLE, lx + 3.40, ly + 0.12, 0.90, 0.38, SURFACE_2, f"{lname} TileA", "Bank A", size=9, color=col)
        sh(s3, MSO_SHAPE.ROUNDED_RECTANGLE, lx + 4.38, ly + 0.12, 0.90, 0.38, SURFACE_2, f"{lname} TileB", lmetric, size=9, color=WHITE)

    # Middle column: 4 Bus Relay Stages for the 4-Packet Braided Cascade Swarm
    relays = [
        ("Relay R1", "PHY Ingress",  1.85, CYAN),
        ("Relay R2", "HBM Crossbar", 3.05, TEAL),
        ("Relay R3", "Tensor Queue", 4.25, VIOLET),
        ("Relay R4", "Token Egress", 5.45, EMERALD),
    ]
    for rname, rlabel, ry, col in relays:
        sh(s3, MSO_SHAPE.ROUNDED_RECTANGLE, 7.15, ry, 1.85, 0.64, SURFACE_1, rname, rlabel, size=12, color=WHITE, border=col)

    # 4 Data Packet Tokens starting at the top of the relay channel
    pkt_colors = [ROSE, AMBER, CYAN, EMERALD]
    for pi in range(4):
        sh(s3, MSO_SHAPE.OVAL, 7.20 + pi * 0.48, 1.25, 0.38, 0.32,
           pkt_colors[pi], f"Swarm PKT-{pi+1}", f"P{pi+1}", size=9, color=BG_BOOKEND)

    # Right column: Audit Probe -> Thermal Throttle Obstacle -> Telemetry Sink (tests auto_avoid)
    sh(s3, MSO_SHAPE.OVAL, 9.25, 3.40, 0.52, 0.52, ROSE, "Audit Probe", "PRB", size=10, color=WHITE)
    sh(s3, MSO_SHAPE.OCTAGON, 10.15, 3.05, 1.18, 1.22, SURFACE_2, "Thermal Obstacle",
       "Thermal\nGate", size=11, color=AMBER, border=AMBER)
    sh(s3, MSO_SHAPE.ROUNDED_RECTANGLE, 11.68, 3.25, 1.18, 0.82, SURFACE_1, "Telemetry Sink",
       "Audit Sink", size=11, color=CYAN, border=CYAN)
    s3.notes_slide.notes_text_frame.text = "Explode the 5-layer silicon stack, stream 4 packets through Relays R1-R4 with color flashes, then route Audit Probe around Thermal Gate."

    # =========================================================================
    # SLIDE 4: Global Cluster Mesh (18 !! Morph-Paired Objects + Arc Swap)
    # =========================================================================
    s4 = prs.slides.add_slide(blank)
    set_bg(s4, BG_CONTENT)
    add_header_band(s4, 4, "SPATIAL TOPOLOGY MESH · DETERMINISTIC !! MORPH PAIRING (SLIDE 4 → 5)",
                    "Six Regional AI Clusters Re-Rank Failover Priority Before Morphing")

    sh(s4, MSO_SHAPE.HEXAGON, 5.55, 3.45, 2.20, 1.55, BLUE, "Anycast Core",
       "Anycast Mesh\nRouter", size=14, color=WHITE, border=CYAN)

    clusters = [
        ("1", "US-West (Oregon)",    "1.2 ms", 0.85, 1.65, CYAN),
        ("2", "US-East (Virginia)",  "1.8 ms", 0.85, 3.55, TEAL),
        ("3", "EU-Central (Frankfurt)","2.4 ms",0.85, 5.45, AMBER),
        ("4", "AP-North (Tokyo)",    "1.5 ms", 8.85, 1.65, EMERALD),
        ("5", "AP-South (Singapore)","2.1 ms", 8.85, 3.55, VIOLET),
        ("6", "SA-East (Sao Paulo)", "2.9 ms", 8.85, 5.45, ROSE),
    ]
    for cid, cname, clat, cx, cy, col in clusters:
        sh(s4, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, 3.60, 1.32, SURFACE_1, f"!!cluster-{cid}", border=col)
        tb(s4, cx + 0.16, cy + 0.10, 2.20, 0.38, f"Cluster Name {cid}", cname, size=13, color=WHITE, bold=True)
        sh(s4, MSO_SHAPE.ROUNDED_RECTANGLE, cx + 2.42, cy + 0.12, 1.02, 0.34, SURFACE_2, f"!!lat-{cid}", clat, size=11, color=col)
        sh(s4, MSO_SHAPE.ROUNDED_RECTANGLE, cx + 0.16, cy + 0.68, 3.28, 0.42, col, f"!!bar-{cid}",
           f"Active Load · Shard {cid}", size=11, color=BG_BOOKEND)
    s4.notes_slide.notes_text_frame.text = "Assemble the 6 regional clusters, swap US-East and EU-Central on curved arcs, then Morph all 18 !! objects into Slide 5's swimlane table."

    # =========================================================================
    # SLIDE 5: Morphed Swimlane Dashboard + Native Chart + Wave + 2 InteractiveSeq
    # =========================================================================
    s5 = prs.slides.add_slide(blank)
    set_bg(s5, BG_BOOKEND)
    add_header_band(s5, 5, "MORPHED SWIMLANE CONSOLE · NATIVE CHART BUILD · DUAL INTERACTIVESEQ",
                    "Regional Mesh Morphs Into Swimlanes Alongside Live Telemetry & Triggers")

    # Left half: The exact same 18 !! objects rearranged into a compact 6-row swimlane table!
    bar_widths = [2.35, 2.10, 2.65, 2.25, 1.95, 1.75]
    for i, (cid, cname, clat, _, _, col) in enumerate(clusters):
        ry = 1.48 + i * 0.88
        sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 0.65, ry, 2.15, 0.72, SURFACE_1, f"!!cluster-{cid}",
           cname.split(" ")[0], size=12, color=WHITE, border=col)
        sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 2.90, ry + 0.14, bar_widths[i], 0.44, col, f"!!bar-{cid}",
           f"Shard {cid} Throughput", size=10, color=BG_BOOKEND)
        sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 5.65, ry + 0.14, 0.92, 0.44, SURFACE_2, f"!!lat-{cid}",
           clat, size=11, color=col)

    # Top-Right: Native Multi-Series PowerPoint Column Chart
    chart_data = CategoryChartData()
    chart_data.categories = ["Q1", "Q2", "Q3", "Q4"]
    chart_data.add_series("Optical Mesh (TB/s)", (9.2, 11.4, 13.1, 14.4))
    chart_data.add_series("Tail p99 (ms)", (3.8, 2.9, 2.1, 1.4))
    gf = s5.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(6.85), Inches(1.45), Inches(3.85), Inches(2.95),
        chart_data,
    )
    gf.name = "Telemetry Chart"

    # Top-Far-Right: Hero KPI Card with standalone number for counter odometer
    sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 10.85, 1.45, 1.85, 2.95, SURFACE_1, "Hero SLA Card", border=EMERALD)
    tb(s5, 10.95, 1.65, 1.65, 0.45, "Hero SLA Label", "GLOBAL MESH SLA", size=11, color=EMERALD, bold=True, align=PP_ALIGN.CENTER)
    tb(s5, 10.92, 2.35, 1.70, 0.85, "Hero SLA Number", "99.9%", size=32, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s5, 10.95, 3.35, 1.65, 0.80, "Hero SLA Foot", "Zero packet loss across 6 regions", size=10, color=MUTED, bold=False, align=PP_ALIGN.CENTER)

    # Bottom-Right: Two Interactive Trigger Buttons + Two Diagnostic Popup Panels
    sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 6.85, 4.65, 2.80, 0.62, ROSE, "Btn Failover",
       "Click: Inspect EU Failover", size=12, color=WHITE)
    sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 9.90, 4.65, 2.80, 0.62, VIOLET, "Btn Quota",
       "Click: Inspect Tensor Quota", size=12, color=WHITE)

    sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 6.85, 5.42, 2.80, 1.32, SURFACE_1, "Panel Failover",
       "EU-Central Rerouted in 0.4 ms\nOptical Ring B absorbed +18% load", size=11, color=WHITE, border=ROSE)
    sh(s5, MSO_SHAPE.ROUNDED_RECTANGLE, 9.90, 5.42, 2.80, 1.32, SURFACE_1, "Panel Quota",
       "Tensor Array Utilization: 94.2%\nSpeculative router saved 31% HBM", size=11, color=WHITE, border=VIOLET)
    s5.notes_slide.notes_text_frame.text = "Morph 18 cluster shapes into swimlanes, build the chart while rippling the swimlane bars, count up the SLA metric, and wire two interactive trigger buttons."

    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)


def build_directed_plan(model):
    inv = model["inventory"]
    return {
        "version": "0.6",
        "kind": "existing-deck-motion-director",
        "source": {
            "pptx_sha256": model["sha256"],
            "inventory_version": inv["version"],
            "source_slide_count": len(model["slides"]),
        },
        "user_instruction": "Create an ultra-detailed, high-difficulty 5-slide architectural animation deck demonstrating every advanced T024 capability.",
        "script": {
            "source": "speaker-notes",
            "summary": "Slide 1 auto-assembles a 22-shape silicon wafer constellation on slide start and orbits 360 deg on click 1. Slide 2 runs a 3D perspective elliptical carousel across five 6-part pods with 30ms follow-through inertia. Slide 3 explodes a 5-layer hardware stack, streams a 4-packet concurrent cascade swarm with node color flashes, and curves an audit probe around a thermal obstacle. Slides 4->5 morph 18 cluster topology objects into a 6-row swimlane dashboard with series chart builds, wave ripples, KPI counter, and dual interactiveSeq triggers.",
            "evidence": ["slide titles and multi-part geometry", "speaker notes", "!! Morph pairs", "chart and standalone number semantics"],
            "beats": [
                "slide 1: on-slide-start wafer constellation assembly + 360 orbit & counter-spin",
                "slide 2: 5x6-part pod assembly with follow-through + two 3D elliptical orbit steps + crimson spotlight + release",
                "slide 3: 5-layer isometric stack explosion + 4-packet braided cascade-flow + auto-arc obstacle bypass + release",
                "slide 4: 6-cluster mesh assembly + curved arc swap between US-East and EU-Central",
                "slide 5: 18-object Morph into swimlanes + chart build & bar wave + KPI counter + 2 interactiveSeq triggers",
            ],
        },
        "preservation": {
            "preserve_text_by_default": True,
            "preserve_media_by_default": True,
            "preserve_theme_by_default": True,
            "preserve_slide_order_by_default": True,
            "slide_count_policy": "preserve",
        },
        "transitions": [
            {
                "slide": 5,
                "kind": "morph",
                "duration_ms": 1600,
                "reason": "Continuity: 18 '!!cluster-*', '!!bar-*', and '!!lat-*' objects morph from the 2x3 spatial mesh on Slide 4 into the 6-row horizontal swimlane table on Slide 5.",
            }
        ],
        "slides": [
            # SLIDE 1
            {
                "source_index": 1,
                "role": "animated hero cover",
                "objective": "Assemble the silicon wafer constellation automatically on slide open, then orbit all 6 multi-part neural tiles on click 1.",
                "beats": [
                    {
                        "id": "s1-auto-die",
                        "purpose": "Zoom in the central NPU-X9 wafer die and outer ring automatically when the slide opens.",
                        "operation": "reveal",
                        "targets": ["Wafer Outer Ring", "Wafer Core Die", "Wafer Core Title", "Wafer Core Sub"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-slide-start",
                        "effect": "zoom",
                        "duration_ms": 500,
                    },
                    {
                        "id": "s1-auto-tiles",
                        "purpose": "Radially assemble all 6 multi-part Neural Engine tiles (24 rigged shapes) from the wafer core with 35ms follow-through inertia and bounce.",
                        "operation": "choreography",
                        "targets": ["Core Tile C1", "Core Tile C2", "Core Tile C3", "Core Tile C4", "Core Tile C5", "Core Tile C6"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "recipe": "assemble",
                        "motion_parameters": {"from": "center", "stagger_ms": 90, "duration_ms": 650, "bounce_end": 0.35, "follow_through_ms": 35},
                    },
                    {
                        "id": "s1-auto-kpis",
                        "purpose": "Reveal the 3 composite telemetry KPI cards along the bottom rail.",
                        "operation": "stagger-reveal",
                        "targets": [
                            "Card BW", "Card BW Bar", "Card BW Val", "Card BW Sub",
                            "Card E",  "Card E Bar",  "Card E Val",  "Card E Sub",
                            "Card SLA","Card SLA Bar","Card SLA Val","Card SLA Sub",
                        ],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "after-previous",
                        "effect": "float-in",
                        "duration_ms": 350,
                    },
                    {
                        "id": "s1-orbit-constellation",
                        "purpose": "Revolve all 6 multi-part Neural Engine tiles (24 rigged shapes) 360 degrees around Wafer Core Die.",
                        "operation": "choreography",
                        "targets": ["Wafer Core Die", "Core Tile C1", "Core Tile C2", "Core Tile C3", "Core Tile C4", "Core Tile C5", "Core Tile C6"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "orbit",
                        "motion_parameters": {"around_first": True, "angle_deg": 360, "duration_ms": 1500},
                    },
                    {
                        "id": "s1-counter-spin-ring",
                        "purpose": "Counter-spin the outer wafer ring -180 degrees while the neural tiles orbit clockwise.",
                        "operation": "rotate",
                        "targets": ["Wafer Outer Ring"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "motion_parameters": {"by_deg": -180, "duration_ms": 1500},
                    },
                ],
                "click_beats": [
                    {"id": "c1-auto", "purpose": "Auto-assemble wafer constellation and telemetry cards on slide open.", "motion_beats": ["s1-auto-die", "s1-auto-tiles", "s1-auto-kpis"], "stable_state": "Full cover layout assembled.", "pause_after": "presenter-explanation", "boundary_reason": "Plays automatically on slide start."},
                    {"id": "c1-orbit", "purpose": "Orbit the 6 neural engine tiles 360 degrees while counter-spinning the outer ring.", "motion_beats": ["s1-orbit-constellation", "s1-counter-spin-ring"], "stable_state": "Constellation completes full 360-degree orbital cycle.", "pause_after": "slide-complete", "boundary_reason": "Demonstrate live synchronous orbital motion on the cover."},
                ],
                "components": [],
            },
            # SLIDE 2
            {
                "source_index": 2,
                "role": "3D perspective elliptical carousel",
                "objective": "Walk 5 composite 6-part subsystem pods (30 rigged shapes) through 3D elliptical depth rotations, crimson spotlighting, and restoration.",
                "beats": [
                    {
                        "id": "s2-hub",
                        "purpose": "Reveal the central Policy Kernel hub.",
                        "operation": "reveal",
                        "targets": ["Kernel Hub", "Kernel Badge", "Kernel Title", "Kernel Sub"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "effect": "zoom",
                        "duration_ms": 450,
                    },
                    {
                        "id": "s2-assemble-pods",
                        "purpose": "Assemble all 5 6-part subsystem pods (30 rigged shapes) outward from the kernel with 30ms secondary follow-through inertia and elastic bounce.",
                        "operation": "choreography",
                        "targets": ["Pod Telemetry", "Pod WorldModel", "Pod RiskSolver", "Pod Shaper", "Pod SelfHeal"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "recipe": "assemble",
                        "motion_parameters": {"from": "center", "stagger_ms": 110, "duration_ms": 650, "bounce_end": 0.35, "follow_through_ms": 30},
                    },
                    {
                        "id": "s2-orbit3d-step1",
                        "purpose": "Rotate all 5 composite pods 1 station clockwise along the tilted 3D ellipse (foreground pods enlarge to 1.20x, background pods shrink to 0.80x and dim).",
                        "operation": "choreography",
                        "targets": ["Kernel Hub", "Pod Telemetry", "Pod WorldModel", "Pod RiskSolver", "Pod Shaper", "Pod SelfHeal"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "orbit-3d",
                        "motion_parameters": {"around_first": True, "steps": 1, "depth_scale": 0.20, "depth_dim": 0.48, "duration_ms": 950},
                    },
                    {
                        "id": "s2-orbit3d-step2",
                        "purpose": "Rotate all 5 composite pods a second station along the tilted 3D ellipse.",
                        "operation": "choreography",
                        "targets": ["Kernel Hub", "Pod Telemetry", "Pod WorldModel", "Pod RiskSolver", "Pod Shaper", "Pod SelfHeal"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "orbit-3d",
                        "motion_parameters": {"around_first": True, "steps": 1, "depth_scale": 0.20, "depth_dim": 0.48, "duration_ms": 950},
                    },
                    {
                        "id": "s2-spotlight-solver",
                        "purpose": "Spotlight Pod RiskSolver (enlarging all 6 of its rigged components and shifting its chassis color to crimson) while dimming the other 4 pods.",
                        "operation": "choreography",
                        "targets": ["Pod RiskSolver", "Pod Telemetry", "Pod WorldModel", "Pod Shaper", "Pod SelfHeal"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "spotlight",
                        "motion_parameters": {"scale": 1.18, "dim": 0.32, "color": "#E11D48", "duration_ms": 550},
                    },
                    {
                        "id": "s2-release-all",
                        "purpose": "Restore all 5 composite pods (30 shapes) to their authored ring positions, 1.0x scale, and 100% opacity.",
                        "operation": "choreography",
                        "targets": ["Pod Telemetry", "Pod WorldModel", "Pod RiskSolver", "Pod Shaper", "Pod SelfHeal"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "release",
                        "motion_parameters": {"duration_ms": 600},
                    },
                ],
                "click_beats": [
                    {"id": "c2-1", "purpose": "Introduce the Policy Kernel and assemble the 5 composite pods with follow-through inertia.", "motion_beats": ["s2-hub", "s2-assemble-pods"], "stable_state": "Kernel and 5 pods (34 shapes) assembled.", "pause_after": "presenter-explanation", "boundary_reason": "First reveal on this slide."},
                    {"id": "c2-2", "purpose": "Advance the 3D elliptical carousel by 1 step.", "motion_beats": ["s2-orbit3d-step1"], "stable_state": "Pods rotated 1 step with 3D perspective depth scaling.", "pause_after": "presenter-explanation", "boundary_reason": "Inspect the first orbital transition."},
                    {"id": "c2-3", "purpose": "Advance the 3D elliptical carousel by a 2nd step.", "motion_beats": ["s2-orbit3d-step2"], "stable_state": "Pods rotated 2 steps in 3D perspective depth.", "pause_after": "presenter-explanation", "boundary_reason": "Bring the solver/shaper pods into foreground focus."},
                    {"id": "c2-4", "purpose": "Spotlight Pod RiskSolver with crimson color shift.", "motion_beats": ["s2-spotlight-solver"], "stable_state": "Pod RiskSolver enlarged and highlighted; others dimmed.", "pause_after": "presenter-explanation", "boundary_reason": "Deep-dive into the counterfactual solver."},
                    {"id": "c2-5", "purpose": "Restore the full 5-pod ring.", "motion_beats": ["s2-release-all"], "stable_state": "All 30 pod shapes restored to authored geometry.", "pause_after": "slide-complete", "boundary_reason": "Close the loop."},
                ],
                "components": [],
            },
            # SLIDE 3
            {
                "source_index": 3,
                "role": "exploded 5-layer stack & 4-packet concurrent swarm",
                "objective": "Explode the 5-layer silicon stack (30 rigged shapes), stream 4 concurrent data packets through Relays R1-R4 with arrival color flashes, and arc Audit Probe around Thermal Obstacle.",
                "beats": [
                    {
                        "id": "s3-explode-stack",
                        "purpose": "Explode all 5 architectural strata (30 rigged shapes) along an isometric axis with staggered bounce and follow-through.",
                        "operation": "choreography",
                        "targets": ["Layer L1", "Layer L2", "Layer L3", "Layer L4", "Layer L5"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "explode-layers",
                        "motion_parameters": {"axis": "iso", "spread": 0.14, "stagger_ms": 80, "duration_ms": 650, "bounce_end": 0.30, "follow_through_ms": 25},
                    },
                    {
                        "id": "s3-swarm-cascade",
                        "purpose": "Launch 4 concurrent data packets (PKT-1..PKT-4) in a braided swarm through Relays R1->R2->R3->R4, flashing each relay cyan upon arrival.",
                        "operation": "choreography",
                        "targets": ["Swarm PKT-1", "Swarm PKT-2", "Swarm PKT-3", "Swarm PKT-4", "Relay R1", "Relay R2", "Relay R3", "Relay R4"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "cascade-flow",
                        "motion_parameters": {"token_count": 4, "stagger_ms": 110, "hop_ms": 380, "arc": 0.16, "offset_y": -0.072, "token_spread_x": 0.036, "stage_color": "#06B6D4"},
                    },
                    {
                        "id": "s3-obstacle-bypass",
                        "purpose": "Route Audit Probe to Telemetry Sink; auto_avoid automatically curves the path over Thermal Obstacle.",
                        "operation": "choreography",
                        "targets": ["Audit Probe", "Telemetry Sink"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "travel",
                        "motion_parameters": {"arc": 0.0, "offset_y": -0.11, "auto_avoid": True, "duration_ms": 850},
                    },
                    {
                        "id": "s3-obstacle-teeter",
                        "purpose": "Rock Thermal Obstacle with a teeter emphasis as Audit Probe arcs past it.",
                        "operation": "emphasize",
                        "targets": ["Thermal Obstacle"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "effect": "teeter",
                        "duration_ms": 600,
                        "motion_parameters": {"by_deg": 4.0},
                    },
                    {
                        "id": "s3-release-stack",
                        "purpose": "Re-collapse the 5 exploded layers and return all packets/probes to their authored positions.",
                        "operation": "choreography",
                        "targets": ["Layer L1", "Layer L2", "Layer L3", "Layer L4", "Layer L5", "Swarm PKT-1", "Swarm PKT-2", "Swarm PKT-3", "Swarm PKT-4", "Audit Probe"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "release",
                        "motion_parameters": {"duration_ms": 600},
                    },
                ],
                "click_beats": [
                    {"id": "c3-1", "purpose": "Explode the 5-layer hardware stack.", "motion_beats": ["s3-explode-stack"], "stable_state": "5 layers (30 shapes) separated along isometric diagonal.", "pause_after": "presenter-explanation", "boundary_reason": "First reveal on this slide."},
                    {"id": "c3-2", "purpose": "Stream 4 concurrent packets through the 4 relay stages.", "motion_beats": ["s3-swarm-cascade"], "stable_state": "All 4 packets complete 4-hop cascade; relays pulsed and flashed cyan.", "pause_after": "presenter-explanation", "boundary_reason": "Demonstrate multi-token concurrent swarm flow."},
                    {"id": "c3-3", "purpose": "Bypass Thermal Obstacle via auto-arc trajectory solver.", "motion_beats": ["s3-obstacle-bypass", "s3-obstacle-teeter"], "stable_state": "Audit Probe lands above Telemetry Sink with zero mid-flight collision.", "pause_after": "presenter-explanation", "boundary_reason": "Show obstacle-avoiding routing."},
                    {"id": "c3-4", "purpose": "Re-compress stack and reset tokens.", "motion_beats": ["s3-release-stack"], "stable_state": "All 45 shapes restored to authored layout.", "pause_after": "slide-complete", "boundary_reason": "Conclude exploded view."},
                ],
                "components": [],
            },
            # SLIDE 4
            {
                "source_index": 4,
                "role": "spatial cluster topology before Morph",
                "objective": "Assemble the 6 regional clusters (24 rigged shapes) and swap US-East with EU-Central on curved arcs before morphing into Slide 5.",
                "beats": [
                    {
                        "id": "s4-assemble-mesh",
                        "purpose": "Assemble all 6 regional cluster pods (with their rigged !!bar-* and !!lat-* children) outward from the Anycast Core.",
                        "operation": "choreography",
                        "targets": ["!!cluster-1", "!!cluster-2", "!!cluster-3", "!!cluster-4", "!!cluster-5", "!!cluster-6"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "assemble",
                        "motion_parameters": {"from": "slide-center", "stagger_ms": 90, "duration_ms": 650, "bounce_end": 0.30, "follow_through_ms": 25},
                    },
                    {
                        "id": "s4-swap-clusters",
                        "purpose": "Swap !!cluster-2 (US-East) and !!cluster-3 (EU-Central) along opposite arcs during failover re-ranking.",
                        "operation": "choreography",
                        "targets": ["!!cluster-2", "!!cluster-3"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "recipe": "swap",
                        "motion_parameters": {"arc": 0.25, "duration_ms": 750},
                    },
                ],
                "click_beats": [
                    {"id": "c4-1", "purpose": "Assemble the 6 regional cluster pods.", "motion_beats": ["s4-assemble-mesh"], "stable_state": "All 6 regional clusters visible.", "pause_after": "presenter-explanation", "boundary_reason": "First reveal on this slide."},
                    {"id": "c4-2", "purpose": "Swap US-East and EU-Central priority positions.", "motion_beats": ["s4-swap-clusters"], "stable_state": "US-East and EU-Central exchanged; ready for cross-slide Morph.", "pause_after": "slide-complete", "boundary_reason": "Prepare failover order before morphing to swimlanes."},
                ],
                "components": [],
            },
            # SLIDE 5
            {
                "source_index": 5,
                "role": "morphed swimlane console, chart build, wave & dual interactiveSeq",
                "objective": "Let the 18 !! objects glide in via Morph, build the multi-series chart while rippling the swimlane bars, count up the hero SLA metric, and wire two interactive trigger buttons.",
                "beats": [
                    {
                        "id": "s5-chart-build",
                        "purpose": "Build the multi-series Telemetry Chart series by series.",
                        "operation": "chart-build",
                        "targets": ["Telemetry Chart"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "data_motion": {
                            "kind": "chart",
                            "chart_type": "column",
                            "recipe": "baseline-grow",
                            "build": "series",
                            "animate_background": False,
                            "rationale": "Compare Optical Mesh throughput growth against tail latency reduction series by series.",
                        },
                    },
                    {
                        "id": "s5-swimlane-wave",
                        "purpose": "Propagate a synchronized wave ripple across the 6 morphed swimlane load bars as the chart builds.",
                        "operation": "choreography",
                        "targets": ["!!bar-1", "!!bar-2", "!!bar-3", "!!bar-4", "!!bar-5", "!!bar-6"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "recipe": "wave",
                        "motion_parameters": {"stagger_ms": 90, "amplitude": 0.025, "scale": 1.08, "duration_ms": 500},
                    },
                    {
                        "id": "s5-sla-card-reveal",
                        "purpose": "Reveal the Hero SLA Card frame and labels.",
                        "operation": "reveal",
                        "targets": ["Hero SLA Card", "Hero SLA Label", "Hero SLA Foot", "Btn Failover", "Btn Quota"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "effect": "zoom",
                        "duration_ms": 450,
                    },
                    {
                        "id": "s5-sla-counter",
                        "purpose": "Reveal and pulse the 99.9% Hero SLA Number with emerald color emphasis.",
                        "operation": "reveal",
                        "targets": ["Hero SLA Number"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "with-previous",
                        "effect": "zoom",
                        "duration_ms": 500,
                    },
                    {
                        "id": "s5-sla-pulse",
                        "purpose": "Pulse Hero SLA Number after it lands.",
                        "operation": "focus",
                        "targets": ["Hero SLA Number"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "after-previous",
                        "effect": "pulse",
                        "duration_ms": 350,
                    },
                    {
                        "id": "s5-trig-failover",
                        "purpose": "Pop open Panel Failover when presenter clicks Btn Failover.",
                        "operation": "reveal",
                        "targets": ["Panel Failover"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "effect": "zoom",
                        "duration_ms": 450,
                    },
                    {
                        "id": "s5-trig-quota",
                        "purpose": "Pop open Panel Quota when presenter clicks Btn Quota.",
                        "operation": "reveal",
                        "targets": ["Panel Quota"],
                        "reuse_existing": True,
                        "same_slide": True,
                        "timing_intent": "on-click",
                        "effect": "zoom",
                        "duration_ms": 450,
                    },
                ],
                "click_beats": [
                    {"id": "c5-1", "purpose": "Build the multi-series telemetry chart and ripple the 6 morphed swimlane bars.", "motion_beats": ["s5-chart-build", "s5-swimlane-wave"], "stable_state": "Chart series built and swimlane bars rippled.", "pause_after": "presenter-explanation", "boundary_reason": "First reveal after the Morph transition."},
                    {"id": "c5-2", "purpose": "Reveal the Hero SLA Card with stepped-text counter and interactive buttons.", "motion_beats": ["s5-sla-card-reveal", "s5-sla-counter", "s5-sla-pulse"], "stable_state": "Hero SLA counted up to 99.9%; interactive buttons ready.", "pause_after": "presenter-explanation", "boundary_reason": "Land the headline SLA metric."},
                    {"id": "c5-trig-1", "purpose": "Interactive drill-down on EU Failover.", "trigger_shape": "Btn Failover", "motion_beats": ["s5-trig-failover"], "stable_state": "Panel Failover visible.", "pause_after": "presenter-explanation", "boundary_reason": "Triggered by clicking Btn Failover."},
                    {"id": "c5-trig-2", "purpose": "Interactive drill-down on Tensor Quota.", "trigger_shape": "Btn Quota", "motion_beats": ["s5-trig-quota"], "stable_state": "Panel Quota visible.", "pause_after": "slide-complete", "boundary_reason": "Triggered by clicking Btn Quota."},
                ],
                "components": [],
            },
        ],
        "target_slide_count": len(model["slides"]),
        "research_metadata": {
            "sources": [],
            "draft_notes": {},
            "style": "cinematic",
            "drafted_by": "T024 high-complexity showcase",
        },
    }


def main():
    exp_dir = Path(__file__).resolve().parent
    src_pptx = exp_dir / "output" / "T024_complex_motion_source.pptx"
    dir_pptx = exp_dir / "output" / "T024_complex_motion_directed.pptx"
    auto_pptx = exp_dir / "output" / "T024_complex_motion_auto.pptx"

    build_source_deck(src_pptx)
    model = md.deck_model(src_pptx)
    total_shapes = sum(len(s["objects"]) for s in model["slides"])

    # 1. Autonomous cinematic draft + apply
    auto_plan = md.draft(model, style="cinematic")
    (exp_dir / "auto-cinematic-plan.json").write_text(json.dumps(auto_plan, indent=2) + "\n", encoding="utf-8")
    auto_report = md.apply(src_pptx, auto_plan, auto_pptx, force=True)
    (exp_dir / "auto-cinematic.report.md").write_text(md.markdown_report(auto_report, auto_plan) + "\n", encoding="utf-8")

    # 2. Directed high-complexity T024 plan + apply
    d_plan = build_directed_plan(model)
    (exp_dir / "directed-plan.json").write_text(json.dumps(d_plan, indent=2) + "\n", encoding="utf-8")
    d_report = md.apply(src_pptx, d_plan, dir_pptx, force=True)
    (exp_dir / "directed.report.md").write_text(md.markdown_report(d_report, d_plan) + "\n", encoding="utf-8")

    # 3. LibreOffice timing crosscheck & RGB render identity check
    lo = crosscheck(dir_pptx)
    (exp_dir / "lo-crosscheck-directed.json").write_text(json.dumps(lo, indent=2) + "\n", encoding="utf-8")
    ri = compare(src_pptx, dir_pptx)
    (exp_dir / "render-identity-directed.json").write_text(json.dumps(ri, indent=2) + "\n", encoding="utf-8")

    # 4. Render simulated motion GIFs + key-state contact sheets for all 5 slides
    previews = []
    for s_idx in (1, 2, 3, 4, 5):
        gif_path = exp_dir / "preview" / f"slide-0{s_idx}.gif"
        png_path = exp_dir / "preview" / f"slide-0{s_idx}.png"
        previews.append(render_slide_motion(dir_pptx, s_idx, gif_path, fps=6, sheet=png_path))
    (exp_dir / "preview-manifest.json").write_text(json.dumps(previews, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": d_report["ok"],
        "problems": d_report["problems"],
        "warnings": d_report["warnings"],
        "total_native_shapes": total_shapes,
        "identical_slides": ri["identical_slides"],
    }, indent=2))


if __name__ == "__main__":
    main()
