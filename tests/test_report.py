from __future__ import annotations

import unittest

from reportlab.pdfbase import pdfmetrics

from src.report import FONT_BOLD, FONT_REGULAR, _register_fonts


class ReportTests(unittest.TestCase):
    def test_report_fonts_are_available_without_system_font_install(self) -> None:
        _register_fonts()
        registered = set(pdfmetrics.getRegisteredFontNames())
        self.assertIn(FONT_REGULAR, registered)
        self.assertIn(FONT_BOLD, registered)


if __name__ == "__main__":
    unittest.main()
