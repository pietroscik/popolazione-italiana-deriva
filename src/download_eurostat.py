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
    df = add_dr_t15(df, raw, out)
    df = df.sort_values(["geo", "anno"]).reset_index(drop=True)
    df.to_csv(out / "eurostat_panel.csv", index=False)
    return df

AGE_15_64 = ("Y15-19", "Y20-24", "Y25-29", "Y30-34", "Y35-39", "Y40-44",
             "Y45-49", "Y50-54", "Y55-59", "Y60-64")
AGE_65_PIU = ("Y65-69", "Y70-74", "Y75-79", "Y80-84", "Y85-89",
              "Y_GE75", "Y_GE80", "Y_GE85", "Y_GE90")


def build_dr_history(raw_dir: Path | None = None,
                     out_dir: Path | None = None) -> pd.DataFrame:
    """DR regionale storico (1990-2024) da demo_r_pjangroup.

    Le codemap delle fasce 65+ cambiano con la classe d'eta' dei vintaggi
    Eurostat (bande fini o aggregati Y_GE75/Y_GE80): si sommano le sole
    bande 65+ presenti per ciascun (geo, anno), accettando solo i codemap
    completi (10 bande 15-64 e codemap 65+ con tutti i valori)."""
    raw = raw_dir or ROOT / "data" / "raw" / "eurostat"
    out = out_dir or ROOT / "data" / "processed"
    raw.mkdir(parents=True, exist_ok=True)
    dest = raw / "pop_eta_storico_nuts2.json"
    if not dest.exists():
        url = f"{BASE}/demo_r_pjangroup?format=JSON&lang=EN&unit=NR&sex=T"
        with urllib.request.urlopen(url, timeout=300) as resp:
            dest.write_bytes(resp.read())

    data = json.loads(dest.read_text())
    dims = list(data["id"])
    size = list(data["size"])
    cats = {d_: list(data["dimension"][d_]["category"]["index"])
            for d_ in dims if d_ in ("age", "geo", "time")}

    acc_w, acc_o = {}, {}
    n15, n65 = {}, {}
    for flat_key, value in data["value"].items():
        rem = int(flat_key)
        coords = {}
        for d_, s in zip(reversed(dims), reversed(size)):
            coords[d_] = rem % s
            rem //= s
        geo = cats["geo"][coords["geo"]]
        if len(geo) != 4:
            continue
        anno = int(cats["time"][coords["time"]])
        age = cats["age"][coords["age"]]
        key = (geo, anno)
        if age in AGE_15_64:
            acc_w[key] = acc_w.get(key, 0.0) + float(value)
            n15[key] = n15.get(key, 0) + 1
        elif age in AGE_65_PIU:
            acc_o[key] = acc_o.get(key, 0.0) + float(value)
            n65[key] = n65.get(key, 0) + 1

    recs = []
    for key, work in acc_w.items():
        if n15[key] != len(AGE_15_64):
            continue
        old = acc_o.get(key)
        if not old or n65.get(key, 0) < 3:
            continue
        recs.append({"geo": key[0], "anno": key[1],
                     "pop_15_64": work, "pop_65piu": old,
                     "dr_hist": old / work})
    hist = pd.DataFrame(recs).sort_values(["geo", "anno"]).reset_index(drop=True)
    out.mkdir(parents=True, exist_ok=True)
    hist.to_csv(out / "dr_storico_nuts2.csv", index=False)
    return hist


def add_dr_t15(df: pd.DataFrame, raw_dir: Path | None = None,
               out_dir: Path | None = None) -> pd.DataFrame:
    """Strumento per la DR endogena: DR regionale osservata 15 anni prima.

    La DR di oggi e' costruita dalle nascite di 15-65 anni orsono, quindi e'
    meccanicamente correlata con la fertilita' storica della regione e con gli
    errori dell'equazione del TFR. La DR a t-15 e' predeterminata rispetto
    agli shock recenti del TFR (protocollo docs/06, appendice B)."""
    hist = build_dr_history(raw_dir, out_dir)
    hist = hist.rename(columns={"anno": "anno_strumento", "dr_hist": "dr_t15"})
    hist["anno_strumento"] = hist["anno_strumento"] + 15
    df = df.copy()
    df["anno_strumento"] = df["anno"] - 15
    df = df.merge(hist[["geo", "anno_strumento", "dr_t15"]],
                  on=["geo", "anno_strumento"], how="left")
    return df.drop(columns=["anno_strumento"])


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
