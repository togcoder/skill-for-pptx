"""Unit tests for Advanced Presentation Interactivity Engine (T049).

Antigravity multi-domain design research lab.
Verifies:
1. Pure-Python synthetic audio generation (WAV PCM 16-bit).
2. Package media embedding and [Content_Types].xml / slide rels registration.
3. DrawingML <a:snd> audio attachment to click and hover actions.
4. In-Slide Lightbox Modal interactive timing compilation.
5. In-Slide Multi-Tab Switcher interactive timing compilation.
6. Morph transition configuration.
7. End-to-end showcase compilation and inspection audit.
"""

import io
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path
from lxml import etree as ET

from scripts.advanced_interactivity import (
    synthesize_ui_sound,
    embed_package_sound,
    attach_click_sound_and_action,
    attach_hover_sound_and_action,
    build_in_slide_modal_click_groups,
    build_tab_switcher_click_groups,
    configure_slide_morph_transition,
    inspect_interactivity,
    compile_advanced_interactive_showcase,
    NAMESPACES,
    NS_P,
    NS_A,
    NS_P14,
)


class TestAdvancedInteractivity(unittest.TestCase):
    """Test suite for T049 advanced interactivity engine."""

    def test_audio_synthesis_wav_format(self):
        """Verify that all synthesized sound types produce valid 16-bit mono WAV streams."""
        for sound_type in ("click", "chime", "buzz", "tap"):
            wav_bytes = synthesize_ui_sound(sound_type)
            self.assertGreater(len(wav_bytes), 100)
            with wave.open(io.BytesIO(wav_bytes), "rb") as w:
                self.assertEqual(w.getnchannels(), 1)
                self.assertEqual(w.getsampwidth(), 2)  # 16-bit
                self.assertEqual(w.getframerate(), 44100)
                self.assertGreater(w.getnframes(), 0)

    def test_embed_package_sound(self):
        """Verify media injection, Content_Types update, and slide relationship generation."""
        files = {
            "[Content_Types].xml": (
                b'<?xml version="1.0" encoding="utf-8"?>\n'
                b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
            ),
            "ppt/slides/_rels/slide1.xml.rels": (
                b'<?xml version="1.0" encoding="utf-8"?>\n'
                b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
            ),
        }
        wav_data = synthesize_ui_sound("click")
        rid = embed_package_sound(files, wav_data, "click.wav", "slide1.xml")
        
        self.assertEqual(rid, "rId1")
        self.assertIn("ppt/media/click.wav", files)
        self.assertEqual(files["ppt/media/click.wav"], wav_data)

        # Check [Content_Types].xml has wav default
        ct = ET.fromstring(files["[Content_Types].xml"])
        default_wav = ct.find(".//{http://schemas.openxmlformats.org/package/2006/content-types}Default[@Extension='wav']")
        self.assertIsNotNone(default_wav)
        self.assertEqual(default_wav.get("ContentType"), "audio/wav")

        # Check slide rels has audio relationship
        rels = ET.fromstring(files["ppt/slides/_rels/slide1.xml.rels"])
        rel_el = rels.find(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship[@Id='rId1']")
        self.assertIsNotNone(rel_el)
        self.assertEqual(rel_el.get("Target"), "../media/click.wav")

    def test_attach_click_and_hover_sound(self):
        """Verify attachment of sound effects to click and hover DrawingML actions."""
        slide_xml = (
            f'<p:sld xmlns:p="{NS_P}" xmlns:a="{NS_A}">'
            f'  <p:cSld><p:spTree>'
            f'    <p:sp>'
            f'      <p:nvSpPr><p:cNvPr id="5" name="Button"/></p:nvSpPr>'
            f'    </p:sp>'
            f'  </p:spTree></p:cSld>'
            f'</p:sld>'
        )
        tree = ET.fromstring(slide_xml.encode("utf-8"))
        
        # Attach click sound
        ok_click = attach_click_sound_and_action(tree, 5, sound_rid="rId9", sound_name="click.wav")
        self.assertTrue(ok_click)

        # Attach hover sound
        ok_hover = attach_hover_sound_and_action(tree, 5, sound_rid="rId9", sound_name="click.wav")
        self.assertTrue(ok_hover)

        # Verify XML structure
        cnvpr = tree.find(f".//{{{NS_P}}}cNvPr[@id='5']")
        self.assertIsNotNone(cnvpr)

        hlink = cnvpr.find(f"{{{NS_A}}}hlinkClick")
        self.assertIsNotNone(hlink)
        snd_c = hlink.find(f"{{{NS_A}}}snd")
        self.assertIsNotNone(snd_c)
        self.assertEqual(snd_c.get("name"), "click.wav")

        hover = cnvpr.find(f"{{{NS_A}}}hlinkHover")
        self.assertIsNotNone(hover)
        snd_h = hover.find(f"{{{NS_A}}}snd")
        self.assertIsNotNone(snd_h)
        self.assertEqual(snd_h.get("name"), "click.wav")

    def test_in_slide_modal_timings(self):
        """Verify compilation of modal open/close click groups."""
        clicks = build_in_slide_modal_click_groups(
            trigger_spid=3,
            modal_spids=[10, 11, 12],
            close_spid=12,
            entrance_preset="zoom",
            exit_preset="fade-out",
            duration_ms=300
        )
        self.assertEqual(len(clicks), 2)
        
        # Open click
        self.assertEqual(clicks[0]["trigger_spid"], "3")
        self.assertEqual(len(clicks[0]["effects"]), 3)
        self.assertEqual(clicks[0]["effects"][0]["spid"], "10")
        self.assertEqual(clicks[0]["effects"][0]["preset"], "fade")  # First item fades (dimmer)
        self.assertEqual(clicks[0]["effects"][1]["preset"], "zoom")

        # Close click
        self.assertEqual(clicks[1]["trigger_spid"], "12")
        self.assertEqual(len(clicks[1]["effects"]), 3)
        self.assertEqual(clicks[1]["effects"][0]["preset"], "fade-out")

    def test_tab_switcher_timings(self):
        """Verify compilation of multi-tab switching click groups."""
        tabs = [
            {"btn_spid": 1, "panel_spids": [10, 11]},
            {"btn_spid": 2, "panel_spids": [20, 21]},
            {"btn_spid": 3, "panel_spids": [30, 31]},
        ]
        clicks = build_tab_switcher_click_groups(tabs, transition_preset="fade", duration_ms=200)
        self.assertEqual(len(clicks), 3)

        # Tab 1 click: exits panels 2 and 3 (4 shapes), enters panel 1 (2 shapes)
        self.assertEqual(clicks[0]["trigger_spid"], "1")
        self.assertEqual(len(clicks[0]["effects"]), 6)

        # Tab 2 click: exits panels 1 and 3, enters panel 2
        self.assertEqual(clicks[1]["trigger_spid"], "2")
        self.assertEqual(len(clicks[1]["effects"]), 6)

    def test_configure_slide_morph_transition(self):
        """Verify slide morph transition injection into slide root."""
        slide_xml = (
            f'<p:sld xmlns:p="{NS_P}">'
            f'  <p:cSld><p:spTree/></p:cSld>'
            f'</p:sld>'
        )
        tree = ET.fromstring(slide_xml.encode("utf-8"))
        configure_slide_morph_transition(tree, duration_ms=800)

        trans = tree.find(f"{{{NS_P}}}transition")
        self.assertIsNotNone(trans)
        morph = trans.find(f"{{{NS_P14}}}morph")
        self.assertIsNotNone(morph)
        self.assertEqual(morph.get("option"), "byObject")

    def test_showcase_compilation_and_audit(self):
        """Verify full showcase deck generation, audio synthesis, and inspection audit."""
        with tempfile.TemporaryDirectory() as td:
            out_deck = Path(td) / "advanced_showcase.pptx"
            res = compile_advanced_interactive_showcase(out_deck)
            self.assertTrue(res["ok"])
            self.assertTrue(out_deck.is_file())

            audit = inspect_interactivity(out_deck)
            self.assertTrue(audit["ok"])
            self.assertEqual(audit["total_slides"], 4)
            self.assertGreater(audit["interactive_sequences_count"], 0)
            self.assertGreater(audit["sound_effects_count"], 0)
            self.assertGreater(audit["hover_actions_count"], 0)
            self.assertGreater(audit["morph_slides_count"], 0)


if __name__ == "__main__":
    unittest.main()
