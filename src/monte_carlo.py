"""Monte Carlo simulation of Gap's one-year earnings-based equity value."""

from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_equity_value(
    base_revenue_m: float,
    net_cash_m: float,
    current_price: float,
    simulation_count: int = 20_000,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict[str, float]]:
    if simulation_count < 1_000:
        raise ValueError("Use at least 1,000 simulations for a stable distribution")

    rng = np.random.default_rng(seed)
    revenue_growth = np.clip(rng.normal(0.015, 0.025, simulation_count), -0.08, 0.10)
    operating_margin = np.clip(rng.normal(0.074, 0.012, simulation_count), 0.035, 0.11)
    tax_rate = np.clip(rng.normal(0.25, 0.015, simulation_count), 0.20, 0.31)
    net_interest_income = np.clip(rng.normal(25, 10, simulation_count), -10, 60)
    diluted_shares = np.clip(rng.normal(373, 5, simulation_count), 350, 390)
    pe_multiple = np.clip(rng.normal(9.5, 2.0, simulation_count), 5.5, 16.0)

    tariff_event = rng.random(simulation_count) < 0.35
    tariff_margin_penalty = np.where(
        tariff_event, rng.uniform(0.004, 0.015, simulation_count), 0.0
    )

    consumer_event = rng.random(simulation_count) < 0.25
    consumer_growth_penalty = np.where(
        consumer_event, rng.uniform(0.010, 0.040, simulation_count), 0.0
    )

    brand_upside_event = rng.random(simulation_count) < 0.30
    brand_growth_benefit = np.where(
        brand_upside_event, rng.uniform(0.010, 0.035, simulation_count), 0.0
    )
    brand_margin_benefit = np.where(
        brand_upside_event, rng.uniform(0.000, 0.004, simulation_count), 0.0
    )

    realized_growth = revenue_growth - consumer_growth_penalty + brand_growth_benefit
    realized_margin = np.clip(
        operating_margin - tariff_margin_penalty + brand_margin_benefit,
        0.02,
        0.12,
    )
    revenue = base_revenue_m * (1 + realized_growth)
    operating_income = revenue * realized_margin
    net_income = (operating_income + net_interest_income) * (1 - tax_rate)
    eps = net_income / diluted_shares

    net_cash_per_share = net_cash_m / diluted_shares
    balance_sheet_adjustment = 0.10 * net_cash_per_share
    simulated_price = np.maximum(eps * pe_multiple + balance_sheet_adjustment, 0)

    frame = pd.DataFrame(
        {
            "revenue_growth": realized_growth,
            "operating_margin": realized_margin,
            "eps": eps,
            "pe_multiple": pe_multiple,
            "simulated_price": simulated_price,
            "tariff_event": tariff_event,
            "consumer_event": consumer_event,
            "brand_upside_event": brand_upside_event,
        }
    )

    prices = frame["simulated_price"]
    summary = {
        "mean": float(prices.mean()),
        "median": float(prices.median()),
        "p05": float(prices.quantile(0.05)),
        "p25": float(prices.quantile(0.25)),
        "p75": float(prices.quantile(0.75)),
        "p95": float(prices.quantile(0.95)),
        "probability_above_reference": float((prices > current_price).mean()),
        "probability_below_15": float((prices < 15).mean()),
        "probability_above_27": float((prices > 27).mean()),
    }
    return frame, summary

