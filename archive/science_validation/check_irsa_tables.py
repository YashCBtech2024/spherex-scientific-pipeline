import urllib.request
import urllib.parse
import json

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
adql = "SELECT table_name FROM TAP_SCHEMA.tables WHERE table_name LIKE '%gaia%' OR table_name LIKE '%dr3%'"
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": adql
}).encode("utf-8")

req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    res = json.loads(resp.read().decode())
    for r in res.get("data", []):
        print(r)
