"""Capitolo LTC 4 - attuariale: premio puro di una rendita LTC a ripartizione.

Replica, sulla piramide proiettata della Leslie-Rogers due sessi, la logica
dell'esempio numerico dell'Ordine degli Attuari (seminario 26.10.2026):

- platea: aderenti alla previdenza complementare (~10 milioni), struttura
  per eta' e sesso della fascia nazionale 25-64, scalata (ipotesi dichiarata:
  la struttura reale degli aderenti e' piu' vicina agli occupati; l'effetto
  della struttura sulla DINAMICA del premio resta il dato robusto del modello);
- copertura: rendita vitalizia LTC di 500 EUR/mese (6.000 EUR/anno);
- prudenza: nessun recupero dell'autosufficienza (assunto dell'esempio);
- esclusi i non autosufficienti all'adesione (regola della proposta):
  i claimants maturano solo per incidenza successiva all'avvio;
- incidenza netta annua per eta': approssimata dal gradiente della
  prevalenza parametrica del capitolo 1 (upper bound prudenziale);
- contribuenti: aderenti in eta' attiva (25-64);
- sistema finanziario: ripartizione del costo annuo delle rendite
  (premio puro, senza caricamenti ne' margini di sicurezza).

Due scenari di platea (il punto dell'esempio 74 vs 113 EUR dell'Ordine):
A) platea costante (coorte chiusa: nessun nuovo aderente);
B) adesioni automatiche (ingressi annuali = coorte nazionale dei 25enni
   scalata alla quota aderenti).
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RENDA_ANNUA = 6_000.0
PLATEA = 10.0e6
ETA_ATTIVA = (25, 64)
POP_TOTALE_2026 = 58_942_828.0


def net_incidence_by_age(max_age: int = 100) -> np.ndarray:
    """Incidenza netta annua approssimata dal gradiente della prevalenza."""
    from ltc import prevalence_by_age
    prev = prevalence_by_age(max_age)
    inc = np.zeros_like(prev)
    inc[:-1] = np.clip(np.diff(prev), 0.0, None)
    return inc


def simulate_fund(adesioni_automatiche: bool = False,
                  start_year: int = 2026, years: int = 55) -> dict:
    """Proiezione del fondo LTC: premio puro anno per anno a ripartizione."""
    from leslie import load_processed, survive

    data = load_processed()
    pf, pm = data["survival"], data["survival_male"]
    n0_f, n0_m = data["n0"], data["n0_male"]

    share = PLATEA / (n0_f[ETA_ATTIVA[0]:ETA_ATTIVA[1] + 1].sum() +
                      n0_m[ETA_ATTIVA[0]:ETA_ATTIVA[1] + 1].sum())

    nf = n0_f * share
    nm = n0_m * share
    claim_f = np.zeros_like(nf)
    claim_m = np.zeros_like(nm)
    inc = net_incidence_by_age(len(nf) - 1)
    inflow_f = n0_f[ETA_ATTIVA[0]] * share
    inflow_m = n0_m[ETA_ATTIVA[0]] * share

    rows = []
    for t in range(years + 1):
        autof_f = np.maximum(nf - claim_f, 0.0)
        autof_m = np.maximum(nm - claim_m, 0.0)
        claim_f = claim_f + autof_f * inc
        claim_m = claim_m + autof_m * inc

        contributors = (nf[ETA_ATTIVA[0]:ETA_ATTIVA[1] + 1].sum() +
                        nm[ETA_ATTIVA[0]:ETA_ATTIVA[1] + 1].sum())
        rendite = (claim_f.sum() + claim_m.sum()) * RENDA_ANNUA
        premio = rendite / contributors if contributors > 0 else float("nan")

        rows.append({
            "anno": start_year + t,
            "aderenti_mln": float((nf.sum() + nm.sum()) / 1e6),
            "claimants": float(claim_f.sum() + claim_m.sum()),
            "contribuenti_mln": float(contributors / 1e6),
            "premio_puro_eur": float(premio),
        })

        claim_f = survive(claim_f, pf)
        claim_m = survive(claim_m, pm)
        nf = survive(nf, pf)
        nm = survive(nm, pm)
        if adesioni_automatiche:
            nf[ETA_ATTIVA[0]] += inflow_f
            nm[ETA_ATTIVA[0]] += inflow_m

    return {"adesioni_automatiche": adesioni_automatiche, "serie": rows}


def attuariale_report(verbose: bool = True) -> dict:
    costante = simulate_fund(adesioni_automatiche=False)
    crescente = simulate_fund(adesioni_automatiche=True)

    def at(rep, anno):
        for r in rep["serie"]:
            if r["anno"] == anno:
                return r["premio_puro_eur"]
        return rep["serie"][-1]["premio_puro_eur"]

    res = {
        "rendita_annua_eur": RENDA_ANNUA,
        "platea_iniziale_mln": PLATEA / 1e6,
        "platea_costante": {
            "premio_2026": at(costante, 2026),
            "premio_2056": at(costante, 2056),
            "premio_2081": at(costante, 2081),
        },
        "adesioni_automatiche": {
            "premio_2026": at(crescente, 2026),
            "premio_2056": at(crescente, 2056),
            "premio_2081": at(crescente, 2081),
        },
        "benchmark_ordine_attuari_eur": {"costante": 113.0, "crescente": 74.0},
    }
    if verbose:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return res


if __name__ == "__main__":
    attuariale_report()
