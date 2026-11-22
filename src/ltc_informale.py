"""Capitolo LTC 3: valore del caregiving informale, sensitivita' della
calibrazione logistica e caregiver gap migratorio.

Tre domande:
1. quanto vale (shadow cost) il lavoro di cura non monetizzato delle famiglie?
2. quanto i risultati del capitolo 2 dipendono dalla calibrazione del flesso
   logistico r0? (analisi di sensitivita')
3. quale flusso migratorio servirebbe per tenere il rapporto caregiver/claimant
   sopra la soglia oltre la quale l'assistenza informale cede? (caregiver gap)

Parametri parametrici e dichiarati, come nei capitoli 1-2.
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

HOURS_PER_WEEK_INFORMAL = 30.0
VALUE_PER_HOUR = 12.0
HORIZON = 55
SOGLIA_RAPPORTO = 11.0


def informal_care_value(informal_claimants,
                        hours_per_week: float = HOURS_PER_WEEK_INFORMAL,
                        value_per_hour: float = VALUE_PER_HOUR):
    """Valore annuo (€) del lavoro di cura informale non monetizzato."""
    hours_year = hours_per_week * 52.0
    return informal_claimants * hours_year * value_per_hour


def _demography(saldo, years=HORIZON):
    from leslie import load_processed, simulate_two_sex
    from ltc import ltc_indicators, prevalence_by_age

    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"],
                           years=years, net_migration_total=saldo,
                           store_ages=True)
    _, _, _, ages_f, ages_m = out
    ages = ages_f + ages_m
    ind = ltc_indicators(ages, prevalence_by_age(len(data["n0"]) - 1))
    return ind


def calibrazione_sensitivity(r0_values=(9.0, 11.0, 13.0),
                             saldo: float = 280_000.0) -> list:
    """Picco di costo del capitolo 2 al variare del flesso logistico r0."""
    from ltc_costi import annual_cost, cost_breakdown

    ind = _demography(saldo)
    out = []
    for r0 in r0_values:
        costs = np.array([
            annual_cost(cost_breakdown(ind["claimants"][t], ind["ratio"][t],
                                        r0=r0))
            for t in range(HORIZON + 1)])
        out.append({
            "r0": r0,
            "costo_picco_mld": float(costs.max() / 1e9),
            "picco_anno": 2026 + int(np.argmax(costs)),
            "costo_2081_mld": float(costs[-1] / 1e9),
            "valore_informale_2026_mld": float(
                informal_care_value(cost_breakdown(
                    ind["claimants"][0], ind["ratio"][0], r0=r0)["informale"])
                / 1e9),
        })
    return out


def caregiver_gap(soglia: float = SOGLIA_RAPPORTO,
                  years: int = HORIZON) -> dict:
    """Saldo migratorio annuo necessario per tenere il rapporto caregiver/claimant
    >= soglia sull'intero orizzonte (bisezione)."""
    def min_ratio(saldo):
        ind = _demography(saldo, years=years)
        return float(np.nanmin(ind["ratio"]))

    if min_ratio(0.0) >= soglia:
        return {"saldo_richiesto": 0.0, "min_ratio_zero": min_ratio(0.0)}

    lo, hi = 0.0, 2_500_000.0
    if min_ratio(hi) < soglia:
        return {"saldo_richiesto": None,
                "min_ratio_zero": min_ratio(0.0),
                "min_ratio_max": min_ratio(hi),
                "nota": "soglia non raggiungibile entro il limite di ricerca"}
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if min_ratio(mid) >= soglia:
            hi = mid
        else:
            lo = mid
    return {"saldo_richiesto": round(hi), "soglia": soglia,
            "min_ratio_zero": min_ratio(0.0),
            "min_ratio_saldo": min_ratio(hi)}


def ltc3_report(verbose: bool = True) -> dict:
    ind = _demography(280_000.0)
    from ltc_costi import cost_breakdown

    value_today = informal_care_value(
        cost_breakdown(ind["claimants"][0], ind["ratio"][0])["informale"])
    value_2056 = informal_care_value(
        cost_breakdown(ind["claimants"][30], ind["ratio"][30])["informale"])

    res = {
        "valore_informale_2026_mld": float(value_today / 1e9),
        "valore_informale_2056_mld": float(value_2056 / 1e9),
        "sensibilita_r0": calibrazione_sensitivity(),
        "caregiver_gap_soglia_11": caregiver_gap(),
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    ltc3_report()
