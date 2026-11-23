# LTC — Capitolo 3: valore del caregiving informale, calibrazione, caregiver gap

> Seguito dei [capitoli 1](08_ltc_capitolo1.md) e [2](09_ltc_capitolo2_costi.md). Implementazione: `src/ltc_informale.py`, esecuzione: `python3 src/ltc_informale.py`.

## 1. Il valore del lavoro di cura non monetizzato

I capitoli precedenti conteggiano solo il costo **formale**. Il caregiving familiare è un costo ombra che il sistema sostiene in natura (ore di lavoro non pagate, carriera interrotta, contributi pensionistici non versati). Valutazione parametrica dichiarata: **30 ore/settimana** per claimant assistito in famiglia × valore ora **12 €** ≈ 18.700 €/anno per assistito.

| Anno | Claimants informali | Valore annuo del caregiving informale |
|---|---|---|
| 2026 | 1,07 M | **19,9 mld €** |
| 2056 | 0,49 M | 9,2 mld € |

Il valore ombra dell'assistenza familiare **si dimezza entro il 2056**: le famiglie assistono ~600 mila persone in meno e — coerentemente col capitolo 2 — la differenza migra sul formale, dove diventa spesa monetizzata (spesa formale 2026: 4,9 mld). L'ordine di grandezza del valore odierno (~20 mld €/anno) è coerente con le stime del settore sul valore del caregiving informale in Italia.

## 2. Sensitività della calibrazione logistica (capitolo 2)

Tutti i risultati del capitolo 2 dipendono dal flesso r0 della logistica della quota informale (calibrato a 11, ipotesi). Sensitività sul picco di costo formale:

| r0 (flesso logistico) | Picco di costo formale | Anno del picco | Costo 2081 |
|---|---|---|---|
| 9 (famiglia più resistente) | 22,0 mld € | 2081 | 22,0 mld |
| **11 (calibrazione base)** | **31,7 mld €** | **2056** | 31,5 mld |
| 13 (famiglia più fragile) | 38,1 mld € | 2056 | 34,3 mld |

Il picco si muove di **±25%** attorno alla calibrazione base (22-38 mld €), ma la **qualità del risultato non cambia**: in tutte le calibrazioni il costo formale cresce di un ordine di grandezza (da ~5 a 22-38 mld) e non torna ai livelli attuali entro il 2081. La datazione del picco (2056 vs fine orizzonte) è l'elemento più sensibile: se la famiglia risultasse più resistente, il picco slitta oltre il 2081 (dopo il passaggio della coorte boomer, su livelli comunque doppi di oggi).

## 3. Il caregiver gap migratorio

**Domanda**: quale flusso migratorio annuo servirebbe per mantenere il rapporto caregiver/claimant sopra la soglia oltre cui l'assistenza informale cede (~11)?

| Saldo migratorio annuo | Rapporto minimo (su 55 anni) | Anno |
|---|---|---|
| 0 | 7,15 | 2081 |
| +280k (attuale) | 8,30 | 2081 |
| +600k (break-even popolazione) | 9,05 | 2081 |
| +1.000k | 9,61 | 2081 |
| **+2.500k** | **10,48** | 2081 |

**Risultato: la migrazione da sola non basta.** Anche ipotizzando un flusso di 2,5 milioni di netti l'anno (quasi dieci volte l'attuale), il rapporto resta sotto la soglia: il denominatore (claimants 80+, la coorte boomer) cresce più in fretta di quanto qualsiasi flusso realistico di 45-64enni possa compensare. Il caregiver gap si chiude solo agendo anche sul lato domanda (prevenzione della non autosufficienza) e sulla produttività dell'assistenza formale, non solo sull'offerta di caregivers.

## 4. Sintesi della catena LTC

| Capitolo | Risultato |
|---|---|
| 1 — domanda e caregivers | picco over-80 7,5 M (2056); rapporto caregiver/claimant -46% |
| 2 — costo formale | picco 31,7 mld € / 1,4% PIL (2056), x6 sul 2026 |
| 3 — valore ombra e gap | valore informale 19,9 → 9,2 mld €; caregiver gap non colmabile dalla sola migrazione |

Limiti dichiarati di tutti i capitoli: prevalenze e costi parametrici (da ancorare a fonti ufficiali), PIL congelato al 2026, assistenza informale modellata come aggregato nazionale (eterogeneità regionale fuori perimetro: raccordo naturale con l'infrastruttura provinciale della Fase 3).
