"""Scarica i dati ISTAT (demo.istat.it) in data/raw/.

- POSAS: popolazione residente per eta' e sesso, province e ripartizioni
- TVM: tavole di mortalita' provinciali complete (eta' singola)
- ASFR: tassi di fecondita' specifici per eta' della madre (endpoint RPCCerca)
"""

import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://demo.istat.it"
APP = "https://demo.istat.it/app"


def download_zip(url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / url.rsplit("/", 1)[-1].replace(".zip", ".csv")
    if dest.exists():
        return dest
    zpath = dest_dir / Path(url).name
    urllib.request.urlretrieve(url, zpath)
    with zipfile.ZipFile(zpath) as z:
        members = [n for n in z.namelist() if n.endswith(".csv")]
        z.extract(members[0], dest_dir)
    return dest_dir / members[0]


def download_asfr(year: int, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"asfr_{year}.json"
    if dest.exists():
        return dest
    payload = urllib.parse.urlencode({
        "indicatore": "ASFR",
        "annoda": str(year),
        "annoa": str(year),
        "etada": "Y14",
        "etaa": "Y50",
        "territorio": "RIP",
        "hid-i": "FE1",
        "hid-a": "2025",
        "hid-l": "it",
        "hid-cat": "FE2",
        "hid-dati": "dati-form-3",
        "hid-tavola": "tavola-form-3",
        "btnricerca-3": "Cerca",
    }).encode()
    req = urllib.request.Request(f"{APP}/RPCCerca.php", data=payload)
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    return dest


def fetch_all(pop_year: int = 2026, tvm_year: int = 2024, asfr_year: int = 2024,
              raw_dir: Path | None = None) -> dict:
    raw = raw_dir or Path(__file__).resolve().parents[1] / "data" / "raw"
    paths = {
        "pop_province": download_zip(
            f"{BASE}/data/posas/POSAS_{pop_year}_it_Province.zip", raw),
        "pop_ripartizioni": download_zip(
            f"{BASE}/data/posas/POSAS_{pop_year}_it_Ripartizioni.zip", raw),
        "tvm": download_zip(
            f"{BASE}/data/tvm/datiprovincialicompleti{tvm_year}.zip", raw),
        "asfr": download_asfr(asfr_year, raw),
        "pop_year": pop_year,
        "tvm_year": tvm_year,
        "asfr_year": asfr_year,
    }
    return paths


if __name__ == "__main__":
    pop_year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    for k, v in fetch_all(pop_year=pop_year).items():
        print(k, "->", v)
