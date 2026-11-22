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

## Ipotesi chiave da dichiarare esplicitamente

- Sopravvivenza alle età 80+: miglioramento futuro (trend e₀ vs. plateau) — sensitivity obbligatia, perché il costo LTC è concentrato nelle code di sopravvivenza.
- Composizione familiare: single / coppie senza figli a carico → sostituibilità dell'assistenza informale.
- Migrazioni: anche qui driver dominante (i caregiver professionali immigrati sono già oggi una quota rilevante del settore).

## Collegamenti con la Fase 5 (econometria collegata)

- **Popolazione attiva** → base contributiva previdenziale e pressione sul rapporto attivi/pensionati.
- **Dimensione delle coorti scolastiche** → domanda educativa futura.
- **Formazione dei nuclei familiari** → domanda abitativa (interazione con OMI, già prevista nella Fase 3).
- **Spazio fiscale locale** → invecchiamento dei piccoli comuni e spesa sanitaria territoriale.
