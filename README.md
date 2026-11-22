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
│   ├── parse_istat.py    # Parser CSV ISTAT Demo → vettori nazionali (due sessi)
│   ├── leslie.py         # Leslie, due sessi, scenari, migrazioni
│   ├── migration.py      # Profilo migratorio Rogers-Castro + calibrazione saldo
│   ├── ltc.py            # Capitolo LTC 1: claimants, caregiver, rapporti
│   ├── ltc_costi.py      # Capitolo LTC 2: costo aggregato (informale/domiciliare/residenziale)
│   └── halving.py        # Modello asintotico di Lotka (t½ analitico)
├── notebooks/
├── docs/                 # Capitoli di analisi
└── README.md
```

## Roadmap

- [x] **Fase 1 — Dato e struttura**: download automatico e parser di POSAS 2026 (popolazione per età, sesso, provincia), TVM 2024 (tavole di mortalità provinciali), ASFR 2024 (fecondità per età) — `src/download_istat.py` + `src/parse_istat.py`
- [x] **Fase 2 — Deriva**: matrice di Leslie sulla piramide reale + sensibilità t½ per TFR 0,95–1,30 — `src/leslie.py` ([risultati](docs/02_dimezzamento.md#5-risultati-dellimplementazione-dati-reali-istat-fase-2-completata))
- [x] **Blocco dinamico completo**: modello a due sessi + migrazione per età Rogers-Castro, scenari di saldo migratorio e **saldo di break-even (~+600k/anno)** — [07_leslie_rogers_migrazioni.md](docs/07_leslie_rogers_migrazioni.md)
- [ ] **Fase 3 — Driver causali**: panel provinciale (ISTAT/OMI/INPS), XGBoost + TreeSHAP per screening, Double Machine Learning per ATE su TFR (design: [04_architettura_due_strati.md](docs/04_architettura_due_strati.md))
- [x] **Fase 4 — LTC, capitolo 1**: proiezione claimants e caregiver potenziali (2026–2081), rapporto caregiver/claimant (-43%): [08_ltc_capitolo1.md](docs/08_ltc_capitolo1.md)
- [x] **Fase 4 — LTC, capitolo 2**: modello di copertura a tre livelli e costo aggregato — picco **31 mld € (1,4% PIL) al 2056**, x6 sul 2026: [09_ltc_capitolo2_costi.md](docs/09_ltc_capitolo2_costi.md). Estensione non lineare (Low Fertility Trap, TFR endogeno con isteresi): [05_low_fertility_trap.md](docs/05_low_fertility_trap.md)
- [ ] **Fase 5 — Econometria collegata**: proiezioni popolazione attiva, pressione previdenziale, housing

## Fonti dati

- [demo.istat.it](https://demo.istat.it) — Popolazione residente per età/sesso, tavole di mortalità, fecondità per età della madre
- [ISTAT, Indicatori demografici](https://www.istat.it/it/dati/indicatori-demografici) — comunicati annuali
- [ISTAT, Natalità e fecondità](https://www.istat.it/it/dati/natalita-e-fecondita) — Tfr e nascite
- OMI (Agenzia delle Entrate), INPS, dati provinciali vari — per Fase 3

## Requisiti

Python 3.10+; dipendenze: `numpy`, `pandas` (`pip install -r requirements.txt`).

Per riprodurre l'analisi:

```bash
python3 src/download_istat.py     # scarica i dati ISTAT in data/raw/
python3 src/parse_istat.py       # genera i vettori in data/processed/
python3 src/leslie.py --scenari  # report + tabella scenari TFR
python3 src/leslie.py --migrazioni  # scenari saldo migratorio + break-even
python3 src/ltc.py                  # capitolo LTC 1: claimants e caregiver
python3 src/ltc_costi.py            # capitolo LTC 2: costo aggregato formale
python3 -m unittest discover tests
```

## Contenuto

La documentazione dettagliata si trova in [docs/](docs/):
- [01_dati.md](docs/01_dati.md) — fonti dati e formati (download automatico)
- [02_dimezzamento.md](docs/02_dimezzamento.md) — tempo di dimezzamento: modello di Lotka e matrice di Leslie (con risultati su dati reali)
- [03_roadmap_ltc.md](docs/03_roadmap_ltc.md) — verso le stime attuariali LTC
- [04_architettura_due_strati.md](docs/04_architettura_due_strati.md) — architettura target: strato causale offline + simulatore dinamico online
- [05_low_fertility_trap.md](docs/05_low_fertility_trap.md) — formalizzazione della trappola della bassa fecondità: isteresi, biforcazione, identificazione PSTR
- [06_backtest_protocol.md](docs/06_backtest_protocol.md) — protocollo di validazione out-of-sample (benchmark M0/M1/M2, Clark-West/DM, robustezza)
- [07_leslie_rogers_migrazioni.md](docs/07_leslie_rogers_migrazioni.md) — migrazione per età (Rogers-Castro), modello a due sessi, saldo di break-even
- [08_ltc_capitolo1.md](docs/08_ltc_capitolo1.md) — LTC: claimants non autosufficienti, caregiver potenziali, rapporto e finestra 2040–2055
- [09_ltc_capitolo2_costi.md](docs/09_ltc_capitolo2_costi.md) — LTC: costo aggregato, cedimento assistenza informale, picco di spesa 2056

Bozza del working paper in inglese: [paper/draft.md](paper/draft.md) — *Escaping the Low Fertility Trap*.

## Licenza

Distribuito con [Licenza MIT](LICENSE).
