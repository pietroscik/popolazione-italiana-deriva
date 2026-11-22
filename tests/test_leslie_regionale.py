"""Test della Leslie regionale (src/leslie_regionale.py)."""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from leslie_regionale import (  # noqa: E402
    RIPARTIZIONI_PROVINCE,
    SARDEGNA,
    area_report,
    load_raw,
    n0_by_group,
    survival_by_group,
    valida_mapping,
)

HAS_DATA = (ROOT / "data" / "raw" / "POSAS_2026_it_Province.csv").exists()
TVM = ROOT / "data" / "raw" / "datiprovincialicompleti2024.csv"


class TestMapping(unittest.TestCase):
    def test_tutte_le_107_province_assegnate_una_volta(self):
        totale = [p for lst in RIPARTIZIONI_PROVINCE.values() for p in lst]
        self.assertEqual(len(totale), 107)
        self.assertEqual(len(set(totale)), 107)

    @unittest.skipUnless(HAS_DATA, "dati POSAS non presenti")
    def test_somme_provinciali_riprendono_il_csv_ripartizioni(self):
        res = valida_mapping()
        self.assertTrue(res["ok"])


@unittest.skipUnless(HAS_DATA, "dati POSAS non presenti")
class TestArea(unittest.TestCase):
    def test_sopravvivenza_di_gruppo_valida_e_diversa(self):
        pop, _ = load_raw()
        p_no = survival_by_group(TVM, pop, RIPARTIZIONI_PROVINCE["1"])
        p_sud = survival_by_group(TVM, pop, RIPARTIZIONI_PROVINCE["4"])
        self.assertTrue(((p_no >= 0) & (p_no <= 1)).all())
        self.assertTrue(((p_sud >= 0) & (p_sud <= 1)).all())
        self.assertFalse(np.allclose(p_no, p_sud))

    def test_somms_popolazione_ripartizioni_uguale_nazionale(self):
        pop, _ = load_raw()
        tot = sum(n0_by_group(pop, v).sum() +
                  n0_by_group(pop, v, "maschi").sum()
                  for v in RIPARTIZIONI_PROVINCE.values())
        nazionale = float(pop["femmine"].sum() + pop["maschi"].sum())
        self.assertAlmostEqual(tot / nazionale, 1.0, delta=1e-6)

    def test_sardegna_sotto_tfr_085_declina_molto_piu_forte(self):
        anag = [("Nord-ovest", RIPARTIZIONI_PROVINCE["1"])]
        rep = area_report(anag, verbose=False)
        lam_no = rep["aree"][0]["lambda1"]
        rep_sar085 = area_report([("Sardegna (TFR 0,85)", SARDEGNA)],
                                 tfr_scale=0.85 / 1.18, verbose=False)
        rep_sarnaz = area_report([("Sardegna", SARDEGNA)], verbose=False)
        lam_sar085 = rep_sar085["aree"][0]["lambda1"]
        lam_sarnaz = rep_sarnaz["aree"][0]["lambda1"]
        self.assertLess(lam_sar085, lam_sarnaz)
        self.assertLess(lam_sar085, lam_no - 0.005)
        # t-mezzo asintotico sardo sotto TFR 0,85: ~26 anni vs 41,5
        self.assertLess(rep_sar085["aree"][0]["t_mezzo_asintotico"], 30.0)
        self.assertGreater(rep_sarnaz["aree"][0]["t_mezzo_asintotico"], 40.0)

    def test_claimants_ripartizioni_sommano_al_nazionale(self):
        anag = [(k, v) for k, v in RIPARTIZIONI_PROVINCE.items()]
        rep = area_report(anag, verbose=False)
        tot = sum(a["claimants_2056_mln"] for a in rep["aree"])
        # coerenza col capitolo 5 nazionale (1,69 M al 2056 in media MC)
        self.assertAlmostEqual(tot, 1.67, delta=0.15)


if __name__ == "__main__":
    unittest.main()
