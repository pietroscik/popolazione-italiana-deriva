# Audit finale di consolidamento (v1.1.0) — quattro livelli

> Audit del ciclo bug → test → rerun → baseline → robustezza → data-vintage → docs. Ogni affermazione rimanda a un test o a un report eseguito.

## Livello 1 — Matematico

| Identità | Verifica | Esito |
|---|---|---|
| r Lotka (equazione caratteristica, convenzione x+1) = ln λ₁ (matrice) | `test_r_lotka_esatto_uguale_ln_lambda1`, tolleranza 1e-6 | **0,0 alla sesta cifra** |
| R₀ = Σₓ ASFRₓ·s_f·lₓ; T = Σₓ x·mₓ·lₓ/R₀ | `test_r0_corrisponde_a_tfr_per_s_f` ( sintetico), `net_reproduction` (dati reali) | R₀ = 0,5733 (A) / 0,5538 (B) |
| Bilancio demografico chiuso: pop(t+1) = nascite + sopravvissuti + ritenuti 100+ | `test_proiezione_chiusa_conserva_la_popolazione` | ✅ esatto a macchina |
| Costi blended severità = costi unitari cap. 2 | `test_blended_riprega_i_costi_del_capitolo_2` | 14,85k/47,5k ≈ 15k/48k |
| DM/CW/CRPS: statistiche su casi con esito noto | `tests/test_backtest.py` | ✅ |

## Livello 2 — Computazionale

Due bug strutturali trovati e corretti nel ciclo (entrambi con test che dimostra l'effetto atteso):

1. **Classe terminale 100+ trattata come chiusa**: la TVM dice P[100]≈0,64 ma la pipeline forzava 0 — tutti i 100+ uscivano in un anno. Corretto in `parse_istat` (P[100] reale), `leslie.survive` + matrice + `leslie_regionale` (classe aperta ritiene n[100]·P[100]). Test: `test_classe_terminale_aperta_ritiene_i_sopravviventi`, `test_matrice_leslie_con_diagonale_terminale`.
2. **Moltiplicatori di sesso campionati e mai usati nel Monte Carlo LTC**: la banda di incertezza risultava artificially stretta sulla dimensione sesso. Corretto in `simulate_claimants_m(..., sex_mult_f, sex_mult_m)`; il MC ora li propaga. Test: `test_moltiplicatore_campionato_arranta_i_claimants` (2× donna → claimants F ↑ >20%, M invariati).

Copertura: **82 test automatici**, CI end-to-end (download ISTAT + parse + test a ogni push).

## Livello 3 — Statistico/econometrico

- **Batteria di stabilità della soglia (eseguita, docs/13 §5-bis)**: θ̂ ∈ [1,66; 1,72] su tutte le specificazioni (CRE/Mundlak 1,72, kinked 1,72, finestra 2013-24: 1,70; IV sotto-campione: 1,94); **γ̂ > 0 in ogni specificazione**; Mundlak assorbe l'eterogeneità regionale correlata (media-F +0,236, γ sale a +0,48) senza spostare θ̂
- **Test kinked eseguito**: DR₀ al pavimento → l'effetto DR è di livello, non il freno fiscale a soglia (lettura pre-registrata)
- **IV con validità condizionata dichiarata** (F=340 ma lo strumento proxya il regime storico sotto norme persistenti — la premessa della trappola); LOCO = paese, non sub-nazionale
- **Backtest DM/CW negativo dichiarato** (h=1 vince il random walk; CW t=−3,80): il valore della PSTR è strutturale, non previsivo
- **Soglia 0,91**: qualificata come *evidenza compatibile, era-specifica, supporto bootstrap 66%* — mai "costante strutturale consolidata"
- Nessun claim causale su γ̂; stabilità tra ere RIGETTATA (docs/15) e dichiarata

## Livello 4 — Riproducibilità

- **Data-vintage manifest** (`data/metadata/manifest.json`): 10 fonti con URL, dataset, vintage, data estrazione, **SHA-256**, script di acquisizione/parsing, versione codice (1.1.0 da CITATION.cff)
- Pipeline a un comando per layer (download → parse → modelli), CI che la riesegue end-to-end
- Coerenza temporale degli input dichiarata (2026 pop / 2024 mortalità-ASFR, scenario A/B) e tabella epistemica osservato/stimato/assunto/simulato/controfattuale nel README
- Numeri documentati sopra = numeri dell'ultima esecuzione (rerun post-fix: C₂₀₅₆ 32,3 [20,6; 44,2], PV 1.084, premio 253/1.409, break-even 616k, rapporto −46%)

## Esito

Tutti e quattro i livelli passano, con le due eccezioni dichiarate come **limiti aperti** (non blocker): il layer causale (DML/mediazione) è specificato ma non eseguito; la soglia 0,91 è era-specifica. La v1.1.0 è **prima release metodologicamente consolidata**: una release scientifica "definitiva" richiederebbe il backtest within-era e il secondo strumento (t-20) per Hansen J — roadmap v1.2.
