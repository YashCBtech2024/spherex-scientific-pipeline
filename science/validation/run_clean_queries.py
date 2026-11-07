import urllib.request
import urllib.parse
import json
import sys

# 1. Gaia DR3 on IRSA TAP
irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
query_c1 = """
SELECT 
    source_id, ra, dec, parallax, parallax_error,
    pmra, pmra_error, pmdec, pmdec_error,
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe
FROM gaiadr3.gaia_source
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.786148, 2.831860, 0.002)) = 1
"""
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": query_c1
}).encode("utf-8")

print("--- Testing IRSA Gaia DR3 for Candidate 1 ---", flush=True)
try:
    req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode())
        print(f"C1 matches: {len(res.get('data', []))}", flush=True)
        for row in res.get("data", []):
            print("C1 Row:", row, flush=True)
except Exception as e:
    print(f"C1 failed: {e}", flush=True)

query_c2 = """
SELECT 
    source_id, ra, dec, parallax, parallax_error,
    pmra, pmra_error, pmdec, pmdec_error,
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe
FROM gaiadr3.gaia_source
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.762635, 2.802392, 0.002)) = 1
"""
data2 = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": query_c2
}).encode("utf-8")

print("\n--- Testing IRSA Gaia DR3 for Candidate 2 ---", flush=True)
try:
    req2 = urllib.request.Request(irsa_tap, data=data2, headers={"User-Agent": "SPHEREx/1.0"})
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        res2 = json.loads(resp2.read().decode())
        print(f"C2 matches: {len(res2.get('data', []))}", flush=True)
        for row in res2.get("data", []):
            print("C2 Row:", row, flush=True)
except Exception as e:
    print(f"C2 failed: {e}", flush=True)

# 2. Check JPL Horizons or sb_ident
print("\n--- Testing JPL Horizons API ---", flush=True)
# JPL Horizons observer ephemeris query format:
# https://ssd.jpl.nasa.gov/api/horizons.api?format=json&COMMAND='DES=1'&EPHEM_TYPE='OBSERVER'&CENTER='500@399'&START_TIME='2025-05-09'&STOP_TIME='2025-05-10'&STEP_SIZE='1d'&QUANTITIES='1'
horizons_url = "https://ssd.jpl.nasa.gov/api/horizons.api"
params = {
    "format": "json",
    "COMMAND": "'DES=1'", # Ceres
    "EPHEM_TYPE": "OBSERVER",
    "CENTER": "500@399",
    "START_TIME": "2025-05-09 03:53:15",
    "STOP_TIME": "2025-05-09 03:54:15",
    "STEP_SIZE": "1m",
    "QUANTITIES": "1"
}
req_h = urllib.request.Request(f"{horizons_url}?{urllib.parse.urlencode(params)}")
try:
    with urllib.request.urlopen(req_h, timeout=15) as resp:
        hres = json.loads(resp.read().decode())
        print("Horizons API responded:", hres.get("signature", {}), flush=True)
except Exception as e:
    print("Horizons API failed:", e, flush=True)
