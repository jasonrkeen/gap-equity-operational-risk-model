"""End-to-end model orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .charts import (
    brand_performance_chart,
    monte_carlo_chart,
    risk_matrix_chart,
    scenario_valuation_chart,
    sensitivity_chart,
    sourcing_chart,
)
from .config import ProjectPaths, VALUATION_BLEND
from .data_loader import load_inputs, snapshot_to_dict
from .market_data import get_market_snapshot
from .monte_carlo import simulate_equity_value
from .report import build_executive_report
from .risk_engine import margin_materiality, score_risks
from .valuation import (
    attach_dcf_values,
    calculate_forward_pe,
    calculate_risk_weighted_value,
    operating_margin_sensitivity,
    scenario_earnings_valuation,
)


@dataclass(frozen=True)
class PipelineResult:
    data_status: str
    reference_price: float
    forward_pe: float
    composite_risk_score: float
    mc_median: float
    probability_above_reference: float
    risk_weighted_value: float
    report_path: Path


def run_pipeline(
    project_root: Path,
    use_live: bool = False,
    simulation_count: int = 20_000,
    seed: int = 42,
) -> PipelineResult:
    paths = ProjectPaths.from_root(project_root)
    paths.ensure_output_directories()

    print("[1/10] Loading and validating pinned inputs...")
    inputs = load_inputs(paths.input_dir)
    snapshot = snapshot_to_dict(inputs["snapshot"])
    pinned_as_of = str(inputs["snapshot"]["as_of"].iloc[0])

    print("[2/10] Resolving market snapshot...")
    market = get_market_snapshot(
        pinned_price=snapshot["share_price_usd"],
        pinned_as_of=pinned_as_of,
        use_live=use_live,
    )

    print("[3/10] Calculating valuation scenarios...")
    valuations = scenario_earnings_valuation(
        scenarios=inputs["scenarios"],
        base_revenue_m=snapshot["fy2025_revenue_m"],
    )
    net_cash_m = snapshot["cash_and_short_term_investments_m"] - snapshot["long_term_debt_m"]
    valuations = attach_dcf_values(
        valuations,
        net_cash_m=net_cash_m,
        earnings_weight=VALUATION_BLEND["earnings"],
        dcf_weight=VALUATION_BLEND["dcf"],
    )
    risk_weighted_value = calculate_risk_weighted_value(valuations)
    forward_pe = calculate_forward_pe(
        market.price,
        snapshot["fy2026_adjusted_eps_low"],
        snapshot["fy2026_adjusted_eps_high"],
    )

    print("[4/10] Scoring operational risks...")
    scored_risks, composite_risk_score = score_risks(inputs["risks"])
    materiality = margin_materiality(
        revenue_m=snapshot["fy2025_revenue_m"]
        * (1 + snapshot["fy2026_revenue_growth_mid"]),
        margin_change_bps=100,
        tax_rate=0.25,
        diluted_shares_m=375,
        pe_multiple=9.5,
    )

    print(f"[5/10] Running {simulation_count:,} Monte Carlo trials...")
    simulations, mc_summary = simulate_equity_value(
        base_revenue_m=snapshot["fy2025_revenue_m"],
        net_cash_m=net_cash_m,
        current_price=market.price,
        simulation_count=simulation_count,
        seed=seed,
    )

    print("[6/10] Building valuation sensitivity...")
    sensitivity = operating_margin_sensitivity(
        base_revenue_m=snapshot["fy2025_revenue_m"]
        * (1 + snapshot["fy2026_revenue_growth_mid"]),
        net_interest_income_m=25,
        tax_rate=0.25,
        diluted_shares_m=375,
        margins=np.array([0.050, 0.060, 0.070, 0.074, 0.080, 0.090]),
        multiples=np.array([7.0, 8.0, 9.0, 9.5, 10.5, 12.0]),
    )

    print("[7/10] Writing analyst data outputs...")
    valuations.to_csv(paths.output_data_dir / "scenario_valuations.csv", index=False)
    scored_risks.to_csv(paths.output_data_dir / "risk_scorecard.csv", index=False)
    sensitivity.to_csv(paths.output_data_dir / "valuation_sensitivity.csv", index=False)
    simulations.to_csv(paths.output_data_dir / "monte_carlo_simulations.csv", index=False)
    pd.DataFrame([mc_summary]).to_csv(
        paths.output_data_dir / "monte_carlo_summary.csv",
        index=False,
    )

    print("[8/10] Generating charts...")
    chart_paths = {
        "scenario": scenario_valuation_chart(
            valuations, paths.chart_dir / "scenario_valuation.png"
        ),
        "monte_carlo": monte_carlo_chart(
            simulations,
            market.price,
            mc_summary,
            paths.chart_dir / "monte_carlo_distribution.png",
        ),
        "risk": risk_matrix_chart(
            scored_risks, paths.chart_dir / "operational_risk_matrix.png"
        ),
        "brands": brand_performance_chart(
            inputs["brands"], paths.chart_dir / "brand_performance.png"
        ),
        "sensitivity": sensitivity_chart(
            sensitivity, paths.chart_dir / "valuation_sensitivity.png"
        ),
        "sourcing": sourcing_chart(
            inputs["sourcing"], paths.chart_dir / "sourcing_concentration.png"
        ),
    }

    print("[9/10] Generating executive PDF brief...")
    report_path = build_executive_report(
        output_path=paths.pdf_dir / "gap_equity_operational_risk_brief.pdf",
        reference_price=market.price,
        data_status=market.status,
        forward_pe=forward_pe,
        composite_risk_score=composite_risk_score,
        risk_weighted_value=risk_weighted_value,
        valuations=valuations,
        scored_risks=scored_risks,
        brands=inputs["brands"],
        sourcing=inputs["sourcing"],
        mc_summary=mc_summary,
        materiality=materiality,
        chart_paths=chart_paths,
        sources=inputs["sources"],
        as_of=market.as_of,
    )

    print("[10/10] Pipeline complete.")
    return PipelineResult(
        data_status=market.status,
        reference_price=market.price,
        forward_pe=forward_pe,
        composite_risk_score=composite_risk_score,
        mc_median=mc_summary["median"],
        probability_above_reference=mc_summary["probability_above_reference"],
        risk_weighted_value=risk_weighted_value,
        report_path=report_path,
    )

