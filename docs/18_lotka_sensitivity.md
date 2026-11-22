# Lotka integrale esatto e sensitivity sistematica

> Implementazione: `src/lotka.py` (`lotka_report`, esecuzione `python3 src/lotka.py`), `src/sensitivity.py` (`sensitivity_report`). Chiude i punti **P1-6** e **P1-9** dell'audit — gli ultimi due aperti.

## 1. Lotka integrale (P1-6): la tripla verifica del README

Il README usava l'approssimazione R₀ ≈ TFR × 0,488 × 0,99 (§"Risultato chiave del modello asintotico"). Il calcolo **esatto** dai vettori ISTAT processati:

| Quantità | Valore | Fonte |
|---|---|---|
| **R₀ esatto** = Σₓ ASFRₓ · s_f · lₓ | **0,5733** | lotka integrale |
| R₀ approssimato (formula README) | 0,5702 | confermata entro lo 0,6% |
| T (lunghezza media generazione) | **32,11 anni** | Σₓ x·mₓ·lₓ / R₀ |
| **r approx** = ln(R₀)/T | **−1,733%**/anno | |
| **r Lotka esatto** (equazione caratteristica, convenzione x+1) | **−1,6685%**/anno | bisezione su Σₑ^(−r(x+1))·mₓ·lₓ = 1 |
| **ln λ₁** (autovalore dominante Leslie) | **−1,6685%**/anno | matrice |
| Differenza r esatto − ln λ₁ | **0,0** (sesta cifra decimale) | verifica chiusa |
| t½ asintotico | 41,5 anni | coerenza confermata |

**Letture**:

1. **Il cerchio è chiuso**: analisi integrale di Lotka e matrice di Leslie danno lo *stesso* tasso intrinseco alla sesta cifra — la convenzione (x+1) nella caratteristica è quella della Leslie in uso (nascite in testa, sopravvivenza spostata di un anno). L'approssimazione ln(R₀)/T sopravvive come diagnostica rapida: sovrastima il declino di ~4% relativo (−1,73% vs −1,67%) perché ignora la struttura della sopravvivenza dentro la fascia fertile.
2. R₀ esatto 0,5733: **ogni generazione di madri viene sostituita al 57,3%** (la formula rapida diceva 55–57%: corretta come ordine di grandezza, ora è un numero, non una stima arrotondata).
3. Il README §"Risultato chiave" continua a citare l'approssimazione quando serve una formula in testa, ma ora rimanda qui per l'esatto.

## 2. Sensitivity sistematica OAT (P1-9): tornado su C₂₀₅₆

One-At-a-Time su C₂₀₅₆ = 31,29 mld€ (prezzi 2026, caso centrale — coincide col cap. 2 entro l'arrotondamento demografico e con la media Monte Carlo del cap. 5):

| Parametro | Perturbazione | C₂₀₅₆ lo → hi | **Elasticità** |
|---|---|---|---|
| **Prevalenza (moltiplicatore)** | ±20% | 15,3 → 44,6 | **+2,12** (sopra-lineare) |
| **r₀ break informale** | ±18% | 20,9 → 38,4 | **+1,26** |
| Quota domiciliare | ±10% | 33,8 → 28,8 | −0,81 |
| Costo unitario residenziale | ±20% | 27,3 → 35,3 | +0,63 |
| Costo unitario domiciliare | ±20% | 29,0 → 33,6 | +0,37 |
| Pendenza logistica b | ±25% | 33,8 → 29,6 | −0,21 |
| TFR scale (al 2056) | ±5% | 31,2 → 31,4 | **+0,08** |
| Miglioramento mortalità annuo | 0 → +1% | 31,3 → 31,8 | +1,7% totale |

**Letture**:

1. **I driver di C₂₀₅₆ sono epidemiologici e relazionali, non demografici**: prevalenza (el. 2,12) e punto di break dell'informale (r₀, el. 1,26) dominano; il TFR al 2056 pesa solo 0,08 perché a 30 anni le coorti 65+ di allora sono già nate — la struttura per età è inerziale su questo orizzonte. Coerente con docs/17 §5 e con tutta la catena: **a medio periodo il LTC italiano è un problema di prevalenza e caregiving, non di nascite**. Le nascite contano (λ₁, t½, platea attuariale cap. 4) ma sui tempi della platea LTC 2056.
2. **La prevalenza è sopra-lineare** (el. 2,12 > 1): +20% di prevalenza aumenta i claimants del 20% ma *anche* riduce il rapporto caregiver/claimant, spingendo una quota ulteriore di domanda verso il formale. La calibrazione della prevalenza sulle fonti ufficiali (ANIA-Sapienza multistato) è quindi **il primo investimento di ricerca del repo**.
3. **r₀ el. 1,26**: quanto prima cede la rete informale (calibrazione dichiarata ±18% ≈ ±2), tanto più rapido il passaggio al formale — il capitolo 3 (caregiver gap) guadagna qui la sua valutazione in termini di costo.
4. La quota domiciliare ha segno negativo (−0,81): ogni punto in più di domanda servita a domicilio (costo 15k) al posto della residenza (48k) risparmia — l' investimento in assistenza domiciliare integrata è la leva di spesa più liquida del sistema.

## 3. Limiti

- OAT è una fotografia locale: le interazioni tra parametri sono nel Monte Carlo del cap. 5 (che campiona congiuntamente), non qui.
- L'elasticità della prevalenza è calcolata a moltiplicatore uniforme per fascia: una calibrazione differenziale (più sugli 85+) avrebbe elasticità ancora maggiore.
- Il miglioramento della mortalità è applicato uniformemente per età; quello selettivo (gain concentrato 80+) amplifica l'effetto, fino a ~+2,5%.
