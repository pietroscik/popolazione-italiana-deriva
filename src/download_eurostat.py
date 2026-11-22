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
    pop_json = _fetch("demo_r_pjanaggr3", {"unit": "NR", "sex": "T"},
                      raw / "pop_eta_nuts2.json")

    tfr = js_to_tidy(tfr_json, "tfr")
    gdp = js_to_tidy(gdp_json, "gdp_pc")
    pop = js_to_tidy(pop_json, "pop")
    pop["age"] = [None] * len(pop)

    pop = _pop_to_age_columns(pop_json, pop)

    df = tfr.merge(gdp, on=["geo", "anno"], how="inner")
    df = df.merge(pop, on=["geo", "anno"], how="left")
    df = df[df["geo"].str.len() == 4]
    df["dr"] = df["pop_65piu"] / df["pop_15_64"]
    df = df.drop(columns=[c for c in ("pop", "pop_15_64", "pop_65piu")
                          if c in df.columns and c not in ("dr",)], errors="ignore")
    df = df.sort_values(["geo", "anno"]).reset_index(drop=True)
    df.to_csv(out / "eurostat_panel.csv", index=False)
    return df


def _pop_to_age_columns(pop_json: Path, pop: pd.DataFrame) -> pd.DataFrame:
    """demo_r_pjanaggr3 (age: TOTAL/Y_LT15/Y15-64/Y_GE65) -> colonne wide.
    Decodifica il flat-index JSON-stat secondo l'ordine reale di id/size."""
    data = json.loads(pop_json.read_text())
    dims = list(data["id"])
    size = list(data["size"])
    cats = {d_: list(data["dimension"][d_]["category"]["index"])
            for d_ in dims}

    def decode(pos):
        coords = {}
        rem = pos
        for d_, s in zip(reversed(dims), reversed(size)):
            coords[d_] = rem % s
            rem //= s
        return coords

    rows = {}
    for flat_key, value in data["value"].items():
        c = decode(int(flat_key))
        geo = cats["geo"][c["geo"]]
        anno = int(cats["time"][c["time"]])
        age = cats["age"][c["age"]]
        rows.setdefault((geo, anno), {})[age] = float(value)

    recs = [{"geo": k[0], "anno": k[1],
             "pop_15_64": v.get("Y15-64", np.nan),
             "pop_65piu": v.get("Y_GE65", np.nan)}
            for k, v in rows.items()]
    return pd.DataFrame(recs)


if __name__ == "__main__":
    panel = build_panel()
    print(panel.describe())
    print("regioni NUTS-2:", panel["geo"].nunique(),
          "| anni:", panel["anno"].nunique())
