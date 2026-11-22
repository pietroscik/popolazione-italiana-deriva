# Tempo di dimezzamento demografico

## 1. Modello asintotico (Lotka)

Tre passaggi dal TFR al tempo di dimezzamento, a regime (popolazione stabile, migrazioni nulle):

**1. Tasso netto di riproduzione (R₀)** — quante figlie femmine avrà in media una donna nella vita, tenendo conto della quota femminile alla nascita (~105 maschi per 100 femmine → quota ≈ 0,488) e della sopravvivenza fino all'età fertile media (~0,99 nei paesi a bassa mortalità):

```
R₀ ≈ TFR × 0,488 × 0,99
```

**2. Tasso intrinseco di variazione annuo (r)** — dipende dalla lunghezza media della generazione T (età media al parto, in Italia oggi **32,7 anni** — ISTAT 2025):

```
r ≈ ln(R₀) / T
```

**3. Tempo di dimezzamento (t½):**

```
t½ = ln(0,5) / r = T · ln(0,5) / ln(R₀)
```

## 2. Tabella di sensitività (T = 32,7 anni, aggiornata a TFR 2025)

Dimezzamento per generazione in funzione di TFR e T — copre il range reale delle regioni italiane (Sardegna 0,85 — Trentino-Alto Adige ~1,4):

| TFR | R₀ | r annuo | t½ (T=31) | t½ (T=32,7) | t½ (T=34) |
|---|---|---|---|---|---|
| 1,30 | 0,628 | -1,4/-1,5% | 46,2 | 48,7 | 50,7 |
| 1,24 | 0,599 | -1,5/-1,7% | 41,9 | 44,2 | 46,0 |
| 1,18 | 0,570 | -1,7/-1,8% | 38,2 | 40,3 | 41,9 |
| **1,14 (Italia 2025)** | 0,551 | **-1,82%** | 36,0 | **38,0** | 39,5 |
| 0,85 (Sardegna) | 0,411 | -2,7% | 24,1 | **25,5** | 26,5 |

Con il dato ISTAT 2025 (TFR = 1,14, T = 32,7): **t½ ≈ 38 anni** per generazione; ogni generazione di madri viene sostituita al ~55%.

## 3. Dalla formula alla traiettoria reale (matrice di Leslie)

Il valore di t½ descrive il ritmo **asintotico**, raggiunto quando la distribuzione per età converge all'autovettore stabile della matrice di Leslie (per Perron-Frobenius: `n_t ≈ c·λ₁ᵗ·v₁`, con `λ₁ ≈ e^r`). Il **primo** dimezzamento della popolazione reale differisce per tre fattori:

1. **Momentum demografico** — l'Italia è già un paese invecchiato: le coorti 1960–1975 oggi 50–65enni mantengono alto il totale finché restano in vita, poi la loro uscita (2040–2055) accelera temporaneamente il declino oltre il ritmo di Lotka.
2. **Speranza di vita** — allungarla rallenta il calo del totale, ma non inverte il trend: rimanda l'uscita delle coorti anziane.
3. **Migrazioni** — il calcolo assume saldo nullo. I flussi in ingresso attuali (~+250–300k/anno) attenuano il declino effettivo: è il driver dominante della differenza tra questo scenario e le previsioni centrali ISTAT, che non prevedono dimezzamento entro il 2080.

**Perimetro**: il modello Leslie solo-femminile proietta la popolazione femminile; il dimezzamento della popolazione totale coincide solo se il rapporto tra i sessi resta stabile — approssimazione dichiarata, accettabile per l'attuale struttura italiana.

## 4. Specifiche del modello Leslie (`src/leslie.py`)

- Convenzione **births-first**: prima riga `F_x = weights_x · TFR · 0,488` separata dalla sopravvivenza neonatale (`L[1,0] = P₀`), evitando di applicare P₀ due volte.
- **Profilo di fecondità per età reale** (da "Fecondità per età della madre", ISTAT), non una gaussiana sintetica: il profilo italiano è asimmetrico con coda sopra i 40 anni e una gaussiana introduce distorsione in R₀.
- Sottodiagonale `P_x = L_{x+1}/L_x` dagli anni vissuti delle tavole ISTAT (più accurato di `1-q_x`).
- Interpolazione lineare per il calcolo di t½ sulla traiettoria simulata.

## 5. Risultati dell'implementazione (dati reali ISTAT, Fase 2 completata)

Esecuzione su dati reali: popolazione POSAS 2026 (30,02 M femmine, 26,0% over-65), tavole TVM 2024 (medie provinciali pesate), ASFR 2024 (TFR implicito 1,18 — coincide col dato ufficiale ISTAT; T media feconda 32,1 anni):

| Scenario (TFR) | r intrinseco | t½ asintotico | Primo dimezzamento | Femmine 2056 | Femmine 2076 |
|---|---|---|---|---|---|
| 0,95 | -2,31%/y | 30,0 anni | 49,0 anni | 21,5 M | 14,7 M |
| **1,18 (attuale)** | **-1,67%/y** | **41,5 anni** | **55,1 anni** | **22,4 M** | **16,2 M** |
| 1,20 | -1,62%/y | 42,8 anni | 55,8 anni | 22,5 M | 16,4 M |
| 1,30 | -1,38%/y | 50,2 anni | 59,6 anni | 22,9 M | 17,1 M |

Letture chiave:

- Il **t½ asintotico sul modello completo (41,5 anni a TFR 1,18)** è leggermente superiore ai ~40 anni della formula di Lotka della sezione 2: la formula R₀ ≈ TFR·0,488·0,99 è un'approssimazione, mentre il λ₁ della Leslie usa il profilo fecondità × sopravvivenza reale.
- Il **primo dimezzamento (~55 anni)** è più lontano dell'asintotico: effetto del momentum; la piramide attuale (26,0% over-65) è più "giovane" dell'autovettore stabile — che converge al **39,2% di over-65**.
- Prompt per riprodurre: `python3 src/download_istat.py && python3 src/parse_istat.py && python3 src/leslie.py --scenari`.

## 6. Collegamento con le policy (Fase 3, outline)

Il framework causale per stimare come una leva (es. copertura asili nido, rapporto affitto/reddito, precarietà femminile 25–39) muove il TFR — e quindi il t½ — è il seguente:

1. Panel provinciale (ISTAT / OMI / INPS), 107 province, ~10–12 anni.
2. DAG causale: separare confondenti (W), leve (T), mediatori (M — non condizionare su `eta_media_parto`, overcontrol bias).
3. Screening non-lineare: XGBoost + TreeSHAP, con lag within-province e two-way demeaning (province × anno) per effetti fissi.
4. Identificazione causale: Double Machine Learning / Causal Forests (EconML), cross-fitting raggruppato per provincia.
5. Diagnostica: Moran's I sui residui DML (pesi KNN spaziali), placebo test.
6. Controfattuale: `TFR_scenario = TFR_base + ATE·ΔT` injiettato nella matrice di Leslie → quanto si sposta il t½.
