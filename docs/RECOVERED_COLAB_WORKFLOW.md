# Recovered Colab Workflow (Historical)

This summarizes the archived notebook and tables as historical work. It does not rerun or replace their results.

- `SPHEREx_two_epoch_analysis(1).ipynb` documents loading two calibrated FITS cutouts, inspecting image/WCS metadata, and first-pass source detection using a local background/noise estimate with DAOStarFinder. The notebook explicitly warns that detection parameters need tuning for SPHEREx PSF/quality behavior and that raw pixel coordinates must not be compared before image registration.
- The historical three-epoch catalogue (`source_detections_51_catalogue.csv`) records 3 April 2025, 6 May 2025, and 42 May 2026 detections. Its columns preserve DAOFind centroids, sharpness/roundness, peak/flux/magnitude fields, sky coordinates, epoch, and input image.
- `photometry_snr_measurements.csv` and incoming `SPHEREx_source_photometry.csv` hold prior flux/error/SNR measurements. Their units and exact aperture/background conventions require confirmation against notebook code and FITS calibration before reuse as calibrated measurements.
- `epoch_comparison_crossmatch.csv`, `candidate_motion_associations.csv`, and `may2025_may2026_candidate_associations.csv` record nearest-neighbor associations and offsets. Existing audits identify two close May 2025–May 2026 pairs at approximately 0.444 and 0.300 arcsec. These are preliminary associations, not confirmed moving objects.
- `SPHEREx_source_motion.csv` and preliminary validation workbook contain prior motion/triage outputs; their assumptions must be traced to formulas and uncertainties before they are treated as validated.

The repeatable processing implemented in `science/fits_pipeline.py` covers FITS reading, full celestial WCS including SIP, sky cutout extraction, robust clipped-median background estimation, subtraction, PNG rendering, and JSON metadata. It does not yet reproduce DAOStarFinder detection, calibrated photometry, or cross-epoch association end-to-end. Historical tables remain preserved unchanged.

## Reproduce the current cutout

From the project root in PowerShell:

```powershell
$env:MPLCONFIGDIR = "data\processed\.mplconfig"
.venv312\Scripts\python.exe -c "from science.fits_pipeline import process_observation; process_observation('data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits', 151.81441452, 2.82631029, 32, 'data/processed/test_region', 'spherex_may2025_d1')"
.venv312\Scripts\python.exe -m pytest tests\test_fits_pipeline.py -q
```

Existing outputs are reused only when metadata and files validate; otherwise a versioned output set is created. Source FITS is read-only to this workflow.
