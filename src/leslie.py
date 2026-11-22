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
    data = {
        "n0": np.load(d / "n0_female.npy"),
        "survival": np.load(d / "survival_probs.npy"),
        "fertility": np.load(d / "fertility_rates.npy"),
    }
    if (d / "n0_male.npy").exists():
        data["n0_male"] = np.load(d / "n0_male.npy")
        data["survival_male"] = np.load(d / "survival_probs_male.npy")
    return data


def project_two_sex(n_f: np.ndarray, n_m: np.ndarray, fertility: np.ndarray,
                     P_f: np.ndarray, P_m: np.ndarray,
                     mig_f: np.ndarray | None = None,
                     mig_m: np.ndarray | None = None,
                     tfr_scale: float = 1.0,
                     sex_ratio_f: float = SEX_RATIO_F
                     ) -> tuple[np.ndarray, np.ndarray]:
    """Un anno di proiezione a due sessi: nascite totali dalle donne, ripartite
    per sesso al parto (quota femminile sex_ratio_f), sopravvivenza sessuale e
    migrazione netta per eta' per sesso."""
    births_total = tfr_scale * (n_f * fertility).sum()
    births_f = births_total * sex_ratio_f
    births_m = births_total - births_f
    new_f = survive(n_f, P_f)
    new_m = survive(n_m, P_m)
    new_f[0] = births_f
    new_m[0] = births_m
    if mig_f is not None:
        new_f = new_f + mig_f
        new_m = new_m + (mig_m if mig_m is not None else mig_f)
    return np.maximum(new_f, 0.0), np.maximum(new_m, 0.0)


def simulate_two_sex(n0_f, n0_m, fertility, P_f, P_m, years=100,
                     tfr_scale=1.0, net_migration_total=0.0,
                     mig=None, store_ages=False):
    """Proiezione a due sessi con saldo migratorio annuo costante.

    net_migration_total: migranti netti annui (livello, non tasso). Se mig non
    e' fornito, il profilo per eta' e sesso e' Rogers-Castro pesato.
    Restituisce (traiettoria totale, traiettoria femmine, traiettoria maschi).
    Con store_ages=True restituisce anche le matrici (anni x eta') per sesso.
    """
    nf = n0_f.astype(float).copy()
    nm = n0_m.astype(float).copy()
    tot = np.zeros(years + 1)
    tr_f = np.zeros(years + 1)
    tr_m = np.zeros(years + 1)
    ages_f = np.zeros((years + 1, len(nf))) if store_ages else None
    ages_m = np.zeros((years + 1, len(nm))) if store_ages else None
    tot[0] = nf.sum() + nm.sum()
    tr_f[0], tr_m[0] = nf.sum(), nm.sum()
    if store_ages:
        ages_f[0], ages_m[0] = nf, nm
    mig_static = mig
    for t in range(1, years + 1):
        if mig_static is not None:
            mig_f = mig_m = mig_static
        elif net_migration_total != 0.0:
            # profilo Rogers-Castro ri-calibrato ogni anno sulla struttura
            # per eta' corrente: le quote s_{x,t} = r_x N_{x,t} / sum_j r_j N_{j,t}
            # si aggiornano con la popolazione che cambia (profilo dinamico)
            from migration import build_migration_profile
            mig_f = build_migration_profile(nf, net_migration_total * 0.5)
            mig_m = build_migration_profile(nm, net_migration_total * 0.5)
        else:
            mig_f = mig_m = None
        nf, nm = project_two_sex(nf, nm, fertility, P_f, P_m,
                                 mig_f, mig_m, tfr_scale)
        tot[t] = nf.sum() + nm.sum()
        tr_f[t], tr_m[t] = nf.sum(), nm.sum()
        if store_ages:
            ages_f[t], ages_m[t] = nf, nm
    if store_ages:
        return tot, tr_f, tr_m, ages_f, ages_m
    return tot, tr_f, tr_m


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


def migration_report(years: int = 55, verbose: bool = True) -> dict:
    """Scenari di saldo migratorio a due sessi (TFR invariato) e saldo di break-even."""
    from migration import saldo_for_constant_population

    data = load_processed()
    n0_f, n0_m = data["n0"], data["n0_male"]
    P_f, P_m = data["survival"], data["survival_male"]
    F = data["fertility"]
    pop0 = n0_f.sum() + n0_m.sum()

    rows = {}
    for saldo, name in [(0.0, "zero"), (130_000.0, "-50%"),
                        (280_000.0, "attuale-media-24-25"),
                        (400_000.0, "alta")]:
        tot, _, _ = simulate_two_sex(n0_f, n0_m, F, P_f, P_m, years=years,
                                     net_migration_total=saldo)
        rows[name] = {
            "saldo": saldo,
            "pop_finale": float(tot[-1]),
            "var_pct": float((tot[-1] / tot[0] - 1.0) * 100),
            "t_mezzo": halving_time(tot),
        }

    def growth(saldo):
        tot, _, _ = simulate_two_sex(n0_f, n0_m, F, P_f, P_m, years=years,
                                     net_migration_total=saldo)
        return tot[-1] - tot[0]

    break_even = saldo_for_constant_population(growth, lo=0.0, hi=1_000_000)
    res = {"popolazione_iniziale": float(pop0), "orizzonte_anni": years,
           "scenari": rows, "saldo_break_even": float(break_even)}
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    report()
    if "--scenari" in sys.argv:
        for row in scenario_table():
            print(json.dumps(row, ensure_ascii=False))
    if "--migrazioni" in sys.argv:
        migration_report()
