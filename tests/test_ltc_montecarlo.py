"""Test del modello attuariale Monte Carlo LTC (src/ltc_montecarlo.py)."""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ltc_montecarlo import (  # noqa: E402
    COST_DOMICILIARE,
    COST_RESIDENZIALE_MG,
    SEVERITY_MIX,
    SEX_MULTIPLIER,
    annual_cost_mc,
    blended_unit_costs,
    prevalence_by_age_sex,
    scenari_longevita,
)

HAS_DATA = (ROOT / "data" / "processed" / "n0_female.npy").exists()


class TestSeverita(unittest.TestCase):
    def test_blended_riprega_i_costi_del_capitolo_2(self):
        dom, res = blended_unit_costs()
        self.assertAlmostEqual(dom, 15_000.0, delta=1_000.0)
        self.assertAlmostEqual(res, 48_000.0, delta=1_000.0)

    def test_mix_somma_a_uno_e_costi_ordine_grave(self):
        self.assertAlmostEqual(SEVERITY_MIX.sum(), 1.0)
        self.assertTrue((np.diff(COST_DOMICILIARE) > 0).all())
        self.assertGreater(COST_RESIDENZIALE_MG[1], COST_RESIDENZIALE_MG[0])


class TestPrevalenzaSesso(unittest.TestCase):
    def test_sopra_65_le_donne_hanno_prevalenza_superiore(self):
        pf = prevalence_by_age_sex("F")[70]
        pm = prevalence_by_age_sex("M")[70]
        self.assertGreater(pf, pm)
        self.assertAlmostEqual(pm, 0.03 * SEX_MULTIPLIER["M"], delta=1e-12)

    def test_sotto_65_i_sessi_oscillano_uguale(self):
        pf = prevalence_by_age_sex("F")[:65]
        pm = prevalence_by_age_sex("M")[:65]
        self.assertTrue((pf == pm).all())


class TestCostoAnnuo(unittest.TestCase):
    def test_caso_centrale_uguale_al_capitolo_2(self):
        """Con mix, costi e calibrazione ai valori centrali, il costo annuo
        per claimant deve coincidere col capitolo 2 (~15k*0.65 + 48k*0.35
        in forma informale ~ al 100%) dentro la tolleranza del blending."""
        claimants = np.array([1_000.0])
        ratio = np.array([14.0])
        got = annual_cost_mc(claimants, ratio, SEVERITY_MIX,
                             COST_DOMICILIARE, COST_RESIDENZIALE_MG,
                             0.65, 11.0, 2.0)
        dom, res = blended_unit_costs()
        informal = 1.0 / (1.0 + np.exp(-(14.0 - 11.0) / 2.0))
        atteso = (claimants * (1 - informal)
                  * (0.65 * dom + 0.35 * res))
        self.assertAlmostEqual(float(got[0]), float(atteso[0]), delta=1.0)


@unittest.skipUnless(HAS_DATA, "dati ISTAT processati non presenti")
class TestScenariLongevita(unittest.TestCase):
    def test_rho_piu_alto_piu_claimants_a_fine_orizzonte(self):
        out = scenari_longevita(rhos=(0.0, 0.01), verbose=False)
        self.assertGreater(out["rho_0.010"]["claimants_fine_mln"],
                           out["rho_0.000"]["claimants_fine_mln"])


if __name__ == "__main__":
    unittest.main()
