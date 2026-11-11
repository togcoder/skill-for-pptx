#!/usr/bin/env python3
"""100% synthetic T102 trial deck: exercises native table contrast/size, chart sizes, PUA symbols,
duplicate photos, busy photo text collisions, clamped fit whitespace reclaim, and check gates."""
import json
import sys
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

EXP = Path(__file__).resolve().parents[1]
REPO = EXP.parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pptx_tools as tools  # noqa: E402


def _assets(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    logo = out_dir / "logo.png"
    im = Image.new("RGB", (180, 60), (20, 70, 140))
    d = ImageDraw.Draw(im)
    d.rectangle((10, 10, 50, 50), fill=(245, 195, 65))
    im.save(logo)

    photo = out_dir / "widget_photo.png"
    im2 = Image.new("RGB", (480, 320), (35, 85, 145))
    d2 = ImageDraw.Draw(im2)
    d2.ellipse((80, 40, 400, 280), fill=(215, 175, 55), outline=(255, 255, 255), width=4)
    im2.save(photo)

    busy = out_dir / "busy_texture.png"
    im3 = Image.new("RGB", (520, 300), (250, 250, 250))
    d3 = ImageDraw.Draw(im3)
    for y in range(0, 300, 10):
        d3.rectangle((0, y, 520, y + 4), fill=(20, 20, 20))
    im3.save(busy)
    return logo, photo, busy


def build_decks():
    inp = EXP / "inputs" / "generated_assets"
    art = EXP / "artifacts"
    prev = EXP / "preview"
    art.mkdir(parents=True, exist_ok=True)
    prev.mkdir(parents=True, exist_ok=True)
    logo, photo, busy = _assets(inp)

    # 1. Synthetic "broken" deck (16:9 13.333 x 7.5 in) showing all T102 blind spots
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    for idx, title_text in enumerate(
        ["Line B Quality Review", "Assembly Audit Table & Notes", "Station Sensor Chart & Overlay", "Summary"], 1
    ):
        sl = prs.slides.add_slide(blank)
        bar = sl.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(9.5), Inches(0.55))
        bar.name = "Title"
        r = bar.text_frame.paragraphs[0].add_run()
        r.text, r.font.name, r.font.size = title_text, "Arial", Pt(24)
        r.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
        lg = sl.shapes.add_picture(str(logo), Inches(11.4), Inches(0.25), Inches(1.3))
        lg.name = "!!logo"

    # Slide 2 faults: unreadable table cell + tiny cell + broken PUA + draft wording + duplicate photo
    s2 = prs.slides[1]
    tframe = s2.shapes.add_table(3, 3, Inches(0.7), Inches(1.2), Inches(6.2), Inches(2.6))
    tframe.name = "AuditTable"
    tbl = tframe.table
    headers = ["Station", "Target", "Actual"]
    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x00, 0x62, 0xAC)
        run = cell.text_frame.paragraphs[0].add_run()
        run.text, run.font.name, run.font.size, run.font.color.rgb = h, "Arial", Pt(16), RGBColor(0xFF, 0xFF, 0xFF)
    rows = [("Press-01", "1200", "1185"), ("Seal-02", "4.8%", "6.1%")]
    for r_i, vals in enumerate(rows, 1):
        for c_i, val in enumerate(vals):
            cell = tbl.cell(r_i, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run = cell.text_frame.paragraphs[0].add_run()
            run.text, run.font.name = val, "Arial"
            if (r_i, c_i) == (1, 1):
                run.font.size, run.font.color.rgb = Pt(16), RGBColor(0xFF, 0xFF, 0xFF)  # white on white
            elif (r_i, c_i) == (2, 1):
                run.font.size, run.font.color.rgb = Pt(8), RGBColor(0x1D, 0x24, 0x33)   # tiny 8pt
            else:
                run.font.size, run.font.color.rgb = Pt(16), RGBColor(0x1D, 0x24, 0x33)

    pua_box = s2.shapes.add_textbox(Inches(0.7), Inches(4.1), Inches(6.2), Inches(0.6))
    pua_box.name = "BrokenArrow"
    rp = pua_box.text_frame.paragraphs[0].add_run()
    rp.text, rp.font.name, rp.font.size = "\uf0e8 Verify gasket seam torque", "Arial", Pt(18)
    rp.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)

    draft_box = s2.shapes.add_textbox(Inches(0.7), Inches(4.9), Inches(6.2), Inches(0.6))
    draft_box.name = "DraftLeak"
    rd = draft_box.text_frame.paragraphs[0].add_run()
    rd.text, rd.font.name, rd.font.size = "Charts kept from old slide [TODO: verify]", "Arial", Pt(18)
    rd.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)

    s2.shapes.add_picture(str(photo), Inches(7.3), Inches(1.2), Inches(2.6)).name = "PartA"
    s2.shapes.add_picture(str(photo), Inches(10.1), Inches(1.2), Inches(2.6)).name = "PartB"

    # Slide 3 faults: busy photo collision + small chart labels + localized micro textbox
    s3 = prs.slides[2]
    s3.shapes.add_picture(str(busy), Inches(0.7), Inches(1.3), Inches(5.6), Inches(3.2)).name = "BusyBg"
    overlay = s3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.6), Inches(1.2))
    overlay.name = "LabelOverPhoto"
    ro = overlay.text_frame.paragraphs[0].add_run()
    ro.text, ro.font.name, ro.font.size = "Inspection torque drift", "Arial", Pt(20)
    ro.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)

    micro = s3.shapes.add_textbox(Inches(0.7), Inches(4.8), Inches(5.6), Inches(0.6))
    micro.name = "MicroNote"
    rm = micro.text_frame.paragraphs[0].add_run()
    rm.text, rm.font.name, rm.font.size = "Detailed tolerance table appendix footnote", "Arial", Pt(8)
    rm.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)

    cdata = CategoryChartData()
    cdata.categories = ["Q1", "Q2", "Q3", "Q4"]
    cdata.add_series("Defects", (42, 31, 18, 9))
    ch = s3.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.7), Inches(1.3), Inches(5.9), Inches(4.2), cdata)
    ch.name = "QuarterChart"
    ch.chart.font.size = Pt(8)

    broken_path = art / "synthetic_broken.pptx"
    prs.save(broken_path)

    # 2. Clean repaired version (fix every flagged defect + reink)
    clean = Presentation(broken_path)
    cs2 = clean.slides[1]
    ctbl = next(sh.table for sh in cs2.shapes if sh.name == "AuditTable")
    for r_i in range(1, 3):
        for c_i in range(3):
            run = ctbl.cell(r_i, c_i).text_frame.paragraphs[0].runs[0]
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
    next(sh for sh in cs2.shapes if sh.name == "BrokenArrow").text_frame.paragraphs[0].runs[0].text = "→ Verify gasket seam torque"
    next(sh for sh in cs2.shapes if sh.name == "DraftLeak").text_frame.paragraphs[0].runs[0].text = "Action: Retorque jig before shift start"
    pb = next(sh for sh in cs2.shapes if sh.name == "PartB")
    pb._element.getparent().remove(pb._element)

    cs3 = clean.slides[2]
    next(sh for sh in cs3.shapes if sh.name == "LabelOverPhoto").top = Inches(0.85)
    next(sh for sh in cs3.shapes if sh.name == "BusyBg").top = Inches(1.6)
    next(sh for sh in cs3.shapes if sh.name == "MicroNote").text_frame.paragraphs[0].runs[0].font.size = Pt(14)
    cch = next(sh for sh in cs3.shapes if sh.name == "QuarterChart")
    cch.chart.font.size = Pt(14)

    clean_path = art / "synthetic_fixed.pptx"
    clean.save(clean_path)

    # 3. Also test fit overflow reclaim on clamped slide
    fit_in = art / "fit_input.pptx"
    fit_out = art / "fit_reclaimed.pptx"
    fprs = Presentation()
    fprs.slide_width, fprs.slide_height = Inches(13.333), Inches(7.5)
    fsl = fprs.slides.add_slide(fprs.slide_layouts[6])
    nbox = fsl.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(8.0), Inches(3.0))
    nbox.name = "Notes"
    nr = nbox.text_frame.paragraphs[0].add_run()
    nr.text, nr.font.size = "Clamped box reclaims nearby slack without touching neighbor", Pt(14)
    fsl.shapes.add_textbox(Inches(9.0), Inches(1.0), Inches(12.0), Inches(3.0)).name = "KPI"
    fprs.save(fit_in)
    fit_summary = tools.fit(str(fit_in), str(fit_out), (0.7, 2.0, 12.0, 4.8))

    # Run glance on broken & fixed
    rep_broken = tools.glance(str(broken_path), prev / "broken")
    rep_fixed = tools.glance(str(clean_path), prev / "fixed")
    summary = {
        "broken": [{"slide": r["slide"], "faults": r["faults"]} for r in rep_broken],
        "fixed": [{"slide": r["slide"], "faults": r["faults"]} for r in rep_fixed],
        "fit": fit_summary,
    }
    (art / "trial_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_decks()
