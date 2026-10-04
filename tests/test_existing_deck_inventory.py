import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspect_existing_deck import inspect_existing_deck

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


class ExistingDeckInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=inspect_existing_deck(SOURCE)

    def test_h001_inventory_reads_source_without_errors(self):
        self.assertEqual(self.report["errors"],[])
        self.assertEqual(self.report["source_sha256"],hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(len(self.report["slides"]),2)
        self.assertEqual([s["index"] for s in self.report["slides"]],[1,2])

    def test_inventory_preserves_semantic_names_and_order(self):
        for slide in self.report["slides"]:
            self.assertEqual(slide["shape_count"],12)
            forced=[s["forced_semantic_name"] for s in slide["shapes"] if s["forced_semantic_name"]]
            self.assertEqual(len(forced),12)
            self.assertEqual(len(forced),len(set(forced)))
            self.assertEqual([s["z_index"] for s in slide["shapes"]],list(range(1,13)))

    def test_geometry_is_normalized(self):
        for slide in self.report["slides"]:
            for shape in slide["shapes"]:
                geom=shape["geometry"]
                self.assertIsNotNone(geom)
                self.assertGreater(geom["w"],0)
                self.assertGreater(geom["h"],0)

    def test_existing_motion_is_detected(self):
        self.assertFalse(self.report["slides"][0]["has_transition"])
        self.assertTrue(self.report["slides"][1]["has_transition"])

    def test_speaker_notes_are_detected_when_present(self):
        rel_ns="http://schemas.openxmlformats.org/package/2006/relationships"
        p_ns="http://schemas.openxmlformats.org/presentationml/2006/main"
        a_ns="http://schemas.openxmlformats.org/drawingml/2006/main"
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"with-notes.pptx"
            notes=(
                f'<p:notes xmlns:p="{p_ns}" xmlns:a="{a_ns}">'
                '<p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/>'
                '<p:cNvSpPr/><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr>'
                '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>'
                'Explain the process, then focus on Inspect.'
                '</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:notes>'
            ).encode()
            rel_part="ppt/slides/_rels/slide1.xml.rels"
            with ZipFile(SOURCE) as src, ZipFile(target,"w") as dst:
                for item in src.infolist():
                    data=src.read(item.filename)
                    if item.filename==rel_part:
                        root=ET.fromstring(data)
                        ET.SubElement(root,f"{{{rel_ns}}}Relationship",{
                            "Id":"rIdNotesTest",
                            "Type":"http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide",
                            "Target":"../notesSlides/notesSlide99.xml",
                        })
                        data=ET.tostring(root,encoding="utf-8",xml_declaration=True)
                    dst.writestr(item,data)
                dst.writestr("ppt/notesSlides/notesSlide99.xml",notes)
            report=inspect_existing_deck(target)
            self.assertEqual(report["errors"],[])
            self.assertEqual(report["slides"][0]["speaker_notes"],
                             "Explain the process, then focus on Inspect.")

    def test_package_capabilities_are_exposed(self):
        self.assertTrue(self.report["package"]["has_theme"])
        self.assertTrue(self.report["slide_size_emu"]["width"]>0)
        self.assertTrue(self.report["slide_size_emu"]["height"]>0)


if __name__=="__main__":
    unittest.main()
