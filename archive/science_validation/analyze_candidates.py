import sys
from pathlib import Path
import csv
import math

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

candidates_file = Path("data/catalogues/may2025_may2026_candidate_associations.csv")
detections_file = Path("data/catalogues/source_detections_51_catalogue.csv")
comparisons_file = Path("data/catalogues/epoch_comparison_crossmatch.csv")

print("=" * 70)
print("SCIENTIFIC AUDIT OF PRELIMINARY CANDIDATE ASSOCIATIONS")
print("=" * 70)

with open(candidates_file, "r") as f:
    reader = csv.DictReader(f)
    candidates = list(reader)

for i, cand in enumerate(candidates, 1):
    m25_id = cand["May2025_source_ID"]
    m26_id = cand["May2026_source_ID"]
    m25_ra, m25_dec = float(cand["May2025_RA_deg"]), float(cand["May2025_Dec_deg"])
    m26_ra, m26_dec = float(cand["May2026_RA_deg"]), float(cand["May2026_Dec_deg"])
    sep_arcsec = float(cand["Separation_arcsec"])
    baseline = float(cand["Baseline_days"])
    rate = float(cand["Apparent_rate_arcsec_per_day"])
    
    print(f"\n--- Candidate Association #{i} ---")
    print(f"May 2025 Source #{m25_id}  ->  May 2026 Source #{m26_id}")
    print(f"  May 2025: RA={m25_ra:.6f} deg, Dec={m25_dec:.6f} deg")
    print(f"  May 2026: RA={m26_ra:.6f} deg, Dec={m26_dec:.6f} deg")
    print(f"  Positional Separation: {sep_arcsec:.4f} arcsec ({sep_arcsec*1000:.1f} mas)")
    print(f"  Temporal Baseline:     {baseline:.2f} days (1.046 years)")
    print(f"  Apparent Motion Rate:  {rate:.6f} arcsec/day = {rate * 365.25 * 1000:.1f} mas/year")
    
    # Assess physical interpretation:
    print("  PHYSICAL EVALUATION:")
    if rate < 0.01:
        print(f"    * Apparent motion rate ({rate*1000:.3f} mas/day) is EXTREMELY SMALL.")
        print(f"    * Solar System bodies (Main-Belt Asteroids, NEOs) move at ~100 to 1000+ arcsec/day.")
        print(f"    * A motion rate of ~{rate * 365.25 * 1000:.0f} mas/year is characteristic of:")
        print(f"        (A) Stellar Proper Motion (typical Galactic stars have mu ~ 5 to 500 mas/yr), OR")
        print(f"        (B) Stationary background astrophysical source within SPHEREx astrometric/centroiding jitter.")
        print(f"    * SPHEREx pixel size is ~6.2 arcsec/pixel. Separation of {sep_arcsec:.3f} arcsec is only {sep_arcsec / 6.2:.3f} pixels!")
        print(f"    * Conclusion: NOT a moving Solar System object. Likely a stationary star or moderate proper-motion star.")
