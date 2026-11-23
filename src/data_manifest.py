"""Data-vintage manifest: provenienza completa e verificabile dei dati grezzi.

Per ogni file in data/raw registra: URL della fonte, dataset, vintage
(anno di riferimento dei dati), data di estrazione (mtime locale al download),
SHA-256, script di acquisizione/parsing e versione del codice (CITATION.cff).
Output: data/metadata/manifest.json (versionato).

Esecuzione: python3 src/data_manifest.py
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ISTAT_BASE = "https://demo.istat.it"
EUROSTAT_BASE = ("https://ec.europa.eu/eurostat/api/dissemination/"
                 "statistics/1.0/data")

SOURCES = {
    "POSAS_2026_it_Province.csv": {
        "provider": "ISTAT", "dataset": "POSAS",
        "url": f"{ISTAT_BASE}/data/posas/POSAS_2026_it_Province.zip",
        "vintage": "2026 (stima post-censuale, al 1 gennaio 2026)",
        "contenuto": "popolazione residente per eta', sesso, provincia",
        "acquisizione": "src/download_istat.py", "parsing": "src/parse_istat.py",
    },
    "POSAS_2026_it_Ripartizioni.csv": {
        "provider": "ISTAT", "dataset": "POSAS",
        "url": f"{ISTAT_BASE}/data/posas/POSAS_2026_it_Ripartizioni.zip",
        "vintage": "2026 (stima)",
        "contenuto": "popolazione per eta', sesso, ripartizione",
        "acquisizione": "src/download_istat.py",
        "parsing": "src/leslie_regionale.py",
    },
    "datiprovincialicompleti2024.csv": {
        "provider": "ISTAT", "dataset": "TVM completi",
        "url": f"{ISTAT_BASE}/data/tvm/datiprovincialicompleti2024.zip",
        "vintage": "2024 (tavole di mortalita' provinciali, eta' singola)",
        "contenuto": "sopravvivenza prospettiva P_x per provincia e sesso",
        "acquisizione": "src/download_istat.py", "parsing": "src/parse_istat.py",
    },
    "asfr_2024.json": {
        "provider": "ISTAT", "dataset": "ASFR",
        "url": f"{ISTAT_BASE}/app/RPCCerca.php",
        "vintage": "2024 (fe.condita' per eta' della madre)",
        "contenuto": "ASFR nazionali per eta' (POST indicatore=ASFR)",
        "acquisizione": "src/download_istat.py", "parsing": "src/parse_istat.py",
    },
    "eurostat/tfr_nuts2.json": {
        "provider": "Eurostat", "dataset": "demo_r_find2",
        "url": f"{EUROSTAT_BASE}/demo_r_find2?indic_de=TOTFERRT",
        "vintage": "2013-2023", "contenuto": "TFR NUTS-2",
        "acquisizione": "src/download_eurostat.py", "parsing": "src/panel_screening.py",
    },
    "eurostat/gdp_nuts2.json": {
        "provider": "Eurostat", "dataset": "nama_10r_2gdp",
        "url": f"{EUROSTAT_BASE}/nama_10r_2gdp?unit=PPS_EU27_2020_HAB",
        "vintage": "2013-2023", "contenuto": "PIL pro-capite PPS NUTS-2",
        "acquisizione": "src/download_eurostat.py", "parsing": "src/panel_screening.py",
    },
    "eurostat/pop_eta_nuts2.json": {
        "provider": "Eurostat", "dataset": "demo_r_pjanaggr3",
        "url": f"{EUROSTAT_BASE}/demo_r_pjanaggr3?unit=NR&sex=T",
        "vintage": "2013-2023",
        "contenuto": "popolazione per classi di eta' NUTS-2 (DR regionale)",
        "acquisizione": "src/download_eurostat.py", "parsing": "src/download_eurostat.py",
    },
    "eurostat/pop_eta_storico_nuts2.json": {
        "provider": "Eurostat", "dataset": "demo_r_pjangroup",
        "url": f"{EUROSTAT_BASE}/demo_r_pjangroup?unit=NR&sex=T",
        "vintage": "1990-2025",
        "contenuto": "storico DR regionale e strumento dr_t15",
        "acquisizione": "src/download_eurostat.py",
        "parsing": "src/download_eurostat.py",
    },
    "eurostat/tfr_nuts2_storico.json": {
        "provider": "Eurostat", "dataset": "demo_r_find2",
        "url": f"{EUROSTAT_BASE}/demo_r_find2?indic_de=TOTFERRT",
        "vintage": "1990-2024", "contenuto": "TFR NUTS-2, serie lunga",
        "acquisizione": "src/download_eurostat.py",
        "parsing": "src/download_eurostat.py",
    },
    "eurostat/gdp_nuts2_storico.json": {
        "provider": "Eurostat", "dataset": "nama_10r_2gdp",
        "url": f"{EUROSTAT_BASE}/nama_10r_2gdp?unit=PPS_EU27_2020_HAB",
        "vintage": "2000-2024", "contenuto": "PIL PPS NUTS-2, serie lunga",
        "acquisizione": "src/download_eurostat.py",
        "parsing": "src/download_eurostat.py",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def code_version() -> str:
    try:
        cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        for line in cff.splitlines():
            if line.startswith("version:"):
                return line.split("version:")[1].strip()
    except OSError:
        pass
    return "unknown"


def build_manifest(verbose: bool = True) -> dict:
    out_dir = ROOT / "data" / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    ver = code_version()
    files = []
    for name, meta in SOURCES.items():
        path = ROOT / "data" / "raw" / name
        if not path.exists():
            continue
        entry = dict(meta)
        entry["file"] = f"data/raw/{name}"
        entry["sha256"] = sha256(path)
        entry["dimensione_bytes"] = path.stat().st_size
        entry["data_estrazione"] = datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc).isoformat()
        entry["versione_codice"] = ver
        files.append(entry)
    manifest = {
        "generato": datetime.now(tz=timezone.utc).isoformat(),
        "versione_codice": ver,
        "nota": ("Ogni numero del repo deriva da questi file: per "
                 "riproducibilita' completa rigenerare con "
                 "src/download_istat.py e src/download_eurostat.py e "
                 "confrontare gli SHA-256 (le fonti ufficiali possono "
                 "revisionare i microdati tra un vintage e il successivo)"),
        "fonti": files,
    }
    dest = out_dir / "manifest.json"
    dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    if verbose:
        print(f"manifest: {len(files)} fonti -> {dest}")
    return manifest


if __name__ == "__main__":
    build_manifest()
