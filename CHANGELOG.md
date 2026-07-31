# Changelog

All notable project changes are documented here.

## [1.0.1] - 2026-07-30

### Added

- Cross-platform PDF font discovery using ReportLab's bundled Bitstream Vera fonts.
- A unit test that verifies report fonts load without a separate system-font installation.
- GitHub Actions testing across Python 3.11, 3.12, 3.13, and 3.14.
- A pinned executive brief for reproducible portfolio review.
- Citation and contribution guidance.

### Validated

- Nine unit tests pass on the release build.
- Pinned and live-price modes complete successfully on Windows with Python 3.14.
- The six-page PDF passes text extraction and full-page visual inspection.

### Fixed

- Removed the Linux-only DejaVu Sans path that prevented PDF creation on Windows.
- Corrected negative brand-performance and overlapping risk-matrix annotations.
- Embedded portable TrueType fonts to prevent irregular PDF character spacing.

## [1.0.0] - 2026-07-30

### Added

- Earnings, DCF, and probability-weighted scenario valuation.
- Eight-factor operational-risk scoring.
- Brand and sourcing-concentration diagnostics.
- Operating-margin sensitivity analysis.
- Seeded 20,000-trial Monte Carlo simulation.
- Pinned-data mode with optional live market-price refresh.
- Six charts, machine-readable outputs, and an executive PDF brief.
- Initial unit-test suite, methodology documentation, and source register.

