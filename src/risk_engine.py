"""Operational-risk scoring and materiality estimates."""

from __future__ import annotations

import pandas as pd


def score_risks(risks: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    required = {
        "risk",
        "category",
        "likelihood",
        "impact",
        "velocity",
        "controllability",
        "weight",
    }
    missing = required - set(risks.columns)
    if missing:
        raise ValueError(f"Risk input missing columns: {sorted(missing)}")

    frame = risks.copy()
    numeric_columns = [
        "likelihood",
        "impact",
        "velocity",
        "controllability",
        "weight",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    for column in ["likelihood", "impact", "velocity", "controllability"]:
        if not frame[column].between(1, 5).all():
            raise ValueError(f"{column} scores must be between 1 and 5")

    if (frame["weight"] <= 0).any():
        raise ValueError("Risk weights must be positive")

    frame["inherent_score"] = frame["likelihood"] * frame["impact"] * 4
    velocity_factor = 1 + 0.10 * (frame["velocity"] - 3)
    control_factor = 1 - 0.05 * (frame["controllability"] - 3)
    frame["adjusted_score"] = (
        frame["inherent_score"] * velocity_factor * control_factor
    ).clip(0, 100)
    frame["normalized_weight"] = frame["weight"] / frame["weight"].sum()
    frame["weighted_contribution"] = (
        frame["adjusted_score"] * frame["normalized_weight"]
    )
    frame = frame.sort_values("adjusted_score", ascending=False).reset_index(drop=True)
    composite = float(frame["weighted_contribution"].sum())
    return frame, composite


def margin_materiality(
    revenue_m: float,
    margin_change_bps: float,
    tax_rate: float,
    diluted_shares_m: float,
    pe_multiple: float,
) -> dict[str, float]:
    pre_tax_impact_m = revenue_m * margin_change_bps / 10_000
    after_tax_impact_m = pre_tax_impact_m * (1 - tax_rate)
    eps_impact = after_tax_impact_m / diluted_shares_m
    price_impact = eps_impact * pe_multiple
    return {
        "pre_tax_impact_m": float(pre_tax_impact_m),
        "after_tax_impact_m": float(after_tax_impact_m),
        "eps_impact": float(eps_impact),
        "price_impact": float(price_impact),
    }

