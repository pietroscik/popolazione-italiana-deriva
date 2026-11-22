"""Test della stima IV (strumento dr_t15) e della robustezza LOCO."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pstr_trap import (  # noqa: E402
    _G,
    fit_pstr,
    fit_pstr_iv,
    loco_by_country,
    prepare_panel,
)


def panel_endogeno(gamma_dr=0.08, n_regioni=120, n_anni=11, seed=11):
    """DGP in cui la DR e' endogena: effetto regione persistente u_i entra
    sia nella DR sia in dF. Lo strumento dr_t15 e' generato prima di u_i
    e quindi esogeno rispetto agli shock correnti."""
    rng = np.random.default_rng(seed)
    rows = []
    n_paesi = max(n_regioni // 20, 1)
    for i in range(n_regioni):
        # prefisso paese a 2 caratteri per il LOCO
        prefisso = f"{chr(65 + (i // 20) % 26)}X"
        u = rng.standard_normal() * 0.02          # eterogeneita' regione
        dr_t15 = 0.30 + 0.002 * rng.standard_normal()
        F = max(0.8, 1.5 + u + 0.1 * rng.standard_normal())
        dr = dr_t15 + u + 0.002 * rng.standard_normal()
        gdp = 25_000.0
        for t in range(n_anni):
            rows.append({"geo": f"{prefisso}{i % 20:02d}", "anno": 2013 + t,
                         "tfr": F, "gdp_pc": gdp, "dr": dr,
                         "dr_t15": dr_t15})
            gdp *= np.exp(0.02 + 0.02 * rng.standard_normal())
            F = F + (-0.06 + 0.04 * F - 0.05 * F * _G(F, 4.0, 1.66)) \
                + gamma_dr * dr + u + 0.008 * rng.standard_normal()
            dr = dr + 0.002 + 0.001 * rng.standard_normal()
    return pd.DataFrame(rows)


class TestIV(unittest.TestCase):
    def test_iv_recupera_gamma_meglio_dell_ols(self):
        df = prepare_panel(panel_endogeno())
        iv = fit_pstr_iv(df.dropna(subset=["dr_t15"]).reset_index(drop=True))
        ols = fit_pstr(df)
        # lo strumento e' forte
        self.assertGreater(iv["first_stage_F"], 10.0)
        # la DR strumentata riduce il bias verso l'alto dell'OLS
        self.assertLess(abs(iv["beta"][4] - 0.08),
                        abs(ols["beta"][4] - 0.08)
                        + 0.005)  # tolleranza: F_lag resta endogeno

    def test_loco_copre_paesi_e_stabilisce_range(self):
        df = prepare_panel(panel_endogeno(n_regioni=200, seed=3))
        res = loco_by_country(df)
        self.assertGreaterEqual(res["n_propri"], 1)
        self.assertLessEqual(res["theta_min"], res["theta_max"])
        self.assertLessEqual(res["gamma_DR_min"], res["gamma_DR_max"])


if __name__ == "__main__":
    unittest.main()
