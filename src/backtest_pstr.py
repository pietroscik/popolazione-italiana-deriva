"""Backtest out-of-sample del PSTR (protocollo docs/06).

Disegno fixed-origin (docs/06 §1.1): stima di M0/M1/M2 su train 2001-2012
(l'anno iniziale è imposto dal PIL regionale, disponibile dal 2000),
proiezione pseudo-out-of-sample 2013-2024 (H=12), condizionata ai valori
realizzati di dlog(PIL) e DR (backtest condizionato: isola l'errore della
dinamica della fecondità dall'errore di previsione macro).

Modelli (docs/06 §2):
- M0 statico: F_{i,t} = F_{i,2012}
- M1 dinamico lineare: dF = mu + b0 F + eta dlog(PIL) + gamma DR (k=0)
- M2 PSTR: aggiunge b1 F G(F;k,theta)

Test: DM (M2 vs M0, modelli non nidificati) con errori standard cluster
per regione; Clark-West (M2 vs M1, nidificati: k->0) che aggiunge
pi^2 = (yhat_M2 - yhat_M1)^2 al differenziale di perdita.

Incertezza: cluster bootstrap sulle regioni del train (rifit a griglia
coarse) -> ensemble di traiettorie -> CRPS e coverage 95% (protocollo §3.C,
B ridotto a 20 per runtime; il protocollo dichiara B=1000 come target).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pstr_trap import _G, fit_pstr, prepare_panel  # noqa: E402

TRAIN_END = 2012
TEST_START = 2013
TEST_END = 2024
REGIME_BANDS = ((0.0, 1.35, "trappola"), (1.35, 1.65, "transizione"),
                (1.65, 10.0, "alta fecondita'"))


def load_estimation_frame():
    from download_eurostat import build_panel_long
    return prepare_panel(build_panel_long())


def fit_m1(df: pd.DataFrame, min_surf=8) -> dict:
    """M1: caso lineare (k=0) della stessa griglia - senza il termine F*G."""
    X = _design_linear(df)
    y = df["d_tfr"].values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    q = X.shape[1]
    return {"beta": beta, "ssr": float(resid @ resid),
            "n_obs": int(len(df)), "dof": q,
            "resid_std": float(np.sqrt(resid @ resid / max(len(y) - q, 1)))}


def _design_linear(df: pd.DataFrame) -> np.ndarray:
    year_dummies = pd.get_dummies(df["anno"], drop_first=True).values.astype(float)
    return np.column_stack([np.ones(len(df)), df["F_lag"].values,
                            df["d_log_gdp"].values, df["dr_lag"].values,
                            year_dummies])


def first_F_by_region(df: pd.DataFrame, year: int) -> pd.Series:
    """Livello iniziale: ultima osservazione di TFR disponibile al massimo
    entro `year` per ciascuna regione."""
    base = df[df["anno"] <= year]
    return base.sort_values("anno").groupby("geo")["tfr"].last()


def observed_F_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(index="geo", columns="anno", values="tfr")


def predict_path_m2(params: dict, F0: float, exog: pd.DataFrame) -> np.ndarray:
    """Ricorsione della mappa PSTR a partire da F0; exog con colonne d_log_gdp
    e dr_lag realizzati (backtest condizionato). Le dummies anno sono poste a
    zero out-of-sample (anno base)."""
    a, b0, b1 = params["beta"][0], params["beta"][1], params["beta"][2]
    eta, gamma = params["beta"][3], params["beta"][4]
    k, theta = params["k"], params["theta"]
    F = F0
    out = []
    for _, row in exog.iterrows():
        dF = a + b0 * F + b1 * F * _G(F, k, theta) \
            + eta * row["d_log_gdp"] + gamma * row["dr_lag"]
        F = F + dF
        out.append(F)
    return np.array(out)


def predict_path_m1(params: dict, F0: float, exog: pd.DataFrame) -> np.ndarray:
    beta = params["beta"]
    a, b0, eta, gamma = beta[0], beta[1], beta[2], beta[3]
    F = F0
    out = []
    for _, row in exog.iterrows():
        F = F + a + b0 * F + eta * row["d_log_gdp"] + gamma * row["dr_lag"]
        out.append(F)
    return np.array(out)


def exog_by_region(df: pd.DataFrame, test_start: int = TEST_START,
                   test_end: int = TEST_END) -> dict:
    """Controlli realizzati per anno di test (per-regione)."""
    sub = df[(df["anno"] >= test_start) & (df["anno"] <= test_end)]
    exog = {}
    for geo, g in sub.groupby("geo"):
        g = g.sort_values("anno")
        exog[geo] = g[["anno", "d_log_gdp", "dr_lag"]].reset_index(drop=True)
    return exog


def paired_errors(pred: dict, obs: pd.DataFrame) -> pd.Series:
    rows = []
    for geo, path in pred.items():
        for t, Fh in path.items():
            o = obs.loc[geo, t] if t in obs.columns and geo in obs.index else np.nan
            rows.append({"geo": geo, "anno": t, "err": Fh - o})
    return pd.DataFrame(rows).dropna()


def cluster_t(d: np.ndarray, groups: np.ndarray) -> tuple[float, float]:
    """t di media con errori standard cluster (per regione), approssimazione
    normale del p-value a due code."""
    n_g = len(np.unique(groups))
    means = np.array([d[groups == g].mean() for g in np.unique(groups)])
    k = n_g
    mu = means.mean()
    var = np.sum((means - mu) ** 2) / (k - 1) if k > 1 else np.nan
    se = np.sqrt(var / k)
    t = mu / se if se > 0 else np.nan
    from math import erfc, sqrt
    p = erfc(abs(t) / sqrt(2)) if np.isfinite(t) else np.nan
    return float(t), float(p)


def diebold_mariano(e_bench: pd.DataFrame, e_alt: pd.DataFrame) -> dict:
    """DM su e_bench^2 - e_alt^2, cluster per regione (positivo: alt meglio)."""
    m = e_bench.merge(e_alt, on=["geo", "anno"], suffixes=("_b", "_a"))
    d = m["err_b"] ** 2 - m["err_a"] ** 2
    t, p = cluster_t(d.values, m["geo"].values)
    return {"dm_t": round(t, 3), "dm_p": round(p, 4),
            "n": int(len(m)), "regioni": int(m["geo"].nunique())}


def _long(pred: dict) -> pd.DataFrame:
    rows = []
    for geo, path in pred.items():
        for t, F in path.items():
            rows.append({"geo": geo, "anno": t, "F_pred": F})
    return pd.DataFrame(rows)


def crps_from_ensemble(sims: np.ndarray, obs: np.ndarray) -> float:
    """CRPS campionaria (formula empirica su ensemble)."""
    n = sims.shape[0]
    order = np.sort(sims)
    crps = 0.0
    # formula: CRPS = mean|X - y| - 0.5 * mean|X - X'|
    term1 = np.mean(np.abs(order - obs))
    if n > 1:
        diffs = np.abs(order[:, None] - order[None, :])
        term2 = diffs.sum() / (n * (n - 1)) / 1.0
        # la formula integrale: 2 * sum_{i} p_i (1-p_i) ... equivalente:
        crps = term1 - 0.5 * term2
    else:
        crps = term1
    return float(crps)


def backtest_report(train_end: int = TRAIN_END, test_start: int = TEST_START,
                    test_end: int = TEST_END, boot_B: int = 20,
                    seed: int = 7, verbose: bool = True,
                    train_start: int = 2001) -> dict:
    """Backtest fixed-origin condizionato. Con i default replica il disegno
    cross-era della v1.1.x (train 2001-2012, test 2013-2024). Con
    train_end=2019, test_start=2020 esegue il disegno WITHIN-ERA della
    roadmap v1.2: stima e proiezione interamente dentro il regime
    post-2013 (il test vale solo se la costanza dei parametri e' rigettata,
    docs/15: il backtest cross-era mischiava i regimi)."""
    frame = prepare_panel_long = load_estimation_frame()
    train = frame[(frame["anno"] >= train_start)
                  & (frame["anno"] <= train_end)].reset_index(drop=True)
    F0 = first_F_by_region(frame, train_end)
    obs = observed_F_by_region(frame[(frame["anno"] >= test_start)
                                     & (frame["anno"] <= test_end)])
    exog = exog_by_region(frame, test_start, test_end)

    m2 = fit_pstr(train)
    m1 = fit_m1(train)

    pred_m0, pred_m1, pred_m2 = {}, {}, {}
    for geo in exog:
        if geo not in F0.index:
            continue
        ex = exog[geo]
        # M0: livello costante
        pred_m0[geo] = {int(r["anno"]): float(F0[geo]) for _, r in ex.iterrows()}
        pm1 = predict_path_m1(m1, float(F0[geo]), ex)
        pred_m1[geo] = {int(a): float(f) for a, f in zip(ex["anno"], pm1)}
        pm2 = predict_path_m2(m2, float(F0[geo]), ex)
        pred_m2[geo] = {int(a): float(f) for a, f in zip(ex["anno"], pm2)}

    e0 = paired_errors(pred_m0, obs)
    e1 = paired_errors(pred_m1, obs)
    e2 = paired_errors(pred_m2, obs)

    res = {
        "disegno": {"train": f"{train_start}-{train_end}",
                    "test": f"{test_start}-{test_end}",
                    "condizionato": "dlog(PIL) e DR realizzati per regione"},
        "rmse": {
            "M0_statico": float(np.sqrt((e0["err"] ** 2).mean())),
            "M1_lineare": float(np.sqrt((e1["err"] ** 2).mean())),
            "M2_pstr": float(np.sqrt((e2["err"] ** 2).mean())),
        },
        "mae": {
            "M0_statico": float(e0["err"].abs().mean()),
            "M1_lineare": float(e1["err"].abs().mean()),
            "M2_pstr": float(e2["err"].abs().mean()),
        },
        "dm_m2_vs_m0": diebold_mariano(e0, e2),
        "dm_m1_vs_m0": diebold_mariano(e0, e1),
    }

    # Clark-West: M1 (benchmark nidificato) vs M2
    pb = _long(pred_m1).rename(columns={"F_pred": "F_m1"})
    pa = _long(pred_m2).rename(columns={"F_pred": "F_m2"})
    m = pb.merge(pa, on=["geo", "anno"]).merge(e1.rename(columns={"err": "e1"}),
                                              on=["geo", "anno"])
    m = m.merge(e2.rename(columns={"err": "e2"}), on=["geo", "anno"])
    pi = m["F_m2"] - m["F_m1"]
    d_cw = m["e1"] ** 2 - (m["e2"] ** 2 - pi ** 2)
    t, p = cluster_t(d_cw.values, m["geo"].values)
    res["clark_west_m2_vs_m1"] = {"cw_t": round(t, 3), "cw_p": round(p, 4),
                                  "n": int(len(m))}

    # Stratificazione per regime (F al 2012)
    strat = {}
    for lo, hi, name in REGIME_BANDS:
        geos = [g for g in F0.index if lo <= F0[g] < hi and g in pred_m2]
        sel = e2[e2["geo"].isin(geos)]
        sel0 = e0[e0["geo"].isin(geos)]
        sel1 = e1[e1["geo"].isin(geos)]
        if len(sel) < 20:
            continue
        strat[name] = {
            "n_regioni": len(geos),
            "rmse_M0": float(np.sqrt((sel0["err"] ** 2).mean())),
            "rmse_M1": float(np.sqrt((sel1["err"] ** 2).mean())),
            "rmse_M2": float(np.sqrt((sel["err"] ** 2).mean())),
        }
    res["regimi_f_2012"] = strat

    # Ensemble bootstrap (cluster sulle regioni, griglia coarse, B ridotto)
    rng = np.random.default_rng(seed)
    geos_train = train["geo"].unique()
    sims_by_pair = {}
    for b in range(boot_B):
        pick = rng.choice(geos_train, size=len(geos_train), replace=True)
        sample = pd.concat([train[train["geo"] == g] for g in pick],
                           ignore_index=True)
        coarse = np.round(np.arange(1.15, 2.01, 0.05), 2)
        try:
            fit_b = fit_pstr(sample, theta_grid=coarse)
        except Exception:
            continue
        for geo, ex in exog.items():
            if geo not in F0.index:
                continue
            pb2 = predict_path_m2(fit_b, float(F0[geo]), ex)
            for a, f in zip(ex["anno"], pb2):
                sims_by_pair.setdefault((geo, int(a)), []).append(f)

    crps_list, covered, total = [], 0, 0
    for (geo, a), sims in sims_by_pair.items():
        o = obs.loc[geo, a] if (geo in obs.index and a in obs.columns) else None
        if o is None or np.isnan(o):
            continue
        s = np.array(sims)
        crps_list.append(crps_from_ensemble(s, o))
        lo, hi = np.quantile(s, 0.025), np.quantile(s, 0.975)
        total += 1
        covered += int(lo <= o <= hi)
    if crps_list:
        res["crps"] = {"media": float(np.mean(crps_list)),
                       "B": boot_B,
                       "nota": "B ridotto per runtime; protocollo target B=1000"}
        res["coverage_95"] = {"rate": round(covered / total, 3), "n": total}

    res["expanding_h1"] = expanding_window_h1(frame)

    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


def expanding_window_h1(frame: pd.DataFrame) -> dict:
    """Secondo disegno del protocollo (docs/06 §1.2): expanding window,
    orizzonte h=1. A ogni anno test t si ristima su tutto il campione
    disponibile fino a t-1 (griglia coarse) e si prevede dF_t dalla mappa
    con F_{t-1} osservato. Verifica se l'orizzonte corto premia la
    non-linearita' anche quando il fisso-12-passi non la premia."""
    coarse = np.round(np.arange(1.15, 2.01, 0.05), 2)
    rows = []
    for t in range(TEST_START, TEST_END + 1):
        train = frame[frame["anno"] < t].reset_index(drop=True)
        test = frame[frame["anno"] == t].reset_index(drop=True)
        if len(test) < 30 or len(train) < 300:
            continue
        m2 = fit_pstr(train, theta_grid=coarse)
        m1 = fit_m1(train)
        beta2 = m2["beta"]
        for _, row in test.iterrows():
            F = row["F_lag"]
            e0 = F - row["tfr"]
            F1 = F + (m1["beta"][0] + m1["beta"][1] * F
                      + m1["beta"][2] * row["d_log_gdp"]
                      + m1["beta"][3] * row["dr_lag"])
            F2 = F + (beta2[0] + beta2[1] * F
                      + beta2[2] * F * _G(F, m2["k"], m2["theta"])
                      + beta2[3] * row["d_log_gdp"]
                      + beta2[4] * row["dr_lag"])
            rows.append({"geo": row["geo"], "anno": t,
                         "e0": e0, "e1": F1 - row["tfr"],
                         "e2": F2 - row["tfr"],
                         "pi": F2 - F1})
    df = pd.DataFrame(rows)
    out = {
        "rmse": {"M0_statico": float(np.sqrt((df["e0"] ** 2).mean())),
                 "M1_lineare": float(np.sqrt((df["e1"] ** 2).mean())),
                 "M2_pstr": float(np.sqrt((df["e2"] ** 2).mean()))},
    }
    dm = diebold_mariano(df.rename(columns={"e0": "err"})[["geo", "anno", "err"]],
                         df.rename(columns={"e2": "err"})[["geo", "anno", "err"]])
    out["dm_m2_vs_m0"] = dm
    d_cw = df["e1"] ** 2 - (df["e2"] ** 2 - df["pi"] ** 2)
    t, p = cluster_t(d_cw.values, df["geo"].values)
    out["clark_west_m2_vs_m1"] = {"cw_t": round(t, 3), "cw_p": round(p, 4),
                                  "n": int(len(df))}
    return out


if __name__ == "__main__":
    if "--within-era" in sys.argv:
        # roadmap v1.2: stima e test interamente nel regime post-2013
        backtest_report(train_start=2013, train_end=2019, test_start=2020,
                        test_end=2024, boot_B=20)
    else:
        backtest_report(boot_B=20)
