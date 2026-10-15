> This file mirrors `.github/copilot-instructions.md`; keep both in sync when either changes.

# CLAUDE.md — Gap Equity and Operational Risk Model

## Purpose
Python-based Gap Inc. equity research model combining scenario valuation, Monte Carlo simulation, sensitivity analysis, and operational-risk scoring with reproducible outputs and an executive PDF brief.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `numpy`, `pandas`, `matplotlib`, `reportlab`, `yfinance`

## Folder structure
- `.github/` (1 files)
- `data/` (6 files)
- `docs/` (1 files)
- `src/` (10 files)
- `tests/` (5 files)
- `CHANGELOG.md`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `README.md`
- `main.py`
- `requirements.txt`

## Setup, run, test
- `pip install -r requirements.txt`
- Entry point present: `main.py`
- Tests: 5 Python test file(s) under `tests/`; framework appears to be unittest. Add/update tests with any logic change.
- CI workflows exist in `.github/workflows/`; keep them passing.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Uses `dataclasses` for structured config/results.
- Config lives in: `src/config.py`; avoid hardcoding parameters elsewhere.
- Random seeds are set for reproducibility (Monte Carlo/simulation); keep seeded, deterministic runs.
- Public data sources referenced: yfinance.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- A PDF report is produced with `reportlab`; keep it in sync with model changes.
- Charts are generated with matplotlib.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
