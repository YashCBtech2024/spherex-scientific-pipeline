import urllib.request
import json

req = urllib.request.Request("https://ssd-api.jpl.nasa.gov/doc/sb_ident.html")
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        # Extract parameter section
        import re
        lines = html.splitlines()
        for i, line in enumerate(lines):
            if "fov-" in line or "obs-time" in line or "Parameters" in line:
                for l in lines[max(0, i-2):min(len(lines), i+8)]:
                    print(l)
                break
except Exception as e:
    print("Error:", e)
