# Popolazione Italiana — Struttura e Deriva

Analisi della struttura per età e della deriva demografica della popolazione residente in Italia, a partire dai dati ufficiali ISTAT, con proiezioni tramite matrice di Leslie e stima del tempo di dimezzamento. Base per stime attuariali LTC e modelli econometrici collegati.

## Quadro attuale (fonte: ISTAT, Indicatori demografici 2025)

| Indicatore | Valore |
|---|---|
| TFR 2025 | **1,14** (da 1,18 nel 2024) |
| Nascite 2025 | 355.772 (-3,9% sul 2024) |
| Decessi 2025 | ~652.000 → saldo naturale ≈ **-296.000/anno** |
| Età media al parto | 32,7 anni |
| Femmine 15–49 anni | 11,4 milioni (da 14,3 milioni nel 1995) |

## Risultato chiave del modello asintotico (Lotka)

Con TFR = 1,14, T = 32,7 anni, quota femminile alla nascita 0,488, sopravvivenza alla generazione media ~0,99:

```
R₀ ≈ 1,14 × 0,488 × 0,99 ≈ 0,551
r  ≈ ln(0,551)/32,7 ≈ -1,82% all'anno
t½ ≈ 38 anni per generazione
```

Ogni generazione di madri viene sostituita al ~55%: la popolazione femminile in regime stabile si dimezza ogni ~38 anni. Vedi [docs/02_dimezzamento.md](docs/02_dimezzamento.md).

⚠️ **Nota critica sul perimetro**: si tratta dello scenario "zero migrazione" (il break-even strutturale), non della previsione centrale ISTAT — che con i flussi migratori attuali non prevede un dimezzamento entro il 2080. Vedi il documento per il ruolo di momentum e migrazioni.

## Struttura del repository

```
.
├── data/
│   ├── raw/        # CSV originali da demo.istat.it (non versionati)
│   └── processed/  # Vettori pronti all'uso (n0_female, survival_probs)
├── src/
│   ├── parse_istat.py    # Parser CSV ISTAT Demo → vettori Leslie
│   ├── leslie.py         # Costruzione matrice + simulazione traiettoria
│   └── halving.py        # Modello asintotico di Lotka (t½ analitico)
├── notebooks/
├── docs/                 # Capitoli di analisi
└── README.md
```

## Roadmap

- [ ] **Fase 1 — Dato e struttura**: parser ISTAT (popolazione per età × sesso, tavole di mortalità, fecondità per età della madre)
- [ ] **Fase 2 — Deriva**: modello asintotico di Lotka + matrice di Leslie sul pyramid reale; sensitivity t½ su TFR ∈ [0,85; 1,30] e T
- [ ] **Fase 3 — Driver causali**: panel provinciale (ISTAT/OMI/INPS), XGBoost + TreeSHAP per screening, Double Machine Learning per ATE su TFR
- [ ] **Fase 4 — LTC / prospettive attuariali**: rapporto caregiver/anziani come driver del costo LTC; impatto della coorte 1960–1975 sulle richieste LTC 2040–2055
- [ ] **Fase 5 — Econometria collegata**: proiezioni popolazione attiva, pressione previdenziale, housing

## Fonti dati

- [demo.istat.it](https://demo.istat.it) — Popolazione residente per età/sesso, tavole di mortalità, fecondità per età della madre
- [ISTAT, Indicatori demografici](https://www.istat.it/it/dati/indicatori-demografici) — comunicati annuali
- [ISTAT, Natalità e fecondità](https://www.istat.it/it/dati/natalita-e-fecondita) — Tfr e nascite
- OMI (Agenzia delle Entrate), INPS, dati provinciali vari — per Fase 3

## Requisiti

Python 3.10+. Nessuna dipendenza aggiuntiva per Fase 1–2 (numpy, pandas, scipy).

## Contenuto

La documentazione dettagliata si trova in [docs/](docs/):
- [01_dati.md](docs/01_dati.md) — fonti dati e formati
- [02_dimezzamento.md](docs/02_dimezzamento.md) — tempo di dimezzamento: modello di Lotka e matrice di Leslie
- [03_roadmap_ltc.md](docs/03_roadmap_ltc.md) — verso le stime attuariali LTC

## Licenza

Distribuito con [Licenza MIT](LICENSE).
