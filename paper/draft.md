# Escaping the Low Fertility Trap: A Coupled Spatial-Causal and Non-Linear Leslie-Rogers Framework for European Demographic Dynamics

> Working paper draft v0.2 — aggiornato con i risultati empirici del repository (Fase 1-3, PSTR). Le sezioni 6-7 restano in parte strutturali fino al backtest completo.

## Abstract

Standard cohort-component projections, such as the classical Lotka and Leslie-Rogers models, treat the Total Fertility Rate (TFR) as an exogenous, time-invariant parameter. While analytically convenient, this assumption systematically underestimates demographic contraction risks in ultra-low fertility regimes — such as Italy (TFR 1.18 in 2024, 1.14 in 2025) — where reinforcing sociological norms, fiscal crowding-out from rising old-age dependency ratios, and selective youth out-migration can lock populations into a self-reinforcing Low Fertility Trap. Concurrently, empirical studies relying on purely predictive machine learning or standard panel regressions often conflate socioeconomic proxies and causal mediators with actionable policy levers.

This paper introduces a coupled, two-layer quantitative framework bridging spatial causal inference and non-linear demographic dynamics. In the offline econometric layer, we decompose period fertility into tempo and quantum components (Bongaarts-Feeney) across European NUTS-2 regions (Eurostat, 2013–2023) and Italian NUTS-3 provinces (ISTAT/OMI/INPS). We combine Spatial-SLX Double Machine Learning with causal mediation analysis to isolate the direct and indirect effects of housing affordability, childcare coverage, and female labor stability, while correcting for spatial spillovers (SUTVA violations). We estimate a Dynamic Panel Smooth Transition Regression (PSTR) with a regional old-age dependency control to empirically identify the hysteresis threshold (θ), transition speed (k), and aging drag (γ). In the online dynamic layer, these structural parameters endogenize fertility within a two-sex Leslie-Rogers matrix featuring age-specific (Rogers-Castro) migration profiles, validated against ISTAT data (implied TFR 1.18; population 58.94M).

First empirical results on 282 NUT-2 regions (2,366 region-year observations after gap filtering) identify a logistic transition threshold θ̂ = 1.66 and an implied dynamic map with an unstable no-return threshold at F ≈ 0.91 and a high stable attractor at F ≈ 1.61: regions below the threshold exhibit self-reinforcing decline (Sardinia, TFR 0.85, is below it), while Italy as a whole (1.14–1.18) remains marginally above. Out-of-sample multi-step backtesting (2013–2024) will assess whether the non-linear PSTR-Leslie architecture outperforms static and linear benchmarks under Clark-West and Diebold-Mariano tests, and quantify the asymmetric policy shock (u_exit ≫ u_prevention) required to escape the lower attractor.

**Keywords**: Low Fertility Trap; PSTR; Double Machine Learning; Leslie-Rogers Matrix; Hysteresis; Spatial Econometrics; Eurostat NUTS-2.

**JEL**: J11, J13, C23, C31, C53.

## 1. Introduction & Motivation

### 1.1 The limits of exogenous demographic projections

Across much of Southern and Eastern Europe, period fertility has fallen well below replacement (2.1), settling into persistent ultra-low regimes. Under a stationary closed-population Lotka model with TFR = 1.18 and mean age at childbearing of 32.7, a population halves asymptotically every ~40 years; on Italy's actual two-sex pyramid via the Leslie-Rogers model developed here, population momentum delays the first halving to ~55 years, after which the trajectory converges to the intrinsic rate (λ₁ = 0.983).

Classical projections suffer from a foundational structural limitation: fertility is exogenous. Per the Low Fertility Trap hypothesis (Lutz, Skirbekk & Testa, 2006), ultra-low fertility triggers three coupled feedback loops: (i) demographic — shrinking female cohorts mechanically reduce future births; (ii) sociological — declining ideal family sizes shift norms downward; (iii) economic — rising old-age dependency ratios strain public finances and crowd out transfers to younger cohorts. With age-selective migration (20–39), the system exhibits bistability and hysteresis; ignoring this non-linearity misprices long-term fiscal sustainability, underestimates regional depopulation speed, and overestimates the efficacy of incremental family policies past the tipping point.

### 1.2 Correlation vs. causation in fertility drivers

Tree-based ML with explainability (XGBoost + TreeSHAP) uncovers non-linearities and thresholds in territorial panels, but standard Shapley values measure predictive association, not causal impact. Our own screening on the European panel (Section 5) shows why this distinction is not academic: the GDP-fertility correlation is 2.5× weaker within regions than between them — most of the apparent "rich regions have more children" signal is fixed territorial structure (family policy regimes), not a movable lever.

Territorial panels also inherently violate SUTVA: labor markets, commuting basins and housing pressures spill over administrative borders. Panel diagnostics (Moran's I on DML residuals; KNN/idw weights for islands) are therefore integral to the design (Section 4).

### 1.3 Contributions

1. **A validated two-sex Leslie-Rogers dynamic layer** on real ISTAT data: automated ISTAT ingestion (POSAS 2026, TVM 2024, ASFR 2024), two-sex projection, Rogers-Castro age-specific migration calibrated on observed net balances (+263k in 2024), and a break-even estimate of ~600k net migrants/year needed for population stability at current fertility.
2. **Spatial-causal identification of policy levers**: screening (XGBoost + native TreeSHAP) decoupled from causal estimation via Spatial-SLX DML with spatial block cross-fitting and Moran's I residual diagnostics, plus mediation analysis separating NDE (quantum) from NIE (tempo). The European NUTS-2 panel (285 regions, TFR + GDP pc PPS + regional DR) is assembled and versioned.
3. **Empirical identification of hysteresis**: the trap is estimated — not assumed — as a Dynamic PSTR on the multi-year NUTS-2 panel, yielding θ̂ = 1.66, an unstable no-return threshold at F ≈ 0.91, a high attractor at F ≈ 1.61, and a positive — theory-contradicting — γ_DR = +0.077 that survives lagged-instrument estimation (t−15 cohort structure, first-stage F = 340, γ̂_IV = +0.129) and leave-one-country-out robustness (positive in all 33 exclusions): the sign is structural, not endogeneity or Nordic-welfare confounding.
4. **A fully reproducible open framework**: every result in this paper is regenerated from raw providers by a single command per layer (`src/download_istat.py`, `src/download_eurostat.py`, `src/pstr_trap.py`...), with 36 unit tests and CI.

## 2. Theoretical Framework: the two-layer architecture

### 2.1 The offline econometric layer

**Tempo/Quantum decomposition.** The period TFR conflates postponed births (tempo) with foregone childbearing (quantum). Level effects in the PSTR are estimated on period TFR; robustness requires re-estimation on Bongaarts-Feeney adjusted TFR* (Appendix A). Position in the transition is instrumented by the mean age at childbearing (available from `demo_r_find2`, indic_de=AGEMOTH/MEDAGEMOTH).

**Causal layer.** The DAG separates confounders W (GDP per capita, education, migration stock), mediators M (mean age at childbearing — never conditioned on: overcontrol bias), and levers T (childcare coverage, housing affordability, labor stability). Estimation: Spatial-SLX Double Machine Learning (CausalForestDML) with spatial block cross-fitting; diagnostics: Moran's I on orthogonalized residuals (KNN weights, k=5, to avoid island isolation); placebo tests by permutation.

### 2.2 The online dynamic layer and the coupled system

The demographic core is a two-sex Leslie-Rogers matrix: female fertility (ASFR by age) generates total births split by sex ratio at birth (0.488 female); sex-specific survival (weighted average of provincial TVM life tables) and sex-specific net migration (Rogers-Castro profile, calibrated level) advance the state:

$$\mathbf{n}_{t+1} = L(F_t)\,\mathbf{n}_t + \mathbf{m}_t$$

The fertility trap endogenizes F_t:

$$\begin{cases}
\mathbf{n}_{t+1} = L(F_t)\,\mathbf{n}_t + \mathbf{m}_t \\
F_{t+1} = (1-\alpha)\,F_t + \alpha\,\Phi(F_t, \mathrm{DR}_t, u_t)
\end{cases}$$

with the feedback function

$$\Phi = F_{\min} + \frac{F_{\max} - F_{\min}}{1 + e^{-k(F_t - \theta)}} \;-\; \gamma \max(0, \mathrm{DR}_t - \mathrm{DR}_0) \;+\; \eta(F_t)\,u_t$$

where DR_t is extracted directly from the age-state vector (65+/15-64). Local stability of a fixed point F* requires Φ'(F*) < 1; a bistable regime exists iff the maximum sigmoid slope exceeds unity, k(F_max−F_min)/4 > 1. At tangency the system undergoes a saddle-node bifurcation (F_c), and crossing below the unstable root F*_U activates structural hysteresis: population aging (rising DR_t) shifts Φ further down, deepening the lower attractor and making exit shocks u_exit far larger than prevention shocks (u_exit ≫ u_prevention).

### 2.3 Identification of the empirical map

For estimation we reduce the coupled system to its transition dynamics: ΔF_{i,t} = a + b0·F_{i,t-1} + b1·F_{i,t-1}·G(F_{i,t-1}; k, θ) + ηΔlog(GDP) + γ·DR_{i,t-1} + year dummies, with G the logistic transition on the state itself. Pooled (not within-country): the fixed effects absorb precisely the basin levels whose separation is the object of the hypothesis. Equilibria of the implied map F_{t+1} = F_t + f̂(F) (controls at sample means) are the empirical counterpart of (F*_L, F*_U, F*_H): stable if f̂' < 0, unstable — no-return threshold — if f̂' > 0.

## 3. Data, Provenance & Pre-processing

All ingestion is automated and versioned; provenance below.

| Dataset | Provider / table | Coverage | Role |
|---|---|---|---|
| Population by age × sex (POSAS) | ISTAT `demo.istat.it`, POSAS 2026 (province, ripping) | Italy, 0–100+, 2026 estimate | initial state n_0, disaggregated aggregation weights |
| Life tables (TVM) | ISTAT `datiprovincialicompleti2024` | 107 provinces, both sexes, single age | survival P_x (population-weighted provincial average) |
| Fertility (ASFR) | ISTAT `demo.istat.it` endpoint RPCCerca (FE1/ASFR) | Italy, by mother's age (14–50), 2024 | fertility profile; implied TFR = 1.18 (= official) |
| Migration balance | ISTAT Migrazioni report (2024 definitive: +263k; 2025 prov.: +296k) | national | calibration of the Rogers-Castro level |
| Regional TFR | Eurostat `demo_r_find2` (TOTFERRT) | 285 NUTS-2 regions, 2013–2023 | transition variable and target of the PSTR |
| Regional GDP per capita | Eurostat `nama_10r_2gdp` (PPS_EU27_2020_HAB) | NUTS-2, 2013–2023 | control (short-run conditions: dlog) |
| Regional dependency ratio | Eurostat `demo_r_pjanaggr3` (Y_GE65 / Y15-64) | NUTS-2, 2013–2023 | aging drag γ |
| Italian provincial panel (Fase 2, integration pending) | OMI (housing), INPS (labor), ISTAT BES (childcare) | 107 NUTS-3, 2013–2024 | causal levers T (Section 4) |

Pre-processing: within-region lags for F and controls (avoiding cross-sectional leakage); log GDP; first differences for the dynamic specification; NUTS-2 selection by code length (removing national and extra-regio codes); TFR range observed 0.84–4.95 (median 1.54). Descriptive statistics and provenance tags are regenerated in `data/processed/eurostat_panel.csv` (2,959 region-year cells; 2,392 after lags).

## 4. Econometric Identification Strategy

1. **DAG-directed screening**: XGBoost + native TreeSHAP (`pred_contribs`) ranking under pooling and within-FE (two-way demeaning) — establishing that the persistence of F dominates the predictive ranking in both variants (first evidence compatible with the trap feedback).
2. **Spatial-SLX DML**: CausalForestDML with W = {log GDP, education, migration} and T = {childcare, housing affordability, labor stability}; spatial block cross-fitting (leave-province-out families); Moran's I on residuals with KNN weights (k = 5, islands included); placebo by permuting T between regions within a year.
3. **Causal mediation**: NDE/NIE decomposition via the age-at-childbearing mediator, quantifying how much of a lever's effect operates through postponement (tempo) rather than realized family size (quantum).
4. **Dynamic PSTR**: transition G(F_{i,t-1}; k, θ) on the state itself, (θ, k) by concentrated least squares over grid, linear part by OLS with year dummies (specification in Section 2.3). Robustness battery per the backtest protocol (Section 6).
5. **Instrumentation of DR**: cohort structure lagged t−15 as an instrument for the current DR (Kleibergen-Paap F > 10; Hansen J), to address the γ sign contradiction documented in Section 5.

## 5. Empirical Results (first wave)

### 5.1 Screening (XGBoost + TreeSHAP, pooling and within-FE)

Persistence (tfr_lag1) dominates the predictive ranking in both variants (importance 0.21 pooled; 0.05 within, on a residual std of 0.09). The 76% of TFR variance is between-region: the GDP-TFR correlation is 2.5x weaker within regions — largely fixed territorial structure (family policy regimes). Screening is predictive, not causal; for this Section 4 introduces identification.

### 5.2 PSTR: threshold and equilibrium structure

| Parameter | Without DR | With DR |
|---|---|---|
| θ̂ (transition threshold) | 1.66 | **1.70** |
| k̂ (slope) | 3.69 | 6.73 |
| b0 (low-regime persistence) | +0.085 | +0.035 |
| b1 (high-regime feedback) | −0.087 | −0.043 |
| η (dlog GDP) | +0.217 | +0.219 |
| γ (DR lag) | — | **+0.081** |

Implied equilibria (controls at sample means, year-base regime): without DR — unstable root F ≈ 0.91, stable attractor F ≈ 1.61; with DR — attractor F ≈ 1.65 (a lower root at 0.49 lies below the observed support, minimum TFR 0.84, and is extrapolation). Cluster bootstrap (B = 399): θ̂ = 1.57 ± 0.18, interval [1.20; 1.75]; the unstable threshold appears in 265/399 replicates (66%). Extending the panel to 1990–2024 rejects parameter constancy: the two-basin structure is a property of the post-2013 era (see docs/15_panel_1990.md), while IV and LOCO on the long window confirm the positive DR sign (γ̂_IV = +0.087, first-stage F = 630).

Three readings. **(i)** The no-return threshold sits below the sociological theoretical threshold (1.35–1.50): the European transition appears more resilient than feared, but no region in the sample ever recovered from below F ≈ 1.0 — Sardinia (TFR 0.85, seventh consecutive year below unity) is below the estimated threshold and its observed trajectory (0.91 → 0.85) is consistent with self-reinforcing decline. Italy (1.18) remains marginally above. **(ii)** The high attractor is ~1.5–1.6, not replacement: even escaping the low regime, the European system converges below 2.1. **(iii)** γ̂ > 0 contradicts the theoretical fiscal-drag sign: we attribute it to the mechanical endogeneity of the DR (built from births 15–65 years ago), to Nordic welfare confounding in the pooled design, and to the level-vs-excess form γ·max(0, DR−DR₀) that the theory actually prescribes — all three addressed in the next wave (t−15 instruments, LOCO, profiled DR₀).

### 5.3 Dynamic layer results (Italy, two-sex Leslie-Rogers)

At TFR 1.18 and observed migration balance: λ₁ = 0.983 (r = −1.67%/yr), asymptotic halving 41.5 years, first halving ~55 years, break-even migration ~600k/yr (2.1× observed); stable structure converges to 39% aged 65+. LTC application: caregiver-per-claimant ratio falls 43% by 2081, shifting an irreducible share of the demand from informal to formal care and raising formal LTC spending from ~5 to 22–38 billion €/yr by mid-century (calibration-sensitive band).

## 6. Out-of-Sample Backtest (in progress)

Protocol (fixed-origin 1995-2012 → test 2013-2024, recursive multi-step; benchmarks M0 static / M1 linear / M2 PSTR; metrics RMSE, MAPE on cohort 0-11, Diebold-Mariano vs M0, Clark-West vs M1, CRPS and coverage from cluster/bootstrap; regime stratification trap/transition/high; robustness: pre-COVID truncation, placebo G, threshold displacement, W_spat perturbation, LOCO, TFR vs TFR*) — specified in full in the repository (docs/06_backtest_protocol.md). [Results: pending — to be compiled upon execution of the protocol on the European panel; current data window (2013–2023) constrains the training window to 2013–2019 for the recursive test, extension backwards via national data under evaluation.]

## 7. Counterfactual Policy Simulations & Conclusions (in progress)

7.1 Case study Italy (TFR 1.14–1.18): 100-year two-sex Leslie-Rogers projections with 95% bands under TFR scenarios (0.95–1.30) and selective migration (0 to +400k/yr) — infrastructure ready (`run_counterfactual_leslie` in the dynamic layer), policy levers pending the causal layer.
7.2 Policy implications (target form): minimum exit shock u_exit and probability of escape from the estimated lower basin; cost of delay via γ·ΔDR. [Pending: u depends on the estimated (k, θ, γ) — available since Section 5.2 — to be propagated through the coupled system with the 1,000-bootstrap draws.]
7.3 Limitations: dynamic-panel (Nickell) bias in the concentrated OLS — corrected by the planned IV/GMM; pooling without country FE exposes to country-level confounding (LOCO in progress); the low attractor F*_L is not identified in the observed range (no region persists below 1.0 for long).

## Appendici

- **A** — Derivazioni matematiche: stabilità locale Φ'(F*) < 1, forma chiusa del punto di biforcazione F_c, raccordo λ₁ (Perron-Frobenius) ↔ tasso intrinseco di Lotka, correzione Bongaarts-Feeney TFR*
- **B** — Specifiche di ottimizzazione PSTR e GMM: griglia Profiled NLS su (k, θ), strumenti ritardati per DR_{i,t}, Kleibergen-Paap, Hansen J, Cluster Block Bootstrap / prior bayesiani (PyMC)
- **C** — Costruzione della curva migratoria (Rogers-Castro) e gestione della classe aperta 100+
- **D** — Data provenance & repository integrity: codici tabella esatti, date di estrazione, schema Parquet, replica end-to-end (`python3 src/download_istat.py && python3 src/download_eurostat.py && python3 src/pstr_trap.py`)
