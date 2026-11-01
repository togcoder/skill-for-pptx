import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from slide_navigator import (
    configure_interactive_navigation,
    inspect_navigation_graph,
    compile_mini_game_state_machine,
    compile_hub_and_spoke_deck,
)

DECKCRAFT_CLI = r"D:\artcraft\DeckCraft\deckcraft-cli.exe"
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
PREVIEWS_DIR = ARTIFACTS_DIR / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

FONT_HEAD = "Montserrat"
FONT_BODY = "Nunito Sans"

# Palette: Dark Forest / Modern Slate
COLOR_BG = RGBColor(15, 23, 42)          # Slate 900
COLOR_CARD = RGBColor(30, 41, 59)        # Slate 800
COLOR_BORDER = RGBColor(51, 65, 85)      # Slate 700
COLOR_TEXT = RGBColor(248, 250, 252)     # White/Slate 50
COLOR_MUTED = RGBColor(148, 163, 184)    # Slate 400
COLOR_ACCENT = RGBColor(16, 185, 129)    # Emerald 500
COLOR_BLUE = RGBColor(14, 165, 233)      # Sky 500
COLOR_RED = RGBColor(239, 68, 68)        # Rose 500
COLOR_AMBER = RGBColor(245, 158, 11)     # Amber 500


def _style_button(shape, bg_color: RGBColor, text: str, font_size: int = 14, is_bold: bool = True):
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = COLOR_BORDER
    shape.line.width = Pt(1.5)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEAD
    p.font.size = Pt(font_size)
    p.font.bold = is_bold
    p.font.color.rgb = COLOR_TEXT


def _style_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card


def build_interactive_adventure_game(output_path: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    layout = prs.slide_layouts[6]

    # --- Slide 1: Start Screen ---
    s1 = prs.slides.add_slide(layout)
    _style_card(s1, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    tb = s1.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(2.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "THỬ THÁCH TRÍ TUỆ NHÂN TẠO"
    p0.font.name = FONT_HEAD
    p0.font.size = Pt(38)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ACCENT
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf.add_paragraph()
    p1.text = "Cuộc Phiêu Lưu Rừng Xanh: Mô Hình Trình Chiếu Phi Tuyến Tính (Non-Linear Game)"
    p1.font.name = FONT_BODY
    p1.font.size = Pt(18)
    p1.font.color.rgb = COLOR_MUTED
    p1.alignment = PP_ALIGN.CENTER

    btn_start = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.666), Inches(4.8), Inches(4), Inches(1.2))
    btn_start.name = "btn_start_game"
    _style_button(btn_start, COLOR_ACCENT, "BẮT ĐẦU HÀNH TRÌNH ➔", font_size=18)

    # --- Slide 2: Question 1 ---
    s2 = prs.slides.add_slide(layout)
    _style_card(s2, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    card_q1 = _style_card(s2, Inches(1.2), Inches(1.0), Inches(10.933), Inches(1.8))
    card_q1.text_frame.word_wrap = True
    p = card_q1.text_frame.paragraphs[0]
    p.text = "CÂU HỎI 1: BẢO TỒN DỮ LIỆU LIÊN ỨNG DỤNG"
    p.font.name = FONT_HEAD
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p2 = card_q1.text_frame.add_paragraph()
    p2.text = "Để chuyển biểu đồ từ Excel sang PowerPoint mà không bị mất công thức (=B2-B3) và mở được trọn vẹn mô hình đa sheet, phương pháp tối ưu là gì?"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_TEXT

    btn_opt1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.2), Inches(10.933), Inches(1.0))
    btn_opt1.name = "btn_opt_wrong_1"
    _style_button(btn_opt1, COLOR_CARD, "A. Chụp ảnh màn hình (Screenshot) dán vào slide", font_size=15)

    btn_opt2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.4), Inches(10.933), Inches(1.0))
    btn_opt2.name = "btn_opt_correct_1"
    _style_button(btn_opt2, COLOR_CARD, "B. Nhúng Workbook Hoàn Chỉnh (Embedded Connected Model)", font_size=15)

    btn_opt3 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.6), Inches(10.933), Inches(1.0))
    btn_opt3.name = "btn_opt_wrong_2"
    _style_button(btn_opt3, COLOR_CARD, "C. Link ngoài đường dẫn tuyệt đối (External Link c:\\...) rồi gửi email", font_size=15)

    # --- Slide 3: Wrong Answer Screen (Thua cuộc / Thử lại) ---
    s3 = prs.slides.add_slide(layout)
    _style_card(s3, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    card_wrong = _style_card(s3, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5), COLOR_CARD, COLOR_RED)
    tf_w = card_wrong.text_frame
    tf_w.word_wrap = True
    pw = tf_w.paragraphs[0]
    pw.text = "LỰA CHỌN CHƯA CHÍNH XÁC!"
    pw.font.name = FONT_HEAD
    pw.font.size = Pt(28)
    pw.font.bold = True
    pw.font.color.rgb = COLOR_RED
    pw.alignment = PP_ALIGN.CENTER

    pw2 = tf_w.add_paragraph()
    pw2.text = "\nẢnh tĩnh sẽ mất hoàn toàn khả năng chỉnh sửa số liệu.\nLiên kết ngoài dễ bị đứt (Broken Link) khi di chuyển máy tính.\nChỉ có Embedded Model mới bảo tồn 100% công thức và tính độc lập!"
    pw2.font.name = FONT_BODY
    pw2.font.size = Pt(16)
    pw2.font.color.rgb = COLOR_MUTED
    pw2.alignment = PP_ALIGN.CENTER

    btn_retry = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.0), Inches(4.5), Inches(3.2), Inches(1.0))
    btn_retry.name = "btn_try_again"
    _style_button(btn_retry, COLOR_AMBER, "↺ THỬ LẠI", font_size=16)

    btn_home = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.133), Inches(4.5), Inches(3.2), Inches(1.0))
    btn_home.name = "btn_quit_home"
    _style_button(btn_home, COLOR_BORDER, "⌂ VỀ TRANG ĐẦU", font_size=16)

    # --- Slide 4: Question 2 ---
    s4 = prs.slides.add_slide(layout)
    _style_card(s4, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    card_q2 = _style_card(s4, Inches(1.2), Inches(1.0), Inches(10.933), Inches(1.8))
    card_q2.text_frame.word_wrap = True
    p = card_q2.text_frame.paragraphs[0]
    p.text = "CÂU HỎI 2: ĐIỀU HƯỚNG PHI TUYẾN TÍNH (NON-LINEAR NAVIGATION)"
    p.font.name = FONT_HEAD
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p2 = card_q2.text_frame.add_paragraph()
    p2.text = "Khi trình bày một nhánh phân tích phụ (Auxiliary Deep Dive), làm sao để nút quay lại tự động đưa người xem về đúng slide họ vừa xuất phát (Quay về kể tiếp)?"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_TEXT

    btn_q2_opt1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.2), Inches(10.933), Inches(1.0))
    btn_q2_opt1.name = "btn_q2_wrong"
    _style_button(btn_q2_opt1, COLOR_CARD, "A. Cố định liên kết cứng (Hardcode) luôn nhảy về Slide số 1", font_size=15)

    btn_q2_opt2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.4), Inches(10.933), Inches(1.0))
    btn_q2_opt2.name = "btn_q2_correct"
    _style_button(btn_q2_opt2, COLOR_CARD, "B. Dùng hành động Last Slide Viewed (lastslideviewed) hoặc Custom Show Return", font_size=15)

    btn_q2_opt3 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.6), Inches(10.933), Inches(1.0))
    btn_q2_opt3.name = "btn_q2_wrong_2"
    _style_button(btn_q2_opt3, COLOR_CARD, "C. Bắt buộc người dùng nhấn phím mũi tên lùi nhiều lần", font_size=15)

    # --- Slide 5: Victory Screen ---
    s5 = prs.slides.add_slide(layout)
    _style_card(s5, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    card_vic = _style_card(s5, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5), COLOR_CARD, COLOR_ACCENT)
    tf_v = card_vic.text_frame
    tf_v.word_wrap = True
    pv = tf_v.paragraphs[0]
    pv.text = "CHIẾN THẮNG XUẤT SẮC!"
    pv.font.name = FONT_HEAD
    pv.font.size = Pt(32)
    pv.font.bold = True
    pv.font.color.rgb = COLOR_ACCENT
    pv.alignment = PP_ALIGN.CENTER

    pv2 = tf_v.add_paragraph()
    pv2.text = "\nBạn đã giải mã thành công bí quyết thiết kế slide phi tuyến tính!\nBiểu đồ nhúng bảo tồn 100% công thức.\nĐiều hướng chia nhánh thông minh với Last Slide Viewed và Kiosk Mode!"
    pv2.font.name = FONT_BODY
    pv2.font.size = Pt(17)
    pv2.font.color.rgb = COLOR_TEXT
    pv2.alignment = PP_ALIGN.CENTER

    btn_replay = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.2), Inches(4.6), Inches(3.2), Inches(1.0))
    btn_replay.name = "btn_replay"
    _style_button(btn_replay, COLOR_BLUE, "CHƠI LẠI TỪ ĐẦU", font_size=15)

    btn_end = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(4.6), Inches(3.2), Inches(1.0))
    btn_end.name = "btn_end_show"
    _style_button(btn_end, COLOR_BORDER, "KẾT THÚC SHOW ✖", font_size=15)

    # Save initial presentation
    prs.save(output_path)

    # Compile the mini-game state machine!
    game_spec = {
        "start": {"slide": 0, "button": "btn_start_game", "first_question": 1},
        "questions": [
            {
                "slide": 1,
                "correct_button": "btn_opt_correct_1",
                "correct_target": 3,
                "wrong_buttons": ["btn_opt_wrong_1", "btn_opt_wrong_2"],
                "wrong_target": 2,
            },
            {
                "slide": 3,
                "correct_button": "btn_q2_correct",
                "correct_target": 4,
                "wrong_buttons": ["btn_q2_wrong", "btn_q2_wrong_2"],
                "wrong_target": 2,
            },
        ],
        "wrong_screens": [
            {
                "slide": 2,
                "try_again_button": "btn_try_again",
                "quit_button": "btn_quit_home",
            }
        ],
        "victory_screen": {
            "slide": 4,
            "restart_button": "btn_replay",
            "end_button": "btn_end_show",
        },
    }
    compile_mini_game_state_machine(output_path, game_spec, output_path=output_path)
    return output_path


def build_executive_interactive_hub(output_path: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    layout = prs.slide_layouts[6]

    # --- Slide 1: Executive Hub Menu ---
    s1 = prs.slides.add_slide(layout)
    _style_card(s1, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    p = tb.text_frame.paragraphs[0]
    p.text = "EXECUTIVE BRIEFING 2026 — INTERACTIVE HUB"
    p.font.name = FONT_HEAD
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p_sub = tb.text_frame.add_paragraph()
    p_sub.text = "Khám phá các trụ cột chiến lược. Click vào thẻ bất kỳ để xem chi tiết và quay lại menu trung tâm."
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_MUTED

    # 3 Topic Cards
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.4), Inches(3.5), Inches(3.8))
    c1.name = "btn_hub_strategy"
    _style_button(c1, COLOR_CARD, "TRỤ CỘT 1\n\nCHIẾN LƯỢC TĂNG TRƯỞNG\n\n➔ Xem chi tiết", font_size=16)

    c2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.916), Inches(2.4), Inches(3.5), Inches(3.8))
    c2.name = "btn_hub_finance"
    _style_button(c2, COLOR_CARD, "TRỤ CỘT 2\n\nTÀI CHÍNH & LỢI NHUẬN\n\n➔ Xem chi tiết", font_size=16)

    c3 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.833), Inches(2.4), Inches(3.5), Inches(3.8))
    c3.name = "btn_hub_risk"
    _style_button(c3, COLOR_CARD, "TRỤ CỘT 3\n\nQUẢN TRỊ RỦI RO\n\n➔ Xem chi tiết", font_size=16)

    # --- Slide 2: Topic 1 (Strategy) ---
    s2 = prs.slides.add_slide(layout)
    _style_card(s2, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)
    c_s2 = _style_card(s2, Inches(1.0), Inches(1.0), Inches(11.333), Inches(4.5))
    c_s2.text_frame.word_wrap = True
    p = c_s2.text_frame.paragraphs[0]
    p.text = "CHIẾN LƯỢC MỞ RỘNG THỊ TRƯỜNG 2026"
    p.font.name = FONT_HEAD
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p2 = c_s2.text_frame.add_paragraph()
    p2.text = "\n• Mở rộng 45 chi nhánh mới tại khu vực Miền Bắc & Miền Trung.\n• Chuyển đổi số toàn diện quy trình cung ứng tự động.\n• Tăng trưởng doanh thu kỳ vọng đạt +28% YoY."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(17)
    p2.font.color.rgb = COLOR_TEXT

    btn_b1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.0), Inches(3.0), Inches(0.9))
    btn_b1.name = "btn_return_hub_1"
    _style_button(btn_b1, COLOR_BORDER, "⌂ VỀ MENU HUB", font_size=14)

    # --- Slide 3: Topic 2 (Finance) with Auxiliary Deep Dive button ---
    s3 = prs.slides.add_slide(layout)
    _style_card(s3, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)
    c_s3 = _style_card(s3, Inches(1.0), Inches(1.0), Inches(11.333), Inches(4.5))
    c_s3.text_frame.word_wrap = True
    p = c_s3.text_frame.paragraphs[0]
    p.text = "KẾT QUẢ TÀI CHÍNH & DỰ BÁO LỢI NHUẬN"
    p.font.name = FONT_HEAD
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p2 = c_s3.text_frame.add_paragraph()
    p2.text = "\n• Doanh thu Q4 bứt phá đạt 2.450 Triệu VNĐ.\n• Biên lợi nhuận gộp duy trì ổn định ở mức 42%.\n• Lợi nhuận thuần (EBIT) đạt 980 Triệu VNĐ."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(17)
    p2.font.color.rgb = COLOR_TEXT

    btn_b2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.0), Inches(3.0), Inches(0.9))
    btn_b2.name = "btn_return_hub_2"
    _style_button(btn_b2, COLOR_BORDER, "⌂ VỀ MENU HUB", font_size=14)

    btn_deep = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(6.0), Inches(4.8), Inches(0.9))
    btn_deep.name = "btn_goto_deepdive"
    _style_button(btn_deep, COLOR_AMBER, "XEM PHỤ LỤC KỸ THUẬT (DEEP DIVE) ➔", font_size=14)

    # --- Slide 4: Topic 3 (Risk) ---
    s4 = prs.slides.add_slide(layout)
    _style_card(s4, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)
    c_s4 = _style_card(s4, Inches(1.0), Inches(1.0), Inches(11.333), Inches(4.5))
    c_s4.text_frame.word_wrap = True
    p = c_s4.text_frame.paragraphs[0]
    p.text = "QUẢN TRỊ RỦI RO & BẢO MẬT HỆ THỐNG"
    p.font.name = FONT_HEAD
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED
    p2 = c_s4.text_frame.add_paragraph()
    p2.text = "\n• Kế hoạch dự phòng gián đoạn chuỗi cung ứng vật tư.\n• Kiểm toán an toàn thông tin ISO 27001 định kỳ quý.\n• Quỹ dự phòng rủi ro biến động tỷ giá."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(17)
    p2.font.color.rgb = COLOR_TEXT

    btn_b3 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.0), Inches(3.0), Inches(0.9))
    btn_b3.name = "btn_return_hub_3"
    _style_button(btn_b3, COLOR_BORDER, "⌂ VỀ MENU HUB", font_size=14)

    # --- Slide 5: Auxiliary Deep Dive (Called from Slide 3, returns via last_viewed!) ---
    s5 = prs.slides.add_slide(layout)
    _style_card(s5, Inches(0), Inches(0), Inches(13.333), Inches(7.5), COLOR_BG, COLOR_BG)
    c_s5 = _style_card(s5, Inches(1.0), Inches(1.0), Inches(11.333), Inches(4.5), COLOR_CARD, COLOR_AMBER)
    c_s5.text_frame.word_wrap = True
    p = c_s5.text_frame.paragraphs[0]
    p.text = "PHỤ LỤC KỸ THUẬT (AUXILIARY DRILL-DOWN)"
    p.font.name = FONT_HEAD
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p2 = c_s5.text_frame.add_paragraph()
    p2.text = "\nĐây là slide phân tích sâu được kích hoạt khi người nghe có nhu cầu đào sâu.\nSử dụng cơ chế 'Last Slide Viewed', người trình bày chỉ cần ấn nút quay lại phía dưới để trở về đúng mạch câu chuyện đang kể dở mà không bị gián đoạn!"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(17)
    p2.font.color.rgb = COLOR_TEXT

    btn_back_last = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.0), Inches(4.5), Inches(0.9))
    btn_back_last.name = "btn_back_to_caller"
    _style_button(btn_back_last, COLOR_ACCENT, "↺ QUAY VỀ MẠCH BÁO CÁO (LAST VIEWED)", font_size=14)

    prs.save(output_path)

    # Configure Navigation:
    # 1. Hub links (0 -> 1, 2, 3)
    # 2. Return to Hub (1, 2, 3 -> 0)
    # 3. Deep dive link (2 -> 4)
    # 4. Deep dive return (4 -> last_viewed!)
    recipe = {
        "kiosk_mode": False,
        "lock_advance_on_click": True,
        "navigation": [
            {"slide": 0, "shape_identifier": "btn_hub_strategy", "action": "jump_to_slide", "target": 1},
            {"slide": 0, "shape_identifier": "btn_hub_finance", "action": "jump_to_slide", "target": 2},
            {"slide": 0, "shape_identifier": "btn_hub_risk", "action": "jump_to_slide", "target": 3},
            {"slide": 1, "shape_identifier": "btn_return_hub_1", "action": "jump_to_slide", "target": 0},
            {"slide": 2, "shape_identifier": "btn_return_hub_2", "action": "jump_to_slide", "target": 0},
            {"slide": 2, "shape_identifier": "btn_goto_deepdive", "action": "jump_to_slide", "target": 4},
            {"slide": 3, "shape_identifier": "btn_return_hub_3", "action": "jump_to_slide", "target": 0},
            {"slide": 4, "shape_identifier": "btn_back_to_caller", "action": "last_viewed"},
        ],
    }
    configure_interactive_navigation(output_path, recipe, output_path=output_path)
    return output_path


def main():
    print("=== T048 Artifact Generation ===")

    # 1. Mini-Game State Machine Deck
    game_deck = ARTIFACTS_DIR / "interactive_adventure_game.pptx"
    build_interactive_adventure_game(game_deck)
    print(f"[1] Built interactive mini-game: {game_deck}")

    # 2. Executive Interactive Hub Deck
    hub_deck = ARTIFACTS_DIR / "executive_interactive_hub.pptx"
    build_executive_interactive_hub(hub_deck)
    print(f"[2] Built executive interactive hub: {hub_deck}")

    # 3. Inspection & Auditing
    audit_game = inspect_navigation_graph(game_deck)
    audit_hub = inspect_navigation_graph(hub_deck)

    (ARTIFACTS_DIR / "audit_game.json").write_text(json.dumps(audit_game, indent=2, ensure_ascii=False), encoding="utf-8")
    (ARTIFACTS_DIR / "audit_hub.json").write_text(json.dumps(audit_hub, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[3] Wrote navigation graph audits")

    # 4. Render previews via DeckCraft CLI
    if Path(DECKCRAFT_CLI).exists():
        game_previews = PREVIEWS_DIR / "game"
        hub_previews = PREVIEWS_DIR / "hub"
        game_previews.mkdir(parents=True, exist_ok=True)
        hub_previews.mkdir(parents=True, exist_ok=True)

        subprocess.run([DECKCRAFT_CLI, "render", str(game_deck), "--all", str(game_previews)], check=True)
        subprocess.run([DECKCRAFT_CLI, "render", str(hub_deck), "--all", str(hub_previews)], check=True)
        print(f"[4] Rendered DeckCraft 1920x1080 previews to: {PREVIEWS_DIR}")

    # 5. Compute SHA256 checksums
    sha_lines = []
    for f in sorted(ARTIFACTS_DIR.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS.txt":
            rel = f.relative_to(ARTIFACTS_DIR)
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            sha_lines.append(f"{h}  {rel}")
    (ARTIFACTS_DIR / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    print("[5] Computed SHA256SUMS.txt")
    print("All T048 artifacts ready!")


if __name__ == "__main__":
    main()
