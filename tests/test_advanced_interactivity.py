"""Unit tests for Advanced Presentation Interactivity & 1-Slide Mini-Games Engine (T049).

Antigravity multi-domain design research lab.
Verifies:
1. Pure-Python synthetic audio generation (WAV PCM 16-bit).
2. Canonical OOXML interactiveSeq XML construction matching Office 16.0 COM.
3. 1-Slide Mini-Games Suite compilation and structural inspection.
"""

import io
import tempfile
import unittest
import wave
from pathlib import Path
from lxml import etree as ET

from scripts.advanced_interactivity import (
    synthesize_ui_sound,
    build_canonical_interactive_seq,
    compile_one_slide_games_suite,
    inspect_interactivity,
    NAMESPACES,
    NS_P,
)


class TestAdvancedInteractivity(unittest.TestCase):
    """Test suite for T049 advanced interactivity & 1-slide mini-games."""

    def test_audio_synthesis_wav_format(self):
        """Verify that all synthesized sound types produce valid 16-bit mono WAV streams."""
        for sound_type in ("click", "chime", "buzz"):
            wav_bytes = synthesize_ui_sound(sound_type)
            self.assertGreater(len(wav_bytes), 100)
            with wave.open(io.BytesIO(wav_bytes), "rb") as w:
                self.assertEqual(w.getnchannels(), 1)
                self.assertEqual(w.getsampwidth(), 2)
                self.assertEqual(w.getframerate(), 44100)
                self.assertGreater(w.getnframes(), 0)

    def test_build_canonical_interactive_seq(self):
        """Verify that the generated interactiveSeq subtree matches native PowerPoint structure."""
        seq_el = build_canonical_interactive_seq(
            trigger_spid=3,
            target_spids=[3],
            is_exit=True,
            preset_name="zoom",
            duration_ms=350,
            seq_id=2
        )
        self.assertEqual(seq_el.tag, f"{{{NS_P}}}seq")
        
        # Verify cTn nodeType
        ctn = seq_el.find(f"{{{NS_P}}}cTn[@nodeType='interactiveSeq']")
        self.assertIsNotNone(ctn)

        # Verify stCondLst with onClick
        st_cond = ctn.find(f".//{{{NS_P}}}stCondLst/{{{NS_P}}}cond[@evt='onClick']/{{{NS_P}}}tgtEl/{{{NS_P}}}spTgt")
        self.assertIsNotNone(st_cond)
        self.assertEqual(st_cond.get("spid"), "3")

        # Verify nextCondLst on seq
        nxt_cond = seq_el.find(f"{{{NS_P}}}nextCondLst/{{{NS_P}}}cond[@evt='onClick']/{{{NS_P}}}tgtEl/{{{NS_P}}}spTgt")
        self.assertIsNotNone(nxt_cond)
        self.assertEqual(nxt_cond.get("spid"), "3")

    def test_compile_one_slide_games_suite(self):
        """Verify compilation of the 2-slide autonomous 1-slide games suite."""
        try:
            import win32com.client  # noqa: F401
        except ImportError:
            self.skipTest("needs PowerPoint COM (pywin32 + PowerPoint)")
        with tempfile.TemporaryDirectory() as td:
            out_deck = Path(td) / "one_slide_games_suite.pptx"
            res = compile_one_slide_games_suite(out_deck)
            self.assertTrue(res["ok"])
            self.assertTrue(out_deck.is_file())

            audit = inspect_interactivity(out_deck)
            self.assertTrue(audit["ok"])
            self.assertEqual(audit["total_slides"], 2)
            # 4 interactive sequences per slide (3 choice/chest triggers + 1 reset trigger)
            self.assertEqual(audit["interactive_sequences_count"], 8)
            self.assertEqual(len(audit["slides"][0]["interactive_sequences"]), 4)
            self.assertEqual(len(audit["slides"][1]["interactive_sequences"]), 4)


if __name__ == "__main__":
    unittest.main()
