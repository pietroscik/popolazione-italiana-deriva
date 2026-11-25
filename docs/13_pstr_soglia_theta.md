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
| k̂ (pendenza) | 3,69 | 10,0 | transizione più netta |
| a | -0,078 | -0,038 | deriva negativa di base |
| b0 (persistenza regime basso) | +0,083 | +0,016 | autoregressione sotto θ |
| b1 (feedback regime alto) | -0,085 | -0,031 | freno sopra θ |
| η (dlog PIL) | +0,204 | +0,214 | stabile: condizioni economiche di breve periodo |
| **γ (DR)** | — | **+0,077** | segno OPPOSTO alla teoria - vedi §5 |
| n osservazioni | 2.366 | 2.366 | panel post-fix (26 righe con gap temporale scartate) |

**Correzione dall'audit (P0)**: il differenziale del log-PIL era calcolato con `diff()` globale invece che per regione — la prima osservazione di ogni regione (~12% del panel) era differenziata contro l'ultimo anno della regione precedente. Fix: `groupby(geo).diff()`. Effetto marginale (θ e γ immutati a due decimali); tutti i numeri di questa pagina sono post-fix e ristimati.

**Bootstrap a cluster sulle regioni (B=399)**: θ̂ = 1,57 ± 0,18, intervallo [1,20; 1,75]; **la soglia instabile emerge in 265/399 repliche (66%), media 0,90** (conteggio a regime anno base). Con B=40 la frequenza apparentemente più bassa (19/40) era in parte rumore da poche repliche: il supporto alla soglia è ora quantificato con stabilità adeguata.

### Punti di equilibrio: i due regimi della mappa (fix dell'audit)

La mappa implicita ora include l'effetto medio delle dummies anno (prima era valutata solo all'anno base). I due regimi danno letture diverse e complementari:

| Regime | Radici di f̂(F)=0 in [0,4; 3,5] | Lettura |
|---|---|---|
| **Anno base, senza DR** (headline) | **0,91 instabile / 1,61 stabile** | soglia di non ritorno e attrattore del sistema a regime pre-2020 |
| **Anno base, con DR** | **0,49 instabile / 1,65 stabile** | la radice bassa è sotto il supporto osservato (min TFR 0,84): pura estrapolazione del ramo lineare, non interpretabile; affidabile solo l'attrattore alto |
| **Anno medio 2013-2023** | **nessuna radice interna** (f̂ < 0 ovunque) | gli effetti 2022-23 (-0,09 ciascuno) dominano la media: nella dinamica recente la mappa punta verso il basso a qualunque F — il collasso post-pandemico trascina sotto ogni bacino interno |

A regime base **senza DR** (modello headline), **la soglia di non ritorno è ~0,91 e l'attrattore ~1,61**: la Sardegna (0,85 nel 2025) è sotto soglia, l'Italia (1,14) sopra. Aggiungere la DR restringe il fit del ramo basso e sposta la radice sotto il supporto dei dati: segno che il regime F<0,9 non è identificato dal panel — non che la soglia sia a 0,49. Il regime medio dice però che il *presente* (2022-23) non contiene alcun equilibrio interno: le letture insieme sono il quadro corretto — la struttura della trappola esiste, la congiuntura attuale la sta attraversando verso il basso.

## 4. Letture base (soglia e attrattore)

> **Convenzione post-audit**: il *modello headline* è quello **senza DR** (θ̂=1,66, soglia ~0,91, attrattore ~1,61); la specificazione **estesa con DR** (θ̂=1,70; 0,49 estrapolazione/1,65) è esplorazione/robustezza — ora supportata da IV strumento-forte e LOCO, ma con γ di segno non ancora interpretato causalmente (§5). Le letture che seguono si riferiscono al modello headline se non indicato diversamente.

1. **C'è una soglia di non ritorno stimata empiricamente, e l'Italia è vicina**: il TFR italiano (1,18 nel 2024, 1,14 nel 2025) sta' **sopra** la soglia di ~0,91 — la dinamica di lungo periodo implicita è di risalita lenta verso l'attrattore ~1,61 — ma la **Sardegna è già sotto** (0,85 nel 2025, settimo anno consecutivo sotto l'unità, datas ISTAT): per il modello il declino sardo è destinato a continuare, e il dato osservato (0,91 → 0,85) è coerente.
2. **La soglia pratica (~0,91) è piu' bassa della soglia teorica sociologica (~1,35-1,50)** di [05_low_fertility_trap.md](05_low_fertility_trap.md): la transizione G(F;k,θ) stimata a 1,66 descrive dove *si spegne il feedback del regime alto*, mentre il punto di non ritorno emerge a F molto piu' basso. Le due soglie non coincidono -- e la differenza è informative: il sistema europeo mostra piu' resilienza di quanto la teoria della trappola teme, ma **sotto F≈1,0-1,1 nessuna regione del panel è mai risalita** con dati osservati.
3. **L'attrattore europeo è ~1,61, non il rimpiazzo (2,1)**: anche uscendo dal regime basso, la dinamica stimata converge a un equilibrio sotto il rimpiazzo — coerente con la capacità attracting della gamma francese/nordica osservata (1,6-1,9) e non oltre.
4. **Il quarto attrattore basso (~1,05-1,15 nella teoria) non è identificato dal panel** (v. il ramo basso della specificazione DR, radice a 0,49 fuori dal supporto): le osservazioni persistentemente sotto 1,05 sono troppo rare (solo livelli tipo Sardegna). Il pavimento bio-sociale F_min della teoria non è visibile nei dati 2013-2023 — servirebbero serie piu' lunghe.

## 5. Letture aggiuntive: il segno di γ

**γ̂ = +0,081: positivo, non negativo come previsto dalla teoria.** Letture non escludentisi:

1. **Endogeneità meccanica del DR — strumentata a t−15 e t−20, con un bug storico corretto (v. §5.5)**: lo strumento etichettato "t-15" nelle versioni ≤ v1.1.2 era in realtà DR a **t−30** (double-shift nella merge, 759/759 righe matchano esattamente DR(anno−30), 0/759 DR(anno−15)). Con lo strumento **correttamente** a t−15: F=4.089, **γ̂_IV = −0,055**; con t−15+t−20 congiunti: **γ̂_IV = −0,045**, Hansen J=0,23 (df=1, p=0,63) non respinge. **Il segno positivo di γ OLS NON sopravvive alla strumentazione corretta**: la lettura più parsimoniosa è eterogeneità regionale persistente nel pooled, non un effetto causale della DR. La validità dello strumento resta comunque condizionata (v. §5 punto 4).
2. **Confondente da country-level welfare** — Nord Europa: DR alto E welfare family-friendly (pensioni sustentabili, asili): nel pooled il segno di γ e' contaminato da questa correlazione territoriale. Il test LOCO per paese (docs/06) e' la robustezza diretta.
3. La teoria prevede il segno negativo sul ΔDR oltre la soglia fiscale DR0 — non sul livello: la forma `γ·max(0, DR-DR0)` con DR0 stimato resta da provare (prossimo passo naturale).

## 5-bis. Batteria di robustezza della soglia (eseguita)

`theta_stability_battery` (`src/pstr_trap.py`): θ̂, γ e soglia attraverso le specificazioni — la lettura corretta è su questa batteria, non su una singola stima:

| Specificazione | θ̂ | γ (DR) | Nota |
|---|---|---|---|
| Headline senza DR | 1,66 | — | modello base |
| Con DR | 1,70 | +0,077 | specificazione estesa |
| **CRE/Mundlak** (medie regionali) | **1,72** | **+0,483** | eterogeneità regionale permanente correlata assorbita (coeff. media-F +0,24): θ̂ stabile, γ sale — coerente con la diagnosi di eterogeneità correlata (§6) |
| Kinked max(0, DR−DR₀) | 1,72 | +0,060 (DR₀→bordo) | §5.4: nessun kink |
| IV t−15 (corretto, post-bug) | 1,40 | **−0,055** | §5.5: lo strumento era t−30 nelle versioni ≤v1.1.2; F=4.089, n=1.971 (copertura ~80%, non più 25,7%: la vecchia bassa copertura era artefatto del t−30 che batteva il pavimento 1990 della storia) |
| **IV t−15 + t−20** (2 strumenti) | 1,68 | **−0,045** | F congiunto 2.537; Hansen J=0,23, df=1, **p=0,63** non respinge la congruenza; n=1.895 |
| Finestra 2013-2024 | 1,70 | +0,077 | estensione forwards |

**Conclusione della batteria**: θ̂ è **stabile in [1,66–1,72]** nelle specificazioni OLS/CRE/kinked; l'IV a strumento singolo t−15 (corretto) scende a 1,40 e l'IV a due strumenti torna a 1,68 — la soglia dell'IV e il quadro di riferimento restano da 1,40 a 1,72. **Il segno di γ̂ è positivo in OLS/CRE ma NEGATIVO sotto strumentazione corretta**: non è identificato in modo robusto. **La soglia di non ritorno F ≈ 0,91 non va presentata come costante strutturale consolidata**:è identificata nell'era 2013-2023, con supporto bootstrap al 66%, e i suoi valori dipendono dal regime (anno base vs anno medio, §3). Formulazione corretta: *evidenza compatibile con una soglia di non ritorno ~0,9 nell'era post-2013, con supporto moderato — non una legge strutturale*. La stabilità tra ere è RIGETTATA (docs/15).

## 6. Limiti dichiarati (aggiornati post-audit)

- **Endogeneità della DR (RIAPERTO, v. §5.5)**: lo strumento "t-15" delle versioni ≤v1.1.2 era in realtà t−30 (double-shift). Con gli strumenti correttamente lagati γ̂_IV ≡ −0,05/−0,045: **il segno positivo è un artefatto della correlazione pooled, non un effetto causale**. L'ipotesi del freno della DR non è così nemmeno nel segno stimato dall'IV — resta aperta ogni lettura. La strumentazione della fertilità stessa (F_lag) resta aperta.
- **Bias da panel dinamico (correlato, non FE-Nickell)**: nel pooled il canale rilevante è l'eterogeneità regionale permanente correlata con F_lag, non la versione FE del problema (precisazione dall'audit: il Nickell riguardava il caso FE). Lo stimatore OLS concentrato ne soffre su T corto (11 anni); il test unitario su processo sintetico mostra il recupero di `a` entro ±0,04. Correttivo naturale: Mundlak (medie regionali dei regressori come controlli, rispetta la scelta identificativa sui livelli) o GMM system con strumenti collassati — prossimo passo.
- ~~LOCO per paese~~ **chiuso** (§5): γ sempre positivo su 33 esclusioni (OLS pooled: misura il segno della correlazione, non un effetto causale — v. §5.5).
- ~~Bootstrap B=40~~ **chiuso**: B=399, soglia in 256/399 repliche (64%).
- **Identificazione del regime basso**: la finestra 2013-2023 non contiene transizioni complete sotto F≈1; il controesempio storico (Germania Est anni '90: TFR 0,77 → 1,4+) è fuori campione. L'estensione del panel a 1990+ è l'upgrade con maggior valore identificativo.
- **IV sotto-campione (OBSOLETO, v. §5.5)**: il vincolo di copertura al 25,7% era un artefatto del t−30 che batteva il pavimento 1990 della storia DR; con la mappatura corretta t−15 copre ~80% del panel (n=1.971, 220 regioni) e t−15+t−20 n=1.895.
- Identificazione limitata dal raggio osservato (min TFR 0,84): il regime F<1 non è attraversato da nessuna coorte ampia di regioni.

### 5.4 Test discriminante: forma kinked γ·max(0, DR−DR₀) — ESEGUITO

La teoria prevede che il freno fiscale si accenda **solo oltre una soglia DR₀** (`fit_pstr_kinked`: concentrated LS con griglia profilata anche su DR₀ ∈ [0,20; 0,45]):

| Specificazione | Parametri | Risultato |
|---|---|---|
| Lineare γ·DR (headline) | SSR 7,2339 | γ̂ = +0,0767 |
| Kinked γ·max(0, DR−DR₀) | SSR 7,2335 | **DR̂₀ = limite inferiore della griglia** (0,20; estesa a [0,05; 0,45] → DR̂₀ = 0,06), **γ̂_kinked ≈ γ̂_lineare** |

**Lettura (pre-registrata prima dell'esecuzione)**: il minimo spinge DR₀ al pavimento e il SSR non migliora → la forma kinked non compra nulla: **l'effetto della DR è di livello, non il freno fiscale a soglia della teoria**. La lettura compatibile è il rebound ad alto sviluppo / esaurimento del rinvio, non il meccanismo di crowding-out fiscale kinked. Il segno è positivo in OLS e LOCO ma NON negli strumenti correttamente lagati (§5.5): la sua interpretazione causale resta aperta.

Nota su Hansen J: **ESEGUITO con il secondo strumento t−20** (§5.5): J=0,23 (df=1, p=0,63) non respinge la congruenza degli strumenti. Lettura pre-registrata: il J non convalida gli strumenti singolarmente — se t−15 e t−20 violano l'esclusione nello stesso verso (norme familiari regionali persistenti), il J non li respinge; un rifiuto sarebbe invece informativo. La promessa del design (docs/06 appendice B) non è quindi più ritirata ma resta condizionata.

### 5.5 Bug dello strumento "t−15" (era DR a t−30) e risultati corretti (v1.2)

**Il bug.** `add_dr_t15` (versioni ≤ v1.1.2) fondava due chiavi sfasate in versi opposti: `df.anno_strumento = anno − 15` e `hist.anno_strumento = storia + 15`. Il match `storia + 15 = anno − 15` produceva **DR(t−30)** etichettata come t−15. Verifica post-correzione sulle 759 righe strumentate del panel v1.1.x: **759/759 matchano esattamente DR(anno−30), 0/759 DR(anno−15)**. La bassa copertura storica (25,7%) non era un limite dei dati: era l'artefatto del t−30 che batteva il pavimento 1990 della storia DR.

**Le correzioni.** `add_dr_instruments(lags=(15, 20))` (`src/download_eurostat.py`) mappa anno−15 e anno−20 direttamente; test di regressione `test_dr_t15_e_dr_t20_risalgono_a_15_e_20_anni_prima`; il panel rigenerato copre ~80% per t−15 (n=1.971, 220 regioni) e n=1.895 con entrambi.

**I risultati corretti (real data):**

| Strumentazione | θ̂ | γ̂_IV | Primo stadio | Note |
|---|---|---|---|---|
| Vecchia (=[v1.1.x], era t−30) | 1,94 | +0,129 | F=340 | sotto-campione 759 righe, claim ritirato |
| **IV t−15 (corretto)** | 1,40 | **−0,055** | F=4.089 | n=1.971 |
| **IV t−15 + t−20** | 1,68 | **−0,045** | F congiunto 2.537 | **Hansen J=0,23 (df=1, p=0,63)** n=1.895 |

**La conseguenza epistemica.** Il claim "il segno positivo di γ̂ è robusto a IV e LOCO" delle versioni ≤ v1.1.2 **non è più sostenuto**: sotto strumentazione corretta γ̂_IV ≈ −0,05. Lettura più parsimoniosa: il γ̂>0 dell'OLS è eterogeneità regionale persistente correlata al livello di DR, non un effetto causale della DR sul ΔF. La sintassi della batteria resta: γ̂ OLS > 0 sempre, ma **il segno non è identificato in modo robusto**; Hansen J non respinge (congruenza t−15/t−20) senza per questo convalidare la validità dell'esclusione (v. lettura pre-registrata sopra). I risultati demografici (Leslie, Lotka, LTC) non sono toccati: γ̂ non entra in nessuna di quelle catene.
