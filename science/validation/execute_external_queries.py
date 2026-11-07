"""Execute external queries: Gaia DR3 via NASA IPAC IRSA TAP and JPL sb_ident API."""

import urllib.request
import urllib.parse
import json
from pathlib import Path

out_dir = Path("data/external")
out_dir.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. NASA IPAC IRSA TAP - GAIA DR3 QUERY
# -------------------------------------------------------------
print("=" * 60)
print("1. QUERYING GAIA DR3 VIA NASA IPAC IRSA TAP")
print("=" * 60)

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
# Query 10 arcsecond radius around Candidate 1 and Candidate 2
# Candidate 1: RA=151.786148, Dec=2.831860
# Candidate 2: RA=151.762635, Dec=2.802392
# 10 arcsec = 0.002778 deg
adql_query = """
SELECT 
    source_id, ra, dec, parallax, parallax_error,
    pmra, pmra_error, pmdec, pmdec_error,
    phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
    ruwe
FROM gaiadr3.gaia_source
WHERE 1 = CONTAINS(
    POINT('ICRS', ra, dec), 
    CIRCLE('ICRS', 151.786148, 2.831860, 0.005)
) OR 1 = CONTAINS(
    POINT('ICRS', ra, dec), 
    CIRCLE('ICRS', 151.762635, 2.802392, 0.005)
)
"""

data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": adql_query
}).encode("utf-8")

gaia_path = out_dir / "gaia_dr3_raw_candidates.json"
try:
    req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8")
        gaia_path.write_text(content, encoding="utf-8")
        parsed = json.loads(content)
        fields = [f["name"] for f in parsed.get("metadata", [])]
        rows = parsed.get("data", [])
        print(f"Gaia DR3 Success! Found {len(rows)} matching sources.")
        print(f"Fields: {fields}")
        for r in rows:
            print(f"  Row: {r}")
except Exception as e:
    print(f"Gaia DR3 query failed: {e}")

# -------------------------------------------------------------
# 2. NASA JPL SMALL-BODY IDENTIFICATION (SB_IDENT) API
# -------------------------------------------------------------
print("\n" + "=" * 60)
print("2. QUERYING NASA JPL SMALL-BODY IDENTIFICATION API")
print("=" * 60)

# Candidate 1: RA 151.786148 deg -> 10h 07m 08.68s -> 10-07-08.68
# Dec +2.831860 deg -> +02d 49m 54.70s -> 02-49-54.70
# Candidate 2: RA 151.762635 deg -> 10h 07m 03.03s -> 10-07-03.03
# Dec +2.802392 deg -> +02d 48m 08.61s -> 02-48-08.61

targets = [
    {
        "name": "Candidate_1",
        "ra_deg": 151.786148, "dec_deg": 2.831860,
        "ra_hms": "10-07-08.68", "dec_dms": "02-49-54.70"
    },
    {
        "name": "Candidate_2",
        "ra_deg": 151.762635, "dec_deg": 2.802392,
        "ra_hms": "10-07-03.03", "dec_dms": "02-48-08.61"
    }
]

epochs = [
    {"name": "May_2025", "time_str": "2025-05-09T03:53:15"},
    {"name": "May_2026", "time_str": "2026-05-26T08:40:11"}
]

jpl_url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
jpl_all_results = {}

for tgt in targets:
    jpl_all_results[tgt["name"]] = {}
    for ep in epochs:
        query_key = f"{tgt['name']}_{ep['name']}"
        print(f"\nQuerying {tgt['name']} at {ep['name']} ({ep['time_str']})...")
        
        # FOV half-width in degrees: 0.1 deg = 6 arcmin (generous cone around SPHEREx field)
        params = {
            "mpc-code": "500",
            "obs-time": ep["time_str"],
            "fov-ra-center": tgt["ra_hms"],
            "fov-dec-center": tgt["dec_dms"],
            "fov-ra-hwidth": "0.1",
            "fov-dec-hwidth": "0.1",
            "two-pass": "false",
            "req-elem": "false"
        }
        url_full = f"{jpl_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url_full, headers={"User-Agent": "SPHEREx-Audit/1.0"})
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                n_matches = resp_data.get("n_matches", 0)
                jpl_all_results[tgt["name"]][ep["name"]] = resp_data
                print(f"  -> Success! Found {n_matches} Solar System object matches in FOV.")
                if n_matches > 0:
                    print(f"  -> Matches: {resp_data.get('data')}")
        except Exception as e:
            print(f"  -> JPL API error: {e}")
            jpl_all_results[tgt["name"]][ep["name"]] = {"error": str(e)}

jpl_path = out_dir / "jpl_sb_ident_raw_candidates.json"
jpl_path.write_text(json.dumps(jpl_all_results, indent=2), encoding="utf-8")
print(f"\nSaved raw JPL results to {jpl_path}")
