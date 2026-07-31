from __future__ import annotations

import unittest

import pandas as pd

from src.risk_engine import margin_materiality, score_risks


class RiskEngineTests(unittest.TestCase):
    def test_scores_are_bounded(self) -> None:
        risks = pd.DataFrame(
            [
                {
                    "risk": "Test risk",
                    "category": "Test",
                    "likelihood": 5,
                    "impact": 5,
                    "velocity": 5,
                    "controllability": 1,
                    "weight": 1,
                }
            ]
        )
        scored, composite = score_risks(risks)
        self.assertEqual(float(scored.loc[0, "adjusted_score"]), 100.0)
        self.assertEqual(composite, 100.0)

    def test_100_bps_materiality(self) -> None:
        result = margin_materiality(
            revenue_m=15_631,
            margin_change_bps=100,
            tax_rate=0.25,
            diluted_shares_m=375,
            pe_multiple=9.5,
        )
        self.assertAlmostEqual(result["pre_tax_impact_m"], 156.31, places=2)
        self.assertAlmostEqual(result["eps_impact"], 0.31262, places=4)
        self.assertAlmostEqual(result["price_impact"], 2.9699, places=3)


if __name__ == "__main__":
    unittest.main()

