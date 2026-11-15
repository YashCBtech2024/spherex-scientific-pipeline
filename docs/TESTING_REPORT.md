# SPHEREx Application Testing Report

**Test date:** 2026-11-07  
**Scope:** Teammate backend and frontend in `reference_repos/`, plus comparison with this workspace's validated scientific products. No teammate source files were changed.

## Setup and environment

- Read both repository READMEs and their dependency lists. No API keys or secrets are required. The frontend accepts optional `API_URL`; its default is `http://127.0.0.1:8000`.
- Installed missing packages only in the existing workspace `.venv312`: `httpx` 0.28.1, `httpx2` 2.16.0 (required by installed Starlette's test client), `streamlit` 1.67.0 and `plotly` 7.1.0. Other required imports were present.
- All backend and frontend dependency imports succeeded. `pip check` reported `No broken requirements found.`
- Started the documented Uvicorn backend on port 8000 and Streamlit frontend on port 8501. Both were stopped after testing.

## Results

| Area | Result |
|---|---|
| Workspace scientific tests | **7 passed** (`tests/`, 103.40 s) |
| Backend calculation tests | **6 passed** (`test_differencing.py`, `test_spectral_ice.py`) |
| Live backend API routes | **18/18 checks passed**; details below |
| Frontend overview AppTest | **No Streamlit exceptions**; metrics and search input rendered |
| Frontend candidate-detail AppTest | **No Streamlit exceptions**; metrics, two epoch records, two cutout images, and four comparison tabs rendered |
| Manual epoch switch | **Passed**; selection changed from Epoch 1 to Epoch 2 without an exception |
| Frontend HTTP page | **HTTP 200** from port 8501; backend health returned `healthy` |
| Browser visual/console inspection | **Not completed**; Windows browser URL policy prevented computer-use inspection |

Live API checks covered `GET /`, health, candidate list and filters, cone search, candidate detail, validation update using its existing status, 404 handling, observation list and band filter, observation detail, cutout PNG data URI and PNG signature, six-band metadata, three ice diagnostics, observation ingestion and retrieval, and a 422 invalid-coordinate response. The ingestion check created only an in-memory test record; the backend was restarted afterward to clear it.

The backend's own `test_api.py` did not complete: its first `TestClient` request hung inside Starlette 1.10 / `httpx2`'s synchronous request path. A timed stack trace placed it in `httpx2._client._send_single_request`; no assertion failure was reported. The API was independently exercised successfully over the live server. The pytest run also emitted the existing `pytest-asyncio` loop-scope deprecation warning.

## Scientific and application findings

- The frontend is connected to the backend and renders candidate metrics, spectra with error bars, per-epoch tables, synthetic cutout thumbnails, auto blink, side-by-side, manual switch, and difference tabs. It displays two candidate epochs. No time-versus-flux light-curve plot is implemented; the spectrum is plotted against wavelength.
- The teammate frontend README states its catalogue contains **seven synthetic seed candidates**. The backend API returned seven candidates and seven observations. All observation records were dated 2025-04-15 in the tested response. A cone search at the real project field (RA 151.81441452°, Dec 2.82631029°) returned zero candidates at 5, 10 and 60 arcminutes.
- The workspace's real processed catalogues contain 5, 7 and 7 detections for 2025-04-25, 2025-05-09 and 2026-05-26. They record input image values in MJy/sr and uncorrected aperture fluxes/empirical errors in Jy. These records and dates are not present in the teammate API seed data, which uses mJy candidate/spectral fields and dates from its own examples. Therefore the frontend's rendered values do **not** represent the supplied scientific results.
- `GET /api/v1/observations/{id}/cutout` returns a valid PNG, but `backend/routes/observations.py` builds it with `CutoutGenerator.generate_point_source_array`; it does not read the real FITS or `image_uri`. Candidate thumbnails are also generated seed images. The image-loading workflow works as a demo, not as a real SPHEREx image viewer.
- The detail page's difference view uses direct pixel differences (resizing only when dimensions differ). It does not register images with WCS. The app has no real source overlay integration. Difference features must not be interpreted as motion or variability evidence.
- The API models require non-null measurement uncertainties, significance values, and a `ScientificCategory`. The current real pipeline marks significance/classification as unavailable and exports nulls; it cannot be represented faithfully by these required fields. The UI also formats detail measurements directly as numbers. `Unreviewed` is styled in the frontend but is absent from the backend's `ValidationStatus` enum; `Inconclusive` is available. There is no general provenance field to distinguish measured, provisional, synthetic, or unverified values.
- Streamlit rendered with no exceptions but reported deprecations: `use_container_width` (replace with `width="stretch"`/`"content"`) and `st.components.v1.html` (replace with `st.iframe`). These still rendered during this run.

## Items for teammate developers

1. **Backend:** provide an ingestion path for the actual observation metadata, common-grid FITS/PNG assets, per-epoch source measurements, units, provenance and uncertainty fields. Serve real cutouts from those products rather than generating point-source arrays. Permit unavailable significance/classification values as nullable and include a provisional/unverified state without implying a confirmed class.
2. **Frontend:** connect the image viewer and source overlays to real observations/catalogues; show three actual epochs; add a time-series light curve when measurements support it; handle null values safely and visibly label provisional/synthetic data. Align images on their WCS before offering difference/blink interpretation.
3. **Both:** agree on units (workspace uncorrected fluxes are Jy; inputs are MJy/sr; backend spectrum/epoch fields are mJy), coordinate reference/equinox, observation IDs and provenance schema. Current candidate models lack fields to convey the workspace's specific aperture/interpolation limitations.
4. **Backend tests:** pin a compatible FastAPI/Starlette/test-client combination or repair the `TestClient` setup; current installed versions caused a hanging request. Use a documented Windows command (`py -m uvicorn ...`) alongside the Bash launcher.
5. **Frontend:** update deprecated Streamlit calls before their removal and add automated tests for null/provisional records, real epoch navigation, and image loading failures.

## Changes made during testing

- Installed the missing packages listed above into the existing `.venv312` only.
- No teammate repository code, data, Git history, remotes, or scientific measurements were changed. Both reference repositories were clean at the end of the run. No project code changes were made.
