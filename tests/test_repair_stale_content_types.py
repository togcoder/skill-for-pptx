import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from repair_stale_content_types import repair_stale_content_type_overrides


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
</Types>"""


class RepairStaleContentTypesTests(unittest.TestCase):
    def test_removes_only_missing_override_and_preserves_other_members(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "source.pptx"
            output = td / "output.pptx"
            payload = b"presentation-bytes-must-not-change"
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("[Content_Types].xml", CONTENT_TYPES)
                z.writestr("ppt/presentation.xml", payload)

            source_bytes = source.read_bytes()
            receipt = repair_stale_content_type_overrides(source, output)

            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(receipt["removed_override_count"], 1)
            self.assertEqual(
                receipt["removed_part_names"],
                ["/ppt/slideMasters/slideMaster2.xml"],
            )
            with zipfile.ZipFile(output) as z:
                self.assertEqual(z.read("ppt/presentation.xml"), payload)
                root = ET.fromstring(z.read("[Content_Types].xml"))
                part_names = [x.attrib.get("PartName") for x in root]
            self.assertIn("/ppt/presentation.xml", part_names)
            self.assertNotIn("/ppt/slideMasters/slideMaster2.xml", part_names)

    def test_refuses_in_place_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "source.pptx"
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("[Content_Types].xml", CONTENT_TYPES)
                z.writestr("ppt/presentation.xml", b"x")
            with self.assertRaisesRegex(ValueError, "differ from source"):
                repair_stale_content_type_overrides(source, source)


if __name__ == "__main__":
    unittest.main()
