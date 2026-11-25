# Executive summary (per il pubblico attuariale)

> Una pagina. I numeri con lo status epistemico corretto: **osservato** (ISTAT), **stimato** (modello), **assunto** (parametrico), **simulato** (scenario). Dettagli e limiti nei documenti citati.

## Il fatto demografico

Con quota femminile alla nascita 0,488 e sopravvivenza ISTAT, il Lotka integrale esatto (verificato identico a ln λ₁ della Leslie alla sesta cifra): **scenario A (TFR 2024 = 1,18, base del modello): R₀ = 0,573, r = −1,6685%/anno, t½ asintotico 41,5 anni**; **scenario B (TFR 2025 = 1,14, 355.772 nati ISTAT): R₀ = 0,554, r = −1,7711%/anno, t½ 39,1 anni**. Ogni generazione di madri si rimpiazza al ~55-57%: il dimezzamento è della struttura dell'albero genealogico, non dell'età media.

## La soglia

Sul panel europeo NUTS-2 — **stima headline sulla finestra 2013-2023** (282 regioni, 2.366 osservazioni post-filtraggio) e **panel esteso 1990-2024** usato per il test di stabilità temporale — la PSTR identifica un **punto di non ritorno a TFR ≈ 0,91** (era post-2013, supporto bootstrap 66% sul campione headline; batteria strutturale docs/13 §5.7: nel regime corrente la mappa è quasi tangente a zero nel regime basso, supporto 12-18% sul panel esteso — compatibile/illustrativa, non costante identificata; l'era 2001-2012 ha struttura specchiata a tre radici, supporto 70,7%. θ̂ OLS/CRE stabile in [1,66–1,72]) e un attrattore a ≈ 1,61. **Sul γ della DR (v. docs/13 §5.5)**: positivo in OLS e LOCO (33/33), ma **negativo sotto strumentazione corretta a t−15/t−20** (γ̂_IV −0,045/−0,055; F 2.537–4.089; Hansen J=0,23 p=0,63): il segno non è identificato in modo robusto — il γ̂>0 pooled va letto come eterogeneità regionale persistente. IV per ere (docs/13 §5.6): l'associazione positiva è un fenomeno 2001-2012; nell'era corrente γ̂ ≈ 0 (±0,07), senza effetto robusto della DR. L'Italia è **sopra** soglia ma vicino; la **Sardegna (0,85) è dentro la trappola**: la sua Leslie regionale dimezza in **26 anni** (−44% di popolazione al 2081). Risultato onesto: cross-era la PSTR **non** prevale (il fallimento era instabilità dei parametri tra regimi); **within-era (train 2013-2019, test 2020-2024) batte nettamente il benchmark statico (DM +6,49)** e nella banda trappola (F<1,35) è il miglior modello in RMSE — il valore è strutturale (regimi e soglie), con vantaggio previsivo locale nel regime basso.

## Il costo LTC

Catena dei claimants: **1,69 M non autosufficienti al 2056 (unisex; per sesso: 1,14 M F vs 0,57 M M, ~67% femmine)**; caregiver potenziali 45-64 anni: **livello −37% (18,1→11,4 M)** e **rapporto caregiver/claimant −46% (14,5→7,9)** tra 2026 e 2081 — è il rapporto, non la sola base, a innescare la migrazione verso il formale. Il costo formale aggregato al 2056 è **C = 32,3 [20,6; 44,2] mld€** (Monte Carlo B=5.000, prezzi 2026, ipotesi dichiarate) e il valore attuale 2026-2081 ammonta a **~1.084 mld€** (sconto reale 1,5%). Driver dominante per elasticità: **prevalenza** (el. 2,12) e **break della rete informale** (el. 1,26) — non il TFR (0,08). Longevità +1%/anno aggiunge solo 0,8% di domanda: con λ₁<1, la struttura per età prevale sulla sopravvivenza.

## Il capitolo attuariale

Una rendita LTC di **500€/mese** (esempio Ordine Attuari) erogata sulla platea della previdenza complementare (~10M aderenti), contributo annuo teorico simulato in ripartizione del costo ("premio puro": indicatore modellistico, non tariffa): **~21€/anno** oggi, **253€ al 2081** con adesioni automatiche; **1.409€** con platea chiusa (insostenibile). Con indicizzazione 2%: 750€ nominali (3%: 1.284€) — il premio reale deflato è identico (253€), l'indicizzazione è puro effetto-prezzo. La platea chiusa è la soluzione fallimentare; servono adesioni automatiche o meccanismi equivalenti.

## Cosa è solido e cosa è parametrico

| Solido (osservato/stimato/verificato) | Parametrico (dichiarato) |
|---|---|
| dati ISTAT/Eurostat pipelineati, 82 test, CI end-to-end | prevalenze LTC per età/sesso |
| λ₁, R₀, Lotka = Leslie (6ª cifra) — scenario A e B | profilo migratorio Rogers-Castro |
| soglia PSTR (**era post-2013**, supporto bootstrap 66%, kinked DR₀→0) | costi unitari 15k/48k€ |
| backtest DM/CW (negativo, dichiarato) | mix di severità LTC |

Prossimi passi dichiarati: tabelle multistato ANIA-Sapienza, platea COVIP reale, MAPE coorte 0-11 sulle strutture regionali storiche.

Quadro completo: [README](../README.md) • [Dimezzamento](02_dimezzamento.md) • [PSTR](13_pstr_soglia_theta.md) • [LTC Monte Carlo](17_ltc_capitolo5_montecarlo.md) • [Capitolo attuariale](14_ltc_capitolo4_attuariale.md)
