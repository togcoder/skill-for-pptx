"""Evidence pass for T094: COM effect check, rechart animation survival, numbers semantics, scale guard."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_tools as tools  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.util import Inches  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

TASK = ROOT / "experiments/T094-20261108-dsh-harmonize-patchwork"
SRC = ROOT / "experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-chap-va.pptx"
FINAL = TASK / "artifacts/qcc-dong-bo-dsh.pptx"
ART = TASK / "artifacts"
OUT = []


def log(s):
    print(s)
    OUT.append(s)


# ---------------------------------------------------------------- A. rechart keeps animation targets
plan = {"transitions": {"default": "fade"}, "clicks": {"3": [["Bieu do loi"]]}}
tmp = ART / "rechart-test-motion.pptx"
tools.apply_motion(str(SRC), plan, str(tmp))
before = Presentation(str(tmp))
slide = before.slides[2]
chart_id = [sh.shape_id for sh in slide.shapes if sh.name == "Bieu do loi"][0]
timing_ids = {int(n.get("spid")) for n in slide._element.iter(qn("p:spTgt"))}
log(f"A1 animation before rechart: chart id {chart_id}, timing targets {sorted(timing_ids)}")
assert chart_id in timing_ids, "test setup: the chart should carry the click effect"

tmp2 = ART / "rechart-test-after.pptx"
info = tools.rechart(str(tmp), 3, "Bieu do loi", "line", str(tmp2), color="1F4E79", font="Century Gothic", size=14)
after = Presentation(str(tmp2))
slide = after.slides[2]
chart_ids = [sh.shape_id for sh in slide.shapes if sh.name == "Bieu do loi"]
timing_ids = {int(n.get("spid")) for n in slide._element.iter(qn("p:spTgt"))}
log(f"A2 after rechart: chart id(s) {chart_ids}, timing targets {sorted(timing_ids)}")
assert chart_ids == [chart_id], "rechart must keep the shape id"
assert chart_id in timing_ids, "rechart lost the animation target"
log("A3 PASS: rechart keeps id/name and the animation still points at the rebuilt chart")

# ---------------------------------------------------------------- B. numbers: value-set comparison caveat
with tempfile.TemporaryDirectory() as td:
    td = Path(td)

    def make(path, texts):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        s = prs.slides.add_slide(prs.slide_layouts[6])
        for i, t in enumerate(texts):
            s.shapes.add_textbox(Inches(1), Inches(1 + i), Inches(10), Inches(0.8)).text_frame.text = t
        prs.save(str(path))

    make(td / "before.pptx", ["Tỉ lệ lỗi 4,1%", "Mục tiêu 2%"])
    make(td / "lost.pptx", ["Tỉ lệ lỗi 4,1%"])
    make(td / "spurious.pptx", ["Tỉ lệ lỗi 4,1% và 2 lần phản hồi"])
    lost = tools.missing_numbers(str(td / "before.pptx"), str(td / "lost.pptx"))
    spurious = tools.missing_numbers(str(td / "before.pptx"), str(td / "spurious.pptx"))
    log(f"B1 target really lost: {lost} (correct: 2 is reported missing)")
    log(f"B2 value 2 kept only as '2 lần', the '2%' target is gone: {spurious} <- no report")
    assert lost and not spurious

log("B3 CONCLUSION: numbers is necessary, not sufficient: it compares value sets, not occurrences.")

# ---------------------------------------------------------------- C. PowerPoint opens the deck, transitions + effects resolve
try:
    import win32com.client as win32
    app = win32.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(FINAL.resolve()), True, False, False)
    try:
        log(f"C1 PowerPoint {app.Version} opened the deck: {pres.Slides.Count} slides")
        for i in range(1, pres.Slides.Count + 1):
            sl = pres.Slides(i)
            trans = sl.SlideShowTransition.EntryEffect
            seq = sl.TimeLine.MainSequence
            ids = []
            for k in range(1, seq.Count + 1):
                eff = seq.Item(k)
                ids.append(eff.Shape.Id)  # raises if the effect points at a missing shape
            if seq.Count or trans not in (0,):
                log(f"C2 slide {i}: transition {trans}, effects {seq.Count}, targets ok {len(ids)}")
        log("C3 PASS: every effect resolves to a shape")
    finally:
        pres.Close()
        app.Quit()
except ImportError:
    log("C skipped: no pywin32")

# ---------------------------------------------------------------- D. scale: what the guide's fallback protects
slide_no = 4
names = [sh.name for sh in Presentation(str(SRC)).slides[slide_no - 1].shapes if sh.name != "Title 1"]
tmp3 = ART / "scale-test.pptx"
low = tools.scale(str(SRC), slide_no, names, 0.72, str(tmp3), at=(0.55, 1.55))
log(f"D1 scale {len(names)} shapes by 0.72: smallest text becomes {low:g} pt (guide 4 minimum is 18)")
log("D2 CONCLUSION: the guide's 'rework instead of shrinking' fallback is the right call for this cluster")

(TASK / "preview" / "verification.txt").write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("wrote", TASK / "preview" / "verification.txt")
