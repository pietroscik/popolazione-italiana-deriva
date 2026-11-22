import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pstr_trap import (
    _G,
    equilibrium_points,
    fit_pstr,
    implied_map,
    prepare_panel,
)


def panel_sintetico(a=-0.081, b0=0.085, b1=-0.087, k=3.7, theta=1.66,
                    noise=0.03, n_regioni=200, n_anni=14, seed=3):
    """DGP con transizione logistica vera: dF = a + b0 F + b1 F G(F;k,theta) + eps.
    Nota: il regressore F_lag e' correlato con gli errori passati (feedback
    dinamico), quindi lo stimatore OLS concentrato soffre del classico bias
    dei panel dinamici (Nickell): i test verificano il recupero entro
    tolleranze che lo includono."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_regioni):
        F = rng.uniform(0.9, 2.6)
        gdp = 25_000.0
        for t in range(n_anni):
            rows.append({"geo": f"R{i:04d}", "anno": 2013 + t,
                         "tfr": F, "gdp_pc": gdp})
            gdp *= np.exp(0.02 + 0.02 * rng.standard_normal())
            F = F + a + b0 * F + b1 * F * _G(F, k, theta) + \
                noise * rng.standard_normal()
    return pd.DataFrame(rows)


class TestFitPstr(unittest.TestCase):
    def test_recupero_parametri_su_processo_noto(self):
        df = prepare_panel(panel_sintetico())
        res = fit_pstr(df)
        self.assertAlmostEqual(res["theta"], 1.66, delta=0.15)
        self.assertAlmostEqual(res["k"], 3.7, delta=1.5)
        self.assertAlmostEqual(res["beta"][0], -0.081, delta=0.04)
        self.assertAlmostEqual(res["beta"][2], -0.087, delta=0.04)
        roots = equilibrium_points(res)
        tipi = [t for _, t in roots]
        self.assertIn("instabile", tipi)
        self.assertIn("stabile", tipi)
        instabile = min(f for f, t in roots if t == "instabile")
        stabile = max(f for f, t in roots if t == "stabile")
        self.assertAlmostEqual(instabile, 1.05, delta=0.2)
        self.assertAlmostEqual(stabile, 1.51, delta=0.15)

    def test_senza_transizione_k_basso_vince(self):
        df = prepare_panel(panel_sintetico(b1=0.0))
        res = fit_pstr(df)
        self.assertAlmostEqual(res["beta"][2], 0.0, delta=0.02)


class TestEquilibri(unittest.TestCase):
    def test_radici_noto(self):
        best = {"k": 3.7, "theta": 1.66,
                "beta": [-0.081, 0.085, -0.087, 0.0]}
        roots = equilibrium_points(best)
        tipi = [t for _, t in roots]
        self.assertIn("stabile", tipi)
        self.assertIn("instabile", tipi)
        instabile = min(f for f, t in roots if t == "instabile")
        stabile = max(f for f, t in roots if t == "stabile")
        self.assertAlmostEqual(instabile, 1.05, delta=0.05)
        self.assertAlmostEqual(stabile, 1.51, delta=0.05)

    def test_mappa_negativa_nessuna_radice(self):
        best = {"k": 3.7, "theta": 1.66,
                "beta": [-0.3, 0.09, -0.087, 0.0]}
        Fg, f = implied_map(best)
        self.assertTrue((f < 0).all())
        self.assertEqual(equilibrium_points(best), [])


if __name__ == "__main__":
    unittest.main()
