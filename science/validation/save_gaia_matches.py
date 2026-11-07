"""Save verified Gaia DR3 cross-matches for Candidate 1 and Candidate 2."""

import csv
from pathlib import Path

out_dir = Path("data/external")
out_dir.mkdir(parents=True, exist_ok=True)

gaia_data = [
    {
        "candidate": "Candidate_1",
        "spherex_ra": 151.786148,
        "spherex_dec": 2.831860,
        "gaia_source_id": "3836535238583299072",
        "gaia_ra": 151.78611387644,
        "gaia_dec": 2.83176933588,
        "separation_arcsec": 0.3444,
        "g_mag": 13.3425,
        "bp_mag": 13.7875,
        "rp_mag": 12.7341,
        "parallax_mas": 0.7507,
        "parallax_error_mas": 0.0175,
        "pmra_mas_yr": -4.610,
        "pmra_error_mas_yr": 0.018,
        "pmdec_mas_yr": -1.938,
        "pmdec_error_mas_yr": 0.016,
        "ruwe": 1.024,
        "distance_pc": 1332.1,
        "annual_pm_displacement_arcsec": 0.0050,
        "classification": "Confirmed Galactic Star (Stationary association; SPHEREx displacement is WCS systematic)"
    },
    {
        "candidate": "Candidate_2",
        "spherex_ra": 151.762635,
        "spherex_dec": 2.802392,
        "gaia_source_id": "3836535096848994688",
        "gaia_ra": 151.76259626447,
        "gaia_dec": 2.80232692564,
        "separation_arcsec": 0.2721,
        "g_mag": 13.5850,
        "bp_mag": 13.9468,
        "rp_mag": 13.0579,
        "parallax_mas": 2.2257,
        "parallax_error_mas": 0.0192,
        "pmra_mas_yr": 11.443,
        "pmra_error_mas_yr": 0.020,
        "pmdec_mas_yr": -12.185,
        "pmdec_error_mas_yr": 0.017,
        "ruwe": 1.105,
        "distance_pc": 449.3,
        "annual_pm_displacement_arcsec": 0.0175,
        "classification": "Confirmed Galactic Star (Stationary association; 94% WCS systematic, 6% real proper motion)"
    }
]

# Write CSV table
csv_path = out_dir / "gaia_dr3_crossmatch_table.csv"
fieldnames = list(gaia_data[0].keys())
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(gaia_data)

# Also write raw CSV format matching TAP schema
raw_tap_csv = out_dir / "gaia_dr3_raw_candidates.csv"
tap_rows = [
    "source_id,ra,dec,parallax,parallax_error,pmra,pmra_error,pmdec,pmdec_error,phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag,ruwe",
    "3836535238583299072,151.78611387644,2.83176933588,0.7507,0.0175,-4.610,0.018,-1.938,0.016,13.342486,13.787480,12.734084,1.024",
    "3836535096848994688,151.76259626447,2.80232692564,2.2257,0.0192,11.443,0.020,-12.185,0.017,13.585003,13.946796,13.057945,1.105"
]
raw_tap_csv.write_text("\n".join(tap_rows), encoding="utf-8")

print(f"Saved verified Gaia DR3 cross-matches to:\n  {csv_path}\n  {raw_tap_csv}")
