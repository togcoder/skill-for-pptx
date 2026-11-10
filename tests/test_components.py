"""T098: taking reusable parts out of a finished deck (groups, vectors, pictures, whole frames)."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree as E
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_tools as tools  # noqa: E402


def _slide_deck(path):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    return prs, prs.slides.add_slide(prs.slide_layouts[6])


def _rect(slide, x, y, w, h, name, colour="C8442E"):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(colour)
    sh.name = name
    return sh


def _grouped(prs, path, scale=2.0):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    a = _rect(slide, 1, 1, 1, 1, "Rect A", "FF0000")
    b = _rect(slide, 4, 1, 2, 1, "Rect B", "00FF00")
    _rect(slide, 8, 1, 1, 1, "Rect C", "0000FF")
    grp = slide.shapes.add_group_shape([a, b])
    grp.name = "Fish frame"
    xfrm = grp._element.find("p:grpSpPr/a:xfrm", tools.NS)
    ext = xfrm.find(qn("a:ext"))
    ext.set("cx", str(int(int(ext.get("cx")) * scale)))
    ext.set("cy", str(int(int(ext.get("cy")) * scale)))
    prs.save(path)
    return slide, grp


class UngroupTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_scaled_group_becomes_correctly_placed_shapes(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        a = _rect(slide, 1, 1, 1, 1, "Rect A")
        b = _rect(slide, 4, 1, 2, 1, "Rect B")
        grp = slide.shapes.add_group_shape([a, b])
        grp.name = "Fish frame"
        xfrm = grp._element.find("p:grpSpPr/a:xfrm", tools.NS)
        ext = xfrm.find(qn("a:ext"))
        ext.set("cx", str(int(int(ext.get("cx")) * 2)))
        ext.set("cy", str(int(int(ext.get("cy")) * 2)))
        src, out = self.dir / "src.pptx", self.dir / "out.pptx"
        prs.save(src)
        tools.ungroup(str(src), 1, ["Fish frame"], str(out))
        shapes = {sh.name: sh for sh in Presentation(str(out)).slides[0].shapes}
        self.assertEqual(set(shapes), {"Rect A", "Rect B"})
        self.assertAlmostEqual(shapes["Rect A"].left / 914400, 1.0, places=2)
        self.assertAlmostEqual(shapes["Rect A"].width / 914400, 2.0, places=2)
        self.assertAlmostEqual(shapes["Rect B"].left / 914400, 7.0, places=2)
        self.assertAlmostEqual(shapes["Rect B"].width / 914400, 4.0, places=2)

    def test_animated_group_is_refused_without_force(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        a = _rect(slide, 1, 1, 1, 1, "Rect A")
        b = _rect(slide, 3, 1, 1, 1, "Rect B")
        grp = slide.shapes.add_group_shape([a, b])
        grp.name = "Animated group"
        root = slide._element
        timing = E.SubElement(root, qn("p:timing"))
        seq = E.SubElement(timing, qn("p:timing"))
        spTgt = E.SubElement(seq, qn("p:spTgt"))
        # the id must match the group's cNvPr id for the guard to fire
        spTgt.set("spid", str(grp.shape_id))
        src, out = self.dir / "anim.pptx", self.dir / "anim-out.pptx"
        prs.save(src)
        with self.assertRaises(ValueError):
            tools.ungroup(str(src), 1, ["Animated group"], str(out))
        tools.ungroup(str(src), 1, ["Animated group"], str(out), force=True)
        self.assertTrue(out.exists())


class ComponentTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.png = self.dir / "pic.png"
        Image.new("RGB", (300, 200), (30, 120, 200)).save(self.png)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)

    def _deck(self, with_bg=True, chart=False):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        if with_bg:
            bg = slide.shapes.add_picture(str(self.png), 0, 0, prs.slide_width, prs.slide_height)
            bg.name = "!!bg"
        _rect(slide, 1, 1, 1, 1, "Frame")
        pic = slide.shapes.add_picture(str(self.png), Inches(3), Inches(1), Inches(2), Inches(1.3))
        pic.name = "Crop pic"
        pic.crop_left, pic.crop_right = 0.1, 0.05
        if chart:
            from pptx.chart.data import CategoryChartData
            from pptx.enum.chart import XL_CHART_TYPE
            data = CategoryChartData()
            data.categories = ["A", "B"]
            data.add_series("S", (1, 2))
            frame = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(5), Inches(4),
                                           Inches(4), Inches(2), data)
            frame.name = "Chart"
        path = self.dir / "deck.pptx"
        prs.save(path)
        return path

    def test_component_drops_background_trims_and_writes_manifest(self):
        src = self._deck()
        out = self.dir / "frame.pptx"
        manifest = self.dir / "frame.json"
        summary = tools.component(str(src), 1, str(out), freeze=True, margin=24,
                                  manifest=str(manifest), png=None)
        self.assertIn("2 shape", summary)
        prs = Presentation(str(out))
        names = [sh.name for sh in prs.slides[0].shapes]
        self.assertEqual(names, ["Frame", "Crop pic"])
        self.assertNotIn("!!bg", names)
        self.assertTrue(manifest.exists())
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(meta["dropped"], ["!!bg"])
        self.assertTrue(meta["frozen_theme"])
        # picture crop survives; text and shape are still editable
        pic = [sh for sh in prs.slides[0].shapes if sh.name == "Crop pic"][0]
        self.assertAlmostEqual(pic.crop_left, 0.1, places=2)
        self.assertLess(prs.slide_width, Inches(13.333))

    def test_component_rejects_a_chart(self):
        src = self._deck(with_bg=False, chart=True)
        with self.assertRaises(ValueError) as ctx:
            tools.component(str(src), 1, str(self.dir / "x.pptx"), names=["Chart"])
        self.assertIn("rechart", str(ctx.exception))

    def test_component_freeze_bakes_theme_colour(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # change the deck's accent1 to red
        from pptx.opc.constants import RELATIONSHIP_TYPE as RT
        tp = prs.slide_master.part.part_related_by(RT.THEME)
        root = E.fromstring(tp.blob)
        scheme = root.find(".//" + qn("a:clrScheme"))
        accent = scheme.find(qn("a:accent1"))
        for child in list(accent):
            accent.remove(child)
        E.SubElement(accent, qn("a:srgbClr")).set("val", "FF0000")
        tp._blob = E.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
        sh.name = "Themed"
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string("00FF00")
        solid = sh._element.spPr.find(qn("a:solidFill"))
        for child in list(solid):
            solid.remove(child)
        E.SubElement(solid, qn("a:schemeClr")).set("val", "accent1")
        src, out = self.dir / "theme.pptx", self.dir / "theme-component.pptx"
        prs.save(src)
        tools.component(str(src), 1, str(out), names=["Themed"], freeze=True)
        with zipfile.ZipFile(out) as z:
            xml = z.read("ppt/slides/slide1.xml").decode("utf-8")
        self.assertIn("FF0000", xml)
        self.assertNotIn("schemeClr", xml)


    def test_thin_component_gets_a_legal_page(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        _rect(slide, 1, 1, 9, 0.42, "Bar")
        prs.save(self.dir / "bar.pptx")
        out = self.dir / "bar-component.pptx"
        tools.component(str(self.dir / "bar.pptx"), 1, str(out), names=["Bar"], margin=10)
        prs2 = Presentation(str(out))
        self.assertGreaterEqual(prs2.slide_height, 914400)
        self.assertGreater(prs2.slide_width, prs2.slide_height)

    def test_component_can_exclude_chrome(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.shapes.add_picture(str(self.png), 0, 0, prs.slide_width, prs.slide_height)
        bg.name = "!!bg"
        _rect(slide, 1, 1, 1, 1, "Frame")
        t = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1))
        t.name = "Title"
        prs.save(self.dir / "chrome.pptx")
        out = self.dir / "chrome-component.pptx"
        tools.component(str(self.dir / "chrome.pptx"), 1, str(out), exclude_chrome=True)
        names = [sh.name for sh in Presentation(str(out)).slides[0].shapes]
        self.assertEqual(names, ["Frame"])

    def test_place_puts_component_back(self):
        src = self._deck()
        comp = self.dir / "comp.pptx"
        tools.component(str(src), 1, str(comp), freeze=True)
        target = self.dir / "target.pptx"
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        prs.slides.add_slide(prs.slide_layouts[6])
        prs.save(target)
        placed = self.dir / "placed.pptx"
        tools.place(str(comp), str(target), 1, str(placed), at=(1, 2))
        prs = Presentation(str(placed))
        names = [sh.name for sh in prs.slides[0].shapes]
        self.assertIn("Frame", names)
        self.assertIn("Crop pic", names)

    def test_components_lists_group_and_background(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.shapes.add_picture(str(self.png), 0, 0, prs.slide_width, prs.slide_height)
        bg.name = "!!bg"
        a = _rect(slide, 1, 1, 1, 1, "A")
        b = _rect(slide, 3, 1, 1, 1, "B")
        slide.shapes.add_group_shape([a, b]).name = "Frame"
        path = self.dir / "inv.pptx"
        prs.save(path)
        text = tools.components(str(path), 1)
        self.assertIn("group of 2", text)
        self.assertIn("background", text)
        self.assertIn("chrome", text)


if __name__ == "__main__":
    unittest.main()
