"""Test di Lotka integrale esatto e della sensitivity sistematica."""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lotka import lotka_r_exact, net_reproduction, survival_to_age  # noqa: E402

HAS_DATA = (ROOT / "data" / "processed" / "n0_female.npy").exists()


class TestLotkaSintetico(unittest.TestCase):
    def setUp(self):
        # popolazione stazionaria per 100 anni con fecondita' uniforme 25-35
        self.p = np.full(100, 0.99)
        self.f = np.zeros(101)
        self.f[25:36] = 0.05

    def test_survival_to_age_e_prodotto_condizionato(self):
        l = survival_to_age(self.p)
        self.assertEqual(l[0], 1.0)
        self.assertAlmostEqual(l[10], 0.99 ** 10, delta=1e-12)

    def test_r0_corrisponde_a_tfr_per_s_f(self):
        r0, T = net_reproduction(self.f, self.p)
        # somma asfr = 0.55; tasso di sopravvivenza medio alla fascia 25-35
        self.assertAlmostEqual(r0, 0.55 * 0.488 * float(np.mean(
            survival_to_age(self.p)[25:36])), delta=1e-9)
        self.assertTrue(25.0 <= T <= 36.0)

    def test_equazione_caratteristica_ha_radice(self):
        r = lotka_r_exact(self.f, self.p)
        self.assertTrue(np.isfinite(r))
        # R0 ~ 0.17 con queste asfr: la popolazione contrae (r < 0)
        self.assertLess(r, 0.0)
        # con fecondita' sufficiente (TFR ~ 3.3) la radice e' positiva
        f_hi = np.zeros(101)
        f_hi[25:36] = 0.30
        self.assertGreater(lotka_r_exact(f_hi, self.p), 0.0)

    def test_asfr_nulle_nessuna_radice(self):
        f0 = np.zeros(101)
        self.assertTrue(np.isnan(lotka_r_exact(f0, self.p)))


@unittest.skipUnless(HAS_DATA, "dati ISTAT processati non presenti")
class TestLotkaDatiReali(unittest.TestCase):
    def test_r_lotka_esatto_uguale_ln_lambda1(self):
        from leslie import build_leslie_matrix, dominant_eigen, load_processed
        data = load_processed()
        lam, _ = dominant_eigen(build_leslie_matrix(
            data["fertility"], data["survival"]))
        r_exact = lotka_r_exact(data["fertility"], data["survival"])
        self.assertAlmostEqual(r_exact, float(np.log(lam)), delta=1e-6)

    def test_r0_tra_quattro_e_sette_decimi(self):
        from leslie import load_processed
        data = load_processed()
        r0, _ = net_reproduction(data["fertility"], data["survival"])
        self.assertTrue(0.4 < r0 < 0.7)

    def test_r_approssimato_dentro_il_dieci_percento(self):
        from leslie import load_processed
        data = load_processed()
        r0, T = net_reproduction(data["fertility"], data["survival"])
        r_app = np.log(r0) / T
        r_exact = lotka_r_exact(data["fertility"], data["survival"])
        self.assertLess(abs(r_app - r_exact) / abs(r_exact), 0.10)


@unittest.skipUnless(HAS_DATA, "dati ISTAT processati non presenti")
class TestSensitivity(unittest.TestCase):
    def test_elasticita_ordine_dei_driver(self):
        from sensitivity import costo_2056
        base = costo_2056()
        # la prevalenza e' il driver dominante e sovra-lineare
        c_hi = costo_2056(prevalence_mult=1.20)
        self.assertGreater(c_hi / base - 1.0, 0.20 * 1.5)
        # il costo unitario domiciliare entra in modo lineare attenuato
        c_dom = costo_2056(unit_dom=18_000.0)
        self.assertAlmostEqual((c_dom / base - 1.0) / 0.20, 0.37, delta=0.05)

    def test_quota_domiciliare_negativa_sul_costo(self):
        from sensitivity import costo_2056
        base = costo_2056()
        c = costo_2056(share_dom=0.715)
        self.assertLess(c, base)

    def test_ltc_e_ltc_montecarlo_condividono_il_caso_centrale(self):
        from sensitivity import costo_2056
        # il caso centrale della sensitivity (prezzi 2026, 2056) riprende
        # il cap. 2 entro l'errore di arrotondamento demografico
        self.assertAlmostEqual(costo_2056(), 31.0, delta=2.0)


if __name__ == "__main__":
    unittest.main()
