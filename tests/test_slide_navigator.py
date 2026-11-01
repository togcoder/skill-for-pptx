import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from lxml import etree as ET
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from scripts.slide_navigator import (
    inspect_navigation_graph,
    configure_interactive_navigation,
    compile_hub_and_spoke_deck,
    compile_mini_game_state_machine,
)


class TestSlideNavigator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_deck(self, slide_count: int = 4) -> Path:
        pptx_path = self.dir / "test_base.pptx"
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        layout = prs.slide_layouts[6]

        for i in range(slide_count):
            s = prs.slides.add_slide(layout)
            # Add a title shape
            tb = s.shapes.add_textbox(Inches(1), Inches(0.5), Inches(8), Inches(1))
            tb.text_frame.text = f"Slide {i + 1} Title"
            # Add a button
            btn = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(2), Inches(3), Inches(1))
            btn.name = f"Btn_Slide_{i + 1}"
            btn.text = f"Action {i + 1}"

        prs.save(pptx_path)
        return pptx_path

    def test_special_action_last_viewed(self):
        deck = self._create_deck(3)
        out_deck = self.dir / "out_last_viewed.pptx"

        recipe = {
            "navigation": [
                {
                    "slide": 1,
                    "shape_identifier": "Btn_Slide_2",
                    "action": "last_viewed",
                }
            ]
        }
        res = configure_interactive_navigation(deck, recipe, output_path=out_deck)
        self.assertTrue(res["ok"])
        self.assertEqual(res["applied_links_count"], 1)

        # Inspect
        graph = inspect_navigation_graph(out_deck)
        edge = graph["edges"][0]
        self.assertEqual(edge["from_slide"], 1)
        self.assertEqual(edge["type"], "last_viewed")
        self.assertEqual(edge["to_slide"], "LAST_VIEWED")

    def test_slide_jump(self):
        deck = self._create_deck(4)
        out_deck = self.dir / "out_jump.pptx"

        recipe = {
            "navigation": [
                {
                    "slide": 0,
                    "shape_identifier": "Btn_Slide_1",
                    "action": "jump_to_slide",
                    "target": 2,
                }
            ]
        }
        res = configure_interactive_navigation(deck, recipe, output_path=out_deck)
        self.assertTrue(res["ok"])

        # Inspect
        graph = inspect_navigation_graph(out_deck)
        edge = graph["edges"][0]
        self.assertEqual(edge["from_slide"], 0)
        self.assertEqual(edge["to_slide"], 2)
        self.assertEqual(edge["type"], "slide_jump")

    def test_custom_show_branch_with_return(self):
        deck = self._create_deck(5)
        out_deck = self.dir / "out_custom_show.pptx"

        recipe = {
            "custom_shows": [
                {
                    "name": "AuxiliaryDeepDive",
                    "slides": [2, 3],
                    "return_after": True,
                }
            ],
            "navigation": [
                {
                    "slide": 0,
                    "shape_identifier": "Btn_Slide_1",
                    "action": "custom_show",
                    "show_id": 0,
                    "return_after": True,
                }
            ],
        }
        res = configure_interactive_navigation(deck, recipe, output_path=out_deck)
        self.assertTrue(res["ok"])

        # Verify XML structure
        with zipfile.ZipFile(out_deck, "r") as z:
            p_xml = z.read("ppt/presentation.xml").decode("utf-8")
            self.assertIn("custShowLst", p_xml)
            self.assertIn('name="AuxiliaryDeepDive"', p_xml)

            s1_xml = z.read("ppt/slides/slide1.xml").decode("utf-8")
            self.assertIn('action="ppaction://customshow?id=0&amp;return=true"', s1_xml)

    def test_kiosk_and_advance_lock(self):
        deck = self._create_deck(3)
        out_deck = self.dir / "out_kiosk.pptx"

        recipe = {
            "kiosk_mode": True,
            "lock_advance_on_click": True,
        }
        res = configure_interactive_navigation(deck, recipe, output_path=out_deck)
        self.assertTrue(res["ok"])
        self.assertTrue(res["kiosk_mode"])

        # Verify XML
        with zipfile.ZipFile(out_deck, "r") as z:
            pp_xml = z.read("ppt/presProps.xml").decode("utf-8")
            self.assertIn("<p:kiosk", pp_xml)

            s1_xml = z.read("ppt/slides/slide1.xml").decode("utf-8")
            self.assertIn('advClick="0"', s1_xml)

    def test_hub_and_spoke_compiler(self):
        pptx_path = self.dir / "test_hub_base.pptx"
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        layout = prs.slide_layouts[6]

        # Slide 0: Hub with 2 buttons
        s0 = prs.slides.add_slide(layout)
        b1 = s0.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(2), Inches(3), Inches(1))
        b1.name = "Btn_Topic_A"
        b1.text = "Topic A"
        b2 = s0.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5), Inches(2), Inches(3), Inches(1))
        b2.name = "Btn_Topic_B"
        b2.text = "Topic B"

        # Slide 1: Topic A with return button
        s1 = prs.slides.add_slide(layout)
        r1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(5), Inches(3), Inches(1))
        r1.name = "Btn_Return_A"
        r1.text = "Return"

        # Slide 2: Topic B with return button
        s2 = prs.slides.add_slide(layout)
        r2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(5), Inches(3), Inches(1))
        r2.name = "Btn_Return_B"
        r2.text = "Return"

        prs.save(pptx_path)

        out_deck = self.dir / "out_hub_spoke.pptx"
        mappings = [
            {"hub_button": "Btn_Topic_A", "target_slide": 1, "return_button": "Btn_Return_A"},
            {"hub_button": "Btn_Topic_B", "target_slide": 2, "return_button": "Btn_Return_B"},
        ]
        res = compile_hub_and_spoke_deck(pptx_path, hub_slide_idx=0, spoke_mappings=mappings, output_path=out_deck)
        self.assertTrue(res["ok"])

        graph = inspect_navigation_graph(out_deck)
        self.assertEqual(len(graph["edges"]), 4)
        self.assertIn("graph TD", graph["mermaid"])

    def test_mini_game_state_machine(self):
        deck = self._create_deck(5)
        out_deck = self.dir / "out_game.pptx"

        # Slide 0: Start
        # Slide 1: Question 1
        # Slide 2: Wrong Answer
        # Slide 3: Question 2 (Correct)
        # Slide 4: Victory
        game_spec = {
            "start": {"slide": 0, "button": "Btn_Slide_1", "first_question": 1},
            "questions": [
                {
                    "slide": 1,
                    "correct_button": "Btn_Slide_2",
                    "correct_target": 3,
                    "wrong_buttons": ["Wrong"],
                    "wrong_target": 2,
                }
            ],
            "wrong_screens": [
                {"slide": 2, "try_again_button": "Btn_Slide_3", "quit_button": "Quit"}
            ],
            "victory_screen": {
                "slide": 4,
                "restart_button": "Btn_Slide_5",
                "end_button": "End",
            },
        }
        res = compile_mini_game_state_machine(deck, game_spec, output_path=out_deck)
        self.assertTrue(res["ok"])
        self.assertTrue(res["kiosk_mode"])

        graph = inspect_navigation_graph(out_deck)
        self.assertTrue(graph["is_non_linear"])


if __name__ == "__main__":
    unittest.main()
