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
    fit_pstr_iv2,
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




def panel_due_strumenti(gamma_dr=0.08, n_regioni=300, n_anni=11,
                       seed=17, rompi_t20=False):
    """DGP con DR endogena e due strumenti validi con pendenza regionale
    regione x tempo (identificazione forte sia nel primo stadio sia per
    la distinzione fra i due strumenti). Con rompi_t20=True il t-20 e'
    contaminato direttamente dall'errore corrente: J deve respingere.
    Nota: il DGP e' volutamente 'sporco' (dr_lag vs dr_t disallineati,
    u_i persistente): recupera il comportamento del test J, non la
    precisione puntuale di gamma (gia' coperta dal test monovariato)."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_regioni):
        prefisso = f"{chr(65 + (i // 20) % 26)}X"
        u = rng.standard_normal() * 0.02
        z15_0 = 0.30 + 0.002 * rng.standard_normal()
        z20_0 = 0.295 + 0.002 * rng.standard_normal()
        slope15 = 0.003 + 0.003 * rng.random()
        slope20 = 0.0025 + 0.003 * rng.random()
        F = max(0.8, 1.5 + u + 0.1 * rng.standard_normal())
        gdp = 25_000.0
        for t in range(n_anni):
            z15 = z15_0 + slope15 * t
            z20 = z20_0 + slope20 * t
            if rompi_t20:
                z20 = z20 + u + 0.001 * rng.standard_normal()   # contagio
            dr = z15 + u + 0.003 * rng.standard_normal()
            eps = 0.006 * rng.standard_normal()
            rows.append({"geo": f"{prefisso}{i % 20:02d}", "anno": 2013 + t,
                         "tfr": F, "gdp_pc": gdp, "dr": dr,
                         "dr_t15": z15, "dr_t20": z20})
            gdp *= np.exp(0.02 + 0.02 * rng.standard_normal())
            F = F + (-0.06 + 0.04 * F - 0.05 * F * _G(F, 4.0, 1.66)) \
                + gamma_dr * dr + u + eps
    return pd.DataFrame(rows)


class TestLagStrumenti(unittest.TestCase):
    def test_dr_t15_e_dr_t20_risalgono_a_15_e_20_anni_prima(self):
        """Regressione del bug double-shift: la vecchia add_dr_t15 fondava
        df(anno-15) con hist(storia+15), producendo di fatto DR(t-30)
        etichettata come t-15 (759/759 righe del panel v1.1.x). La
        strumentazione corretta deve mappare anno-15 e anno-20."""
        raw = Path("/workspace/github__pietroscik__popolazione-italiana-deriva"
                   "/data/processed/dr_storico_nuts2.csv")
        panel = Path("/workspace/github__pietroscik__popolazione-italiana-deriva"
                     "/data/processed/eurostat_panel.csv")
        if not (raw.exists() and panel.exists()):
            self.skipTest("panel Eurostat non presente")
        hist = pd.read_csv(raw)
        df = pd.read_csv(panel)
        n15 = n20 = 0
        for _, r in df.dropna(subset=["dr_t15"]).head(500).iterrows():
            h = hist[(hist.geo == r["geo"]) & (hist.anno == int(r["anno"]) - 15)]
            if len(h):
                n15 += 1
                self.assertAlmostEqual(float(h.iloc[0]["dr_hist"]),
                                       float(r["dr_t15"]), delta=1e-9)
        for _, r in df.dropna(subset=["dr_t20"]).head(500).iterrows():
            h = hist[(hist.geo == r["geo"]) & (hist.anno == int(r["anno"]) - 20)]
            if len(h):
                n20 += 1
                self.assertAlmostEqual(float(h.iloc[0]["dr_hist"]),
                                       float(r["dr_t20"]), delta=1e-9)
        # copertura verificabile su almeno 100 righe per strumento
        self.assertGreaterEqual(n15, 100)
        self.assertGreaterEqual(n20, 100)


class TestIV2HansenJ(unittest.TestCase):
    def test_due_strumenti_validi_hansen_j_non_respinge(self):
        df = prepare_panel(panel_due_strumenti())
        df = df.dropna(subset=["dr_t15", "dr_t20"]).reset_index(drop=True)
        iv2 = fit_pstr_iv2(df)
        # primi stadi forti (F congiunto) e strumenti congruenti: J passa
        self.assertGreater(iv2["first_stage_F"], 10.0)
        self.assertGreater(iv2["hansen_J_p"], 0.05)
    def test_strumento_incoerente_hansen_j_respinge(self):
        df = prepare_panel(panel_due_strumenti(rompi_t20=True, seed=5))
        df = df.dropna(subset=["dr_t15", "dr_t20"]).reset_index(drop=True)
        iv2 = fit_pstr_iv2(df)
        # il t-20 contaminato dall'eterogeneita' corrente e' incongruente
        # col t-15: il J (df=1) deve respingere la validita' congiunta
        self.assertLess(iv2["hansen_J_p"], 0.10)


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


class TestMundlakEBatteria(unittest.TestCase):
    def test_mundlak_assorbe_l_eterogeneita_e_theta_stabile(self):
        """DGP con alpha_i correlato con F_lag: il pooled ha bias sul
        coefficiente; il CRE/Mundlak lo assorbe (media-F significativa) e
        la theta resta identificata."""
        rng = np.random.default_rng(9)
        rows = []
        for i in range(120):
            alpha = 0.05 * rng.standard_normal()
            F = 1.5 + alpha + 0.1 * rng.standard_normal()
            gdp = 25_000.0
            pref = f"{chr(65 + (i // 20) % 26)}X"
            for t in range(11):
                rows.append({"geo": f"{pref}{i % 20:02d}", "anno": 2013 + t,
                             "tfr": F, "gdp_pc": gdp,
                             "dr": 0.30, "dr_t15": 0.30})
                gdp *= np.exp(0.02 + 0.02 * rng.standard_normal())
                F = F + alpha + (-0.06 + 0.04 * F
                                 - 0.05 * F * _G(F, 4.0, 1.66)) \
                    + 0.008 * rng.standard_normal()
        from pstr_trap import fit_pstr_mundlak, prepare_panel, theta_stability_battery
        df = prepare_panel(pd.DataFrame(rows))
        res = fit_pstr_mundlak(df)
        self.assertAlmostEqual(res["theta"], 1.66, delta=0.2)
        bat = theta_stability_battery(df)
        for k in ("senza_dr", "con_dr", "mundlak_cre", "kinked"):
            self.assertIn(k, bat)

    def test_su_dati_reali_media_F_assorbe_eterogeneita(self):
        from pstr_trap import fit_pstr_mundlak, prepare_panel
        raw = Path("/workspace/github__pietroscik__popolazione-italiana-deriva"
                   "/data/processed/eurostat_panel.csv")
        if not raw.exists():
            self.skipTest("panel Eurostat non presente")
        import pandas as pd
        df = prepare_panel(pd.read_csv(raw))
        res = fit_pstr_mundlak(df)
        self.assertGreater(abs(res["mundlak"]["media_F"]), 0.05)
        self.assertTrue(1.60 <= res["theta"] <= 1.80)


class TestThetaStrutturale(unittest.TestCase):
    def test_batteria_per_era_su_dati_reali(self):
        """Regressione docs/13 par. 5.7: nel regime corrente la soglia e'
        fragile (bassa tangenza, nessuna radice instabile nel punto),
        nell'era 2001-2012 la mappa ha tre radici con supporto alto."""
        panel = Path("/workspace/github__pietroscik__popolazione-italiana-deriva"
                     "/data/processed/eurostat_panel_1990.csv")
        if not panel.exists():
            self.skipTest("panel Eurostat esteso non presente")
        from pstr_trap import prepare_panel, theta_structural_battery
        df = prepare_panel(pd.read_csv(panel))
        res = theta_structural_battery(df, B=9)
        self.assertIn("2013-2024", res)
        self.assertIn("2001-2012", res)
        # tangenza del regime corrente: mappa <= 0.02 in F in [0.85;1.10]
        self.assertLess(res["2013-2024"]["map_abs_max_f_0.85_1.10"], 0.02)
        # era 2001-2012: struttura a tre radici con supporto della soglia
        self.assertEqual(len(res["2001-2012"]["radici_base"]), 3)
        self.assertGreater(res["2001-2012"]["supporto_soglia_pct"],
                           res["2013-2024"]["supporto_soglia_pct"])
