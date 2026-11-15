import urllib.request

for test_url in ["https://www.google.com", "https://ssd-api.jpl.nasa.gov/doc/version.html"]:
    try:
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"Success reaching {test_url}: status {resp.status}")
    except Exception as e:
        print(f"Failed reaching {test_url}: {e}")
