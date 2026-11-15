import urllib.request
import urllib.parse
import json

# Test JPL sb_ident format
url = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
# Check docs or error message
req = urllib.request.Request(f"{url}?obs-time=2025-05-09%2003:53:15&fov-ra-center=151.786148&fov-dec-center=2.831860&fov-ra-lim=0.05&fov-dec-lim=0.05")
try:
    with urllib.request.urlopen(req) as resp:
        print("JPL Success:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("JPL Error code:", e.code)
    print("JPL Error body:", e.read().decode())
