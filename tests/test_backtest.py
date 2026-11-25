"""Test della suite DM/Clark-West/CRPS del backtest (src/backtest_pstr.py)."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from backtest_pstr import (  # noqa: E402
    _G,
    cluster_t,
    crps_from_ensemble,
    diebold_mariano,
    predict_path_m2,
)


class TestClusterT(unittest.TestCase):
    def test_media_positiva_significativa(self):
        rng = np.random.default_rng(1)
        d = 0.05 + 0.01 * rng.standard_normal(500)
        groups = np.repeat(np.arange(50), 10)
        t, p = cluster_t(d, groups)
        self.assertGreater(t, 5.0)
        self.assertLess(p, 0.001)

    def test_rumore_puro_non_significativo(self):
        rng = np.random.default_rng(2)
        d = 0.01 * rng.standard_normal(500)
        groups = np.repeat(np.arange(50), 10)
        t, p = cluster_t(d, groups)
        self.assertGreater(p, 0.01)


class TestDMCW(unittest.TestCase):
    def _errs(self, e0, e2):
        n = len(e0)
        geo = [f"G{i % 25:02d}" for i in range(n)]
        anno = [2013 + (i % 12) for i in range(n)]
        df0 = pd.DataFrame({"geo": geo, "anno": anno, "err": e0})
        df2 = df0.copy(); df2["err"] = e2
        return df0, df2

    def test_dm_modello_alternato_perfetto(self):
        rng = np.random.default_rng(3)
        e0 = 0.1 * rng.standard_normal(300)
        df0, df2 = self._errs(e0, np.zeros(300))
        res = diebold_mariano(df0, df2)
        self.assertGreater(res["dm_t"], 1.0)
        self.assertLess(res["dm_p"], 0.1)

    def test_cw_correzione_positiva(self):
        """Clark-West: d = e1^2 - e2^2 + pi^2. Se il modello alternato e'\n        uguale al benchmark (e1 = e2) ma pi != 0 (stima extra non nulla),\n        il termine pi^2 rende il differenziale positivo: e' la correzione\n        che evita di penalizzare il modello nidificato per la varianza di\n        stima."""
        rng = np.random.default_rng(4)
        e = 0.1 * rng.standard_normal(300)
        pi = np.abs(0.05 * rng.standard_normal(300))
        d_cw = e ** 2 - (e ** 2 - pi ** 2)
        t, p = cluster_t(d_cw, np.repeat(np.arange(25), 12))
        self.assertGreater(t, 2.0)
        self.assertLess(p, 0.05)


class TestCRPS(unittest.TestCase):
    def test_ensemble_deterministico_uguale_osservato(self):
        obs = np.array([1.5])
        sims = np.full(50, 1.5)
        self.assertAlmostEqual(crps_from_ensemble(sims, obs), 0.0, delta=1e-9)

    def test_ensemble_sbiarato_penalizzato(self):
        obs = np.array([1.5])
        centrato = np.linspace(1.3, 1.7, 50)
        sbiara = np.linspace(3.0, 3.4, 50)
        self.assertLess(crps_from_ensemble(centrato, obs),
                        crps_from_ensemble(sbiara, obs))


class TestRicorsioneM2(unittest.TestCase):
    def test_ricorsione_riproduce_la_mappa(self):
        params = {"beta": np.array([-0.02, 0.01, -0.03, 0.2, 0.05]),
                  "k": 4.0, "theta": 1.6}
        exog = pd.DataFrame({"anno": [2013, 2014],
                              "d_log_gdp": [0.01, 0.02],
                              "dr_lag": [0.3, 0.31]})
        path = predict_path_m2(params, 1.5, exog)
        F1 = 1.5 + (-0.02 + 0.01 * 1.5
                    - 0.03 * 1.5 * _G(1.5, 4.0, 1.6)
                    + 0.2 * 0.01 + 0.05 * 0.3)
        self.assertAlmostEqual(path[0], F1, delta=1e-12)
        F2 = F1 + (-0.02 + 0.01 * F1
                   - 0.03 * F1 * _G(F1, 4.0, 1.6)
                   + 0.2 * 0.02 + 0.05 * 0.31)
        self.assertAlmostEqual(path[1], F2, delta=1e-12)


if __name__ == "__main__":
    unittest.main()


class TestWithinEra(unittest.TestCase):
    """Roadmap v1.2: backtest interamente dentro il regime post-2013."""

    def test_finestre_parametrizzate(self):
        from backtest_pstr import exog_by_region
        rows = []
        for geo in ("AX01", "BX01"):
            for anno in range(2018, 2024):
                rows.append({"geo": geo, "anno": anno,
                             "d_log_gdp": 0.01, "dr_lag": 0.3})
        df = pd.DataFrame(rows)
        ex = exog_by_region(df, 2020, 2022)
        for geo, g in ex.items():
            self.assertEqual(sorted(g["anno"]), [2020, 2021, 2022])

    def test_within_era_m2_batte_lo_statico(self):
        """Su dati reali (se presenti): train 2013-2019, test 2020-2024.
        Nel regime corrente il PSTR batte il benchmark statico (DM t>0);
        la dinamica lineare resta superiore al termine non-lineare (CW<0).
        Regressione del risultato documentato in docs/16 par. 6."""
        panel = Path("/workspace/github__pietroscik__popolazione-italiana-deriva"
                     "/data/processed/eurostat_panel_1990.csv")
        if not panel.exists():
            self.skipTest("panel Eurostat esteso non presente")
        from backtest_pstr import backtest_report
        rep = backtest_report(train_start=2013, train_end=2019,
                             test_start=2020, test_end=2024, boot_B=0,
                             verbose=False)
        self.assertEqual(rep["disegno"]["train"], "2013-2019")
        self.assertGreater(rep["dm_m2_vs_m0"]["dm_t"], 0.0)
        self.assertGreater(rep["dm_m1_vs_m0"]["dm_t"], 0.0)
        self.assertLess(rep["clark_west_m2_vs_m1"]["cw_t"], 0.0)
