from __future__ import annotations

import unittest

import pandas as pd

from src.valuation import (
    calculate_forward_pe,
    dcf_per_share,
    scenario_earnings_valuation,
)


class ValuationTests(unittest.TestCase):
    def test_forward_pe_uses_guidance_midpoint(self) -> None:
        self.assertAlmostEqual(calculate_forward_pe(20.38, 2.30, 2.40), 8.6723, places=3)

    def test_scenario_earnings_math(self) -> None:
        scenarios = pd.DataFrame(
            [
                {
                    "scenario": "Base",
                    "revenue_growth": 0.015,
                    "operating_margin": 0.074,
                    "net_interest_income_m": 25,
                    "tax_rate": 0.25,
                    "diluted_shares_m": 373,
                    "pe_multiple": 9.5,
                }
            ]
        )
        result = scenario_earnings_valuation(scenarios, 15_400)
        self.assertGreater(float(result.loc[0, "estimated_eps"]), 2.30)
        self.assertLess(float(result.loc[0, "estimated_eps"]), 2.45)
        self.assertGreater(float(result.loc[0, "earnings_value"]), 21)

    def test_dcf_rejects_invalid_terminal_rate(self) -> None:
        with self.assertRaises(ValueError):
            dcf_per_share(
                starting_fcf_m=650,
                annual_growth=0.02,
                discount_rate=0.02,
                terminal_growth=0.02,
                forecast_years=5,
                net_cash_m=1_108,
                diluted_shares_m=373,
            )


if __name__ == "__main__":
    unittest.main()

