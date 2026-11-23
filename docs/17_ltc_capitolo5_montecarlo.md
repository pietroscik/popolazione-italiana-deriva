# LTC capitolo 5 — Modello attuariale probabilistico (Monte Carlo)

> Implementazione: `src/ltc_montecarlo.py`, esecuzione: `python3 src/ltc_montecarlo.py [B]` (default B=5.000; `--longevita` per gli scenari di mortalità). Chiude i punti P2-11…16 dell'audit. Status epistemico: tutto ciò che è qui sotto è **assunto/simulato** (v. tabella nel README) — il Monte Carlo quantifica l'incertezza *condizionata alle ipotesi*, non l'incertezza strutturale.

## 1. Prevalenza per età e sesso (P2-11)

Moltiplicatori parametrici dichiarati sopra i 65 anni: **F ×1,20 / M ×0,75** (ordine di grandezza delle indagini italiane: sopravvivenza femminile e vedovanza spostano la prevalenza 80+ verso le donne; ISTAT Condizioni di salute, Osservatorio Non Autosufficienza — àncora qualitativa, da calibrare sulle fonti ufficiali quando entreranno nel repo).

Risultato al 2056: **1,14 M claimants femmine vs 0,57 M maschi** — rapporto **2:1**, che rende quantitativo ciò che il capitolo 3 (caregiving informale) raccontava qualitativamente: la domanda LTC è femminile, l'offerta informale (45-64) è in corso di collasso proprio nelle coorti femmine.

## 2. Severità a tre livelli (P2-12)

| Livello | Quota claimants | Costo domiciliare | Costo residenziale |
|---|---|---|---|
| Lieve | 45% | 9.000 € | — |
| Medio | 35% | 16.000 € | 45.000 € |
| Grave | 20% | 26.000 € | 52.000 € |

Calibrazione per **coerenza col capitolo 2**: i costi blended (14,85k domiciliare; 47,5k residenziale sul mix medio+grave rinormalizzato) riproducono i 15k/48k del modello deterministico — quest'ultimo è il *caso centrale* del nuovo, non un modello diverso. La struttura residenziale accoglie solo medio+grave.

## 3. Monte Carlo (P2-13/14) — distribuzioni dichiarate

| Parametro | Distribuzione | Centralità |
|---|---|---|
| Moltiplicatori di sesso | Lognormale (σ=0,10) | 1,20 F / 0,75 M |
| Mix di severità | Dirichlet(α=100) | (0,45; 0,35; 0,20) |
| Costi domiciliare per livello | Lognormale (σ=0,15) | 9/16/26k |
| Costi residenziale | Lognormale (σ=0,10) | 45/52k |
| Quota domiciliare | Beta(65, 35) | 0,65 |
| Calibrazione informale r0 | Normale (σ=1) | 11 |
| Pendenza logistica b | Lognormale (σ=0,10) | 2 |
| **Miglioramento annuo mortalità ρ** | Uniforme [0; 1%] | demografia campionata per replica |
| Scala TFR | Normale (σ=0,03) | 1,00 |

B=5.000 repliche (~35 s su CI): ogni replica **riesima la Leslie due sessi** con mortalità migliorata e TFR scalati.

## 4. Risultati (prezzi 2026)

### Costo al picco 2056

| Statistica | mld € |
|---|---|
| Media | **32,3** |
| Q05 | 20,6 |
| Mediana | 32,3 |
| Q95 | **44,2** |

**Letture**: la media Monte Carlo (32,3) è coerente col deterministico del capitolo 2 (31,7): il modello precedente è il caso centrale, non un'ipotesi favorevole. L'intervallo [20,6; 44,2] è il numero giusto da citare con il claim "il costo sarà ~31 mld": **C₂₀₅₆ ∈ [23; 40] mld€ a prezzi 2026, condizionato alle ipotesi**.

### Valore attuale del programma 2026-2081 (P2-15)

Sconto reale 1,5%, inflazione generale 2%, **eccesso di inflazione sanitaria campionato** [0; 1%]:

| Statistica | mld € (valore 2026) |
|---|---|
| Media | **1.084** |
| Q05 | 638 |
| Q95 | 1.579 |

L'ordine di grandezza è ~1.000 mld€ in 55 anni: il confronto giusto per il quadro polizza-fondo (capitolo 4), non per il singolo anno di PIL.

## 5. Scenari di longevità (P2-16)

| ρ (miglioramento annuo mortalità) | Claimants 2056 | Claimants 2081 |
|---|---|---|
| 0% | 1,686 M | 1,430 M |
| 0,5% | 1,692 M | 1,435 M |
| 1% | 1,698 M | 1,441 M |

**Lettura controintuitiva ma robusta**: +1% annuo di miglioramento survival aggiunge solo **+0,8% di claimants al 2081**. Con TFR a 1,1-1,2 le coorti in ingresso sono così piccole che vive più a lungo fa più che altro *riempire* le fasce 80+ che il trend demografico già gonfia; la dominante resta la struttura per età, non la sopravvivenza. È il riflesso attuariale di λ₁=0,983: longevità e fecondità non sono simmetriche.

## 6. Limiti

- Le distribuzioni sono ipotesi, non stime (status epistemico: assunto). Il Monte Carlo misura quanto le conclusioni sono sensibili alle ipotesi, non la probabilità che le ipotesi siano vere.
- Mancano ancora le fonti ufficiali per i moltiplicatori di sesso e il mix di severità (ANIA-Sapienza multistato è il passo naturale successivo — già in docs/14).
- Il modello di base non simula l'insorgenza/recupero per coorte (incidenza × durata): resta un modello di **prevalenza**, conservativo per un fondo (v. docs/14).
- La correlazione tra parametri (es. costi domiciliare/residenziale) è posta nulla.
