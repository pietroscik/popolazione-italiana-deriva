import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ltc_costi import (
    UNIT_COST_DOMICILIARE,
    UNIT_COST_RESIDENZIALE,
    annual_cost,
    cost_breakdown,
    informal_share,
)


class TestInformalShare(unittest.TestCase):
    def test_monotonia_decrescente(self):
        ratios = np.array([4.0, 8.0, 14.5, 20.0])
        shares = informal_share(ratios)
        self.assertTrue((np.diff(shares) > 0).all())

    def test_calibrazione_dichiarata(self):
        self.assertGreater(informal_share(14.5), 0.75)
        self.assertAlmostEqual(informal_share(11.0), 0.5, places=6)
        self.assertLess(informal_share(6.0), 0.2)


class TestCostBreakdown(unittest.TestCase):
    def test_conservazione_claimants(self):
        bd = cost_breakdown(1000.0, 10.0)
        total = bd["informale"] + bd["domiciliare"] + bd["residenziale"]
        self.assertAlmostEqual(total, 1000.0)

    def test_costo_aggiuntivo(self):
        bd = cost_breakdown(1000.0, 10.0)
        self.assertGreater(bd["domiciliare"], bd["residenziale"])
        cost = annual_cost(bd)
        expected = (bd["domiciliare"] * UNIT_COST_DOMICILIARE +
                    bd["residenziale"] * UNIT_COST_RESIDENZIALE)
        self.assertAlmostEqual(cost, expected)

    def test_ratio_basso_aumenta_costo_formale(self):
        alto = annual_cost(cost_breakdown(1000.0, 14.0))
        basso = annual_cost(cost_breakdown(1000.0, 6.0))
        self.assertGreater(basso, alto)


if __name__ == "__main__":
    unittest.main()
