# Fonti dati ISTAT

I dati vengono scaricati automaticamente da [demo.istat.it](https://demo.istat.it) tramite `src/download_istat.py` (nessun download manuale necessario):

```bash
python3 src/download_istat.py        # scarica in data/raw/
python3 src/parse_istat.py           # genera i vettori in data/processed/
```

## Dataset usati

| Dataset | Endpoint | Anno | Contenuto |
|---|---|---|---|
| Popolazione residente (POSAS) | `https://demo.istat.it/data/posas/POSAS_<anno>_it_Province.zip` | 2026 (stima) | popolazione per età (0–100+), sesso e provincia, classi aperta 100 |
| Tavole di mortalità (TVM) | `https://demo.istat.it/data/tvm/datiprovincialicompleti<anno>.zip` | 2024 | tavole Provinciali complete per età singola (Sopravviventi, decessi, P_x prospettiva). La versione "ridotti" ha classi quinquennali: non usare per la Leslie a età singola. |
| Fecondità per età (ASFR) | POST `https://demo.istat.it/app/RPCCerca.php` (indicatore `ASFR`, anno evento) | 2024 (2025 non ancora disponibile) | tassi per mille per età 14–50, righe aggregate incl. **Italia** |

⚠️ Nota TVM: le tavole nazionali non esistono come file separato; la tabella femminile nazionale è ricostruita in `parse_istat.py` come **media provinciale delle P_x pesata per la popolazione femminile** di ciascuna provincia ed età (approximation standard, vedi docstring).

## Aggregazioni in parse_istat.py

- `n0_female`: femmine per età 0–100, somma delle 107 province (istanze come ripartizioni non incluse)
- `survival_probs`: P_x = media provinciale pesata (pesi = femmine per provincia ed età); classe aperta chiusa con P_100 = 0
- `fertility_rates`: ASFR nazionale (riga "Italia"), convertita da per mille a per donna

## Controlli di qualità (summary.json)

Confrontare con i comunicati ISTAT: TFR implicito atteso 1,18 (2024); popolazione totale attesa ≈ 58,9 M (maschi+femmine). Ultima esecuzione:

```json
{
  "anno_popolazione": "2026",
  "popolazione_totale_femmine": 30022193.0,
  "over_65_femmine_pct": 26.0,
  "tfr_implicito": 1.18028,
  "eta_media_feconda": 32.11,
  "P_0": 0.99980,
  "P_30": 0.99976,
  "P_80": 0.96747
}
```

## Aggiornamenti futuri

- Quando ISTAT pubblica l'ASFR 2025/2026: rieseguire con `python3 src/download_istat.py 2027` (la disponibilità dell'ASFR dipende dal comunicato annuale natalità/fecondità)
- Per esercizi territoriali: sono disponibili anche `POSAS_<anno>_it_Ripartizioni.zip` e i singoli zips provinciali
