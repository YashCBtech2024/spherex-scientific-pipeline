import urllib.request
import urllib.parse
import json

# 1. Test VizieR Gaia DR3 query
vizier_url = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"
adql = """
SELECT TOP 10
    Source, RA_ICRS, DE_ICRS, Plx, e_Plx, pmRA, e_pmRA, pmDE, e_pmDE, Gmag, BPmag, RPmag, RUWE
FROM "I/355/gaiadr3"
WHERE 1=CONTAINS(POINT('ICRS', RA_ICRS, DE_ICRS), CIRCLE('ICRS', 151.786148, 2.831860, 0.003))
   OR 1=CONTAINS(POINT('ICRS', RA_ICRS, DE_ICRS), CIRCLE('ICRS', 151.762635, 2.802392, 0.003))
"""
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": adql
}).encode("utf-8")

print("Querying VizieR Gaia DR3 TAP...")
req = urllib.request.Request(vizier_url, data=data, headers={"User-Agent": "SPHEREx/1.0"})
with urllib.request.urlopen(req, timeout=20) as resp:
    res = json.loads(resp.read().decode())
    print("VizieR Gaia DR3 Success! Rows:", len(res.get("data", [])))
    for row in res.get("data", []):
        print(row)

# 2. Test JPL sb_ident
# RA = 151.786148 deg -> 10h 07m 08.68s -> 10-07-08.68
# Dec = +2.831860 deg -> +02d 49m 54.70s -> 02-49-54.70
jpl_url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
params = {
    "mpc-code": "500",
    "obs-time": "2025-05-09_03:53:15",
    "fov-ra-center": "10-07-08.68",
    "fov-dec-center": "02-49-54.70",
    "fov-ra-hwidth": "0.1",
    "fov-dec-hwidth": "0.1",
    "two-pass": "true",
    "suppress-first-pass": "true"
}
full_url = f"{jpl_url}?{urllib.parse.urlencode(params)}"
print("\nQuerying JPL sb_ident:", full_url)
req_jpl = urllib.request.Request(full_url, headers={"User-Agent": "SPHEREx/1.0"})
try:
    with urllib.request.urlopen(req_jpl, timeout=20) as resp:
        jres = json.loads(resp.read().decode())
        print("JPL Success! matches:", jres.get("n_matches", 0))
        print("Keys:", list(jres.keys()))
except urllib.error.HTTPError as e:
    print("JPL HTTP Error:", e.code, e.read().decode())
