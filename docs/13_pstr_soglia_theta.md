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

1. **Endogeneità meccanica del DR — testata con strumento t-15 (F=340, γ̂_IV=+0,129)**: il segno resta positivo con la strumentazione, MA la validità dello strumento stesso è condizionata (v. §5 punto 4): sotto norme persistenti la DR a t-15 proxya il regime storico di fecondità.
2. **Confondente da country-level welfare** — Nord Europa: DR alto E welfare family-friendly (pensioni sustentabili, asili): nel pooled il segno di γ e' contaminato da questa correlazione territoriale. Il test LOCO per paese (docs/06) e' la robustezza diretta.
3. La teoria prevede il segno negativo sul ΔDR oltre la soglia fiscale DR0 — non sul livello: la forma `γ·max(0, DR-DR0)` con DR0 stimato resta da provare (prossimo passo naturale).

## 6. Limiti dichiarati (aggiornati post-audit)

- ~~Endogeneità della DR~~ **chiuso con l'IV t-15** (§5): strumento forte (F=340), segno confermato e rinforzato. La strumentazione della fertilità stessa (F_lag) resta invece aperta: punto seguente.
- **Bias da panel dinamico (correlato, non FE-Nickell)**: nel pooled il canale rilevante è l'eterogeneità regionale permanente correlata con F_lag, non la versione FE del problema (precisazione dall'audit: il Nickell riguardava il caso FE). Lo stimatore OLS concentrato ne soffre su T corto (11 anni); il test unitario su processo sintetico mostra il recupero di `a` entro ±0,04. Correttivo naturale: Mundlak (medie regionali dei regressori come controlli, rispetta la scelta identificativa sui livelli) o GMM system con strumenti collassati — prossimo passo.
- ~~LOCO per paese~~ **chiuso** (§5): γ sempre positivo su 33 esclusioni.
- ~~Bootstrap B=40~~ **chiuso**: B=399, soglia in 256/399 repliche (64%).
- **Identificazione del regime basso**: la finestra 2013-2023 non contiene transizioni complete sotto F≈1; il controesempio storico (Germania Est anni '90: TFR 0,77 → 1,4+) è fuori campione. L'estensione del panel a 1990+ è l'upgrade con maggior valore identificativo.
- **IV sotto-campione**: la merge t-15 copre il 25,7% del panel (i codici NUTS-2 di molti paesi sono cambiati tra 1998-2008 e oggi); DE/FR/ES/IT sono ben coperti, ma la selezione geografica va pesata nella lettura di γ̂_IV.
- Identificazione limitata dal raggio osservato (min TFR 0,84): il regime F<1 non è attraversato da nessuna coorte ampia di regioni.

### 5.4 Test discriminante: forma kinked γ·max(0, DR−DR₀) — ESEGUITO

La teoria prevede che il freno fiscale si accenda **solo oltre una soglia DR₀** (`fit_pstr_kinked`: concentrated LS con griglia profilata anche su DR₀ ∈ [0,20; 0,45]):

| Specificazione | Parametri | Risultato |
|---|---|---|
| Lineare γ·DR (headline) | SSR 7,2339 | γ̂ = +0,0767 |
| Kinked γ·max(0, DR−DR₀) | SSR 7,2335 | **DR̂₀ = limite inferiore della griglia** (0,20; estesa a [0,05; 0,45] → DR̂₀ = 0,06), **γ̂_kinked ≈ γ̂_lineare** |

**Lettura (pre-registrata prima dell'esecuzione)**: il minimo spinge DR₀ al pavimento e il SSR non migliora → la forma kinked non compra nulla: **l'effetto della DR è di livello, non il freno fiscale a soglia della teoria**. La lettura compatibile è il rebound ad alto sviluppo / esaurimento del rinvio, non il meccanismo di crowding-out fiscale kinked. Il segno resta robusto a IV e LOCO, ma la sua interpretazione causale resta aperta (§5, punto 4).

Nota su Hansen J: con un solo strumento (t-15) il test di over-identificazione non è calcolabile — la promessa del design (docs/06 appendice B) è ritirata; un secondo strumento (t-20, DR a 20 anni) è pianificato per rendere J testabile.
