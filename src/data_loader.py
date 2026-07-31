"""Input loading and validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_FILES = {
    "snapshot": "financial_snapshot.csv",
    "brands": "brand_performance.csv",
    "risks": "risk_inputs.csv",
    "scenarios": "valuation_scenarios.csv",
    "sourcing": "sourcing_exposure.csv",
    "sources": "source_register.csv",
}


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"Input file contains no records: {path}")
    return frame


def load_inputs(input_dir: Path) -> dict[str, pd.DataFrame]:
    inputs = {key: _read_csv(input_dir / name) for key, name in REQUIRED_FILES.items()}

    snapshot = inputs["snapshot"]
    required_snapshot_columns = {"metric", "value", "unit", "as_of"}
    if not required_snapshot_columns.issubset(snapshot.columns):
        missing = sorted(required_snapshot_columns - set(snapshot.columns))
        raise ValueError(f"Financial snapshot missing columns: {missing}")
    if snapshot["metric"].duplicated().any():
        duplicates = snapshot.loc[snapshot["metric"].duplicated(), "metric"].tolist()
        raise ValueError(f"Financial snapshot has duplicate metrics: {duplicates}")

    scenario_probabilities = inputs["scenarios"]["probability"].sum()
    if abs(scenario_probabilities - 1.0) > 1e-9:
        raise ValueError("Valuation scenario probabilities must sum to 1.0")

    return inputs


def snapshot_to_dict(snapshot: pd.DataFrame) -> dict[str, float]:
    return {
        str(row.metric): float(row.value)
        for row in snapshot[["metric", "value"]].itertuples(index=False)
    }

