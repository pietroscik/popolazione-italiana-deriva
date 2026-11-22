# Fase 3 — Panel Europeo NUTS-2 e screening delle direttrici del TFR

> Implementazione: `src/download_eurostat.py` (download panel) e `src/panel_screening.py` (screening), esecuzione: `python3 src/panel_screening.py`.

## 1. Il dataset (reale, Eurostat JSON-stat API)

| Variabile | Tabella | Copertura |
|---|---|---|
| TFR regionale | `demo_r_find2` (indic_de=TOTFERRT) | 285 regioni NUTS-2, 2013–2023 |
| PIL pro-capite | `nama_10r_2gdp` (unit=PPS_EU27_2020_HAB) | idem |

Panel risultante: **2.674 osservazioni regione-anno** su 282 regioni ripulite (mediana TFR 1,54; min 0,84 (livelli tipo Sardegna); max ≈ 4,9 (picchi periferici)). Il panel europeo è la **condizione di identificazione** menzionata in [05_low_fertility_trap.md](05_low_fertility_trap.md): solo attraversando entrambi i regimi (Nord Europa sopra soglia, Italia/Spagna sotto) si può stimare la soglia θ della trappola.

## 2. La pipeline di screening

Feature (con lag within-regione): TFR ritardato (persistenza), log PIL pro-capite, crescita del PIL anno precedente, anno. Due varianti:

- **pooling**: modello grezzo su tutte le osservazioni
- **within-FE**: two-way demeaning (rimozione media regionale e media annua) — rimuove gli effetti fissi territoriali e gli shock macro europei (COVID, inflazione), isolando la dinamica dentro-regione

Ranking via **XGBoost + TreeSHAP nativo** (`pred_contribs`, nessuna dipendenza extra oltre `xgboost`).

## 3. Risultati (SHAP importance media |valore|)

| Feature | Pooling | Within-FE |
|---|---|---|
| **tfr_lag1 (persistenza)** | 0,211 | **0,049** |
| anno | 0,026 | — (0,003) |
| log_gdp_pc | 0,017 | 0,007 |
| gdp_growth | 0,007 | 0,004 |

Deviazione standard del TFR residuo: 0,378 (pooling) → 0,090 (within): **il 76% della variabilità del TFR europeo è between-region** — territorialmente strutturata, non congiunturale.

### Letture

1. **La persistenza domina in entrambe le varianti**: il TFR di un anno è il miglior predittore del TFR successivo anche rimuovendo tutta l'eterogeneità territoriale. È una prima evidenza empirica coerente col meccanismo di feedback del [Low Fertility Trap](05_low_fertility_trap.md): il comportamento riproduttivo di ieri è la variabile che spiega oggi, più dell'economia.
2. **La correlazione PIL-fecondità è per lo più territoriale**: l'importanza del log PIL scende di 2,5 volte passando da pooling a within-FE. La relazione PIL→TFR osservata a livello europeo è ampiamente un effetto della struttura territoriale (paesi ricchi del Nord con welfare family-friendly ≠ paesi del Sud), non una leva che si muove anno per anno dentro le regioni.
3. **Disclaimer metodologico** (come da design [04_architettura_due_strati.md](04_architettura_due_strati.md)): questo è uno **screening predittivo, non un'identificazione causale**. Il TFR pretto è un confondente in potenza (regioni ricche hanno più asili e più TFR), il DAG delle figure produttive va seguito con la fase DML/EconML documentata in [02_dimezzamento.md §6](02_dimezzamento.md) e [06_backtest_protocol.md](06_backtest_protocol.md), e la isteresi PSTR resta l'obiettivo finale (θ, k, γ).

## 4. Prossimi passi della fase

- Aggiungere covariate al panel: disoccupazione giovanile (nuova tabella labguida NUTS-2), costo abitativo, copertura asili (richiede dati nazionali, non Eurostat)
- Implementare DML (EconML CausalForestDML) con cross-fitting raggruppato e Moran's I sui residui (design completo in docs/04)
- Stimare la PSTR della Low Fertility Trap su questo panel, con la condizione di bistabilità k(F_max-F_min)/4 > 1 di docs/05

## Nota tecnica

Il panel viene rigenerato con `python3 src/download_eurostat.py` (salva `data/processed/eurostat_panel.csv`, ~3.000 righe). I test usano un panel sintetico, non la rete.
