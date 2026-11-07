import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from science.utils.fits_header_reader import read_fits_headers

raw_dir = Path("data/raw")
fits_files = sorted(raw_dir.glob("*.fits"))

print(f"Found {len(fits_files)} FITS files in {raw_dir}:")
for f in fits_files:
    print("\n" + "=" * 70)
    print(f"FILE: {f.name} ({f.stat().st_size:,} bytes)")
    try:
        hdus = read_fits_headers(f)
        print(f"Total HDUs found: {len(hdus)}")
        for h in hdus:
            cards = h["cards"]
            extname = cards.get("EXTNAME", "PRIMARY")
            print(f"\n  HDU {h['hdu_index']} ({extname}):")
            for k in [
                "DATE-OBS", "MJD-OBS", "DATE_OBS", "OBSDATE", "TIME-OBS",
                "NAXIS1", "NAXIS2", "NAXIS3", "BITPIX",
                "CTYPE1", "CTYPE2", "CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2",
                "CDELT1", "CDELT2", "CD1_1", "CD1_2", "CD2_1", "CD2_2",
                "CROTA2", "ORIENTAT",
                "FILTER", "BAND", "CHANNEL", "EXPTIME", "TELESCOP", "INSTRUME",
                "WAVELMIN", "WAVELMAX", "WAVELEN"
            ]:
                if k in cards:
                    print(f"    {k} = {cards[k]}")
    except Exception as e:
        print(f"Error inspecting {f.name}: {e}")
