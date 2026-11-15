# Development Log

## 2026-11-07 — Python environment setup

- Resumed the incomplete installation in the existing `.venv312`; did not recreate the environment.
- Installed only missing requirements from `requirements.txt`; existing working NumPy, Astropy, Matplotlib, and Pillow were retained.
- Verified imports for all direct project requirements and test dependencies: passed.
- Ran `.venv312\Scripts\python.exe -m pip check`: `No broken requirements found.`
- Recorded the exact verified package set in [ENVIRONMENT.md](ENVIRONMENT.md).
- FITS scientific processing has not yet resumed in this environment-setup step.

## 2026-11-07 — FITS cutout milestone

- Recovered the documented historical workflow from the archived Colab notebook and catalogs: local-background/noise first-pass DAOStarFinder; three-epoch 51-detection catalogue; aperture/flux/SNR tables; nearest-neighbor crossmatch tables; two close associations (~0.444 and ~0.300 arcsec), still preliminary. Historical outputs were not changed. See `RECOVERED_COLAB_WORKFLOW.md`.
- Implemented `science/fits_pipeline.py` for HDU inspection, image loading, SIP-aware WCS checks, sky cutouts, sigma-clipped median/MAD background, background subtraction, asinh PNG and metadata JSON.
- Processed actual May 2025 IMAGE HDU at requested coordinate into 32x32 FITS cutout and 720x720 PNG. FITS retains TAN-SIP WCS, `BUNIT=MJy / sr`; background median 0.280438 MJy/sr, robust RMS 0.020925 MJy/sr. WCS round-trip error 1.19e-10 px; axis scales 6.2347 and 6.0685 arcsec/px.
- Inspected PNG; updated colorbar to show the true MJy/sr unit and regenerated versioned v3 outputs. Existing earlier outputs were preserved. Processing now reuses a validated complete output set or creates a versioned set; it never overwrites source FITS.
- Added `tests/test_fits_pipeline.py`; final run: **3 passed**. One earlier test run found two test/API mismatches; these were corrected before the passing run.
- Remaining scope: historical detection/photometry/crossmatch calculations are not yet rebuilt end-to-end; their measurement units and uncertainty assumptions still need validation before public use.

## 2026-11-07 — Three-epoch common-coverage alignment validation

- Corrected footprint edge sampling to use pixel-edge bounds `[-0.5, N-0.5]`; dense 257-sample TAN-SIP boundaries are finite, duplicate-filtered and valid polygons.
- Reprojected each original 48x48 cutout through its full WCS onto the existing 60x62 TAN shared grid. Built a strict all-epoch coverage mask from each reproject footprint (`>= 1 - 1e-6`).
- Preserved individual cutouts and preliminary alignment products. Wrote separate final FITS products and the shared mask under `data/processed/aligned_validated/`; invalid pixels are NaN in all epochs.
- Common valid pixels: 2,259 / 3,720; masked pixels: 1,461; fraction 0.607258; valid sky area 0.00659267 deg^2 (local pixel-area approximation).
- Verified identical shape and celestial WCS for all final epoch FITS; output finite-pixel pattern equals the shared mask. Reprojection used bilinear interpolation; this correlates pixels/smooths the PSF, and no source-based astrometric registration was performed.
- Added common coverage tests. Full suite result: **5 passed**. One test initially used an integer pixel instead of the geometric center of the even-sized grid; corrected and reran successfully.
- Comparison PNG is in the validated output folder; images use common coverage and shared display limits. These are ready as inputs for later consistent detection/photometry, with interpolation effects to be included in uncertainty work.

## 2026-11-07 — Three-epoch source analysis handoff

- Ran consistent DAOStarFinder + circular-aperture measurements on the three validated aligned products, restricted to the common coverage mask. Settings are fixed in `science/source_analysis.py`.
- Generated per-epoch detections/photometry CSVs (5, 7, 7 sources), master provisional coordinate-association CSV/JSON, historical candidate reassessment JSON, source-overlay PNG and photometry comparison PNG under `data/catalogues/reprocessed/`.
- Flux conversion reports uncorrected aperture flux in Jy using grid solid angle. Empirical background-RMS errors are independent-pixel approximations and omit interpolation covariance; photometric/astrometric calibration and PSF/aperture corrections remain outstanding.
- Historical candidate pair #4/#23 has nearby new detections, while #6/#29 is not recovered within 2 arcsec in the new detection tables. These are uncertain re-identifications, not motion classifications.
- Gaia/JPL/SkyBoT saved artifacts contain failed or unverified query provenance; no new query result was asserted.
- Added `tests/test_source_analysis.py`; focused test passed. Full suite was invoked but the environment command timed out without a final summary; rerun complete suite before release.
- Handoff and integration limitations documented in `SCIENTIFIC_HANDOFF.md`.

## 2026-11-07 — Teammate integration handoff

- Inspected backend Pydantic models/routes and frontend API consumers from read-only reference repositories; made no changes to either repository.
- Added `science/integration_export.py`; generated flat import CSV, explicitly provisional CandidateSummary-shaped JSON, and manifest under `data/integration/`.
- Missing required significance/displacement/category/calibration/position-error values remain null or are omitted in science measurements. Export marks provisional examples incompatible with the current strict CandidateSummary schema instead of fabricating values.
- Created `docs/TEAMMATE_INTEGRATION_HANDOFF.md` with exact files, schema/unit gaps, necessary teammate changes, limits and test instructions.
- Added schema/provenance test; complete test suite: **7 passed**.
- Export fields are not currently postable to CandidateSummary because required float/category model fields reject null; frontend also formats those metrics as numbers. Backend import/persistence and frontend null-safe preliminary-state handling are required before application display.

## 2026-11-07 — Final scientific handoff package

- Packaged selected raw observations, validated cutouts/aligned outputs, common mask, analysis catalogues, visualizations, integration exports, processing source, tests and scientific/integration documentation.
- Excluded virtual environments, caches, teammate reference repositories and unnecessary duplicate raw files. Original project files and archive remain untouched.
- Re-ran full tests immediately before packaging: **7 passed**.
- Verified ZIP CRCs and unique/exact archive member list (77 files); package includes root README, test results and per-file inventory/hash manifest.
- Package SHA-256 and size recorded in `docs/HANDOFF_PACKAGE_INVENTORY.md` and sidecar `.sha256`.

## 2026-11-15 — Spectral-coordinate audit

- Confirmed the science photometry routine previously read only the aligned 2D IMAGE arrays; it did not read the `WCS-WAVE` table. Its existing epoch plot groups by detection row, not source identity, and was not a light curve.
- Added `science/spectral_wavelength.py` to evaluate the alternate tabular spectral WCS at original-image sky positions, returning approximate wavelength and bandwidth with explicit diagnostic provenance. Celestial SIP distortion is not applied to the separate spectral alternate WCS.
- Added `science/spectral_audit.py`; it maps existing catalogue coordinates to the original FITS files and writes new versioned diagnostics. Existing measurements/catalogues remain untouched.
- IRSA's data-product documentation recommends CWAVE/CBAND calibration maps for science analysis; those products are not present here. WCS-WAVE diagnostics do not establish comparable bandpasses, and cross-epoch flux differences must not be interpreted as variability.
- Updated README/handoff language and the future-generated plot annotation to explicitly say the flux plot is not a light curve.
- Existing catalogue detections mapped successfully with no out-of-footprint sources: 5/5, 7/7, 7/7. Approximate wavelength ranges are 0.90202–0.90693 µm (Apr 25), 0.90183–0.90805 µm (May 9), and 0.91297–0.91996 µm (May 26); these are WCS-WAVE diagnostics, not calibrated bandpasses.
- Added `per_epoch_photometry_not_lightcurve_v1.png`, preserving the earlier figure and explicitly warning that the points are not matched sources or wavelength-matched variability measurements.
- Added four focused wavelength tests; focused run: **4 passed**. Full test suite: **11 passed**. Pytest emitted an existing pytest-asyncio configuration deprecation warning; no test failures.

## 2026-11-15 — Repository deduplication

- Removed the copied `applications/` and `spherex-temporary-integration/` trees from the published repository while preserving both local folders; `.gitignore` keeps them local-only. README now links to the teammates' separate repositories.
- Compared archive copies to canonical active files using SHA-256; 12 exact duplicate archive files are retained locally and excluded from Git. Active copies in `data/raw/`, `data/catalogues/`, and `data/external/` remain tracked.
- Confirmed the unsuffixed May 2025 test-region FITS and `_v2_`/`_v3_` FITS have the same SHA-256. Kept the unsuffixed canonical file tracked; the suffixed copies remain local and ignored. PNG and JSON variants were not identical and were left alone.
- Kept the new dependency, portable-path, wavelength-diagnostic, and test updates in the repository.

## 2026-11-15 — Catalogue and scratch-file cleanup

- Renamed `candidate_associations_validated.csv` to `candidate_associations_provisional.csv`; both classification labels now read `Unconfirmed; Gaia association unverified`. Numeric historical fields were left unchanged.
- Moved the 23 Python files from `science/validation/` to `archive/science_validation/` without altering their contents. This is 22 exploratory scripts plus the empty package initializer; seven scripts use the `test_*.py` filename pattern and are not the automated unit-test suite.
- Removed three empty placeholder packages (`science/astrometry`, `science/detection`, `science/matching`) after confirming they contained only empty initializers and had no code references.
- Moved the non-identical v2/v3 PNG and JSON outputs out of the active test-region folder to `archive/processed_variants/test_region/`; their duplicate FITS pixel arrays remain local and ignored, with the canonical FITS retained.
- Added pytest discovery configuration restricting default collection to `tests/`, so archived exploratory query scripts are not mistaken for automated tests.
- Replaced unsupported “confirmed star” text in the saved Gaia candidate table and epoch metadata with unconfirmed/unverified status; recorded numeric measurements were preserved.
