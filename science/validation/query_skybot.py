import urllib.request
import urllib.parse
import json

# SkyBoT cone search for Candidate 1 & Candidate 2 at May 2025 and May 2026
# Candidate 1: RA=151.786148, Dec=2.831860
# Epoch May 2025: JD 2460804.661985 (2025-05-09 03:53:15 UTC)
# Epoch May 2026: JD 2461186.861248 (2026-05-26 08:40:11 UTC)

skybot_url = "https://vo.imcce.fr/webservices/skybot/skybotquery.php"

queries = [
    {"name": "Candidate_1_May_2025", "ra": 151.786148, "dec": 2.831860, "jd": 2460804.661985},
    {"name": "Candidate_1_May_2026", "ra": 151.786148, "dec": 2.831860, "jd": 2461186.861248},
    {"name": "Candidate_2_May_2025", "ra": 151.762635, "dec": 2.802392, "jd": 2460804.661985},
    {"name": "Candidate_2_May_2026", "ra": 151.762635, "dec": 2.802392, "jd": 2461186.861248},
]

skybot_results = {}
for q in queries:
    params = {
        "-ra": str(q["ra"]),
        "-dec": str(q["dec"]),
        "-epoch": str(q["jd"]),
        "-rd": "300", # 300 arcseconds (5 arcmin radius, covering the entire SPHEREx cutout!)
        "-mime": "json",
        "-output": "all"
    }
    url_full = f"{skybot_url}?{urllib.parse.urlencode(params)}"
    print(f"Querying SkyBoT for {q['name']}...")
    try:
        req = urllib.request.Request(url_full, headers={"User-Agent": "SPHEREx/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            n_targets = data.get("total", 0)
            skybot_results[q["name"]] = data
            print(f"  -> Found {n_targets} Solar System objects within 5 arcminutes!")
            if n_targets > 0:
                for row in data.get("data", []):
                    print("     Target:", row)
    except Exception as e:
        print(f"  -> Failed: {e}")
        skybot_results[q["name"]] = {"error": str(e)}

out_file = "data/external/skybot_solar_system_matches.json"
with open(out_file, "w") as f:
    json.dump(skybot_results, f, indent=2)
print("Saved SkyBoT results to", out_file)
