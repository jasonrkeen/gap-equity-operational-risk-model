from __future__ import annotations

import unittest

from src.monte_carlo import simulate_equity_value


class MonteCarloTests(unittest.TestCase):
    def test_simulation_is_reproducible(self) -> None:
        first_frame, first_summary = simulate_equity_value(
            base_revenue_m=15_400,
            net_cash_m=1_108,
            current_price=20.38,
            simulation_count=2_000,
            seed=7,
        )
        second_frame, second_summary = simulate_equity_value(
            base_revenue_m=15_400,
            net_cash_m=1_108,
            current_price=20.38,
            simulation_count=2_000,
            seed=7,
        )
        self.assertEqual(len(first_frame), 2_000)
        self.assertAlmostEqual(first_summary["median"], second_summary["median"], places=12)
        self.assertTrue((first_frame["simulated_price"] >= 0).all())

    def test_rejects_too_few_trials(self) -> None:
        with self.assertRaises(ValueError):
            simulate_equity_value(
                base_revenue_m=15_400,
                net_cash_m=1_108,
                current_price=20.38,
                simulation_count=500,
            )


if __name__ == "__main__":
    unittest.main()

