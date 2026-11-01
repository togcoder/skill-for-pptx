"""Advanced Presentation Interactivity Engine for PowerPoint (T049).

Antigravity multi-domain design research lab.
Extends baseline slide branching (T048) with high-level in-slide interactivity:
1. In-Slide Lightbox Modal Dialogs: Overlay backdrop dimmer + modal dialog card + close button
   triggered natively on the SAME slide via <p:cTn nodeType="interactiveSeq"> without jarring slide switches.
2. In-Slide Multi-Tab Switcher: 2-5 tab buttons seamlessly toggling content panels on a single slide.
3. Tactile Sound Effects on Actions: Native <a:snd> audio embedding in <a:hlinkClick> and <a:hlinkHover>,
   backed by pure-Python synthetic PCM WAV assets (clicks, chimes, buzzers) with zero external dependencies.
4. Interactive Hover States & Tooltips: Mouse-over actions and sound feedback (<a:hlinkHover>).
5. Gamified Choice & Decision Engine: Instant feedback loops with tactile sound effects.
6. Morph-Powered Fluid Visual Navigation: Seamless 60fps object interpolation across states.
7. Comprehensive inspection and auditing of presentation interactivity.
"""

from __future__ import annotations

import io
import math
import struct
import wave
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from lxml import etree as ET

try:
    from . import pptx_animator as pa
    from . import slide_navigator as sn
except ImportError:
    import pptx_animator as pa
    import slide_navigator as sn

# XML Namespaces
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"

NAMESPACES = {
    "p": NS_P,
    "a": NS_A,
    "r": NS_R,
    "rel": NS_REL,
    "ct": NS_CT,
    "p14": NS_P14,
}


# ==============================================================================
# 1. PURE-PYTHON AUDIO SYNTHESIS & PACKAGE EMBEDDING
# ==============================================================================

def synthesize_ui_sound(sound_type: str = "click", sample_rate: int = 44100) -> bytes:
    """Synthesize clean, pristine 16-bit mono PCM WAV audio using only Python standard library.
    
    Supported types:
    - 'click': 40ms, 1200Hz punchy tactile UI click with exponential decay.
    - 'chime': 350ms harmonic major triad (C5=523Hz, E5=659Hz, G5=784Hz) with smooth bell envelope.
    - 'buzz': 250ms low 140Hz buzzer with harmonic edge for incorrect/alert feedback.
    - 'tap': 25ms subtle 800Hz gentle tactile tap.
    """
    buf = io.BytesIO()
    
    if sound_type == "click":
        duration_s = 0.04
        freqs = [1200.0, 2400.0]
        decay_factor = 3.5
        volume = 0.45
    elif sound_type == "chime":
        duration_s = 0.35
        freqs = [523.25, 659.25, 783.99]
        decay_factor = 2.8
        volume = 0.50
    elif sound_type == "buzz":
        duration_s = 0.25
        freqs = [140.0, 280.0, 420.0]
        decay_factor = 1.8
        volume = 0.40
    elif sound_type == "tap":
        duration_s = 0.025
        freqs = [800.0]
        decay_factor = 4.0
        volume = 0.35
    else:
        duration_s = 0.04
        freqs = [1000.0]
        decay_factor = 3.0
        volume = 0.40

    n_samples = int(sample_rate * duration_s)
    
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            env = math.exp(-decay_factor * t / duration_s)
            val = sum(math.sin(2.0 * math.pi * f * t) for f in freqs) / len(freqs)
            sample = int(val * volume * env * 32767.0)
            sample = max(-32768, min(32767, sample))
            frames.extend(struct.pack("<h", sample))
            
        wav.writeframes(frames)
        
    return buf.getvalue()


def embed_package_sound(
    files: Dict[str, bytes],
    wav_bytes: bytes,
    sound_filename: str,
    slide_filename: str
) -> str:
    """Embeds a WAV audio asset into the PPTX package and registers it for a specific slide.
    
    1. Writes to ppt/media/<sound_filename>.
    2. Registers .wav in [Content_Types].xml.
    3. Adds an audio relationship to ppt/slides/_rels/<slide_filename>.rels.
    
    Returns:
        The allocated relationship ID (e.g. 'rId9').
    """
    media_path = f"ppt/media/{sound_filename}"
    files[media_path] = wav_bytes

    # Ensure [Content_Types].xml has .wav registration
    if "[Content_Types].xml" in files:
        ct_tree = ET.fromstring(files["[Content_Types].xml"])
        has_wav = False
        for d in ct_tree.findall(f"{{{NS_CT}}}Default"):
            if d.get("Extension", "").lower() == "wav":
                has_wav = True
                break
        if not has_wav:
            ET.SubElement(
                ct_tree,
                f"{{{NS_CT}}}Default",
                Extension="wav",
                ContentType="audio/wav"
            )
            files["[Content_Types].xml"] = ET.tostring(
                ct_tree, xml_declaration=True, encoding="utf-8", standalone=True
            )

    # Add relationship to slide rels
    rels_path = f"ppt/slides/_rels/{slide_filename}.rels"
    if rels_path in files:
        rels_tree = ET.fromstring(files[rels_path])
    else:
        rels_tree = ET.Element(f"{{{NS_REL}}}Relationships")

    # Find highest existing rId
    r_ids = []
    for r in rels_tree.findall(f"{{{NS_REL}}}Relationship"):
        rid = r.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            r_ids.append(int(rid[3:]))
            
    next_rid = f"rId{max(r_ids, default=0) + 1}"
    
    # Check if target media already registered in this rels
    existing_rid = None
    target_rel = f"../media/{sound_filename}"
    for r in rels_tree.findall(f"{{{NS_REL}}}Relationship"):
        if r.get("Target") == target_rel:
            existing_rid = r.get("Id")
            break
            
    if existing_rid:
        return existing_rid

    ET.SubElement(
        rels_tree,
        f"{{{NS_REL}}}Relationship",
        Id=next_rid,
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio",
        Target=target_rel
    )
    files[rels_path] = ET.tostring(
        rels_tree, xml_declaration=True, encoding="utf-8", standalone=True
    )
    return next_rid


# ==============================================================================
# 2. SHAPE ACTION & SOUND BINDING
# ==============================================================================

def attach_click_sound_and_action(
    slide_tree: ET.Element,
    spid: Union[str, int],
    sound_rid: Optional[str] = None,
    sound_name: Optional[str] = None,
    action: str = "ppaction://noaction",
    target_slide_rid: Optional[str] = None
) -> bool:
    """Attaches a click action and optional audio sound effect to a shape's cNvPr."""
    spid_str = str(spid)
    target_shape = None
    
    for sp in slide_tree.iter():
        if sp.tag in (f"{{{NS_P}}}sp", f"{{{NS_P}}}pic", f"{{{NS_P}}}graphicFrame", f"{{{NS_P}}}grpSp"):
            cnvpr = sp.find(f".//{{{NS_P}}}cNvPr")
            if cnvpr is not None and cnvpr.get("id") == spid_str:
                target_shape = cnvpr
                break
                
    if target_shape is None:
        return False

    hlink = target_shape.find(f"{{{NS_A}}}hlinkClick")
    if hlink is None:
        hlink = ET.SubElement(target_shape, f"{{{NS_A}}}hlinkClick")

    if action:
        hlink.set("action", action)
    if target_slide_rid:
        hlink.set(f"{{{NS_R}}}id", target_slide_rid)

    if sound_rid and sound_name:
        # Clear existing snd if any
        for snd in hlink.findall(f"{{{NS_A}}}snd"):
            hlink.remove(snd)
        snd_el = ET.SubElement(hlink, f"{{{NS_A}}}snd", name=sound_name)
        snd_el.set(f"{{{NS_R}}}embed", sound_rid)

    return True


def attach_hover_sound_and_action(
    slide_tree: ET.Element,
    spid: Union[str, int],
    sound_rid: Optional[str] = None,
    sound_name: Optional[str] = None,
    action: str = "ppaction://noaction",
    target_slide_rid: Optional[str] = None
) -> bool:
    """Attaches a mouse-over (hover) action and optional sound effect to a shape's cNvPr."""
    spid_str = str(spid)
    target_shape = None
    
    for sp in slide_tree.iter():
        if sp.tag in (f"{{{NS_P}}}sp", f"{{{NS_P}}}pic", f"{{{NS_P}}}graphicFrame", f"{{{NS_P}}}grpSp"):
            cnvpr = sp.find(f".//{{{NS_P}}}cNvPr")
            if cnvpr is not None and cnvpr.get("id") == spid_str:
                target_shape = cnvpr
                break
                
    if target_shape is None:
        return False

    hover = target_shape.find(f"{{{NS_A}}}hlinkHover")
    if hover is None:
        hover = ET.SubElement(target_shape, f"{{{NS_A}}}hlinkHover")

    if action:
        hover.set("action", action)
    if target_slide_rid:
        hover.set(f"{{{NS_R}}}id", target_slide_rid)

    if sound_rid and sound_name:
        for snd in hover.findall(f"{{{NS_A}}}snd"):
            hover.remove(snd)
        snd_el = ET.SubElement(hover, f"{{{NS_A}}}snd", name=sound_name)
        snd_el.set(f"{{{NS_R}}}embed", sound_rid)

    return True


# ==============================================================================
# 3. IN-SLIDE LIGHTBOX MODAL DIALOGS
# ==============================================================================

def build_in_slide_modal_click_groups(
    trigger_spid: Union[str, int],
    modal_spids: List[Union[str, int]],
    close_spid: Union[str, int],
    entrance_preset: str = "zoom",
    exit_preset: str = "fade-out",
    duration_ms: int = 250
) -> List[Dict[str, Any]]:
    """Generates the click groups specification for an In-Slide Lightbox Modal Dialog.
    
    - Open Trigger: Clicking trigger_spid triggers entrance animations for all modal_spids.
    - Close Trigger: Clicking close_spid triggers exit animations for all modal_spids.
    
    Returns:
        List of click group dicts formatted for `pptx_animator.apply_timeline`.
    """
    trig_str = str(trigger_spid)
    close_str = str(close_spid)
    modal_strs = [str(s) for s in modal_spids]
    
    # 1. Open group
    open_effects = []
    for i, s in enumerate(modal_strs):
        eff_preset = entrance_preset
        # If dimmer is among spids, fade it in smoothly
        if i == 0 and entrance_preset == "zoom":
            eff_preset = "fade"
        open_effects.append({
            "preset": eff_preset,
            "spid": s,
            "trigger": "click" if i == 0 else "with",
            "duration_ms": duration_ms
        })
        
    open_click = {
        "id": f"open_modal_{trig_str}",
        "start": "click",
        "trigger_spid": trig_str,
        "effects": open_effects
    }
    
    # 2. Close group
    close_effects = []
    for i, s in enumerate(modal_strs):
        close_effects.append({
            "preset": exit_preset,
            "spid": s,
            "trigger": "click" if i == 0 else "with",
            "duration_ms": max(100, duration_ms - 50)
        })
        
    close_click = {
        "id": f"close_modal_{close_str}",
        "start": "click",
        "trigger_spid": close_str,
        "effects": close_effects
    }
    
    return [open_click, close_click]


# ==============================================================================
# 4. IN-SLIDE MULTI-TAB SWITCHER
# ==============================================================================

def build_tab_switcher_click_groups(
    tabs: List[Dict[str, Any]],
    transition_preset: str = "fade",
    duration_ms: int = 200
) -> List[Dict[str, Any]]:
    """Generates click groups for an In-Slide Multi-Tab Switcher.
    
    Args:
        tabs: List of dicts, each with:
              - 'btn_spid': spid of the tab button
              - 'panel_spids': list of spids belonging to this tab's content panel
        transition_preset: entrance preset ('fade', 'appear', etc.)
        duration_ms: animation duration
        
    Returns:
        List of click group dicts formatted for `pptx_animator.apply_timeline`.
    """
    clicks = []
    all_panels = []
    for t in tabs:
        all_panels.append([str(s) for s in t["panel_spids"]])
        
    for i, t in enumerate(tabs):
        btn_spid = str(t["btn_spid"])
        this_panel = [str(s) for s in t["panel_spids"]]
        
        effects = []
        # 1. Exit other panels first (fast disappear / fade-out)
        exit_count = 0
        for j, other_panel in enumerate(all_panels):
            if j == i:
                continue
            for s in other_panel:
                effects.append({
                    "preset": "disappear" if transition_preset == "appear" else "fade-out",
                    "spid": s,
                    "trigger": "click" if exit_count == 0 else "with",
                    "duration_ms": max(50, duration_ms // 2)
                })
                exit_count += 1
                
        # 2. Enter this tab's panel
        for k, s in enumerate(this_panel):
            effects.append({
                "preset": transition_preset,
                "spid": s,
                "trigger": "with" if exit_count > 0 or k > 0 else "click",
                "duration_ms": duration_ms
            })
            
        clicks.append({
            "id": f"tab_switch_{i}_{btn_spid}",
            "start": "click",
            "trigger_spid": btn_spid,
            "effects": effects
        })
        
    return clicks


# ==============================================================================
# 5. GAMIFIED CHOICE & DECISION STATE ENGINE
# ==============================================================================

def build_decision_choice_click_groups(
    choices: List[Dict[str, Any]],
    feedback_duration_ms: int = 250
) -> List[Dict[str, Any]]:
    """Generates interactive click groups for a multiple-choice challenge.
    
    Args:
        choices: List of dicts:
                 - 'btn_spid': shape ID of the button/choice option
                 - 'feedback_spids': list of shape IDs to reveal upon click (e.g. Success/Fail modal)
                 - 'is_correct': bool
    """
    clicks = []
    for i, c in enumerate(choices):
        btn_spid = str(c["btn_spid"])
        feedback_spids = [str(s) for s in c["feedback_spids"]]
        
        effects = []
        preset = "zoom" if c.get("is_correct") else "fade"
        for j, s in enumerate(feedback_spids):
            effects.append({
                "preset": preset,
                "spid": s,
                "trigger": "click" if j == 0 else "with",
                "duration_ms": feedback_duration_ms
            })
            
        clicks.append({
            "id": f"decision_choice_{i}_{btn_spid}",
            "start": "click",
            "trigger_spid": btn_spid,
            "effects": effects
        })
        
    return clicks


# ==============================================================================
# 6. MORPH-POWERED FLUID NAVIGATION TRANSITION
# ==============================================================================

def configure_slide_morph_transition(
    slide_tree: ET.Element,
    duration_ms: int = 750
) -> None:
    """Configures a native PowerPoint Morph transition on the slide."""
    # Transitions live under <p:transition> in slide root
    transition = slide_tree.find(f"{{{NS_P}}}transition")
    if transition is None:
        # Must be placed before <p:timing> or <p:extLst>
        timing = slide_tree.find(f"{{{NS_P}}}timing")
        ext_lst = slide_tree.find(f"{{{NS_P}}}extLst")
        transition = ET.Element(f"{{{NS_P}}}transition")
        if timing is not None:
            timing.addprevious(transition)
        elif ext_lst is not None:
            ext_lst.addprevious(transition)
        else:
            slide_tree.append(transition)

    transition.set("spd", "med")
    
    # Morph is an extension element: <p14:morph xmlns:p14="..."/>
    # Clear existing transitions inside
    for child in list(transition):
        transition.remove(child)
        
    morph = ET.SubElement(transition, f"{{{NS_P14}}}morph")
    morph.set("option", "byObject")


# ==============================================================================
# 7. INSPECTION & AUDITING
# ==============================================================================

def inspect_interactivity(pptx_path: Union[str, Path]) -> Dict[str, Any]:
    """Inspects a presentation and extracts all advanced interactive features."""
    p = Path(pptx_path)
    if not p.is_file():
        raise FileNotFoundError(f"Presentation not found: {p}")

    report = {
        "ok": True,
        "path": str(p),
        "total_slides": 0,
        "interactive_sequences_count": 0,
        "sound_effects_count": 0,
        "hover_actions_count": 0,
        "morph_slides_count": 0,
        "slides": []
    }

    with zipfile.ZipFile(p, "r") as z:
        namelist = z.namelist()
        
        # Discover slide files
        slide_files = sorted(
            [n for n in namelist if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
            key=lambda x: int(x.replace("ppt/slides/slide", "").replace(".xml", "")) if x.replace("ppt/slides/slide", "").replace(".xml", "").isdigit() else 999
        )
        report["total_slides"] = len(slide_files)

        for s_file in slide_files:
            s_tree = ET.fromstring(z.read(s_file))
            slide_data = {
                "file": s_file,
                "interactive_sequences": [],
                "sound_actions": [],
                "hover_actions": [],
                "has_morph": False
            }

            # Check Morph transition
            morph_el = s_tree.find(f".//{{{NS_P14}}}morph")
            if morph_el is not None:
                slide_data["has_morph"] = True
                report["morph_slides_count"] += 1

            # Check Sound & Hover actions on shapes
            for sp in s_tree.iter():
                if sp.tag in (f"{{{NS_P}}}sp", f"{{{NS_P}}}pic", f"{{{NS_P}}}graphicFrame", f"{{{NS_P}}}grpSp"):
                    cnvpr = sp.find(f".//{{{NS_P}}}cNvPr")
                    if cnvpr is None:
                        continue
                    spid = cnvpr.get("id")
                    sp_name = cnvpr.get("name", "")
                    
                    # Click sound
                    hlink = cnvpr.find(f"{{{NS_A}}}hlinkClick")
                    if hlink is not None:
                        snd = hlink.find(f"{{{NS_A}}}snd")
                        if snd is not None:
                            slide_data["sound_actions"].append({
                                "spid": spid,
                                "shape_name": sp_name,
                                "type": "click",
                                "sound_name": snd.get("name"),
                                "embed_id": snd.get(f"{{{NS_R}}}embed")
                            })
                            report["sound_effects_count"] += 1

                    # Hover action & sound
                    hover = cnvpr.find(f"{{{NS_A}}}hlinkHover")
                    if hover is not None:
                        snd_h = hover.find(f"{{{NS_A}}}snd")
                        slide_data["hover_actions"].append({
                            "spid": spid,
                            "shape_name": sp_name,
                            "action": hover.get("action"),
                            "sound_name": snd_h.get("name") if snd_h is not None else None
                        })
                        report["hover_actions_count"] += 1

            # Check Interactive Sequences in timing
            timing = s_tree.find(f"{{{NS_P}}}timing")
            if timing is not None:
                for seq in timing.iter(f"{{{NS_P}}}seq"):
                    ctn = seq.find(f"{{{NS_P}}}cTn[@nodeType='interactiveSeq']")
                    if ctn is None:
                        continue
                    tgt = seq.find(f"{{{NS_P}}}nextCondLst/{{{NS_P}}}cond/{{{NS_P}}}tgtEl/{{{NS_P}}}spTgt")
                    trigger_spid = tgt.get("spid") if tgt is not None else None
                    
                    # Count effects
                    effects = []
                    for c in ctn.iter(f"{{{NS_P}}}cTn"):
                        sp_tgt = c.find(f".//{{{NS_P}}}spTgt")
                        if sp_tgt is not None:
                            effects.append(sp_tgt.get("spid"))
                            
                    slide_data["interactive_sequences"].append({
                        "trigger_spid": trigger_spid,
                        "animated_spids": list(set(effects))
                    })
                    report["interactive_sequences_count"] += 1

            report["slides"].append(slide_data)

    return report


# ==============================================================================
# 8. HIGH-LEVEL SHOWCASE DECK COMPILER
# ==============================================================================

def compile_advanced_interactive_showcase(
    output_path: Union[str, Path]
) -> Dict[str, Any]:
    """Compiles a complete 4-slide showcase demonstrating all advanced interactive paradigms.
    
    Slide 1: Executive KPI Dashboard with In-Slide Lightbox Modal Dialog (Zero slide switch).
    Slide 2: Unified Product Architecture with In-Slide 3-Tab Switcher.
    Slide 3: Interactive Decision Assessment with Sound FX (Ding on correct, Buzz on wrong).
    Slide 4: Twin-Morph Fluid Navigation.
    """
    import pptx
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches, Pt

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palette
    C_BG = RGBColor(15, 23, 42)          # Slate 900
    C_CARD = RGBColor(30, 41, 59)        # Slate 800
    C_ACCENT = RGBColor(56, 189, 248)    # Sky 400
    C_SUCCESS = RGBColor(34, 197, 94)    # Emerald 500
    C_DANGER = RGBColor(239, 68, 68)     # Red 500
    C_TEXT = RGBColor(248, 250, 252)     # Slate 50
    C_MUTED = RGBColor(148, 163, 184)    # Slate 400

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    # --------------------------------------------------------------------------
    # SLIDE 1: Executive Dashboard with In-Slide Modal Dialog
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    t1 = s1.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf1 = t1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "EXECUTIVE DASHBOARD • IN-SLIDE MODAL DEMO"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT

    sub1 = tf1.add_paragraph()
    sub1.text = "Nhấp vào nút [Chi Tiết] để mở Lightbox Modal trực tiếp trong slide (không đổi slide, không giật màn hình)."
    sub1.font.size = Pt(13)
    sub1.font.color.rgb = C_MUTED

    # 3 Baseline KPI Cards
    kpis = [
        ("TĂNG TRƯỞNG DOANH THU", "+142.8%", "Vượt mục tiêu Q3 toàn tập đoàn", C_SUCCESS),
        ("TỶ LỆ GIỮ CHÂN (NDR)", "128.4%", "Chỉ số mở rộng phân khúc Enterprise", C_ACCENT),
        ("CHI PHÍ VẬN HÀNH (OPEX)", "$4.2M", "Tối ưu hóa -18% so với ngân sách", C_TEXT),
    ]

    for idx, (label, val, desc, val_color) in enumerate(kpis):
        x = Inches(0.8 + idx * 3.95)
        y = Inches(1.8)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.8), Inches(4.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = RGBColor(51, 65, 85)
        card.line.width = Pt(1.5)

        tb = s1.shapes.add_textbox(x + Inches(0.25), y + Inches(0.25), Inches(3.3), Inches(2.5))
        ctf = tb.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = label
        cp1.font.size = Pt(11)
        cp1.font.bold = True
        cp1.font.color.rgb = C_MUTED

        cp2 = ctf.add_paragraph()
        cp2.text = val
        cp2.font.size = Pt(36)
        cp2.font.bold = True
        cp2.font.color.rgb = val_color

        cp3 = ctf.add_paragraph()
        cp3.text = desc
        cp3.font.size = Pt(12)
        cp3.font.color.rgb = C_TEXT

    # Trigger Button on Card 1
    s1_trigger_btn = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.05), Inches(4.8), Inches(3.3), Inches(0.8))
    s1_trigger_btn.fill.solid()
    s1_trigger_btn.fill.fore_color.rgb = C_ACCENT
    s1_trigger_btn.line.fill.background()
    s1_trigger_btn.text_frame.text = "🔍 Xem Chi Tiết Báo Cáo (Modal)"
    s1_trigger_btn.text_frame.paragraphs[0].font.size = Pt(12)
    s1_trigger_btn.text_frame.paragraphs[0].font.bold = True
    s1_trigger_btn.text_frame.paragraphs[0].font.color.rgb = C_BG

    # Modal Components (Added last so they sit on top)
    # 1. Dimmer Overlay
    s1_dimmer = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    s1_dimmer.fill.solid()
    s1_dimmer.fill.fore_color.rgb = RGBColor(10, 15, 30)
    s1_dimmer.line.fill.background()

    # 2. Modal Box
    s1_modal_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(1.2), Inches(8.333), Inches(5.1))
    s1_modal_box.fill.solid()
    s1_modal_box.fill.fore_color.rgb = RGBColor(24, 33, 54)
    s1_modal_box.line.color.rgb = C_ACCENT
    s1_modal_box.line.width = Pt(2.5)

    # 3. Modal Content Text
    s1_modal_txt = s1.shapes.add_textbox(Inches(2.9), Inches(1.6), Inches(7.5), Inches(4.2))
    mtf = s1_modal_txt.text_frame
    mtf.word_wrap = True
    mp1 = mtf.paragraphs[0]
    mp1.text = "PHÂN TÍCH CHUYÊN SÂU DOANH THU Q3 • IN-SLIDE LIGHTBOX"
    mp1.font.size = Pt(18)
    mp1.font.bold = True
    mp1.font.color.rgb = C_ACCENT

    mp2 = mtf.add_paragraph()
    mp2.text = (
        "• Cơ cấu tăng trưởng: Doanh thu ARR đạt mốc kỷ lục với mức đóng góp 62% từ khối doanh nghiệp lớn.\n"
        "• Thị trường trọng điểm: Đông Nam Á tăng 185%, Bắc Mỹ tăng 94% nhờ các sản phẩm AI Agent tự hành.\n"
        "• Kỹ thuật tương tác: Modal này xuất hiện trực tiếp bên trong slide hiện tại nhờ OOXML interactiveSeq. "
        "Không cần tạo thêm slide phụ, không làm phân mảnh luồng trình bày của diễn giả!"
    )
    mp2.font.size = Pt(13)
    mp2.font.color.rgb = C_TEXT

    # 4. Close Button
    s1_close_btn = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), Inches(1.4), Inches(0.8), Inches(0.5))
    s1_close_btn.fill.solid()
    s1_close_btn.fill.fore_color.rgb = C_DANGER
    s1_close_btn.line.fill.background()
    s1_close_btn.text_frame.text = "✕ Đóng"
    s1_close_btn.text_frame.paragraphs[0].font.size = Pt(11)
    s1_close_btn.text_frame.paragraphs[0].font.bold = True
    s1_close_btn.text_frame.paragraphs[0].font.color.rgb = C_TEXT

    # --------------------------------------------------------------------------
    # SLIDE 2: Multi-Tab Switcher (3 Tabs on Single Slide)
    # --------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)

    t2 = s2.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf2 = t2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "HỆ THỐNG KIẾN TRÚC • IN-SLIDE MULTI-TAB SWITCHER"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = C_ACCENT

    sub2 = tf2.add_paragraph()
    sub2.text = "Nhấp chọn giữa 3 Tab bên dưới để xem các phân vùng kiến trúc khác nhau trên cùng 1 slide."
    sub2.font.size = Pt(13)
    sub2.font.color.rgb = C_MUTED

    # 3 Tab Buttons
    s2_tab1_btn = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(3.6), Inches(0.7))
    s2_tab1_btn.fill.solid()
    s2_tab1_btn.fill.fore_color.rgb = RGBColor(37, 99, 235)  # Active Blue
    s2_tab1_btn.text_frame.text = "📂 Tab 1: Tổng Quan Kiến Trúc"
    s2_tab1_btn.text_frame.paragraphs[0].font.size = Pt(12)
    s2_tab1_btn.text_frame.paragraphs[0].font.bold = True

    s2_tab2_btn = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.6), Inches(1.6), Inches(3.6), Inches(0.7))
    s2_tab2_btn.fill.solid()
    s2_tab2_btn.fill.fore_color.rgb = C_CARD
    s2_tab2_btn.text_frame.text = "⚡ Tab 2: Hiệu Năng & Tải"
    s2_tab2_btn.text_frame.paragraphs[0].font.size = Pt(12)
    s2_tab2_btn.text_frame.paragraphs[0].font.bold = True

    s2_tab3_btn = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.4), Inches(1.6), Inches(3.6), Inches(0.7))
    s2_tab3_btn.fill.solid()
    s2_tab3_btn.fill.fore_color.rgb = C_CARD
    s2_tab3_btn.text_frame.text = "🛡️ Tab 3: An Toàn & Bảo Mật"
    s2_tab3_btn.text_frame.paragraphs[0].font.size = Pt(12)
    s2_tab3_btn.text_frame.paragraphs[0].font.bold = True

    # Panels (Cards sharing the same layout rectangle)
    # Panel 1
    s2_p1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.5), Inches(11.2), Inches(4.3))
    s2_p1.fill.solid()
    s2_p1.fill.fore_color.rgb = C_CARD
    s2_p1.line.color.rgb = C_ACCENT
    s2_p1_tf = s2_p1.text_frame
    s2_p1_tf.word_wrap = True
    s2_p1_p = s2_p1_tf.paragraphs[0]
    s2_p1_p.text = "KIẾN TRÚC PHÂN TÁN MICROSERVICES & EVENT-DRIVEN"
    s2_p1_p.font.size = Pt(18)
    s2_p1_p.font.bold = True
    s2_p1_p.font.color.rgb = C_ACCENT
    s2_p1_p2 = s2_p1_tf.add_paragraph()
    s2_p1_p2.text = (
        "\n• Lớp điều phối: Kubernetes Cluster phân cụm tự động qua 3 khu vực địa lý (Multi-Region).\n"
        "• Lớp trung gian dữ liệu: Apache Kafka xử lý trên 100,000 sự kiện/giây với độ trễ dưới 5ms.\n"
        "• Khả năng chịu lỗi: Zero-Downtime Deployment với tỷ lệ sẵn sàng đạt 99.99% SLA."
    )
    s2_p1_p2.font.size = Pt(14)
    s2_p1_p2.font.color.rgb = C_TEXT

    # Panel 2
    s2_p2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.5), Inches(11.2), Inches(4.3))
    s2_p2.fill.solid()
    s2_p2.fill.fore_color.rgb = C_CARD
    s2_p2.line.color.rgb = C_SUCCESS
    s2_p2_tf = s2_p2.text_frame
    s2_p2_tf.word_wrap = True
    s2_p2_p = s2_p2_tf.paragraphs[0]
    s2_p2_p.text = "CHỈ SỐ HIỆU NĂNG TẢI THỰC NGHIỆM & ĐỘ TRỄ"
    s2_p2_p.font.size = Pt(18)
    s2_p2_p.font.bold = True
    s2_p2_p.font.color.rgb = C_SUCCESS
    s2_p2_p2 = s2_p2_tf.add_paragraph()
    s2_p2_p2.text = (
        "\n• Thông lượng tối đa: Đạt đỉnh 2.4 triệu truy vấn/phút trong chiến dịch siêu sale.\n"
        "• Thời gian phản hồi P99: 18.2ms trên toàn bộ các Endpoint API nghiệp vụ lõi.\n"
        "• Tiết kiệm tài nguyên: Giảm 42% lượng CPU tiêu thụ nhờ thuật toán bộ đệm nhị phân."
    )
    s2_p2_p2.font.size = Pt(14)
    s2_p2_p2.font.color.rgb = C_TEXT

    # Panel 3
    s2_p3 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.5), Inches(11.2), Inches(4.3))
    s2_p3.fill.solid()
    s2_p3.fill.fore_color.rgb = C_CARD
    s2_p3.line.color.rgb = RGBColor(245, 158, 11)  # Amber
    s2_p3_tf = s2_p3.text_frame
    s2_p3_tf.word_wrap = True
    s2_p3_p = s2_p3_tf.paragraphs[0]
    s2_p3_p.text = "TIÊU CHUẨN AN TOÀN DỮ LIỆU & BẢO MẬT ĐA LỚP"
    s2_p3_p.font.size = Pt(18)
    s2_p3_p.font.bold = True
    s2_p3_p.font.color.rgb = RGBColor(245, 158, 11)
    s2_p3_p2 = s2_p3_tf.add_paragraph()
    s2_p3_p2.text = (
        "\n• Mã hóa đầu cuối: Tiêu chuẩn AES-256 GCM cho dữ liệu lưu trữ và TLS 1.3 cho dữ liệu truyền tải.\n"
        "• Chứng nhận quốc tế: Đạt đầy đủ chứng chỉ tuân thủ SOC 2 Type II và ISO 27001.\n"
        "• Phân quyền thông minh: RBAC tích hợp Zero-Trust Architecture và MFA phần cứng."
    )
    s2_p3_p2.font.size = Pt(14)
    s2_p3_p2.font.color.rgb = C_TEXT

    # --------------------------------------------------------------------------
    # SLIDE 3: Interactive Sound Quiz / Knowledge Assessment
    # --------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)

    t3 = s3.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf3 = t3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "BÀI ĐÁNH GIÁ TƯƠNG TÁC • ÂM THANH PHẢN HỒI (SOUND FX)"
    p3.font.size = Pt(22)
    p3.font.bold = True
    p3.font.color.rgb = C_ACCENT

    sub3 = tf3.add_paragraph()
    sub3.text = "Chọn đáp án đúng nhất để kiểm tra phản hồi âm thanh (Ding/Chime khi đúng, Buzz khi sai)."
    sub3.font.size = Pt(13)
    sub3.font.color.rgb = C_MUTED

    # Question Box
    q_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.3))
    q_box.fill.solid()
    q_box.fill.fore_color.rgb = C_CARD
    q_box.line.color.rgb = C_ACCENT
    q_box.text_frame.text = "Câu hỏi: Phương pháp nào tốt nhất để hiển thị nội dung phụ trợ mà KHÔNG làm gián đoạn luồng trình bày?"
    q_box.text_frame.paragraphs[0].font.size = Pt(16)
    q_box.text_frame.paragraphs[0].font.bold = True
    q_box.text_frame.paragraphs[0].font.color.rgb = C_TEXT

    # 3 Choice Options
    s3_opt_a = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.1), Inches(11.7), Inches(0.9))
    s3_opt_a.fill.solid()
    s3_opt_a.fill.fore_color.rgb = C_CARD
    s3_opt_a.text_frame.text = "A. Nhảy văng sang một slide khác hoàn toàn và bắt người dùng ấn nút quay lại"
    s3_opt_a.text_frame.paragraphs[0].font.size = Pt(13)
    s3_opt_a.text_frame.paragraphs[0].font.color.rgb = C_MUTED

    s3_opt_b = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.2), Inches(11.7), Inches(0.9))
    s3_opt_b.fill.solid()
    s3_opt_b.fill.fore_color.rgb = C_CARD
    s3_opt_b.text_frame.text = "B. Sử dụng In-Slide Lightbox Modal / Tab Switcher kích hoạt bằng tương tác ngay trên slide (CHÍNH XÁC)"
    s3_opt_b.text_frame.paragraphs[0].font.size = Pt(13)
    s3_opt_b.text_frame.paragraphs[0].font.color.rgb = C_ACCENT

    s3_opt_c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.7), Inches(0.9))
    s3_opt_c.fill.solid()
    s3_opt_c.fill.fore_color.rgb = C_CARD
    s3_opt_c.text_frame.text = "C. Nhồi nhét toàn bộ văn bản dày đặc lên màn hình cùng một lúc để người xem tự đọc"
    s3_opt_c.text_frame.paragraphs[0].font.size = Pt(13)
    s3_opt_c.text_frame.paragraphs[0].font.color.rgb = C_MUTED

    # Feedback Modals (Initial state: hidden)
    # Success Modal (for Option B)
    s3_success_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.5), Inches(2.2), Inches(6.3), Inches(3.2))
    s3_success_box.fill.solid()
    s3_success_box.fill.fore_color.rgb = RGBColor(6, 78, 59)  # Deep Emerald
    s3_success_box.line.color.rgb = C_SUCCESS
    s3_success_box.line.width = Pt(2.5)
    s3_succ_tf = s3_success_box.text_frame
    s3_succ_tf.word_wrap = True
    sp_1 = s3_succ_tf.paragraphs[0]
    sp_1.text = "🎉 CHÍNH XÁC! +100 ĐIỂM"
    sp_1.font.size = Pt(20)
    sp_1.font.bold = True
    sp_1.font.color.rgb = C_SUCCESS
    sp_2 = s3_succ_tf.add_paragraph()
    sp_2.text = "\nÂm thanh Chime đã phát! In-Slide Lightbox giữ trọn vẹn sự tập trung và ngữ cảnh của bài thuyết trình."
    sp_2.font.size = Pt(13)
    sp_2.font.color.rgb = C_TEXT

    # --------------------------------------------------------------------------
    # SLIDE 4: Morph Navigation (Twin Morph)
    # --------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)

    t4 = s4.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf4 = t4.text_frame
    tf4.word_wrap = True
    p4 = tf4.paragraphs[0]
    p4.text = "ĐIỀU HƯỚNG NÂNG CAO • TWIN MORPH VISUAL FLOW"
    p4.font.size = Pt(22)
    p4.font.bold = True
    p4.font.color.rgb = C_ACCENT

    sub4 = tf4.add_paragraph()
    sub4.text = "PowerPoint Morph transition kết hợp với slide branching tạo chuyển động điện ảnh mượt mà 60 FPS."
    sub4.font.size = Pt(13)
    sub4.font.color.rgb = C_MUTED

    # Morph Target Shape
    morph_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2.0), Inches(10.3), Inches(4.5))
    morph_card.fill.solid()
    morph_card.fill.fore_color.rgb = C_CARD
    morph_card.line.color.rgb = C_ACCENT
    morph_card.line.width = Pt(2)
    mctf = morph_card.text_frame
    mctf.word_wrap = True
    mp_1 = mctf.paragraphs[0]
    mp_1.text = "🌟 TỔNG HỢP NĂNG LỰC TƯƠNG TÁC CAO CẤP (T049)"
    mp_1.font.size = Pt(18)
    mp_1.font.bold = True
    mp_1.font.color.rgb = C_ACCENT
    mp_2 = mctf.add_paragraph()
    mp_2.text = (
        "\n1. In-Slide Lightbox Modals: Hiển thị hộp thoại nổi, lớp mờ phông nền, đóng mở mượt mà.\n"
        "2. In-Slide Multi-Tab Switcher: 3 Tab chuyển đổi nội dung linh hoạt không cần nhân bản slide.\n"
        "3. Tactile Sound Effects (Click & Hover): Âm thanh phản hồi xúc giác tăng cường trải nghiệm người dùng.\n"
        "4. Non-Linear State Engine: Tương thích hoàn toàn với kiosk mode và mini-game branching (T048).\n"
        "5. Tiêu chuẩn quốc tế OOXML: Hoạt động trơn tru trên mọi phiên bản PowerPoint và DeckCraft."
    )
    mp_2.font.size = Pt(13)
    mp_2.font.color.rgb = C_TEXT

    # Save presentation to memory / temp
    temp_buf = io.BytesIO()
    prs.save(temp_buf)
    temp_buf.seek(0)

    # Now unpack into memory files for OOXML manipulation
    with zipfile.ZipFile(temp_buf, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    # Synthesize Audio Assets
    click_wav = synthesize_ui_sound("click")
    chime_wav = synthesize_ui_sound("chime")
    buzz_wav = synthesize_ui_sound("buzz")

    # Embed Audio Assets in Package
    s1_click_rid = embed_package_sound(files, click_wav, "click.wav", "slide1.xml")
    s2_click_rid = embed_package_sound(files, click_wav, "click.wav", "slide2.xml")
    s3_chime_rid = embed_package_sound(files, chime_wav, "chime.wav", "slide3.xml")
    s3_buzz_rid = embed_package_sound(files, buzz_wav, "buzz.wav", "slide3.xml")
    s3_click_rid = embed_package_sound(files, click_wav, "click.wav", "slide3.xml")

    # --------------------------------------------------------------------------
    # Wire Slide 1: In-Slide Modal Dialog
    # --------------------------------------------------------------------------
    s1_tree = ET.fromstring(files["ppt/slides/slide1.xml"])
    s1_objs = pa.top_level_objects(s1_tree)
    # Map shapes
    # trigger_btn: s1_trigger_btn
    # dimmer: s1_dimmer
    # modal_box: s1_modal_box
    # modal_txt: s1_modal_txt
    # close_btn: s1_close_btn
    
    # Identify spids by scanning cNvPr name or text
    spid_trigger = None
    spid_dimmer = None
    spid_modal_box = None
    spid_modal_txt = None
    spid_close = None

    for spid, el in s1_objs.items():
        t = el.find(f".//{{{NS_A}}}t")
        txt = t.text if t is not None else ""
        if "Xem Chi Tiết Báo Cáo" in txt:
            spid_trigger = spid
        elif "PHÂN TÍCH CHUYÊN SÂU" in txt:
            spid_modal_txt = spid
        elif "✕ Đóng" in txt:
            spid_close = spid

    # Find dimmer and modal box (non-text or container)
    for spid, el in s1_objs.items():
        if spid in (spid_trigger, spid_modal_txt, spid_close):
            continue
        # Check size or fill to identify dimmer vs modal box
        xfrm = el.find(f".//{{{NS_A}}}xfrm")
        if xfrm is not None:
            ext = xfrm.find(f"{{{NS_A}}}ext")
            if ext is not None:
                cx = int(ext.get("cx", 0))
                if cx > 10000000:  # Full slide width (~12.1M EMU)
                    spid_dimmer = spid
                elif cx > 5000000:  # Modal box
                    spid_modal_box = spid

    # Fallback to order if not identified
    remaining = [s for s in s1_objs.keys() if s not in (spid_trigger, spid_modal_txt, spid_close)]
    if not spid_dimmer and len(remaining) >= 1:
        spid_dimmer = remaining[-2]
    if not spid_modal_box and len(remaining) >= 2:
        spid_modal_box = remaining[-1]

    modal_spids = [s for s in [spid_dimmer, spid_modal_box, spid_modal_txt, spid_close] if s]

    if spid_trigger and spid_close and modal_spids:
        s1_clicks = build_in_slide_modal_click_groups(
            trigger_spid=spid_trigger,
            modal_spids=modal_spids,
            close_spid=spid_close,
            entrance_preset="zoom",
            exit_preset="fade-out",
            duration_ms=250
        )
        pa.apply_timeline(s1_tree, s1_clicks, mode="replace")

        # Attach tactile sound to trigger and close buttons
        attach_click_sound_and_action(s1_tree, spid_trigger, s1_click_rid, "click.wav")
        attach_click_sound_and_action(s1_tree, spid_close, s1_click_rid, "click.wav")
        # Attach hover sound
        attach_hover_sound_and_action(s1_tree, spid_trigger, s1_click_rid, "click.wav")

    files["ppt/slides/slide1.xml"] = ET.tostring(s1_tree, xml_declaration=True, encoding="utf-8", standalone=True)

    # --------------------------------------------------------------------------
    # Wire Slide 2: In-Slide 3-Tab Switcher
    # --------------------------------------------------------------------------
    s2_tree = ET.fromstring(files["ppt/slides/slide2.xml"])
    s2_objs = pa.top_level_objects(s2_tree)

    spid_t1_btn = None
    spid_t2_btn = None
    spid_t3_btn = None
    spid_p1 = None
    spid_p2 = None
    spid_p3 = None

    for spid, el in s2_objs.items():
        t = el.find(f".//{{{NS_A}}}t")
        txt = t.text if t is not None else ""
        if "Tab 1: Tổng Quan" in txt:
            spid_t1_btn = spid
        elif "Tab 2: Hiệu Năng" in txt:
            spid_t2_btn = spid
        elif "Tab 3: An Toàn" in txt:
            spid_t3_btn = spid
        elif "MICROSERVICES" in txt:
            spid_p1 = spid
        elif "HIỆU NĂNG TẢI" in txt:
            spid_p2 = spid
        elif "TIÊU CHUẨN AN TOÀN" in txt:
            spid_p3 = spid

    if all([spid_t1_btn, spid_t2_btn, spid_t3_btn, spid_p1, spid_p2, spid_p3]):
        tab_configs = [
            {"btn_spid": spid_t1_btn, "panel_spids": [spid_p1]},
            {"btn_spid": spid_t2_btn, "panel_spids": [spid_p2]},
            {"btn_spid": spid_t3_btn, "panel_spids": [spid_p3]},
        ]
        s2_clicks = build_tab_switcher_click_groups(tab_configs, transition_preset="fade", duration_ms=200)
        pa.apply_timeline(s2_tree, s2_clicks, mode="replace")

        # Attach sound to tab buttons
        for btn_s in (spid_t1_btn, spid_t2_btn, spid_t3_btn):
            attach_click_sound_and_action(s2_tree, btn_s, s2_click_rid, "click.wav")
            attach_hover_sound_and_action(s2_tree, btn_s, s2_click_rid, "click.wav")

    files["ppt/slides/slide2.xml"] = ET.tostring(s2_tree, xml_declaration=True, encoding="utf-8", standalone=True)

    # --------------------------------------------------------------------------
    # Wire Slide 3: Sound Quiz Assessment
    # --------------------------------------------------------------------------
    s3_tree = ET.fromstring(files["ppt/slides/slide3.xml"])
    s3_objs = pa.top_level_objects(s3_tree)

    spid_opt_a = None
    spid_opt_b = None
    spid_opt_c = None
    spid_succ_box = None

    for spid, el in s3_objs.items():
        t = el.find(f".//{{{NS_A}}}t")
        txt = t.text if t is not None else ""
        if "A. Nhảy văng sang" in txt:
            spid_opt_a = spid
        elif "B. Sử dụng In-Slide" in txt:
            spid_opt_b = spid
        elif "C. Nhồi nhét toàn bộ" in txt:
            spid_opt_c = spid
        elif "CHÍNH XÁC! +100" in txt:
            spid_succ_box = spid

    if all([spid_opt_a, spid_opt_b, spid_opt_c, spid_succ_box]):
        # Option B reveals success box
        s3_clicks = [
            {
                "id": "quiz_correct",
                "start": "click",
                "trigger_spid": spid_opt_b,
                "effects": [
                    {"preset": "zoom", "spid": spid_succ_box, "trigger": "click", "duration_ms": 300}
                ]
            }
        ]
        pa.apply_timeline(s3_tree, s3_clicks, mode="replace")

        # Sound effects:
        # Option B (Correct) -> Chime
        attach_click_sound_and_action(s3_tree, spid_opt_b, s3_chime_rid, "chime.wav")
        # Option A & C (Wrong) -> Buzz
        attach_click_sound_and_action(s3_tree, spid_opt_a, s3_buzz_rid, "buzz.wav")
        attach_click_sound_and_action(s3_tree, spid_opt_c, s3_buzz_rid, "buzz.wav")

    files["ppt/slides/slide3.xml"] = ET.tostring(s3_tree, xml_declaration=True, encoding="utf-8", standalone=True)

    # --------------------------------------------------------------------------
    # Wire Slide 4: Morph Transition
    # --------------------------------------------------------------------------
    s4_tree = ET.fromstring(files["ppt/slides/slide4.xml"])
    configure_slide_morph_transition(s4_tree, duration_ms=750)
    files["ppt/slides/slide4.xml"] = ET.tostring(s4_tree, xml_declaration=True, encoding="utf-8", standalone=True)

    # Repack into output file
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)

    # Produce audit
    audit = inspect_interactivity(out_file)

    return {
        "ok": True,
        "output_file": str(out_file),
        "audit": audit
    }
