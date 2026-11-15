"""Create non-destructive, source-level WCS-WAVE diagnostics for existing catalogs."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from science.spectral_wavelength import wavelength_bandwidth_at_sky


RAW_BY_EPOCH = {
    "2025-04-25": "level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits",
    "2025-05-09": "level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits",
    "2026-05-26": "level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150.fits",
}


def create_spectral_diagnostics(project_root: Path, output_version: str = "v1") -> tuple[Path, Path]:
    """Map existing catalog detections to approximate wavelengths, preserving inputs.

    Existing photometry/catalogues are only read. New, versioned sidecar files
    are created; no flux measurements or prior products are modified.
    """
    root = Path(project_root)
    catalog_dir = root / "data" / "catalogues" / "reprocessed"
    raw_dir = root / "data" / "raw"
    csv_path = catalog_dir / f"wcs_wave_diagnostics_{output_version}.csv"
    json_path = catalog_dir / f"wcs_wave_diagnostics_{output_version}.json"
    if csv_path.exists() or json_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing spectral diagnostics for {output_version}")

    output_rows: list[dict] = []
    summary: dict[str, dict] = {}
    for epoch, raw_name in RAW_BY_EPOCH.items():
        raw_path = raw_dir / raw_name
        source_path = catalog_dir / f"{epoch}_detections_photometry.csv"
        values: list[float] = []
        with source_path.open(encoding="utf-8-sig", newline="") as stream:
            for index, detection in enumerate(csv.DictReader(stream)):
                ra, dec = float(detection["ra_deg"]), float(detection["dec_deg"])
                try:
                    spectral = wavelength_bandwidth_at_sky(raw_path, ra, dec)
                    values.append(spectral["wavelength_um_wcs_wave_approx"])
                    output_rows.append({
                        "epoch": epoch,
                        "detection_index": index,
                        "ra_deg": ra,
                        "dec_deg": dec,
                        "input_fits": f"data/raw/{raw_name}",
                        **spectral,
                        "status": "approximate WCS-WAVE diagnostic only; not wavelength-matched photometry",
                    })
                except (ValueError, KeyError) as exc:
                    output_rows.append({
                        "epoch": epoch,
                        "detection_index": index,
                        "ra_deg": ra,
                        "dec_deg": dec,
                        "input_fits": f"data/raw/{raw_name}",
                        "x_input_pixel": None,
                        "y_input_pixel": None,
                        "wavelength_um_wcs_wave_approx": None,
                        "bandwidth_um_wcs_wave_approx": None,
                        "spectral_metadata_source": "unavailable",
                        "status": f"not mapped: {exc}",
                    })
        summary[epoch] = {
            "input_fits": f"data/raw/{raw_name}",
            "mapped_detections": len(values),
            "unmapped_detections": sum(row["epoch"] == epoch and row["wavelength_um_wcs_wave_approx"] is None for row in output_rows),
            "wavelength_min_um_approx": float(np.min(values)) if values else None,
            "wavelength_max_um_approx": float(np.max(values)) if values else None,
            "wavelength_median_um_approx": float(np.median(values)) if values else None,
            "interpretation": "WCS-WAVE diagnostic only; not a calibrated effective bandpass",
        }

    columns = [
        "epoch", "detection_index", "ra_deg", "dec_deg", "input_fits",
        "x_input_pixel", "y_input_pixel", "wavelength_um_wcs_wave_approx",
        "bandwidth_um_wcs_wave_approx", "spectral_metadata_source", "status",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(output_rows)
    json_path.write_text(json.dumps({
        "description": "Approximate wavelength diagnostics mapped from existing source positions through each raw image WCS and WCS-WAVE alternate WCS.",
        "units": {"ra_deg": "deg ICRS", "dec_deg": "deg ICRS", "wavelength_um_wcs_wave_approx": "um", "bandwidth_um_wcs_wave_approx": "um"},
        "scientific_caveat": "IRSA recommends CWAVE/CBAND calibration maps for science analysis. They are not included in this workspace. These WCS-WAVE values are approximate diagnostics, not calibrated bandpasses; do not interpret flux differences as variability.",
        "epochs": summary,
    }, indent=2), encoding="utf-8")
    return csv_path, json_path


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    csv_output, json_output = create_spectral_diagnostics(project)
    print(csv_output)
    print(json_output)
