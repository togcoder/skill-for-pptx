"""The lab layout rules (lab/standards/OUTPUTS.md) hold for the repository."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"tools"))
import check_layout  # noqa: E402


class LabLayoutTests(unittest.TestCase):
    def test_repository_layout(self):
        self.assertEqual(check_layout.problems(),[])

    def test_every_domain_has_a_card(self):
        for d in (ROOT/"domains").iterdir():
            if d.is_dir() and not d.name.startswith("_"):
                self.assertTrue((d/"DOMAIN.md").is_file(),d.name)


if __name__=="__main__":
    unittest.main()
