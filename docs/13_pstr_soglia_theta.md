# PSTR — Stima empirica della soglia della Low Fertility Trap

> Implementazione: `src/pstr_trap.py`, esecuzione: `python3 src/pstr_trap.py [--no-boot]`. Primo tassello empirico della Fase 4 dell'architettura ([05_low_fertility_trap.md](05_low_fertility_trap.md) §5) sulla base del panel NUTS-2 di [12_fase3_panel_europeo.md](12_fase3_panel_europeo.md).

## 1. Specificazione

Il TFR diventa variabile di stato endogena. Equazione dinamica (ΔTFR annuo delle regioni NUTS-2):

    dF_{i,t} = a + b0·F_{i,t-1} + b1·F_{i,t-1}·G(F_{i,t-1}; k, θ) + η·dlog(PIL) + dummies_anno + ε

con **G logistica a transizione sulla variabile di stato stessa** (il feedback del fertility trap):

    G(q; k, θ) = 1 / (1 + e^{−k(q−θ)})

**Pooled con dummies anno, senza effetti fissi paese** — scelta strutturale: gli attrattori multipli sono ipotesi sui *livelli*; il within (FE paese) assorbe nel fixed effect il punto di equilibrio di ciascun paese e cancella l'informazione necessaria a identificare la mappa globale. Le dummies anno rimuovono gli shock comuni europei (COVID, inflazione). Stima: minimi quadrati concentrati con profilo su (θ, k) grigliati.

**Dalla mappa agli equilibri**: f̂(F) = a + b0·F + b1·F·G(F;k,θ) è la derivata discreta della traiettoria; gli equilibri della dinamica sono le radici di f̂(F)=0 — stabile se f̂'(F*)<0, **instabile (soglia di non ritorno) se f̂'(F*)>0**.

## 2. Specificazione estesa con il freno economico (γ·DR)

La teoria ([05_low_fertility_trap.md](05_low_fertility_trap.md), equazione di Φ) prevede un freno `-γ·max(0, DR - DR0)`: l'invecchiamento, comprimendo le risorse fiscali delle coorti giovani, deve trascinare verso il basso la mappa. Il componente DR regionale (65+/15-64, Eurostat `demo_r_pjanaggr3`) ora entra nel panel e nel modello:

    dF_{i,t} = a + b0·F + b1·F·G(F;k,θ) + η·dlog(PIL) + γ·DR_{i,t-1} + dummies_anno + ε

## 3. Risultati (panel reale Eurostat: 2.392 osservazioni, 282 regioni, 2013-2023)

| Parametro | Stima (senza DR) | Stima (con DR) | Lettura |
|---|---|---|---|
| **θ̂ (soglia transizione)** | 1,66 | **1,70** | punto di flesso del feedback del regime alto |
| k̂ (pendenza) | 3,69 | 6,73 | transizione più netta |
| a | -0,081 | -0,060 | deriva negativa di base |
| b0 (persistenza regime basso) | +0,085 | +0,035 | autoregressione sotto θ |
| b1 (feedback regime alto) | -0,087 | -0,043 | freno sopra θ |
| η (dlog PIL) | +0,217 | +0,219 | stabile: condizioni economiche di breve periodo |
| **γ (DR)** | — | **+0,081** | segno OPPOSTO alla teoria - vedi §5 |

**Bootstrap a cluster sulle regioni (B=40)**: θ̂ = 1,56 ± 0,17, intervallo [1,20; 1,75]; la soglia instabile emerge in 19/40 repliche (media 0,92) — meno stabile che nel modello senza DR: segno che parte dell'identificazione della soglia era sorretta dalla struttura demografica dei regimi.

### Punti di equilibrio della mappa estesa (controlli a media campione)

| F* | Tipo | Significato |
|---|---|---|
| **~0,81** | **instabile** | soglia di non ritorno ancora più bassa (ma fuori dal fit range denso: particolare) |
| **~1,64** | stabile | attrattore alto |

Con la DR nel modello, **la soglia di non ritorno scende sotto l'unità e l'attrattore sale a ~1,64**: la mappa diventa più "generosa" con il regime basso (più margini di risalita) ma anche più dipendente dal profilo DR della regione.

## 4. Letture base (soglia e attrattore)

1. **C'è una soglia di non ritorno stimata empiricamente, e l'Italia è vicina**: il TFR italiano (1,18 nel 2024, 1,14 nel 2025) sta' **sopra** la soglia di ~1,05 — la dinamica di lungo periodo implicita è di risalita lenta verso l'attrattore ~1,51 — ma la **Sardegna è già sotto** (0,85 nel 2025, settimo anno consecutivo sotto l'unità, datas ISTAT): per il modello il declino sardo è destinato a continuare, e il dato osservato (0,91 → 0,85) è coerente.
2. **La soglia pratica (~1,05) è piu' bassa della soglia teorica sociologica (~1,35-1,50)** di [05_low_fertility_trap.md](05_low_fertility_trap.md): la transizione G(F;k,θ) stimata a 1,66 descrive dove *si spegne il feedback del regime alto*, mentre il punto di non ritorno emerge a F molto piu' basso. Le due soglie non coincidono -- e la differenza è informative: il sistema europeo mostra piu' resilienza di quanto la teoria della trappola teme, ma **sotto F≈1,0-1,1 nessuna regione del panel è mai risalita** con dati osservati.
3. **L'attrattore europeo è ~1,51, non il rimpiazzo (2,1)**: anche uscendo dal regime basso, la dinamica stimata converge a un equilibrio sotto il rimpiazzo — coerente con la capacità attracting della gamma francese/nordica osservata (1,6-1,9) e non oltre.
4. **Il quarto attrattore basso (~1,05-1,15 nella teoria) non è identificato dal panel**: le osservazioni persistentemente sotto 1,05 sono troppo rare (solo livelli tipo Sardegna). Il pavimento bio-sociale F_min della teoria non è visibile nei dati 2013-2023 — servirebbero serie piu' lunghe.

## 5. Letture aggiuntive: il segno di γ

**γ̂ = +0,081: positivo, non negativo come previsto dalla teoria.** Letture non escludentisi:

1. **Endogeneità meccanica del DR** — il DR di oggi è costruito dalle nascite di 15-65 anni or sono: una regione con TFR basso da decenni ha per costruzione un DR alto. Cio' che γ̂ cattura con segno positivo e' probabilmente il rimbalzo meccanico (le regioni molto vecchie hanno esaurito il hiatus di rinvio). E' ESATTAMENTE il caso d'uso degli strumenti ritardati t-15 previsto dal design ([06_backtest_protocol.md](06_backtest_protocol.md) appendice B): strumentare DR con la struttura per eta' indietro di 15 anni e stimare la forma strutturale.
2. **Confondente da country-level welfare** — Nord Europa: DR alto E welfare family-friendly (pensioni sustentabili, asili): nel pooled il segno di γ e' contaminato da questa correlazione territoriale. Il test LOCO per paese (docs/06) e' la robustezza diretta.
3. La teoria prevede il segno negativo sul ΔDR oltre la soglia fiscale DR0 — non sul livello: la forma `γ·max(0, DR-DR0)` con DR0 stimato resta da provare (prossimo passo naturale).

## 6. Limiti dichiarati (da chiudere)

- **Bias da panel dinamico (Nickell)**: il regressore F_lag è correlato con gli errori passati (feedback); lo stimatore OLS concentrato ne soffre su T corto (11 anni). Correttivo progettuale: IV/GMM con strumenti ritardati t-15 come da [06_backtest_protocol.md](06_backtest_protocol.md) appendice B. Il test unitario su processo sintetico noto mostra il bias esplicitamente (recupero di `a` entro ±0,04).
- **Pooled senza FE paese** è la scelta identificativa corretta per la mappa globale, ma espone a omittedcountry-level confounders (welfare, cultura) — mitigabile con robustezza LOCO per paese (protocollo docs/06).
- Identificazione limitata dal raggio osservato (min TFR 0,84): il regime F<1 non è attraversato da nessuna coorte ampia di regioni.
