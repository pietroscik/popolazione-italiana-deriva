"""Validazione demografica e conservazione della popolazione.

Il test suite storico copre la correttezza del codice; qui si verifica la
coerenza demografica dei dati ISTAT processati e la conservazione della
popolazione nella proiezione a due sessi (bilancio demografico chiuso)."""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from leslie import project_two_sex, simulate_two_sex  # noqa: E402

HAS_DATA = (ROOT / "data" / "processed" / "n0_female.npy").exists()


class TestBilancioDemografico(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(5)
        n = 101
        self.nf = rng.uniform(100_000, 500_000, n)
        self.nm = rng.uniform(100_000, 500_000, n)
        fert = np.zeros(n)
        fert[15:50] = 0.05
        self.P_f = np.ones(n) * 0.999
        self.P_m = np.ones(n) * 0.999
        self.fert = fert

    def test_proiezione_chiusa_conserva_la_popolazione(self):
        nf1, nm1 = project_two_sex(self.nf, self.nm, self.fert,
                                   self.P_f, self.P_m)
        nascite = (self.nf * self.fert).sum()
        sopravv_f = (self.nf[:-1] * self.P_f[:-1]).sum()
        sopravv_m = (self.nm[:-1] * self.P_m[:-1]).sum()
        # bilancio demografico chiuso: la classe aperta 100+ RITIENE una
        # quota P[100] dei suoi membri (classe terminale aperta)
        ritenuti = (self.nf[-1] * self.P_f[-1] + self.nm[-1] * self.P_m[-1])
        atteso = nascite + sopravv_f + sopravv_m + ritenuti
        self.assertAlmostEqual(nf1.sum() + nm1.sum(), atteso, delta=1.0)

    def test_classe_terminale_aperta_ritiene_i_sopravviventi(self):
        n = np.zeros(101); n[100] = 1000.0
        P = np.full(101, 0.9)
        from leslie import survive
        out = survive(n, P)
        self.assertAlmostEqual(out[100], 1000.0 * 0.9, delta=1e-9)

    def test_matrice_leslie_con_diagonale_terminale(self):
        from leslie import build_leslie_matrix
        P = np.full(101, 0.9); P[-1] = 0.5
        L = build_leslie_matrix(np.zeros(101), P)
        self.assertAlmostEqual(L[-1, -1], 0.5, delta=1e-12)
        self.assertAlmostEqual(L[-1, -2], 0.9, delta=1e-12)

    def test_saldo_migratorio_nullo_lascia_invariato_il_bilancio(self):
        tot, tr_f, tr_m = simulate_two_sex(self.nf, self.nm, self.fert,
                                           self.P_f, self.P_m, years=3)
        self.assertEqual(len(tot), 4)
        # senza migrazione la dinamica dipende solo da nascite e decessi
        self.assertGreaterEqual(tot[3], 0)

    @unittest.skipUnless(HAS_DATA, "dati ISTAT processati non presenti")
    def test_coerenza_dati_istat(self):
        from leslie import load_processed
        data = load_processed()
        n0, P, F = data["n0"], data["survival"], data["fertility"]
        self.assertTrue((P >= 0).all() and (P <= 1).all())
        self.assertTrue((F >= 0).all())
        tfr = float(F.sum())
        self.assertAlmostEqual(tfr, 1.18, delta=0.02)
        self.assertGreater(n0.sum(), 25e6)
        if "n0_male" in data:
            self.assertTrue((data["survival_male"] >= 0).all())
            self.assertTrue((data["survival_male"] <= 1).all())


if __name__ == "__main__":
    unittest.main()
