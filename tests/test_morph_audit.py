import unittest
from pathlib import Path

from scripts.morph_studio import Package, audit_morph_pairs

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "experiments/T074-20261105-opencode-morph-rules/artifacts/morph-matrix.pptx"
T069A = ROOT / "experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx"


class MorphAuditTests(unittest.TestCase):
    def test_matrix_catches_type_entrance_and_offslide(self):
        report = audit_morph_pairs(Package(str(MATRIX)))
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("MORPH-TYPE-MISMATCH", codes)
        self.assertIn("MORPH-ENTRANCE", codes)
        self.assertIn("MORPH-OFFSLIDE", codes)
        self.assertEqual(len(report["errors"]), 3)

    def test_t069a_has_no_structural_morph_error(self):
        report = audit_morph_pairs(Package(str(T069A)))
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
