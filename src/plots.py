"""Figure del repository (quick-win editoriali).

Genera i PNG in docs/figures/ (committati: la CI non dipende da matplotlib).
Esecuzione locale: `python3 src/plots.py` (richiede matplotlib, che NON e'
in requirements perche' le figure sono gia' nel repo).

Figure:
1. piramide_2026_2056.png  - piramide della popolazione, 2026 vs 2056
2. mappa_pstr.png          - mappa implicita f(F) con soglia e attrattore
3. traiettoria_dimezzamento.png - fan chart di scenario (TFR, migrazioni)
4. costi_ltc.png          - costo LTC annuo 2026-2081 (deterministico + banda MC)
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
        ax.set_xlim(-450, 450)
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
    for tfr, nome, dy in ((1.18, "Italia 2024 (TFR 1,18)", -0.005),
                           (0.85, "Sardegna 2025 (TFR 0,85)", -0.038)):
        idx = int(np.argmin(np.abs(F_grid - tfr)))
        ax.plot([tfr], [f[idx]], "s", color="#111", ms=8, zorder=6)
        ax.annotate(nome, (tfr, f[idx] + dy), fontsize=9,
                    ha="left", xytext=(6, -10), textcoords="offset points",
                    va="top")
    theta = base_year["theta"]
    ax.axvline(theta, color="#999", ls="--", lw=1)
    ax.annotate(f"θ̂ = {theta:.2f}", (theta, ax.get_ylim()[1] * 0.85),
                fontsize=8, color="#555")
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
        ("C: TFR 1,3, saldo +617k (break-even)", 1.3 / 1.18, 617_000.0, "#1b7837"),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for nome, scala, saldo, colore in scenari:
        tot, *_ = simulate_two_sex(data["n0"], data["n0_male"],
                                   data["fertility"], data["survival"],
                                   data["survival_male"], years=55,
                                   tfr_scale=scala, net_migration_total=saldo)
        ax.plot(range(2026, 2082), tot / 1e6, color=colore, lw=2, label=nome)
    ax.axhline(tot[0] / 1e6 / 2, color="#999", ls=":", lw=1)
    ax.annotate("metà della popolazione 2026", (2027, tot[0] / 1e6 / 2 + 0.5),
                fontsize=8, color="#555")
    ax.set_xlabel("anno")
    ax.set_ylabel("milioni")
    ax.set_title("Scenari di traiettoria della popolazione (Leslie due sessi)")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "traiettoria_dimezzamento.png", dpi=150)
    plt.close(fig)


def plot_costi_ltc():
    import numpy as np
    from ltc_montecarlo import annual_cost_mc
    from leslie import load_processed, simulate_two_sex
    from ltc import prevalence_by_age
    # rigenerazione della banda: MC ridotto (B=200) con le stesse regole del cap. 5
    from ltc_montecarlo import (COST_DOMICILIARE, COST_RESIDENZIALE_MG,
                                SEVERITY_CONCENTRATION, SEVERITY_MIX,
                                SHARE_DOMICILIARE_CENTER, monte_carlo_ltc)

    rng = np.random.default_rng(7)
    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"], years=55,
                           net_migration_total=280_000.0, store_ages=True)
    tot, tr_f, tr_m, ages_f, ages_m = out
    prev = prevalence_by_age(len(data["n0"]) - 1)
    claimants = ((ages_f + ages_m) * prev[None, :]).sum(axis=1)
    caregivers = (ages_f + ages_m)[:, 45:65].sum(axis=1)
    ratio = caregivers / claimants

    anni = np.arange(2026, 2082)
    B = 200
    costs = np.zeros((B, len(anni)))
    for b in range(B):
        sev = rng.dirichlet(SEVERITY_MIX * SEVERITY_CONCENTRATION)
        cost_dom = rng.lognormal(np.log(COST_DOMICILIARE), 0.15)
        cost_res = rng.lognormal(np.log(COST_RESIDENZIALE_MG), 0.10)
        share = rng.beta(SHARE_DOMICILIARE_CENTER * 100, 35)
        r0 = rng.normal(11.0, 1.0)
        bb = rng.lognormal(np.log(2.0), 0.10)
        costs[b] = annual_cost_mc(claimants, ratio, sev, cost_dom, cost_res,
                                  share, r0, bb) / 1e9

    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.fill_between(anni, np.quantile(costs, 0.05, axis=0),
                    np.quantile(costs, 0.95, axis=0), color="#2166ac",
                    alpha=0.25, label=" Monte Carlo 90% (parametri severità/costi)")
    ax.plot(anni, np.median(costs, axis=0), color="#2166ac", lw=2,
            label="mediana MC")
    ax.set_xlabel("anno")
    ax.set_ylabel("miliardi di € (prezzi 2026)")
    ax.set_title("Costo formale annuo LTC — banda Monte Carlo (cap. 5, regime parametrico)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "costi_ltc.png", dpi=150)
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
