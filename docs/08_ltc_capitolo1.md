# LTC — Capitolo 1: domanda assistenziale e caregiver potenziali

> Prima stima del capitolo LTC ([03_roadmap_ltc.md](03_roadmap_ltc.md)), costruita direttamente sul modello Leslie-Rogers a due sessi ([07_leslie_rogers_migrazioni.md](07_leslie_rogers_migrazioni.md)). Implementazione: `src/ltc.py`, esecuzione: `python3 src/ltc.py [saldo]`.

## 1. Metodo

Per ogni anno proiettato `src/ltc.py` estrae dal vettore di stato per età:

- **over-80**: bacino di domanda LTC (le fasce a intensità assistenziale massima)
- **claimants**: popolazione non autosufficiente attesa, applicando una **prevalenza per fascia d'età parametrica** (0,5% sotto i 65; 2% 65-69 → 28% 90+; ordini di grandezza coerenti con le indagini sul settore, da calibrare su ISTAT Condizioni di salute / Osservatorio non autosufficienza appena disponibili nel repo)
- **caregiver potenziali**: tutti i residenti **45–64 anni** (proxy dell'assistenza informale familiare, la definizione più ampia possibile)
- **rapporto caregiver/claimant**: il driver del costo medio LTC — se scende, una quota crescente della domanda non può essere assorbita dall'assistenza informale e migra verso quella formale (domiciliare pubblica o istituzionalizzata), con salto di costo unitario per assistito

## 2. Risultati (2026, TFR 1,18, saldo migratorio +280k/anno)

| Anno | Popolazione | Over-80 | Claimants | Caregivers (45-64) | Caregivers per claimant |
|---|---|---|---|---|---|
| 2026 | 58,9 M | 4,61 M | 1,25 M | 18,1 M | 14,5 |
| 2041 | 57,3 M | 5,83 M | 1,49 M | 15,4 M | 10,3 |
| **2056** | **52,7 M** | **7,46 M** | **1,68 M** | 15,3 M | 9,2 |
| 2071 | 46,7 M | 6,16 M | 1,47 M | 13,4 M | 9,1 |
| 2081 | 43,4 M | 6,06 M | 1,41 M | 11,7 M | 8,3 |

Controllo di qualità: gli over-80 2026 ricostruiti (4,61 M) coincidono con il dato osservato in piramide POSAS; i claimants odierni (~1,25 M) sono nell'ordine delle stime italiane di popolazione non autosufficiente.

## 3. Letture

1. **Il picco è al 2056**: il massimo di over-80 (7,46 M, +62% sul 2026) arriva quando la coorte 1960-1975 (baby boom) entra negli 80 anni e la coorte dei figli, già piccola, entra nella fascia di caregiving.
2. **Il rapporto caregiver/claimant crolla del 46% in 55 anni** (14,5 → 7,9): la contrazione della popolazione in età potenzialmente assistiva è **strutturale**, non congiunturale — le fasce 45-64 del 2050 sono oggi 20-35enni, coorti la cui dimensione è già scritta.
3. **Dopo il picco boomer gli over-80 scendono ma il rapporto non risale**: il denominatore (claimants) scende, ma il numeratore (caregivers) scende più in fretta, essendo alimentato dalle nascite di oggi. Il rapporto tocca il minimo al bordo dell'orizzonte (8,3 nel 2081): l'assistenza informale diventa strutturalmente più scarsa anche a parità di domanda.

## 4. Limiti da chiudere (prossimi passi del capitolo)

- **Prevalenze ufficiali**: la tabella attuale è parametrica — sostituire con tassi sesso×fascia da fonti ufficiali appena integrati
- **Costo per assistito**: serve distinguere assistito a domicilio vs istituzionalizzato, e il **salto di costo** quando il rapporto caregiver si esaurisce — è qui che il capitolo raccorda al perimetro attuariale (LTC premium, riserve)
- **Migrazione come input del caregiving**: una quota crescente dei caregiver professionali è di cittadinanza straniera; lo scenario saldo-0 e il saldo attuale divergono in modo rilevante proprio sul rapporto caregivers/claimants
- Rapporto caregivers attivi (non solo potenziali): modulare per tasso di partecipazione al caregiving per fascia d'età

I limiti 2-3 motivano l'integrazione con le Fasi causali: migrazione e sostegno alla fecondità competono sullo stesso piatto (denominatore del rapporto) documentato in [07 §4](07_leslie_rogers_migrazioni.md).
