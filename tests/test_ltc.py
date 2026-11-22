import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ltc import ELDERLY_AGE, CAREGIVER_AGE, ltc_indicators, prevalence_by_age


class TestLtc(unittest.TestCase):
    def test_prevalenza_crescente(self):
        prev = prevalence_by_age()
        self.assertTrue((np.diff(prev) >= 0).all())
        self.assertEqual(prev[50], 0.005)
        self.assertEqual(prev[95], 0.28)

    def test_indicatori_sintetici(self):
        ages = np.zeros((2, 101))
        ages[0, 85] = 100.0
        ages[0, 50] = 400.0
        ind = ltc_indicators(ages)
        self.assertAlmostEqual(ind["over80"][0], 100.0)
        self.assertAlmostEqual(ind["claimants"][0], 100.0 * 0.16)
        self.assertAlmostEqual(ind["caregivers"][0], 400.0)
        self.assertAlmostEqual(ind["ratio"][0], 400.0 / 16.0)

    def test_indicatori_vuoti(self):
        ages = np.zeros((1, 101))
        ind = ltc_indicators(ages)
        self.assertEqual(ind["claimants"][0], 0.0)
        self.assertTrue(np.isnan(ind["ratio"][0]))

    def test_bande_coerenti(self):
        prev = prevalence_by_age()
        self.assertLess(prev[ELDERLY_AGE], prev[95])
        self.assertGreater(prev[CAREGIVER_AGE[1]], 0)
