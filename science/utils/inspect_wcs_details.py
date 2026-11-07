import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from science.utils.fits_header_reader import read_fits_headers

# Let's inspect the exact WCS cards for April 2025 (HDU 1)
apr_headers = read_fits_headers("data/raw/level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits")
image_hdr = apr_headers[1]["cards"]

print("April 2025 Image HDU WCS Cards:")
for k, v in image_hdr.items():
    if any(x in k for x in ["CRVAL", "CRPIX", "CDELT", "CTYPE", "CD1_", "CD2_", "PC1_", "PC2_", "A_ORDER", "B_ORDER"]):
        print(f"  {k} = {v}")
