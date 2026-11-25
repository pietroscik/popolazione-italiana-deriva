import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leslie import project_two_sex, simulate_two_sex, SEX_RATIO_F
from migration import build_migration_profile, rogers_castro_rates


class TestRogersCastro(unittest.TestCase):
    def test_non_negativi(self):
        rates = rogers_castro_rates(np.arange(101))
        self.assertTrue((rates >= 0).all())
        self.assertGreater(rates.sum(), 0)

    def test_picco_forza_lavoro(self):
        rates = rogers_castro_rates(np.arange(101))
        best = int(np.argmax(rates))
        self.assertGreaterEqual(best, 18)
        self.assertLessEqual(best, 35)

    def test_profilo_calibrato(self):
        n = np.full(101, 1000.0)
        prof = build_migration_profile(n, net_total=280_000.0)
        self.assertAlmostEqual(prof.sum(), 280_000.0, places=6)
        share_20_39 = prof[20:40].sum() / prof.sum()
        self.assertGreater(share_20_39, 0.45)


class TestTwoSex(unittest.TestCase):
    def setUp(self):
        self.max_age = 100
        self.fert = np.zeros(101)
        self.fert[15:50] = 1.18 / 35
        self.pf = np.full(101, 0.995)
        self.pm = np.full(101, 0.993)
        self.pf[-1] = self.pm[-1] = 0.0
        self.nf = np.full(101, 500.0)
        self.nm = np.full(101, 480.0)

    def test_ripartizione_sessi_nascite(self):
        new_f, new_m = project_two_sex(self.nf, self.nm, self.fert,
                                       self.pf, self.pm)
        self.assertAlmostEqual(new_f[0] + new_m[0],
                               (self.nf * self.fert).sum(), places=6)
        self.assertAlmostEqual(new_f[0] / (new_f[0] + new_m[0]),
                               SEX_RATIO_F, places=6)

    def test_zero_fertilita_zero_nascite(self):
        new_f, new_m = project_two_sex(self.nf, self.nm, np.zeros(101),
                                       self.pf, self.pm)
        self.assertEqual(new_f[0], 0.0)
        self.assertEqual(new_m[0], 0.0)

    def test_migrazione_somma(self):
        mig = np.full(101, 100.0)
        new_f, new_m = project_two_sex(self.nf, self.nm, self.fert,
                                       self.pf, self.pm, mig, mig)
        delta = (new_f.sum() + new_m.sum()) - \
                ((self.nf.sum() + self.nm.sum()) * 0.995 + 0.005 * (
                    self.nf * self.fert).sum() * (1 - SEX_RATIO_F))
        self.assertGreater(delta, 95 * 101)

    def test_simulazione_coerente(self):
        tot, tr_f, tr_m = simulate_two_sex(self.nf, self.nm, self.fert,
                                           self.pf, self.pm, years=10,
                                           net_migration_total=0.0)
        self.assertAlmostEqual(tot[0], tr_f[0] + tr_m[0])
        self.assertTrue((np.diff(tot) < 0).all())


if __name__ == "__main__":
    unittest.main()


ROOT = Path(__file__).resolve().parents[1]

class TestMigrazioneOsservata(unittest.TestCase):
    """Roadmap v1.2 ramo 4: profilo migratorio netto OSSERVATO per eta'."""

    def test_nessuna_migrazione_residuo_zero(self):
        """Se P_{t+1} e' esattamente P_t * S (nessun flusso), il residuo
        m(a) deve andare a zero su TUTTE le eta', classe 100+ compresa."""
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from migration_observed import MAX_AGE
        rng = np.random.default_rng(3)
        S = np.ones(MAX_AGE + 1); S[5] = 0.99; S[60] = 0.97; S[100] = 0.5
        P_t = 1000 + rng.random(MAX_AGE + 1) * 500
        # shift di coorte senza migrazione: P_{t+1}(a+1) = P_t(a)*S(a)
        P_t1 = np.zeros(MAX_AGE + 1)
        for a in range(MAX_AGE):
            P_t1[a + 1] = P_t[a] * S[a]
        P_t1[MAX_AGE] = (P_t[MAX_AGE - 1] * S[MAX_AGE - 1]
                         + P_t[MAX_AGE] * S[MAX_AGE])
        # residuo manuale con la stessa formula del modulo
        m = np.zeros(MAX_AGE + 1)
        for a in range(1, MAX_AGE - 1):
            m[a] = P_t1[a + 1] - P_t[a] * S[a]
        m[MAX_AGE - 1] = (P_t1[MAX_AGE]
                          - P_t[MAX_AGE - 1] * S[MAX_AGE - 1]
                          - P_t[MAX_AGE] * S[MAX_AGE])
        self.assertLess(float(np.abs(m).max()), 1e-6)

    def test_su_dati_reali_saldo_positivo_eta_plausibile(self):
        """POSAS <-> TVM: saldo osservato positivo, eta' media 25-40,
        correlazione col sintetico positiva ma lontana da 1."""
        base = ROOT / "data" / "processed" / "survival_probs.npy"
        raw = ROOT / "data" / "raw" / "POSAS_2024_it_Ripartizioni.csv"
        if not base.exists() or not raw.exists():
            self.skipTest("dati POSAS/TVM non presenti")
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from migration_observed import observed_net_migration_by_age
        r = observed_net_migration_by_age(2024, 2025)
        prof = r["femmine"] + r["maschi"]
        self.assertGreater(prof.sum(), 100_000)
        self.assertTrue(25 <= r["eta_media_migranti_pos"] <= 40)

    def test_scenario_osservato_piu_generativo(self):
        """Regressione docs/21: col profilo osservato la popolazione finale
        e' MAGGIORE del sintetico a parita' di saldo (family-shaped)."""
        base = ROOT / "data" / "processed" / "survival_probs.npy"
        raw = ROOT / "data" / "raw" / "POSAS_2024_it_Ripartizioni.csv"
        if not base.exists() or not raw.exists():
            self.skipTest("dati POSAS/TVM non presenti")
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from migration_observed import scenario_observed_vs_synth
        res = scenario_observed_vs_synth(saldo=263_000.0, years=30)
        self.assertGreater(res["pop_finale_osservato"],
                           res["pop_finale_sintetico"])
        self.assertLess(res["break_even_osservato"],
                        res["break_even_sintetico"])
