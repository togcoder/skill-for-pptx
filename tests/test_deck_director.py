"""Unit tests for Deck Director compiler and narrative laws (T068)."""
import json
from pathlib import Path
import pytest

from scripts.deck_director import check_direction, compile_direction, scaffold_direction


@pytest.fixture
def valid_direction_data():
    return {
        "brief": {
            "audience": "Sinh viên đại học",
            "minutes": 15,
            "room": "Giảng đường 100 người",
            "decision": "Nắm vững 3 tiền đề của triết học Mác",
            "one_sentence": "Triết học Mác là bước ngoặt cách mạng trong lịch sử tư tưởng nhân loại.",
            "register": "editorial_teaching"
        },
        "style": {
            "preset": "editorial-crimson",
            "base_state": "poster_first",
            "image_role": "evidence"
        },
        "beats": [
            {
                "id": "b1",
                "job": "hook",
                "claim": "Khái luận triết học Mác – Lênin",
                "carrier": "art:hero",
                "attention": "art:hero",
                "figure": "arrive",
                "t0_says": "Chào mừng các bạn đến với chương mở đầu của học thuyết kinh điển.",
                "clicks": [
                    {
                        "id": "b1.1",
                        "lead_in": "Để bắt đầu hành trình,",
                        "state": "Tiêu đề xuất hiện định vị chủ đề bài giảng",
                        "post_click_says": "chúng ta cùng bước vào cánh cửa nền tảng tư duy hiện đại.",
                        "target_refs": ["title:main"]
                    }
                ]
            },
            {
                "id": "b2",
                "job": "define",
                "claim": "Triết học là hệ thống tri thức lý luận chung nhất về thế giới",
                "carrier": "art:plato",
                "attention": "art:plato",
                "figure": "build",
                "t0_says": "Nhìn vào bức tượng triết gia này, ai trong chúng ta cũng từng trăn trở về bản chất cuộc sống.",
                "clicks": [
                    {
                        "id": "b2.1",
                        "lead_in": "Nhưng để đúc kết thành khoa học,",
                        "state": "Định nghĩa hiện thành ba tầng lý luận",
                        "post_click_says": "giáo trình phân lập bức tranh tổng thể thành hai miền thực tại: thế giới vật chất bên ngoài và các thiết chế tương tác giữa loài người.",
                        "target_refs": ["card:def1", "card:def2"]
                    },
                    {
                        "id": "b2.2",
                        "lead_in": "Và khi đối chiếu với thực tiễn,",
                        "state": "Hai đối tượng đầu mờ đi để làm nổi bật tầng thứ ba",
                        "post_click_says": "đỉnh cao nhất chính là năng lực phản ánh thế giới vào trong ý thức và phương pháp tư biện của chính chúng ta.",
                        "target_refs": ["card:def3"]
                    }
                ]
            }
        ],
        "shots": [
            {
                "id": "sh1",
                "beat": "b1",
                "layout": "title",
                "objects": [
                    {"id": "art:hero", "role": "hero", "asset": {"file": "inputs/hero.png"}},
                    {"id": "title:main", "role": "title", "text": "Triết học Mác – Lênin"}
                ],
                "base_state": ["art:hero"],
                "state_after": {
                    "b1.1": {
                        "enter": ["title:main"],
                        "dim": [],
                        "highlight": [],
                        "exit": [],
                        "action": None
                    }
                }
            },
            {
                "id": "sh2",
                "beat": "b2",
                "layout": "asymmetric",
                "objects": [
                    {"id": "art:plato", "role": "anchor", "asset": {"file": "inputs/plato.png"}},
                    {"id": "card:def1", "role": "card", "text": "Quy luật Tự nhiên"},
                    {"id": "card:def2", "role": "card", "text": "Quan hệ Xã hội"},
                    {"id": "card:def3", "role": "card", "text": "Quy luật Tư duy"}
                ],
                "base_state": ["art:plato"],
                "state_after": {
                    "b2.1": {
                        "enter": ["card:def1", "card:def2"],
                        "dim": [],
                        "highlight": [],
                        "exit": [],
                        "action": None
                    },
                    "b2.2": {
                        "enter": ["card:def3"],
                        "dim": ["card:def1"],
                        "highlight": ["card:def3"],
                        "exit": [],
                        "action": None
                    }
                }
            }
        ]
    }


def test_valid_direction_passes(valid_direction_data):
    res = check_direction(valid_direction_data)
    assert res["ok"] is True
    assert len(res["errors"]) == 0


def test_coda_trap_empty_click(valid_direction_data):
    # Set an empty transition
    valid_direction_data["shots"][0]["state_after"]["b1.1"] = {
        "enter": [], "dim": [], "highlight": [], "exit": [], "action": None
    }
    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "NAR-CODA-TRAP" in codes


def test_coda_trap_t0_says_too_long(valid_direction_data):
    # Set t0_says to 38 words (>35 words threshold before click)
    valid_direction_data["beats"][1]["t0_says"] = (
        "Một hai ba bốn năm sáu bảy tám chín mười "
        "mười một mười hai mười ba mười bốn mười lăm mười sáu mười bảy mười tám mười chín hai mươi "
        "hai mốt hai hai hai ba hai bốn hai lăm hai sáu hai bảy hai tám hai chín ba mươi "
        "ba mốt ba hai ba ba ba bốn ba lăm ba sáu ba bảy ba tám"
    )
    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "NAR-CODA-TRAP" in codes


def test_unanchored_missing_target_refs(valid_direction_data):
    valid_direction_data["beats"][0]["clicks"][0]["target_refs"] = []
    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "NAR-UNANCHORED" in codes


def test_collision_missing_lead_in(valid_direction_data):
    # figure is assemble without lead_in
    valid_direction_data["beats"][1]["figure"] = "assemble"
    valid_direction_data["beats"][1]["clicks"][0]["lead_in"] = ""
    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "NAR-COLLISION" in codes


def test_additive_clutter_word_cap(valid_direction_data):
    # Add > 55 words across 3 clicks without any dim or exit
    shot = valid_direction_data["shots"][1]
    beat = valid_direction_data["beats"][1]
    # Add third click
    beat["clicks"].append({
        "id": "b2.3",
        "lead_in": "Tiếp theo là,",
        "state": "Thêm nội dung",
        "post_click_says": "giải thích thêm chi tiết",
        "target_refs": ["card:def4"]
    })
    shot["objects"].append({
        "id": "card:def4",
        "role": "card",
        "text": (
            "Nội dung này được cố tình viết rất dài dòng với mục đích tạo ra một khối lượng từ vựng khổng lồ "
            "vượt xa ngưỡng năm mươi lăm từ của toàn bộ slide nhằm kích hoạt luật chặn rác sân khấu khi diễn giả "
            "nhồi nhét quá nhiều câu chữ lên màn hình mà không hề có bất kỳ hành động làm mờ hay ẩn bớt các đối tượng cũ đi."
        )
    })
    shot["state_after"]["b2.3"] = {"enter": ["card:def4"], "dim": [], "highlight": [], "exit": [], "action": None}
    # Remove dim from b2.2
    shot["state_after"]["b2.2"]["dim"] = []

    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "DEN-ACTIVE-VIEW" in codes


def test_karaoke_redundancy_fails(valid_direction_data):
    # Make speech verbatim repeat on-slide text (> 45% containment)
    beat = valid_direction_data["beats"][1]
    beat["t0_says"] = "Quy luật Tự nhiên Quan hệ Xã hội Quy luật Tư duy bản chất vũ trụ"
    beat["clicks"][0]["post_click_says"] = "Quy luật Tự nhiên Quan hệ Xã hội được thể hiện rõ"
    res = check_direction(valid_direction_data)
    assert res["ok"] is False
    codes = [e["code"] for e in res["errors"]]
    assert "NAR-KARAOKE" in codes


def test_compile_direction(valid_direction_data):
    deck_spec, director_plan = compile_direction(valid_direction_data)
    assert "slides" in deck_spec
    assert len(deck_spec["slides"]) == 2
    assert deck_spec["slides"][0]["title"] == "Triết học Mác – Lênin"
    assert deck_spec["slides"][1]["layout"] == "asymmetric"

    assert "slides" in director_plan
    assert len(director_plan["slides"]) == 2
    assert len(director_plan["slides"][0]["click_beats"]) == 1
    assert len(director_plan["slides"][1]["click_beats"]) == 2
    # In v0.7 contract, motion targets live on the beat object referenced by the click
    beat_id = director_plan["slides"][1]["click_beats"][0]["motion_beats"][0]
    beat_obj = next(b for b in director_plan["slides"][1]["beats"] if b["id"] == beat_id)
    assert "Major Content" in beat_obj["targets"]
    assert "notes" in deck_spec["slides"][0]
    assert "[T=0]" in deck_spec["slides"][0]["notes"]
    assert "[CLICK 1 - b1.1]" in deck_spec["slides"][0]["notes"]


def test_pass1_check_ignores_speech(valid_direction_data):
    # Remove spoken cues and target_refs
    for b in valid_direction_data["beats"]:
        b["t0_says"] = ""
        for c in b["clicks"]:
            c["lead_in"] = ""
            c["post_click_says"] = ""
            c["target_refs"] = []

    # Pass 1 should pass (Stage & State Machine only)
    res_pass1 = check_direction(valid_direction_data, pass_num=1)
    assert res_pass1["ok"] is True
    assert len(res_pass1["errors"]) == 0

    # Pass 2 must fail on speech checks
    res_pass2 = check_direction(valid_direction_data, pass_num=2)
    assert res_pass2["ok"] is False
    codes = [e["code"] for e in res_pass2["errors"]]
    assert "NAR-T0-SAYS-MISSING" in codes
    assert "NAR-UNANCHORED" in codes


def test_scaffold_direction():
    scaffold = scaffold_direction(title="Học Thuyết Giá Trị", slides_count=3, preset="editorial-crimson")
    assert scaffold["brief"]["topic"] == "Học Thuyết Giá Trị"
    assert len(scaffold["beats"]) == 3
    assert len(scaffold["shots"]) == 3

    # Must pass both Pass 1 and Pass 2
    res1 = check_direction(scaffold, pass_num=1)
    assert res1["ok"] is True

    res2 = check_direction(scaffold, pass_num=2)
    assert res2["ok"] is True


def test_compile_exit_targets(valid_direction_data):
    # Add exit target to b2.2
    valid_direction_data["shots"][1]["state_after"]["b2.2"]["exit"] = ["card:def2"]
    deck_spec, director_plan = compile_direction(valid_direction_data)

    s2 = director_plan["slides"][1]
    exit_beats = [b for b in s2["beats"] if b["operation"] == "exit"]
    assert len(exit_beats) >= 1
    assert exit_beats[0]["effect"] == "fade-out"
    assert "Minor Content" in exit_beats[0]["targets"]


def test_narrative_critic_on_directed_pptx():
    import scripts.design_critic as dc
    pptx_path = Path("experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx")
    if pptx_path.is_file():
        crit = dc.critique(pptx_path)
        assert "narrative" in crit["scores"]
        assert crit["scores"]["narrative"] == 5.0
        assert crit["scores"]["overall"] >= 4.9
