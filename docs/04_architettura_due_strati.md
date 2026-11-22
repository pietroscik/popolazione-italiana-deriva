# Architettura a due strati (design di riferimento)

> Fonte: contributo dell'utente (documentazione teorica, da integrare via via che le fasi vengono implementate). Questo documento descrive l'architettura *target* del progetto; lo stato di implementazione è indicato per ciascuna fase.

## Sintesi

L'impostazione più performante non è una pipeline lineare ma un'**architettura ibrida causale-dinamica a due strati**: uno strato econometrico-causale **offline** (stima dei parametri strutturali puliti da bias sui dati panel) che alimenta uno strato dinamico non-lineare **online** (simulatore a stati accoppiati). L'ordine di esecuzione è vincolato: invertire le fasi introduce data leakage, overcontrol bias o stime distorte del tempo di dimezzamento.

| Fase | Strato | Metodo core | Input principali | Bias/limite risolto | Stato nel repo |
|---|---|---|---|---|---|
| 1. Tempo/Quantum | Offline (Dati) | Decomposizione Bongaarts-Feeney | TFR, età al parto | Distorsione del TFR di periodo dovuta al rinvio | ⬜ da fare (l'età media al parto per regione è già scaricabile da `demo_r_find2`) |
| 2. Causale Spaziale | Offline (Stima) | Spatial-SLX DML + causal mediation | Panel ISTAT/OMI/INPS + W_spat | Confondimento, spillover (SUTVA), overcontrol bias | ◐ screening implementato su panel europeo ([12](12_fase3_panel_europeo.md)); DML/EconML da implementare (design in [02 §6](02_dimezzamento.md)) |
| 3. Migrazione Selettiva | Online (Dinamica) | Leslie-Rogers (profilo per età) | n_t, tavole P_x, curva migratoria | Sottostima dell'erosione delle coorti fertili | ✔ implementata e validata: due sessi + Rogers-Castro calibrato sul saldo osservato ([07](07_leslie_rogers_migrazioni.md)) |
| 4. Fertility Trap | Online (Feedback) | Sistema non-lineare con isteresi | Stato n_t, DR_t, shock policy | Linearità irrealistica e assenza di punti di non ritorno | ◐ formalizzazione matematica completa ([05](05_low_fertility_trap.md)) + **stima empirica PSTR di (θ, k, γ) e delle radici della mappa** ([13](13_pstr_soglia_theta.md)); accoppiamento dinamico completo (F_t endogeno nella Leslie) da implementare |

## I quattro nodi concettuali

1. **Effetto Tempo vs. Quantum (Bongaarts-Feeney)**: il TFR di periodo schiaccia insieme quante nascite si perdono definitivamente (quantum) e quante vengono solo rinviate per l'aumento dell'età media al parto (tempo). Se T sale, il TFR osservato sottostima la fecondità reale delle coorti; ma oltre una certa soglia biologica il rinvio diventa perdita permanente. Proiettare la Leslie senza distinguere i due effetti distorce il lungo periodo.
2. **Causal mediation sull'età al parto**: nel DAG `eta_media_parto` è un mediatore, non un confondente (mai condizionarvi: overcontrol bias). Il passo successivo è la decomposizione NDE/NIE: una leva (stabilità lavorativa, costo abitativo) alza il TFR perché fa fare il secondo figlio alle stesse età (quantum) oppure perché anticipa il primo parto (tempo)?
3. **Low Fertility Trap (Lutz et al.)**: la Leslie standard assume TFR esogeno e costante; nella realtà esiste un feedback non lineare (demografico, sociologico, economico) con possibili punti di non ritorno — le stesse policy efficaci a TFR 1,5 diventano inefficaci a TFR 1,15. Formalizzazione completa in [05_low_fertility_trap.md](05_low_fertility_trap.md).
4. **Selezione migratoria ed endogeneità del saldo negativo**: un deflusso netto concentrato 20–39 anni non è uno shock neutrale: altera piramide, tasso di dipendenza e composizione socioeconomica di chi resta, con spillover spaziali che violano SUTVA nel DML.

## Stack previsto (Fase 2–4)

Dipendenze da aggiungere solo all'attivarsi delle fasi corrispondenti (pin pensati per Python 3.10/3.11): `xgboost`, `shap`, `econml`, `statsmodels`, `geopandas`, `libpysal`, `esda`, `scipy`, `pyarrow`. Le fasi 1 (attuale) e la Leslie pura richiedono solo `numpy`/`pandas`.

## Protocollo di validazione

La validazione end-to-end del framework (backtest out-of-sample, benchmark nidificati M0/M1/M2, test Clark-West/Diebold-Mariano, batterie di robustezza) è specificata in [06_backtest_protocol.md](06_backtest_protocol.md).
