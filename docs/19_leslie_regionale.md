# Leslie regionale — ripartizioni e spotlight Sardegna

> Implementazione: `src/leslie_regionale.py`, esecuzione: `python3 src/leslie_regionale.py` (`--valida` per il check del mapping). Realizza il coupling su base geografica dichiarato in docs/06 §5 e apre la strada al MAPE coorte 0-11 regionale.

## 1. Costruzione e validazione

- **Vettori**: POSAS 2026 per ripartizione (csv ufficiale) e per gruppo di province (Sardegna = 090, 091, 092, 095, 111)
- **Mortalità**: tavole provinciali complete 2024 aggregate con media pesata per popolazione provinciale, ristretta alle province del gruppo (stessa logica della media nazionale)
- **Fecondità**: ASFR nazionale — limitazione dichiarata (le ASFR per ripartizione non sono nel formato del parser); il livello regionale entra come `tfr_scale` (scenario Sardegna TFR 0,85 del 2025 = scala 0,72)
- **Migrazione**: saldo nazionale (+280k/anno) ripartito in proporzione alla popolazione dell'area
- **Mapping validato automaticamente**: le 107 province sono assegnate una sola volta e le somme per ripartizione riprendono i totali del CSV Ripartizioni con **delta 0,0%**

## 2. Risultati per ripartizione (TFR nazionale, 2026-2081)

| Ripartizione | Pop 2026 | λ₁ | r | t½ asint. | Pop 2056 | Pop 2081 | Claimants 2056 | Over-80 2056 |
|---|---|---|---|---|---|---|---|---|
| Nord-ovest | 15,96 M | 0,9835 | −1,67% | 41,6 | 14,25 M | 11,66 M | 462k | 2,08 M |
| Nord-est | 11,62 M | 0,9835 | −1,67% | 41,5 | 10,45 M | 8,56 M | 345k | 1,56 M |
| Centro | 11,70 M | 0,9835 | −1,67% | 41,6 | 10,33 M | 8,36 M | 341k | 1,54 M |
| Sud | 13,34 M | 0,9834 | −1,67% | 41,5 | 12,03 M | 9,92 M | 353k | 1,52 M |
| Isole | 6,33 M | 0,9834 | −1,67% | 41,5 | 5,59 M | 4,59 M | 169k | 0,74 M |

Somma claimants 2056 = **1,68 M**: coincide col nazionale del capitolo 5 (1,69 M media MC) — la scomposizione è coerente.

**Lettura principale**: le cinque ripartizioni sono nello **stesso regime asintotico** (λ₁ = 0,9834-0,9835, t½ 41,5-41,6): le differenze di mortalità tra nord e sud esistono ma la media prospettica pesata le appiattisce, e la struttura per età conta più della geografia sulla dinamica. **L'Italia del dimezzamento non ha macro-regioni divergenti: divergono i livelli (momentum), non i regimi.** Le differenze rilevanti emergono sotto la soglia: è lì che la dinamica cambia qualità.

## 3. Spotlight Sardegna: dentro la soglia di non ritorno

La Sardegna è la regione-che-test del modello PSTR (docs/13: TFR 0,85 nel 2025, sotto la soglia instabile stimata ~0,91):

| Scenario | λ₁ | r | t½ asintotico | Pop 2056 | Pop 2081 |
|---|---|---|---|---|---|
| **TFR 0,85** (osservato 2025) | **0,9739** | **−2,64%** | **26,2 anni** | 1,22 M | **0,87 M** |
| TFR nazionale (1,18) | 0,9834 | −1,67% | 41,5 | 1,28 M | 1,00 M |

**Letture**:

1. **Il t½ asintotico sardo è 26 anni, non 41**: mantenendo il TFR osservato, la popolazione sarda si dimezza ogni generazione umana a cavallo (0,87 M al 2081 da 1,55 M — −44%). È la prima quantificazione su modello della distanza fra "declino nazionale" e "declino da regime basso": il paese perde il 26% in 55 anni, l'isola perde il 44%.
2. **La struttura dà riscatto parziale**: la popolazione sarda ha un profilo vecchio ma il momento di fertilità non è amplificato nemmeno da questo — a 55 anni il rapporto 2081/2026 (0,56) è vicino alla soglia del dimezzamento ma non la raggiunge: il primo dimezzamento sardo avverrebbe poco dopo il 2081, quasi il doppio del tempo asintotico.
3. **Connessione ai claimants LTC**: 46k claimants al 2056 in uno scenario di popolazione −29% prima del 2056: la base fragilità sarda cresce in quota anche quando cala in livello — la struttura del piano assistenziale (presidi, reti informali) va dimensionata su dinamiche diverse dal resto d'Italia.

## 4. Verso il coupling pieno (docs/06 §3.A)

Con questo PR l'infrastruttura regionale esiste: il passo finale del protocollo è il MAPE sulla coorte 0-11 al 2024 (validazione della Leslie regionale contro i bilanci ISTAT osservati 2013-2024), che richiede le strutture per età regionali storiche 2012-2024 (ISTAT Ricostruzione), non ancora nel repo — dichiarato come prossimo passo.

## 5. Limiti

- ASFR unica nazionale per tutte le aree: il profilo per età della fecondità sarda (più tarda) non è distinto dal nazionale; solo il livello entra via scala.
- Le tavole provinciali 2024 sono usate statiche per tutto l'orizzonte (stessa scelta del modello nazionale).
- Migrazione: il saldo proporzionale alla popolazione è una prima approssimazione — il profilo reale è clustered verso nord (dichiarato; il modello Rogers-Casto regionale è il prossimo upgrade).
