"""Figure del repository (quick-win editoriali).

Genera i PNG in docs/figures/ (committati: la CI non dipende da matplotlib).
Esecuzione locale: `python3 src/plots.py` (richiede matplotlib, che NON e'
in requirements perche' le figure sono gia' nel repo).

Figure:
1. piramide_2026_2056.png  - piramide della popolazione, 2026 vs 2056
2. mappa_pstr.png          - mappa implicita f(F) con soglia e attrattore
3. traiettoria_dimezzamento.png - fan chart di scenario (TFR, migrazioni)
4. costi_ltc.png          - costo LTC annuo 2026-2081 (banda MC cap. 5, B=5.000)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
FIG = ROOT / "docs" / "figures"

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit("matplotlib richiesto solo per rigenerare le figure: "
                     "i PNG sono gia' committati in docs/figures/") from exc


def plot_piramide():
    import numpy as np
    from leslie import load_processed, simulate_two_sex

    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"], years=30,
                           net_migration_total=280_000.0, store_ages=True)
    tot, tr_f, tr_m, ages_f, ages_m = out
    ages = [0, 30]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, t in zip(axes, ages):
        f = ages_f[t] / 1000
        m = -ages_m[t] / 1000
        anni = np.arange(len(f))
        ax.barh(anni, f, color="#b2182b", label="femmine", height=1)
        ax.barh(anni, m, color="#2166ac", label="maschi", height=1)
        ax.set_title(f"{2026 + t}")
        ax.set_xlim(-500, 500)
        ax.axvline(0, color="k", lw=0.5)
    axes[0].set_ylabel("età")
    axes[0].set_xlabel("migliaia")
    axes[1].set_xlabel("migliaia")
    axes[0].legend(loc="lower right", fontsize=8)
    fig.suptitle("Piramide della popolazione italiana — Leslie due sessi "
                 "(saldo +280k/anno)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "piramide_2026_2056.png", dpi=150)
    plt.close(fig)


def plot_mappa_pstr():
    import numpy as np
    from pstr_trap import equilibrium_points, fit_pstr, implied_map, prepare_panel
    from download_eurostat import build_panel

    df = prepare_panel(build_panel())
    df_no_dr = df.copy()
    df_no_dr["dr_lag"] = 0.0
    best = fit_pstr(df_no_dr)
    base_year = dict(best)
    base_year["dummy_share"] = np.zeros(len(best["beta"]) - 5)
    F_grid, f = implied_map(base_year)
    roots = equilibrium_points(base_year)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.plot(F_grid, f, color="#b2182b", lw=2, label="f(F): TFR dell'anno successivo − TFR corrente")
    ax.axhline(0, color="k", lw=0.8)
    for Fr, tipo in roots:
        colore = "#d95f02" if tipo == "instabile" else "#1b7837"
        ax.plot([Fr], [0], "o", color=colore, ms=9, zorder=5)
        ax.annotate(f"{Fr:.2f}\n({tipo})", (Fr, 0), textcoords="offset points",
                    xytext=(0, 10 if tipo == "instabile" else -34),
                    ha="center", fontsize=8, color=colore)
    for tfr, nome, tx, ty in ((1.18, "Italia 2024 (TFR 1,18)", 0.55, 0.019),
                               (0.85, "Sardegna 2025 (TFR 0,85)", 1.05, -0.068)):
        idx = int(np.argmin(np.abs(F_grid - tfr)))
        ax.plot([tfr], [f[idx]], "s", color="#111", ms=8, zorder=6)
        ax.annotate(nome, (tfr, f[idx]), xytext=(tx, ty), textcoords="data",
                    fontsize=9, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color="#111", lw=0.8))
    theta = base_year["theta"]
    ax.axvline(theta, color="#999", ls="--", lw=1)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax + 0.14 * (ymax - ymin))
    ax.annotate(f"θ̂ = {theta:.2f}", (theta, 1),
                xycoords=("data", "axes fraction"), xytext=(4, -5),
                textcoords="offset points", va="top", fontsize=8, color="#555")
    ax.set_xlabel("TFR (F)")
    ax.set_ylabel("ΔF annuo implicito")
    ax.set_title("Mappa implicita PSTR sul panel NUTS-2 (modello base, regime ad anno base)")
    ax.set_xlim(0.4, 3.0)
    fig.tight_layout()
    fig.savefig(FIG / "mappa_pstr.png", dpi=150)
    plt.close(fig)


def plot_traiettoria():
    import numpy as np
    from leslie import load_processed, simulate_two_sex

    data = load_processed()
    scenari = [
        ("A: TFR 1,18, saldo +280k", 1.0, 280_000.0, "#2166ac"),
        ("B: TFR 1,14, saldo +70k", 1.14 / 1.18, 70_000.0, "#b2182b"),
        ("D: TFR 1,18, saldo 0", 1.0, 0.0, "#8c510a"),
        ("C: TFR 1,18, saldo +617k (break-even)", 1.0, 617_000.0, "#1b7837"),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for nome, scala, saldo, colore in scenari:
        tot, *_ = simulate_two_sex(data["n0"], data["n0_male"],
                                   data["fertility"], data["survival"],
                                   data["survival_male"], years=55,
                                   tfr_scale=scala, net_migration_total=saldo)
        ax.plot(range(2026, 2082), tot / 1e6, color=colore, lw=2, label=nome)
    ax.axhline(tot[0] / 1e6 / 2, color="#999", ls=":", lw=1)
    ax.annotate("metà della popolazione 2026", (2027, tot[0] / 1e6 / 2 + 0.4),
                fontsize=8, color="#555", ha="left", va="bottom")
    ax.set_xlabel("anno")
    ax.set_ylabel("milioni")
    ax.set_title("Scenari di traiettoria della popolazione (Leslie due sessi)")
    # legenda sotto gli assi: non copre più la linea del dimezzamento a sinistra
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18),
              ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "traiettoria_dimezzamento.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)


def plot_costi_ltc():
    import numpy as np
    from leslie import load_processed
    # replica esatta del cap. 5 (monte_carlo_ltc): B=5.000, seed=7, demografia
    # ristimata per replica (rho e scala TFR campionati) — cosi' la banda
    # della figura coincide con i numeri headline della release (docs/17)
    from ltc_montecarlo import (COST_DOMICILIARE, COST_RESIDENZIALE_MG,
                                SEVERITY_CONCENTRATION, SEVERITY_MIX,
                                SHARE_DOMICILIARE_CENTER, SEX_MULTIPLIER,
                                simulate_claimants_m, annual_cost_mc)
    from ltc_costi import R_LOGIT_PENDENZA, R_RATIO_INFLESSO

    rng = np.random.default_rng(7)
    data = load_processed()
    n0_f, n0_m = data["n0"], data["n0_male"]
    fert = data["fertility"]
    P_f, P_m = data["survival"], data["survival_male"]

    B, years, saldo = 5_000, 55, 280_000.0
    T = years + 1
    costs = np.zeros((B, T))
    for b in range(B):
        sex_mult_f = rng.lognormal(np.log(SEX_MULTIPLIER["F"]), 0.10)
        sex_mult_m = rng.lognormal(np.log(SEX_MULTIPLIER["M"]), 0.10)
        sev = rng.dirichlet(SEVERITY_MIX * SEVERITY_CONCENTRATION)
        cost_dom = rng.lognormal(np.log(COST_DOMICILIARE), 0.15)
        cost_res = rng.lognormal(np.log(COST_RESIDENZIALE_MG), 0.10)
        share = rng.beta(SHARE_DOMICILIARE_CENTER * 100, 35)
        r0 = rng.normal(R_RATIO_INFLESSO, 1.0)
        bb = rng.lognormal(np.log(R_LOGIT_PENDENZA), 0.10)
        rho = rng.uniform(0.0, 0.01)
        tfr_scale = rng.normal(1.0, 0.03)
        cl_f, cl_m, claimants, ratio = simulate_claimants_m(
            n0_f, n0_m, fert, P_f, P_m, tfr_scale, rho, years, saldo,
            sex_mult_f=sex_mult_f, sex_mult_m=sex_mult_m)
        costs[b] = annual_cost_mc(claimants, ratio, sev, cost_dom, cost_res,
                                  share, r0, bb) / 1e9

    anni = np.arange(2026, 2026 + T)
    q05, med, q95 = (np.quantile(costs, p, axis=0) for p in (0.05, 0.50, 0.95))

    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.fill_between(anni, q05, q95, color="#2166ac",
                    alpha=0.25, label="Monte Carlo 90% (parametri + demografia ristimata per replica)")
    ax.plot(anni, med, color="#2166ac", lw=2, label="mediana MC")
    i2056 = 2056 - 2026
    lab = (f"2056: {med[i2056]:.1f}".replace(".", ",") + " mld € ["
           + f"{q05[i2056]:.1f}".replace(".", ",") + "; "
           + f"{q95[i2056]:.1f}".replace(".", ",") + "]")
    ax.plot([2056], [med[i2056]], "o", color="#b2182b", ms=7, zorder=6)
    ax.annotate(lab, (2056, med[i2056]), xytext=(-8, 22),
                textcoords="offset points", fontsize=9, color="#b2182b",
                fontweight="bold", ha="right",
                arrowprops=dict(arrowstyle="-", color="#b2182b", lw=0.8))
    ax.set_xlabel("anno")
    ax.set_ylabel("miliardi di € (prezzi 2026)")
    ax.set_title("Costo formale annuo LTC — banda Monte Carlo cap. 5 (B=5.000, regime parametrico)")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "costi_ltc.png", dpi=150)
    print("LTC 2056 — mediana:", round(float(med[i2056]), 1),
          "| q05:", round(float(q05[i2056]), 1),
          "| q95:", round(float(q95[i2056]), 1))
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    plot_piramide()
    plot_mappa_pstr()
    plot_traiettoria()
    plot_costi_ltc()
    print("figure generate in", FIG)


if __name__ == "__main__":
    main()
