# Low Fertility Trap: isteresi e punti di non ritorno

> Fonte: contributo dell'utente — formalizzazione della Fase 4 dell'architettura ([04_architettura_due_strati.md](04_architettura_due_strati.md)).

## 1. Il sistema dinamico accoppiato

Per formalizzare la Low Fertility Trap (Lutz, Skirbekk, Testa) occorre trasformare il TFR da parametro esogeno a **variabile di stato endogena**. Lo stato al tempo t è la coppia (n_t, F_t), con n_t vettore della popolazione per età e F_t = TFR_t:

$$\begin{cases}
\mathbf{n}_{t+1} = L(F_t)\,\mathbf{n}_t + \mathbf{m}_t \\
F_{t+1} = (1-\alpha) F_t + \alpha\, \Phi(F_t, \mathrm{DR}_t, u_t)
\end{cases}$$

Dove:

- α ∈ (0, 1] = velocità di aggiustamento delle norme sociali (inerzia culturale)
- DR_t = Σ_{x≥65} n_{x,t} / Σ_{15≤x≤64} n_{x,t} = indice di dipendenza anziani, **estratto direttamente dal vettore di stato della Leslie**
- u_t = Σ_k η_k ΔT_{k,t} = shock netto di policy stimato nella Fase 2 (Spatial DML)

## 2. La funzione di feedback Φ

$$\Phi(F_t, \mathrm{DR}_t, u_t) = F_{\min} + \frac{F_{\max} - F_{\min}}{1 + e^{-k(F_t - \theta)}} - \gamma \max(0, \mathrm{DR}_t - \mathrm{DR}_0) + \eta(F_t)\,u_t$$

Tre meccanismi:

1. **Componente sociologica (sigmoide)**: F_min ≈ 0,95–1,05 (pavimento bio-sociale), F_max ≈ 2,05 (rimpiazzo), θ ≈ 1,45–1,50 (soglia di flesso), k > 0 (intensità del conformismo sociale).
2. **Freno economico-fiscale (-γ ΔDR_t)**: quando l'indice di dipendenza supera DR_0, spesa pensionistica e sanitaria drena risorse dalle coorti giovani, traslando verso il basso l'intera Φ.
3. **Attenuazione di policy η(F_t) ∈ (0, 1]**: funzione crescente di F_t — gli incentivi perdono efficacia marginale quando la trappola è consolidata.

## 3. Stabilità e biforcazione saddle-node

Linearizzando attorno a un punto fisso F* (con DR fissato, approssimazione fast-slow), l'autovalore locale è μ(F*) = (1-α) + α Φ'(F*) e la **condizione di stabilità locale** si riduce a:

$$\Phi'(F^*) < 1$$

La pendenza massima della sigmoide (al flesso F = θ) è k(F_max − F_min)/4. La **trappola emerge se e solo se**:

$$\frac{k\,(F_{\max} - F_{\min})}{4} > 1$$

In tal caso Φ interseca la bisettrice in **tre punti fissi**:

| Punto fisso | Pendenza | Stabilità | Significato |
|---|---|---|---|
| F*_H (alto) | Φ' < 1 | stabile (attrattore) | regime sostenibile ~1,8–2,0 |
| F*_U (soglia) | Φ' > 1 | **instabile** (repulsore) | **soglia critica di non ritorno** ~1,35–1,45 |
| F*_L (basso) | Φ' < 1 | stabile (attrattore) | **Low Fertility Trap** ~1,05–1,15 |

La biforcazione saddle-node avviene nel punto critico F_c dove Φ(F_c) = F_c ∧ Φ'(F_c) = 1.

## 4. Isteresi strutturale

L'accoppiamento con la Leslie genera due asimmetrie:

1. **Collasso asimmetrico**: se uno shock porta F_t < F*_U, il sistema entra nel bacino di F*_L. La Leslie svuota le coorti giovani → DR_t sale → Φ si trasla ulteriormente verso il basso → F*_L scende: la trappola si autoapprofondisce.
2. **Asimmetria di policy (u_uscita ≫ u_prevenzione)**: riportare le condizioni economiche al livello pre-crisi **non basta** a uscire da F*_L. Occorre uno shock u_uscita abbastanza grande da superare la biforcazione superiore **e** compensare il freno γ(DR_t − DR_0) accumulato nel frattempo.

## 5. Identificazione empirica dei parametri (θ, k, γ): Dynamic PSTR

Per non imporli arbitrariamente, l'equazione di stato va riscritta come **Dynamic Panel Smooth Transition Regression** (González, Teräsvirta, van Dijk) su panel **Eurostat NUTS-2** (~240 regioni, 1995–2024).

**Perché panel europeo (condizione necessaria di identificazione)**: per stimare una sigmoide con θ ≈ 1,45–1,50 servono osservazioni che attraversino *entrambi* i regimi (Francia/Nord Europa sopra soglia; Italia/Spagna/Est sotto). Sulla sola Italia quasi tutte le osservazioni giacciono nella coda inferiore: θ e F_max sarebbero debolmente identificati. (Implicazione operativa per questo repo: le stime nazionali/provinciali possono stimare k e γ ma **non** θ in isolamento.)

Stima:

- **Inferenza**: Bayesian Hierarchical PSTR (PyMC/Stan) con prior debolmente informativi θ ~ N(1.5, 0.2²), k ~ HalfNormal(5); oppure Cluster Block Bootstrap a livello di regione (ricampionare intere NUTS-2 per preservare l'autocorrelazione seriale).
- **Incertezza propagata**: B = 1.000 tuple (posterior/bootstrap) → 1.000 simulazioni Leslie → l'output non è un numero ma la **probabilità stimata di uscita dalla trappola** per un dato pacchetto di policy u_t.
- **Strumenti per l'endogeneità di DR_t**: lag ritardati (t−15) della struttura di coorti come strumento demografico; diagnostica Kleibergen-Paap (F > 10, preferibile > 20) e Hansen J (p > 0,10).

Il protocollo di validazione out-of-sample è in [06_backtest_protocol.md](06_backtest_protocol.md); il raccordo con le leve causali (Fase 2, ATE → shock ΔT) è in [02_dimezzamento.md §6](02_dimezzamento.md).
