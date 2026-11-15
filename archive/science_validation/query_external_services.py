"""Query ESA Gaia TAP service and NASA JPL SSD Small-Body Identification API
for SPHEREx candidate associations.
"""

import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

out_dir = Path("data/external")
out_dir.mkdir(parents=True, exist_ok=True)

# Candidate coordinates
cands = [
    {"name": "Candidate_1", "ra": 151.786148, "dec": 2.831860},
    {"name": "Candidate_2", "ra": 151.762635, "dec": 2.802392}
]

# Observation timestamps
obs_times = [
    {"epoch": "May_2025", "time_utc": "2025-05-09 03:53:15", "jd": 2460804.661985},
    {"epoch": "May_2026", "time_utc": "2026-05-26 08:40:11", "jd": 2461186.861248}
]

print("=" * 60)
print("1. QUERYING ESA GAIA DR3 TAP SERVICE")
print("=" * 60)

gaia_tap_url = "https://gea.esac.esa.int/tap-server/tap/sync"
adql_query = """
SELECT 
    source_id, ra, dec, parallax, parallax_error, 
    pmra, pmra_error, pmdec, pmdec_error, 
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
    ruwe, radial_velocity
FROM gaiadr3.gaia_source
WHERE 1 = CONTAINS(
    POINT('ICRS', ra, dec), 
    CIRCLE('ICRS', 151.786148, 2.831860, 0.00277)
) OR 1 = CONTAINS(
    POINT('ICRS', ra, dec), 
    CIRCLE('ICRS', 151.762635, 2.802392, 0.00277)
)
"""

data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "csv",
    "QUERY": adql_query
}).encode("utf-8")

req = urllib.request.Request(
    gaia_tap_url, 
    data=data, 
    headers={"User-Agent": "SPHEREx-Audit/1.0 (Astrophysics Research)"}
)

gaia_raw_path = out_dir / "gaia_dr3_raw_candidates.csv"
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        content = response.read().decode("utf-8")
        gaia_raw_path.write_text(content, encoding="utf-8")
        print(f"Saved raw Gaia DR3 response to: {gaia_raw_path}")
        print("Response preview:")
        print("\n".join(content.strip().splitlines()[:10]))
except Exception as e:
    print(f"Gaia TAP query error: {e}")

print("\n" + "=" * 60)
print("2. QUERYING NASA JPL SMALL-BODY IDENTIFICATION (SB_IDENT) API")
print("=" * 60)

jpl_url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
jpl_results = {}

for cand in cands:
    jpl_results[cand["name"]] = {}
    for obs in obs_times:
        key = f"{cand['name']}_{obs['epoch']}"
        print(f"\nQuerying JPL sb_ident for {cand['name']} at {obs['epoch']} ({obs['time_utc']} UTC)...")
        
        # sb_ident parameters:
        # obs-time: YYYY-MM-DD HH:MM:SS
        # fov-ra-center: RA in deg
        # fov-dec-center: Dec in deg
        # fov-ra-lim: FOV half-width in arcmin (e.g. 1.0 arcmin = 60 arcsec)
        # fov-dec-lim: FOV half-height in arcmin (e.g. 1.0 arcmin)
        # mag-required: false
        params = {
            "obs-time": obs["time_utc"],
            "fov-ra-center": str(cand["ra"]),
            "fov-dec-center": str(cand["dec"]),
            "fov-ra-lim": "1.0",
            "fov-dec-lim": "1.0",
            "mag-required": "false"
        }
        
        url_full = f"{jpl_url}?{urllib.parse.urlencode(params)}"
        req_jpl = urllib.request.Request(
            url_full,
            headers={"User-Agent": "SPHEREx-Audit/1.0 (Astrophysics Research)"}
        )
        
        try:
            with urllib.request.urlopen(req_jpl, timeout=30) as resp:
                resp_text = resp.read().decode("utf-8")
                parsed = json.loads(resp_text)
                jpl_results[cand["name"]][obs["epoch"]] = parsed
                n_matches = parsed.get("n_matches", 0)
                print(f"  -> Returned status: {resp.status}, matches found: {n_matches}")
        except Exception as err:
            print(f"  -> JPL query error: {err}")
            jpl_results[cand["name"]][obs["epoch"]] = {"error": str(err)}

jpl_raw_path = out_dir / "jpl_sb_ident_raw_candidates.json"
jpl_raw_path.write_text(json.dumps(jpl_results, indent=2), encoding="utf-8")
print(f"\nSaved raw JPL response to: {jpl_raw_path}")
