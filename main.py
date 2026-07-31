"""Command-line entry point for the Gap Equity and Operational Risk Model."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Gap Inc. equity valuation and operational-risk analysis."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Attempt to refresh the market price with yfinance; pinned data remains the fallback.",
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=20_000,
        help="Number of Monte Carlo trials (default: 20,000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    result = run_pipeline(
        project_root=project_root,
        use_live=args.live,
        simulation_count=args.simulations,
        seed=args.seed,
    )

    print("=" * 72)
    print("Gap Equity and Operational Risk Model")
    print("=" * 72)
    print(f"Data status:              {result.data_status}")
    print(f"Reference price:          ${result.reference_price:,.2f}")
    print(f"Forward P/E:              {result.forward_pe:,.2f}x")
    print(f"Composite risk score:     {result.composite_risk_score:,.1f}/100")
    print(f"Monte Carlo median:       ${result.mc_median:,.2f}")
    print(f"P(price > reference):     {result.probability_above_reference:.1%}")
    print(f"Risk-weighted fair value: ${result.risk_weighted_value:,.2f}")
    print(f"Executive brief:          {result.report_path}")


if __name__ == "__main__":
    main()

