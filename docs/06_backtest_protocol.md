# Protocollo di backtest out-of-sample (PSTR + Leslie)

> Fonte: contributo dell'utente. Validazione del framework descritto in [04_architettura_due_strati.md](04_architettura_due_strati.md) e [05_low_fertility_trap.md](05_low_fertility_trap.md) su panel Eurostat NUTS-2 (1995–2024).

## 1. Disegno temporale e controllo del look-ahead bias

Finestra Train 1995–2012 (18 anni) e Test 2013–2024 (H = 12 anni), in due modalità complementari:

1. **Fixed-Origin Multi-Step**: si stimano (α̂, k̂, θ̂, γ̂, η̂) una sola volta sul 1995–2012. Al 1° gennaio 2013 si inizializza la Leslie con il vettore reale n_{i,2012} e si lascia correre il sistema accoppiato fino al 2024. Il DR̂_{i,t} usato nell'isteresi al passo t deve essere quello **generato internamente** dalla Leslie, mai quello osservato.
2. **Expanding Window** (orizzonti h = 1, 3, 5 anni): ri-stima del PSTR allargando la finestra e valutazione a orizzonte fisso. Verifica la stabilità strutturale dei parametri attraverso lo shock COVID 2020–2021.

Regola sui controlli esogeni (u_{i,t} e mortalità P_x): eseguire il test **condizionato** — valori realizzati di PIL/occupazione/migrazioni 2013–2024 come input esogeni e tavole di mortalità congelate al 2012 (o aggiornate identicamente per tutti i modelli in gara) — per isolare l'errore del modello demografico dall'errore di previsione macro.

## 2. Griglia dei benchmark (modelli nidificati)

Confrontare il PSTR direttamente con una Leslie a TFR costante non basta: se il PSTR vince non si sa se il merito è della dinamica temporale o della non-linearità. Tre modelli nidificati, tutti su Leslie-Rogers:

| Modello | Equazione del TFR | Cosa testa |
|---|---|---|
| **M0** — statico | F_{i,t+1} = F_{i,2012} | proiezione inerziale classica |
| **M1** — dinamico lineare | ΔF_{i,t+1} = μ_i + β_0 F_{i,t} − γ̃ DR_{i,t} + η̃ u_{i,t} | driver lineari e invecchiamento, senza trappola (k = 0) |
| **M2** — PSTR non-lineare | ΔF_{i,t+1} = μ_i + β_0 F_{i,t} + β_1 G(F_{i,t}; k, θ) − γ̃ DR_{i,t} + η̃ u_{i,t} | guadagno marginale dell'isteresi e della soglia θ |

**Condizione di promozione**: M2 è validato solo se batte in modo statisticamente significativo sia M0 sia M1.

## 3. Metriche e test statistici

### A. Accuratezza puntuale
- RMSE e MAE su F_{i,t} sull'orizzonte 2013–2024
- **MAPE sulla coorte 0–11 anni al 2024**: la popolazione totale in 12 anni cambia poco (dominata dagli adulti nati prima del 2012); il vero banco di prova della Leslie è la fascia composta interamente dalle nascite simulate nel periodo di test

### B. Superiorità predittiva (modelli nidificati)
- **M2 vs M0**: test di Diebold-Mariano sui differenziali d_{i,t} = e²_{M0} − e²_{M2}, con errori standard Driscoll-Kraay (correlazione spaziale e seriale tra regioni)
- **M2 vs M1**: M1 è nidificato in M2 (k → 0), il DM standard è distorto a sfavore del modello complesso → **test di Clark-West**, che corregge per la varianza di stima dei parametri aggiuntivi (k, θ)

### C. Validazione probabilistica (calibrazione dell'incertezza)
Sulle B = 1.000 traiettorie (Cluster Block Bootstrap o posterior bayesiana):
- **CRPS** (Continuous Ranked Probability Score): accuratezza + nitidezza congiunte
- **Coverage rate**: l'IC 95% deve contenere il TFR osservato nel ~92–97% delle coppie regione-anno (copertura molto più bassa = sottostima dell'incertezza strutturale)

### D. Test decisivo: stratificazione per regime
L'RMSE medio europeo maschera il punto: la sigmoide è quasi piatta lontano da θ (M1 ≈ M2 nelle regioni stabilmente a 1,15 o 1,90). Gli errori vanno stratificati sul TFR iniziale 2012:

1. **Regioni in trappola** (F < 1,35; Italia, Spagna, Polonia): M2 deve catturare la persistenza senza falsi rimbalzi verso la media europea (mean reversion tipica di M1)
2. **Zona di transizione** (1,35 ≤ F ≤ 1,65; Germania, Austria, Finlandia, Baltici): qui M2 deve mostrare il **massimo vantaggio**, prevedendo chi "scivola" nella trappola dopo uno shock negativo (es. crollo finlandese post-2012) e chi regge
3. **Alta fecondità** (F > 1,65; Francia, Svezia, Irlanda): controllo negativo — M2 non deve generare falsi allarmi di collasso

## 4. Batterie di robustezza (criteri pass/fail)

| Test | Cosa verifica | Criterio di superamento |
|---|---|---|
| Truncation 2013–2019 | assenza di distorsione COVID | Clark-West p < 0,05 già sul solo pre-COVID |
| Stabilità strutturale (Chow/Wald su θ, k, γ con pulse dummies 2020–21) | COVID = rumore transitorio | parametri non significativamente variati |
| Placebo su G(F_{i,t}) (randomization inference, B = 500; anche AR(1) sintetico con stessa persistenza) | non-linearità reale vs autocorrelazione | < 5% delle repliche placebo batte il modello reale; LM p > 0,10 |
| Placebo threshold displacement (θ forzato a 1,10 / 1,90) | identificazione della soglia | minimo netto dell'RMSE out-of-sample su θ ∈ [1,35; 1,55] |
| Forme funzionali alternative (LSTR vs ESTR vs spline cubica penalizzata) | validità della scelta parametrica | la spline non parametrica riproduce la "S" con flesso vicino a θ̂ |
| Perturbazione W_spat (KNN k ∈ {3,5,8}, IDW 200/400 km, Queen con isole, row vs spectral normalization) | stabilità spaziale (SUTVA) | segno e significatività stabili; Moran's I p > 0,05 sui residui |
| Leave-One-Country-Out (escludere a rotazione IT/FR/DE/ES) | generalizzabilità europea | θ̂ varia entro ±0,05 (altrimenti: effetto fisso nazionale, non legge generale) |
| TFR vs TFR* (Bongaarts-Feeney) | effetto quantum puro | condizione di bistabilità confermata anche sul quantum depurato dal tempo |
| Diagnostica strumenti (DR_t endogeno) | weak instruments | Kleibergen-Paap F > 10 (preferibile > 20); Hansen J p > 0,10 — **nota**: J richiede ≥2 strumenti; con il solo t-15 non è calcolabile, ritirata dalle promesse correnti, secondo strumento t-20 pianificato |

## 5. Nota di raccordo con lo stato attuale del repo

**Stato attuale**: la suite M0/M1/M2 con DM e Clark-West è **eseguita** su fixed-origin 2013-2024 e expanding h=1 — esito: la condizione di promozione del §2 NON è superata (M2 non batte né M0 né M1; a h=1 vince il random walk). Risultati e letture: [16_backtest.md](16_backtest.md), con la spiegazione strutturale in [15_panel_1990.md](15_panel_1990.md) (costanza dei parametri rigettata tra ere).

**Quanto è già pronto** (a che punto è il protocollo):

- Panel Eurostat NUTS-2 richiesto dal backtest: **assemblato e versionato** ([12_fase3_panel_europeo.md](12_fase3_panel_europeo.md); ESTENSIONE richiesta: il disegno originale prevede train 1995–2012, il panel copre 2013–2023 — per un fixed-origin test pieno serve estendere indietro TFR/PIL regionali, disponibili per il PIL ma parzialmente per il TFR NUTS-2; in alternativa expanding-window 2013–2023 con test 2020–2024)
- **Baseline M0**: Leslie a fertilità costante, validata su dati reali ([02 §5](02_dimezzamento.md))
- **M2 (PSTR)**: stima puntuale di (a, b0, b1, θ, k, γ) eseguita ([13](13_pstr_soglia_theta.md)); la versione dinamica-ricorsiva da inizializzare con n_2012 richiede la matrice Leslie-Rogers per singola regione (infrastruttura pronta al livello nazionale, da regionalizzare)
- **M1 (lineare)**: ricavabile come caso k → 0 della stessa griglia — implementazione immediata
- ~~Suite DM/Clark-West~~ **eseguita** ([16_backtest.md](16_backtest.md))
- ~~Stratificazione per regime~~ **eseguita** (RMSE per F_2012 < 1,35 / 1,35-1,65 / > 1,65)
- CRPS/coverage: eseguiti con B=20 ridotto (target B=1000 con block bootstrap sui residui)
- Da costruire: il coupling Leslie regionale (MAPE coorte 0-11), le batterie di robustezza §4 (Chow/Wald, placebo θ, ESTR/spline, W_spat, TFR*)

Il vincolo operativo più stringente è la finestra temporale del TFR regionale: la priorità essere allungare il panel indietro (Eurostat ha TFR NUTS-2 dal 2013; i dati pre-2013 a livello regionale sono in ricostruzione ISTAT/Eurostat).
