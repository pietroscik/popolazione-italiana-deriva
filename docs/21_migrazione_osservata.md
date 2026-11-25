# Migrazione netta OSSERVATA per età — dal sintetico Rogers-Castro al profilo reale (v1.2)

**Modulo**: `src/migration_observed.py` • **Roadmap v1.2, ramo 4** ("migrazione osservata/strutturale")

## 1. Metodo

Il modello due sessi usa un profilo migratorio **SINTETICO** Rogers-Castro (forma teorica, calibrata solo sul saldo ~+263k/2024). Qui il profilo **netto osservato** per età e sesso è derivato dalla bilancia implicita di due POSAS consecutive:

```
m(a)  = P_{t+1}(a+1) − P_t(a) · S(a)          (a = 1..98)
m(99+) = P_{t+1}(100) − [P_t(99)·S(99) + P_t(100)·S(100)]   (classe aperta: 99 e 100+ inseparabili)
```

- Sopravvivenza S: TVM 2024 (unico vintage applicato a entrambi gli intervalli — **assunzione dichiarata**; errore del tasso di secondo ordine rispetto al residuo)
- **Età 0 esclusa** (richiederebbe le nascite dell'anno t dal bilancio demografico)
- Fonti: POSAS Ripartizioni 2023, 2024, 2025 (demo.istat.it, stesso URL pattern del POSAS 2026)
- Il residuo a 99+ è combinato: con una classe terminale aperta la migrazione a 99 anni non è separabile da quella dei centenari (convenzione "99+"; il primo giro contabilizzava l'intrattenimento dei 100+ due volte — un picco spurio a 99 — corretto con test)

## 2. Risultati sul profilo osservato

| Intervallo | Saldo oss. (1+) | Età media migranti | Quota 20-39 | Quota 20-39 sintetico | Correlazione col sintetico |
|---|---|---|---|---|---|
| 2023→2024 | +224k | 29,2 | 54,5% | 46,4% | 0,60 |
| 2024→2025 | +244k | 29,3 | 51,7% | 46,4% | 0,51 |

Struttura per bande (2024→2025): 1-14 **+36k**, 15-19 **+32k**, 20-29 **+72k**, 30-39 **+54k**, 40-49 **+29k**, 50-64 **+22k**, 65+ ≈ 0.

**Lettura 1 — il profilo reale è "family-shaped", non "labor-shaped"**: (~+40k bambini/anno, picco secondario 17-19, metà dell'incasso nelle età 20-39, anziani ≈ 0). Il Rogers-Castro sintetico concentra quasi tutto sul picco di forza lavoro (25-39) e trascura i minori al seguito.

**Lettura 2 — il sintetico sottostima i minori**: quota 20-39 osservata 52-55% vs 46% del sintetico; i bambini migrati (1-14) NON figurano nel profilo teorico.

## 3. Scenario: profilo osservato vs sintetico (saldo +263k/anno, 2026-2081)

| Quantità | Sintetico (headline) | Osservato (2024→2025) | Delta |
|---|---|---|---|
| Popolazione 2081 | 42,30 M | **45,77 M** | **+8,2%** |
| **Break-even migratorio** | **616.104** | **~481.000** | **−22%** |

**Lettura 3 — il break-even cala di un quinto con il profilo reale**: i bambini migrati entrano nelle coorti feconde e generano nascite nella generazione successiva; il profilo labor-only del sintetico, a parità di saldo, produce una popolazione finale inferiore dell'8%. Il break-even ufficiale del repo (616k, profilo dinamico sintetico) resta il numero headline dichiarato; il 481k è lo scenario "profilo osservato" — insieme dicono che **la stima 616k è conservativa rispetto al valore demografico della migrazione in corso**.

## 4. Limiti dichiarati

- Un solo intervallo annuo ciascuno (2023→24, 2024→25): il profilo è statico e non cattura la stagione migratoria; la stabilità tra i due intervalli (saldo +224/+244k, età media 29,2/29,3) suggerisce comunque robustezza di forma
- TVM 2024 su entrambi gli intervalli (vintage unico): i residui ad alta età (86-99) sono sensibili alla precisione della sopravvivenza e vanno letti con cautela
- POSAS = stime post-censuali soggette a revisione
- Il residuo netto osservato include effetto di native-born leaving Italy per fascia (già saldo, non separabile per nazionalità con questi soli dati)
- Il break-even con profilo osservato eredita il limite di entrambi i metodi: staticità del profilo nel tempo

## 5. Tests

`tests/test_migration_twosex.py::TestMigrazioneOsservata`:
- `test_nessuna_migrazione_residuo_zero`: nessun flusso ⇒ residuo ≡ 0 su ogni età, 99+ compreso (ha scovato il double-counting del primo giro)
- `test_su_dati_reali_saldo_positivo_eta_plausibile`: saldo >100k, età media 25-40
- `test_scenario_osservato_piu_generativo`: pop osservata > sintetica, break-even osservato < sintetico
