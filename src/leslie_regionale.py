"""Leslie regionale per ripartizione geografica + spotlight Sardegna.

Ambizione dichiarata in docs/06 §5 (coupling Leslie regionale) e docs/14/15:
la catena fino ad ora e' nazionale. Qui la Leslie due sessi viene
regionalizzata per le 5 ripartizioni ISTAT:

- n0 per ripartizione da POSAS_2026_it_Ripartizioni.csv (vettori ufficiali)
- sopravvivenza per ripartizione = media delle tavole provinciali complete
  (TVM 2024) pesata per la popolazione provinciale di ciascun sesso, --
  stessa logica della media nazionale, ristretta alle province del gruppo
- fecondita': ASFR nazionale (limitazione dichiarata: le ASFR per
  ripartizione non sono nel formato del parser; si usa `tfr_scale` per gli
  scenari di livello, come per la Sardegna)

Validazione del mapping: la somma delle popolazioni provinciali per gruppo
riprende i totali del CSV Ripartizioni entro lo 0,5% (test automatico).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MAX_AGE = 100

# Provincia (codice ISTAT a 3 cifre) -> ripartizione (1 NO, 2 NE, 3 C, 4 S, 5 Isole)
RIPARTIZIONI_PROVINCE = {
    "1": ["001", "002", "003", "004", "005", "006", "007", "008", "009",
          "010", "011", "012", "013", "014", "015", "016", "017", "018",
          "019", "020", "096", "097", "098", "103", "108"],
    "2": ["021", "022", "023", "024", "025", "026", "027", "028", "029",
          "030", "031", "032", "033", "034", "035", "036", "037", "038",
          "039", "040", "093", "099"],
    "3": ["041", "042", "043", "044", "045", "046", "047", "048", "049",
          "050", "051", "052", "053", "054", "055", "056", "057", "058",
          "059", "060", "100", "109"],
    "4": ["061", "062", "063", "064", "065", "066", "067", "068", "069",
          "070", "071", "072", "073", "074", "075", "076", "077", "078",
          "079", "080", "094", "101", "102", "110"],
    "5": ["081", "082", "083", "084", "085", "086", "087", "088", "089",
          "090", "091", "092", "095", "111"],
}
SARDEGNA = ["090", "091", "092", "095", "111"]
RIPARTIZIONI_NOMI = {"1": "Nord-ovest", "2": "Nord-est", "3": "Centro",
                     "4": "Sud", "5": "Isole"}


def prov_to_ripartizione(prov_code: str) -> str:
    for rip, lst in RIPARTIZIONI_PROVINCE.items():
        if prov_code in lst:
            return rip
    raise KeyError(f"codice provincia sconosciuto: {prov_code}")


def load_raw():
    """(popolazione provinciale tidy, popolazione ripartizioni tidy)."""
    raw = ROOT / "data" / "raw"
    prov = pd.read_csv(raw / "POSAS_2026_it_Province.csv", sep=";",
                       skiprows=1, encoding="utf-8-sig")
    prov.columns = [c.strip().strip('"') for c in prov.columns]
    prov = prov.rename(columns={"Codice provincia": "prov_code",
                                "Età": "eta",
                                "Totale maschi": "maschi",
                                "Totale femmine": "femmine"})
    prov["prov_code"] = prov["prov_code"].astype(str).str.strip('"')
    prov["eta"] = pd.to_numeric(prov["eta"], errors="coerce")
    prov = prov.dropna(subset=["eta"])
    prov = prov[prov["eta"] <= MAX_AGE]
    for col in ("maschi", "femmine"):
        prov[col] = pd.to_numeric(
            prov[col].astype(str).str.strip('"').str.replace(",", "."),
            errors="coerce")

    rip = pd.read_csv(raw / "POSAS_2026_it_Ripartizioni.csv", sep=";",
                      skiprows=1, encoding="utf-8-sig")
    rip.columns = [c.strip().strip('"') for c in rip.columns]
    rip = rip.rename(columns={"Codice ripartizione": "rip_code",
                              "Età": "eta",
                              "Totale maschi": "maschi",
                              "Totale femmine": "femmine"})
    rip["rip_code"] = rip["rip_code"].astype(str).str.strip('"')
    rip["eta"] = pd.to_numeric(rip["eta"], errors="coerce")
    rip = rip.dropna(subset=["eta"]).query("eta <= @MAX_AGE")
    for col in ("maschi", "femmine"):
        rip[col] = pd.to_numeric(
            rip[col].astype(str).str.strip('"').str.replace(",", "."),
            errors="coerce")
    return prov, rip


def n0_by_group(pop: pd.DataFrame, group_codes: list,
                sex: str = "femmine") -> np.ndarray:
    sub = pop[pop["prov_code"].isin(group_codes)]
    grouped = sub.groupby("eta")[sex].sum()
    vec = np.zeros(MAX_AGE + 1)
    for age in range(MAX_AGE + 1):
        vec[age] = grouped.get(age, 0.0)
    return vec


def survival_by_group(tvm_csv: Path, pop: pd.DataFrame,
                      group_codes: list, sex: str = "femmine") -> np.ndarray:
    """Media delle probabilita' prospettiche provinciali (TVM) pesata per la
    popolazione del sesso di riferimento, ristretta al gruppo di province."""
    df = pd.read_csv(tvm_csv, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Sesso"] == {"femmine": "Femmine", "maschi": "Maschi"}[sex]]
    df["prov_code"] = df["Cod. provincia"].astype(int).astype(str).str.zfill(3)
    df["eta"] = pd.to_numeric(df["Età"], errors="coerce")
    p_col = next(c for c in df.columns if "prospett" in c.lower())
    df["P"] = pd.to_numeric(df[p_col], errors="coerce")
    df = df.dropna(subset=["eta", "P"]).query("eta <= @MAX_AGE")
    df = df[df["prov_code"].isin(group_codes)]

    weights = pop[pop["prov_code"].isin(group_codes)][
        ["prov_code", "eta", sex]]
    merged = df.merge(weights, on=["prov_code", "eta"], how="inner")
    num = (merged["P"] * merged[sex]).groupby(merged["eta"]).sum()
    den = merged.groupby("eta")[sex].sum()
    p_bar = num / den
    probs = np.zeros(MAX_AGE + 1)
    for age in range(MAX_AGE):
        probs[age] = float(p_bar.get(age, 0.0))
    probs[MAX_AGE] = 0.0
    return np.clip(probs, 0.0, 1.0)


def area_report(anagrafica: list[tuple[str, str]], tfr_scale: float = 1.0,
                years: int = 55, start_year: int = 2026,
                saldo_nazionale: float = 280_000.0, verbose: bool = True) -> dict:
    """Per ciascuna area (nome, codici gruppo): Leslie due sessi + indicatori.
    Il saldo migratorio nazionale e' ripartito in proporzione alla popolazione."""
    from leslie import (asymptotic_halving, build_leslie_matrix,
                        dominant_eigen, halving_time, load_processed,
                        simulate_two_sex)
    from ltc import prevalence_by_age

    data = load_processed()
    fert = data["fertility"]
    tvm = ROOT / "data" / "raw" / "datiprovincialicompleti2024.csv"
    pop, rip_csv = load_raw()
    prev = prevalence_by_age(MAX_AGE)

    # saldo proporzionale alla popolazione dell'area
    tot_naz = float(pop["femmine"].sum() + pop["maschi"].sum())
    rows = []
    for nome, codes in anagrafica:
        n0_f = n0_by_group(pop, codes, "femmine")
        n0_m = n0_by_group(pop, codes, "maschi")
        pop_area = float(n0_f.sum() + n0_m.sum())
        saldo = saldo_nazionale * pop_area / tot_naz
        P_f = survival_by_group(tvm, pop, codes, "femmine")
        P_m = survival_by_group(tvm, pop, codes, "maschi")
        lam, _ = dominant_eigen(build_leslie_matrix(fert * tfr_scale, P_f))
        out = simulate_two_sex(n0_f, n0_m, fert, P_f, P_m, years=years,
                               net_migration_total=saldo,
                               tfr_scale=tfr_scale, store_ages=True)
        tot, tr_f, tr_m, ages_f, ages_m = out
        claimants = ((ages_f + ages_m) * prev[None, :]).sum(axis=1)
        over80 = (ages_f + ages_m)[:, 80:].sum(axis=1)
        rows.append({
            "area": nome,
            "popolazione_2026": round(pop_area / 1e6, 2),
            "lambda1": round(float(lam), 4),
            "r_pct": round(float(np.log(lam)) * 100, 3),
            "t_mezzo_asintotico": round(float(asymptotic_halving(lam)), 1),
            "t_mezzo_primo": round(float(halving_time(tot)), 1),
            "pop_2056_mln": round(float(tot[years - 55 + 30]) / 1e6, 2),
            "pop_2081_mln": round(float(tot[years]) / 1e6, 2),
            "claimants_2056_mln": round(float(claimants[30]) / 1e6, 3),
            "over80_2056_mln": round(float(over80[30]) / 1e6, 3),
        })
    res = {"tfr_scale": tfr_scale, "aree": rows}
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


def regionale_report(verbose: bool = True) -> dict:
    anagrafica = [(RIPARTIZIONI_NOMI[k], v) for k, v in
                  sorted(RIPARTIZIONI_PROVINCE.items())]
    res = area_report(anagrafica, verbose=verbose)
    # spotlight Sardegna: TFR 2025 (0,85) come scala del TFR nazionale 1,18
    sar = area_report([("Sardegna (TFR 0,85)", SARDEGNA)],
                      tfr_scale=0.85 / 1.18, verbose=False)
    sar_naz = area_report([("Sardegna (TFR nazionale)", SARDEGNA)],
                          verbose=False)
    res["sardegna"] = {
        "tfr_085": sar["aree"][0],
        "tfr_nazionale": sar_naz["aree"][0],
    }
    if verbose:
        print(json.dumps({"sardegna": res["sardegna"]}, indent=2,
                         ensure_ascii=False))
    return res


def valida_mapping(tol: float = 0.005) -> dict:
    """Somma delle popolazioni provinciali per ripartizione vs CSV Ripartizioni."""
    pop, rip_csv = load_raw()
    checks = []
    for rip, codes in RIPARTIZIONI_PROVINCE.items():
        sub = pop[pop["prov_code"].isin(codes)]
        got = float(sub["femmine"].sum() + sub["maschi"].sum())
        exp_rows = rip_csv[rip_csv["rip_code"] == rip]
        exp = float(exp_rows.groupby("eta")[["maschi", "femmine"]]
                    .sum().sum().sum())
        rel = abs(got - exp) / exp if exp else np.nan
        checks.append({"ripartizione": RIPARTIZIONI_NOMI[rip],
                       "provinciale": round(got), "csv": round(exp),
                       "delta_rel": round(rel, 5)})

        assert rel < tol, f"mismatch {RIPARTIZIONI_NOMI[rip]}: {rel}"
    return {"check": checks, "ok": True}


if __name__ == "__main__":
    if "--valida" in sys.argv:
        print(json.dumps(valida_mapping(), indent=2, ensure_ascii=False))
    else:
        regionale_report()
