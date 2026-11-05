#!/usr/bin/env python3
"""Presentation script <-> motion plan (T024).

The script decides WHEN things appear; the deck's structure and the style
decide HOW they move.

* parse_script(): Markdown/plain scripts with slide headings ("## Slide 3",
  "Trang 3:", or a heading matching a slide title) and click cues
  ("[click]", "[nhấp]", "[bấm]", "[next]", ">>").  Text before the first cue
  is the slide intro.  Sections without cues are split into paragraphs.
* plan_from_script(): aligns every script segment with the slide resources it
  mentions (accent-insensitive token overlap, numbers weigh more), turns first
  mentions into reveals (keeping cards, labels, process steps and cycle stages
  together), repeated mentions into emphasis, records narration per click, and
  reports gaps: clicks with nothing to show and numbers the slide does not
  contain.  With fill_gaps=True a gap becomes a generated callout.
* script_from_plan(): writes a complete presenter script (narration per click)
  for a plan, in the deck's language, so a deck without any script still gets
  one; an AI should then rewrite it into natural speech.
* write_notes(): appends the motion script to speaker notes (creating notes
  slides from the notes master when missing).
"""
import argparse
import copy
import json
from pathlib import Path
import re
import sys
import unicodedata
from zipfile import ZipFile

from lxml import etree as E

sys.path.insert(0,str(Path(__file__).resolve().parent))
import motion_director as md  # noqa: E402
from data_motion_recipes import chart_motion_recipe  # noqa: E402

CUE=re.compile(r"^\s*(?:\[(?:click|nhấp|nhap|bấm|bam|next|tiếp|tiep)\]|\((?:click|nhấp|bấm)\)|>>)\s*",re.I)
HEAD_NUM=re.compile(r"^\s*(?:#{1,6}\s*)?(?:slide|trang|slide số|page)\s*(\d+)\s*[:.\-–—)]?\s*(.*)$",re.I)
HEAD_TXT=re.compile(r"^\s*#{1,6}\s*(.+?)\s*$")
STOP=set("""the a an of and or to in is are was were be been we our you your for on with this that these those it its as at by
from than then so but not no yes can will would should may might do does did have has had there here which who what when how
va la cua cac nhung mot trong cho voi de duoc co khong nay do thi ma se da khi tu ve o ra len nhu cung hon rat
chung ta toi ban minh day roi nen vi neu tai theo sau truoc nua moi nhieu it""".split())
NUM=re.compile(r"\d+(?:[.,]\d+)?")

# T081: Canonical 15-verb table linking pedagogical story verbs to motion/Morph categories
VERB_TABLE = {
    "soi": {"action": "spotlight", "type": "in-slide/morph", "desc": "thấu kính lướt rồi dừng"},
    "gom thành hệ thống": {"action": "converge", "type": "morph", "desc": "mảnh hội tụ, xếp hàng"},
    "cân nhắc": {"action": "hold", "type": "in-slide", "desc": "đứng yên (lặng)"},
    "nghiêng về": {"action": "tilt", "type": "in-slide", "desc": "cân nghiêng hai phía"},
    "nối lại, vận động": {"action": "connect-cycle", "type": "morph", "desc": "ô tan, hình lên vòng tròn, xoay"},
    "đứng ở / còn trống": {"action": "slot-in", "type": "in-slide", "desc": "thẻ vào ô, ô trống sáng viền"},
    "đứng ở": {"action": "slot-in", "type": "in-slide", "desc": "thẻ vào ô"},
    "còn trống": {"action": "slot-in", "type": "in-slide", "desc": "ô trống sáng viền"},
    "lộn ngược, ghép": {"action": "flip-merge", "type": "morph", "desc": "xoay 180°, hai nửa gộp"},
    "lộn ngược": {"action": "flip-merge", "type": "morph", "desc": "xoay 180°"},
    "dựng lại": {"action": "flip-merge", "type": "morph", "desc": "dựng lại trên chân"},
    "dâng lên, gặp nhau": {"action": "converge-rise", "type": "in-slide", "desc": "dòng sáng rồi dịu, hội tụ"},
    "dâng lên": {"action": "converge-rise", "type": "in-slide", "desc": "dòng sáng rồi dịu"},
    "gặp nhau": {"action": "converge-rise", "type": "in-slide", "desc": "hội tụ gặp nhau"},
    "trở thành, thống nhất": {"action": "transform-unify", "type": "morph", "desc": "cùng vật thể đổi trạng thái"},
    "trở thành": {"action": "transform-unify", "type": "morph", "desc": "vật thể đổi trạng thái"},
    "thống nhất": {"action": "transform-unify", "type": "morph", "desc": "thanh nền + mái khóa lại"},
    "đi qua thời gian": {"action": "timeline-pan", "type": "morph", "desc": "camera trượt dọc dòng thời gian"},
    "đi vào lịch sử": {"action": "timeline-pan", "type": "morph", "desc": "camera trượt theo dòng thời gian"},
    "từ… đến…": {"action": "timeline-pan", "type": "morph", "desc": "camera trượt dọc dòng thời gian"},
    "đi sâu, phóng to chi tiết": {"action": "zoom-in", "type": "morph", "desc": "camera zoom vào"},
    "phóng to": {"action": "zoom-in", "type": "morph", "desc": "camera zoom vào"},
    "nhưng": {"action": "swap-weights", "type": "in-slide/morph", "desc": "hoán đổi trọng lượng"},
    "song": {"action": "swap-weights", "type": "in-slide/morph", "desc": "hoán đổi trọng lượng"},
    "bản lề": {"action": "swap-weights", "type": "in-slide/morph", "desc": "hoán đổi trọng lượng"},
    "quay lại, nhớ lại": {"action": "revisit-layout", "type": "morph", "desc": "lặp bố cục cảnh trước"},
    "nhìn lại": {"action": "revisit-layout", "type": "morph", "desc": "lặp bố cục cảnh trước"},
    "loại bỏ, phủ định": {"action": "dim-exit", "type": "in-slide", "desc": "thu nhỏ, mờ hoặc gạch bỏ rồi ra"},
    "nhấn một trong nhiều": {"action": "dim-others", "type": "in-slide", "desc": "các mục khác mờ đi (vòng đời dim)"},
    "nhìn": {"action": "spotlight", "type": "in-slide", "desc": "nhìn qua kính"},
}

# T081 (D004, D005): Cliché placeholder phrases banned across screenplay text
BANNED_PLACEHOLDERS = [
    "tất yếu khách quan",
    "chuyển đổi số toàn diện",
    "hành động quyết liệt là chìa khóa",
    "bước hoàn thiện",
    "chỉ số 1",
    "chỉ số 2",
    "chỉ số 3",
    "chỉ số 4",
    "lorem ipsum",
    "{title}"
]


def fold(text):
    t=unicodedata.normalize("NFD",(text or "").lower()).replace("đ","d")
    return "".join(c for c in t if unicodedata.category(c)!="Mn")


def tokens(text,keep_stop=False):
    raw=re.findall(r"[a-z0-9]+(?:[.,][0-9]+)?",fold(text))
    return [w.replace(",",".") for w in raw if (len(w)>1 or w.isdigit()) and (keep_stop or w not in STOP)]


def cand_tokens(cand):
    """Short labels ("Do", "Act") keep words that are stopwords elsewhere."""
    short=len((cand["text"] or "").split())<=2
    return set(tokens(cand["text"],keep_stop=short))


def language(model):
    text=" ".join(o["text"] or "" for s in model["slides"] for o in s["objects"])
    viet=sum(1 for c in text if c in "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ")
    return "vi" if viet>=max(3,len(text)//200) else "en"


# ---------------------------------------------------------------------------
# Parsing


def parse_script(text):
    sections=[]
    cur=None
    for line in text.splitlines():
        m=HEAD_NUM.match(line)
        h=None if m else HEAD_TXT.match(line)
        if m or h:
            cur={"slide":int(m.group(1)) if m else None,"title":(m.group(2) if m else h.group(1)).strip(),
                 "intro":"","segments":[]}
            sections.append(cur)
            continue
        if cur is None:
            continue
        stripped=line.strip()
        if CUE.match(line):
            cur["segments"].append({"text":CUE.sub("",line).strip(),"cue":True})
        elif stripped:
            if cur["segments"] and cur["segments"][-1]["cue"] and not cur["segments"][-1].get("closed"):
                seg=cur["segments"][-1]
                seg["text"]=(seg["text"]+" "+stripped).strip()
            elif any(s["cue"] for s in cur["segments"]):
                cur["segments"][-1]["text"]+=" "+stripped
            else:
                cur.setdefault("_paras",[[]])[-1].append(stripped.lstrip("-*• ").strip())
        else:
            if cur["segments"] and cur["segments"][-1]["cue"]:
                cur["segments"][-1]["closed"]=True
            elif "_paras" in cur and cur["_paras"][-1]:
                cur["_paras"].append([])
    for sec in sections:
        paras=[" ".join(p) for p in sec.pop("_paras",[]) if p]
        if any(s["cue"] for s in sec["segments"]):
            sec["intro"]=" ".join(paras)
        else:
            sec["segments"]=[{"text":p,"cue":False} for p in paras]
        for s in sec["segments"]:
            s.pop("closed",None)
    return sections




def parse_intent(text):
    """Extract Section 0 (Intent) key-value pairs from Markdown table or bullets."""
    intent = {}
    table_m = re.search(r"##\s*(?:Phần 0[.:\s]+Ý đồ|Intent|Phần Ý đồ)(.*?)(?=[\r\n]+##|\Z)", text, re.S | re.I)
    if table_m:
        sec = table_m.group(1)
        for line in sec.splitlines():
            row = [c.strip() for c in line.strip().split("|") if c.strip()]
            if len(row) >= 2 and not all(c.startswith("-") for c in row):
                k, v = row[0].lower(), row[1]
                if any(x in k for x in ("người nghe", "audience")):
                    intent["audience"] = v
                elif any(x in k for x in ("họ đang tin", "tin trước", "belief_before")):
                    intent["belief_before"] = v
                elif any(x in k for x in ("sau buổi", "tin sau", "belief_after")):
                    intent["belief_after"] = v
                elif any(x in k for x in ("xương sống", "spine", "one_sentence")):
                    intent["spine"] = re.sub(r"\*+", "", v).strip()
                elif any(x in k for x in ("ẩn dụ", "metaphor")):
                    intent["metaphor"] = v
                elif any(x in k for x in ("diễn viên", "actor")):
                    intent["actors_raw"] = v
                    actors = re.findall(r"`(!![a-zA-Z0-9_\-\.\*]+)`", v)
                    intent["persistent_actors"] = [a for a in actors if a.startswith("!!")]
                elif any(x in k for x in ("khung", "frame")):
                    intent["frame"] = v
                elif any(x in k for x in ("thời lượng", "duration", "minutes")):
                    intent["duration"] = v
                elif any(x in k for x in ("giọng", "tone", "register")):
                    intent["tone"] = v
    return intent


def parse_gold_script(text):
    """Parse structured screenplay scenes (T078/T081 gold format)."""
    SCENE_HEAD = re.compile(r"^##\s*(?:Cảnh|Slide)\s*(\d+)[\.:\s\-–—]*(.*)$", re.M | re.I)
    splits = list(SCENE_HEAD.finditer(text))
    if not splits:
        return []
    scenes = []
    for i, m in enumerate(splits):
        idx = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = splits[i+1].start() if i+1 < len(splits) else len(text)
        chunk = text[start:end]

        turn_m = re.search(r"-\s*\*\*Chuyển dịch[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\Z)", chunk, re.S)
        morph_m = re.search(r"-\s*\*\*Morph từ [Cc]ảnh\s*(\d+)[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\Z)", chunk, re.S)
        base_m = re.search(r"-\s*\*\*Trên màn hình lúc mở[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\Z)", chunk, re.S)
        speech_m = re.search(r"-\s*\*\*Lời nói[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\Z)", chunk, re.S)
        verb_m = re.search(r"-\s*\*\*Động từ(?: → chuyển động)?[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\Z)", chunk, re.S)
        why_m = re.search(r"-\s*\*\*Vì sao[^*]*:\*\*\s*(.*?)(?=\n-\s*\*\*|\n##|\Z)", chunk, re.S)
        claim_m = re.search(r"^\s*claim:\s*(.*)$", chunk, re.M | re.I)

        speech = speech_m.group(1).strip() if speech_m else ""
        speech_clean = re.sub(r"^\s*>\s*", "", speech, flags=re.M)
        speech_clean = re.sub(r"\s+", " ", speech_clean).strip()

        cue_pattern = re.compile(r"(\*{0,2}\[(?:CLICK|nhấp|nhap|bấm|bam|next)\]\*{0,2})", re.I)
        parts = cue_pattern.split(speech_clean)
        clicks = []
        lead_in = parts[0].strip() if parts else ""
        for c_idx in range(1, len(parts), 2):
            cue = parts[c_idx]
            post = parts[c_idx+1].strip() if c_idx+1 < len(parts) else ""
            clicks.append({
                "index": (c_idx + 1) // 2,
                "cue": "[CLICK]",
                "lead_in": parts[c_idx-1].strip() if c_idx == 1 else "",
                "post_click": post
            })

        # Match verbs from VERB_TABLE
        vm_text = verb_m.group(1).strip() if verb_m else ""
        matched_verbs = [v for v in VERB_TABLE if v in vm_text.lower()]

        turn_text = turn_m.group(1).strip() if turn_m else ""
        turn_from, turn_to = "", ""
        if "→" in turn_text:
            t_parts = turn_text.split("→", 1)
            turn_from, turn_to = t_parts[0].strip().strip('"'), t_parts[1].strip().strip('"')

        scenes.append({
            "index": idx,
            "title": title,
            "turn": {"from": turn_from, "to": turn_to, "raw": turn_text},
            "morph_from": int(morph_m.group(1)) if morph_m else None,
            "morph_text": morph_m.group(2).strip() if morph_m else "",
            "base_state": base_m.group(1).strip() if base_m else "",
            "speech": speech_clean,
            "clicks": clicks,
            "verb_motion": vm_text,
            "matched_verbs": matched_verbs,
            "why": why_m.group(1).strip() if why_m else "",
            "claim": claim_m.group(1).strip() if claim_m else ""
        })
    return scenes


def parse_script_full(text):
    """Unified entry point: returns intent + scenes (gold format) or legacy sections."""
    intent = parse_intent(text)
    gold_scenes = parse_gold_script(text)
    if gold_scenes:
        return {"format": "gold", "intent": intent, "scenes": gold_scenes}
    return {"format": "legacy", "intent": intent, "sections": parse_script(text)}


def check_script(text):
    """Automated quality gate for presentation screenplay (T081).
    Enforces D003, D004, D005 without requiring an LLM.
    """
    errors = []
    warnings = []

    intent = parse_intent(text)
    if not intent:
        errors.append("[SCRIPT-NO-INTENT] Missing Section 0 / Intent table (## Phần 0. Ý đồ)")
    else:
        spine = intent.get("spine", "")
        if not spine:
            errors.append("[SCRIPT-SPINE-MISSING] Missing spine sentence (Câu xương sống)")
        else:
            w_count = len(spine.split())
            if w_count > 22:
                errors.append(f"[SCRIPT-SPINE-LONG] Spine exceeds maximum 22 words ({w_count} words): '{spine}'")
            elif w_count > 20:
                warnings.append(f"[SCRIPT-SPINE-RECOMMENDATION] Spine has {w_count} words (recommended <= 20 words): '{spine}'")

    scenes = parse_gold_script(text)
    if not scenes:
        simple_secs = parse_script(text)
        if not simple_secs:
            errors.append("[SCRIPT-NO-SCENES] No scenes or slides found in script")
        else:
            scenes = [{"index": s["slide"] or i+1, "title": s["title"], "clicks": s["segments"],
                       "speech": " ".join(x["text"] for x in s["segments"]), "base_state": s["intro"],
                       "why": "", "claim": "", "verb_motion": "", "matched_verbs": []} for i, s in enumerate(simple_secs)]

    for phrase in BANNED_PLACEHOLDERS:
        if phrase.lower() in text.lower():
            errors.append(f"[SCRIPT-PLACEHOLDER] Banned placeholder / filler phrase found: '{phrase}'")

    for s in scenes:
        s_id = f"Cảnh {s['index']} ({s['title']})"
        speech = s.get("speech", "")
        base = s.get("base_state", "")
        clicks = s.get("clicks", [])
        claim = s.get("claim", "")

        if claim and len(claim.split()) > 25:
            errors.append(f"[SCRIPT-CLAIM-LONG] {s_id}: Claim exceeds 25 words ({len(claim.split())} words)")

        if not speech and not clicks:
            errors.append(f"[SCRIPT-EMPTY-SCENE] {s_id}: Scene has no speech or narration")

        verb_motion = s.get("verb_motion", "").lower()
        is_intentional_hold = any(w in verb_motion or w in speech.lower() for w in ("không click", "lặng", "pause", "hold"))

        if speech and not clicks and not is_intentional_hold:
            errors.append(f"[SCRIPT-NO-CLICK] {s_id}: Speech exists but no [CLICK] cue was placed")

        if not base and not s.get("morph_from"):
            warnings.append(f"[SCRIPT-BASE-UNSTATED] {s_id}: Opening base state (t=0) is unstated")

        if s.get("verb_motion") and not s.get("matched_verbs"):
            warnings.append(f"[SCRIPT-VERB-UNVERIFIED] {s_id}: Verb in '{s['verb_motion'][:40]}' is not in the 15 verified verbs")

        # [SCRIPT-MORPH-CONTINUITY] Ensure actors morphing from previous scene exist in that previous scene
        if s.get("morph_from"):
            src_idx = s["morph_from"]
            src_scene = next((prev for prev in scenes if prev["index"] == src_idx), None)
            morph_text = s.get("morph_text", "")
            morph_actors = re.findall(r"!![a-zA-Z0-9_\-]+", morph_text)
            if src_scene:
                src_content = (src_scene.get("morph_text", "") + " " + src_scene.get("base_state", "") + " " +
                               src_scene.get("speech", "") + " " +
                               src_scene.get("verb_motion", ""))
                for actor in morph_actors:
                    if actor not in src_content:
                        warnings.append(f"[SCRIPT-MORPH-CONTINUITY] {s_id}: Actor '{actor}' declared morphing from Scene {src_idx} was not found in Scene {src_idx}")

        # [SCRIPT-ASPECT-16x9] Warn if circle is defined with w == h in normalized coords on 16:9 canvas
        full_scene_text = base + " " + s.get("verb_motion", "") + " " + s.get("morph_text", "")
        circle_matches = re.finditer(r"(?:vòng tròn|hình tròn|đồng tâm|circle)[^.]*?w\s*=\s*([0-9.]+)[^.]*?h\s*=\s*([0-9.]+)", full_scene_text, re.I)
        for cm in circle_matches:
            w_val, h_val = float(cm.group(1)), float(cm.group(2))
            if abs(w_val - h_val) < 0.02 and h_val > 0.05:
                warnings.append(f"[SCRIPT-ASPECT-16x9] {s_id}: Circle defined with w={w_val} == h={h_val} in normalized coords will distort on 16:9 canvas (recommended w ~= 0.5625 * h)")

    ok = len(errors) == 0
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "intent": intent,
        "scenes_count": len(scenes)
    }


def compile_to_scene(text):
    """Compile script.md into scene.json draft for T075 scene compiler."""
    parsed = parse_script_full(text)
    intent = parsed.get("intent", {})
    raw_scenes = parsed.get("scenes") or []

    actors = []
    p_actors = intent.get("persistent_actors", [])
    for a in p_actors:
        actors.append({"id": a, "role": "persistent", "desc": ""})

    scenes = []
    for s in raw_scenes:
        clicks = []
        for c in s.get("clicks", []):
            verb = s["matched_verbs"][0] if s.get("matched_verbs") else ""
            clicks.append({
                "id": f"c{s['index']}.{c['index']}",
                "index": c["index"],
                "cue": c["cue"],
                "lead_in": c["lead_in"],
                "post_click": c["post_click"],
                "verb": verb,
                "action": VERB_TABLE.get(verb, {}).get("action", "reveal")
            })

        scenes.append({
            "id": f"s{s['index']}",
            "index": s["index"],
            "title": s["title"],
            "turn": s.get("turn", {}),
            "morph_from": f"s{s['morph_from']}" if s.get("morph_from") else None,
            "base_state": s.get("base_state", ""),
            "speech": s.get("speech", ""),
            "clicks": clicks,
            "verb_motion": s.get("verb_motion", ""),
            "reason": s.get("why", "")
        })

    return {
        "version": 1,
        "generator": "motion_script.compile_to_scene (T081)",
        "intent": intent,
        "actors": actors,
        "scenes": scenes
    }


def compile_to_direction(text):
    """Compile script.md into direction.json format for backward compatibility with deck_director.py."""
    parsed = parse_script_full(text)
    intent = parsed.get("intent", {})
    raw_scenes = parsed.get("scenes") or []

    brief = {
        "title": raw_scenes[0]["title"] if raw_scenes else "Deck",
        "one_sentence": intent.get("spine", ""),
        "audience": intent.get("audience", ""),
        "duration": intent.get("duration", "15 phút")
    }

    beats = []
    shots = []
    for s in raw_scenes:
        b_id = f"b{s['index']}"
        sh_id = f"sh{s['index']}"

        clicks = []
        for c in s.get("clicks", []):
            clicks.append({
                "id": f"{b_id}.{c['index']}",
                "says": (c["lead_in"] + " " + c["post_click"]).strip(),
                "lead_in": c["lead_in"],
                "post_click_says": c["post_click"]
            })

        beats.append({
            "id": b_id,
            "scene": f"s{s['index']}",
            "job": "define",
            "claim": s.get("claim") or s["title"],
            "clicks": clicks
        })

        shots.append({
            "id": sh_id,
            "beat_id": b_id,
            "layout": "asymmetric" if s["index"] > 1 else "title",
            "t0_says": s.get("clicks", [{}])[0].get("lead_in", "") if s.get("clicks") else s.get("speech", ""),
            "base_objects": [{"id": "Title", "role": "title", "text": s["title"]}],
            "clicks": [{"beat_click_id": f"{b_id}.{c['index']}", "enter": ["Points"]} for c in s.get("clicks", [])]
        })

    return {
        "brief": brief,
        "style": {
            "theme": "editorial",
            "register": intent.get("tone", "editorial_teaching")
        },
        "beats": beats,
        "shots": shots
    }


def scaffold_script():
    """Emit an empty script.md template with guiding questions and zero filler prose (D004, D005)."""
    return """# Kịch bản Thuyết trình: [Tên Đề Tài]

## Phần 0. Ý đồ

| Ô | Nội dung |
|---|---|
| Người nghe | <!-- Ai đang nghe? Trình độ? Họ đang nghĩ gì khi bước vào phòng? --> |
| Họ đang tin | <!-- Niềm tin hiện tại của họ trước khi nghe buổi này? --> |
| Sau buổi họ phải tin | <!-- Niềm tin hoặc nhận thức cốt lõi họ mang về? --> |
| Câu xương sống (≤ 20 từ) | <!-- 1 câu duy nhất <= 20 từ định hình toàn bộ bài thuyết trình --> |
| Ẩn dụ chủ đạo | <!-- Hình tượng thị giác xuyên suốt kết nối các cảnh (vd: thấu kính, cán cân...) --> |
| Diễn viên bền vững (cho Morph) | <!-- Danh sách vật thể mang định danh xuyên slide: `!!kinh`, `!!the1`, `!!the2` --> |
| Khung kể | <!-- Khung dẫn dắt: Câu hỏi -> Công cụ -> Áp dụng, hoặc Nỗi đau -> Giải pháp -> Minh chứng --> |
| Thời lượng | <!-- Số phút dự kiến và số cảnh --> |
| Giọng | <!-- Giọng điệu: đối thoại, hùng biện, giảng giải hay phản biện --> |

---

## Cảnh 1. [Tiêu đề Cảnh Mở Đầu]

- **Chuyển dịch[^*]*:** [Khán giả nghĩ gì] → [Sau cảnh này khán giả thấy gì]
- **Trên màn hình lúc mở[^*]*:** [Mô tả trạng thái t=0; TUYỆT ĐỐI KHÔNG ĐỂ MÀN HÌNH TRỐNG]
- **Lời nói[^*]*:**
  > [Đoạn mở đầu lời nói...] **[CLICK]** [tiếp tục câu nói, đặt đúng chữ bản lề]
- **Động từ → chuyển động:** [Chọn từ bảng động từ: soi, nghiêng về, gom thành hệ thống, lộn ngược, hoán đổi trọng lượng...] → [Mô tả chuyển động tương ứng của vật thể mang `!!id`]
- **Vì sao[^*]*:** [Lý do sư phạm / lý luận kể chuyện cho cảnh này]

---

## Cảnh 2. [Tiêu đề Cảnh Tiếp Theo]

- **Chuyển dịch[^*]*:** [Chuyển dịch nhận thức]
- **Morph từ cảnh 1:** [Mô tả diễn viên mang `!!id` chuyển trạng thái thế nào từ cảnh trước]
- **Trên màn hình lúc mở[^*]*:** [Mô tả trạng thái t=0]
- **Lời nói[^*]*:**
  > [Lời thoại có chứa mốc] **[CLICK]** [đoạn nói sau click]
- **Động từ → chuyển động:** [Động từ hành động] → [Chuyển động]
- **Vì sao[^*]*:** [Lý do]
"""


def match_sections(sections,model):
    """Map script sections to slide indices (number first, else title)."""
    out={}
    for sec in sections:
        idx=sec["slide"]
        if idx is None:
            best,score=None,0
            want=set(tokens(sec["title"]))
            for s in model["slides"]:
                title=md._implicit_title(s) or next((o for o in s["objects"] if o["placeholder"]
                                                      and o["placeholder"]["type"] in md.TITLE_TYPES),None)
                have=set(tokens(title["text"] if title else ""))
                sc=len(want&have)/max(1,len(want|have))
                if sc>score:
                    best,score=s["index"],sc
            idx=best if score>=0.5 else None
        if idx is not None and 1<=idx<=len(model["slides"]):
            out[idx]=sec
    return out


# ---------------------------------------------------------------------------
# Alignment


def _candidates(slide):
    """Mentionable resources: (key, object, paragraph index or None, text)."""
    title=md._implicit_title(slide)
    cands=[]
    for o in slide["objects"]:
        if o["placeholder"] and o["placeholder"]["type"] in md.TITLE_TYPES|md.CHROME_TYPES:
            continue
        if o is title or o["already_animated"]:
            continue
        if len(o["paragraphs"])>=2 and not md._is_heading(o):
            for p in o["paragraphs"]:
                cands.append({"key":f"{o['id']}#{p['index']}","obj":o,"para":p["index"],"text":p["text"],"level":p["level"]})
        else:
            text=o["text"] or ""
            keywords=set()
            if o["kind"]=="chart":
                text=o["name"]
                keywords=set(tokens("chart graph biểu đồ"))
            elif o["kind"]=="picture":
                text=o["name"]
                keywords=set(tokens("picture photo image ảnh hình"))
            if not text.strip():
                continue
            cands.append({"key":o["id"],"obj":o,"para":None,"text":text,"level":0,"keywords":keywords})
    return cands


def _score(seg_tokens,cand,weights=None):
    """Weighted overlap. Words shared by many resources on the slide weigh
    less; long paragraphs also count how much of the script line they cover
    (paraphrases rarely repeat a long paragraph)."""
    ct=cand_tokens(cand)
    bonus=0.5 if cand.get("keywords") and cand["keywords"]&seg_tokens else 0.0
    if not ct:
        return bonus
    hit=ct&seg_tokens
    nums={t for t in ct if NUM.fullmatch(t) and len(t)>1}
    if nums and nums&seg_tokens:
        return 1.0
    if len(ct)==1:
        return 1.0 if hit else bonus
    w=weights or {}
    cover=sum(w.get(t,1.0) for t in hit)/sum(w.get(t,1.0) for t in ct)
    if len(ct)>=8:
        content={t for t in seg_tokens if t not in STOP}
        if content:
            cover=max(cover,0.9*sum(w.get(t,1.0) for t in hit&content)/sum(w.get(t,1.0) for t in content))
    return min(1.0,cover+bonus)


def _position(seg_text,cand):
    folded=fold(seg_text)
    pos=[m.start() for t in cand_tokens(cand) for m in [re.search(rf"\b{re.escape(t)}\b",folded)] if m]
    return min(pos) if pos else len(folded)


def _groups(slide):
    """object id -> group record (card / labeled / step / cycle) from the director's units."""
    by={}
    for u in md._units(slide):
        kind=u["kind"]
        if kind=="card":
            for o in u["objs"]:
                by[o["id"]]={"kind":"card","objs":u["objs"]}
        elif kind=="labeled":
            for o in u["objs"]:
                by[o["id"]]={"kind":"labeled","objs":u["objs"]}
        elif kind=="process":
            for st in u["steps"]:
                rec={"kind":"step","objs":st["connectors"]+[st["step"]]}
                for o in rec["objs"]:
                    by[o["id"]]=rec
        elif kind=="cycle":
            rec={"kind":"cycle","objs":u["members"],"hub":u["hub"]}
            for o in u["members"]:
                by[o["id"]]=rec
            if u["hub"]:
                by[u["hub"]["id"]]={"kind":"hub","objs":[u["hub"]]}
    return by


def align(slide,section,threshold=0.5):
    cands=_candidates(slide)
    segments=section["segments"]
    seg_tokens=[set(tokens(s["text"],keep_stop=True)) for s in segments]
    df={}
    for c in cands:
        for t in cand_tokens(c):
            df[t]=df.get(t,0)+1
    weights={t:1.0/n for t,n in df.items()}
    first={}
    mentions=[[] for _ in segments]
    for c in cands:
        scores=[_score(st,c,weights) for st in seg_tokens]
        best=max(scores,default=0)
        # First mention = first line that is nearly as strong as the best one,
        # so a weak early echo does not steal a later, clear mention.
        hits=[i for i,sc in enumerate(scores) if sc>=max(threshold,best-0.15)]
        if hits:
            first[c["key"]]=hits[0]
            for i,sc in enumerate(scores):
                if sc>=threshold:
                    mentions[i].append((c,sc))
    gaps=[]
    slide_nums={t for o in slide["objects"] for t in tokens(o["text"] or "",keep_stop=True) if NUM.fullmatch(t)}
    for i,s in enumerate(segments):
        missing=sorted({t for t in seg_tokens[i] if NUM.fullmatch(t)}-slide_nums)
        if missing:
            gaps.append({"segment":i,"kind":"number-not-on-slide","values":missing,"text":s["text"]})
    return cands,first,mentions,gaps


def _key_phrase(text,values=None):
    sentences=re.split(r"(?<=[.!?…])\s+",text.strip())
    pick=next((s for s in sentences if values and any(v in fold(s).replace(",",".") for v in values)),sentences[0])
    words=pick.split()
    phrase=" ".join(words[:18])+("…" if len(words)>18 else "")
    return phrase.strip(" .")


def _bundle_keys(bundle,slide):
    """Source resources a draft click bundle reveals or focuses."""
    objs={}
    for o in slide["objects"]:
        for k in (o["name"],o["id"],o["token"]):
            objs.setdefault(k,o)
    reveal,focus=[],None
    kind="reveal"
    for b in bundle["beats"]:
        if b.get("layer")=="ambient" and b["timing_intent"]=="on-slide-start":
            kind="ambient"
        if b.get("recipe")=="spotlight":
            kind="focus"
            focus=objs.get(b["targets"][0])
            continue
        if b.get("recipe")=="release":
            kind="release" if kind!="focus" else kind
            continue
        for t in b["targets"]:
            o=objs.get(t)
            if o is None:
                continue
            if b["operation"]=="text-build" and b.get("paragraphs"):
                reveal+= [f"{o['id']}#{p}" for p in b["paragraphs"]]
            else:
                reveal.append(o["id"])
    return kind,reveal,focus


def plan_from_script(model,script_text,goal="",style="modern",fill_gaps=False,threshold=0.5):
    """Director v0.7 plan whose clicks follow the script.

    The draft director decides HOW each resource moves (cards, labels,
    process rails, cycle tours, chart builds...); the script decides WHEN:
    every draft click bundle is moved to the script line that first names
    its resources, focus bundles go to the line that names their target
    again, and the script's narration is attached to each click."""
    sections=match_sections(parse_script(script_text),model)
    fx=md.STYLES[style]
    slides=[]
    report={}
    for s in model["slides"]:
        sec=sections.get(s["index"])
        if sec is None:
            report[s["index"]]={"status":"no script section; slide left static"}
            continue
        if s["existing_click_groups"]:
            report[s["index"]]={"status":"existing animation kept; script attached as narration only",
                                "intro":sec["intro"],"narration":[x["text"] for x in sec["segments"]]}
            continue
        cands,first,mentions,gaps=align(s,sec,threshold)
        mention_segs={}
        for i,ms in enumerate(mentions):
            for c,_ in ms:
                mention_segs.setdefault(c["key"],[]).append(i)
        draft_slide,_=md.draft_slide(dict(s,notes="walk the steps in order"),style)
        beats_by={b["id"]:b for b in (draft_slide or {}).get("beats",[])}
        bundles=[{"beats":[copy.deepcopy(beats_by[m]) for m in c["motion_beats"]],"click":c}
                 for c in (draft_slide or {}).get("click_beats",[])]
        components=list((draft_slide or {}).get("components",[]))
        placed={}
        ambient=None
        reveal_seg={}
        dropped=[]
        focus_bundles=[]
        release_bundle=None
        for bi,b in enumerate(bundles):
            kind,keys,focus=_bundle_keys(b,s)
            if kind=="ambient":
                ambient=b
                continue
            if kind=="reveal":
                segs=[first[k] for k in keys if k in first]
                if not segs:
                    dropped.append(b["click"]["purpose"])
                    continue
                seg=min(segs)
                for k in keys:
                    reveal_seg[k]=seg
                    reveal_seg[k.split("#")[0]]=min(seg,reveal_seg.get(k.split("#")[0],seg))
                pos=min((_position(sec["segments"][seg]["text"],c) for c in cands if c["key"] in keys and first.get(c["key"])==seg),default=0)
                placed.setdefault(seg,[]).append((pos,bi,b))
            elif kind=="focus" and focus is not None:
                focus_bundles.append((bi,b,focus))
            elif kind=="release":
                release_bundle=(bi,b)
        # Paraphrase fallback: a cued line that names nothing recognisable takes
        # the next unplaced reveal bundle in the director's reading order.
        by_order=[]
        unplaced=[(bi,b) for bi,b in enumerate(bundles) if _bundle_keys(b,s)[0]=="reveal"
                  and not any(bi==x[1] for lst in placed.values() for x in lst)]
        for i,seg in enumerate(sec["segments"]):
            if i in placed or not seg["cue"] or not unplaced:
                continue
            if any(first.get(c["key"])==i or sc>=0.8 for c,sc in mentions[i]):
                continue
            prev=[x[1] for j,lst in placed.items() if j<i for x in lst]
            nxt=[(bi,b) for bi,b in unplaced if bi>max(prev,default=-1)]
            if not nxt:
                continue
            bi,b=nxt[0]
            placed[i]=[(0,bi,b)]
            unplaced=[x for x in unplaced if x[0]!=bi]
            by_order.append({"segment":i,"kind":"placed-by-order","bundle":b["click"]["purpose"],"text":seg["text"]})
            dropped=[d for d in dropped if d!=b["click"]["purpose"]]
            for k in _bundle_keys(b,s)[1]:
                reveal_seg.setdefault(k,i)
        gaps.extend(by_order)
        # Focus: at most one per script line, the resource the line names first,
        # and only after that resource has been revealed.
        free=list(focus_bundles)
        for i,seg in enumerate(sec["segments"]):
            options=[(_position(seg["text"],next(c for c in cands if c["key"]==f["id"])),bi,b,f)
                     for bi,b,f in free if i in mention_segs.get(f["id"],[]) and i>reveal_seg.get(f["id"],-1)
                     and any(c["key"]==f["id"] for c in cands)]
            if options:
                pos,bi,b,f=min(options,key=lambda x:x[0])
                placed.setdefault(i,[]).append((pos,bi,b))
                free=[x for x in free if x[0]!=bi]
        dropped+= [b["click"]["purpose"] for _,b,_ in free]
        # Release goes to the first later line that names nothing new (e.g.
        # "and the cycle starts again"). With no such line the slide still
        # ends on the whole picture: an unscripted closing click settles it,
        # so nothing snaps back when the next slide (or Morph) takes over.
        focus_segs=[i for i,lst in placed.items() for _,_,x in lst if _bundle_keys(x,s)[0]=="focus"]
        settle=None
        if release_bundle and focus_segs:
            later=[i for i in range(max(focus_segs)+1,len(sec["segments"])) if i not in placed]
            if later:
                placed[later[0]]=[(0,release_bundle[0],release_bundle[1])]
            else:
                settle=release_bundle[1]
        elif release_bundle:
            dropped.append(release_bundle[1]["click"]["purpose"])
        beats=[]
        clicks=[]
        intro=sec["intro"]
        n=[0]
        if ambient:
            beats.extend(ambient["beats"])
            clicks.append(dict(ambient["click"]))
        for i,seg in enumerate(sec["segments"]):
            group=[b for _,_,b in sorted(placed.get(i,[]),key=lambda x:(x[0],x[1]))]
            members=[]
            for gi,b in enumerate(group):
                for bj,beat in enumerate(b["beats"]):
                    if bj==0:
                        beat["timing_intent"]="on-click" if gi==0 else "after-previous"
                    elif beat["timing_intent"]=="on-click":
                        beat["timing_intent"]="after-previous"
                    members.append(beat)
            if not members:
                again=[(c,sc) for c,sc in mentions[i] if first[c["key"]]<i and sc>=0.8]
                if again:
                    o=max(again,key=lambda cs:cs[1])[0]["obj"]
                    n[0]+=1
                    members.append(md._beat(f"stress-{n[0]}",f"The script returns to '{(o['text'] or o['name'])[:40]}': pulse it.",
                                            "emphasize",[o["token"]],"on-click"))
                elif fill_gaps and seg["cue"]:
                    gap=next((g for g in gaps if g["segment"]==i),None)
                    cid=f"callout{i+1}"
                    comp=md._component(cid,"callout","states what the script says at this click",
                                       "Resource gap: the script needs this point on screen but the slide has no object for it.",
                                       anchors=[],text=_key_phrase(seg["text"],gap["values"] if gap else None))
                    comp["data_provenance"]="user-provided"
                    components.append(comp)
                    members.append(md._beat(f"gap-{i+1}","Show the generated callout for this script line.","reveal",[cid],
                                            "on-click",*fx["callout"]))
                    gaps.append({"segment":i,"kind":"filled-with-callout","component":cid,"text":seg["text"]})
                else:
                    if seg["cue"]:
                        gaps.append({"segment":i,"kind":"click-without-visual","text":seg["text"]})
                    if clicks and clicks[-1].get("narration") is not None:
                        clicks[-1]["narration"]=(clicks[-1]["narration"]+" "+seg["text"]).strip()
                    else:
                        intro=(intro+" "+seg["text"]).strip()
                    continue
            beats.extend(members)
            real=[c for c in clicks if c.get("narration") is not None]
            clicks.append(md._click(f"say-{i+1}",seg["text"][:80] or "Advance the script.",[b["id"] for b in members],
                                    "What the presenter is talking about is on screen.","presenter-explanation",
                                    "The script places a click here." if seg["cue"] else
                                    ("The script moves to a new resource here." if real else "First reveal on this slide.")))
            clicks[-1]["narration"]=seg["text"]
        if settle:
            beats.extend(settle["beats"])
            clicks.append(dict(settle["click"],narration=""))
            gaps.append({"segment":len(sec["segments"]),"kind":"settle-click-without-line",
                         "text":f"{settle['click']['purpose']} (add a closing line here, or keep it silent)"})
        used={t for b in beats for t in b["targets"]}|{(b.get("motion_parameters") or {}).get("halo") for b in beats}
        components=[c for c in components if c["id"] in used]
        placed_keys={k for lst in placed.values() for _,_,b in lst for k in _bundle_keys(b,s)[1]}
        unmentioned=[c["text"][:60] for c in cands if c["key"] not in first and c["key"] not in placed_keys]
        report[s["index"]]={"status":"scripted","clicks":len([c for c in clicks if c.get("narration") is not None]),
                            "unmentioned_static":unmentioned,"gaps":gaps,"dropped_draft_bundles":dropped}
        if not any(c.get("narration") is not None for c in clicks):
            continue
        clicks[-1]["pause_after"]="slide-complete"
        for ci,c in enumerate(clicks):
            if ci>0 and not c.get("boundary_reason"):
                c["boundary_reason"]="The script places a click here."
        slides.append({"source_index":s["index"],"role":"scripted slide",
                       "objective":f"Follow the script for slide {s['index']}.","beats":beats,"click_beats":clicks,
                       "components":components,"intro_narration":intro})
    inv=model["inventory"]
    plan={
        "version":"0.7","kind":"existing-deck-motion-director",
        "source":{"pptx_sha256":model["sha256"],"inventory_version":inv["version"],"source_slide_count":len(model["slides"])},
        "user_instruction":goal or "Follow the provided presentation script.",
        "script":{"source":"provided","summary":"Clicks follow the provided script; the director's choreography supplies how each resource moves; narration is kept per click.",
                  "evidence":["provided script","slide text alignment"],
                  "beats":[f"slide {k}: {v['status']}" for k,v in sorted(report.items())]},
        "preservation":{"preserve_text_by_default":True,"preserve_media_by_default":True,"preserve_theme_by_default":True,
                        "preserve_slide_order_by_default":True,"slide_count_policy":"preserve"},
        "slides":slides,"target_slide_count":len(model["slides"]),
        "research_metadata":{"sources":[],"style":style,"script_alignment":{str(k):v for k,v in report.items()},
                             "drafted_by":"motion_script.py: draft choreography retimed by script"},
    }
    transitions=md.detect_morph_pairs(model)
    for t in transitions:
        t.pop("continuing_ids",None)
    if transitions:
        plan["transitions"]=transitions
    return plan,report


def _beat(bid,purpose,op,targets,fx,**extra):
    effect,dur=(fx if fx else (None,None))
    return md._beat(bid,purpose,op,targets,"on-click",effect,dur,**extra)


# ---------------------------------------------------------------------------
# Script generation and output


CONNECT={"vi":("Đầu tiên,","Tiếp theo,","Cuối cùng,","Mở đầu:"),"en":("First,","Next,","Finally,","To open:")}


def script_from_plan(model,plan,lang=None):
    """A complete presenter script for a plan: existing narration is kept,
    missing narration is drafted from the content each click reveals."""
    lang=lang or language(model)
    first,nxt,last,opening=CONNECT[lang]
    by={s["index"]:s for s in model["slides"]}
    planned={s["source_index"]:s for s in plan["slides"]}
    lines=[]
    for s in model["slides"]:
        title=md._implicit_title(s) or next((o for o in s["objects"] if o["placeholder"]
                                              and o["placeholder"]["type"] in md.TITLE_TYPES),None)
        lines.append(f"## Slide {s['index']}: {(title['text'] if title else '').strip()}")
        ps=planned.get(s["index"])
        intro=(ps or {}).get("intro_narration") or (f"{opening} {title['text']}." if title and title.get("text") else "")
        if intro:
            lines.append(intro)
        if ps:
            beats={b["id"]:b for b in ps["beats"]}
            objs={}
            for o in by[s["index"]]["objects"]:
                for k in (o["name"],o["id"],o["token"]):
                    objs.setdefault(k,o)
            real=[c for c in ps["click_beats"] if beats[c["motion_beats"][0]]["timing_intent"]!="on-slide-start"]
            total=len(real)
            for ci,c in enumerate(real):
                text=c.get("narration")
                if not text:
                    said=[]
                    for mid in c["motion_beats"]:
                        b=beats[mid]
                        if b.get("layer")=="ambient":
                            continue
                        for t in b["targets"][:1 if b.get("recipe") in ("spotlight","travel","zoom-focus") else None]:
                            o=objs.get(t)
                            if not o:
                                continue
                            if b["operation"]=="text-build" and b.get("paragraphs"):
                                said+= [p["text"] for p in o["paragraphs"] if p["index"] in b["paragraphs"]]
                            elif o.get("text"):
                                said.append(o["text"].replace("\n"," "))
                            elif o["kind"] in ("chart","picture"):
                                said.append(("biểu đồ " if lang=="vi" else "the chart ")+o["name"] if o["kind"]=="chart"
                                            else ("hình " if lang=="vi" else "the picture ")+o["name"])
                    said=list(dict.fromkeys(x.strip().rstrip(".") for x in said if x))
                    lead=first if ci==0 else (last if ci==total-1 and total>2 else nxt)
                    text=f"{lead} {'; '.join(said)}." if said else f"{lead} …"
                lines.append(f"[click] {text}")
        lines.append("")
    return "\n".join(lines).strip()+"\n"


def presenter_script_md(model,plan,report=None):
    """Readable presenter script: narration + what moves at each click."""
    out=["# Presenter script",""]
    for s in plan["slides"]:
        out.append(f"## Slide {s['source_index']}")
        if s.get("intro_narration"):
            out.append(f"*Intro:* {s['intro_narration']}")
        beats={b["id"]:b for b in s["beats"]}
        for i,c in enumerate(s["click_beats"],1):
            moves=", ".join(f"{beats[m]['operation'] if beats[m]['operation']!='choreography' else beats[m]['recipe']}"
                            f"({', '.join(beats[m]['targets'][:3])}{'…' if len(beats[m]['targets'])>3 else ''})"
                            for m in c["motion_beats"])
            out.append(f"{i}. **[click]** {c.get('narration') or c['purpose']}  \n   _motion:_ {moves}")
        out.append("")
    if report:
        gaps=[(k,g) for k,v in report.items() for g in v.get("gaps",[])]
        if gaps:
            out.append("## Script gaps")
            out+= [f"- slide {k}: {g['kind']} — {g['text'][:90]}" for k,g in gaps]
    return "\n".join(out)+"\n"


# ---------------------------------------------------------------------------
# Speaker notes

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
CT="http://schemas.openxmlformats.org/package/2006/content-types"
NOTES_CT="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
RT=R


def _note_lines(plan_slide):
    lines=["[Motion script]"]
    if plan_slide.get("intro_narration"):
        lines.append(plan_slide["intro_narration"])
    for i,c in enumerate(plan_slide["click_beats"],1):
        lines.append(f"[Click {i}] {c.get('narration') or c['purpose']}")
    return lines


def write_notes(pptx_in,plan,pptx_out):
    """Append each planned slide's motion script to its speaker notes.
    Creates a notes slide from the notes master when the slide has none."""
    import os
    import tempfile
    from zipfile import ZIP_DEFLATED
    model=md.deck_model(pptx_in)
    by={s["index"]:s for s in model["slides"]}
    updates={}
    added=[]
    written=[]
    skipped=[]
    with ZipFile(pptx_in) as z:
        names=set(z.namelist())
        ct=E.fromstring(z.read("[Content_Types].xml"))
        master=next((n for n in sorted(names) if n.startswith("ppt/notesMasters/") and n.endswith(".xml")),None)
        for ps in plan["slides"]:
            if not any(c.get("narration") for c in ps["click_beats"]) and not ps.get("intro_narration"):
                continue
            part=by[ps["source_index"]]["part"]
            base,fname=part.rsplit("/",1)
            rel_part=f"{base}/_rels/{fname}.rels"
            rels=E.fromstring(updates.get(rel_part) or z.read(rel_part)) if rel_part in names else E.Element(f"{{{REL}}}Relationships")
            note=next((r for r in rels if r.get("Type","").endswith("/notesSlide")),None)
            if note is not None:
                npart="ppt/"+note.get("Target").replace("../","")
                root=E.fromstring(z.read(npart))
            else:
                if master is None:
                    skipped.append(ps["source_index"])
                    continue
                k=1
                while f"ppt/notesSlides/notesSlide{k}.xml" in names|set(added):
                    k+=1
                npart=f"ppt/notesSlides/notesSlide{k}.xml"
                root=E.fromstring(f'''<p:notes xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/><p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp><p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>''')
                nrels=E.Element(f"{{{REL}}}Relationships")
                E.SubElement(nrels,f"{{{REL}}}Relationship",Id="rId1",Type=f"{RT}/notesMaster",Target="../"+master.split("ppt/",1)[1])
                E.SubElement(nrels,f"{{{REL}}}Relationship",Id="rId2",Type=f"{RT}/slide",Target=f"../slides/{fname}")
                updates[f"ppt/notesSlides/_rels/notesSlide{k}.xml.rels"]=E.tostring(nrels,xml_declaration=True,encoding="UTF-8",standalone=True)
                rid=f"rIdNotes{k}"
                E.SubElement(rels,f"{{{REL}}}Relationship",Id=rid,Type=f"{RT}/notesSlide",Target=f"../notesSlides/notesSlide{k}.xml")
                updates[rel_part]=E.tostring(rels,xml_declaration=True,encoding="UTF-8",standalone=True)
                E.SubElement(ct,f"{{{CT}}}Override",PartName=f"/{npart}",ContentType=NOTES_CT)
                added.append(npart)
            body=next((sp.find(f"{{{P}}}txBody") for sp in root.iter(f"{{{P}}}sp")
                       if sp.find(f".//{{{P}}}ph[@type='body']") is not None),None)
            if body is None:
                continue
            for line in ([""] if body.findall(f"{{{A}}}p") else [])+_note_lines(ps):
                p=E.SubElement(body,f"{{{A}}}p")
                if line:
                    r=E.SubElement(p,f"{{{A}}}r")
                    E.SubElement(r,f"{{{A}}}rPr",lang="vi-VN",dirty="0")
                    E.SubElement(r,f"{{{A}}}t").text=line
            updates[npart]=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
            written.append(ps["source_index"])
        if added:
            updates["[Content_Types].xml"]=E.tostring(ct,xml_declaration=True,encoding="UTF-8",standalone=True)
        fd,tmp=tempfile.mkstemp(dir=Path(pptx_out).parent,suffix=".pptx")
        os.close(fd)
        with ZipFile(tmp,"w",ZIP_DEFLATED) as dst:
            for item in z.infolist():
                dst.writestr(item,updates.pop(item.filename,z.read(item.filename)))
            for name,data in updates.items():
                dst.writestr(name,data)
    os.replace(tmp,pptx_out)
    return {"notes_written":written,"notes_slides_created":added,
            "skipped_no_notes_master":skipped}


# ---------------------------------------------------------------------------
# CLI


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sp=ap.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("scaffold",help="emit an empty script.md template with guiding questions and zero prose (D004)")
    a.add_argument("-o","--output",default="script.md")
    a=sp.add_parser("check",help="check script for spine length, banned placeholders, cues, and verb alignment")
    a.add_argument("script")
    a=sp.add_parser("compile-scene",help="compile script.md to scene.json draft for T075 scene compiler")
    a.add_argument("script")
    a.add_argument("-o","--output",required=True)
    a=sp.add_parser("compile-direction",help="compile script.md to direction.json for backward compatibility")
    a.add_argument("script")
    a.add_argument("-o","--output",required=True)
    a=sp.add_parser("draft",help="write a complete presenter script (with click cues) for a deck")
    a.add_argument("deck")
    a.add_argument("-o","--output",required=True)
    a.add_argument("--style",default="modern",choices=sorted(md.STYLES))
    a.add_argument("--lang",choices=["vi","en"])
    a=sp.add_parser("plan",help="turn a script into a Director v0.7 plan (+ alignment report)")
    a.add_argument("deck")
    a.add_argument("script")
    a.add_argument("-o","--output",required=True)
    a.add_argument("--style",default="modern",choices=sorted(md.STYLES))
    a.add_argument("--fill-gaps",action="store_true",help="generate callouts for clicks the slide cannot show")
    a.add_argument("--goal",default="")
    args=ap.parse_args(argv)
    if args.cmd=="scaffold":
        Path(args.output).write_text(scaffold_script(),encoding="utf-8")
        print(f"wrote empty script template to {args.output}")
        return 0
    if args.cmd=="check":
        res=check_script(Path(args.script).read_text(encoding="utf-8"))
        if res["ok"]:
            print(f"PASS: script {args.script} OK ({res['scenes_count']} scenes, spine: {len(res['intent'].get('spine','').split())} words)")
            if res["warnings"]:
                for w in res["warnings"]:
                    print(f"  warning: {w}")
            return 0
        else:
            print(f"FAIL: script {args.script} has {len(res['errors'])} error(s):")
            for e in res["errors"]:
                print(f"  {e}")
            return 1
    if args.cmd=="compile-scene":
        scene_data=compile_to_scene(Path(args.script).read_text(encoding="utf-8"))
        Path(args.output).write_text(json.dumps(scene_data,ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"compiled {args.script} -> {args.output} ({len(scene_data['scenes'])} scenes, {len(scene_data['actors'])} persistent actors)")
        return 0
    if args.cmd=="compile-direction":
        dir_data=compile_to_direction(Path(args.script).read_text(encoding="utf-8"))
        Path(args.output).write_text(json.dumps(dir_data,ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"compiled {args.script} -> {args.output} ({len(dir_data['beats'])} beats, {len(dir_data['shots'])} shots)")
        return 0
    model=md.deck_model(args.deck)
    if args.cmd=="draft":
        plan=md.draft(model,style=args.style)
        Path(args.output).write_text(script_from_plan(model,plan,args.lang),encoding="utf-8")
        print(f"wrote {args.output}")
        return 0
    plan,report=plan_from_script(model,Path(args.script).read_text(encoding="utf-8"),args.goal,args.style,args.fill_gaps)
    errors=md.validate_director(plan,model["inventory"])
    if errors:
        raise SystemExit("script plan failed validation:\n"+"\n".join(errors))
    md._dump(plan,args.output)
    for k,v in sorted(report.items()):
        print(f"slide {k}: {v['status']}"+(f", {v['clicks']} click(s)" if "clicks" in v else "")
              +(f", gaps: {len(v['gaps'])}" if v.get("gaps") else "")
              +(f", static: {v['unmentioned_static']}" if v.get("unmentioned_static") else ""))
    print(f"wrote {args.output}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
