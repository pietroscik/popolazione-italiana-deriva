# Executive summary (per il pubblico attuariale)

> Una pagina. I numeri con lo status epistemico corretto: **osservato** (ISTAT), **stimato** (modello), **assunto** (parametrico), **simulato** (scenario). Dettagli e limiti nei documenti citati.

## Il fatto demografico

Con quota femminile alla nascita 0,488 e sopravvivenza ISTAT, il Lotka integrale esatto (verificato identico a ln λ₁ della Leslie alla sesta cifra): **scenario A (TFR 2024 = 1,18, base del modello): R₀ = 0,573, r = −1,6685%/anno, t½ asintotico 41,5 anni**; **scenario B (TFR 2025 = 1,14, 355.772 nati ISTAT): R₀ = 0,554, r = −1,7711%/anno, t½ 39,1 anni**. Ogni generazione di madri si rimpiazza al ~55-57%: il dimezzamento è della struttura dell'albero genealogico, non dell'età media.

## La soglia

Sul panel europeo NUTS-2 — **stima headline sulla finestra 2013-2023** (282 regioni, 2.366 osservazioni post-filtraggio) e **panel esteso 1990-2024** usato per il test di stabilità temporale — la PSTR con strumentazione della dependency ratio (first-stage F=340; γ_IV = +0,129; backtest fixed-origin addestrato su 2001-2012) identifica un **punto di non ritorno a TFR ≈ 0,91** e un attrattore a ≈ 1,61, γ>0 robusto per paese (LOCO) e finestra. L'Italia è **sopra** soglia ma vicino; la **Sardegna (0,85) è dentro la trappola**: la sua Leslie regionale dimezza in **26 anni** (−44% di popolazione al 2081). Risultato onesto: il backtest DM/CW mostra che la PSTR **non** prevede meglio di un modello lineare o di un random walk — il suo valore è strutturale (regimi e soglie), non previsivo.

## Il costo LTC

Catena dei claimants: **1,69 M non autosufficienti al 2056 (~67% femmine, rapporto 2:1)**; caregiver potenziali 45-64 anni: **livello −37% (18,1→11,4 M)** e **rapporto caregiver/claimant −45% (14,5→7,9)** tra 2026 e 2081 — è il rapporto, non la sola base, a innescare la migrazione verso il formale. Il costo formale aggregato al 2056 è **C = 31,8 [23,2; 40,2] mld€** (Monte Carlo B=5.000, prezzi 2026, ipotesi dichiarate) e il valore attuale 2026-2081 ammonta a **~1.057 mld€** (sconto reale 1,5%). Driver dominante per elasticità: **prevalenza** (el. 2,12) e **break della rete informale** (el. 1,26) — non il TFR (0,08). Longevità +1%/anno aggiunge solo 0,8% di domanda: con λ₁<1, la struttura per età prevale sulla sopravvivenza.

## Il capitolo attuariale

Una rendita LTC di **500€/mese** (esempio Ordine Attuari) erogata sulla platea della previdenza complementare (~10M aderenti), premio puro pay-as-you-go: **~21€/anno** oggi, **251€ al 2081** con adesioni automatiche; **1.397€** con platea chiusa (insostenibile). Con indicizzazione 2%: 746€ nominali (3%: 1.275€) — il costo reale deflato è identico, l'indicizzazione è puro effetto-prezzo. La platea chiusa è la soluzione fallimentare; servono adesioni automatiche o meccanismi equivalenti.

## Cosa è solido e cosa è parametrico

| Solido (osservato/stimato/verificato) | Parametrico (dichiarato) |
|---|---|
| dati ISTAT/Eurostat pipelineati, 76 test, CI end-to-end | prevalenze LTC per età/sesso |
| λ₁, R₀, Lotka = Leslie (6ª cifra) — scenario A e B | profilo migratorio Rogers-Castro |
| soglia PSTR (**era post-2013**, supporto bootstrap 66%, kinked DR₀→0) | costi unitari 15k/48k€ |
| backtest DM/CW (negativo, dichiarato) | mix di severità LTC |

Prossimi passi dichiarati: tabelle multistato ANIA-Sapienza, platea COVIP reale, MAPE coorte 0-11 sulle strutture regionali storiche.

Quadro completo: [README](../README.md) • [Dimezzamento](02_dimezzamento.md) • [PSTR](13_pstr_soglia_theta.md) • [LTC Monte Carlo](17_ltc_capitolo5_montecarlo.md) • [Capitolo attuariale](14_ltc_capitolo4_attuariale.md)
