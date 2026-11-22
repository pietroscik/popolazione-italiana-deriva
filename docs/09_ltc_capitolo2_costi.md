# LTC — Capitolo 2: dal rapporto caregiver al costo aggregato

> Seguito del [capitolo 1](08_ltc_capitolo1.md). Implementazione: `src/ltc_costi.py`, esecuzione: `python3 src/ltc_costi.py [saldo]`.

## 1. Il modello di copertura a tre livelli

La domanda LTC (claimants, dal capitolo 1) viene smistata su tre livelli di copertura:

1. **Assistenza informale** (familiare): la quota coperta è una **logistica nel rapporto caregiver/claimant** con punto di flesso ~11 e pendenza 2 — al rapporto attuale (~14,5) la famiglia assorve ~85% della domanda; al calare del rapporto la capacità informale cede e la domanda migra verso il formale
2. **Assistenza formale domiciliare** (ADI / day care): ~65% della domanda formale, costo unitario ~15.000 €/anno
3. **Assistenza residenziale** (RSA): ~35% della domanda formale, costo unitario ~48.000 €/anno

Il costo aggregato del capitolo è quello del **formale** (domiciliare + residenziale); quello informale è non monetizzato (valore economico del caregiving familiare, non rilevato dal documento corrente).

**Tutti i parametri (flesso logistico, split domiciliare/residenziale, costi unitari) sono dichiarati e parametrici**: ordini di grandezza del settore italiano (retta RSA 40-60k €/anno, costi domiciliari dell'ordine di 15k), da ancorare a fonti ufficiali appena integrate. Il denominatore macro (PIL nominale 2.200 mld) è congelato al 2026: semplificazione dichiarata, da sostituire con una proiezione di PIL quando serve confronto di lungo periodo in % PIL.

## 2. Risultati (2026, TFR 1,18, saldo +280k/anno)

| Anno | Claimants | Rapporto | Informali | Domiciliare | Residenziali | Costo formale (mld €) | % PIL |
|---|---|---|---|---|---|---|---|
| 2026 | 1,25 M | 14,5 | 1,07 M | 0,12 M | 0,06 M | 4,9 | 0,22% |
| 2041 | 1,49 M | 10,3 | 0,62 M | 0,57 M | 0,31 M | 23,2 | 1,05% |
| **2056** | **1,66 M** | 9,3 | 0,49 M | 0,76 M | 0,41 M | **31,0** | **1,41%** |
| 2071 | 1,47 M | 9,1 | 0,42 M | 0,69 M | 0,37 M | 28,1 | 1,28% |
| 2081 | 1,41 M | 8,3 | 0,29 M | 0,73 M | 0,39 M | 29,8 | 1,35% |

**Picco del costo: 31,0 mld € (1,41% del PIL) nel 2056** — piccolo picco coerente con il picco over-80 del capitolo 1.

## 3. Letture

1. **Il costo cresce 6 volte in 15 anni** (da 4,9 a 31 mld) per due motori congiunti: la crescita dei claimants (+33%) e il **cedimento dell'assistenza informale** (da 85% a 49%) — il secondo fattore domina: il costo non scende sensibilmente dopo il 2056 pur scendendo i claimants, perché la quota informale continua a cedere con il rapporto.
2. **Il driver di costo non è l'invecchiamento quanto la scarsità di caregivers**: a parità di domanda, un rapporto caregiver/claimant che scende da 14 a 8 raddoppia-triplica il costo formale del sistema. È l'arco di ponte tra questo capitolo e il capitolo 1: la stessa dinamica demografica (coorti 45-64 in contrazione strutturale) che erode il numeratore del rapporto diventa, qui, il moltiplicatore dei costi formali.
3. **Implicazione per il perimetro attuariale**: il salto di costo medio per assistito formale (~28-31k €/anno medi) e la finestra di stress 2041-2071 sono i termini entro cui dimensionare **premium LTCI e riserve**. La finestra coincide con quella prevista nella [roadmap attuariale](03_roadmap_ltc.md) — con il picco sito a metà coorte del baby boom negli 80+.

## 4. Limiti e passi successivi

- **Parametri da ancorare**: flesso logistico e costi unitari sono ordini di grandezza, non stime — reintegrare con ISTAT Condizioni di salute, Osservatorio NAS, tariffe regionali ADI/RSA
- **Split 65/35 fisso**: la composizione domicilio/residenza varia col grado di gravità e la pressione sui caregivers — modulare entrambe col rapporto (più caregivers scarsi → più residenzializzazione, non solo più formale)
- **PIL congelato**: per confronti di sostenibilità nella finestra 2041-2081 serve una traiettoria di PIL, non il valore 2026
- **Costo informale non monetizzato**: il valore del tempo di caregiving familiare (perdita di lavoro, pensione, salute del caregiver) è un capitolo separato — il numero odierno è l'ordine di 1,1 milioni di persone assistite in famiglia, con il costo pieno che sposta sì il valore assoluto, ma non il segno della dinamica
- **Eterogeneità territoriale**: i costi unitari e la pressione sul caregiving sono fortemente regionali (Nord vs Mezzogiorno): l'infrastruttura provinciale della Fase 3 è il raccordo naturale

## Nota tecnica

Il capitolo non introduce dipendenze: tutto è `numpy` + le funzioni già nella Leslie-Rogers. Il report è auto-contenuto: `python3 src/ltc_costi.py [saldo]` produce la tabella e il picco.
