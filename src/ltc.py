"""Capitolo LTC: claimants non autosufficienti e caregiver potenziali.

Dal vettore di stato per eta' proiettato a due sessi (Leslie-Rogers) calcola:
- over-80 (proxy del bacino di domanda LTC)
- claimants stimati applicando una prevalenza di non-autosufficienza per fascia
- caregiver informali potenziali (45-64 anni)
- rapporto caregiver/claimants, il driver del costo medio LTC nel modello
  basato su assistenza familiare (docs/03_roadmap_ltc.md)
"""

import json
import sys
from pathlib import Path

import numpy as np

MAX_AGE = 100
ROOT = Path(__file__).resolve().parents[1]

# Prevalenza di non-autosufficienza per fascia d'eta' (parametrica, dichiarata).
# Ordine di grandezza coerente con le indagini italiane sul settore (ISTAT
# Condizioni di salute, Osservatorio sulla non autosufficienza): da calibrare
# sulle fonti ufficiali quando entreranno nel repo.
PREVALENCE_BANDS = [
    (0, 64, 0.005),
    (65, 69, 0.02),
    (70, 74, 0.03),
    (75, 79, 0.05),
    (80, 84, 0.09),
    (85, 89, 0.16),
    (90, 100, 0.28),
]

CAREGIVER_AGE = (45, 64)
ELDERLY_AGE = 80


def prevalence_by_age(max_age: int = MAX_AGE) -> np.ndarray:
    vec = np.zeros(max_age + 1)
    for lo, hi, p in PREVALENCE_BANDS:
        vec[lo:hi + 1] = p
    return vec


def ltc_indicators(ages: np.ndarray, prevalence: np.ndarray | None = None,
                   max_age: int = MAX_AGE) -> dict:
    """Indicatore LTC anno per anno da una matrice (anni x eta') due sessi."""
    if prevalence is None:
        prevalence = prevalence_by_age(max_age)
    years = ages.shape[0]
    over80 = ages[:, ELDERLY_AGE:].sum(axis=1)
    claimants = (ages * prevalence[None, :]).sum(axis=1)
    caregivers = ages[:, CAREGIVER_AGE[0]:CAREGIVER_AGE[1] + 1].sum(axis=1)
    ratio = np.divide(caregivers, claimants,
                      out=np.full_like(caregivers, np.nan),
                      where=claimants > 0)
    return {"over80": over80, "claimants": claimants,
            "caregivers": caregivers, "ratio": ratio}


def ltc_report(years: int = 55, start_year: int = 2026,
               saldo: float = 280_000.0, verbose: bool = True) -> dict:
    from leslie import load_processed, simulate_two_sex

    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"],
                           years=years, net_migration_total=saldo,
                           store_ages=True)
    tot, tr_f, tr_m, ages_f, ages_m = out
    ages = ages_f + ages_m
    prev = prevalence_by_age(len(data["n0"]) - 1)
    ind = ltc_indicators(ages, prev)

    marker_years = [0, 15, 30, 45, years]
    table = []
    for t in marker_years:
        table.append({
            "anno": start_year + t,
            "popolazione": float(tot[t]),
            "over80": float(ind["over80"][t]),
            "claimants": float(ind["claimants"][t]),
            "caregivers": float(ind["caregivers"][t]),
            "caregivers_per_claimant": float(ind["ratio"][t]),
        })

    min_ratio = float(np.nanmin(ind["ratio"]))
    min_year = start_year + int(np.nanargmin(ind["ratio"]))
    res = {"saldo_migratorio": saldo, "tabella": table,
           "ratio_minimo": min_ratio, "ratio_minimo_anno": min_year}
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    saldo = float(sys.argv[1]) if len(sys.argv) > 1 else 280_000.0
    ltc_report(saldo=saldo)
