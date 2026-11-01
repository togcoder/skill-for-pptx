"""Advanced Presentation Interactivity & 1-Slide Mini-Games Engine (T049).

Antigravity multi-domain design research lab.
Core Capabilities:
1. 1-Slide Native Mini-Games:
   - Mystery Treasure Chests Game: 3 side-by-side chests with self-triggered zoom-out cover reveals
     and an all-chest reset button operating 100% within a single slide.
   - Interactive Quiz Battle: Dynamic choice evaluation with instant green/red badge feedback
     and reset capability on 1 single slide.
2. Root-Cause Hardening:
   - Eliminates hit-test blocking (no full-screen dimmer rectangles sitting above interactive shapes).
   - Eliminates hyperlink hijacking (never attaches ppaction://noaction hlinks to animation trigger shapes).
   - Generates 100% canonical OOXML interactiveSeq timing structures validated on Office 16.0 COM.
"""

from __future__ import annotations

import io
import math
import os
import struct
import wave
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from lxml import etree as ET

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
# 1. AUDIO SYNTHESIS & EMBEDDING
# ==============================================================================

def synthesize_ui_sound(sound_type: str = "click", sample_rate: int = 44100) -> bytes:
    """Synthesizes pristine 16-bit mono PCM WAV audio using only Python standard library."""
    buf = io.BytesIO()
    if sound_type == "click":
        duration_s = 0.04
        freqs = [1200.0, 2400.0]
        decay = 3.5
        volume = 0.45
    elif sound_type == "chime":
        duration_s = 0.35
        freqs = [523.25, 659.25, 783.99]
        decay = 2.8
        volume = 0.50
    elif sound_type == "buzz":
        duration_s = 0.25
        freqs = [140.0, 280.0, 420.0]
        decay = 1.8
        volume = 0.40
    else:
        duration_s = 0.04
        freqs = [1000.0]
        decay = 3.0
        volume = 0.40

    n_samples = int(sample_rate * duration_s)
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            env = math.exp(-decay * t / duration_s)
            val = sum(math.sin(2.0 * math.pi * f * t) for f in freqs) / len(freqs)
            sample = int(val * volume * env * 32767.0)
            sample = max(-32768, min(32767, sample))
            frames.extend(struct.pack("<h", sample))
        wav.writeframes(frames)
    return buf.getvalue()


# ==============================================================================
# 2. CANONICAL NATIVE INTERACTIVE TIMING BUILDER
# ==============================================================================

def build_canonical_interactive_seq(
    trigger_spid: Union[str, int],
    target_spids: List[Union[str, int]],
    is_exit: bool = False,
    preset_name: str = "zoom",
    duration_ms: int = 350,
    seq_id: int = 2
) -> ET.Element:
    """Constructs a 100% canonical PowerPoint interactiveSeq XML subtree.
    
    Structure matches Office 16.0 COM native output:
    - <p:seq concurrent="1" nextAc="seek">
      - <p:cTn nodeType="interactiveSeq">
        - <p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="..."/></p:tgtEl></p:cond></p:stCondLst>
        - <p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync>
        - <p:childTnLst>
          ...
      - <p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="..."/></p:tgtEl></p:cond></p:nextCondLst>
    """
    trig_s = str(trigger_spid)
    preset_id = "53" if preset_name == "zoom" else "10"
    preset_cls = "exit" if is_exit else "entr"
    preset_sub = "32" if preset_name == "zoom" else "0"

    seq = ET.Element(f"{{{NS_P}}}seq", concurrent="1", nextAc="seek")
    
    # Root cTn of interactive sequence
    ctn = ET.SubElement(
        seq,
        f"{{{NS_P}}}cTn",
        id=str(seq_id),
        restart="whenNotActive",
        fill="hold",
        evtFilter="cancelBubble",
        nodeType="interactiveSeq"
    )
    st = ET.SubElement(ctn, f"{{{NS_P}}}stCondLst")
    cond = ET.SubElement(st, f"{{{NS_P}}}cond", evt="onClick", delay="0")
    tgt = ET.SubElement(cond, f"{{{NS_P}}}tgtEl")
    ET.SubElement(tgt, f"{{{NS_P}}}spTgt", spid=trig_s)

    endsync = ET.SubElement(ctn, f"{{{NS_P}}}endSync", evt="end", delay="0")
    ET.SubElement(endsync, f"{{{NS_P}}}rtn", val="all")

    child_tn = ET.SubElement(ctn, f"{{{NS_P}}}childTnLst")

    # For each target shape, create animation effect
    outer_par = ET.SubElement(child_tn, f"{{{NS_P}}}par")
    outer_ctn = ET.SubElement(outer_par, f"{{{NS_P}}}cTn", id=str(seq_id + 1), fill="hold")
    ET.SubElement(ET.SubElement(outer_ctn, f"{{{NS_P}}}stCondLst"), f"{{{NS_P}}}cond", delay="0")
    inner_child = ET.SubElement(outer_ctn, f"{{{NS_P}}}childTnLst")

    sub_id = seq_id + 2
    for idx, tgt_spid in enumerate(target_spids):
        tgt_s = str(tgt_spid)
        bpar = ET.SubElement(inner_child, f"{{{NS_P}}}par")
        bctn = ET.SubElement(bpar, f"{{{NS_P}}}cTn", id=str(sub_id), fill="hold")
        ET.SubElement(ET.SubElement(bctn, f"{{{NS_P}}}stCondLst"), f"{{{NS_P}}}cond", delay="0")
        sub_id += 1

        eff_child = ET.SubElement(bctn, f"{{{NS_P}}}childTnLst")
        eff_par = ET.SubElement(eff_child, f"{{{NS_P}}}par")
        eff_ctn = ET.SubElement(
            eff_par,
            f"{{{NS_P}}}cTn",
            id=str(sub_id),
            presetID=preset_id,
            presetClass=preset_cls,
            presetSubtype=preset_sub,
            fill="hold",
            grpId="0",
            nodeType="clickEffect" if idx == 0 else "withEffect"
        )
        ET.SubElement(ET.SubElement(eff_ctn, f"{{{NS_P}}}stCondLst"), f"{{{NS_P}}}cond", delay="0")
        sub_id += 1

        b_child = ET.SubElement(eff_ctn, f"{{{NS_P}}}childTnLst")

        if is_exit:
            # Exit animation: scale down and set visibility hidden
            if preset_name == "zoom":
                for prop in ("ppt_w", "ppt_h"):
                    anim = ET.SubElement(b_child, f"{{{NS_P}}}anim", calcmode="lin", valueType="num")
                    cbhvr = ET.SubElement(anim, f"{{{NS_P}}}cBhvr")
                    ET.SubElement(cbhvr, f"{{{NS_P}}}cTn", id=str(sub_id), dur=str(duration_ms))
                    sub_id += 1
                    ET.SubElement(ET.SubElement(cbhvr, f"{{{NS_P}}}tgtEl"), f"{{{NS_P}}}spTgt", spid=tgt_s)
                    ET.SubElement(ET.SubElement(cbhvr, f"{{{NS_P}}}attrNameLst"), f"{{{NS_P}}}attrName").text = prop
                    tav_lst = ET.SubElement(anim, f"{{{NS_P}}}tavLst")
                    ET.SubElement(ET.SubElement(ET.SubElement(tav_lst, f"{{{NS_P}}}tav", tm="0"), f"{{{NS_P}}}val"), f"{{{NS_P}}}strVal", val=prop)
                    ET.SubElement(ET.SubElement(ET.SubElement(tav_lst, f"{{{NS_P}}}tav", tm="100000"), f"{{{NS_P}}}val"), f"{{{NS_P}}}fltVal", val="0")

            anim_eff = ET.SubElement(b_child, f"{{{NS_P}}}animEffect", transition="out", filter="fade")
            cbhvr_eff = ET.SubElement(anim_eff, f"{{{NS_P}}}cBhvr")
            ET.SubElement(cbhvr_eff, f"{{{NS_P}}}cTn", id=str(sub_id), dur=str(duration_ms))
            sub_id += 1
            ET.SubElement(ET.SubElement(cbhvr_eff, f"{{{NS_P}}}tgtEl"), f"{{{NS_P}}}spTgt", spid=tgt_s)

            # Set hidden
            s_node = ET.SubElement(b_child, f"{{{NS_P}}}set")
            cbhvr_set = ET.SubElement(s_node, f"{{{NS_P}}}cBhvr")
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}cTn", id=str(sub_id), dur="1", fill="hold"), f"{{{NS_P}}}stCondLst")
            sub_id += 1
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}tgtEl"), f"{{{NS_P}}}spTgt", spid=tgt_s)
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}attrNameLst"), f"{{{NS_P}}}attrName").text = "style.visibility"
            ET.SubElement(ET.SubElement(s_node, f"{{{NS_P}}}to"), f"{{{NS_P}}}strVal", val="hidden")
        else:
            # Entrance animation: set visible and scale/fade up
            s_node = ET.SubElement(b_child, f"{{{NS_P}}}set")
            cbhvr_set = ET.SubElement(s_node, f"{{{NS_P}}}cBhvr")
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}cTn", id=str(sub_id), dur="1", fill="hold"), f"{{{NS_P}}}stCondLst")
            sub_id += 1
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}tgtEl"), f"{{{NS_P}}}spTgt", spid=tgt_s)
            ET.SubElement(ET.SubElement(cbhvr_set, f"{{{NS_P}}}attrNameLst"), f"{{{NS_P}}}attrName").text = "style.visibility"
            ET.SubElement(ET.SubElement(s_node, f"{{{NS_P}}}to"), f"{{{NS_P}}}strVal", val="visible")

            anim_eff = ET.SubElement(b_child, f"{{{NS_P}}}animEffect", transition="in", filter="fade")
            cbhvr_eff = ET.SubElement(anim_eff, f"{{{NS_P}}}cBhvr")
            ET.SubElement(cbhvr_eff, f"{{{NS_P}}}cTn", id=str(sub_id), dur=str(duration_ms))
            sub_id += 1
            ET.SubElement(ET.SubElement(cbhvr_eff, f"{{{NS_P}}}tgtEl"), f"{{{NS_P}}}spTgt", spid=tgt_s)

    # NextCondLst on seq
    nxt = ET.SubElement(seq, f"{{{NS_P}}}nextCondLst")
    cond_nxt = ET.SubElement(nxt, f"{{{NS_P}}}cond", evt="onClick", delay="0")
    tgt_nxt = ET.SubElement(cond_nxt, f"{{{NS_P}}}tgtEl")
    ET.SubElement(tgt_nxt, f"{{{NS_P}}}spTgt", spid=trig_s)

    return seq


# ==============================================================================
# 3. HIGH-LEVEL 1-SLIDE GAME COMPILER
# ==============================================================================

def compile_one_slide_games_suite(output_path: Union[str, Path]) -> Dict[str, Any]:
    """Compiles a complete 2-slide game suite where each slide is an autonomous 1-slide game.
    
    Slide 1: Mystery Treasure Chests (3 chests side-by-side with reveal & reset).
    Slide 2: Interactive Quiz Battle (3 choice cards with instant feedback badges & reset).
    
    Built natively via PowerPoint 16.0 COM to guarantee 100% native runtime behavior.
    """
    import win32com.client

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    ppt = win32com.client.Dispatch("PowerPoint.Application")
    prs = ppt.Presentations.Add(True)
    prs.PageSetup.SlideWidth = 960
    prs.PageSetup.SlideHeight = 540

    # Colors (BGR hex for PowerPoint COM)
    C_DARK = 0x1E170F
    C_GOLD = 0x22B8FF
    C_GREEN = 0x5ECC22
    C_PURPLE = 0xD946A8
    C_RED = 0x3844EF
    C_CARD = 0x3B2D1E
    C_TEXT = 0xFFFFFF
    C_MUTED = 0xCCCCCC

    # --------------------------------------------------------------------------
    # SLIDE 1: Mystery Treasure Chests Game (100% on 1 Slide)
    # --------------------------------------------------------------------------
    s1 = prs.Slides.Add(1, 12)  # Blank layout
    bg1 = s1.Shapes.AddShape(1, 0, 0, 960, 540)
    bg1.Fill.Solid()
    bg1.Fill.ForeColor.RGB = C_DARK
    bg1.Line.Visible = False

    t1 = s1.Shapes.AddTextbox(1, 50, 25, 860, 50)
    t1.TextFrame.TextRange.Text = "🎮 GAME 1: KHÁM PHÁ 3 RƯƠNG BÁU HOÀNG GIA (1 SLIDE)"
    t1.TextFrame.TextRange.Font.Size = 22
    t1.TextFrame.TextRange.Font.Bold = True
    t1.TextFrame.TextRange.Font.Color.RGB = C_TEXT

    sub1 = s1.Shapes.AddTextbox(1, 50, 70, 860, 30)
    sub1.TextFrame.TextRange.Text = "Nhấp chuột trực tiếp vào từng rương để mở nắp khám phá phần thưởng. Nhấp nút Reset để đóng lại!"
    sub1.TextFrame.TextRange.Font.Size = 12
    sub1.TextFrame.TextRange.Font.Color.RGB = C_MUTED

    chests = [
        ("Reward_1", "💎 1,000 KIM CƯƠNG!\n\nPhần thưởng siêu cấp huyền thoại đã được mở khóa!", C_GREEN),
        ("Reward_2", "⚡ BÙA SẤM SÉT!\n\nTăng 100% sức mạnh công kích toàn đội!", C_PURPLE),
        ("Reward_3", "💣 ÔI KHÔNG! BẪY RỒNG!\n\nBạn đã kích hoạt bẫy nổ, bị trừ 500 điểm!", C_RED),
    ]

    covers1 = []
    for i, (name, text, col) in enumerate(chests):
        x = 60 + i * 300
        y = 115
        # Reward
        rew = s1.Shapes.AddShape(1, x, y, 240, 280)
        rew.Name = name
        rew.Fill.Solid()
        rew.Fill.ForeColor.RGB = col
        rew.Line.Weight = 2
        rew.Line.ForeColor.RGB = 0xFFFFFF
        rew.TextFrame.TextRange.Text = text
        rew.TextFrame.TextRange.Font.Size = 14
        rew.TextFrame.TextRange.Font.Bold = True
        rew.TextFrame.TextRange.Font.Color.RGB = 0xFFFFFF

        # Cover (Sits exactly over reward)
        cov = s1.Shapes.AddShape(1, x, y, 240, 280)
        cov.Name = f"Cover_{i+1}"
        cov.Fill.Solid()
        cov.Fill.ForeColor.RGB = C_CARD
        cov.Line.Weight = 3
        cov.Line.ForeColor.RGB = C_GOLD
        cov.TextFrame.TextRange.Text = f"📦 RƯƠNG BÍ MẬT #{i+1}\n\n[ Nhấp Vào Để Mở ]"
        cov.TextFrame.TextRange.Font.Size = 15
        cov.TextFrame.TextRange.Font.Bold = True
        cov.TextFrame.TextRange.Font.Color.RGB = C_GOLD
        covers1.append(cov)

    reset_btn1 = s1.Shapes.AddShape(1, 330, 430, 300, 60)
    reset_btn1.Name = "Reset_Button_S1"
    reset_btn1.Fill.Solid()
    reset_btn1.Fill.ForeColor.RGB = C_GOLD
    reset_btn1.Line.Visible = False
    reset_btn1.TextFrame.TextRange.Text = "🔄 ĐÓNG LẠI TẤT CẢ RƯƠNG (RESET)"
    reset_btn1.TextFrame.TextRange.Font.Size = 13
    reset_btn1.TextFrame.TextRange.Font.Bold = True
    reset_btn1.TextFrame.TextRange.Font.Color.RGB = 0x000000

    # Triggers for Slide 1
    for i, cov in enumerate(covers1):
        seq = s1.TimeLine.InteractiveSequences.Add()
        eff = seq.AddEffect(cov, 48, 0, 4)  # Zoom out Exit
        eff.Exit = -1
        eff.Timing.Duration = 0.35
        eff.Timing.TriggerShape = cov

    reset_seq1 = s1.TimeLine.InteractiveSequences.Add()
    for i, cov in enumerate(covers1):
        eff = reset_seq1.AddEffect(cov, 48, 0, 4)  # Zoom in Entrance
        eff.Exit = 0
        eff.Timing.Duration = 0.30
        eff.Timing.TriggerShape = reset_btn1
        if i > 0:
            eff.Timing.TriggerType = 3  # With Previous

    # --------------------------------------------------------------------------
    # SLIDE 2: Interactive Quiz Battle (100% on 1 Slide)
    # --------------------------------------------------------------------------
    s2 = prs.Slides.Add(2, 12)
    bg2 = s2.Shapes.AddShape(1, 0, 0, 960, 540)
    bg2.Fill.Solid()
    bg2.Fill.ForeColor.RGB = C_DARK
    bg2.Line.Visible = False

    t2 = s2.Shapes.AddTextbox(1, 50, 25, 860, 50)
    t2.TextFrame.TextRange.Text = "🧠 GAME 2: ĐẤU TRÍ TRẮC NGHIỆM TƯƠNG TÁC (1 SLIDE)"
    t2.TextFrame.TextRange.Font.Size = 22
    t2.TextFrame.TextRange.Font.Bold = True
    t2.TextFrame.TextRange.Font.Color.RGB = C_TEXT

    # Question Box
    qbox = s2.Shapes.AddShape(1, 50, 80, 860, 70)
    qbox.Fill.Solid()
    qbox.Fill.ForeColor.RGB = C_CARD
    qbox.Line.Weight = 2
    qbox.Line.ForeColor.RGB = C_GOLD
    qbox.TextFrame.TextRange.Text = "Câu hỏi: Cấu trúc XML nào quản lý hoạt ảnh tương tác theo sự kiện click nút bấm trong PPTX?"
    qbox.TextFrame.TextRange.Font.Size = 15
    qbox.TextFrame.TextRange.Font.Bold = True
    qbox.TextFrame.TextRange.Font.Color.RGB = C_TEXT

    options = [
        ("Choice_A", "A. <p:custShowLst> (Danh sách trình chiếu tùy chỉnh)", False, "❌ SAI RỒI!\n<p:custShowLst> dùng để tạo nhánh slide chứ không kích hoạt hoạt ảnh tại chỗ."),
        ("Choice_B", "B. <p:cTn nodeType=\"interactiveSeq\"> (Chuỗi hoạt ảnh tương tác)", True, "🎉 CHÍNH XÁC! +100 ĐIỂM!\nnodeType=\"interactiveSeq\" quản lý toàn bộ trigger on-click ngay trên 1 slide!"),
        ("Choice_C", "C. <w:body> (Thẻ nội dung tài liệu)", False, "❌ SAI RỒI!\n<w:body> là thành phần của WordprocessingML (Word DOCX), không thuộc PPTX."),
    ]

    feedback_shapes = []
    for i, (name, opt_text, is_correct, fb_text) in enumerate(options):
        y = 170 + i * 95
        btn = s2.Shapes.AddShape(1, 50, y, 460, 75)
        btn.Name = name
        btn.Fill.Solid()
        btn.Fill.ForeColor.RGB = C_CARD
        btn.Line.Weight = 2
        btn.Line.ForeColor.RGB = C_GOLD if is_correct else 0x666666
        btn.TextFrame.TextRange.Text = opt_text
        btn.TextFrame.TextRange.Font.Size = 13
        btn.TextFrame.TextRange.Font.Bold = True
        btn.TextFrame.TextRange.Font.Color.RGB = C_TEXT

        # Feedback badge on the right
        fb = s2.Shapes.AddShape(1, 530, y, 380, 75)
        fb.Name = f"Feedback_{i+1}"
        fb.Fill.Solid()
        fb.Fill.ForeColor.RGB = C_GREEN if is_correct else C_RED
        fb.Line.Weight = 2
        fb.Line.ForeColor.RGB = 0xFFFFFF
        fb.TextFrame.TextRange.Text = fb_text
        fb.TextFrame.TextRange.Font.Size = 12
        fb.TextFrame.TextRange.Font.Bold = True
        fb.TextFrame.TextRange.Font.Color.RGB = 0xFFFFFF
        feedback_shapes.append(fb)

        # Wire trigger: Clicking btn reveals fb
        seq = s2.TimeLine.InteractiveSequences.Add()
        eff = seq.AddEffect(fb, 10, 0, 4)  # Fade Entrance
        eff.Exit = 0
        eff.Timing.Duration = 0.25
        eff.Timing.TriggerShape = btn

    # Reset button for Slide 2
    reset_btn2 = s2.Shapes.AddShape(1, 330, 465, 300, 50)
    reset_btn2.Name = "Reset_Button_S2"
    reset_btn2.Fill.Solid()
    reset_btn2.Fill.ForeColor.RGB = C_GOLD
    reset_btn2.Line.Visible = False
    reset_btn2.TextFrame.TextRange.Text = "🔄 LÀM LẠI CÂU HỎI (RESET)"
    reset_btn2.TextFrame.TextRange.Font.Size = 13
    reset_btn2.TextFrame.TextRange.Font.Bold = True
    reset_btn2.TextFrame.TextRange.Font.Color.RGB = 0x000000

    # Wire Reset on Slide 2: Clicking reset_btn2 hides all feedback badges
    reset_seq2 = s2.TimeLine.InteractiveSequences.Add()
    for i, fb in enumerate(feedback_shapes):
        eff = reset_seq2.AddEffect(fb, 10, 0, 4)  # Fade Exit
        eff.Exit = -1
        eff.Timing.Duration = 0.20
        eff.Timing.TriggerShape = reset_btn2
        if i > 0:
            eff.Timing.TriggerType = 3

    prs.SaveAs(str(out_file))
    prs.Close()

    # Produce audit
    audit = inspect_interactivity(out_file)

    return {
        "ok": True,
        "output_file": str(out_file),
        "audit": audit
    }


def inspect_interactivity(pptx_path: Union[str, Path]) -> Dict[str, Any]:
    """Inspects a presentation and extracts all interactive sequences and triggers."""
    p = Path(pptx_path)
    if not p.is_file():
        raise FileNotFoundError(f"Presentation not found: {p}")

    report = {
        "ok": True,
        "path": str(p),
        "total_slides": 0,
        "interactive_sequences_count": 0,
        "slides": []
    }

    with zipfile.ZipFile(p, "r") as z:
        namelist = z.namelist()
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
            }

            timing = s_tree.find(f"{{{NS_P}}}timing")
            if timing is not None:
                for seq in timing.iter(f"{{{NS_P}}}seq"):
                    ctn = seq.find(f"{{{NS_P}}}cTn[@nodeType='interactiveSeq']")
                    if ctn is None:
                        continue
                    
                    # Find trigger spid either in stCondLst or nextCondLst
                    tgt = ctn.find(f".//{{{NS_P}}}stCondLst/{{{NS_P}}}cond/{{{NS_P}}}tgtEl/{{{NS_P}}}spTgt")
                    if tgt is None:
                        tgt = seq.find(f"{{{NS_P}}}nextCondLst/{{{NS_P}}}cond/{{{NS_P}}}tgtEl/{{{NS_P}}}spTgt")
                    trigger_spid = tgt.get("spid") if tgt is not None else None

                    effects = []
                    for c in ctn.iter(f"{{{NS_P}}}cTn"):
                        sp_tgt = c.find(f".//{{{NS_P}}}spTgt")
                        if sp_tgt is not None and sp_tgt.get("spid") != trigger_spid:
                            effects.append(sp_tgt.get("spid"))

                    slide_data["interactive_sequences"].append({
                        "trigger_spid": trigger_spid,
                        "animated_spids": list(set(effects))
                    })
                    report["interactive_sequences_count"] += 1

            report["slides"].append(slide_data)

    return report
