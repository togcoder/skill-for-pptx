#!/usr/bin/env python3
"""T067 motion direction: rebuild T066's timing from a beat sheet.

Reads the frozen T066 deck, renames the Morph-convention shapes, replaces the
whole timing tree with the directed plan below, replaces the nine Morph
transitions with a 350 ms Fade, writes the presenter notes, and saves a copy.
No product code is changed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from lxml import etree as ET
from pptx import Presentation
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_animator as anim  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
SRC = ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx"
OUT = EXP / "motion" / "artifacts" / "T066-deck-directed.pptx"
PLAN_OUT = EXP / "motion" / "motion-plan.json"

# --- effect helpers -------------------------------------------------------
def E(shape, preset, trigger="click", dur=300, **kw):
    return {"shape": shape, "preset": preset, "trigger": trigger,
            "duration_ms": dur, **kw}


def R(shape, trigger="after", dur=250):
    return E(shape, "wipe-left", trigger, dur)


def A(shape, trigger="after"):
    return E(shape, "appear", trigger, 0)


def F(shape, trigger="click", dur=300):
    return E(shape, "fade", trigger, dur)


# --- the beat sheet, machine-readable ------------------------------------
SLIDES = []


def slide(n, title, base, beats, notes):
    SLIDES.append({"slide": n, "title": title, "base": base, "beats": beats,
                   "notes": notes})


slide(1, "Cover", [
    "bg", "panel", "kicker", "title", "subtitle", "caption",
    "marx-ring", "marx", "engels-ring", "engels", "lenin-ring", "lenin",
    "margin-rule", "margin-dot",
], [
    {"id": "auto-rings", "kind": "auto", "start": "auto",
     "spoken": "Chương 1 mở bằng ba chân dung, không phải ba biểu tượng: ba mốc của một dòng lý luận gắn với thực tiễn.",
     "visual": "Ba vòng vàng tự vẽ quanh ba chân dung đã hiện sẵn; không có gì bị giấu.",
     "roles": {"anchor": ["title", "marx", "engels", "lenin"],
               "evidence": ["subtitle", "caption"],
               "turn": [], "payoff": []},
     "hero": "Ba vòng vàng vẽ liên tiếp như một nhịp thở, không phải một cú click.",
     "duration_ms": 1500,
     "effects": [
         E("marx-ring", "circle", "click", 500),
         E("engels-ring", "circle", "after", 500),
         E("lenin-ring", "circle", "after", 500),
     ]},
], "Mở đầu: Chương 1 đặt câu hỏi nền tảng — triết học là gì, và triết học Mác – Lênin trả lời từ đâu? Ba chân dung đã ở đó, như ba mốc của một lý luận gắn với thực tiễn. Không cần click; ba vòng vàng tự vẽ trong 1,5 giây đầu.")

slide(2, "Triết học là gì?", [
    "bg", "kicker", "title", "def1", "def2",
    "plato-disc", "plato", "plato-cap", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Triết học không phải một định nghĩa để học thuộc: nó là hệ thống tri thức lý luận chung nhất về thế giới và vị trí con người trong đó.",
     "visual": "Định nghĩa thứ nhất hiện lên dưới câu hỏi; tượng triết gia đã ở đó từ đầu.",
     "roles": {"anchor": ["title", "plato"], "evidence": ["def1"],
               "turn": [], "payoff": []},
     "hero": "Không có cú bay nào; chữ hiện như một dòng chú giải.",
     "duration_ms": 350,
     "effects": [F("def1", "click", 350)]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Định nghĩa thứ hai hẹp hơn: khoa học về những quy luật chung nhất của tự nhiên, xã hội và tư duy.",
     "visual": "Dòng thứ hai nối tiếp, cùng một nhịp.",
     "roles": {"anchor": ["title", "plato"], "evidence": ["def2"],
               "turn": [], "payoff": []},
     "hero": "Một dòng nữa, không thêm hiệu ứng.",
     "duration_ms": 350,
     "effects": [F("def2", "click", 350)]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "Ba việc triết học làm: cho ta một thế giới quan, một phương pháp luận, và một logic để không tự lừa mình.",
     "visual": "Ba gạch vàng vẽ lần lượt; nhãn của từng gạch hiện ngay sau khi gạch tới.",
     "roles": {"anchor": ["title", "plato"], "evidence": ["l0-rule", "l1-rule", "l2-rule"],
               "turn": [], "payoff": ["l0-h", "l1-h", "l2-h"]},
     "hero": "Ba gạch vàng như ba nhịp đánh dấu, mỗi lúc chỉ một gạch chạy.",
     "duration_ms": 1000,
     "effects": [
         R("l0-rule", "click", 250), A("l0-n"), E("l0-h", "appear", "with", 0), E("l0-s", "appear", "with", 0),
         R("l1-rule", "after", 250), A("l1-n"), E("l1-h", "appear", "with", 0), E("l1-s", "appear", "with", 0),
         R("l2-rule", "after", 250), A("l2-n"), E("l2-h", "appear", "with", 0), E("l2-s", "appear", "with", 0),
     ]},
], "Định nghĩa không phải để học thuộc. [nhấp] Định nghĩa thứ nhất: một hệ thống tri thức lý luận chung nhất về thế giới và vị trí con người trong đó. [nhấp] Định nghĩa thứ hai: khoa học về những quy luật chung nhất của tự nhiên, xã hội và tư duy. [nhấp] Ba việc triết học làm: thế giới quan, phương pháp luận, logic biện chứng. Tượng triết gia đã ở đó từ đầu — nó là bối cảnh, không phải phần thưởng cuối slide.")

slide(3, "Vật chất hay ý thức?", [
    "bg", "kicker", "title", "left", "left-title", "left-body", "left-foot",
    "right", "right-title", "right-body", "right-foot", "qmark", "qline", "qcap",
    "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Mặt thứ nhất là bản thể luận: vật chất có trước, quyết định ý thức.",
     "visual": "Thẻ trái dựng lên; tiêu đề thẻ hiện sau tấm nền, thân và nhãn đi kèm.",
     "roles": {"anchor": ["title"], "evidence": ["left"],
               "turn": [], "payoff": ["left-foot"]},
     "hero": "Tấm nền đỏ thẫm trượt lên như một trang được đặt xuống.",
     "duration_ms": 550,
     "effects": [
         E("left", "wipe-up", "click", 300),
         F("left-title", "after", 250),
         A("left-body"), A("left-foot", "with"),
     ]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Mặt thứ hai là nhận thức luận: ý thức có sau, phản ánh vật chất.",
     "visual": "Thẻ phải dựng lên, đối xứng với thẻ trái.",
     "roles": {"anchor": ["title"], "evidence": ["right"],
               "turn": [], "payoff": ["right-foot"]},
     "hero": "Cùng một động tác, đối xứng — không phải một hiệu ứng mới.",
     "duration_ms": 550,
     "effects": [
         E("right", "wipe-down", "click", 300),
         F("right-title", "after", 250),
         A("right-body"), A("right-foot", "with"),
     ]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "Câu hỏi còn lại nằm giữa hai câu trả lời: cái nào có trước?",
     "visual": "Dấu hỏi vàng rơi vào khoảng trống giữa hai thẻ; gạch và caption theo sau.",
     "roles": {"anchor": ["title"], "evidence": ["left", "right"],
               "turn": ["qmark"], "payoff": ["qcap"]},
     "hero": "Dấu hỏi là cú chốt: nó chỉ xuất hiện sau khi cả hai câu trả lời đã có mặt.",
     "duration_ms": 800,
     "effects": [
         E("qmark", "zoom", "click", 350),
         E("qline", "wipe-left", "after", 250),
         F("qcap", "after", 250),
     ]},
], "Đây là câu hỏi nền tảng, không phải câu hỏi triết học duy nhất. [nhấp] Mặt bản thể luận: vật chất có trước, quyết định ý thức. [nhấp] Mặt nhận thức luận: ý thức có sau, phản ánh vật chất. [nhấp] Và câu hỏi vẫn ở giữa: cái nào có trước? Dấu hỏi chỉ hiện sau khi cả hai câu trả lời đã có mặt.")

slide(4, "Biện chứng hay siêu hình?", [
    "bg", "kicker", "title", "dialectic-circle", "dialectic-core", "dialectic-arrow",
    "dialectic-card", "dialectic-name", "dialectic-desc",
    "straight-line", "straight-dot-8.35", "straight-dot-9.95", "straight-dot-11.55",
    "straight-label", "meta-card", "meta-name", "meta-desc", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Biện chứng nhìn sự vật trong liên hệ, vận động, mâu thuẫn — vòng tròn đã ở đó, nhưng ý nghĩa chưa được gọi tên.",
     "visual": "Thẻ đỏ thẫm của biện chứng dựng lên dưới vòng tròn; tên và mô tả hiện sau.",
     "roles": {"anchor": ["title", "dialectic-circle", "dialectic-core"],
               "evidence": ["dialectic-card"], "turn": [], "payoff": ["dialectic-desc"]},
     "hero": "Thẻ biện chứng là tấm nền duy nhất chuyển động; vòng tròn đứng yên làm điểm tựa.",
     "duration_ms": 550,
     "effects": [
         E("dialectic-card", "wipe-up", "click", 300),
         F("dialectic-name", "after", 250),
         A("dialectic-desc"),
     ]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Siêu hình nhìn sự vật tách rời, tĩnh tại, phiến diện — một đường thẳng có ba điểm dừng.",
     "visual": "Đường thẳng vẽ từ trái sang phải, dừng ở ba điểm; nhãn hiện sau khi đường đã dừng.",
     "roles": {"anchor": ["title"], "evidence": ["straight-line", "straight-dot-8.35", "straight-dot-9.95", "straight-dot-11.55"],
               "turn": ["straight-label"], "payoff": []},
     "hero": "Đường thẳng là cú tương phản: nó chạy nhưng không chuyển hóa, dừng ở ba mốc cố định.",
     "duration_ms": 750,
     "effects": [
         R("straight-line", "click", 450),
         A("straight-dot-8.35"), E("straight-dot-9.95", "appear", "with", 0), E("straight-dot-11.55", "appear", "with", 0),
         F("straight-label", "after", 300),
     ]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "Cùng một sự vật, hai cách nhìn; chọn cách nào là chọn cái gì được thấy.",
     "visual": "Thẻ siêu hình khép lại bên phải; bố cục hai bên đã cân.",
     "roles": {"anchor": ["title"], "evidence": ["meta-card"], "turn": [],
               "payoff": ["meta-desc"]},
     "hero": "Không thêm chuyển động mới: chỉ khép tấm nền còn lại.",
     "duration_ms": 550,
     "effects": [
         E("meta-card", "wipe-up", "click", 300),
         F("meta-name", "after", 250),
         A("meta-desc"),
     ]},
], "Biện chứng không phải 'mọi thứ đều thay đổi' một cách mơ hồ. [nhấp] Nó là cách xem xét trong chỉnh thể, có mâu thuẫn, có chuyển hóa — vòng tròn đã ở đó từ đầu. [nhấp] Siêu hình là cách xem xét tách rời, tĩnh tại, phiến diện — một đường thẳng dừng ở ba điểm. [nhấp] Cùng một sự vật, hai cách nhìn; chọn cách nào là chọn cái gì được thấy.")

slide(5, "Điều kiện ra đời", [
    "bg", "kicker", "title", "sub", "card0", "card0-n", "card0-h", "card0-b",
    "card1", "card1-n", "card1-h", "card1-b", "card2", "card2-n", "card2-h", "card2-b",
    "timeline", "timeline-dot", "timeline-text", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Điều kiện kinh tế – xã hội: chủ nghĩa tư bản phát triển mạnh, giai cấp vô sản xuất hiện.",
     "visual": "Thẻ 01 dựng lên; số, tiêu đề, thân theo sau.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["card0"], "turn": [], "payoff": []},
     "hero": "Tấm nền thẻ 01 trượt lên, một mình.",
     "duration_ms": 550,
     "effects": [
         E("card0", "wipe-up", "click", 300),
         F("card0-h", "after", 250),
         A("card0-n"), A("card0-b", "with"),
     ]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Điều kiện khoa học tự nhiên: tế bào, bảo toàn năng lượng, tiến hóa — ba phát hiện đổi cách nhìn thế giới.",
     "visual": "Thẻ 02 dựng lên, cùng nhịp với thẻ 01.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["card1"], "turn": [], "payoff": []},
     "hero": "Cùng một động tác, không đổi ngôn ngữ.",
     "duration_ms": 550,
     "effects": [
         E("card1", "wipe-up", "click", 300),
         F("card1-h", "after", 250),
         A("card1-n"), A("card1-b", "with"),
     ]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "Điều kiện tư tưởng: Hegel, Feuerbach và chủ nghĩa xã hội không tưởng — một dòng để phê phán và kế thừa.",
     "visual": "Thẻ 03 dựng lên, khép hàng ba điều kiện.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["card2"], "turn": [], "payoff": []},
     "hero": "Tấm nền cuối cùng khép hàng; không có gì nhảy.",
     "duration_ms": 550,
     "effects": [
         E("card2", "wipe-up", "click", 300),
         F("card2-h", "after", 250),
         A("card2-n"), A("card2-b", "with"),
     ]},
    {"id": "c4", "kind": "click", "start": "click",
     "spoken": "Ba điều kiện gặp nhau ở một mốc: 1848, Tuyên ngôn Đảng Cộng sản.",
     "visual": "Đường thời gian vẽ từ trái sang phải; điểm 1848 và nhãn landing.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["card0", "card1", "card2"],
               "turn": ["timeline"], "payoff": ["timeline-text"]},
     "hero": "Đường thời gian là cú chốt: nó nối ba điều kiện thành một mốc lịch sử.",
     "duration_ms": 1000,
     "effects": [
         R("timeline", "click", 500),
         E("timeline-dot", "zoom", "after", 250),
         F("timeline-text", "after", 250),
     ]},
], "Ba điều kiện không tách rời. [nhấp] Kinh tế – xã hội: chủ nghĩa tư bản phát triển mạnh, giai cấp vô sản xuất hiện. [nhấp] Khoa học tự nhiên: tế bào, bảo toàn năng lượng, tiến hóa. [nhấp] Tư tưởng: Hegel, Feuerbach, chủ nghĩa xã hội không tưởng. [nhấp] Ba điều kiện gặp nhau ở 1848 — Tuyên ngôn Đảng Cộng sản. Mác và Ăngghen không sáng tạo từ hư không.")

slide(6, "Ba bộ phận", [
    "bg", "kicker", "title", "sub", "part0", "part0-n", "part0-h", "part0-b",
    "part1", "part1-n", "part1-h", "part1-b", "part2", "part2-n", "part2-h", "part2-b",
    "arrow1", "arrow2", "note", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Ba bộ phận không phải ba môn học rời: triết học cho phương pháp, kinh tế chính trị chỉ ra quan hệ sản xuất, chủ nghĩa xã hội khoa học nói về con đường.",
     "visual": "Ba thẻ dựng lên như một làn sóng từ trái sang phải; mỗi thẻ tự hoàn tất trước khi thẻ sau bắt đầu.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["part0", "part1", "part2"],
               "turn": [], "payoff": []},
     "hero": "Làn sóng ba thẻ là cú chuyển động duy nhất; nó nói 'một chỉnh thể', không phải ba cú click rời.",
     "duration_ms": 1650,
     "effects": [
         E("part0", "wipe-up", "click", 300), F("part0-h", "after", 250), A("part0-n"), A("part0-b", "with"),
         E("part1", "wipe-up", "after", 300), F("part1-h", "after", 250), A("part1-n"), A("part1-b", "with"),
         E("part2", "wipe-up", "after", 300), F("part2-h", "after", 250), A("part2-n"), A("part2-b", "with"),
     ]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Ba bộ phận nối với nhau, và cả hệ thống là một chỉnh thể: triết học là nền tảng phương pháp; kinh tế chính trị là giải phẫu xã hội; CNXH khoa học là mục tiêu và con đường.",
     "visual": "Hai mũi nối hiện ra giữa các thẻ; câu chốt hiện cuối cùng.",
     "roles": {"anchor": ["title", "sub"], "evidence": ["part0", "part1", "part2"],
               "turn": ["arrow1", "arrow2"], "payoff": ["note"]},
     "hero": "Hai mũi nối là cú chốt: chúng biến ba thẻ thành một hệ.",
     "duration_ms": 800,
     "effects": [
         F("arrow1", "click", 250),
         E("arrow2", "fade", "with", 250),
         F("note", "after", 300),
     ]},
], "Ba bộ phận không phải ba môn học rời. [nhấp] Triết học cho phương pháp; kinh tế chính trị chỉ ra quan hệ sản xuất; chủ nghĩa xã hội khoa học nói về con đường. [nhấp] Hai mũi nối cho thấy chúng là một chỉnh thể: triết học là nền tảng phương pháp; kinh tế chính trị là giải phẫu xã hội; CNXH khoa học là mục tiêu và con đường.")

slide(7, "Một dòng chảy", [
    "bg", "kicker", "title", "sub",
    "marx-ring", "marx", "marx-date", "marx-name", "marx-desc",
    "engels-ring", "engels", "engels-date", "engels-name", "engels-desc",
    "lenin-ring", "lenin", "lenin-date", "lenin-name", "lenin-desc",
    "timeline", "tl-1848", "tl-1848-t", "tl-1867", "tl-1867-t", "tl-1917", "tl-1917-t",
    "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "C. Mác, 1818–1883: Tư bản, 1867.",
     "visual": "Ba chân dung đã ở đó; tên và niên đại của Mác hiện dưới chân dung ông.",
     "roles": {"anchor": ["title", "sub", "marx", "engels", "lenin"],
               "evidence": ["marx-name", "marx-date"], "turn": [], "payoff": []},
     "hero": "Không có ảnh nào xuất hiện; chỉ có nhãn được gọi tên.",
     "duration_ms": 300,
     "effects": [F("marx-name", "click", 250), A("marx-date"), A("marx-desc", "with")]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Ph. Ăngghen, 1820–1895: Tuyên ngôn, 1848.",
     "visual": "Nhãn của Ăngghen hiện, cùng nhịp.",
     "roles": {"anchor": ["title", "sub", "marx", "engels", "lenin"],
               "evidence": ["engels-name", "engels-date"], "turn": [], "payoff": []},
     "hero": "Cùng một nhịp, không đổi động tác.",
     "duration_ms": 300,
     "effects": [F("engels-name", "click", 250), A("engels-date"), A("engels-desc", "with")]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "V.I. Lênin, 1870–1924: Cách mạng, 1917.",
     "visual": "Nhãn của Lênin hiện, khép ba chân dung.",
     "roles": {"anchor": ["title", "sub", "marx", "engels", "lenin"],
               "evidence": ["lenin-name", "lenin-date"], "turn": [], "payoff": []},
     "hero": "Nhãn cuối khép lại; ba người đã được gọi tên.",
     "duration_ms": 300,
     "effects": [F("lenin-name", "click", 250), A("lenin-date"), A("lenin-desc", "with")]},
    {"id": "c4", "kind": "click", "start": "click",
     "spoken": "Ba người, ba thời điểm, một dự án: dòng chảy từ lý luận đến cách mạng.",
     "visual": "Đường thời gian vẽ; ba điểm 1848, 1867, 1917 landing theo thứ tự.",
     "roles": {"anchor": ["title", "sub", "marx", "engels", "lenin"],
               "evidence": ["marx-name", "engels-name", "lenin-name"],
               "turn": ["timeline"], "payoff": ["tl-1917-t"]},
     "hero": "Đường thời gian là cú chốt: nó nối ba chân dung thành một dòng.",
     "duration_ms": 1400,
     "effects": [
         R("timeline", "click", 600),
         E("tl-1848", "zoom", "after", 250), A("tl-1848-t", "with"),
         E("tl-1867", "zoom", "after", 250), A("tl-1867-t", "with"),
         E("tl-1917", "zoom", "after", 250), A("tl-1917-t", "with"),
     ]},
], "Ba người, ba thời điểm, một dự án. [nhấp] C. Mác, 1818–1883: Tư bản, 1867. [nhấp] Ph. Ăngghen, 1820–1895: Tuyên ngôn, 1848. [nhấp] V.I. Lênin, 1870–1924: Cách mạng, 1917. [nhấp] Đường thời gian nối họ: 1848, 1867, 1917. Đừng biến họ thành ba biểu tượng tách rời khỏi lịch sử — ba chân dung đã ở đó từ đầu, như ba người cùng một dòng.")

slide(8, "Đối tượng & chức năng", [
    "bg", "kicker", "title",
    "tile0", "tile0-n", "tile0-h", "tile0-b", "tile1", "tile1-n", "tile1-h", "tile1-b",
    "tile2", "tile2-n", "tile2-h", "tile2-b", "tile3", "tile3-n", "tile3-h", "tile3-b",
    "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Hai chức năng đầu: thế giới quan — nhìn thế giới như một chỉnh thể có quy luật; phương pháp luận — cách đặt vấn đề và hành động trong thực tiễn.",
     "visual": "Hàng trên: hai khung cùng vẽ, rồi hai tiêu đề cùng hiện; số và thân theo sau.",
     "roles": {"anchor": ["title"], "evidence": ["tile0", "tile1"], "turn": [], "payoff": []},
     "hero": "Hai khung là một cặp: chúng vẽ cùng lúc, không lệch nhịp.",
     "duration_ms": 550,
     "effects": [
         E("tile0", "wipe-up", "click", 300), E("tile1", "wipe-up", "with", 300),
         F("tile0-h", "after", 250), E("tile1-h", "fade", "with", 250),
         A("tile0-n"), E("tile1-n", "appear", "with", 0),
         A("tile0-b"), E("tile1-b", "appear", "with", 0),
     ]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Hai chức năng sau: phê phán cái lỗi thời, mở đường cho cái mới; và không đứng trên khoa học — là phương pháp của khoa học.",
     "visual": "Hàng dưới: cùng một cặp, khép lưới 2×2.",
     "roles": {"anchor": ["title"], "evidence": ["tile2", "tile3"], "turn": [],
               "payoff": ["tile3-h"]},
     "hero": "Hàng dưới khép lưới; bốn chức năng thành một bộ công cụ.",
     "duration_ms": 550,
     "effects": [
         E("tile2", "wipe-up", "click", 300), E("tile3", "wipe-up", "with", 300),
         F("tile2-h", "after", 250), E("tile3-h", "fade", "with", 250),
         A("tile2-n"), E("tile3-n", "appear", "with", 0),
         A("tile2-b"), E("tile3-b", "appear", "with", 0),
     ]},
], "Chức năng không phải 'ứng dụng triết học vào mọi thứ'. [nhấp] Hai chức năng đầu: thế giới quan — nhìn thế giới như một chỉnh thể có quy luật; phương pháp luận — cách đặt vấn đề và hành động trong thực tiễn. [nhấp] Hai chức năng sau: phê phán cái lỗi thời, mở đường cho cái mới; không đứng trên khoa học mà là phương pháp của khoa học. Bốn ô là một bộ công cụ, không phải bốn định nghĩa.")

slide(9, "Luận cương", [
    "bg", "kicker", "quote-mark", "quote0", "quote1", "quote2",
    "quote-rule", "author", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Câu này thường bị trích như một khẩu hiệu; tên tác giả và năm mới biến nó thành một phát ngôn có nguồn.",
     "visual": "Cả câu đã ở đó từ đầu; gạch vàng và dòng tác giả hiện sau, như một chú thích.",
     "roles": {"anchor": ["quote-mark", "quote0", "quote1", "quote2"],
               "evidence": ["author"], "turn": ["quote-rule"], "payoff": []},
     "hero": "Gạch vàng kéo ra dưới câu trích; không có chữ nào bị giấu.",
     "duration_ms": 700,
     "effects": [R("quote-rule", "click", 400), F("author", "after", 300)]},
], "Câu này thường bị trích như một khẩu hiệu. Cả câu đã ở đó từ đầu — 'Các nhà triết học chỉ giải thích thế giới bằng nhiều cách khác nhau; vấn đề là cải tạo thế giới.' [nhấp] Gạch vàng và tên tác giả: C. Mác, Luận cương về Phoiơbắc, 1845. Lý luận không phải để chiêm ngưỡng mà để chỉ ra hành động có thể kiểm chứng.")

slide(10, "Mang theo", [
    "bg", "kicker", "title",
    "take0-n", "take0-h", "take0-b", "take0-line",
    "take1-n", "take1-h", "take1-b", "take1-line",
    "take2-n", "take2-h", "take2-b", "take2-line",
    "closing", "credits", "margin-rule", "margin-dot",
], [
    {"id": "c1", "kind": "click", "start": "click",
     "spoken": "Mang theo câu hỏi nền tảng: cái nào có trước, vật chất hay ý thức?",
     "visual": "Dòng 01: tiêu đề hiện, số và câu hỏi theo sau; gạch mảnh khép dòng.",
     "roles": {"anchor": ["title"], "evidence": ["take0-h", "take0-b"], "turn": [], "payoff": []},
     "hero": "Một dòng được đặt xuống, không có gì bay.",
     "duration_ms": 300,
     "effects": [F("take0-h", "click", 250), A("take0-n"), A("take0-b", "with"), A("take0-line", "with")]},
    {"id": "c2", "kind": "click", "start": "click",
     "spoken": "Mang theo cách nhìn biện chứng: sự vật trong liên hệ, vận động, mâu thuẫn.",
     "visual": "Dòng 02 hiện, cùng nhịp.",
     "roles": {"anchor": ["title"], "evidence": ["take1-h", "take1-b"], "turn": [], "payoff": []},
     "hero": "Cùng một nhịp.",
     "duration_ms": 300,
     "effects": [F("take1-h", "click", 250), A("take1-n"), A("take1-b", "with"), A("take1-line", "with")]},
    {"id": "c3", "kind": "click", "start": "click",
     "spoken": "Mang theo lý luận gắn thực tiễn: giải thích thế giới để cải tạo thế giới.",
     "visual": "Dòng 03 hiện; ba dòng đã đủ.",
     "roles": {"anchor": ["title"], "evidence": ["take2-h", "take2-b"], "turn": [], "payoff": []},
     "hero": "Dòng cuối của danh sách khép lại.",
     "duration_ms": 300,
     "effects": [F("take2-h", "click", 250), A("take2-n"), A("take2-b", "with"), A("take2-line", "with")]},
    {"id": "c4", "kind": "click", "start": "click",
     "spoken": "Kết bằng câu hỏi: trong ba cách nhìn này, cách nào bạn đang thiếu nhất khi phân tích một vấn đề thật?",
     "visual": "Câu chốt nổi lên từ dưới danh sách; credits đã ở đó từ đầu.",
     "roles": {"anchor": ["title"], "evidence": ["take0-h", "take1-h", "take2-h"],
               "turn": ["closing"], "payoff": ["closing"]},
     "hero": "Câu chốt là cú nâng duy nhất: nó thoát khỏi danh sách, không lặp lại một dòng nào.",
     "duration_ms": 500,
     "effects": [E("closing", "float-in", "click", 500)]},
], "Ba điều mang theo, không phải ba định nghĩa. [nhấp] Câu hỏi nền tảng: cái nào có trước, vật chất hay ý thức? [nhấp] Cách nhìn biện chứng: sự vật trong liên hệ, vận động, mâu thuẫn. [nhấp] Lý luận gắn thực tiễn: giải thích thế giới để cải tạo thế giới. [nhấp] Kết bằng câu hỏi: trong ba cách nhìn này, cách nào bạn đang thiếu nhất khi phân tích một vấn đề thật?")

# --- transition: Fade 350 ms ---------------------------------------------
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def set_fade(slide, duration_ms=350):
    root = slide._element
    for child in list(root):
        if child.tag == f"{{{MC}}}AlternateContent":
            if child.find(".//p:transition", anim.NS) is not None:
                root.remove(child)
        elif child.tag == qn("p:transition"):
            root.remove(child)
    tr = ET.Element(qn("p:transition"))
    tr.set("spd", "med")
    tr.set(f"{{{P14}}}dur", str(duration_ms))
    ET.SubElement(tr, qn("p:fade"))
    timing = root.find("p:timing", anim.NS)
    if timing is not None:
        timing.addprevious(tr)
    else:
        root.append(tr)


def clean(name: str) -> str:
    if name == "!!thread":
        return "margin-rule"
    if name == "!!dot":
        return "margin-dot"
    if name.startswith("!!"):
        return name[2:]
    return name


def main():
    prs = Presentation(str(SRC))
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # 1. retire the Morph naming convention
    renamed = []
    for idx, slide in enumerate(prs.slides, 1):
        # T066 revealed dialectic-foot under an opaque card: a dead shape.
        if idx == 4:
            for shape in list(slide.shapes):
                if shape.name == "dialectic-foot":
                    shape._element.getparent().remove(shape._element)
        for shape in slide.shapes:
            old = shape.name
            new = clean(old)
            if new != old:
                shape.name = new
                renamed.append({"slide": idx, "old": old, "new": new})

    # 2. replace timing + notes, and set the fade transition
    plan_slides = []
    for idx, (slide, spec) in enumerate(zip(prs.slides, SLIDES), 1):
        assert spec["slide"] == idx, (spec["slide"], idx)
        ids = {}
        for shape in slide.shapes:
            if shape.name:
                ids[shape.name] = str(shape.shape_id)
        clicks = []
        for beat in spec["beats"]:
            effects = []
            for e in beat["effects"]:
                shape = e["shape"]
                if shape not in ids:
                    raise KeyError(f"slide {idx}: shape {shape!r} not found; have {sorted(ids)}")
                effects.append({
                    "spid": ids[shape], "preset": e["preset"],
                    "trigger": e["trigger"], "duration_ms": e["duration_ms"],
                    **{k: v for k, v in e.items() if k not in ("shape", "preset", "trigger", "duration_ms")},
                })
            clicks.append({"id": beat["id"], "start": beat.get("start", "click"),
                           "effects": effects})
        receipt = anim.apply_timeline(slide._element, clicks, mode="replace")
        slide.notes_slide.notes_text_frame.text = spec["notes"]
        if idx > 1:
            set_fade(slide, 350)
        else:
            # cover has no transition; make sure an inherited one is gone
            for child in list(slide._element):
                if child.tag == f"{{{MC}}}AlternateContent" or child.tag == qn("p:transition"):
                    slide._element.remove(child)
        plan_slides.append({
            "slide": idx, "title": spec["title"], "base": spec["base"],
            "beats": [{k: v for k, v in b.items() if k != "effects"} | {
                "effects": [{**e, "spid": ids[e["shape"]]} for e in b["effects"]]}
                for b in spec["beats"]],
            "com": {"appended_click_groups": receipt["appended_click_groups"],
                    "replaced_existing_timing": receipt["replaced_existing_timing"]},
        })

    prs.save(str(OUT))
    PLAN_OUT.write_text(json.dumps({
        "deck": "T066-deck-directed.pptx",
        "source": "experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx",
        "date": "2026-11-04",
        "rules": {
            "base_state": "title, claim, key image and margin rule are visible at t=0; no entrance effect on them",
            "reading_order": "top-to-bottom, left-to-right; a label appears only after its carrier",
            "max_simultaneous_movers": 2,
            "hero_moves_per_slide": 1,
            "transitions": "0 Morph; 350 ms Fade on slides 2-10; no transition on slide 1",
            "morph_audit": "0 of 9 kept: no adjacent pair shares an object or an idea that survives the transition",
        },
        "renamed": renamed,
        "slides": plan_slides,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), "bytes": OUT.stat().st_size,
                      "slides": len(prs.slides), "renamed": len(renamed)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
