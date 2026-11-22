import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ltc_informale import (
    HOURS_PER_WEEK_INFORMAL,
    VALUE_PER_HOUR,
    calibrazione_sensitivity,
    caregiver_gap,
    informal_care_value,
)

HAS_PROCESSED_DATA = (ROOT / "data" / "processed" / "n0_female.npy").exists()


class TestInformalValue(unittest.TestCase):
    def test_valore_lineare(self):
        v = informal_care_value(1000.0)
        expected = 1000.0 * HOURS_PER_WEEK_INFORMAL * 52 * VALUE_PER_HOUR
        self.assertAlmostEqual(v, expected)

    def test_ordini_di_grandezza(self):
        v_mld = informal_care_value(1.0e6) / 1e9
        self.assertGreater(v_mld, 10.0)
        self.assertLess(v_mld, 30.0)


class TestSensitivity(unittest.TestCase):
    @unittest.skipUnless(HAS_PROCESSED_DATA, "vettori preprocessati non generati")
    def test_picco_cresce_con_r0(self):
        res = calibrazione_sensitivity()
        peaks = [r["costo_picco_mld"] for r in res]
        self.assertTrue(all(np.diff(peaks) > 0))


class TestCaregiverGap(unittest.TestCase):
    @unittest.skipUnless(HAS_PROCESSED_DATA, "vettori preprocessati non generati")
    def test_gap_corretto(self):
        gap = caregiver_gap(soglia=7.0)
        self.assertEqual(gap["saldo_richiesto"], 0.0)

    @unittest.skipUnless(HAS_PROCESSED_DATA, "vettori preprocessati non generati")
    def test_soglia_irraggiungibile_dichiarata(self):
        gap = caregiver_gap(soglia=11.5)
        self.assertIsNone(gap["saldo_richiesto"])
        self.assertIn("nota", gap)


if __name__ == "__main__":
    unittest.main()
