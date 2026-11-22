# Fase 5 — Econometria collegata: ind economici dalla piramide

> Implementazione: `src/economia_collegata.py`, esecuzione: `python3 src/economia_collegata.py [saldo]`. Proiezioni a TFR 1,18 e saldo +280k/anno, come nei capitoli LTC.

## Indicatore

Anno per anno dal vettore di stato a due sessi:

- **attivi 15-64** → base contributiva previdenziale e presidio del mercato del lavoro
- **anziani 65+** → proxy dell'esercizio pensionistico e della domanda sanitaria/assistenziale
- **giovani 0-14 e scolastici 0-17** → coorti educative future
- **nuclei potenti di formazione famiglia 20-44** → driver strutturale della domanda abitativa
- **dependency ratio anziani** (65+/15-64) → pressione fiscale e previdenziale per attivo

## Risultati (2026, saldo +280k/anno)

| Anno | Pop. | Attivi 15-64 | Anziani 65+ | Dep. ratio anziani | 0-14 | Nuclei 20-44 |
|---|---|---|---|---|---|---|
| 2026 | 58,9 M | 37,3 M | 14,8 M | **0,40** | 6,9 M | 16,2 M |
| 2041 | 57,3 M | 32,9 M | 18,8 M | 0,57 | 5,6 M | 15,5 M |
| 2056 | 52,7 M | 29,6 M | 18,2 M | **0,62** | 4,9 M | 12,3 M |
| 2071 | 46,7 M | 25,8 M | 16,9 M | 0,66 | 4,0 M | 10,8 M |
| 2081 | 43,4 M | 23,0 M | 16,6 M | **0,72** | 3,8 M | 10,0 M |

## Letture

1. **La pressione previdenziale quasi raddoppia**: 0,40 → 0,72 (+81%) significa passare da ~2,5 attivi per anziano a ~1,4. Il picco fiscale non è al picco degli over-80 (2056) ma cresce monotono fino al 2081: gli attivi scendono del -38% mentre gli anziani calano solo dell'-11%. (Le previsioni ISTAT mediano, che ipotizzano recovery parziale della fecondità, collocano il rapporto in una banda analoga: il numero d'ordine è condiviso.)
2. **La domanda abitativa ha un tetto strutturale**: i nuclei 20-44 scendono del -39% — quando le coorti della denatalità entrano nell'età di formazione famiglia, nessuna politica creditizia può ripristinare la demografia sottostante (... ma vedi [07_leslie_rogers_migrazioni.md](07_leslie_rogers_migrazioni.md): il profilo migratorio 20-39 è esattamente la contropartita).
3. **Coorti scolastiche: -45% in 55 anni** (6,9 → 3,8 M). Fuori orizzonte per l'istruzione primaria entro fine decennio, ma la compressione diventa operativa sugli istituti superiori dal 2040 e sull'università dal 2045.
4. **Il raccordo attuariale**: la Fase 4 LTC e questa Fase 5 condividono il medesimo numeratore strutturale (attivi/caregivers). Ogni leva che sostiene il rapporto — fecondità ora, migrazione domani — ha un doppio rendimento: sulla spesa LTC e sulla base contributiva.

## Sensitività al saldo migratorio (stessi indici a saldo attuale vs zero)

Il denominatore comune di tutti gli indici di questa fase è la popolazione in età attiva: la migrazione è пер definizione concentrata nelle fasce 20-39 (profilo Rogers-Castro, [07](07_leslie_rogers_migrazioni.md)), quindi gli effetti qui sono amplificati rispetto alla popolazione totale:

| Indice (2081, TFR 1,18) | saldo +280k/anno | saldo 0 | Delta |
|---|---|---|---|
| Attivi 15-64 | 23,0 M | 15,4 M | -33% |
| Dependency ratio anziani | 0,72 | 0,76 | +6% rel. |
| Nuclei 20-44 | 10,0 M | 6,9 M | -31% |

Nota: a saldo zero gli attivi scendono sotto i 16 milioni — ma il dependency ratio sale solo di un 6% relativo, perché senza migrazione scendono sia gli attivi sia gli anziani (coorti più piccole in ingresso nelle fasce 65+ dopo il 2050). L'effetto dominante della migrazione è sul **livello** della base attiva e dei nuclei, non sul rapporto: è il riflesso del risultato del [07](07_leslie_rogers_migrazioni.md) (break-even a ~617k/anno per la stabilità numerica).
