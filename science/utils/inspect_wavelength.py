import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from science.utils.fits_header_reader import read_fits_headers

apr_fits = "data/raw/level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits"
may_fits = "data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits"
may26_fits = "data/raw/level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits"

print("=" * 60)
print("SPHEREx SPECTRAL & BAND CONFIGURATION:")
print("=" * 60)

for fpath in [apr_fits, may_fits, may26_fits]:
    headers = read_fits_headers(fpath)
    print(f"\nFile: {Path(fpath).name}")
    for idx, h in enumerate(headers):
        ext = h["cards"].get("EXTNAME", f"HDU_{idx}")
        keys_to_print = [k for k in h["cards"] if any(w in k for w in ["WAVE", "BAND", "ARRAY", "DET", "FILTER", "CHANN", "OBS", "DATE", "MJD", "DISP", "SPECT"])]
        if keys_to_print:
            print(f"  HDU {idx} ({ext}):")
            for k in keys_to_print[:10]:
                print(f"    {k} = {h['cards'][k]}")
