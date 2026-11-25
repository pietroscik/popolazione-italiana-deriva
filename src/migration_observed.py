"""Migrazione netta OSSERVATA per eta' e sesso (roadmap v1.2, ramo 4).

Il modello due sessi usa oggi un profilo migratorio Rogers-Castro
SINTETICO, calibrato solo sul saldo totale annuo (~+263k nel 2024) e sulla
forma teorica. Questo modulo deriva il profilo NETTO OSSERVATO per eta'
dalla bilancia demografica implicita in due POSAS consecutive:

    m(a, {m,f}) = P_{t+1}(a+1) - P_t(a) * S(a, {m,f})

con S la sopravvivenza condizionale TVM 2024 (un solo vintage: mostrato in
docs/21 come assunzione dichiarata). La classe terminale 100+ e' APERTA
(stessa convenzione della Leslie, v. il fix del ciclo v1.1):

    m(100) = P_{t+1}(100) - [P_t(99)*S(99) + P_t(100)*S(100)]

L'eta' 0 e' ESCLUSA (richiederebbe le nascite dell'anno t: dichiarato).
"""

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from parse_istat import load_population, n0_from_population  # noqa: E402

BASE = "https://demo.istat.it/data/posas"
MAX_AGE = 100


def download_posas(year: int, raw_dir: Path | None = None) -> Path:
    """POSAS Ripartizioni dell'anno richiesto (csv estratto dallo zip)."""
    raw = raw_dir or (ROOT / "data" / "raw")
    raw.mkdir(parents=True, exist_ok=True)
    dest = raw / f"POSAS_{year}_it_Ripartizioni.zip"
    csv = raw / f"POSAS_{year}_it_Ripartizioni.csv"
    if csv.exists():
        return csv
    if not dest.exists():
        req = urllib.request.Request(
            f"{BASE}/POSAS_{year}_it_Ripartizioni.zip",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
    with zipfile.ZipFile(dest) as zf:
        member = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        csv.write_bytes(zf.read(member))
    return csv


def population_by_sex_year(year: int, raw_dir: Path | None = None
                           ) -> dict[str, np.ndarray]:
    """Vettori nazionali per eta' (0..100+, classe aperta) da POSAS."""
    csv = download_posas(year, raw_dir)
    pop = load_population(csv, max_age=MAX_AGE)
    return {"femmine": n0_from_population(pop, MAX_AGE, "femmine"),
            "maschi": n0_from_population(pop, MAX_AGE, "maschi")}


def observed_net_migration_by_age(year_t: int, year_t1: int,
                                  raw_dir: Path | None = None) -> dict:
    """Profilo netto osservato per eta' e sesso tra due POSAS consecutive.

    La sopravvivenza e' la TVM 2024 (un solo vintage per entrambi gli
    intervalli: assunzione dichiarata; l'errore del tasa e' del secondo
    ordine rispetto al residuo migratorio).
    """
    pt = population_by_sex_year(year_t, raw_dir)
    pt1 = population_by_sex_year(year_t1, raw_dir)
    data_dir = ROOT / "data" / "processed"
    s_f = np.load(data_dir / "survival_probs.npy")
    s_m = np.load(data_dir / "survival_probs_male.npy")

    out = {}
    for sex, pt_vec, pt1_vec, S in (
            ("femmine", pt["femmine"], pt1["femmine"], s_f),
            ("maschi", pt["maschi"], pt1["maschi"], s_m)):
        m = np.zeros(MAX_AGE + 1)
        for a in range(1, MAX_AGE - 1):
            m[a] = pt1_vec[a + 1] - pt_vec[a] * S[a]
        # classe aperta 100+: il residuo di 99 e 100+ e' inseparabile
        # (chi ha 99 anni a gennaio e' nei 100+ l'anno dopo, insieme ai
        # centenari ritenuti): unica cella "99+" combinata alla voce 99
        m[MAX_AGE - 1] = (pt1_vec[MAX_AGE]
                          - pt_vec[MAX_AGE - 1] * S[MAX_AGE - 1]
                          - pt_vec[MAX_AGE] * S[MAX_AGE])
        m[MAX_AGE] = 0.0
        out[sex] = m
    prof = out["femmine"] + out["maschi"]
    mean_age = float((np.arange(MAX_AGE + 1) * np.clip(prof, 0, None)).sum()
                     / np.clip(prof, 0, None).sum())
    return {
        "anni": f"{year_t}->{year_t1}",
        "femmine": out["femmine"], "maschi": out["maschi"],
        "totale": out, "saldo_obs (eta' 1-100+)": float(prof.sum()),
        "eta_media_migranti_pos": mean_age,
        "eta_p95_out": None,
        "assunzioni": [
            "sopravvivenza TVM 2024 (unico vintage) su entrambi gli intervalli",
            "eta' 0 esclusa (serve il fluslo di nascite; richiede bilancio)",
            "classe terminale 100+ aperta (convenzione Leslie v1.1)",
        ],
    }


def compare_with_synthetic(prof_obs: np.ndarray, net_total: float = 263_000.0
                           ) -> dict:
    """Confronto col profilo Rogers-Castro sintetico del repo."""
    from migration import rogers_castro_rates
    ages = np.arange(len(prof_obs))
    synth = rogers_castro_rates(ages)
    synth = synth / synth.sum() * net_total
    corr = float(np.corrcoef(prof_obs, synth)[0, 1])
    share_20_39_obs = float(prof_obs[(ages >= 20) & (ages <= 39)].sum()
                             / prof_obs.sum())
    share_20_39_syn = float(synth[(ages >= 20) & (ages <= 39)].sum()
                            / synth.sum())
    return {
        "correlazione_obs_synth": corr,
        "quota_20_39_obs": share_20_39_obs,
        "quota_20_39_synth": share_20_39_syn,
        "saldo_obs": float(prof_obs.sum()),
        "saldo_sintetico_imposto": net_total,
    }


def observed_report(years=((2023, 2024), (2024, 2025)),
                    verbose: bool = True) -> dict:
    res = {}
    for y0, y1 in years:
        mig = observed_net_migration_by_age(y0, y1)
        prof = (mig["femmine"] + mig["maschi"])
        comp = compare_with_synthetic(prof)
        res[mig["anni"]] = {
            "saldo_obs_eta1_100": comp["saldo_obs"],
            "eta_media": round(mig["eta_media_migranti_pos"], 1),
            "correlazione_col_sintetico": round(comp["correlazione_obs_synth"], 3),
            "quota_20_39_obs": round(comp["quota_20_39_obs"], 3),
            "quota_20_39_sintetico": round(comp["quota_20_39_synth"], 3),
        }
    if verbose:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    return res


def simulate_two_sex_profiles(n0_f, n0_m, fertility, P_f, P_m, mig_f, mig_m,
                             years=55, tfr_scale=1.0):
    """Le due trajettorie con profili migratori PER SESSO statici (usa
    project_two_sex direttamente: simulate_two_sex accetta un solo profilo
    condiviso)."""
    from leslie import project_two_sex
    nf, nm = n0_f.astype(float).copy(), n0_m.astype(float).copy()
    tot = [nf.sum() + nm.sum()]
    for _ in range(years):
        nf, nm = project_two_sex(nf, nm, fertility, P_f, P_m,
                                 mig_f, mig_m, tfr_scale)
        tot.append(nf.sum() + nm.sum())
    return np.array(tot)


def scenario_observed_vs_synth(saldo: float = 263_000.0, years: int = 55,
                               year_pair: tuple = (2024, 2025)) -> dict:
    """Scenario a saldo costante: profilo sintetico dinamico (headline) vs
    profilo OSSERVATO statico (anno year_pair), entrambi a saldo `saldo`.
    Break-even ricalcolato con entrambi i profili (bisezione)."""
    from leslie import load_processed, simulate_two_sex
    from migration import saldo_for_constant_population
    data = load_processed()
    n0_f, n0_m = data["n0"], data["n0_male"]
    P_f, P_m = data["survival"], data["survival_male"]
    fert = data["fertility"]

    mig = observed_net_migration_by_age(*year_pair)
    scale = saldo / float((mig["femmine"] + mig["maschi"]).sum())
    prof_f, prof_m = mig["femmine"] * scale, mig["maschi"] * scale

    tot_obs = simulate_two_sex_profiles(n0_f, n0_m, fert, P_f, P_m,
                                        prof_f, prof_m, years=years)
    tot_syn, _, _ = simulate_two_sex(n0_f, n0_m, fert, P_f, P_m, years=years,
                                     net_migration_total=saldo)

    def growth_synth(s):
        t, _, _ = simulate_two_sex(n0_f, n0_m, fert, P_f, P_m, years=years,
                                   net_migration_total=s)
        return t[-1] - t[0]

    def growth_obs(s):
        k = s / saldo if saldo else 0.0
        tt = simulate_two_sex_profiles(n0_f, n0_m, fert, P_f, P_m,
                                       prof_f * k, prof_m * k, years=years)
        return tt[-1] - tt[0]

    be_syn = float(saldo_for_constant_population(growth_synth, lo=0,
                                                 hi=1_000_000))
    lo, hi = 0.0, 1_000_000.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if growth_obs(mid) > 0:
            hi = mid
        else:
            lo = mid
    return {
        "saldo_assunto": saldo,
        "anni": years,
        "anno_profilo": f"{year_pair[0]}->{year_pair[1]}",
        "pop_finale_sintetico": float(tot_syn[-1]),
        "pop_finale_osservato": float(tot_obs[-1]),
        "differenza_pct": float((tot_obs[-1] / tot_syn[-1] - 1) * 100),
        "break_even_sintetico": be_syn,
        "break_even_osservato": float(0.5 * (lo + hi)),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({k: (r if not isinstance(r, np.ndarray) else None)
                      for k, r in observed_report(verbose=False).items()},
                     indent=1, ensure_ascii=False))
    print("--- scenario")
    print(json.dumps(scenario_observed_vs_synth(), indent=1))
