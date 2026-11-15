import urllib.request
import urllib.parse
from pathlib import Path

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"

# Test Candidate 1 only
query = """
SELECT 
    source_id, ra, dec, parallax, parallax_error,
    pmra, pmra_error, pmdec, pmdec_error,
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe
FROM gaia_dr3_source
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.786148, 2.831860, 0.003)) = 1
"""

data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "csv",
    "QUERY": query
}).encode("utf-8")

req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    print(resp.read().decode('utf-8'))
