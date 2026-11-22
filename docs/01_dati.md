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
- La CI scarica e riprocessa tutto a ogni push/PR: una pubblicazione ISTAT nuova si rileva automaticamente fallendo o aggiornando i controlli di qualità (`summary.json`)

## Fonti previste non ancora integrate (Fase 2-3)

| Dato | Fonte | Unità | Uso previsto |
|---|---|---|---|
| Canoni di locazione OMI | Agenzia delle Entrate (dati.agenziaentrate.gov.it, semiportali OMI) | €/m² per comune e tipologia | leva `ratio_affitto_reddito` (housing affordability) |
| Redditi fiscali | MEF / Open BDAP (dichiarazioni per comune) | reddito mediano | denominatore del rapporto affitto/reddito |
| Occupazione e tipi di contratto | INPS (Osservatorio sul lavoro) | quote a termine/part-time 25-39 | leva `quota_indet_f25_39` (precarietà) |
| Copertura asili nido | ISTAT BES / Regioni | posti per 100 bambini 0-2 | leva `copertura_nidi` |
| TFR regionale e PIL | Eurostat `demo_r_find2`, `nama_10r_2gdp` | panel NUTS-2 | ✔ già integrati (Fase 3) |
| Dependency ratio regionale | Eurostat `demo_r_pjanaggr3` | 65+/15-64 | ✔ già integrata (PSTR) |

Politica di provenienza: ogni dataset ha tag di fonte e data di estrazione nel nome file o in `summary.json`; i dati grezzi non sono versionati (dimensione) ma sono riscaricabili in modo deterministico dagli endpoint pubblici.

## Coerenza temporale degli input (dichiarazione esplicita)

La proiezione Leslie usa tre input di **annate diverse**. La scelta è intenzionale (sono le fonti più recenti disponibili per ciascun blocco alla data del setup) ma va dichiarata per evitare letture improprie:

| Blocco | Anno | Fonte | Ruolo nel modello |
|---|---|---|---|
| **Base demographic state** n₀ | **2026** | POSAS 2026 (stima post-censuale 2021) | condizione iniziale della proiezione |
| **Parametri strutturali** P_x | **2024** | TVM completi 2024 | sopravvivenza per età, ritenuta costante nel tempo |
| **Fertility baseline** ASFR_x | **2024** | ASFR 2024 (TFR implicito 1,18) | profilo di fecondità per età, scalato via `tfr_scale` |

Non è una proiezione "2025-based": la struttura per età della fecondità e la mortalità sono 2024, solo lo stato iniziale è 2026. Le tavole e le ASFR 2025 non sono ancora pubblicate nei formati completi usati dal parser; l'aggiornamento è meccanico (cambiare gli anni in `download_istat.py`).

Per evitare l'ambiguità tra il TFR implicito del modello e il dato annunciato dall'ISTAT per il 2025, i due scenari base sono separati esplicitamente:

| | Scenario A (base del modello) | Scenario B (TFR 2025 annunciato) |
|---|---|---|
| TFR | **1,18** (implicito, ASFR 2024) | **1,14** (comunicato ISTAT, 355.772 nati) |
| Scala `tfr_scale` | 1,00 | 1,14/1,18 ≈ 0,966 |
| λ₁ | 0,9834 | **0,9824** |
| r | -0,0167 | **-0,0177** |
| t½ asintotico | 41,5 anni | **39,1 anni** |
| Primo dimezzamento | 55,1 anni | **53,8 anni** |
| Pop. femmine 2056 | 22,4 M | **22,3 M** |
| Pop. 2076 | 16,2 M | **16,0 M** |

Lettura: il momento di fertilità al 2025 (effetto tempo, cfr. Bongaarts–Feeney) peggiora il t½ asintotico di ~2,4 anni ma lascia quasi invariata la traiettoria a medio periodo — la quantità rilevante per la catena LTC è la struttura per età delle madri potenziali, non il solo TFR corrente. Lo scenario B è riproducibile con `python3 src/leslie.py --scenari` (include 1,14 in griglia).
