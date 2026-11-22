"""Matrice di Leslie: costruzione, autovalori, simulazione, tempo di dimezzamento."""

import json
import sys
from pathlib import Path

import numpy as np

MAX_AGE = 100
SEX_RATIO_F = 0.488
ROOT = Path(__file__).resolve().parents[1]


def build_leslie_matrix(fertility_rates: np.ndarray, survival_probs: np.ndarray,
                        sex_ratio_f: float = SEX_RATIO_F) -> np.ndarray:
    """Leslie a un anno, eta' 0..max_age, convenzione postcensale:
    prima riga F_x = ASFR_x * quota femminile; sottodiagonale P_x."""
    n = len(survival_probs)
    L = np.zeros((n, n))
    L[0, :len(fertility_rates)] = fertility_rates * sex_ratio_f
    L[1:, :-1] = np.diag(survival_probs[:-1])
    return L


def dominant_eigen(L: np.ndarray) -> tuple[float, np.ndarray]:
    eigvals, eigvecs = np.linalg.eig(L)
    idx = np.argmax(eigvals.real)
    lam = eigvals[idx].real
    vec = np.abs(eigvecs[:, idx].real)
    return lam, vec / vec.sum()


def survive(n: np.ndarray, probs: np.ndarray) -> np.ndarray:
    out = np.zeros_like(n)
    out[1:] = n[:-1] * probs[:-1]
    return out


def project_year(n: np.ndarray, fertility: np.ndarray, probs: np.ndarray,
                 tfr_scale: float = 1.0,
                 net_migration_rate: np.ndarray | None = None) -> np.ndarray:
    births = tfr_scale * (n * fertility * SEX_RATIO_F).sum()
    aged = survive(n, probs)
    aged[0] = births
    if net_migration_rate is not None:
        aged = aged * (1.0 + net_migration_rate)
    return aged


def simulate(n0: np.ndarray, fertility: np.ndarray, probs: np.ndarray,
             years: int = 100, tfr_scale: float = 1.0,
             net_migration_rate: np.ndarray | None = None) -> np.ndarray:
    traj = np.zeros(years + 1)
    n = n0.astype(float).copy()
    traj[0] = n.sum()
    for t in range(1, years + 1):
        n = project_year(n, fertility, probs, tfr_scale, net_migration_rate)
        traj[t] = n.sum()
    return traj


def halving_time(traj: np.ndarray) -> float:
    target = 0.5 * traj[0]
    below = np.where(traj <= target)[0]
    if len(below) == 0:
        return float("nan")
    idx = below[0]
    if idx == 0:
        return 0.0
    prev, curr = traj[idx - 1], traj[idx]
    return (idx - 1) + (prev - target) / (prev - curr)


def asymptotic_halving(lam: float) -> float:
    return np.log(0.5) / np.log(lam)


def load_processed(processed_dir: Path | None = None) -> dict:
    d = processed_dir or ROOT / "data" / "processed"
    return {
        "n0": np.load(d / "n0_female.npy"),
        "survival": np.load(d / "survival_probs.npy"),
        "fertility": np.load(d / "fertility_rates.npy"),
    }


def report(verbose: bool = True) -> dict:
    data = load_processed()
    n0, P, F = data["n0"], data["survival"], data["fertility"]

    L = build_leslie_matrix(F, P)
    lam, stable = dominant_eigen(L)
    r = float(np.log(lam))
    t_half_asym = asymptotic_halving(lam)

    traj = simulate(n0, F, P, years=150)
    t_half_first = halving_time(traj)

    res = {
        "lambda_1": float(lam),
        "r": r,
        "t_mezzo_asintotico": t_half_asym,
        "t_mezzo_primo": t_half_first,
        "pop_iniziale_femmine": float(n0.sum()),
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        print("quota over-65 struttura iniziale):",
              round(float(n0[66:].sum() / n0.sum()), 4))
        print("quota over-65 struttura stabile:",
              round(float(stable[66:].sum()), 4))
    return res


def scenario_table(tfr_values=(0.95, 1.18, 1.20, 1.30)) -> list[dict]:
    data = load_processed()
    n0, P, F = data["n0"], data["survival"], data["fertility"]
    base_tfr = F.sum()
    rows = []
    for tfr in tfr_values:
        scale = tfr / base_tfr
        L = build_leslie_matrix(F * scale, P)
        lam, _ = dominant_eigen(L)
        traj = simulate(n0, F, P, years=150, tfr_scale=scale)
        rows.append({
            "tfr": tfr,
            "r": float(np.log(lam)),
            "t_mezzo_asintotico": asymptotic_halving(lam),
            "t_mezzo_primo": halving_time(traj),
            "pop_2056": float(traj[30]) / 1e6,
            "pop_2076": float(traj[50]) / 1e6,
        })
    return rows


if __name__ == "__main__":
    report()
    if "--scenari" in sys.argv:
        for row in scenario_table():
            print(json.dumps(row, ensure_ascii=False))
