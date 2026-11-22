# Escaping the Low Fertility Trap: A Coupled Spatial-Causal and Non-Linear Leslie-Rogers Framework for European Demographic Dynamics

> Working paper draft — bozza in inglese derivata dal contributo dell'utente. Placeholder strutturati per i risultati numerici da compilare con gli output del repository.

## Abstract

Standard cohort-component projections, such as the classical Lotka and Leslie-Rogers models, treat the Total Fertility Rate (TFR) as an exogenous, time-invariant parameter. While analytically convenient, this assumption systematically underestimates demographic contraction risks in ultra-low fertility regimes — such as Italy (TFR ≈ 1.15) — where reinforcing sociological norms, fiscal crowding-out from rising old-age dependency ratios, and selective youth out-migration can lock populations into a self-reinforcing Low Fertility Trap. Concurrently, empirical studies relying on purely predictive machine learning or standard panel regressions often conflate socioeconomic proxies and causal mediators with actionable policy levers.

This paper introduces a coupled, two-layer quantitative framework bridging spatial causal inference and non-linear demographic dynamics. In the offline econometric layer, we decompose period fertility into tempo and quantum components (Bongaarts-Feeney) across European NUTS-2 regions (Eurostat, 1995–2024) and Italian NUTS-3 provinces (ISTAT/OMI/INPS). We combine Spatial-SLX Double Machine Learning with causal mediation analysis to isolate the direct and indirect effects of housing affordability, childcare coverage, and female labor stability, while correcting for spatial spillovers (SUTVA violations). We then estimate a Dynamic Panel Smooth Transition Regression (PSTR) to empirically identify the hysteresis threshold (θ), transition speed (k), and aging drag (γ). In the online dynamic layer, these structural parameters endogenize fertility within a non-linear Leslie-Rogers matrix featuring age-specific migration profiles.

Out-of-sample multi-step backtesting (2013–2024) assesses whether the non-linear PSTR-Leslie architecture outperforms static and linear benchmarks under Clark-West and Diebold-Mariano tests — particularly in transition-zone regions — and quantifies the asymmetric policy shock (u_exit ≫ u_prevention) required to escape the lower attractor.

**Keywords**: Low Fertility Trap; PSTR; Double Machine Learning; Leslie-Rogers Matrix; Hysteresis; Spatial Econometrics; Eurostat NUTS-2.

**JEL**: J11, J13, C23, C31, C53.

## 1. Introduction & Motivation

1.1 The limits of exogenous demographic projections. Across much of Southern and Eastern Europe, period fertility has fallen well below replacement (2.1), settling into persistent ultra-low regimes. Under a stationary closed-population Lotka model with TFR = 1.15 and mean age at childbearing of 32.5, a population halves asymptotically every ~38 years; on Italy's actual pyramid via a standard Leslie matrix, momentum delays the first halving to roughly 48–55 years, after which the trajectory converges to the intrinsic rate. Despite their widespread use, classical projections suffer from a foundational structural limitation: fertility is exogenous. Per the Low Fertility Trap hypothesis (Lutz, Skirbekk & Testa, 2006), ultra-low fertility triggers three coupled feedback loops: (i) demographic — shrinking female cohorts mechanically reduce future births; (ii) sociological — declining ideal family sizes shift norms downward; (iii) economic — rising old-age dependency ratios strain public finances and crowd out transfers to younger cohorts. With age-selective out-migration (20–39), the system exhibits bistability and hysteresis; ignoring this non-linearity misprices long-term fiscal sustainability, underestimates regional depopulation speed, and overestimates the efficacy of incremental family policies past the tipping point.

1.2 Correlation vs. causation in fertility drivers. Tree-based ML with explainability (XGBoost + TreeSHAP) uncovers non-linearities and thresholds in territorial panels, but standard Shapley values measure predictive association, not causal impact. Without explicit identification, algorithms assign high importance to proxies (GDP, education) or condition on causal mediators — notably the mean age at childbearing — inducing overcontrol bias that masks upstream causes (labor precarity, housing affordability). Territorial panels also inherently violate SUTVA: labor markets, commuting basins and housing pressures spill over administrative borders.

1.3 Contributions. (1) Spatial-causal identification of policy levers: exploratory screening decoupled from estimation via Spatial-SLX DML with spatial block cross-fitting and Moran's I residual diagnostics, plus mediation analysis separating NDE (quantum) from NIE (tempo). (2) Empirical identification of hysteresis: the trap is calibrated as a Dynamic PSTR on a multi-decade NUTS-2 panel, with lagged cohort structures instrumenting the mechanical endogeneity of the dependency ratio — yielding testable bistability conditions. (3) A reproducible open framework: the full pipeline (data provenance to counterfactual simulation) is versioned in this repository, with the classical Lotka/Leslie baseline already implemented and validated on ISTAT data.

## 2. Theoretical Framework: the two-layer architecture

[Da sviluppare — vedi docs/04_architettura_due_strati.md per la sintesi e docs/05_low_fertility_trap.md per: sistema dinamico accoppiato (n_t, F_t); funzione di feedback Φ(F_t, DR_t, u_t); condizione di stabilità locale Φ'(F*) < 1; condizione di bistabilità k(F_max−F_min)/4 > 1; biforcazione saddle-node; isteresi (collasso asimmetrico, asimmetria di policy).]

*Fig. 1 — Diagramma dell'architettura a due strati (offline econometrico → online dinamico) + DAG causale.*
*Fig. 2 — Diagramma di fase Φ(F_t) vs bisettrice: equilibri (F*_L, F*_U, F*_H) e biforcazione saddle-node.*

## 3. Data, Provenance & Pre-processing

[Da compilare — mappatura esatta delle tabelle: Eurostat (TFR NUTS-2: demo_gind / tfr per regione; struttura per età; PIL/covariate regionali: nama_10r_2gdp, etc.) e ISTAT/OMI/INPS provinciali (POSAS, TVM, ASFR — già automatizzati in `src/download_istat.py`; OMI canoni, INPS occupazione: da integrare in Fase 2). Statistiche descrittive con tag di provenienza (Tab. 1).]

## 4. Econometric Identification Strategy

Spatial-SLX DML (CausalForestDML) con spatial block cross-fitting; causal mediation (NDE/NIE); Dynamic PSTR con strumenti ritardati per DR_{i,t}. Condizioni di identificazione: la soglia θ richiede il panel europeo (osservazioni su entrambi i regimi); sulla sola Italia θ è debolmente identificato.

## 5. Empirical Results & Out-of-Sample Backtest 2013–2024

[Placeholder — protocollo completo in docs/06_backtest_protocol.md. Risultati attesi: Tab. 3 stime PSTR (α̂, θ̂, k̂, γ̂) + test LM di non-linearità + verifica bistabilità; Tab. 4 backtest: RMSE, MAPE coorte 0–11, CRPS, coverage 95%, DM e Clark-West globali e stratificati nei 3 regimi (trappola / transizione / alta fecondità).]

## 6. Robustness

[Quattro batterie con criteri pass/fail — vedi docs/06_backtest_protocol.md §4: pre-COVID truncation, placebo (randomization inference, threshold displacement, LSTR vs ESTR vs spline), perturbazione W_spat + LOCO (esclusione IT/FR/DE/ES), TFR vs TFR* (Bongaarts-Feeney) + diagnostica strumenti (Kleibergen-Paap, Hansen J).]

## 7. Counterfactual Policy Simulations & Conclusions

7.1 Caso di studio Italia (TFR = 1,15/1,18): proiezione a 100 anni con bande IC 95% (1.000 repliche bootstrap/bayesiane), scenario inerziale vs pacchetti di policy combinati (asili nido + stabilità lavorativa + costo abitativo) e saldo migratorio selettivo 20–39.
7.2 Implicazioni di policy: shock minimo u_uscita e probabilità stimata di uscita dalla trappola; costo del ritardo (effetto γ ΔDR_t accumulato).
7.3 Limiti e sviluppi futuri: modelli multi-regionali accoppiati (migrazioni interprovinciali endogene); integrazione dinamiche pensionistiche/fiscali; estensione LTC (roadmap in docs/03_roadmap_ltc.md).

## Appendici

- **A** — Derivazioni matematiche: stabilità locale (Φ'(F*) < 1), forma chiusa del punto di biforcazione F_c, raccordo λ₁ (Perron-Frobenius) ↔ tasso intrinseco di Lotka
- **B** — Specifiche di ottimizzazione PSTR e GMM: griglia Profiled NLS su (k, θ), strumenti ritardati, Kleibergen-Paap, Hansen J, Cluster Block Bootstrap / prior bayesiani
- **C** — Costruzione della curva migratoria (Rogers-Castro) e gestione della classe aperta 100+ nella Leslie
- **D** — Data provenance & repository integrity: codici tabella esatti, date di estrazione, schema Parquet, replica end-to-end
