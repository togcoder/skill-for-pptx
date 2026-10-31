#!/usr/bin/env python3
"""Tests for the DeckCraft native bridge (T035)."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.deckcraft_bridge import (
    find_deckcraft_cli,
    is_available,
    render_slides,
    inspect_deck,
)


class DeckCraftBridgeTests(unittest.TestCase):
    def test_cli_detection_returns_valid_binary_or_none(self):
        cli = find_deckcraft_cli()
        if cli is not None:
            self.assertTrue(cli.is_file(), f"Detected CLI path is not a file: {cli}")
            self.assertTrue(is_available())
        else:
            self.assertFalse(is_available())

    def test_render_slides_on_fixture_when_available(self):
        if not is_available():
            self.skipTest("deckcraft-cli not available on this host")

        # Find any valid pptx fixture
        repo_root = Path(__file__).resolve().parents[1]
        sample = repo_root / "experiments" / "T019-20261005-claude-motion-director" / "report_deck_motion.pptx"
        if not sample.is_file():
            self.skipTest(f"Sample presentation fixture not found: {sample}")

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            images = render_slides(sample, out_dir, scale=1)
            self.assertGreater(len(images), 0, "Expected at least one slide to be rendered")
            for img in images:
                self.assertTrue(img.is_file(), f"Rendered image missing: {img}")
                self.assertGreater(img.stat().st_size, 0, f"Rendered image is empty: {img}")

    def test_render_single_slide(self):
        if not is_available():
            self.skipTest("deckcraft-cli not available on this host")

        repo_root = Path(__file__).resolve().parents[1]
        sample = repo_root / "experiments" / "T019-20261005-claude-motion-director" / "report_deck_motion.pptx"
        if not sample.is_file():
            self.skipTest(f"Sample presentation fixture not found: {sample}")

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            images = render_slides(sample, out_dir, scale=1, slide_index=0)
            self.assertEqual(len(images), 1)
            self.assertTrue(images[0].name.endswith(".png"))


if __name__ == "__main__":
    unittest.main()
