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
import math
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
    # nei panel sbilanciati: lag e differenze valide solo tra anni
    # consecutivi — un buco temporale non deve produrre diff a orizzonte misto
    gap = df.groupby("geo")["anno"].diff()
    consecutive = gap.eq(1)
    df["d_tfr"] = df.groupby("geo")["tfr"].diff()
    df["F_lag"] = df.groupby("geo")["tfr"].shift(1)
    df["gdp_lag"] = df.groupby("geo")["gdp_pc"].shift(1)
    df["d_log_gdp"] = np.log(df["gdp_lag"]).groupby(df["geo"]).diff()
    df.loc[~consecutive, ["d_tfr", "F_lag", "gdp_lag", "d_log_gdp"]] = np.nan
    if "dr" in df.columns:
        df["dr_lag"] = df.groupby("geo")["dr"].shift(1)
    else:
        df["dr_lag"] = 0.3
    df = df.dropna(subset=["d_tfr", "F_lag", "d_log_gdp", "dr_lag"])
    if "dr_t15" in df.columns:
        df["_has_iv"] = df["dr_t15"].notna()
    return df.reset_index(drop=True)


def _design(df, k, theta):
    F = df["F_lag"].values
    year_dummies = pd.get_dummies(df["anno"], drop_first=True).values.astype(float)
    X = np.column_stack([np.ones(len(df)), F, F * _G(F, k, theta),
                         df["d_log_gdp"].values, df["dr_lag"].values,
                         year_dummies])
    return X, year_dummies


def fit_pstr(df: pd.DataFrame, theta_grid=THETA_GRID, k_grid=K_GRID) -> dict:
    y = df["d_tfr"].values
    means = {c: float(df[c].mean()) for c in CONTROLS}
    best = None
    dummy_share = None
    for theta in theta_grid:
        for k in k_grid:
            X, year_dummies = _design(df, k, theta)
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            resid = y - X @ beta
            ssr = float(resid @ resid)
            if best is None or ssr < best["ssr"]:
                best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                        "beta": beta}
                dummy_share = year_dummies.mean(axis=0)
    best["control_means"] = means
    best["dummy_share"] = dummy_share
    best["n_obs"] = int(len(df))
    best["n_regioni"] = int(df["geo"].nunique())
    best["resid_std"] = float(np.sqrt(best["ssr"] / max(len(df) - 30, 1)))
    return best


def implied_map(best: dict, F_grid=None):
    if F_grid is None:
        F_grid = np.linspace(0.4, 3.5, 621)
    a, b0, b1, eta_dlgdp, gamma_dr = best["beta"][:5]
    k, theta = best["k"], best["theta"]
    means = best.get("control_means", {})
    offset = eta_dlgdp * means.get("d_log_gdp", 0.0) + gamma_dr * means.get("dr_lag", 0.0)
    beta_dummies = best["beta"][5:]
    share = best.get("dummy_share")
    if share is not None and len(beta_dummies) == len(share):
        # effetto medio delle dummies anno sulle osservazioni del panel
        # (la dummy dell'anno base e' implicitamente 0)
        offset += float(beta_dummies @ share)
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


def fit_pstr_iv(df: pd.DataFrame, theta_grid=THETA_GRID,
               k_grid=K_GRID) -> dict:
    """2SLS concentrato: come fit_pstr ma con la DR strumentata da dr_t15.

    La DR di oggi e' costruita dalle nascite di 15-65 anni orsono: e'
    meccanicamente correlata con la fertilita' storica della regione e con
    gli errori dell'equazione del TFR (endogeneita' meccanica, docs/13
    par. 5.1). La DR osservata 15 anni prima e' predeterminata rispetto
    agli shock recenti del TFR (protocollo docs/06, appendice B).

    Per ogni (k, theta) sulla griglia: il primo stadio proietta dr_lag
    sugli strumenti (tutti i regressori ma con dr_t15 al posto di dr_lag);
    il secondo stima beta sulla proiezione. La selezione sulla griglia
    minimizza la SSR strutturale 2SLS. Statistica F parziale del primo
    stadio per l'esclusione dello strumento (regola empirica: F > 10)."""
    y = df["d_tfr"].values
    dr = df["dr_lag"].values
    z = df["dr_t15"].values
    best = None
    for theta in theta_grid:
        for k in k_grid:
            X, _ = _design(df, k, theta)
            Z = X.copy()
            Z[:, 4] = z
            # primo stazio: dr_lag su Z
            pi, *_ = np.linalg.lstsq(Z, dr, rcond=None)
            dr_hat = Z @ pi
            # F parziale del primo stadio: modello ristretto senza lo
            # strumento (solo regressori esogeni) vs modello completo
            W = np.delete(X, 4, axis=1)
            beta_r, *_ = np.linalg.lstsq(W, dr, rcond=None)
            resid_r = dr - W @ beta_r
            ssr_r = float(resid_r @ resid_r)
            resid1 = dr - dr_hat
            ssr_f = float(resid1 @ resid1)
            q = Z.shape[1]
            if ssr_f <= 0 or len(dr) - q <= 0:
                continue
            F1 = (ssr_r - ssr_f) / ssr_f * (len(dr) - q)
            # secondo stadio
            X_hat = X.copy()
            X_hat[:, 4] = dr_hat
            beta_iv, *_ = np.linalg.lstsq(X_hat, y, rcond=None)
            resid = y - X @ beta_iv
            ssr = float(resid @ resid)
            if best is None or ssr < best["ssr"]:
                best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                        "beta": beta_iv, "first_stage_F": float(F1)}
    best["control_means"] = {c: float(df[c].mean()) for c in CONTROLS}
    X_opt, _ = _design(df, best["k"], best["theta"])
    best["dummy_share"] = X_opt[:, 5:].mean(axis=0)
    best["n_obs"] = int(len(df))
    best["n_regioni"] = int(df["geo"].nunique())
    return best


def fit_pstr_iv2(df: pd.DataFrame, theta_grid=THETA_GRID,
                k_grid=K_GRID) -> dict:
    """2SLS a DUE strumenti: dr_t15 e dr_t20 (roadmap v1.2, punto 1).

    Con due strumenti e un solo regressore endogeno il modello e'
    sovraidentificato di 1: l'ipotesi di validita' conjunta degli strumenti
    diventa testabile con la statistica J di Hansen (robusta all'
    eteroschedasticita', df=1, p-value via erfc — niente scipy).

    ATTENZIONE (lettura pre-registrata): il test J non convalida lo
    strumento t-15 da solo — testa la congruenza reciproca di t-15 e t-20.\n    Se entrambi violano l'esclusione nello stesso verso (norme familiari
    regionali persistenti che correlano DR storica e errori del TFR di
    oggi), il J NON li respinge: la causalita' di gamma resta aperta in
    ogni caso (v. docs/13 par. 5.1). Un rifiuto, invece, sarebbe informativo:
    almeno uno dei due strumento non e' congruente con l'altro.

    Primo stadio congiunto per l'esclusione di ENTRAMBI gli strumenti
    (F parziale congiunto), secondo stadio 2SLS standard.
    """
    y = df["d_tfr"].values
    dr = df["dr_lag"].values
    z15 = df["dr_t15"].values
    z20 = df["dr_t20"].values
    best = None
    n = len(df)
    for theta in theta_grid:
        for k in k_grid:
            X, _ = _design(df, k, theta)
            exog = np.delete(X, 4, axis=1)
            Z = np.column_stack([exog, z15, z20])
            # primo stadio congiunto
            pi, *_ = np.linalg.lstsq(Z, dr, rcond=None)
            dr_hat = Z @ pi
            resid1 = dr - dr_hat
            ssr_f = float(resid1 @ resid1)
            beta_r, *_ = np.linalg.lstsq(exog, dr, rcond=None)
            resid_r = dr - exog @ beta_r
            ssr_r = float(resid_r @ resid_r)
            q = Z.shape[1]
            if ssr_f <= 0 or n - q <= 0:
                continue
            # F parziale congiunto (2 restrizioni)
            F1 = ((ssr_r - ssr_f) / 2.0) / (ssr_f / (n - q))
            # secondo stadio
            X_hat = X.copy()
            X_hat[:, 4] = dr_hat
            beta_iv, *_ = np.linalg.lstsq(X_hat, y, rcond=None)
            resid = y - X @ beta_iv
            ssr = float(resid @ resid)
            if best is None or ssr < best["ssr"]:
                # Hansen J robusto: g_i = z_i * u_i su TUTTI gli strumenti
                g = Z * resid[:, None]          # (n, q)
                gbar = g.mean(axis=0)
                S = (g.T @ g) / n                # (q, q)
                try:
                    S_inv = np.linalg.pinv(S)
                except np.linalg.LinAlgError:
                    continue
                J = float(n * gbar @ S_inv @ gbar)
                # p-value chi2 con 1 g.d.l.: sf(x) = erfc(sqrt(x/2))
                p_J = math.erfc(math.sqrt(max(J, 0.0) / 2.0))
                best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                        "beta": beta_iv, "first_stage_F": float(F1),
                        "hansen_J": J, "hansen_J_df": 1,
                        "hansen_J_p": float(p_J)}
    best["control_means"] = {c: float(df[c].mean()) for c in CONTROLS}
    X_opt, _ = _design(df, best["k"], best["theta"])
    best["dummy_share"] = X_opt[:, 5:].mean(axis=0)
    best["n_obs"] = int(len(df))
    best["n_regioni"] = int(df["geo"].nunique())
    return best


def loco_by_country(df: pd.DataFrame, theta_grid=THETA_GRID,
                    k_grid=K_GRID) -> dict:
    """Robustezza LOCO (leave-one-country-out) per la stima pooled.

    Esclude iterativamente ciascun paese (prefisso ISO a 2 caratteri del
    codice NUTS-2) e ristima (k, theta) e gamma_DR."""
    df = df.copy()
    df["paese"] = df["geo"].str[:2]
    freq = df["paese"].value_counts()
    records = []
    for paese in freq.index:
        sub = df[df["paese"] != paese]
        if sub["geo"].nunique() < 20:
            continue
        try:
            res = fit_pstr(sub, theta_grid=theta_grid, k_grid=k_grid)
        except Exception:
            continue
        records.append({"paese_escluso": paese,
                        "n_regioni": res["n_regioni"],
                        "theta": res["theta"], "k": res["k"],
                        "gamma_DR": float(res["beta"][4]),
                        "eta_d_log_gdp": float(res["beta"][3]),
                        "equilibri": [(round(f, 3), t)
                                       for f, t in equilibrium_points(res)]})
    thetas = [r["theta"] for r in records]
    gammas = [r["gamma_DR"] for r in records]
    return {
        "n_propri": len(records),
        "theta_min": float(min(thetas)), "theta_max": float(max(thetas)),
        "gamma_DR_min": float(min(gammas)), "gamma_DR_max": float(max(gammas)),
        "per_paese": records,
    }



def fit_pstr_mundlak(df: pd.DataFrame, theta_grid=THETA_GRID,
                     k_grid=K_GRID) -> dict:
    """CRE/Mundlak: pooled + medie regionali dei regressori come controlli.

    Corregge il canale di eterogeneita' regionale permanente correlata con
    F_lag (la versione pooled del problema del panel dinamico; docs/13 S6)
    senza assorbire i livelli nel fixed effect: la scelta identificativa
    sulla mappa globale resta intatta e il coefficiente sulle medie regionali
    quantifica l'eterogeneita' assorbita (attesa positiva su media-F)."""
    y = df["d_tfr"].values
    mF = df.groupby("geo")["F_lag"].transform("mean").values
    mG = df.groupby("geo")["d_log_gdp"].transform("mean").values
    mD = df.groupby("geo")["dr_lag"].transform("mean").values
    best = None
    for theta in theta_grid:
        for k in k_grid:
            F = df["F_lag"].values
            X, _ = _design(df, k, theta)
            X = np.column_stack([X, mF, mG, mD])
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            resid = y - X @ beta
            ssr = float(resid @ resid)
            if best is None or ssr < best["ssr"]:
                best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                        "beta": beta}
    best["mundlak"] = {"media_F": float(best["beta"][-3]),
                       "media_dlog_gdp": float(best["beta"][-2]),
                       "media_dr": float(best["beta"][-1])}
    best["control_means"] = {c: float(df[c].mean()) for c in CONTROLS}
    best["n_obs"] = int(len(df))
    return best


def theta_stability_battery(df: pd.DataFrame) -> dict:
    """Batteria di stabilita' della soglia (robustezza, audit P1):
    theta, gamma_DR e soglia instabile (anno base) attraverso le
    specificazioni. La soglia 0,91 va letta con questa batteria, non come
    costante strutturale (v. docs/13 S4)."""
    res = {}
    # 1. headline senza DR
    nd = df.copy()
    nd["dr_lag"] = 0.0
    f1 = fit_pstr(nd)
    res["senza_dr"] = {"theta": f1["theta"], "gamma": None}
    # 2. con DR
    f2 = fit_pstr(df)
    res["con_dr"] = {"theta": f2["theta"], "gamma": float(f2["beta"][4])}
    # 3. CRE/Mundlak
    f3 = fit_pstr_mundlak(df)
    res["mundlak_cre"] = {"theta": f3["theta"],
                          "gamma": float(f3["beta"][4])}
    # 4. kinked (DR0 profilato)
    f4 = fit_pstr_kinked(df)
    res["kinked"] = {"theta": f4["theta"],
                     "gamma": float(f4["gamma_kinked"]),
                     "dr0": f4["dr0"]}
    # 5. IV t-15 (se lo strumento e' presente)
    if "dr_t15" in df.columns:
        div = df.dropna(subset=["dr_t15"]).reset_index(drop=True)
        if len(div) > 500:
            f5 = fit_pstr_iv(div)
            res["iv_t15"] = {"theta": f5["theta"],
                             "gamma_iv": float(f5["beta"][4])}
    # 5-bis. IV a due strumenti t-15 + t-20 (Hansen J testabile, v1.2)
    if {"dr_t15", "dr_t20"}.issubset(df.columns):
        div2 = df.dropna(subset=["dr_t15", "dr_t20"])
        div2 = div2.dropna(subset=["d_tfr", "F_lag", "d_log_gdp",
                                   "dr_lag"]).reset_index(drop=True)
        if len(div2) > 500:
            f5b = fit_pstr_iv2(div2)
            res["iv_t15_t20"] = {
                "theta": f5b["theta"],
                "gamma_iv": float(f5b["beta"][4]),
                "first_stage_F": f5b["first_stage_F"],
                "hansen_J": f5b["hansen_J"],
                "hansen_J_p": f5b["hansen_J_p"],
                "n_obs": f5b["n_obs"]}
    # 6. finestra estesa 2013-2024 (panel lungo)
    ext = df[df["anno"] >= 2013]
    if len(ext) > 1500:
        f6 = fit_pstr(ext.reset_index(drop=True))
        res["finestra_2013_2024"] = {"theta": f6["theta"],
                                     "gamma": float(f6["beta"][4])}
    return res


DR0_GRID = np.round(np.arange(0.20, 0.46, 0.01), 2)


def fit_pstr_kinked(df: pd.DataFrame, theta_grid=THETA_GRID,
                    k_grid=K_GRID, dr0_grid=DR0_GRID) -> dict:
    """Test discriminante della forma attesa dalla teoria (docs/05, eq. di
    Phi): gamma * max(0, DR - DR0). La teoria prevede che il freno fiscale
    si accenda SOLO oltre la soglia DR0; le letture alternative (rimbalzo
    post-rinvio, Myrskyla-Kohler-Billari) implicano un effetto positivo al
    livello, cioe' gamma_lineare > 0 anche senza kink.

    Concentrated LS 3D su (k, theta, DR0): la forma kinked sostituisce
    dr_lag con max(0, dr_lag - DR0). Confronto: gamma_delivira il segno
    del freno oltre DR0. Se il minimo e' a DR0 al bordo INFERIORE della
    griglia e gamma>0, la forma kinked non compra nulla: il livello
    spiega tutto (lettura rebound)."""
    y = df["d_tfr"].values
    dr = df["dr_lag"].values
    best = None
    for theta in theta_grid:
        for k in k_grid:
            X0, _ = _design(df, k, theta)
            exog = X0[:, [0, 1, 2, 3]]
            dummies = X0[:, 5:]
            for dr0 in dr0_grid:
                ex = np.column_stack([exog, np.maximum(0.0, dr - dr0), dummies])
                beta, *_ = np.linalg.lstsq(ex, y, rcond=None)
                resid = y - ex @ beta
                ssr = float(resid @ resid)
                if best is None or ssr < best["ssr"]:
                    best = {"ssr": ssr, "k": float(k), "theta": float(theta),
                            "dr0": float(dr0),
                            "gamma_kinked": float(beta[4]),
                            "eta": float(beta[3]), "b1": float(beta[2]),
                            "b0": float(beta[1]), "a": float(beta[0])}
    best["control_means"] = {c: float(df[c].mean()) for c in CONTROLS}
    best["n_obs"] = int(len(df))
    return best


def bootstrap_theta(df: pd.DataFrame, B: int = 399, seed: int = 7) -> dict:
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
        # conteggio della soglia a regime ad anno base (ambiente costante):
        # al regime medio il panel 2013-2023 non ha incroci interni di
        # per se' (effetti 2022-23), sarebbe un conteggio sempre vuoto
        base_year = dict(res)
        base_year["dummy_share"] = np.zeros(len(res["beta"]) - 5)
        roots = equilibrium_points(base_year)
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


def pstr_report(boot: bool = True, verbose: bool = True,
                panel: str = "2013") -> dict:
    if panel == "1990":
        from download_eurostat import build_panel_long
        raw = build_panel_long()
    else:
        from download_eurostat import build_panel
        raw = build_panel()

    df = prepare_panel(raw)
    best = fit_pstr(df)
    roots = equilibrium_points(best)
    res = {
        "panel": panel,
        "stima": {k: v for k, v in best.items()
                  if k not in ("beta", "dummy_share")},
        "beta": {"a": float(best["beta"][0]),
                 "b0_F": float(best["beta"][1]),
                 "b1_FxG": float(best["beta"][2]),
                 "eta_d_log_gdp": float(best["beta"][3]),
                 "gamma_DR": float(best["beta"][4])},
        "equilibri": [{"F": round(f, 3), "tipo": t} for f, t in roots],
        "n_equilibri": len(roots),
        "bootstrap": bootstrap_theta(df) if boot else None,
    }
    # La mappa include l'effetto medio delle dummies anno (regime medio, che
    # nel 2013-2023 e' dominato dagli effetti 2022-23, molto negativi): con
    # quell'offset la dinamica recente non ha incroci interni. Si riporta
    # anche il regime ad anno base (ambiente costante, dummies = 0).
    base_year = dict(best)
    base_year["dummy_share"] = np.zeros(len(best["beta"]) - 5)
    res["equilibri_anno_base"] = [{"F": round(f, 3), "tipo": t}
                                   for f, t in equilibrium_points(base_year)]
    if "dr_t15" in df.columns and df["dr_t15"].notna().sum() > 200:
        df_iv = df.dropna(subset=["dr_t15"]).reset_index(drop=True)
        iv = fit_pstr_iv(df_iv)
        res["strumento_iv_dr_t15"] = {
            "n_obs": iv["n_obs"],
            "theta": iv["theta"], "k": iv["k"],
            "gamma_DR_iv": float(iv["beta"][4]),
            "eta_d_log_gdp_iv": float(iv["beta"][3]),
            "first_stage_F": iv.get("first_stage_F"),
            "equilibri": [{"F": round(f, 3), "tipo": t}
                          for f, t in equilibrium_points(iv)],
        }
        res["loco"] = loco_by_country(df)
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    pstr_report(boot="--no-boot" not in sys.argv,
                panel="1990" if "--panel-1990" in sys.argv else "2013")


def theta_structural_battery(df: pd.DataFrame, windows=None, B: int = 99,
                             seed: int = 7) -> dict:
    """Batteria strutturale della soglia (roadmap v1.2, punto 3).

    Per ciascuna finestra: stima puntuale, bootstrap a cluster sulle regioni
    (con supporto della soglia instabile a regime anno-base) e misura di
    TANGENZA della mappa implicita nella banda F in [0,85; 1,10]: se
    |f(F)| e' molto piccolo l'esistenza dell'attraversamento e' dentro il
    rumore campionario e la soglia varia con l'offset (docs/13 par. 5.7).
    """
    if windows is None:
        windows = [(2001, 2012), (2013, 2024), (2013, 2018), (2019, 2024)]
    out = {}
    F_grid, err_band = np.linspace(0.4, 3.5, 621), []
    for lo, hi in windows:
        d = df[(df["anno"] >= lo) & (df["anno"] <= hi)].reset_index(drop=True)
        if len(d) < 500:
            continue
        f = fit_pstr(d)
        base = dict(f)
        base["dummy_share"] = np.zeros(len(f["beta"]) - 5)
        _, m = implied_map(base)
        band = m[(F_grid >= 0.85) & (F_grid <= 1.10)]
        boot = bootstrap_theta(d, B=B, seed=seed)
        out[f"{lo}-{hi}"] = {
            "n": int(len(d)),
            "theta": float(f["theta"]),
            "theta_q05": boot["theta_q05"],
            "theta_q95": boot["theta_q95"],
            "supporto_soglia_pct": round(100.0 * boot["n_bootstrap_con_soglia"]
                                         / max(boot["B"], 1), 1),
            "map_abs_max_f_0.85_1.10": float(np.abs(band).max()),
            "radici_base": [(float(a), b) for a, b in equilibrium_points(base)],
        }
    return out
