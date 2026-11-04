"""T083: coordination layer — registry, task IDs, single writer, collisions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"tools"))

import coord  # noqa: E402


class RegistryTests(unittest.TestCase):
    def test_every_script_has_exactly_one_owner(self):
        self.assertEqual(coord.registry_problems(ROOT),[])

    def test_unregistered_script_is_an_error(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"scripts").mkdir()
            (root/"lab").mkdir()
            (root/"scripts"/"known.py").write_text("")
            (root/"scripts"/"new_style_engine.py").write_text("")
            reg={"capabilities":[{"id":"pptx.style","title":"t","files":{"scripts/known.py":"canonical"}}]}
            (root/"lab"/"capabilities.json").write_text(json.dumps(reg))
            probs=coord.registry_problems(root)
            self.assertEqual(len(probs),1)
            self.assertIn("new_style_engine.py",probs[0])

    def test_product_module_importing_experimental_code_warns(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"scripts").mkdir()
            (root/"scripts"/"forge.py").write_text("import lab_toy\n")
            (root/"scripts"/"lab_toy.py").write_text("")
            reg={"capabilities":[{"id":"x","title":"t","files":{"scripts/forge.py":"canonical",
                                                                 "scripts/lab_toy.py":"experimental"}}]}
            self.assertEqual(coord.import_warnings(root,reg),["scripts/forge.py (canonical) imports lab_toy (experimental)"])


class TaskIdTests(unittest.TestCase):
    def test_next_free_row_is_not_a_claim(self):
        index="| T082 | [pptx] x | a | b | open | c |\n| T083 | *next free ID* | | | | |\n| T069a | y |"
        self.assertEqual(coord.ids_in_index(index),{82,69})

    def test_next_id_counts_rows_on_unmerged_branches(self):
        main={70}
        branch_rows={70,71,72,73,74,75,76,77}
        self.assertEqual(coord.next_free_id(main|branch_rows),"T078")


class SingleWriterTests(unittest.TestCase):
    reg={"lead":["claude"],"single_writer":["HANDOFF.md","docs/ROADMAP.md"]}

    def test_agent_branch_cannot_rewrite_handoff(self):
        probs=coord.single_writer_problems("work/T074-opencode-morph-rules",["HANDOFF.md","scripts/x.py"],self.reg)
        self.assertEqual(len(probs),1)
        self.assertIn("D006",probs[0])

    def test_lead_and_integration_branches_may(self):
        self.assertEqual(coord.single_writer_problems("work/T083-claude-coordination",["HANDOFF.md"],self.reg),[])
        self.assertEqual(coord.single_writer_problems("integrate/20261105",["HANDOFF.md"],self.reg),[])
        self.assertEqual(coord.single_writer_problems("work/T074-opencode-x",None,self.reg),[])


class CollisionTests(unittest.TestCase):
    def test_same_capability_or_file_collides_shared_files_do_not(self):
        owners={"scripts/theme_engine.py":[("pptx.style","experimental")],
                "scripts/brand_palette.py":[("pptx.style","canonical")]}
        branches={"a":["scripts/theme_engine.py","docs/CHANGELOG.md","research/tasks/INDEX.md"],
                  "b":["scripts/brand_palette.py","docs/CHANGELOG.md"],
                  "c":["docs/CHANGELOG.md","experiments/T090-x/REPORT.md"]}
        col=coord.collisions(branches,owners)
        self.assertEqual(col,[("a","b",[],["pptx.style"])])


if __name__=="__main__":
    unittest.main()
