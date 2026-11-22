"""Fase 5 - Econometria collegata: indici economico-sociali dalla piramide.

Dal vettore di stato per eta' a due sessi (Leslie-Rogers) calcola anno per anno
gli aggregati che governano i raccordi economici della dinamica demografica:
- popolazione in eta' attiva (15-64) → base contributiva previdenziale
- popolazione 65+ → proxy dell'esercito pensionistico e della domanda sanitaria
- coorti 0-14 e 15-17 → domanda educativa futura
- dependency ratios (anziani e giovanili) → pressione fiscale e previdenziale
- nucleo potenziale di formazione famiglia (25-44) → domanda abitativa
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

ETA_ATTIVA = (15, 64)
ETA_ANZIANI = (65, 100)
ETA_SCOLASTICA = (0, 17)
ETA_FORMAZIONE_FAMIGLIE = (20, 44)


def indici_economici(ages: np.ndarray) -> dict:
    """Indici anno per anno da una matrice (anni x eta') due sessi."""
    attivi = ages[:, ETA_ATTIVA[0]:ETA_ATTIVA[1] + 1].sum(axis=1)
    anziani = ages[:, ETA_ANZIANI[0]:].sum(axis=1)
    giovani = ages[:, :ETA_ATTIVA[0]].sum(axis=1)
    scolastici = ages[:, :ETA_SCOLASTICA[1] + 1].sum(axis=1)
    nuclei = ages[:, ETA_FORMAZIONE_FAMIGLIE[0]:ETA_FORMAZIONE_FAMIGLIE[1] + 1].sum(axis=1)
    dep_old = np.divide(anziani, attivi, out=np.zeros_like(attivi),
                        where=attivi > 0)
    dep_young = np.divide(giovani, attivi, out=np.zeros_like(attivi),
                          where=attivi > 0)
    return {
        "attivi_15_64": attivi,
        "anziani_65piu": anziani,
        "giovani_0_14": giovani,
        "scolastici_0_17": scolastici,
        "nuclei_20_44": nuclei,
        "dependency_ratio_anziani": dep_old,
        "dependency_ratio_giovani": dep_young,
    }


def fase5_report(years: int = 55, start_year: int = 2026,
                 saldo: float = 280_000.0, verbose: bool = True) -> dict:
    from leslie import load_processed, simulate_two_sex

    data = load_processed()
    out = simulate_two_sex(data["n0"], data["n0_male"], data["fertility"],
                           data["survival"], data["survival_male"],
                           years=years, net_migration_total=saldo,
                           store_ages=True)
    tot, _, _, ages_f, ages_m = out
    ind = indici_economici(ages_f + ages_m)

    rows = []
    for t in [0, 15, 30, 45, years]:
        rows.append({
            "anno": start_year + t,
            "popolazione_totale": float(tot[t]),
            "attivi_15_64_mln": float(ind["attivi_15_64"][t] / 1e6),
            "anziani_65piu_mln": float(ind["anziani_65piu"][t] / 1e6),
            "dependency_ratio_anziani": float(ind["dependency_ratio_anziani"][t]),
            "giovani_0_14_mln": float(ind["giovani_0_14"][t] / 1e6),
            "nuclei_20_44_mln": float(ind["nuclei_20_44"][t] / 1e6),
        })

    res = {"saldo_migratorio": saldo, "tabella": rows}
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    saldo = float(sys.argv[1]) if len(sys.argv) > 1 else 280_000.0
    fase5_report(saldo=saldo)
