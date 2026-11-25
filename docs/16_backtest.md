# Backtest out-of-sample M0/M1/M2 — DM e Clark-West

> Implementazione: `src/backtest_pstr.py`, esecuzione: `python3 src/backtest_pstr.py`. Protocollo: [06_backtest_protocol.md](06_backtest_protocol.md). Risponde ai punti P1-7 e P3-18 dell'audit.

## 1. Disegno

**Fixed-Origin Multi-Step**: stima di M0/M1/M2 su **train 2001-2012** (l'anno iniziale è imposto dal PIL regionale Eurostat, disponibile dal 2000; il protocollo prevedeva 1995-2012), proiezione ricorsiva **2013-2024 (H=12)**, condizionata ai valori realizzati di Δlog(PIL) e DR per regione (backtest condizionato, protocollo §1: isola l'errore della dinamica della fecondità dall'errore macro).

**Expanding Window h=1**: a ogni anno test t (2013-2024) ristima su tutto il campione ≤ t-1 (griglia coarse) e previsione a un passo con F_{t-1} osservato.

Modelli (protocollo §2): M0 statico (F = F_2012), M1 lineare dinamico (caso k→0 della PSTR), M2 PSTR completa. Sample: 251-282 regioni NUTS-2, 2.879-3.102 coppie regione-anno. Statistiche: DM con SE cluster per regione (M2 vs M0, non nidificati); **Clark-West** con correzione π̂² = (ŷ_M2 − ŷ_M1)² (M2 vs M1, nidificati); CRPS e coverage da ensemble cluster-bootstrap (B=20, ridotto per runtime, target B=1000 dichiarato).

## 2. Risultati — la condizione di promozione NON è superata

### Fixed-origin 2013-2024 (H=12)

| Metrica | M0 statico | M1 lineare | M2 PSTR |
|---|---|---|---|
| RMSE | 0,2043 | **0,1864** | 0,2006 |

| Test | Statistica | p | Esito |
|---|---|---|---|
| DM M1 vs M0 | t = 4,70 | <0,0001 | M1 > M0 ✓ |
| DM M2 vs M0 | t = 1,72 | 0,085 | **non significativo al 5%** |
| **Clark-West M2 vs M1** | t = **−3,80** | 0,0001 | **M2 significativamente PEGGIORE di M1** |

### Expanding window h=1

| Metrica | M0 statico | M1 lineare | M2 PSTR |
|---|---|---|---|
| RMSE | **0,0697** | 0,0712 | 0,0717 |

| Test | Statistica | p | Esito |
|---|---|---|---|
| DM M2 vs M0 | t = −3,36 | 0,0008 | **M2 peggiore del random walk** |
| Clark-West M2 vs M1 | t = −2,34 | 0,019 | M2 peggiore anche con correzione CW |

### Stratificazione per regime (fixed-origin, RMSE)

| Regime F_2012 | n | M0 | M1 | M2 |
|---|---|---|---|---|
| Trappola (<1,35) | 49 | 0,204 | **0,196** | 0,197 |
| Transizione (1,35-1,65) | 112 | **0,165** | 0,168 | 0,171 |
| Alta fecondità (>1,65) | 90 | 0,248 | **0,203** | 0,236 |

### Calibrazione (fixed-origin, ensemble B=20)

- **CRPS medio: 0,137** — informativo come ordine di grandezza, ma il valore assoluto dipende da B ridotto
- **Coverage 95%: 15,7%** — largamente sotto il nominale: l'ensemble (solo incertezza di stima, senza shock residuo) **sottostima l'incertezza strutturale**, come previsto dal protocollo §3.C

## 3. Letture

1. **La condizione di promozione del protocollo FALLISCE**: M2 non batte né M0 (p=0,085) né M1 (CW: M2 è peggiore). Il valore della PSTR **non è previsionale puntuale**: è strutturale (identificazione della soglia, degli attrattori, della non-linearità del regime). La formulazione corretta per il paper: la PSTR è un modello di *comprensione* del regime, non un modello di forecasting a 1-12 anni del TFR regionale.
2. **La spiegazione è già dentro il repo**: la [15_panel_1990.md](15_panel_1990.md) mostra che la costanza dei parametri è rigettata — la mappa stimata sul train 2001-2012 (θ̂ al bordo, tre attraversamenti, era post-comunista) non è trasponibile al regime 2013-2024. Un modello non-lineare con parametri instabili tra ere compone gli errori in modo più severo; il lineare, più piatto, soffre meno.
3. **A h=1 vince il random walk**: il TFR regionale di anno in anno è vicino a una martingala; i driver (Δlog PIL, DR) e la non-linearità aggiungono rumore di stima più che segnale. Coerente con la struttura della letteratura: gli effetti isteretici operano a orizzonte di generazione, non annuale — e la finestra disponibile non basta a coprire una generazione out-of-sample.
4. **Il triggering empirico resta**: M1 > M0 al fisso-12-passi (t=4,70) conferma che c'è segnale dinamico reale nel panel (i livelli non sono sufficienti); è la trasduzione in mappa non-lineare a non generalizzare tra ere.
5. **Coverage 15,7%**: l'incertezza da solo-bootstrap-parametrico è un limite inferiore; per il protocollo pieno servono i blocchi sui residui (block bootstrap) e B=1000.

## 3-bis. Backtest WITHIN-ERA (v1.2 — ESEGUITO)

`backtest_report(train_start=2013, train_end=2019, test_start=2020, test_end=2024)`: stima e proiezione interamente dentro il regime post-2013. È il test che il §3 lettura 2 indicava come naturale: se il fallimento cross-era era instabilità dei parametri (e non assenza di mappa), *dentro* il regime corrente la PSTR deve recuperare valore.

| Metrica | M0 statico | M1 lineare | M2 PSTR |
|---|---|---|---|
| RMSE (test 2020-2024) | 0,1451 | **0,1152** | 0,1222 |
| DM vs M0 | — | t=8,19 (p<0,001) | **t=+6,49 (p<0,001)** |
| Clark-West M2 vs M1 | — | — | **t=−3,12 (p=0,002): M1 resta migliore** |

Stratificazione per regime (RMSE): nella **banda trappola (F<1,35, 54 regioni) M2 è il migliore** (0,0805 vs 0,0837 M0, 0,0846 M1); nelle bande transizione e alta vince M1.

**Letture.** (1) **Il fallimento cross-era era instabilità dei parametri, non assenza di mappa**: within-era la PSTR batte il benchmark statico in modo netto (DM +6,49, opposto al −3,36 del disegno cross-era) — la condizione di promozione *verso M0* è superata dentro il regime. (2) **M1 resta comunque superiore (CW)**: il termine non-lineare F·G non ripaga globalmente la sua complessità within-era. (3) **Il valore del termine non-lineare è concentrato nella banda di trappola** (RMSE minimo di M2 nell'F<1,35): coerente con la teoria — la non-linearità serve dove la trappola opera, non nel cuore del regime alto. La formulazione corretta resta: la PSTR è strutturale, con un vantaggio previsivo locale nel regime basso; il complessivo h=1 expanding rimane del random walk (non toccato da questo test, che opera su H=5 fissato).

## 4. Conseguenze per il paper

- L'abstract va aggiornato dal promesso "will assess" al risultato: *out-of-sample, the PSTR does not beat linear or static benchmarks (DM and Clark-West); its contribution is structural, not predictive* — un referee apprezza molto di più un risultato negativo dichiarato e spiegato che una promessa.
- Il titolo "Escaping the Low Fertility Trap" va calibrato: i numeri del backtest suggeriscono l'enfasi giusta (struttura della trappola post-2013, non previsione).
- La batteria di robustezza §4 del protocollo (Chow/Wald, placebo θ, ESTR/spline, W_spat) resta aperta e documentata come tale.

## 5. Limiti

- Train 2001-2012 invece di 1995-2012 (PIL regionale dal 2000): la finestra include il collasso post-comunista, che domina la forma stimata (v. lettura 2).
- Le dummies anno sono poste a zero out-of-sample (anno base): penalizza uniformemente M1 e M2, ma va dichiarato.
- L'endpoint del PSTR congiunto alla Leslie regionale (MAPE coorte 0-11, protocollo §3.A) richiede la Leslie per singola regione — infrastruttura regionale da costruire (docs/06 §5).
- B=20 per CRPS/coverage: ordine di grandezza indicativo, non quantifica del protocollo (target B=1000).
