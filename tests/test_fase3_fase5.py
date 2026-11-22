import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from download_eurostat import js_to_tidy
from economia_collegata import indici_economici
from panel_screening import (
    FEATURES,
    prepare_features,
    screen,
    two_way_demean,
)


def synthetic_panel() -> pd.DataFrame:
    geos = ["ITC1", "ITC2", "ITF1", "FR10", "DE21"]
    rows = []
    rng = np.random.default_rng(7)
    for g in geos:
        base_tfr = 1.2 if g.startswith("IT") else 1.8
        base_gdp = 25_000.0 if g.startswith("IT") else 40_000.0
        for anno in range(2013, 2024):
            rows.append({
                "geo": g,
                "anno": anno,
                "tfr": base_tfr + 0.01 * (anno - 2013) + 0.05 * rng.standard_normal(),
                "gdp_pc": base_gdp * (1.01 ** (anno - 2013)) + 500 * rng.standard_normal(),
            })
    return pd.DataFrame(rows)


class TestJsToTidy(unittest.TestCase):
    def test_parsing_minimo(self):
        data = {
            "id": ["geo", "time"],
            "size": [2, 2],
            "value": {"0": 1.5, "3": 2.5},
            "dimension": {
                "geo": {"category": {"index": ["ITC1", "ITC2"],
                                     "label": {}}},
                "time": {"category": {"index": ["2020", "2021"],
                                       "label": {}}},
            },
        }
        tmp = ROOT / "data" / "raw" / "eurostat"
        tmp.mkdir(parents=True, exist_ok=True)
        p = tmp / "_test_fixture.json"
        p.write_text(json.dumps(data))
        df = js_to_tidy(p, "tfr")
        self.assertEqual(len(df), 2)
        self.assertAlmostEqual(df[df["anno"] == 2020]["tfr"].iloc[0], 1.5)
        self.assertAlmostEqual(df[df["anno"] == 2021]["tfr"].iloc[0], 2.5)
        p.unlink()


class TestPanelScreening(unittest.TestCase):
    def test_prepare_features(self):
        df = prepare_features(synthetic_panel())
        self.assertTrue((df["tfr_lag1"].notna()).all())
        self.assertGreater(df["gdp_growth"].iloc[0], -1)

    def test_two_way_demean(self):
        df = prepare_features(synthetic_panel())
        d = two_way_demean(df, ["tfr"])
        self.assertAlmostEqual(d["tfr"].mean(), 0.0, places=8)
        self.assertAlmostEqual(d.groupby("geo")["tfr"].mean().abs().max(), 0.0, places=8)
        self.assertAlmostEqual(d.groupby("anno")["tfr"].mean().abs().max(), 0.0, places=8)

    def test_screen_sintetico(self):
        res = screen(synthetic_panel(), within=False)
        self.assertIn("shap_importance", res)
        for f in FEATURES:
            self.assertIn(f, res["shap_importance"])
        top = list(res["shap_importance"])[0]
        self.assertEqual(top, "tfr_lag1")
        self.assertEqual(res["n_regioni"], 5)


class TestIndiciEconomici(unittest.TestCase):
    def test_indici(self):
        ages = np.zeros((2, 101))
        ages[0, 10] = 500.0
        ages[0, 40] = 1000.0
        ages[0, 70] = 300.0
        ind = indici_economici(ages)
        self.assertAlmostEqual(ind["attivi_15_64"][0], 1000.0)
        self.assertAlmostEqual(ind["anziani_65piu"][0], 300.0)
        self.assertAlmostEqual(ind["giovani_0_14"][0], 500.0)
        self.assertAlmostEqual(ind["dependency_ratio_anziani"][0], 0.3)
        self.assertAlmostEqual(ind["dependency_ratio_giovani"][0], 0.5)
        self.assertAlmostEqual(ind["scolastici_0_17"][0], 500.0)


if __name__ == "__main__":
    unittest.main()
