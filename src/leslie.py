"""Costruzione della matrice di Leslie e simulazione della traiettoria.

Specifiche in docs/02_dimezzamento.md (par. 4):
- convenzione births-first (fecondita' separata dalla sopravvivenza neonatale)
- profilo di fecondita' per eta' reale (da ISTAT), non gaussiano
- P_x = L_{x+1}/L_x dalle tavole di mortalita'

Da completare in Fase 2: implementazione dopo il parser ISTAT (src/parse_istat.py).
Interfaccia prevista:
    build_leslie_matrix(fertility_rates, survival_probs, tfr) -> np.ndarray
    simulate_trajectory(n0_female, L, years, mig_rate_vec) -> (pop_total, t_half)
"""
