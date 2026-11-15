import urllib.request
import urllib.parse
from pathlib import Path

out_dir = Path("data/external")
out_dir.mkdir(parents=True, exist_ok=True)

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"

# Query 10 arcseconds around Candidate 1 and Candidate 2
# 10 arcsec = 0.002778 deg
query = """
SELECT 
    source_id, ra, dec, parallax, parallax_error,
    pmra, pmra_error, pmdec, pmdec_error,
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe
FROM gaia_dr3_source
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.786148, 2.831860, 0.003)) = 1
   OR CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.762635, 2.802392, 0.003)) = 1
"""

data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "csv",
    "QUERY": query
}).encode("utf-8")

req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    csv_data = resp.read().decode('utf-8')
    raw_path = out_dir / "gaia_dr3_raw_candidates.csv"
    raw_path.write_text(csv_data, encoding="utf-8")
    print(f"Saved Gaia DR3 to {raw_path}")
    print("Results:")
    print(csv_data)
