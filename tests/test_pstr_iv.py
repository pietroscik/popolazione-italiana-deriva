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


class TestPanelSbilanciato(unittest.TestCase):
    def test_buco_temporale_non_produce_diff_misti(self):
        rows = []
        for geo in ("AX01", "BX01"):
            for t, tfr in ((2001, 1.4), (2002, 1.3), (2003, 1.2),
                           (2004, 1.1),
                           # 2005 mancante: gap di un anno
                           (2006, 1.0)):
                rows.append({"geo": geo, "anno": t, "tfr": tfr,
                             "gdp_pc": 20_000.0 * 1.01 ** t, "dr": 0.3})
        df = prepare_panel(pd.DataFrame(rows))
        # la riga 2006 (dopo il buco) non deve produrre un diff 2-ennale
        self.assertNotIn(2006, df["anno"].unique())
        # le righe con anni consecutivi restano utilizzabili
        # (2002 e' scartata per il doppio lag del PIL: serve il PIL del 2000)
        self.assertEqual(sorted(df["anno"].unique()), [2003, 2004])
        # i d_tfr corrispondono a orizzonte annuo
        self.assertAlmostEqual(
            float(df[df.anno == 2004]["d_tfr"].iloc[0]), -0.1, delta=1e-9)


class TestKinked(unittest.TestCase):
    def test_recupera_dr0_vero_e_gamma_della_forma_kinked(self):
        """DGP con freno kinked VERO oltre DR0=0.30 (DR su entrambi i lati):
        la griglia profilata deve recuperare DR0 e il gamma negativo
        (segno del freno, come DGP -0.15*max(0, DR-DR0))."""
        from pstr_trap import fit_pstr_kinked
        rng = np.random.default_rng(21)
        rows = []
        for i in range(200):
            dr_t15 = 0.20 + 0.25 * rng.random()
            F = 1.5 + 0.1 * rng.standard_normal()
            gdp = 25_000.0
            pref = f"{chr(65 + (i // 20) % 26)}X"
            for t in range(12):
                rows.append({"geo": f"{pref}{i % 20:02d}",
                             "anno": 2012 + t, "tfr": F, "gdp_pc": gdp,
                             "dr": dr_t15, "dr_t15": dr_t15})
                gdp *= np.exp(0.02 + 0.02 * rng.standard_normal())
                kink = 0.15 * max(0.0, dr_t15 - 0.30)
                F = F + (-0.06 + 0.04 * F - 0.05 * F * _G(F, 4.0, 1.66)) \
                    - kink + 0.005 * rng.standard_normal()
        df = prepare_panel(pd.DataFrame(rows))
        res = fit_pstr_kinked(
            df, dr0_grid=np.round(np.arange(0.15, 0.46, 0.03), 2))
        self.assertAlmostEqual(res["dr0"], 0.30, delta=0.03)
        self.assertAlmostEqual(res["gamma_kinked"], -0.15, delta=0.05)
