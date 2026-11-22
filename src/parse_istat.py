"""Parser dei CSV ISTAT Demo -> vettori per la matrice di Leslie.

Gestisce i formati tipici di demo.istat.it: intestazioni multi-riga,
separatore ';' o ',', decimali con virgola, righe 'Totale', classe aperta
'100 e piu''. Dettagli sulle fonti in docs/01_dati.md.

Da completare in Fase 1. Interfaccia prevista:
    load_istat_population_female(csv_path, territory, max_age) -> np.ndarray  # n0_female
    load_istat_survival_probs(csv_path, territory, max_age) -> np.ndarray    # P_x = L_{x+1}/L_x
    load_istat_fertility_rates(csv_path, territory) -> np.ndarray            # per eta' 15-49
"""
