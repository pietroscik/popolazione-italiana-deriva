"""Capitolo LTC 2: dal rapporto caregiver/claimant al costo aggregato.

Modello di copertura della domanda LTC in tre livelli:
1. assistenza informale (familiare): capacita' funzione decrescente del
   rapporto caregiver/claimant (quando i potenziali assistenti scarseggiano,
   una quota crescente dei claimants non puo' piu' essere assorbita in casa);
2. assistenza formale domiciliare (ADI / day care);
3. assistenza residenziale (RSA) per la quota piu' fragile.

Tutti i parametri di costo e capacita' sono PARAMETRICI e dichiarati: ordini
di grandezza del settore italiano, da calibrare su fonti ufficiali
(ISTAT Condizioni di salute, Osservatorio sulla non autosufficienza).
"""

import json
import sys
from pathlib import Path

import numpy as np

MAX_AGE = 100
ROOT = Path(__file__).resolve().parents[1]

UNIT_COST_DOMICILIARE = 15_000.0
UNIT_COST_RESIDENZIALE = 48_000.0
SHARE_DOMICILIARE_FORMALE = 0.65
GDP_NOMINALE_2026 = 2_200_000_000_000.0

R_RATIO_INFLESSO = 11.0
R_LOGIT_PENDENZA = 2.0


def informal_share(ratio: np.ndarray | float,
                   r0: float = R_RATIO_INFLESSO,
                   b: float = R_LOGIT_PENDENZA) -> np.ndarray | float:
    """Quota di claimants coperta dall'assistenza informale.

    Logistica nel rapporto caregiver/claimant: al rapporto alto la famiglia
    assorbe quasi tutto; sotto il punto di flesso r0 la capacita' informale
    cede e la domanda migra verso quella formale. Calibrazione dichiarata:
    ~75-80% informale al rapporto attuale (~14), ~50% a rapporto ~8-11.
    """
    return 1.0 / (1.0 + np.exp(-(ratio - r0) / b))


def cost_breakdown(claimants, ratio):
    """Scomposizione dei claimants nei tre livelli di copertura."""
    informal = claimants * informal_share(ratio)
    formal = claimants - informal
    domiciliare = formal * SHARE_DOMICILIARE_FORMALE
    residenziale = formal * (1.0 - SHARE_DOMICILIARE_FORMALE)
    return {"informale": informal, "domiciliare": domiciliare,
            "residenziale": residenziale}


def annual_cost(breakdown):
    return (breakdown["domiciliare"] * UNIT_COST_DOMICILIARE +
            breakdown["residenziale"] * UNIT_COST_RESIDENZIALE)


def ltc_cost_report(years: int = 55, start_year: int = 2026,
                    saldo: float = 280_000.0, tfr_scale: float = 1.0,
                    verbose: bool = True) -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from leslie import load_processed, simulate_two_sex
    from ltc import ltc_indicators, prevalence_by_age

    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"],
                           years=years, net_migration_total=saldo,
                           tfr_scale=tfr_scale, store_ages=True)
    tot, _, _, ages_f, ages_m = out
    ages = ages_f + ages_m
    ind = ltc_indicators(ages, prevalence_by_age(len(data["n0"]) - 1))

    rows = []
    for t in [0, 15, 30, 45, years]:
        bd = cost_breakdown(ind["claimants"][t], ind["ratio"][t])
        cost = annual_cost(bd)
        rows.append({
            "anno": start_year + t,
            "claimants": float(ind["claimants"][t]),
            "ratio": float(ind["ratio"][t]),
            "informali": float(bd["informale"]),
            "domiciliare": float(bd["domiciliare"]),
            "residenziali": float(bd["residenziale"]),
            "costo_formale_mld": float(cost / 1e9),
            "costo_pct_gdp": float(cost / GDP_NOMINALE_2026 * 100.0),
        })

    costs = np.array([annual_cost(cost_breakdown(ind["claimants"][t],
                                                 ind["ratio"][t]))
                      for t in range(years + 1)])
    peak_year = start_year + int(np.argmax(costs))
    res = {
        "saldo_migratorio": saldo,
        "tfr_scale": tfr_scale,
        "tabella": rows,
        "costo_picco_mld": float(costs.max() / 1e9),
        "costo_picco_anno": peak_year,
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    saldo = float(sys.argv[1]) if len(sys.argv) > 1 else 280_000.0
    ltc_cost_report(saldo=saldo)
