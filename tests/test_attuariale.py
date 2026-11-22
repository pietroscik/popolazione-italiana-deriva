import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

HAS_PROCESSED_DATA = (ROOT / "data" / "processed" / "n0_female.npy").exists()

import ltc_attuariale as act


def fake_processed(max_age=100, survival=0.99):
    n = np.full(max_age + 1, 1000.0)
    surv = np.full(max_age + 1, survival)
    surv[-1] = 0.0
    fert = np.zeros(max_age + 1)
    return {"n0": n, "n0_male": n, "survival": surv,
            "survival_male": surv, "fertility": fert}


class TestIncidenza(unittest.TestCase):
    def test_non_negativa_con_spikes_ai_bordi_banda(self):
        inc = act.net_incidence_by_age()
        self.assertTrue((inc >= 0).all())
        self.assertGreater(inc[89], 0.1)
        self.assertGreater(inc[84], 0.05)
        self.assertEqual(inc[85], 0.0)
        self.assertEqual(inc[100], 0.0)


class TestFondo(unittest.TestCase):
    @patch("leslie.load_processed")
    def test_nessuna_incidenza_premio_zero(self, mock):
        mock.return_value = fake_processed()
        with patch.object(act, "PLATEA", 100_000.0):
            with patch.object(act, "net_incidence_by_age",
                              return_value=np.zeros(101)):
                res = act.simulate_fund(years=3)
        for r in res["serie"]:
            self.assertEqual(r["claimants"], 0.0)
            self.assertEqual(r["premio_puro_eur"], 0.0)

    @patch("leslie.load_processed")
    def test_con_incidenza_premio_crescente(self, mock):
        mock.return_value = fake_processed()
        inc = np.zeros(101)
        inc[60:] = 0.01
        with patch.object(act, "PLATEA", 1_000_000.0):
            with patch.object(act, "net_incidence_by_age", return_value=inc):
                res = act.simulate_fund(adesioni_automatiche=False, years=10)
        premi = [r["premio_puro_eur"] for r in res["serie"]]
        self.assertTrue(np.all(np.diff(premi) > 0))

    @unittest.skipUnless(HAS_PROCESSED_DATA, "vettori preprocessati non generati")
    def test_report_reale_ordini_grandezza(self):
        res = act.attuariale_report(verbose=False)
        self.assertGreater(res["adesioni_automatiche"]["premio_2026"], 0)
        self.assertLess(res["adesioni_automatiche"]["premio_2056"],
                        res["platea_costante"]["premio_2056"])


class TestIndicizzazione(unittest.TestCase):
    @patch("leslie.load_processed")
    def test_indicizzazione_pura_e_demografia_separate(self, mock):
        mock.return_value = fake_processed()
        inc = np.zeros(101)
        inc[60:] = 0.01
        with patch.object(act, "PLATEA", 1_000_000.0):
            with patch.object(act, "net_incidence_by_age", return_value=inc):
                base = act.simulate_fund(adesioni_automatiche=True,
                                          indicizzazione=0.0, years=10)
                idx = act.simulate_fund(adesioni_automatiche=True,
                                        indicizzazione=0.02, years=10)
        inflaz = (1.02) ** 10
        self.assertAlmostEqual(idx["serie"][-1]["premio_puro_eur"],
                                base["serie"][-1]["premio_puro_eur"] * inflaz,
                                delta=1e-6)
        self.assertAlmostEqual(idx["serie"][-1]["premio_reale_eur"],
                                base["serie"][-1]["premio_puro_eur"],
                                delta=1e-6)


if __name__ == "__main__":
    unittest.main()
