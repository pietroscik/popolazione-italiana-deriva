# Origine del progetto — Seminario CN Attuari "Quale sviluppo in Italia per le coperture LTC"

> Roma, 26 ottobre 2026 — Consiglio Nazionale degli Attuari / Assoprevidenza. Questo repository nasce da quell'evento: i materiali (Di Falco/ANIA, De Tommaso/Secondo Welfare, Casdic, Ordine degli Attuari) sono la domanda a cui le analisi qui dentro cercano di dare una base quantitativa. Questo documento mette in correlazione i contenuti dell'evento con i risultati del repo.
>
> **Natura del riferimento**: esclusivamente documentale. Il presente progetto è autonomo e indipendente; non è commissionato, patrocinato, approvato o validato dal Consiglio Nazionale degli Attuari, da Assoprevidenza né da altri organismi citati.

## I quattro interventi e cosa dicono

### 1. Di Falco (ANIA) — La LTC assicurativa: basi tecniche, soluzioni
- **Premessa**: più anziani → più bisogno di assistenza; **meno caregiver familiari** → il modello attuale (prestazioni pubbliche insufficienti, peso sulle famiglie) va sotto pressione
- Basi tecniche ANIA-La Sapienza (2016): indennità di accompagnamento INPS su 14 anni, modello multistato markoviano, Lee-Carter/Brouhns esteso, tavole proiettate al **2043**
- Fondo LTC del settore assicurativo (CCNL 2004): 0,5% della retribuzione, rendita vitalizia rivalutabile di 15.000 € iniziali, gara quinquennale che esternalizza il rischio
- Retail: riserve LTC ramo IV < 1,2 mld € — la copertura generalizzata è lontana

### 2. De Tommaso (Secondo Welfare) — Il caso tedesco e la riforma Pnog 2026-27
- Quinto pilastro della sicurezza sociale dal 1995: aliquota 3,6% su salari e pensioni (4,2% senza figli), 5 gradi, importi fissi
- **Deficit atteso ~8 mld € nel 2027** senza riforma (15 mld nel 2028); Pnog ≈ 6,25 mld di nuove entrate senza toccare l'aliquota base
- Quota media a carico del residente: **3.364 €/mese** nel primo anno (~1.775 € per la sola cura)
- 80% sceglie il denaro, 70% è assistito a domicilio; la cassa versa i contributi pensionistici dei caregiver familiari (≥10h/settimana)

### 3. Casdic — La LTC del credito in esercizio
- 399.021 aventi diritto (248.160 attivi + 150.861 cessati); contributi 100-400 €/anno a carico delle aziende dal 2012
- Formula a rimborso (ramo danni): massimale 16.800 € dal 2013, rimborso medio ~11.700 €
- Fondazione con governance separata (Prometeia come advisor/risk manager)

### 4. Ordine degli Attuari — La proposta multi-pilastro
- Piattaforma: LTC dentro la previdenza complementare (~10 milioni di aderenti), adesione automatica, rendita di base uguale per tutti
- **Esempio numerico: rendita vitalizia di 500 €/mese → premio puro 113 €/anno medio (3,5‰ della retribuzione)** con aderenti costanti; **74 €/anno (2,3‰)** con aderenti crescenti
- Sistema finanziario: ripartizione dei capitali di copertura (come il Fondo ANIA); definizione unica (via INPS, poi L. 33/2023); presidio attuariale su sostenibilità/equità/accesso

## Cross-reading con i risultati del repo

| Tesi dell'evento | Riscontro quantitativo in questo repo |
|---|---|
| "Più anziani e **meno caregiver familiari**" (Di Falco, apertura) | Capitolo LTC 1: rapporto caregiver/claimant **-43%** al 2081 ([08](08_ltc_capitolo1.md)) |
| "Il peso sulle famiglie non è sostenibile" | Capitolo 2: spesa formale da 4,9 a **31,7 mld €/anno** (+x6) quando il caregiving informale cede dal 85% al 21% ([09](09_ltc_capitolo2_costi.md)); valore ombra dell'informale 19,9 mld €/anno ([10](10_ltc_capitolo3_informale.md)) |
| Basi tecniche "da costruire su dati italiani" (Di Falco, Sapienza 2016) | Il bisogno che quel tipo di basi incorporano — la piramide proiettata due sessi con migrazioni — è esattamente il substrato costruito in [02](02_dimezzamento.md)/[07](07_leslie_rogers_migrazioni.md): **fascia 80+ da 4,6 a 7,3 M al 2056** |
| Quota a carico residenza tedesca: **3.364 €/mese** (= ~40.400 €/anno) | Il nostro costo unitario residenziale parametrico (48.000 €/anno, [09 §1](09_ltc_capitolo2_costi.md)) è **dello stesso ordine** del caso tedesco osservato: la calibrazione iniziale era ragionevole, l'ancoraggio tedesco la conferma |
| "Il rischio grava su famiglie e finanza pubblica" (Ordine Attuari) | Caregiver gap non colmabile dalla sola migrazione ([10 §3](10_ltc_capitolo3_informale.md)); pressione previdenziale 0,40 → 0,72 ([11](11_fase5_economia_collegata.md)) |
| Lo shock da TFR che deteriinea il perimetro di sostenibilità | L'evento ha origine dal dibattito sul TFR: qui il legame è reso endogeno — **PSTR con soglia di non ritorno F ≈ 1,05** ([13](13_pstr_soglia_theta.md)): il perimetro dei 10 milioni di aderenti e il loro invecchiamento futuro sono una funzione del diramazione demografica sottostante |
| Premio puro 74-113 €/anno per rendita 500 €/mese (Ordine Attuari, ipotesi attuariali standard) | Estensione naturale: usare la Leslie-Rogers due sessi comepiramide di riferimento per la platea (~10M aderenti invecchiante), e il modello multistato su dati INPS come livello di servizio — dati pronti nel repo |

## Implicazioni per le prossime fasi del repo

1. **Capitolo attuariale (LTC 4)**: l'esempio numerico dell'Ordine degli Attuari (rendita 500 €/mese, premio puro 3,5‰ vs 2,3‰ a seconda della platea) è il target di calcolo: la nostra piramide due sessi con scenario TFR/migrazione può generare la platea invecchiante degli aderenti e il rapporto attivi/pensionati della fondazione — la differenza 113 vs 74 € è proprio dinamica di platea, il tema che questo repo quantifica direttamente
2. **Ancoraggio dei parametri DMV**: il costo residenziale tedesco (3.364 €/mese a carico) e il pattern di scelte (80% denaro, 70% domiciliarità) permettono di sostituire i placeholder parametrici dei capitoli 2-3 con valori osservati
3. **Modellazione del quarto attore — la platea della previdenza complementare**: aggiungere nei modelli una popolazione "aderenti" (per fascia di età, sesso) proiettata con la stessa Leslie-Rogers, per dare base concreta alle simulazioni attuariali del tavolo che l'Ordine ha promesso
4. **La definizione unica** (INPS in avvio, L. 33/2023 a regime): quando arriveranno i microdati INPS per fascia (il passaggio del modello ANIA-Sapienza), la pipeline è pronta a riceverli come stratificazione di prevalenza per fascia
