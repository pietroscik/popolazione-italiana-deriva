"""Lotka integrale esatto (P1-6 dell'audit): tripla verifica analitica.

Il README usa l'approssimazione R0 = TFR * s_f * S con S ~ 0,99. Qui il tasso
netto di riproduzione e l'equazione caratteristica di Lotka sono calcolati
ESATTAMENTE dai vettori ISTAT processati:

    R0 = somma_x ASFR_x * s_f * l_x                      (net repl. rate)
    T  = somma_x x * ASFR_x * s_f * l_x / R0             (lunghezza generazione)
    r_approx = ln(R0) / T                                (approssimazione)
    r_exact  radice di: somma_x e^{-r*(x+1)} * ASFR_x * s_f * l_x = 1
                                                          (Lotka esatto)

La convenzione (x+1) nella caratteristica e' quella della Leslie in uso
(nascite in testa alla matrice, sopravvivenza spostata di un anno): r_exact
combacia ln(lambda_1) al 6 decimale — la verifica chiude il cerchio tra
l'analisi asintotica integrale e l'autovalore dominante della matrice.
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SEX_RATIO_F = 0.488


def survival_to_age(p_cond: np.ndarray) -> np.ndarray:
    """l_x = sopravvivenza dalla nascita all'eta' x (l_0 = 1)."""
    l = np.ones(len(p_cond) + 1)
    for x in range(len(p_cond)):
        l[x + 1] = l[x] * p_cond[x]
    return l


def net_reproduction(asfr: np.ndarray, p_cond: np.ndarray,
                     s_f: float = SEX_RATIO_F) -> tuple[float, float]:
    """R0 e lunghezza media di generazione T dal profilo ASFR e mortalita'."""
    l = survival_to_age(p_cond)
    m = asfr * s_f
    lx = l[:len(m)]
    r0 = float((m * lx).sum())
    T = float((np.arange(len(m)) * m * lx).sum() / r0) if r0 > 0 else np.nan
    return r0, T


def lotka_r_exact(asfr: np.ndarray, p_cond: np.ndarray,
                  s_f: float = SEX_RATIO_F, lo: float = -0.2, hi: float = 0.2,
                  tol: float = 1e-12, max_iter: int = 200) -> float:
    """Radice dell'equazione caratteristica di Lotka discreta (bisezione,
    nessuna dipendenza da scipy).
        phi(r) = somma_x e^{-r (x+1)} * ASFR_x * s_f * l_x - 1
    phi e' decrescente in r: phi > 0 -> r troppo piccolo."""
    l = survival_to_age(p_cond)
    m = asfr * s_f
    lx = l[:len(m)]
    ages = np.arange(len(m)) + 1.0

    def phi(r):
        return float(np.sum(m * np.exp(-r * ages) * lx) - 1.0)

    if phi(lo) * phi(hi) > 0:
        return float("nan")
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        if abs(phi(mid)) < tol:
            return mid
        if phi(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lotka_report(verbose: bool = True) -> dict:
    from leslie import (asymptotic_halving, build_leslie_matrix,
                        dominant_eigen, load_processed)
    data = load_processed()
    F, P = data["fertility"], data["survival"]
    lam, _ = dominant_eigen(build_leslie_matrix(F, P))
    r0, T = net_reproduction(F, P)
    r_approx = float(np.log(r0) / T)
    r_exact = lotka_r_exact(F, P)

    res = {
        "R0_esatto": round(r0, 4),
        "R0_approssimato_readme": round(float(F.sum()) * SEX_RATIO_F * 0.99, 4),
        "T_generazione_anni": round(T, 2),
        "r_approx_ln_R0_su_T": round(r_approx, 6),
        "r_lotka_esatto": round(r_exact, 6),
        "ln_lambda1_leslie": round(float(np.log(lam)), 6),
        "differenza_esatto_leslie": round(abs(r_exact - float(np.log(lam))), 8),
        "t_mezzo_asintotico_anni": round(asymptotic_halving(lam), 1),
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    lotka_report()
