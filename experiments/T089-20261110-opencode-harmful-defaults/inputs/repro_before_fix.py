"""Reproduce the T089 harmful defaults.

Run this on the code before the fix to see the failures quoted in REPORT.md
(the build raises on KPI 0, card titles print 14 pt, `!!orb` shapes appear,
the word logo is drawn, the cover gets 4 clicks, decoration causes a Morph,
and the missing font is an overflow error). On the fixed code the same script
prints the new behaviour, which is the point of the regression tests.
"""
import sys, tempfile, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import slide_forge as sf
import forge_qa
import motion_director as md
from pptx import Presentation
from pptx.util import Inches, Pt

tmp = Path(tempfile.mkdtemp(prefix="t089-"))


def sizes(path, names):
    prs = Presentation(str(path))
    out = {}
    for slide in prs.slides:
        for sh in slide.shapes:
            if sh.name in names and sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.size:
                            out.setdefault(sh.name, set()).add(r.font.size.pt)
    return out


print("== 1. KPI 0 ==")
spec = {"title": "KPI zero", "slides": [
    {"layout": "title", "title": "Bìa", "subtitle": "Phụ đề"},
    {"layout": "kpis", "title": "Kết quả", "items": [{"value": "0", "label": "ca bệnh"}]}]}
try:
    v = sf.build(spec, tmp / "kpi0.pptx")
    print("ok", v["ok"], v["errors"])
except Exception as e:
    print("RAISED", type(e).__name__, e)

print("== 2. card titles ==")
spec = {"title": "Cards", "slides": [
    {"layout": "asymmetric", "title": "Bất đối xứng",
     "major": {"heading": "Việc lớn", "text": "Nội dung lớn."},
     "minor": {"heading": "Việc nhỏ", "text": "Nội dung nhỏ."}},
    {"layout": "bento", "title": "Bento",
     "hero": {"title": "Hero", "text": "Nội dung hero."},
     "top_right": {"title": "Góc phải", "text": "Nội dung phải."},
     "bottom_right_1": {"kpi": "12", "label": "nhãn"},
     "bottom_right_2": {"kpi": "8", "label": "nhãn"}}]}
v = sf.build(spec, tmp / "cards.pptx")
print("ok", v["ok"], "warnings", [w["code"] for w in v["warnings"]])
print(sizes(tmp / "cards.pptx", {"Minor Heading", "TopRight Title", "Major Heading", "Hero Title"}))

print("== 3. orbs + morph default ==")
spec = {"title": "Plain", "slides": [
    {"layout": "statement", "title": "Một câu", "text": "Nội dung."},
    {"layout": "statement", "title": "Câu hai", "text": "Nội dung."}]}
v = sf.build(spec, tmp / "plain.pptx")
prs = Presentation(str(tmp / "plain.pptx"))
orbs = [(s, sh.name) for s, slide in enumerate(prs.slides, 1) for sh in slide.shapes if sh.name.startswith("!!")]
print("orbs", orbs, "morph_transitions", v["metrics"]["morph_transitions"])

print("== 4. logo as word ==")
spec = {"title": "Logo", "logo": "ACME", "slides": [
    {"layout": "bullets", "title": "Một", "bullets": ["a", "b"]}]}
v = sf.build(spec, tmp / "logo.pptx")
prs = Presentation(str(tmp / "logo.pptx"))
print([(sh.name, sh.has_text_frame and sh.text_frame.text) for slide in prs.slides for sh in slide.shapes if "logo" in sh.name.lower()])

print("== 5. cover clicks ==")
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
cover = prs.slides.add_slide(blank)
texts = [("KICKER", 0.8, 1.4), ("Tên bài giảng", 0.8, 1.8), ("Phụ đề bài giảng", 0.8, 2.6),
         ("Người trình bày", 0.8, 3.2), ("2026", 0.8, 3.6)]
for t, x, y in texts:
    box = cover.shapes.add_textbox(Inches(x), Inches(y), Inches(6), Inches(0.5))
    box.text_frame.text = t
bar = cover.shapes.add_shape(1, Inches(0.8), Inches(4.2), Inches(4), Inches(0.05))
body = prs.slides.add_slide(blank)
b = body.shapes.add_textbox(Inches(0.8), Inches(1), Inches(8), Inches(3))
b.text_frame.text = "Nội dung chính của bài."
prs.save(tmp / "cover.pptx")
model = md.deck_model(tmp / "cover.pptx")
plan = md.draft(model, style="modern", morph=False)
for s in plan["slides"]:
    print("slide", s["source_index"], "clicks", len(s["click_beats"]),
          [c["motion_beats"][0] for c in s["click_beats"]])

print("== 6. morph reason ==")
def obj(i, name, text, x):
    return {"id": i, "name": name, "kind": "shape", "text": text, "image": None,
            "geometry": {"x": x, "y": 0.1, "w": 0.2, "h": 0.2}, "placeholder": None}

orb_model = {"slides": [
    {"index": 1, "has_transition": False, "objects": [obj("1", "!!orb-1", None, 0.1), obj("2", "Title", "A", 0.4)]},
    {"index": 2, "has_transition": False, "objects": [obj("1", "!!orb-1", None, 0.7), obj("3", "Title", "B", 0.4)]}]}
print("orb-only morphs", md.detect_morph_pairs(orb_model))
content_model = {"slides": [
    {"index": 1, "has_transition": False, "objects": [obj("1", "Portrait", "A", 0.1)]},
    {"index": 2, "has_transition": False, "objects": [obj("1", "Portrait", "A", 0.7)]}]}
print("content morphs", md.detect_morph_pairs(content_model))

print("== 7. missing font ==")
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])
box = s.shapes.add_textbox(Inches(1), Inches(1), Inches(2.0), Inches(0.5))
tf = box.text_frame
tf.word_wrap = True
run = tf.paragraphs[0].add_run()
run.text = "A sentence that is far too long for this narrow box"
run.font.name = "NoSuchFontXYZ"
run.font.size = Pt(24)
prs.save(tmp / "font.pptx")
v = forge_qa.qa(tmp / "font.pptx")
print("errors", [(e["code"], e["object"]) for e in v["errors"]])
print("warnings", [(w["code"], w["object"]) for w in v["warnings"]])
print("tmp", tmp)
