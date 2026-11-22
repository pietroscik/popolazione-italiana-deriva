"""Curva migratoria per eta' ( modello Rogers-Castro ) e calibrazione del saldo.

Costruisce il profilo dei tassi di migrazione netta per eta' (14-80+) con la
parametrizzazione Rogers-Castro a 11 parametri (famiglia a 7 + picco pensionistico),
poi calibra il livello totale per ottenere un saldo migratorio annuo prefissato.
"""

import numpy as np

MAX_AGE = 100


def rogers_castro_rates(ages: np.ndarray,
                        a1: float = 0.02, alpha1: float = 0.15,
                        a2: float = 0.10, alpha2: float = 0.05,
                        mu2: float = 25.0, lam2: float = 0.50,
                        c: float = 0.003, lambda3: float = 0.10,
                        x3: float = 65.0, lambda4: float = 0.50) -> np.ndarray:
    """Tassi relativi (forma, non calibrata) del modello Rogers-Castro.

    m(x) = a1 exp(-a1*x)  [infanzia]
         + a2 exp(-alpha2 (x-mu2) - exp(-lam2 (x-mu2)))  [picco forza lavoro]
         + c (1 + exp(-lambda3 (x - x3) - exp(-lambda4 (x - x3))) - ...)  [picco pensionistico]
    """
    x = np.asarray(ages, dtype=float)
    child = a1 * np.exp(-alpha1 * x)
    dx2 = x - mu2
    labor = a2 * np.exp(-alpha2 * dx2 - np.exp(-lam2 * dx2))
    dx4 = x - x3
    retire = c * np.exp(-lambda3 * dx4 - np.exp(-lambda4 * dx4))
    return child + labor + retire


def build_migration_profile(n_by_age: np.ndarray, net_total: float,
                            max_age: int = MAX_AGE) -> np.ndarray:
    """Vettore di migranti netti per eta' con saldo annuo pari a net_total.

    Distribuisce il saldo secondo il profilo Rogers-Castro, pesato per la
    popolazione residente di ciascuna eta' (le migrazioni seguono le coorti
    piu' numerose la' dove i tassi sono alti).
    """
    ages = np.arange(max_age + 1)
    shape = rogers_castro_rates(ages)
    shape[shape < 0] = 0.0
    weight = shape * np.maximum(n_by_age, 0.0)
    if weight.sum() <= 0:
        weight = np.ones_like(shape)
    share = weight / weight.sum()
    return net_total * share


def saldo_for_constant_population(simulate_fn, lo: float = 0.0, hi: float = 600_000,
                                   tol: float = 500.0, max_iter: int = 40) -> float:
    """Bisezione sul saldo migratorio annuo che azzera la crescita della popolazione.

    simulate_fn(saldo) deve restituire la variazione percent della popolazione
    sull'orizzonte considerato.
    """
    def f(s):
        return simulate_fn(s)

    if f(lo) * f(hi) > 0:
        return float("nan")
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        val = f(mid)
        if abs(val) < tol:
            return mid
        if val * f(lo) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
