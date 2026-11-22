"""Sensitivity sistematica OAT (P1-9 dell'audit).

One-At-a-Time: ogni parametro chiave della catena Leslie -> LTC viene
perturbato in un intervallo dichiarato, il modello viene rieseguito e si
riporta l'elasticita' (variazione % dell'output / variazione % del
parametro) dell'output headline C_2056 (costo formale aggregato al picco,
prezzi 2026) e t-mezzo asintotico per i parametri demografici.

Le elasticita' ordinano i driver: la tabella tornado risultente dice dove
una calibratione piu' accurata pagherebbe di piu'.
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def costo_2056(saldo: float = 280_000.0, tfr_scale: float = 1.0,
               surv_improvement: float = 0.0,
               unit_dom: float = 15_000.0, unit_res: float = 48_000.0,
               share_dom: float = 0.65, r0: float = 11.0, b: float = 2.0,
               prevalence_mult: float = 1.0, years: int = 30) -> float:
    """C_2056 (mld, prezzi 2026) del capitolo 2 con override parametrici."""
    from leslie import load_processed, simulate_two_sex
    from ltc import prevalence_by_age
    from ltc_costi import informal_share

    data = load_processed()
    P_f = 1.0 - (1.0 - data["survival"]) * (1.0 - surv_improvement)
    P_m = 1.0 - (1.0 - data["survival_male"]) * (1.0 - surv_improvement)
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           P_f, P_m, years=years,
                           net_migration_total=saldo, tfr_scale=tfr_scale,
                           store_ages=True)
    tot, tr_f, tr_m, ages_f, ages_m = out
    prev = prevalence_by_age(len(data["n0"]) - 1) * prevalence_mult
    claimants = ((ages_f + ages_m) * prev[None, :]).sum(axis=1)
    caregivers = (ages_f + ages_m)[:, 45:65].sum(axis=1)
    ratio = caregivers / claimants
    informal = claimants * informal_share(ratio, r0=r0, b=b)
    formal = claimants - informal
    c = (formal * (share_dom * unit_dom + (1 - share_dom) * unit_res))[-1]
    return float(c / 1e9)


def t_mezzo(tfr_scale: float = 1.0) -> float:
    from leslie import (asymptotic_halving, build_leslie_matrix,
                        dominant_eigen, load_processed)
    data = load_processed()
    lam, _ = dominant_eigen(build_leslie_matrix(data["fertility"] * tfr_scale,
                                                data["survival"]))
    return float(asymptotic_halving(lam))


PARAMS = [
    # (nome report, kwarg di costo_2056, tipo, centrale, perturbazioni %)
    ("costo_unitario_domiciliare", "unit_dom", "costo", 15_000.0, (-0.20, 0.20)),
    ("costo_unitario_residenziale", "unit_res", "costo", 48_000.0, (-0.20, 0.20)),
    ("quota_domiciliare", "share_dom", "costo", 0.65, (-0.10, 0.10)),
    ("prevalenza_multiplier", "prevalence_mult", "costo", 1.00, (-0.20, 0.20)),
    ("r0_break_informale", "r0", "costo", 11.0, (-0.18, 0.18)),
    ("pendenza_logistica_b", "b", "costo", 2.0, (-0.25, 0.25)),
    ("tfr_scale", "tfr_scale", "demo", 1.00, (-0.05, 0.05)),
    ("survival_improvement", "surv_improvement", "demo", 0.0, (0.0, 0.01)),
]


def sensitivity_report(verbose: bool = True) -> dict:
    base_c = costo_2056()
    base_t = t_mezzo()
    rows = []
    for name, kwarg, kind, center, (lo_pct, hi_pct) in PARAMS:
        entry = {"parametro": name, "centrale": center, "tipo": kind}
        if kind == "costo":
            for tag, pct in (("lo", lo_pct), ("hi", hi_pct)):
                val = center * (1 + pct)
                kw = {kwarg: val}
                try:
                    c = costo_2056(**kw)
                    entry[f"C2056_{tag}"] = round(c, 2)
                except Exception:
                    entry[f"C2056_{tag}"] = None
            c_lo, c_hi = entry.get("C2056_lo"), entry.get("C2056_hi")
            if c_lo is not None and c_hi is not None and base_c > 0:
                # elasticita' media sul ramo +%
                denom = hi_pct if hi_pct else 1.0
                entry["elasticita_C2056"] = round((c_hi - base_c)
                                                  / base_c / denom, 2)
        else:
            if name == "tfr_scale":
                for tag, scale in (("lo", 1 + lo_pct), ("hi", 1 + hi_pct)):
                    entry[f"thalf_{tag}"] = round(t_mezzo(scale), 1)
                entry["C2056_lo"] = round(costo_2056(tfr_scale=1 + lo_pct), 2)
                entry["C2056_hi"] = round(costo_2056(tfr_scale=1 + hi_pct), 2)
                entry["elasticita_C2056"] = round(
                    (entry["C2056_hi"] - base_c) / base_c / hi_pct, 2)
            elif name == "survival_improvement":
                c_hi = costo_2056(surv_improvement=hi_pct)
                entry["C2056_lo"] = round(base_c, 2)
                entry["C2056_hi"] = round(c_hi, 2)
                entry["d_commento"] = ("+1%/anno miglioramento mortalita' "
                                      f"-> {(c_hi / base_c - 1) * 100:+.1f}% "
                                      "su C2056 (segue docs/17 par. 5)")
        rows.append(entry)
    res = {"C2056_base_mld": round(base_c, 2),
           "t_mezzo_base_anni": round(base_t, 1),
           "sensitivita_oat": rows}
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    sensitivity_report()
