import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from science.utils.fits_data_reader import read_fits_image_2d

apr_fits = "data/raw/level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits"
may_fits = "data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits"

apr_img, apr_hdr = read_fits_image_2d(apr_fits, hdu_index=1)
apr_flags, _ = read_fits_image_2d(apr_fits, hdu_index=2)
apr_var, _ = read_fits_image_2d(apr_fits, hdu_index=3)

may_img, may_hdr = read_fits_image_2d(may_fits, hdu_index=1)

print(f"April 2025 Image Dimensions: {len(apr_img)} rows (NAXIS2) x {len(apr_img[0])} cols (NAXIS1)")
print(f"May 2025 Image Dimensions:   {len(may_img)} rows x {len(may_img[0])} cols")

# In May 2025:
# Candidate 1 (May #4) was at X=10.62, Y=31.31
# Candidate 2 (May #6) was at X=4.61, Y=52.29
# Let's inspect the April 2025 image values at these locations:
for name, may_x, may_y in [("Candidate 1", 10.62, 31.31), ("Candidate 2", 4.61, 52.29)]:
    x_int = int(round(may_x))
    y_int = int(round(may_y))
    print(f"\n--- {name} at May pixel ~(X={x_int}, Y={y_int}) ---")
    if 0 <= y_int < len(apr_img) and 0 <= x_int < len(apr_img[0]):
        apr_val = apr_img[y_int][x_int]
        flag_val = apr_flags[y_int][x_int]
        var_val = apr_var[y_int][x_int]
        may_val = may_img[y_int][x_int]
        print(f"  May 2025 flux at ({x_int},{y_int}):   {may_val:.4f}")
        print(f"  April 2025 flux at ({x_int},{y_int}): {apr_val:.4f}")
        print(f"  April 2025 flag at ({x_int},{y_int}): {flag_val} (binary: {bin(flag_val)})")
        print(f"  April 2025 variance:                  {var_val:.6f}")
    else:
        print("  Coordinates fall outside April image boundaries!")
