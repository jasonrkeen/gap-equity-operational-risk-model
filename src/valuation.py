"""Earnings, DCF, and sensitivity valuation functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_forward_pe(price: float, eps_low: float, eps_high: float) -> float:
    midpoint = (eps_low + eps_high) / 2
    if midpoint <= 0:
        raise ValueError("Forward EPS midpoint must be positive")
    return float(price / midpoint)


def scenario_earnings_valuation(
    scenarios: pd.DataFrame,
    base_revenue_m: float,
) -> pd.DataFrame:
    frame = scenarios.copy()
    frame["revenue_m"] = base_revenue_m * (1 + frame["revenue_growth"])
    frame["operating_income_m"] = frame["revenue_m"] * frame["operating_margin"]
    frame["pre_tax_income_m"] = (
        frame["operating_income_m"] + frame["net_interest_income_m"]
    )
    frame["net_income_m"] = frame["pre_tax_income_m"] * (1 - frame["tax_rate"])
    frame["estimated_eps"] = frame["net_income_m"] / frame["diluted_shares_m"]
    frame["earnings_value"] = frame["estimated_eps"] * frame["pe_multiple"]
    return frame


def dcf_per_share(
    starting_fcf_m: float,
    annual_growth: float,
    discount_rate: float,
    terminal_growth: float,
    forecast_years: int,
    net_cash_m: float,
    diluted_shares_m: float,
) -> float:
    if discount_rate <= terminal_growth:
        raise ValueError("Discount rate must exceed terminal growth")
    if diluted_shares_m <= 0:
        raise ValueError("Diluted share count must be positive")

    forecast_fcfs = [
        starting_fcf_m * ((1 + annual_growth) ** year)
        for year in range(1, forecast_years + 1)
    ]
    present_values = [
        fcf / ((1 + discount_rate) ** year)
        for year, fcf in enumerate(forecast_fcfs, start=1)
    ]
    terminal_fcf = forecast_fcfs[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_years)
    equity_value_m = sum(present_values) + pv_terminal + net_cash_m
    return float(equity_value_m / diluted_shares_m)


def attach_dcf_values(
    valuations: pd.DataFrame,
    net_cash_m: float,
    earnings_weight: float = 0.70,
    dcf_weight: float = 0.30,
) -> pd.DataFrame:
    frame = valuations.copy()
    frame["dcf_value"] = frame.apply(
        lambda row: dcf_per_share(
            starting_fcf_m=float(row["starting_fcf_m"]),
            annual_growth=float(row["fcf_growth"]),
            discount_rate=float(row["discount_rate"]),
            terminal_growth=float(row["terminal_growth"]),
            forecast_years=5,
            net_cash_m=net_cash_m,
            diluted_shares_m=float(row["diluted_shares_m"]),
        ),
        axis=1,
    )
    frame["blended_value"] = (
        earnings_weight * frame["earnings_value"] + dcf_weight * frame["dcf_value"]
    )
    return frame


def calculate_risk_weighted_value(valuations: pd.DataFrame) -> float:
    return float((valuations["probability"] * valuations["blended_value"]).sum())


def operating_margin_sensitivity(
    base_revenue_m: float,
    net_interest_income_m: float,
    tax_rate: float,
    diluted_shares_m: float,
    margins: np.ndarray,
    multiples: np.ndarray,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for margin in margins:
        pre_tax = base_revenue_m * margin + net_interest_income_m
        eps = pre_tax * (1 - tax_rate) / diluted_shares_m
        for multiple in multiples:
            rows.append(
                {
                    "operating_margin": float(margin),
                    "pe_multiple": float(multiple),
                    "implied_price": float(eps * multiple),
                }
            )
    return pd.DataFrame(rows)

