# Temporary SPHEREx Integration Testing Report

**Tested:** 8 November 2026  
**Scope:** isolated `spherex-temporary-integration` copy only  
**Frontend:** Streamlit at `http://127.0.0.1:8501`  
**Backend:** FastAPI at `http://127.0.0.1:8000` (`/docs`)

## Outcome

The temporary frontend communicates with the temporary backend and displays the copied scientific products. The backend health endpoint responds successfully, and it reports `synthetic_seed_data_loaded=false`, 3 observations and 19 detections. No API keys or external credentials are needed for this local integration test.

## Verification performed

- Read both reference README/setup guides, requirements, backend API routes/models, frontend API helpers and page structure. Their original claims/features are not assumed to be implemented in this science-backed copy.
- Confirmed both original reference working trees remain clean; all code changes are in this temporary copy.
- Complete automated suite: **16 passed** (`13` backend integration tests plus `3` scientific product checks). The added API-route/filter test covers spectral routes, observation metadata/filtering, cone search and safe 422 validation of write requests without mutating records.
- All documented GET endpoints and `/docs` returned HTTP 200 in API smoke checks. Write endpoints were checked with invalid empty requests and returned expected 422 responses; valid ingestion and review writes were intentionally not performed.
- Backend HTTP tests include health/root, three epochs and metadata, null/provisional candidate values, real FITS image/mask/WCS payloads, a real-pixel 48×48 PNG cutout, associations and 404 behavior.
- Scientific product checks verified 5/7/7 detections, three common 60×62 images, identical WCS, exact 2,259-pixel common mask, image/catalogue WCS positions, positive empirical errors and preserved raw FITS files.
- Streamlit `AppTest` smoke run: **0 exceptions** on the sky viewer. Switched from the first to the 26 May 2026 epoch (no exceptions); loaded the source detail page (no exceptions). Confirmed null displacement/significance, absent classification, ICRS coordinates, units, errors and provenance render as explicit unavailable/provisional text.
- Browser check at localhost: actual image heatmap and WCS-projected source table rendered; the three-epoch comparison produced all three epoch panels; preliminary photometry plotted by date without connecting unvalidated detections; both historical candidate reassessments appeared with caveats; a sky cutout request returned an 86.2%-covered raster and WCS metadata.
- Parsed **38 Python files** in the copied backend/frontend/science code: no syntax errors.
- First UI smoke run exposed duplicate Streamlit Plotly element IDs, which were fixed by assigning unique chart keys. A later smoke run passed.
- Pytest emitted one non-failing `pytest-asyncio` deprecation warning because the inherited test config does not set `asyncio_default_fixture_loop_scope`.

## Features working

- Three dates and source counts reflect the copied scientific catalogues.
- Aligned images display actual FITS pixel values in MJy/sr on the validated common WCS grid. Invalid common-footprint pixels remain masked.
- Source markers are displayed using catalogue RA/Dec transformed through the shared celestial WCS.
- Sky-coordinate cutout API uses copied FITS pixels and returns a pixel-sized PNG plus cutout WCS and coverage information.
- Source details and measurement table retain uncorrected aperture flux and empirical uncertainty separately from calibrated flux (null), scientific classification (not assessed), and motion metrics (not measured).
- The comparison uses the same grid, common mask and intensity limits for each epoch.
- Available photometry is shown by epoch with empirical error bars but no identity linking or variability claim.
- Historical associations are presented as provisional and not as motion detections.

## Bugs and changes made

- Assigned unique keys to repeated Plotly panels after Streamlit raised `StreamlitDuplicateElementId`.
- Reworked the flux-vs-time panel after a runtime `KeyError: epoch`: the observation API does not contain that association-only field. The panel now shows separate, unlinked detections by actual observation timestamp, avoiding an unsupported identity link.
- Updated source detail copy to match the unlinked photometry presentation.
- The first backend run exposed that the cutout PNG endpoint returned a display-sized bitmap rather than the requested FITS-sized dimensions. The copied backend now returns and tests a 48×48 pixel raster; final backend suite passes.

No scientific catalogues, uncertainties, or classifications were changed to make tests pass.

## Failures / incomplete checks

- The complete combined automated suite passed **16/16**. The UI was smoke-tested with Streamlit `AppTest` and browser checks; those are not part of pytest.
- Browser developer-console logs were not available through the active in-app browser interface. The visible app rendered without an error banner after fixes, and the Streamlit process remained active; this is not equivalent to a captured zero-error browser console report.
- Valid observation ingestion was not exercised: creating a valid ingestion fixture would require adding a made-up observation, which would violate the scientific data safeguard. The route's missing-body validation returns 422. The scientist validation route's missing-body validation returns 422; successful triage writes were not exercised to avoid changing temporary review state.
- Gaia DR3 and JPL Horizons are not queried by this temporary app. External validation remains incomplete.

## Scientific limitations

- Three small cutouts are the only observations loaded, not a sky-wide SPHEREx archive.
- The common rectangular grid is 60×62, of which 2,259 pixels (60.7%, approximately 0.00659 deg²) have valid coverage in all three epochs. Other pixels are masked.
- Reprojection has already interpolated the source images. Interpolation covariance is omitted from the empirical photometric errors; the alignment does not independently calibrate astrometric residuals.
- The available source measurement is a preliminary uncorrected aperture sum. It is not PSF/aperture corrected or absolutely calibrated. Band and wavelength mapping are unavailable and shown as null.
- The 19 rows are epoch detections, not 19 validated astronomical objects. The two historical candidate associations remain preliminary and are not confirmed moving objects.

## Remaining developer work

- Independently validate astrometric calibration and PSF/aperture photometry, including correlated interpolation uncertainties.
- Complete genuine Gaia DR3 and Solar System object cross-matching; retain query provenance.
- Resolve observation band/wavelength and calibration metadata from authoritative products.
- Replace temporary local file loading with the backend deployment's configured scientific-data store and define durable metadata/version contracts.
- Add browser automation and console capture; add input validation/accessibility and failure-state tests; assess image performance at larger field sizes.
- Integrate only after the teammates review the needed API model and UI changes; this temporary build has not altered their repositories.
