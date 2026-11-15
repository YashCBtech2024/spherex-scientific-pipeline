import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from science.utils.fits_header_reader import read_fits_headers

files = {
    "April 2025": "data/raw/level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits",
    "May 2025":   "data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits",
    "May 2026 (cutout)": "data/raw/level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150.fits",
    "May 2026 (mosaic)": "data/raw/level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits"
}

print("=== TASK 1: DETAILED PIXEL SCALE & WCS AUDIT FOR EACH FILE ===")
for name, fpath in files.items():
    hdus = read_fits_headers(fpath)
    img_hdr = hdus[1]["cards"]
    
    naxis1 = int(img_hdr.get("NAXIS1", 0))
    naxis2 = int(img_hdr.get("NAXIS2", 0))
    ctype1 = img_hdr.get("CTYPE1", "")
    ctype2 = img_hdr.get("CTYPE2", "")
    crval1 = float(img_hdr.get("CRVAL1", 0))
    crval2 = float(img_hdr.get("CRVAL2", 0))
    crpix1 = float(img_hdr.get("CRPIX1", 0))
    crpix2 = float(img_hdr.get("CRPIX2", 0))
    
    pc1_1 = float(img_hdr.get("PC1_1", 0))
    pc1_2 = float(img_hdr.get("PC1_2", 0))
    pc2_1 = float(img_hdr.get("PC2_1", 0))
    pc2_2 = float(img_hdr.get("PC2_2", 0))
    cdelt1 = float(img_hdr.get("CDELT1", 1.0))
    cdelt2 = float(img_hdr.get("CDELT2", 1.0))
    
    # Calculate pixel scale in axis 1 and axis 2
    # s1 = sqrt((CDELT1*PC1_1)^2 + (CDELT1*PC1_2)^2)
    s1_deg = math.hypot(cdelt1 * pc1_1, cdelt1 * pc1_2)
    s2_deg = math.hypot(cdelt2 * pc2_1, cdelt2 * pc2_2)
    s1_arcsec = s1_deg * 3600.0
    s2_arcsec = s2_deg * 3600.0
    
    # Area per pixel
    det_pc = (cdelt1*pc1_1)*(cdelt2*pc2_2) - (cdelt1*pc1_2)*(cdelt2*pc2_1)
    pixel_area_arcsec2 = abs(det_pc) * (3600.0**2)
    
    # Check SIP distortion coefficients if present
    has_sip = "SIP" in ctype1 or "A_ORDER" in img_hdr
    a_order = img_hdr.get("A_ORDER", "None")
    b_order = img_hdr.get("B_ORDER", "None")
    
    # Check units
    bunit = img_hdr.get("BUNIT", "UNKNOWN")
    
    print(f"\n{name} -> {Path(fpath).name}:")
    print(f"  NAXIS: {naxis1} x {naxis2} | BUNIT: {bunit}")
    print(f"  CTYPE: {ctype1}, {ctype2} (SIP present: {has_sip}, A_ORDER={a_order}, B_ORDER={b_order})")
    print(f"  CRPIX: ({crpix1}, {crpix2}) | CRVAL: ({crval1:.6f}, {crval2:.6f})")
    print(f"  PC Matrix: [[{pc1_1:.8e}, {pc1_2:.8e}], [{pc2_1:.8e}, {pc2_2:.8e}]]")
    print(f"  Pixel scale axis 1: {s1_arcsec:.4f} arcsec/pixel")
    print(f"  Pixel scale axis 2: {s2_arcsec:.4f} arcsec/pixel")
    print(f"  Pixel area:         {pixel_area_arcsec2:.4f} arcsec^2")
