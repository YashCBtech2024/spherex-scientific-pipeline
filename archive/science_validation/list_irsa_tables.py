import urllib.request
import urllib.parse

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
query = "SELECT table_name FROM TAP_SCHEMA.tables"
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "csv",
    "QUERY": query
}).encode("utf-8")

req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx/1.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('utf-8')
        tables = [t.strip() for t in text.splitlines() if t.strip()]
        gaia_tbls = [t for t in tables if 'gaia' in t.lower()]
        print("Gaia tables found in IRSA:", gaia_tbls)
        if not gaia_tbls:
            print("Total tables in IRSA:", len(tables))
            print("First 20 tables:", tables[1:21])
except Exception as e:
    print("Failed:", e)
