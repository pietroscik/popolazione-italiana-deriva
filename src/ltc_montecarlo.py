"""Capitolo LTC 5 (P2 dell'audit): modello attuariale probabilistico.

Dal capitolo 2 (deterministico, costi parametrici puntuali) si passa a:

- **prevalenza per eta' e sesso** (P2-11): moltiplicatori parametrici
  dichiarati (femminile 1,20 / maschile 0,75 sopra i 65 anni — ordine di
  grandezza delle indagini italiane: sopravvivenza femminile e vedovanza
  spostano la prevalenza 80+ verso le donne)
- **severita' a tre livelli** (P2-12): lieve / medio / grave con mix e costi
 /per livello calibrati **sui costi unitari medi del capitolo 2** (blended
  ~15k domiciliare / ~48k residenziale): il modello deterministico e' il
  caso centrale del nuovo, non un modello diverso
- **Monte Carlo** (P2-13/14): distribuzioni su moltiplicatori di sesso, mix
  di severita' (Dirichlet), costi per livello (lognormali), quota
  domiciliare (Beta), calibrazione informale (r0, b) e **demografia**
  (miglioramento annuo della mortalita' e scala TFR campionati per replica)
- **inflazione sanitaria e sconto** (P2-15): stream nominale con eccesso di
  inflazione sanitaria campionato, valore attuale con tasso reale
- **scenari di longevita'** (P2-16): miglioramento annuo della mortalita'
  rho in {0, 0,5%, 1%} come sensibilita' deterministica.

Tutte le distribuzioni sono dichiarate come **assunte parametriche** (status
epistemico: docs/01), con la fonte di ancoraggio indicata. Nessuna pretesa di
stima: il Monte Carlo quantifica l'incertezza *condizionata alle ipotesi*,
non l'incertezza strutturale.
"""

import json
import sys
from pathlib import Path

import numpy as np

from ltc import PREVALENCE_BANDS, prevalence_by_age
from ltc_costi import R_LOGIT_PENDENZA, R_RATIO_INFLESSO, informal_share

ROOT = Path(__file__).resolve().parents[1]

SEX_MULTIPLIER = {"F": 1.20, "M": 0.75}
SEXAGE = 65

SEVERITY_MIX = np.array([0.45, 0.35, 0.20])          # lieve, medio, grave
SEVERITY_CONCENTRATION = 100.0                        # Dirichlet alfa-scalare
COST_DOMICILIARE = np.array([9_000.0, 16_000.0, 26_000.0])
COST_RESIDENZIALE_MG = np.array([45_000.0, 52_000.0])  # medio, grave
SHARE_DOMICILIARE_CENTER = 0.65

INFLAZIONE = 0.02
TASSO_REALE = 0.015
ECESSO_SANITARIO_MEDIA = 0.005                        # inflazione sanitaria - CPI


def prevalence_by_age_sex(sex: str, max_age: int = 100) -> np.ndarray:
    """Prevalenza per fascia, scalata per sesso sopra i 65 anni."""
    base = prevalence_by_age(max_age)
    out = base.copy()
    out[SEXAGE:] *= SEX_MULTIPLIER[sex]
    return out


def blended_unit_costs(sev_mix: np.ndarray = SEVERITY_MIX) -> tuple[float, float]:
    """Costi blended: verificano la coerenza col capitolo 2 (15k/48k)."""
    dom = float(sev_mix @ COST_DOMICILIARE)
    mg = sev_mix[1:] / sev_mix[1:].sum()
    res = float(mg @ COST_RESIDENZIALE_MG)
    return dom, res


def simulate_claimants_m(n0_f, n0_m, fertility, P_f, P_m, tfr_scale,
                         surv_improvement, years, saldo,
                         sex_mult_f=SEX_MULTIPLIER["F"],
                         sex_mult_m=SEX_MULTIPLIER["M"]):
    """Due sessi con mortalita' migliorata e TFR scala; ritorna claimants per
    sesso (anni x 1) e il rapporto caregiver/claimant combinato. I moltiplicatori
    di prevalenza per sesso sono argomento: nel Monte Carlo vengono campionati
    per replica, fuori dal MC restano ai valori centrali dichiarati."""
    from leslie import simulate_two_sex
    if surv_improvement > 0.0:
        P_f = 1.0 - (1.0 - P_f) * (1.0 - surv_improvement)
        P_m = 1.0 - (1.0 - P_m) * (1.0 - surv_improvement)
    out = simulate_two_sex(n0_f, n0_m, fertility, P_f, P_m, years=years,
                           net_migration_total=saldo, tfr_scale=tfr_scale,
                           store_ages=True)
    tot, tr_f, tr_m, ages_f, ages_m = out
    prev_f = prevalence_by_age_sex("F", len(n0_f) - 1)
    prev_m = prevalence_by_age_sex("M", len(n0_m) - 1)
    prev_f[SEXAGE:] /= SEX_MULTIPLIER["F"]
    prev_f[SEXAGE:] *= sex_mult_f
    prev_m[SEXAGE:] /= SEX_MULTIPLIER["M"]
    prev_m[SEXAGE:] *= sex_mult_m
    cl_f = (ages_f * prev_f[None, :]).sum(axis=1)
    cl_m = (ages_m * prev_m[None, :]).sum(axis=1)
    caregivers = (ages_f + ages_m)[:, 45:65].sum(axis=1)
    claimants = cl_f + cl_m
    ratio = np.divide(caregivers, claimants,
                      out=np.full_like(caregivers, np.nan),
                      where=claimants > 0)
    return cl_f, cl_m, claimants, ratio


def annual_cost_mc(claimants, ratio, sev_mix, cost_dom, cost_res, share_dom,
                   r0, b):
    """Costo annuo formale con severita' a livelli e mix per livello."""
    informal = claimants * informal_share(ratio, r0=r0, b=b)
    formal = claimants - informal
    n_dom = formal * share_dom
    n_res = formal * (1.0 - share_dom)
    dom = n_dom * float(sev_mix @ cost_dom)
    mg = sev_mix[1:] / sev_mix[1:].sum()
    res = n_res * float(mg @ cost_res)
    return dom + res


def monte_carlo_ltc(B: int = 500, seed: int = 7, years: int = 55,
                    start_year: int = 2026, saldo: float = 280_000.0,
                    verbose: bool = True) -> dict:
    from leslie import load_processed
    data = load_processed()
    n0_f, n0_m = data["n0"], data["n0_male"]
    fert, P_f, P_m = data["fertility"], data["survival"], data["survival_male"]

    rng = np.random.default_rng(seed)
    T = years + 1
    costs = np.zeros((B, T))
    cl_f_2056 = np.zeros(B)
    cl_m_2056 = np.zeros(B)
    tfr_center = 1.0

    ann = years
    t_index_2056 = min(30, years)

    for b in range(B):
        sex_mult_f = rng.lognormal(np.log(SEX_MULTIPLIER["F"]), 0.10)
        sex_mult_m = rng.lognormal(np.log(SEX_MULTIPLIER["M"]), 0.10)
        sev = rng.dirichlet(SEVERITY_MIX * SEVERITY_CONCENTRATION)
        cost_dom = rng.lognormal(np.log(COST_DOMICILIARE), 0.15)
        cost_res = rng.lognormal(np.log(COST_RESIDENZIALE_MG), 0.10)
        share_dom = rng.beta(SHARE_DOMICILIARE_CENTER * 100, 35)
        r0 = rng.normal(R_RATIO_INFLESSO, 1.0)
        b_par = rng.lognormal(np.log(R_LOGIT_PENDENZA), 0.10)
        rho = rng.uniform(0.0, 0.01)
        tfr_scale = rng.normal(tfr_center, 0.03)

        cl_f, cl_m, claimants, ratio = simulate_claimants_m(
            n0_f, n0_m, fert, P_f, P_m, tfr_scale, rho, years, saldo,
            sex_mult_f=sex_mult_f, sex_mult_m=sex_mult_m)

        costs[b] = annual_cost_mc(claimants, ratio, sev, cost_dom, cost_res,
                                  share_dom, r0, b_par) / 1e9
        cl_f_2056[b] = cl_f[t_index_2056]
        cl_m_2056[b] = cl_m[t_index_2056]

    t2056 = start_year + t_index_2056
    c2056 = costs[:, t_index_2056]
    peak_year_idx = int(np.argmax(np.median(costs, axis=0)))
    peak_vals = costs[:, peak_year_idx]

    # inflazione sanitaria e valore attuale (per replica: eccesso campionato)
    eccesso = rng.uniform(0.0, 0.01, size=B)
    anni = np.arange(T)
    fattore = ((1.0 + INFLAZIONE + eccesso)[:, None]
               / (1.0 + INFLAZIONE + TASSO_REALE)) ** anni[None, :]
    pv = (costs * fattore).sum(axis=1)

    def q(x, p):
        return float(np.quantile(x, p))

    res = {
        "B": B,
        "costo_2056_mld EUR (prezzi 2026)": {
            "media": round(float(c2056.mean()), 1),
            "q05": round(q(c2056, 0.05), 1),
            "q50": round(q(c2056, 0.50), 1),
            "q95": round(q(c2056, 0.95), 1),
        },
        "picco_mld": {
            "anno": start_year + peak_year_idx,
            "media": round(float(peak_vals.mean()), 1),
            "q05": round(q(peak_vals, 0.05), 1),
            "q95": round(q(peak_vals, 0.95), 1),
        },
        "claimants_mld_per_sesso": {
            "anno": t2056,
            "femmine_media": round(float(cl_f_2056.mean() / 1e6), 2),
            "maschi_media": round(float(cl_m_2056.mean() / 1e6), 2),
        },
        "valore_attuale_2026_2081_mld": {
            "istruzioni": "prezzi 2026, sconto reale 1,5%, inflazione 2% + eccesso sanitario campionato",
            "media": round(float(pv.mean()), 1),
            "q05": round(q(pv, 0.05), 1),
            "q95": round(q(pv, 0.95), 1),
        },
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


def scenari_longevita(rhos=(0.0, 0.005, 0.01), years: int = 55,
                      start_year: int = 2026, saldo: float = 280_000.0,
                      verbose: bool = True) -> dict:
    """P2-16: sensibilita' deterministica al miglioramento della mortalita'."""
    from leslie import load_processed
    data = load_processed()
    out = {}
    for rho in rhos:
        cl_f, cl_m, claimants, ratio = simulate_claimants_m(
            data["n0"], data["n0_male"], data["fertility"],
            data["survival"], data["survival_male"],
            1.0, rho, years, saldo)
        out[f"rho_{rho:.3f}"] = {
            "claimants_2056_mln": round(float(claimants[min(30, years)]) / 1e6, 3),
            "claimants_fine_mln": round(float(claimants[years]) / 1e6, 3),
            "claimants_2056_F_mln": round(float(cl_f[min(30, years)]) / 1e6, 3),
            "claimants_2056_M_mln": round(float(cl_m[min(30, years)]) / 1e6, 3),
        }
    if verbose:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


if __name__ == "__main__":
    if "--longevita" in sys.argv:
        scenari_longevita()
    else:
        B = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 500
        monte_carlo_ltc(B=B)
