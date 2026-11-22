"""Fase 3 - Screening predittivo del TFR sul panel Europeo NUTS-2.

Pipeline (step 1-2 dell'architettura a due strati, docs/04):
- lag within-regione e creazione feature
- variante "within" con two-way demeaning (rimozione media regionale e annua:
  effetti fissi territoriali e shock macro nazionali/ europei)
- XGBoost + TreeSHAP nativo (pred_contribs) per il ranking delle direttrici

ATTENZIONE (come in docs/04 e docs/05): lo screening misura importanza
PREDITTIVA, non causale. Il passo di identificazione causale (DML) e'
documentato ma non implementato in questo modulo.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from download_eurostat import build_panel

FEATURES = ["tfr_lag1", "log_gdp_pc", "gdp_growth", "anno"]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["geo", "anno"]).copy()
    df["tfr_lag1"] = df.groupby("geo")["tfr"].shift(1)
    df["log_gdp_pc"] = np.log(df["gdp_pc"].clip(lower=100))
    df["gdp_growth"] = df.groupby("geo")["gdp_pc"].pct_change()
    return df.dropna(subset=FEATURES + ["tfr"]).reset_index(drop=True)


def two_way_demean(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        mean_i = df.groupby("geo")[col].transform("mean")
        mean_t = df.groupby("anno")[col].transform("mean")
        mean_all = df[col].mean()
        out[col] = df[col] - mean_i - mean_t + mean_all
    return out


def xgboost_shap_importance(X: np.ndarray, y: np.ndarray,
                            feature_names: list) -> dict:
    import xgboost as xgb

    dtrain = xgb.DMatrix(X, label=y, feature_names=feature_names)
    params = {"objective": "reg:squarederror", "max_depth": 4,
              "eta": 0.05, "subsample": 0.8, "colsample_bytree": 0.8,
              "seed": 42, "verbosity": 0}
    model = xgb.train(params, dtrain, num_boost_round=300)

    contrib = model.predict(dtrain, pred_contribs=True)
    shap_vals = contrib[:, :-1]
    importance = np.abs(shap_vals).mean(axis=0)
    ranking = {name: float(imp) for name, imp in zip(feature_names, importance)}
    return dict(sorted(ranking.items(), key=lambda kv: -kv[1]))


def screen(panel_df: pd.DataFrame, within: bool = False) -> dict:
    df = prepare_features(panel_df)
    if within:
        df = two_way_demean(df, FEATURES + ["tfr"])
    X = df[FEATURES].values
    y = df["tfr"].values
    ranking = xgboost_shap_importance(X, y, FEATURES)
    resid_scale = float(np.std(y))
    return {"within": within, "n_osservazioni": int(len(df)),
            "n_regioni": int(df["geo"].nunique()),
            "dev_std_tfr": resid_scale,
            "shap_importance": ranking}


def fase3_report(verbose: bool = True) -> dict:
    panel = build_panel()
    res = {
        "pooling": screen(panel, within=False),
        "within_fe": screen(panel, within=True),
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    fase3_report()
