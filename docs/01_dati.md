# Fonti dati ISTAT

Tutti i dati grezzi vanno scaricati manualmente da [demo.istat.it](https://demo.istat.it) e salvati in `data/raw/` (non versionati per dimensione/licenza di rediffusione).

## File necessari per Fase 1–2

| File | Percorso su demo.istat.it | Uso | Output |
|---|---|---|---|
| Popolazione residente al 1° gennaio, per età e sesso | Popolazione e famiglie → Popolazione residente | `n0_female`, `n0_male` | `data/processed/n0_female.npy` |
| Tavole di mortalità della popolazione residente (Femmine/Maschi) | Mortalità → Tavole di mortalità | `survival_probs` (P_x = L_{x+1}/L_x) | `data/processed/survival_probs.npy` |
| Tasso di fecondità per età della madre | Natalità e fecondità → Fecondità per età | `fertility_rates` (consigliato), usare i tassi reali per fascia invece di un profilo gaussiano sintetico | `data/processed/fertility_rates.npy` |

## Note sui formati CSV ISTAT

- Intestazioni descrittive su più righe prima della tabella vera
- Separatore `;` o `,` a seconda dell'export
- Decimali con virgola, migliaia con punto
- Classe aperta finale: `100 e più`
- Righe `Totale` da filtrare

Il parser in `src/parse_istat.py` gestisce automaticamente questi casi, con fallback su `qx` se la colonna `Lx` non fosse presente.

## Comunicati di riferimento per il quadro iniziale

- Indicatori demografici anno 2025 — https://www.istat.it/comunicato-stampa/indicatori-demografici-anno-2025/
- Natalità e fecondità anno 2025 — https://www.istat.it/comunicato-stampa/natalita-e-fecondita-della-popolazione-residente-anno-2025/
