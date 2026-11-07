# Teammate Integration Handoff

## Completed scientific contribution

The science workspace now has preserved FITS inputs, validated common-grid outputs, a three-epoch coverage mask, preliminary masked source detections/aperture photometry, provisional coordinate associations, historical candidate reassessment, visualizations and export tooling. Reprocessing uses a common mask of 2,259/3,720 grid pixels (60.73%). Detection counts are 5, 7, 7 across April 2025, May 2025 and May 2026. These are preliminary detections, not confirmed astrophysical classifications.

## Files to give teammates

All paths are relative to project root:

- `data/integration/source_measurements_for_import.csv` — flat source measurements; RA/Dec in degrees, flux in Jy from uncorrected aperture sum, empirical flux error in Jy, SNR dimensionless.
- `data/integration/candidate_payloads_provisional.json` — CandidateSummary-shaped examples that explicitly retain unavailable displacement, significance and category as null. **Current backend rejects these records** because its Pydantic fields are required/non-null.
- `data/integration/integration_manifest.json` — output inventory, units, purpose and intended API use.
- `data/catalogues/reprocessed/three_epoch_master_associations.csv` and `.json` — provisional coordinate associations.
- `data/catalogues/reprocessed/historical_candidate_reassessment.json` — positions rechecked against new detections.
- `data/catalogues/reprocessed/{epoch}_detections_photometry.csv` — per-epoch source tables.
- `data/processed/aligned_validated/{epoch}_common_aligned.fits`, `three_epoch_common_coverage_mask.fits`, and `three_epoch_common_comparison_v2.png` — aligned science images and shared validity mask.
- `data/catalogues/reprocessed/three_epoch_source_overlays.png` and `per_epoch_photometry.png` — diagnostic plots.

FITS outputs preserve shared TAN WCS. Original per-epoch cutouts retain their TAN-SIP WCS; reprojection evaluates the input SIP transform. Do not treat interpolated pixels as independent detector samples.

## Existing API contract and fit

The inspected backend's `POST /api/v1/observations/ingest` accepts an `ObservationRecord` and returns 201; it stores only in memory. `ObservationRecord` requires timestamp UTC/MJD, band enum (`BAND_1`…`BAND_6`), wavelength center, exposure time, WCS, zeropoint and background RMS. Its nested source records require positional uncertainty and flux density/error in mJy. Current science exports cannot truthfully fill all these values: channel mapping, exposure/zeropoint, calibrated mJy total flux, and positional uncertainty are not established. Backend `WCSMetadata` also cannot preserve full SIP/CD matrix.

`GET /api/v1/candidates` and `GET /api/v1/candidates/{id}` serve `CandidateSummary`/`CandidateDetail`; no candidate ingestion endpoint exists. CandidateSummary requires non-null displacement, displacement error/significance, magnitude change/error/significance, category enum and validation status. Our one-band aperture values do not provide those quantities. `POST /api/v1/candidates/{id}/validate` is for review updates, not science-data ingestion. Do not use it to inject detections.

The frontend calls health, candidate list and candidate detail only. It formats displacement/magnitude/significance numerically, so null values need frontend guards. It does not currently call observation/cutout or source-measurement endpoints.

## Required teammate changes

### Backend

1. Add a versioned science-product import/storage mechanism behind existing APIs (or a coordinated endpoint) that can store per-epoch detections and provenance; current observation ingest is ephemeral.
2. Make unavailable candidate metrics/category optional or introduce an explicit preliminary-record model/status without changing meaning of existing confirmed records.
3. Add provenance fields for flux unit/method, error method, input file, processing version, common-mask/interpolation note, and WCS calibration state.
4. Support full FITS WCS/SIP or serve cutout FITS/PNG via a documented URI. Simplified TAN WCS alone loses detector distortion.
5. Define conversion policy for MJy/sr-to-mJy, detector/channel mapping, exposure metadata and zeropoint before ObservationRecord ingestion.

### Frontend

1. Display missing metrics as “not measured” rather than formatting null as a number.
2. Distinguish preliminary detection/association from confirmed candidate classification.
3. Display flux units/method and uncertainty caveat; preserve mask/coverage boundaries in image overlays.
4. Add observation and source-list consumption if the app should show this science catalog; current frontend only consumes candidates.

## Scientific limits

Aperture photometry is uncorrected; Jy conversion uses pixel solid angle. Uncertainty is empirical RMS propagated assuming independent pixels, while bilinear reprojection correlates pixels; errors may be low. No PSF/aperture correction, absolute calibration, Gaia-based WCS refinement, or independent cross-epoch identity validation has been performed. Candidate reassessment is positional and provisional; pointing/WCS residuals are not physical motion. Existing Gaia raw query artifact is an IRSA error and the saved rows have unverified provenance. JPL sb_ident and SkyBoT artifacts record failures. No external cross-match is claimed complete.

## Integration test instructions

1. Preserve the science export files as immutable inputs and load the manifest.
2. Validate the flat CSV types/units and reject unknown units rather than assuming mJy.
3. Backend owner should import into an isolated datastore through the agreed loader. Do not send provisional JSON to the current candidate route: it is intentionally marked incompatible until nullable/provenance model support is added.
4. After the backend schema is updated, validate payloads with its Pydantic models and exercise `/api/v1/observations` or candidate list/detail routes in an isolated backend.
5. Point the frontend `API_URL` at that instance. Confirm null-safe rendering, preliminary status labels and truthful units before demo use.
6. From this workspace, regenerate exports with `.venv312\Scripts\python.exe -c "from pathlib import Path; from science.integration_export import export_integration; export_integration(Path('data/catalogues/reprocessed'),Path('data/integration'))"` and run `.venv312\Scripts\python.exe -m pytest tests -q`.

The workspace export intentionally preserves nulls where backend-required significance/classification values are not scientifically available. A fully accepted API payload requires the teammate-side schema/data-loading decisions above; no backend/frontend code was modified here.
