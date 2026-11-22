"""Scarica il panel Europeo NUTS-2 (Eurostat) per la Fase 3.

Dataset:
- TFR regionale: demo_r_find2, indic_de=TOTFERRT
- PIL pro-capite: nama_10r_2gdp, unit=PPS_EU27_2020_HAB (PPS per abitante)

Output: data/raw/eurostat/{tfr,gdp}_nuts2.json (formato JSON-stat) e
data/processed/eurostat_panel.csv (tidy: geo, anno, tfr, gdp_pc).
"""

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
YEARS = range(2013, 2024)


def _fetch(code: str, params: dict, dest: Path, years=YEARS) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    times = "&".join(f"time={y}" for y in years)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{code}?format=JSON&lang=EN&{qs}&{times}"
    with urllib.request.urlopen(url, timeout=180) as resp:
        dest.write_bytes(resp.read())
    return dest


def js_to_tidy(path: Path, value_name: str) -> pd.DataFrame:
    """JSON-stat (2 dimensioni ordinate: geo, time / unit..) -> DataFrame tidy."""
    data = json.loads(path.read_text())
    dims = list(data["dimension"].keys())
    idx = data["id"] if "id" in data else dims
    size = data["size"]
    cat_index = {d: data["dimension"][d]["category"]["index"] for d in dims}
    cat_label = {d: data["dimension"][d]["category"]["label"] for d in dims}

    rows = []
    for flat_key, value in data["value"].items():
        pos = int(flat_key)
        coords = {}
        rem = pos
        for d, s in zip(reversed(idx), reversed(size)):
            coords[d] = rem % s
            rem //= s
        row = {
            "geo": list(cat_index["geo"])[coords["geo"]],
            "anno": int(list(cat_index["time"])[coords["time"]]),
            value_name: float(value),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def build_panel(raw_dir: Path | None = None,
                out_dir: Path | None = None) -> pd.DataFrame:
    raw = raw_dir or ROOT / "data" / "raw" / "eurostat"
    out = out_dir or ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)

    tfr_json = _fetch("demo_r_find2", {"indic_de": "TOTFERRT"},
                      raw / "tfr_nuts2.json")
    gdp_json = _fetch("nama_10r_2gdp", {"unit": "PPS_EU27_2020_HAB"},
                      raw / "gdp_nuts2.json")

    tfr = js_to_tidy(tfr_json, "tfr")
    gdp = js_to_tidy(gdp_json, "gdp_pc")

    df = tfr.merge(gdp, on=["geo", "anno"], how="inner")
    df = df[df["geo"].str.len() == 4]
    df = df.sort_values(["geo", "anno"]).reset_index(drop=True)
    df.to_csv(out / "eurostat_panel.csv", index=False)
    return df


if __name__ == "__main__":
    panel = build_panel()
    print(panel.describe())
    print("regioni NUTS-2:", panel["geo"].nunique(),
          "| anni:", panel["anno"].nunique())
