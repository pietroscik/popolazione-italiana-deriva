"""Parser dei dati ISTAT Demo -> vettori nazionali per la matrice di Leslie.

Input attesi (prodotti da src/download_istat.py in data/raw/):
  - POSAS_<year>_it_Province.csv : popolazione per eta', sesso e provincia
  - datiprovincialicompleti<year>.csv : tavole di mortalita' provinciali (eta' singola)
  - asfr_<year>.json : tassi di fecondita' per eta' della madre (endpoint RPCCerca)

Output (data/processed/):
  - n0_female.npy : popolazione femminile per eta' 0..100 (somma province)
  - survival_probs.npy : P_x femminile nazionale (media provinciale pesata per popolazione)
  - fertility_rates.npy : ASFR nazionale per eta' 14..50, per donna (non per mille)
  - summary.json : statistiche di controllo
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

MAX_AGE = 100
ROOT = Path(__file__).resolve().parents[1]


def load_population(csv_path: Path | str, max_age: int = MAX_AGE) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=";", skiprows=1, encoding="utf-8-sig")
    df.columns = [c.strip().strip('"') for c in df.columns]
    df = df.rename(columns={
        "Codice provincia": "prov_code", "Codice ripartizione": "rip_code",
        "Età": "eta", "Totale maschi": "maschi", "Totale femmine": "femmine",
    })
    for code_col in ("prov_code", "rip_code"):
        if code_col in df.columns:
            df[code_col] = df[code_col].astype(str).str.strip('"')
    df["eta"] = pd.to_numeric(df["eta"], errors="coerce")
    df = df.dropna(subset=["eta"])
    df = df[df["eta"] <= max_age]
    df["eta"] = df["eta"].astype(int)
    for col in ("maschi", "femmine"):
        if df[col].dtype == object:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.strip('"').str.replace(",", "."),
                errors="coerce")
    return df.dropna(subset=["femmine", "maschi"])


def n0_from_population(pop: pd.DataFrame, max_age: int = MAX_AGE,
                       sex: str = "femmine") -> np.ndarray:
    grouped = pop.groupby("eta")[sex].sum()
    vec = np.zeros(max_age + 1)
    for age in range(max_age + 1):
        vec[age] = grouped.get(age, 0.0)
    return vec


def load_survival_probs(tvm_csv: Path | str, pop: pd.DataFrame,
                        max_age: int = MAX_AGE, sex: str = "femmine") -> np.ndarray:
    df = pd.read_csv(tvm_csv, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Sesso"] == {"femmine": "Femmine", "maschi": "Maschi"}[sex]].copy()
    df["prov_code"] = df["Cod. provincia"].astype(int).astype(str).str.zfill(3)
    df["eta"] = pd.to_numeric(df["Età"], errors="coerce")
    p_col = next(c for c in df.columns if "prospett" in c.lower())
    df["P"] = pd.to_numeric(df[p_col], errors="coerce")
    df = df.dropna(subset=["eta", "P"])
    df = df[df["eta"] <= max_age]

    weights = pop[["prov_code", "eta", sex]].copy()
    merged = df.merge(weights, on=["prov_code", "eta"], how="inner")
    num = (merged["P"] * merged[sex]).groupby(merged["eta"]).sum()
    den = merged.groupby("eta")[sex].sum()
    p_bar = num / den

    probs = np.zeros(max_age + 1)
    for age in range(max_age + 1):
        probs[age] = p_bar.get(age, 0.0).item() if age in p_bar.index else 0.0
    probs[max_age] = float(p_bar.get(max_age, 0.0))
    return np.clip(probs, 0.0, 1.0)


def load_fertility(asfr_json: Path | str, max_age: int = MAX_AGE) -> np.ndarray:
    with open(asfr_json, encoding="utf-8") as f:
        data = json.load(f)
    rows = [d for d in data["datatable"]["data"]
            if d["denominazione"] == "Italia" and d.get("asfr") not in (None, "N")]
    vec = np.zeros(max_age + 1)
    for d in rows:
        age = int(d["eta"])
        if age <= max_age:
            vec[age] = float(str(d["asfr"]).replace(",", ".")) / 1000.0
    return vec


def process_all(raw_dir: Path | None = None, out_dir: Path | None = None,
                verbose: bool = True) -> dict:
    raw = raw_dir or ROOT / "data" / "raw"
    out = out_dir or ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)

    pop_csv = next(raw.glob("POSAS_*_it_Province.csv"))
    pop = load_population(pop_csv)
    n0 = n0_from_population(pop, sex="femmine")
    n0_m = n0_from_population(pop, sex="maschi")

    tvm_csv = next(raw.glob("datiprovincialicompleti*.csv"))
    survival = load_survival_probs(tvm_csv, pop, sex="femmine")
    survival_m = load_survival_probs(tvm_csv, pop, sex="maschi")

    asfr_json = sorted(raw.glob("asfr_*.json"))[-1]
    fertility = load_fertility(asfr_json)

    np.save(out / "n0_female.npy", n0)
    np.save(out / "n0_male.npy", n0_m)
    np.save(out / "survival_probs.npy", survival)
    np.save(out / "survival_probs_male.npy", survival_m)
    np.save(out / "fertility_rates.npy", fertility)

    tfr = fertility.sum()
    eta_media = (fertility * np.arange(MAX_AGE + 1)).sum() / tfr if tfr > 0 else float("nan")
    summary = {
        "anno_popolazione": pop_csv.stem.split("_")[1],
        "popolazione_totale_femmine": float(n0.sum()),
        "popolazione_totale_maschi": float(n0_m.sum()),
        "popolazione_totale": float(n0.sum() + n0_m.sum()),
        "over_65_femmine_pct": float(n0[66:].sum() / n0.sum() * 100),
        "tfr_implicito": float(tfr),
        "eta_media_feconda": float(eta_media),
        "P_0": float(survival[0]),
        "P_30": float(survival[30]),
        "P_80": float(survival[80]),
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if verbose:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return {"n0": n0, "survival": survival, "fertility": fertility,
            "summary": summary}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from download_istat import fetch_all

    fetch_all()
    process_all()
