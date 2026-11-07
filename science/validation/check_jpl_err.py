import urllib.request
import urllib.parse

# Test query to see error message
url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
params = {
    "mpc-code": "500",
    "obs-time": "2025-05-09 03:53:15",
    "fov-ra-center": "10-07-08.68",
    "fov-dec-center": "02-49-54.70",
    "fov-ra-hwidth": "0.1",
    "fov-dec-hwidth": "0.1"
}
full_url = f"{url}?{urllib.parse.urlencode(params)}"
try:
    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Success:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error code:", e.code)
    print("HTTP Error body:", e.read().decode())
