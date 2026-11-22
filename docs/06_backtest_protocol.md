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
| Diagnostica strumenti (DR_t endogeno) | weak instruments | Kleibergen-Paap F > 10 (preferibile > 20); Hansen J p > 0,10 |

## 5. Nota di raccordo con lo stato attuale del repo

Il backtest richiede il panel Eurostat NUTS-2 (TFR regionale, struttura per età, covariate macro) e le Fasi 1–2 completate. Il repo implementa già il **baseline M0** (Leslie a fertilità costante su dati reali ISTAT, [02_dimezzamento.md §5](02_dimezzamento.md)); M1 e M2 sono oggetto delle Fasi 2–4 della roadmap del [README](../README.md).
