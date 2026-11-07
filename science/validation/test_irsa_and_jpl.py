import urllib.request
import urllib.parse
import json

# 1. Test JPL sb_ident with clean parameters
jpl_url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
# Candidate 1: RA=151.786148 deg (10h 07m 08.68s -> 10-07-08.68)
# Dec=+2.831860 deg (02d 49m 54.70s -> 02-49-54.70)
params = {
    "mpc-code": "500", # Geocenter
    "obs-time": "2025-05-09_03:53:15",
    "fov-ra-center": "10-07-08.68",
    "fov-dec-center": "02-49-54.70",
    "fov-ra-hwidth": "0.5",  # 0.5 degrees
    "fov-dec-hwidth": "0.5",
    "two-pass": "false",
    "mag-required": "false"
}
full_jpl = f"{jpl_url}?{urllib.parse.urlencode(params)}"
print("Querying JPL sb_ident...")
try:
    req = urllib.request.Request(full_jpl, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode())
        print("JPL Success! matches:", res.get("n_matches", 0))
        print("Fields:", res.get("fields", []))
        print("Data rows:", len(res.get("data", [])))
except Exception as e:
    print("JPL failed:", e)

# 2. Test NASA IRSA Gaia DR3 TAP
irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
adql = """
SELECT TOP 5
    source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
FROM gaia_dr3_source
WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.786148, 2.831860, 0.005))
"""
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": adql
}).encode("utf-8")

print("\nQuerying NASA IPAC IRSA Gaia DR3...")
try:
    req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode())
        print("IRSA Success! rows:", len(res.get("data", [])))
        for r in res.get("data", []):
            print(r)
except Exception as e:
    print("IRSA failed:", e)
