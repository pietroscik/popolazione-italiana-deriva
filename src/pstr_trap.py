"""PSTR - stima della soglia theta della Low Fertility Trap.

Specificazione (docs/05, par. 5): il TFR diventa variabile di stato endogena.
Equazione in forma dinamica (panel NUTS-2 europeo, pooled con dummies anno):

    dF_{i,t} = a + b0 * F_{i,t-1} + b1 * F_{i,t-1} * G(F_{i,t-1}; k, theta)
               + eta * dlog_gdp_{i,t-1} + dummies_anno + eps_{i,t}

con G logistica (PSTR, Gonzalez-Teravirta-van Dijk) e transizione sulla
variabile di stato stessa (feedback del fertility trap):

    G(q; k, theta) = 1 / (1 + exp(-k (q - theta)))

Perche' pooled e non con effetti fissi paese: gli attrattori multipli sono
ipotesi sui LIVELLI; il within (FE) assorbe nella costante il punto di
equilibrio di ciascun paese e cancella proprio l'informazione necessaria a
identificare la mappa globale. Gli shock comuni europei (COVID, inflazione)
sono rimossi con le dummies anno.

Stima: minimi quadrati concentrati - dati (k, theta) su griglia, i parametri
lineari si risolvono con OLS. (k, theta) ottimali = minimo della SSR.

Letture della trappola: dalla mappa implicita F_{t+1} = F_t + f_hat(F)
(si ignorano controlli e dummies, a regime medio) si cercano gli equilibri
f_hat(F) = 0; stabile se f_hat'(F*) < 0, instabile (soglia di non ritorno
verso il basso) se f_hat'(F*) > 0.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

THETA_GRID = np.round(np.arange(1.10, 2.06, 0.02), 2)
K_GRID = np.exp(np.arange(np.log(0.5), np.log(60.0), 0.20))
CONTROLS = ["d_log_gdp", "dr_lag"]


def _G(q, k, theta):
    return 1.0 / (1.0 + np.exp(-k * (q - theta)))


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["geo", "anno"]).copy()
    df["d_tfr"] = df.groupby("geo")["tfr"].diff()
    df["F_lag"] = df.groupby("geo")["tfr"].shift(1)
    df["gdp_lag"] = df.groupby("geo")["gdp_pc"].shift(1)
    df["d_log_gdp"] = np.log(df["gdp_lag"]).diff()
    if "dr" in df.columns:
        df["dr_lag"] = df.groupby("geo")["dr"].shift(1)
    else:
        df["dr_lag"] = 0.3
    df = df.dropna(subset=["d_tfr", "F_lag", "d_log_gdp", "dr_lag"])
    return df.reset_index(drop=True)


def _design(df, k, theta):
    F = df["F_lag"].values
    year_dummies = pd.get_dummies(df["anno"], drop_first=True).values.astype(float)
    X = np.column_stack([np.ones(len(df)), F, F * _G(F, k, theta),
                         df["d_log_gdp"].values, df["dr_lag"].values,
                         year_dummies])
    return X


def fit_pstr(df: pd.DataFrame, theta_grid=THETA_GRID, k_grid=K_GRID) -> dict:
    y = df["d_tfr"].values
    means = {c: float(df[c].mean()) for c in CONTROLS}
    best = None
    for theta in theta_grid:
        for k in k_grid:
            X = _design(df, k, theta)
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            resid = y - X @ beta
            ssr = float(resid @ resid)
            if best is None or ssr < best["ssr"]:
                best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                        "beta": beta}
    best["control_means"] = means
    best["n_obs"] = int(len(df))
    best["n_regioni"] = int(df["geo"].nunique())
    best["resid_std"] = float(np.sqrt(best["ssr"] / max(len(df) - 30, 1)))
    return best


def implied_map(best: dict, F_grid=None):
    if F_grid is None:
        F_grid = np.linspace(0.7, 3.5, 561)
    a, b0, b1, eta_dlgdp, gamma_dr = best["beta"][:5]
    k, theta = best["k"], best["theta"]
    means = best.get("control_means", {"d_log_gdp": 0.0, "dr_lag": 0.0})
    offset = eta_dlgdp * means["d_log_gdp"] + gamma_dr * means["dr_lag"]
    return F_grid, a + offset + b0 * F_grid + b1 * F_grid * _G(F_grid, k, theta)


def equilibrium_points(best: dict):
    F_grid, f = implied_map(best)
    roots = []
    for i in range(len(F_grid) - 1):
        if f[i] * f[i + 1] < 0:
            Fr = float(F_grid[i] - f[i] * (F_grid[i + 1] - F_grid[i]) /
                       (f[i + 1] - f[i]))
            slope = (f[i + 1] - f[i]) / (F_grid[i + 1] - F_grid[i])
            roots.append((Fr, "stabile" if slope < 0 else "instabile"))
    return roots


def bootstrap_theta(df: pd.DataFrame, B: int = 40, seed: int = 7) -> dict:
    """Cluster bootstrap sulle regioni (preserva la correlazione seriale)."""
    rng = np.random.default_rng(seed)
    geos = df["geo"].unique()
    thetas, ks, unstable_roots = [], [], []
    coarse_theta = np.round(np.arange(1.15, 2.01, 0.05), 2)
    for _ in range(B):
        pick = rng.choice(geos, size=len(geos), replace=True)
        sample = pd.concat([df[df["geo"] == g] for g in pick],
                            ignore_index=True)
        res = fit_pstr(sample, theta_grid=coarse_theta)
        thetas.append(res["theta"])
        ks.append(res["k"])
        roots = equilibrium_points(res)
        unstable_roots.append(min([f for f, t in roots if t == "instabile"],
                                  default=np.nan))
    thetas = np.array(thetas)
    unstable_roots = np.array([r for r in unstable_roots if not np.isnan(r)])
    return {
        "B": B,
        "theta_media": float(thetas.mean()),
        "theta_std": float(thetas.std()),
        "theta_q05": float(np.quantile(thetas, 0.05)),
        "theta_q95": float(np.quantile(thetas, 0.95)),
        "soglia_instabile_media": float(unstable_roots.mean()) if len(unstable_roots) else None,
        "n_bootstrap_con_soglia": int(len(unstable_roots)),
    }


def pstr_report(boot: bool = True, verbose: bool = True) -> dict:
    from download_eurostat import build_panel

    df = prepare_panel(build_panel())
    best = fit_pstr(df)
    roots = equilibrium_points(best)
    res = {
        "stima": {k: v for k, v in best.items() if k != "beta"},
        "beta": {"a": float(best["beta"][0]),
                 "b0_F": float(best["beta"][1]),
                 "b1_FxG": float(best["beta"][2]),
                 "eta_d_log_gdp": float(best["beta"][3]),
                 "gamma_DR": float(best["beta"][4])},
        "equilibri": [{"F": round(f, 3), "tipo": t} for f, t in roots],
        "n_equilibri": len(roots),
        "bootstrap": bootstrap_theta(df) if boot else None,
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    pstr_report(boot="--no-boot" not in sys.argv)
