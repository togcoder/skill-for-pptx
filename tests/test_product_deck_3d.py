"""T055 tests: a PowerPoint-native 3D product deck, not a rendered picture.

These are package-contract tests: they need no PowerPoint session. The native
reopen evidence lives in preview/native-audit-v3.json and is checked when that
artefact is present.
"""
from __future__ import annotations

import hashlib
import json
import struct
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "T055-20261103-opencode-pptx-3d"
PPTX = EXP / "artifacts" / "quickmill_native_product_tour_v3.pptx"
GLB = EXP / "artifacts" / "quickmill-blockout.glb"
MANIFEST = EXP / "preview" / "tour-v3-manifest.json"
GLB_MANIFEST = EXP / "preview" / "glb-manifest.json"
AUDIT = EXP / "preview" / "native-audit-v3.json"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
AM3D = "http://schemas.microsoft.com/office/drawing/2017/model3d"


def read_glb(raw: bytes) -> dict:
    magic, version, length = struct.unpack("<III", raw[:12])
    if magic != 0x46546C67 or version != 2 or length != len(raw):
        raise AssertionError("not a glTF 2.0 GLB")
    json_len, json_type = struct.unpack("<II", raw[12:20])
    if json_type != 0x4E4F534A:
        raise AssertionError("missing JSON chunk")
    return json.loads(raw[20:20 + json_len])


class ProductDeck3DTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PPTX.exists():
            raise unittest.SkipTest(f"missing {PPTX}")
        cls.zip = zipfile.ZipFile(PPTX)
        cls.names = set(cls.zip.namelist())
        cls.slides = [f"ppt/slides/slide{i}.xml" for i in (1, 2, 3)]
        cls.roots = [ET.fromstring(cls.zip.read(s)) for s in cls.slides]
        cls.glb_names = sorted(n for n in cls.names
                               if n.startswith("ppt/media/model3d") and n.endswith(".glb"))
        cls.glb_raw = [cls.zip.read(n) for n in cls.glb_names]
        cls.gltf = [read_glb(raw) for raw in cls.glb_raw]

    @classmethod
    def tearDownClass(cls):
        cls.zip.close()

    def test_deck_is_three_widescreen_slides(self):
        pres = ET.fromstring(self.zip.read("ppt/presentation.xml"))
        size = pres.find(f"{{{P}}}sldSz")
        self.assertEqual(int(size.get("cx")), 960 * 12700)
        self.assertEqual(int(size.get("cy")), 540 * 12700)
        self.assertEqual(len(self.roots), 3)

    def test_each_slide_has_exactly_one_native_3d_model(self):
        for i, root in enumerate(self.roots, start=1):
            models = root.findall(f".//{{{AM3D}}}model3d")
            self.assertEqual(len(models), 1, f"slide {i}")
            self.assertTrue(models[0].get(f"{{{R}}}embed"))
            frame = root.find(f".//{{{P}}}graphicFrame")
            self.assertIsNotNone(frame, f"slide {i}: no graphicFrame")
            ext = frame.find(f"{{{P}}}xfrm/{{{A}}}ext")
            self.assertEqual(int(ext.get("cx")), 500 * 12700)
            self.assertEqual(int(ext.get("cy")), 490 * 12700)

    def test_each_slide_relationships_point_at_a_model_glb(self):
        for i in range(1, 4):
            rels = ET.fromstring(
                self.zip.read(f"ppt/slides/_rels/slide{i}.xml.rels"))
            model_rels = [r for r in rels.findall(f"{{{REL}}}Relationship")
                          if r.get("Type", "").endswith("/model3d")]
            self.assertEqual(len(model_rels), 1, f"slide {i}")
            target = model_rels[0].get("Target").replace("../", "ppt/")
            self.assertIn(target, self.names)
            self.assertTrue(target.startswith("ppt/media/model3d"))

    def test_three_embedded_glbs_are_identical_and_valid(self):
        self.assertEqual(len(self.glb_names), 3)

        def fingerprint(gltf):
            payload = {
                "materials": sorted(
                    [[m.get("name"),
                      m.get("pbrMetallicRoughness", {}).get("baseColorFactor")]
                     for m in gltf["materials"]],
                    key=lambda row: str(row[0])),
                "meshes": sorted(m.get("name") for m in gltf["meshes"]),
                "nodes": sorted(str(n.get("name")) for n in gltf["nodes"]),
            }
            return hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

        fingerprints = {fingerprint(gltf) for gltf in self.gltf}
        self.assertEqual(len(fingerprints), 1)
        for raw, gltf in zip(self.glb_raw, self.gltf):
            self.assertEqual(gltf["asset"]["version"], "2.0")
            self.assertGreaterEqual(len(gltf["meshes"]), 30)
            self.assertGreaterEqual(len(gltf["materials"]), 30)
            self.assertNotIn("images", gltf)
            self.assertNotIn("textures", gltf)
            self.assertTrue(all(
                m.get("pbrMetallicRoughness", {}).get("metallicFactor", 1.0) == 0.0
                for m in gltf["materials"]))

    def test_glb_is_y_up_metres_and_the_product_size(self):
        mins = [1e9, 1e9, 1e9]
        maxs = [-1e9, -1e9, -1e9]
        for gltf in self.gltf:
            for mesh in gltf["meshes"]:
                for prim in mesh["primitives"]:
                    acc = gltf["accessors"][prim["attributes"]["POSITION"]]
                    for k in range(3):
                        mins[k] = min(mins[k], acc["min"][k])
                        maxs[k] = max(maxs[k], acc["max"][k])
        self.assertAlmostEqual(maxs[1] - mins[1], 0.553, delta=0.002)  # height
        self.assertAlmostEqual(maxs[0] - mins[0], 0.400, delta=0.002)  # width
        self.assertAlmostEqual(maxs[2] - mins[2], 0.326, delta=0.004)  # depth
        self.assertAlmostEqual(mins[1], 0.0, delta=0.001)              # on the floor

    def test_colour_regions_are_separate_materials(self):
        regions = {r["name"]: r for r in
                   json.loads(GLB_MANIFEST.read_text(encoding="utf-8"))["regions"]}
        for name in ("lower_body_yellow", "upper_core_bay", "chrome_top",
                     "tower_trim", "tray_grate"):
            self.assertIn(name, regions)
            self.assertEqual(regions[name]["metallic"], 0.0)
        self.assertEqual(regions["lower_body_yellow"]["color"], "#E0AE2E")
        self.assertEqual(regions["chrome_top"]["color"], "#D5D2C8")

    def test_callouts_are_editable_powerpoint_text(self):
        texts = []
        for root in self.roots:
            texts.extend((t.text or "") for t in root.findall(f".//{{{A}}}t"))
        joined = "\n".join(texts)
        for expected in ("TOP HOUSING", "GROUP HEAD", "SWITCH PLATE",
                         "HEIGHT", "553 mm", "WIDTH", "400 mm",
                         "ROTATE IN POWERPOINT", "NATIVE 3D"):
            self.assertIn(expected, joined)

    def test_focus_boxes_are_native_shapes(self):
        for i, root in enumerate(self.roots, start=1):
            sp = root.findall(f".//{{{P}}}sp")
            cxn = root.findall(f".//{{{P}}}cxnSp")
            frames = root.findall(f".//{{{P}}}graphicFrame")
            self.assertGreaterEqual(len(sp), 18, f"slide {i}")
            self.assertGreaterEqual(len(cxn), 10, f"slide {i}")
            self.assertEqual(len(frames), 1, f"slide {i}")
            self.assertGreaterEqual(len(sp) + len(cxn) + len(frames), 30,
                                    f"slide {i}")
            texts = [(t.text or "") for t in root.findall(f".//{{{A}}}t")]
            self.assertIn(f"{i:02d}", texts)

    def test_manifest_cameras_match_the_pptx(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["views"]), 3)
        for view in manifest["views"]:
            self.assertEqual(view["type"], 30)
            self.assertEqual(view["shape"], "Product3D")
            self.assertAlmostEqual(view["camera"][0], -0.85, delta=0.01)
            self.assertAlmostEqual(view["camera"][2], 2.10, delta=0.01)
            self.assertAlmostEqual(view["look_at"][1], 0.28, delta=0.01)
            self.assertEqual(view["rotation"], [6.0, 0.0, 0.0])
            self.assertEqual(view["fov"], 40.0)

    def test_native_audit_evidence_if_present(self):
        if not AUDIT.exists():
            self.skipTest("native audit not generated")
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["slide_count"], 3)
        self.assertEqual(len(audit["package"]["model_glb"]), 3)
        for slide in audit["slides"]:
            self.assertEqual(len(slide["models"]), 1)
            self.assertEqual(slide["models"][0]["type"], 30)
        for glb in audit["glb"]:
            self.assertEqual(glb["metallic"], [0.0])
            self.assertGreater(glb["bytes"], 10_000)
        pdf = EXP / "preview" / "quickmill_native_product_tour_v3.pdf"
        self.assertTrue(pdf.exists())
        self.assertGreater(pdf.stat().st_size, 100_000)


if __name__ == "__main__":
    unittest.main()
