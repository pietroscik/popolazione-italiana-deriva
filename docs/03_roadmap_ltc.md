# Roadmap: stime attuariali su LTC

## Il ponte demografia → LTC

Il punto di contatto più rilevante tra la deriva demografica italiana e le stime attuariali LTC (Long-Term Care) non è il conteggio assoluto degli over-65, ma il **rapporto caregiver potenziali / anziani**: il costo medio LTC e la sostenibilità del modello basato su assistenza informale (familiare) dipendono da questo rapporto, che si deteriora strutturalmente più in fretta della popolazione totale.

## Finestra critica: coorte 1960–1975

La coorte del baby boom italiano (nati 1960–1975, oggi 50–65enni) entrerà nella fascia di massimo utilizzo LTC (80+) tra il **2040 e il 2055**. Nella stessa finestra:

- i potenziali assistenti familiari (figli di quelle coorti, oggi 30–45enni) appartengono alle generazioni della denatalità post-1975 — si assottigliano a un ritmo strutturale (~t½ per generazione, vedi [02_dimezzamento.md](02_dimezzamento.md));
- l'onda di mortalità dei baby boomer porterà i decessi verso i picchi di ~750–800k/anno.

## Piano di lavoro (Fase 4)

1. **Prevalenza LTC per fascia di età e sesso**: integrare le proiezioni della piramide (output della matrice di Leslie) con tassi di prevalenza di non-autosufficienza per fascia 65+/80+ (fonti: ISTAT salute, Ministero della Salute, Osservatorio sulla non autosufficienza).
2. **Claimants attesi LTC 2040–2080**: proiezione del numeratore (anziani 80+ con bisogno di assistenza) e del denominatore (caregiver informali potenziali) sotto scenari TFR e migrazione alternativi.
3. **Scenario di costo**: combinare i claimants proiettati con costo medio per assistito (informale vs. istituzionalizzato) → scenario costi aggregati LTC, anche sotto ipotesi di diverso mix di policy (investimenti in assistenza domiciliare).
4. **Valutazione attuariale**: tariffe LTCI (Long-Term Care Insurance), riserve attuariali, test di solvency sulle code di longevità — sfruttando la distribuzione per età proiettata (non solo il totale) per il calcolo della duration delle passività.

## Stato di avanzamento (aggiornato)

| Passo | Stato | Risultato |
|---|---|---|
| 1. Prevalenza LTC per fascia | ◐ parametrica ([08](08_ltc_capitolo1.md)): 0,5% <65 → 28% 90+ | da ancorare a fonti ufficiali |
| 2. Claimants attesi 2040-2080 | ✔ | picco 1,66 M al 2056 ([08](08_ltc_capitolo1.md)) |
| 3. Sbalzi di costo | ✔ | picco 31 mld € / 1,4% PIL al 2056, robustezza ±25% ([09](09_ltc_capitolo2_costi.md), [10](10_ltc_capitolo3_informale.md)) |
| 4. Valutazione attuariale (premium, riserve, duration) | ⬜ | finestra di stress 2041-2081 quantificata (~28-31 mld/anno formali) |
| Extra: caregiver gap | ✔ | non colmabile dalla sola migrazione ([10](10_ltc_capitolo3_informale.md)) |

## Ipotesi chiave da dichiarare esplicitamente

- Sopravvivenza alle età 80+: miglioramento futuro (trend e₀ vs. plateau) — sensitivity obbligatia, perché il costo LTC è concentrato nelle code di sopravvivenza.
- Composizione familiare: single / coppie senza figli a carico → sostituibilità dell'assistenza informale.
- Migrazioni: anche qui driver dominante (i caregiver professionali immigrati sono già oggi una quota rilevante del settore).

## Collegamenti con la Fase 5 (econometria collegata)

- **Popolazione attiva** → base contributiva previdenziale e pressione sul rapporto attivi/pensionati.
- **Dimensione delle coorti scolastiche** → domanda educativa futura.
- **Formazione dei nuclei familiari** → domanda abitativa (interazione con OMI, già prevista nella Fase 3).
- **Spazio fiscale locale** → invecchiamento dei piccoli comuni e spesa sanitaria territoriale.
