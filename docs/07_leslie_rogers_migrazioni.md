# Leslie-Rogers: migrazione per età e modello a due sessi

> Completamento del blocco dinamico (Fase 3 dell'architettura, [04_architettura_due_strati.md](04_architettura_due_strati.md)): il saldo migratorio per età entra nel modello di proiezione e la popolazione maschile viene aggiunta.

## 1. Il profilo migratorio (Rogers-Castro)

L'ISTAT non pubblica il saldo migratorio nazionale per singola età; il livello totale invece sì (saldo con l'estero: **+263 mila nel 2024**, **+296 mila nel 2025**, dati definitivi/provvisori — comunicati Migrazioni interne e internazionali 2024-2025). Il profilo per età è quindi modellato con la parametrizzazione **Rogers-Castro** (`src/migration.py`): tre componenti (infanzia a decadimento rapido, picco della forza lavoro centrato sui 25 anni, picco pensionistico sui 65), poi ricalibrato in livello così che la somma sul vettore di età dia il saldo annuo prescelto, pesato per la popolazione residente di ciascuna età.

Limiti dichiarati: il profilo è quello tipico di un flusso complessivo; il saldo con l'estero italiano non è neutrale nei confronti del profilo (es. espatri di laureati 25-34 vs ingressi per ricongiungimento), quindi la forma andrà ri-calibrata sui micro-dati di settore quando entrerà la Fase 3 causale. Il livello, invece, è direttamente osservato ISTAT.

## 2. Il modello a due sessi

`src/leslie.py: simulate_two_sex` — le nascite generate dalle donne (tassi ASFR per età) sono ripartite per sesso al parto (quota femminile 0,488), sopravvivenza sessuale separata (tavole TVM Femmine/Maschi, medie provinciali pesate) e migrazione sessuale separata.

Controllo di qualità: popolazione 2026 ricostruita = **58.942.828** (30,02 M femmine + 28,92 M maschi), coerente con la stima ISTAT.

## 3. Risultati (TFR 1,18 invariato, orizzonte 55 anni → 2081)

`python3 src/leslie.py --migrazioni`:

| Scenario saldo annuo | Pop. 2081 | Var. % | Lettura |
|---|---|---|---|
| 0 | 29,8 M | -49,4% | dimezzamento sconfina oltre l'orizzonte (~55 anni, coerente col modello solo-femmine) |
| +130.000 (saldo dimezzato) | 36,2 M | -38,7% | |
| **+280.000 (media 2024-25)** | **43,4 M** | **-26,3%** | ordine di grandezza della previsione ISTAT mediana (che assume anche recovery parziale della fecondità) |
| +400.000 (saldo alto) | 49,3 M | -16,4% | |

**Saldo di break-even: ~+616.000 migranti netti/anno** (profilo Rogers-Castro dinamico; ~+600.000 col profilo statico calibrato sulla struttura 2026, pre-fix) per mantenere la popolazione costante a TFR 1,18 e struttura per sesso/età attuale — circa **2,1 volte il saldo osservato 2024-25**. Non è uno shock frontale: il saldo oggi compensa il deficit naturale corrente (~-296 mila), ma il deficit cresce nel tempo perché le nascite continuano a contrarre (le madri potenziali sono le generazioni della denatalità) e una quota crescente del saldo serve solo a "riempire" coorti più piccole.

## 4. Lettura d'insieme

Congiungendo col [05_low_fertility_trap.md](05_low_fertility_trap.md): la migrazione agisce esattamente sul nodo che rende l'analisi departe dal regime asintotico — e il costo del ritardo è visibile qui. Lo shock di policy `u_uscita` richiesto per risalire dal regime a TFR 1,15 verso il bacino alto compete direttamente col fattore migrazione: 617 mila netti l'anno per la sola stabilit numerica, oppure un recupero di fecondità che allevi il spettro futuro deficit naturale. La combinazione dei due è il vero oggetto di policy.

## Nota tecnica

- La migrazione in `simulate_two_sex` è un flusso **assoluto annuo** (positivo o negativo), distribuito per età col Rogers-Castro pesato; il sesso è distribuito ~50/50. L'interfaccia precedente `simulate` (modello femminile, tasso di migrazione per età resta disponibile per compatibilità).
- Il saldo 2024 (+263k) e 2025 (+296k) sono rispettivamente definitivo e provvisorio: rivalutare a ogni aggiornamento ISTAT.
