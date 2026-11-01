#!/usr/bin/env python3
"""Tests for WordCraft, GridCraft, and VectorCraft Native Bridges (T037)."""
from __future__ import annotations

import unittest

from scripts.wordcraft_bridge import (
    find_wordcraft_cli,
    is_available as is_wordcraft_available,
)
from scripts.gridcraft_bridge import (
    find_gridcraft_cli,
    is_available as is_gridcraft_available,
    eval_formula,
)
from scripts.vectorcraft_bridge import (
    find_vectorcraft_cli,
    is_available as is_vectorcraft_available,
)


class CraftBridgesTests(unittest.TestCase):
    def test_wordcraft_cli_detection(self):
        cli = find_wordcraft_cli()
        if cli is not None:
            self.assertTrue(cli.is_file())
            self.assertTrue(is_wordcraft_available())
        else:
            self.assertFalse(is_wordcraft_available())

    def test_gridcraft_cli_detection_and_eval(self):
        cli = find_gridcraft_cli()
        if cli is not None:
            self.assertTrue(cli.is_file())
            self.assertTrue(is_gridcraft_available())
            res = eval_formula("10 + 20")
            self.assertEqual(res, 30)
        else:
            self.assertFalse(is_gridcraft_available())

    def test_vectorcraft_cli_detection(self):
        cli = find_vectorcraft_cli()
        if cli is not None:
            self.assertTrue(cli.is_file())
            self.assertTrue(is_vectorcraft_available())
        else:
            self.assertFalse(is_vectorcraft_available())


if __name__ == "__main__":
    unittest.main()
