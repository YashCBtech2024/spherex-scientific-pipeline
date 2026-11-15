import sys
from pathlib import Path
import csv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

catalogue_path = Path("data/catalogues/source_detections_51_catalogue.csv")

with open(catalogue_path, "r") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in 51-source catalogue: {len(rows)}")

epochs = {}
for r in rows:
    ep = r["Epoch"]
    epochs.setdefault(ep, []).append(r)

for ep, items in epochs.items():
    print(f"\nEpoch: {ep} ({len(items)} sources)")
    for it in items:
        print(f"  ID {it['id']:>2} | X={float(it['x_centroid']):6.2f}, Y={float(it['y_centroid']):6.2f} | RA={float(it['RA_deg']):10.6f}, Dec={float(it['Dec_deg']):9.6f} | Peak={float(it['peak']):8.4f} | Flux={float(it['flux']):9.4f} | Mag={float(it['mag']):6.3f} | Sharp={float(it['sharpness']):5.3f}")

# Cross-epoch checks for Candidate 1 & Candidate 2
print("\n" + "="*70)
print("CANDIDATE SOURCE DETAILED COMPARISON ACROSS EPOCHS:")
print("="*70)
# Candidate 1: May 2025 #4 -> May 2026 #23
may25_4 = next(r for r in rows if r["Epoch"] == "May_2025" and r["id"] == "4")
may26_23 = next(r for r in rows if r["Epoch"] == "May_2026" and r["id"] == "23")
print("Candidate 1:")
print(f"  May 2025 #4 : RA={may25_4['RA_deg']}, Dec={may25_4['Dec_deg']}, Flux={may25_4['flux']}, Peak={may25_4['peak']}, Mag={may25_4['mag']}")
print(f"  May 2026 #23: RA={may26_23['RA_deg']}, Dec={may26_23['Dec_deg']}, Flux={may26_23['flux']}, Peak={may26_23['peak']}, Mag={may26_23['mag']}")
flux_ratio_1 = float(may26_23['flux']) / float(may25_4['flux'])
print(f"  Flux Ratio (2026/2025): {flux_ratio_1:.4f} (Flux is virtually identical: 26.17 vs 26.12!)")

# Candidate 2: May 2025 #6 -> May 2026 #29
may25_6 = next(r for r in rows if r["Epoch"] == "May_2025" and r["id"] == "6")
may26_29 = next(r for r in rows if r["Epoch"] == "May_2026" and r["id"] == "29")
print("\nCandidate 2:")
print(f"  May 2025 #6 : RA={may25_6['RA_deg']}, Dec={may25_6['Dec_deg']}, Flux={may25_6['flux']}, Peak={may25_6['peak']}, Mag={may25_6['mag']}")
print(f"  May 2026 #29: RA={may26_29['RA_deg']}, Dec={may26_29['Dec_deg']}, Flux={may26_29['flux']}, Peak={may26_29['peak']}, Mag={may26_29['mag']}")
flux_ratio_2 = float(may26_29['flux']) / float(may25_6['flux'])
print(f"  Flux Ratio (2026/2025): {flux_ratio_2:.4f} (Flux is virtually identical: 19.50 vs 18.92!)")
