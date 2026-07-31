# Contributing

Contributions should preserve the model's reproducibility, source traceability,
and separation between pinned financial assumptions and optional live market data.

## Development setup

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python main.py --simulations 2000 --seed 42
```

On Windows PowerShell, activate the environment with:

```powershell
& ".\.venv\Scripts\Activate.ps1"
```

## Pull-request checklist

- Explain the analytical reason for the change.
- Add or update tests for changed logic.
- Keep scenario probabilities summing to 1.0.
- Record dates and primary sources for new pinned inputs.
- Do not replace pinned assumptions with silently fetched live data.
- Run the full unit-test suite.
- Run the pinned pipeline and inspect the generated report.
- Update `CHANGELOG.md` when the change affects users or outputs.

## Updating financial assumptions

When updating the model after an earnings release:

1. Preserve the existing dated snapshot before replacing it.
2. Update every affected file under `data/pinned/`.
3. Add the source URL and date to `source_register.csv`.
4. Reassess valuation scenarios and operational-risk scores independently.
5. Document material judgment changes in the pull request.

## Scope

This repository is intended for transparent research and decision support. Do
not present model outputs as guaranteed returns or individualized investment advice.

