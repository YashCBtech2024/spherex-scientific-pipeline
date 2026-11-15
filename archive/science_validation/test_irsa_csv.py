import urllib.request
import urllib.parse

irsa_tap = "https://irsa.ipac.caltech.edu/TAP/sync"
query_c1 = "SELECT TOP 5 source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 151.786148, 2.831860, 0.005)) = 1"
data = urllib.parse.urlencode({
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "csv",
    "QUERY": query_c1
}).encode("utf-8")

req = urllib.request.Request(irsa_tap, data=data, headers={"User-Agent": "SPHEREx/1.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('utf-8')
        print("IRSA CSV Output:")
        print(text)
except Exception as e:
    print("Failed:", e)
