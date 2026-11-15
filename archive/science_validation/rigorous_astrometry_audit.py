import sys
import csv
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from science.utils.fits_header_reader import read_fits_headers

# --- 1. REPRODUCE CANDIDATE ASSOCIATIONS INDEPENDENTLY ---
cat_path = Path("data/catalogues/source_detections_51_catalogue.csv")
with open(cat_path, "r") as f:
    rows = list(csv.DictReader(f))

m25_sources = [r for r in rows if r["Epoch"] == "May_2025"]
m26_sources = [r for r in rows if r["Epoch"] == "May_2026"]

print("=== INDEPENDENT REPRODUCTION OF CROSS-MATCHING ===")
# For every May 2025 source, find nearest neighbor in May 2026
matches = []
for s25 in m25_sources:
    id25 = s25["id"]
    ra25 = float(s25["RA_deg"])
    dec25 = float(s25["Dec_deg"])
    
    best_dist = 1e9
    best_m26 = None
    best_dra_cosdec = 0.0
    best_ddec = 0.0
    
    for s26 in m26_sources:
        id26 = s26["id"]
        ra26 = float(s26["RA_deg"])
        dec26 = float(s26["Dec_deg"])
        
        # Great-circle distance
        # dra in arcsec: (ra26 - ra25) * cos((dec25 + dec26)/2) * 3600
        mid_dec_rad = math.radians((dec25 + dec26) / 2.0)
        dra = (ra26 - ra25) * math.cos(mid_dec_rad) * 3600.0
        ddec = (dec26 - dec25) * 3600.0
        dist = math.hypot(dra, ddec)
        
        if dist < best_dist:
            best_dist = dist
            best_m26 = s26
            best_dra_cosdec = dra
            best_ddec = ddec
            
    matches.append({
        "id25": id25,
        "id26": best_m26["id"],
        "ra25": ra25, "dec25": dec25,
        "ra26": float(best_m26["RA_deg"]), "dec26": float(best_m26["Dec_deg"]),
        "sep_arcsec": best_dist,
        "dra_arcsec": best_dra_cosdec,
        "ddec_arcsec": best_ddec,
        "flux25": float(s25["flux"]),
        "flux26": float(best_m26["flux"]),
        "peak25": float(s25["peak"]),
        "peak26": float(best_m26["peak"]),
        "sharp25": float(s25["sharpness"]),
        "sharp26": float(best_m26["sharpness"]),
        "snr25": float(s25["peak"]) / 0.12, # estimate noise floor from variance (~0.014-0.12)
    })

print(f"{'May25 ID':<10}{'May26 ID':<10}{'Sep (arcsec)':<15}{'dRA*cosDec':<15}{'dDec':<15}{'Within 2\"':<10}")
for m in matches:
    w2 = m["sep_arcsec"] < 2.0
    print(f"{m['id25']:<10}{m['id26']:<10}{m['sep_arcsec']:<15.4f}{m['dra_arcsec']:<15.4f}{m['ddec_arcsec']:<15.4f}{str(w2):<10}")

# --- 2. POSITIONAL UNCERTAINTIES & STATISTICAL SIGNIFICANCE ---
# Theoretical centroid uncertainty: sigma_x,y approx FWHM / (2.355 * SNR)
# SPHEREx PSF FWHM ~ 1.5 - 2.0 pixels ~ 9.3 - 12.5 arcsec
# Typical pointing / WCS 1-sigma uncertainty for SPHEREx Level 2:
# SPHEREx requirement is ~0.5" - 1.0" absolute astrometry.
print("\n=== POSITIONAL UNCERTAINTIES & SIGNIFICANCE TEST ===")
fwhm_arcsec = 11.0 # SPHEREx diffraction/PSF beam FWHM ~ 1.75 pixels * 6.24" ~ 11"

# Net flux & noise from historical photometry table
snr_table = {
    # May 2025 sources SNR from photometry_snr_measurements.csv
    "1": 74.51, "2": 2.52, "3": 29.77, "4": 123.97, "5": 16.66, "6": 104.81
}

for m in matches:
    if m["sep_arcsec"] < 2.0:
        id25 = m["id25"]
        snr25 = snr_table.get(id25, 50.0)
        # Centroiding precision: sigma_pos = FWHM / (2.355 * SNR)
        sigma_centroid_25 = fwhm_arcsec / (2.355 * snr25)
        # May 2026 is similarly high SNR for these bright sources (Flux ~ 20-26, peak ~ 6-8)
        # Peak 8.5 vs noise 0.05 -> SNR ~ 100+
        sigma_centroid_26 = fwhm_arcsec / (2.355 * 100.0)
        sigma_centroid_tot = math.hypot(sigma_centroid_25, sigma_centroid_26)
        
        # WCS registration uncertainty between independent Level 2 pointings (sigma_wcs)
        # SPHEREx star tracker and WCS residual fit uncertainty is typically ~ 0.3" to 0.5"
        for sigma_wcs in [0.2, 0.35, 0.5]:
            sigma_total = math.hypot(sigma_centroid_tot, sigma_wcs)
            chi = m["sep_arcsec"] / sigma_total
            print(f"\nCandidate May25 #{id25} -> May26 #{m['id26']}:")
            print(f"  Observed Separation: {m['sep_arcsec']:.4f} arcsec")
            print(f"  Centroid error 2025 (SNR={snr25:.1f}): {sigma_centroid_25*1000:.1f} mas")
            print(f"  Centroid error 2026 (SNR~100):        {sigma_centroid_26*1000:.1f} mas")
            print(f"  Combined Centroiding Error:           {sigma_centroid_tot*1000:.1f} mas")
            print(f"  Under assumed WCS systematic sigma_wcs = {sigma_wcs:.2f}\":")
            print(f"    Total Expected sigma = {sigma_total:.4f}\"")
            print(f"    Significance (Separation / sigma) = {chi:.2f} sigma")
            if chi < 2.0:
                print(f"    -> NOT statistically significant (< 2-sigma). Fully consistent with astrometric systematics!")
            elif chi < 3.0:
                print(f"    -> Marginal (2 to 3-sigma). Could be minor WCS frame rotation/distortion or low proper motion.")
            else:
                print(f"    -> Statistically significant if WCS uncertainty is strictly <= {sigma_wcs}\".")

# --- 3. SKY COVERAGE OVERLAP & FOV CORNERS ---
print("\n=== SKY FOOTPRINT OVERLAP ===")
def get_footprint(hdr):
    n1 = int(hdr["NAXIS1"])
    n2 = int(hdr["NAXIS2"])
    crp1 = float(hdr["CRPIX1"])
    crp2 = float(hdr["CRPIX2"])
    crv1 = float(hdr["CRVAL1"])
    crv2 = float(hdr["CRVAL2"])
    pc11 = float(hdr["PC1_1"])
    pc12 = float(hdr["PC1_2"])
    pc21 = float(hdr["PC2_1"])
    pc22 = float(hdr["PC2_2"])
    
    # 4 corners in pixel coords (1-based: (1,1), (n1,1), (n1,n2), (1,n2))
    corners = [(1, 1), (n1, 1), (n1, n2), (1, n2), (n1/2, n2/2)]
    sky_pts = []
    for px, py in corners:
        dx = px - crp1
        dy = py - crp2
        # linear tangent plane approx (small field ~ 6 arcmin)
        dra_deg = pc11 * dx + pc12 * dy
        ddec_deg = pc21 * dx + pc22 * dy
        ra = crv1 + dra_deg / math.cos(math.radians(crv2))
        dec = crv2 + ddec_deg
        sky_pts.append((ra, dec))
    return sky_pts

hdr_m25 = read_fits_headers("data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits")[1]["cards"]
hdr_m26 = read_fits_headers("data/raw/level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits")[1]["cards"]

fp25 = get_footprint(hdr_m25)
fp26 = get_footprint(hdr_m26)

print(f"May 2025 Field Center: RA={fp25[4][0]:.5f}, Dec={fp25[4][1]:.5f}")
print(f"  RA span:  [{min(p[0] for p in fp25[:4]):.5f}, {max(p[0] for p in fp25[:4]):.5f}]")
print(f"  Dec span: [{min(p[1] for p in fp25[:4]):.5f}, {max(p[1] for p in fp25[:4]):.5f}]")

print(f"May 2026 Field Center: RA={fp26[4][0]:.5f}, Dec={fp26[4][1]:.5f}")
print(f"  RA span:  [{min(p[0] for p in fp26[:4]):.5f}, {max(p[0] for p in fp26[:4]):.5f}]")
print(f"  Dec span: [{min(p[1] for p in fp26[:4]):.5f}, {max(p[1] for p in fp26[:4]):.5f}]")

# Check if candidates lie inside both footprints
for cand_name, ra, dec in [("Candidate 1", 151.7861, 2.8319), ("Candidate 2", 151.7626, 2.8024)]:
    in25 = (min(p[0] for p in fp25[:4]) <= ra <= max(p[0] for p in fp25[:4])) and (min(p[1] for p in fp25[:4]) <= dec <= max(p[1] for p in fp25[:4]))
    in26 = (min(p[0] for p in fp26[:4]) <= ra <= max(p[0] for p in fp26[:4])) and (min(p[1] for p in fp26[:4]) <= dec <= max(p[1] for p in fp26[:4]))
    print(f"  {cand_name} (RA={ra}, Dec={dec}) inside May 2025: {in25}, inside May 2026: {in26}")
