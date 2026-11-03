"""T056 tests: the iso-vector-craft skill contract.

These tests do not need Node or VectorCraft. They check the shipped SVGs and
the skill's provenance/portability guarantees, so a bad export fails in CI
before anyone opens PowerPoint or an editor.
"""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/iso-vector-craft"
ART = ROOT / "experiments/T056-20261103-opencode-iso-vector/artifacts"

SVG_NS = "{http://www.w3.org/2000/svg}"

ARTIFACTS = {
    "technics-sl1200.svg": {
        "viewbox": "0 0 980 900",
        "paths": (500, 540),
        "parts": 12,
    },
    "gale-speaker-front.svg": {
        "viewbox": "0 0 820 900",
        "paths": (70, 90),
        "parts": 0,
    },
    "gale-speaker-rear.svg": {
        "viewbox": "0 0 820 900",
        "paths": (100, 125),
        "parts": 0,
    },
    "rolleiflex-tlr.svg": {
        "viewbox": "0 0 820 900",
        "paths": (200, 230),
        "parts": 0,
    },
}

TECHNICS_PARTS = {
    "halo",
    "feet",
    "plinth",
    "platter",
    "record",
    "tonearm-mount",
    "tonearm",
    "headshell",
    "arm-rest",
    "controls",
    "target-light",
    "marks",
}


def _text(name: str) -> str:
    return (ART / name).read_text(encoding="utf-8")


class KitProvenanceTests(unittest.TestCase):
    def test_vendored_files_exist(self):
        for name in ("iso-kit.mjs", "tube.mjs", "lathe.mjs", "iso.css", "LICENSE"):
            self.assertTrue((SKILL / "kit" / name).is_file(), name)

    def test_mit_license_and_attribution(self):
        license_text = (SKILL / "kit" / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 Ryan", license_text)
        attribution = (SKILL / "kit" / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("wheresryan22/anatomy", attribution)
        self.assertIn("1482e8469b0a9e0d8cc18ea2740a01423d29ae80", attribution)
        self.assertIn("MIT", attribution)

    def test_examples_use_the_vendored_kit(self):
        builds = list((SKILL / "examples").rglob("*.mjs"))
        self.assertGreaterEqual(len(builds), 3)
        for build in builds:
            text = build.read_text(encoding="utf-8")
            self.assertNotIn("anatomy-ref", text, build)
            self.assertIn("../../kit/", text, build)
            self.assertIn("writeFileSync", text, build)

    def test_no_reference_photos_are_redistributed(self):
        media = [
            p
            for p in SKILL.rglob("*")
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
        ]
        self.assertEqual(media, [])

    def test_skill_has_frontmatter_and_limits(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: iso-vector-craft\n"))
        for heading in (
            "## The one idea",
            "## When to use it",
            "## Workflow",
            "## Kit API",
            "## Failure modes",
            "## Checklist",
            "## Attribution",
        ):
            self.assertIn(heading, text)
        self.assertIn("EXPERIMENTAL", text)
        self.assertIn("1482e84", text)


class SvgContractTests(unittest.TestCase):
    def test_artifacts_exist(self):
        for name in ARTIFACTS:
            self.assertTrue((ART / name).is_file(), name)

    def test_svg_is_well_formed_and_labelled(self):
        for name, spec in ARTIFACTS.items():
            with self.subTest(name=name):
                root = ET.fromstring(_text(name))
                self.assertEqual(root.tag, SVG_NS + "svg")
                self.assertEqual(root.get("viewBox"), spec["viewbox"])
                self.assertEqual(root.get("role"), "img")
                self.assertTrue(root.get("aria-label"))
                self.assertIsNotNone(root.find(SVG_NS + "title"))
                self.assertIsNotNone(root.find(SVG_NS + "desc"))

    def test_no_raster_or_external_references(self):
        for name in ARTIFACTS:
            with self.subTest(name=name):
                text = _text(name)
                self.assertNotIn("<image", text)
                self.assertNotIn("<foreignObject", text)
                self.assertNotIn("data:image", text)
                self.assertNotIn("xlink:href", text)
                self.assertNotRegex(text, r'(?:href|src)\s*=\s*["\']https?://')

    def test_palette_is_baked_and_fonts_are_named(self):
        for name in ARTIFACTS:
            with self.subTest(name=name):
                text = _text(name)
                self.assertNotIn("var(--anatomy", text)
                self.assertNotIn('font-family="#000"', text)
                self.assertNotIn("font-family:var(", text.split("</style>")[-1])

    def test_path_counts_and_part_groups(self):
        for name, spec in ARTIFACTS.items():
            with self.subTest(name=name):
                text = _text(name)
                count = text.count("<path")
                low, high = spec["paths"]
                self.assertGreaterEqual(count, low)
                self.assertLessEqual(count, high)
                groups = re.findall(r'<g data-part="([^"]+)"', text)
                self.assertEqual(len(groups), spec["parts"])
                if spec["parts"]:
                    self.assertEqual(set(groups), TECHNICS_PARTS)

    def test_every_solid_is_its_own_group(self):
        minimums = {
            "technics-sl1200.svg": 40,
            "gale-speaker-front.svg": 5,
            "gale-speaker-rear.svg": 8,
            "rolleiflex-tlr.svg": 20,
        }
        for name, minimum in minimums.items():
            with self.subTest(name=name):
                text = _text(name)
                solids = text.count('<g class="iso-solid')
                self.assertGreaterEqual(solids, minimum)

    def test_technics_has_materials_and_geometry(self):
        text = _text("technics-sl1200.svg")
        for material in ("qm-silver", "qm-dark", "qm-record", "qm-label"):
            self.assertIn(material, text)
        self.assertIn(".iso-face-text{font-family:Arial", text)
        self.assertGreaterEqual(text.count('data-shade="0"'), 30)
        self.assertIn('data-theme="light"', text)

    def test_every_path_has_geometry(self):
        for name in ARTIFACTS:
            with self.subTest(name=name):
                text = _text(name)
                empty = re.findall(r'<path[^>]*\sd=""', text)
                self.assertEqual(empty, [])
                self.assertGreaterEqual(len(re.findall(r'<path[^>]*\sd="[MmLlHhVvCcSsQqTtAa]', text)), 1)


if __name__ == "__main__":
    unittest.main()
