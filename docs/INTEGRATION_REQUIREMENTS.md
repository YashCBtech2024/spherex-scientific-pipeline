# SPHEREx Teammate Repositories: Integration Requirements

**Inspection basis:** backend `Arnyz17/spherex-backend` commit `dd39b96`; frontend `shrutiprasad925-pixel/spherex-frontend` commit `ef544a1`. Read-only reference clones are in `reference_repos/`. The teammate repositories were not edited. This document describes the inspected code and declared contracts; it does not certify scientific validity or production readiness.

## Summary

The teammate projects provide a FastAPI service and a Streamlit candidate dashboard/detail viewer. The frontend already calls the backend candidate list and detail routes and can show epoch thumbnails. It does not yet explore observation records or fetch cutouts itself.

The backend models support observation and candidate data, but current runtime data is an in-memory synthetic seed catalogue. Its observation cutout route returns a generated Gaussian PNG, not a cutout from the requested FITS observation. The current integration work must therefore supply traceable science products and connect them through existing models/routes or an import mechanism behind the existing API. Do not pass the synthetic data off as measurements from the project FITS files.

## Existing backend capabilities

The backend uses FastAPI, Pydantic models, and an in-memory repository. Its main code is under `backend/`.

- Candidate listing supports filtering, coordinate cone search, and pagination.
- Candidate detail returns multi-epoch measurements, a six-band spectrum, ice-feature fields, and image thumbnails.
- Candidate validation status and notes can be changed through a POST route.
- Observation records can be listed, retrieved by ID, and added in memory.
- An observation cutout route accepts sky coordinates and size, then returns a base64 PNG data URI.
- Spectral band and ice diagnostic metadata are exposed.
- `/docs` and `/redoc` are configured for interactive API documentation; health routes are also present.

**Runtime limitations found in source:** `backend/db/repository.py` initializes from `generate_seed_catalog()`, which creates seven synthetic examples. The repository is in memory and is reset on restart. `POST /observations/ingest` stores only an `ObservationRecord` in that process. There is no candidate ingestion endpoint. `CutoutGenerator` synthesizes a Gaussian point source, and `GET /observations/{id}/cutout` calls that generator regardless of requested RA/Dec; it does not open `image_uri` or the FITS file. Thus, the route shape exists, but real observation ingestion and cutout delivery do not.

The code defines six broad `BAND_1`…`BAND_6` enum values. These should not be confused with the mission's 102 spectral channels or treated as the same data product without a mapping decision. The current project workspace's raw files are FITS images/cubes with WCS and multiple HDUs; the backend observation model does not carry the complete FITS header or arbitrary SIP/CD distortion terms.

## Existing frontend capabilities

The frontend is a Streamlit application (`app.py`, `pages/overview.py`, `pages/detail.py`) with shared helpers in `common.py`.

- Overview dashboard: candidate metrics, class/status filters, a candidate sky distribution plot, significance charts, a catalogue table, and CSV export.
- Candidate gallery links into candidate detail views.
- Detail page: candidate measurements, spectrum and ice features, observation epochs, thumbnails, side-by-side image comparison, blink and difference views, and the displayed validation status. The inspected frontend does not submit status updates to the backend.
- The coordinate cone filter is currently computed client-side against the already fetched candidate list; it is not an observation image search.
- The frontend fetches the first 100 candidates (`page=1&page_size=100`). It does not follow pagination beyond that page.
- It does not currently call observation-list, observation-detail, cutout, spectral-band, ice-diagnostics, or candidate-validation routes. Its main API data path is health + candidate list + candidate detail.

The UI contains generated decorative/class artwork. These assets are not SPHEREx observation data. The README and overview page disclose that the present backend catalogue is synthetic; preserve that disclosure until real data is wired in.

## Exact backend API contracts

Base URL is the service origin, e.g. `http://127.0.0.1:8000`. The paths below are implemented in the inspected backend source.

### Health and service information

| Method and path | Request | Response |
|---|---|---|
| `GET /` | None | Object with `mission`, `launch_date`, `objective`, `status`, `bands_count`, `indexed_candidates_count`, `indexed_observations_count`, `docs_url`. |
| `GET /api/v1/health` | None | `{"status":"healthy"}` |

### Observations

| Method and path | Request | Response |
|---|---|---|
| `GET /api/v1/observations` | Optional query: `band` (`BAND_1`…`BAND_6`), `min_date`, `max_date` (ISO datetimes) | JSON array of `ObservationRecord`. |
| `GET /api/v1/observations/{observation_id}` | Path ID | One `ObservationRecord`; 404 if absent. |
| `GET /api/v1/observations/{observation_id}/cutout` | Required `ra` and `dec` in degrees; optional `size_px` integer, default 48, allowed 16–256 | `CutoutResponse`: `observation_id`, `ra`, `dec`, `size_pixels`, `data_uri`. The current implementation's `data_uri` is a synthetic PNG data URI. |
| `POST /api/v1/observations/ingest` | JSON `ObservationRecord` | HTTP 201 and the submitted `ObservationRecord`. Stored in memory only. |

`ObservationRecord` fields:

```text
observation_id: string
timestamp_utc: datetime
timestamp_mjd: float
band: "BAND_1" | "BAND_2" | "BAND_3" | "BAND_4" | "BAND_5" | "BAND_6"
wavelength_center_um: float
exposure_time_sec: float
wcs: WCSMetadata
quality_flags: integer (default 0)
zeropoint_mag: float
background_rms: float
sources: SourceMeasurement[] (default [])
image_uri: string | null (default null)
```

`WCSMetadata` requires `crval1`, `crval2`, `crpix1`, `crpix2`, `cdelt1`, `cdelt2`; `ctype1` defaults to `RA---TAN` and `ctype2` to `DEC--TAN`. `SourceMeasurement` requires `source_id`, `pixel_x`, `pixel_y`, `ra_deg`, `dec_deg`, `positional_uncertainty_arcsec`, `flux_density_mjy`, `flux_uncertainty_mjy`, `snr`; `quality_flags` defaults to 0.

The model describes `background_rms` as mJy/sr, but source flux fields as mJy. Units must be checked and explicitly converted before serialization. `image_uri` is only a field; the backend has no route in the inspected source to serve arbitrary files at that URI.

### Candidates

| Method and path | Request | Response |
|---|---|---|
| `GET /api/v1/candidates` | All query parameters optional except defaults: `min_displacement_sigma` float; `min_delta_mag` float; `ice_molecule` string (intended H2O/CO2/CO); `validation_status` enum; `category` enum; `ra` float 0–360; `dec` float −90–90; `radius_arcmin` float >0; `page` integer ≥1 default 1; `page_size` integer 1–100 default 20. | `CandidateListResponse`: `total`, `page`, `page_size`, `items: CandidateSummary[]`. For cone search, provide the center coordinates and radius together. |
| `GET /api/v1/candidates/{candidate_id}` | Path ID | `CandidateDetail`; 404 if absent. |
| `POST /api/v1/candidates/{candidate_id}/validate` | JSON `{"validation_status": enum, "user_notes": string|null}` | Updated `CandidateDetail`; 404 if absent. |

`ValidationStatus` values are `Plausible Candidate`, `Confirmed`, `Inconclusive`, `Likely Artifact`. `ScientificCategory` values are `High Proper Motion Star`, `Photometric Transient / Variable Star`, `Interstellar H2O Ice Feature`, `Circumstellar CO2 Ice Feature`, `Dense Core CO Ice Feature`, `Quiescent Galaxy SED`, `Detector Artifact / Spike`.

`CandidateSummary` requires:

```text
candidate_id: string; ra: float; dec: float
observation_dates: datetime[]; bands_observed: SPHERExBand[]
displacement_arcsec: float; displacement_uncertainty_arcsec: float
displacement_significance_sigma: float
delta_brightness_mag: float; delta_brightness_uncertainty_mag: float
delta_brightness_significance_sigma: float
quality_indicators: string[]; has_quality_warnings: boolean (default false)
scientific_interpretation: ScientificCategory; scientific_summary: string
validation_status: ValidationStatus
```

`CandidateDetail` extends the summary with:

```text
epochs: EpochMeasurement[] (default [])
spectrum: SpectralPoint[] (default [])
ice_features: IceAbsorptionFeature[] (default [])
cutout_thumbnails: object mapping string keys to base64/data-URI strings or URLs
user_notes: string (default ""); updated_at: datetime (UTC default)
```

`EpochMeasurement`: `epoch_index`, `observation_id`, `timestamp_utc`, `timestamp_mjd`, `band`, `ra`, `dec`, `flux_density_mjy`, `flux_density_err_mjy`, `magnitude`, `magnitude_err`, `quality_flags: string[]`.

`SpectralPoint`: `wavelength_um`, `flux_density_mjy`, `flux_error_mjy`, `band`, `resolving_power`.

`IceAbsorptionFeature`: `molecule`, `central_wavelength_um`, `equivalent_width_um`, `equivalent_width_uncertainty_um`, `detection_significance_sigma`, `band`, `is_detected`.

### Spectral metadata

| Method and path | Request | Response |
|---|---|---|
| `GET /api/v1/spectral/bands` | None | Object keyed by band enum; each value has `band`, `wavelength_min_um`, `wavelength_max_um`, `wavelength_center_um`, `resolving_power`, `primary_diagnostic`. |
| `GET /api/v1/spectral/ice-diagnostics` | None | Array of objects with `molecule`, `target_band`, `center_um`, `feature_range_um: [float,float]`, `scientific_significance`. |

## Frontend API and image behavior

- `API_URL` is read from the process environment first, then Streamlit secrets, then defaults to `http://127.0.0.1:8000`. This is the only frontend API setting found. The frontend README says to set `API_URL` when the backend is elsewhere.
- Backend source declares no required environment variables. `run_backend.sh` creates/uses a local `venv`, installs its requirements when first run, sets `PYTHONPATH=.`, and starts Uvicorn on port 8000. Do not run this setup script as part of this integration audit.
- Backend CORS currently allows all origins, methods, and headers.
- Detail thumbnails are expected under keys such as `epoch_1` and `epoch_2`. The frontend accepts either a raw base64 value or a `data:` URI, strips the data-URI prefix, base64-decodes it, and passes resulting bytes to Streamlit image display/PIL comparison. Backend generated data URIs use `data:image/png;base64,...`; PNG is therefore the currently implemented thumbnail format. The cutout route returns a field named `data_uri`, distinct from `cutout_thumbnails`.
- Candidate thumbnails can also be URLs by model description, but the inspected frontend decoder treats values as base64/data-URI, not remote URLs. Use PNG data URIs/base64 for the existing frontend integration unless its owners extend that behavior.
- The cutout generator outputs 128×128 PNG previews after stretching and resizing, regardless of input size. These are display products, not science arrays. A FITS image is not directly accepted by the frontend's current thumbnail decoder.
- Frontend dependencies: Streamlit, pandas, Plotly, Requests, NumPy, Pillow (minimum versions in `reference_repos/spherex-frontend/requirements.txt`). Backend dependencies: FastAPI, Uvicorn, Pydantic, NumPy, SciPy, Astropy, Pillow, HTTPX, pytest (minimum versions in `reference_repos/spherex-backend/requirements.txt`).

## Scientific workspace comparison and required formats

The workspace has four FITS observations under `data/raw/`, preliminary CSV catalogues under `data/catalogues/`, epoch metadata JSON under `data/processed/`, and external-query artifacts under `data/external/`. The master catalogue columns include `id`, pixel centroid and DAOFind fields, `peak`, `flux`, `mag`, `RA_deg`, `Dec_deg`, `Epoch`, and `Image`. FITS headers include observation metadata and WCS; inspected files use TAN-SIP distortion and have image, flags, variance, zodiacal-light, PSF, and wavelength-related HDUs. The science workspace has no current exporter that emits the backend Pydantic records or frontend thumbnails from these files.

For the current backend contract, a first adapter would need to emit:

1. `ObservationRecord` JSON per observation, with UTC timestamp and MJD, a defined band mapping, exposure/calibration metadata, WCS, quality, and an `image_uri` understood by the deployment.
2. `SourceMeasurement` JSON entries for measured sources, including honest uncertainties, SNR, and quality bits.
3. `CandidateSummary` and `CandidateDetail` records for cross-epoch associations, including measurements, uncertainty, provenance/notes, and status. The current API has no route to ingest candidates, so the backend owner must provide an import/seed-loading path or another agreed data-loading mechanism **without changing the public API contract**.
4. PNG thumbnails (or data URIs) generated from actual FITS planes for the current detail-page thumbnail fields. Keep original FITS files intact and retain a link to their provenance.

Do not map the current catalogue's `flux` column directly to `flux_density_mjy`: historical documentation describes image units as MJy or MJy/sr in different places and describes the catalogue flux as integrated flux. Resolve the actual unit/calibration and apply pixel solid angle / calibration as scientifically appropriate before conversion. Similarly, backend `WCSMetadata` only carries a simplified TAN/CDelt representation; it cannot encode this workspace's full CD/PC matrix and SIP distortion. Do not discard distortion and call the resulting coordinates equivalent. Preserve the full FITS WCS and define/document the display cutout reprojection or a compatible metadata extension with the backend team before relying on sub-arcsecond positions.

The backend's candidate enums include categories that do not include “unclassified” or “preliminary association.” The two workspace associations are not confirmed moving objects, and Gaia provenance/Solar System matching remain unverified. A safe mapping may use `Inconclusive` and a cautious scientific summary if evidence supports that enum; do not force an unsupported class or `Confirmed` status. Coordinate the precise representation with the backend/frontend teammates.

## Missing integration components

1. **Real FITS cutout implementation:** backend route currently returns synthetic pixels and ignores requested sky position for image generation.
2. **Observation discovery in frontend:** no UI path currently calls observation routes, chooses a coordinate region/date, or blinks observations by ID.
3. **Scientific product adapter:** no reproducible transform from FITS/CSV analysis outputs into the backend's observation/source/candidate JSON models.
4. **Candidate loading/persistence:** no public candidate ingestion route; repository is in-memory seed data and validation edits are not durable.
5. **Schema/unit mapping:** workspace flux, uncertainties, background units, six band enum, and 102-channel mission data need explicit mappings and provenance. FITS SIP/CD WCS is richer than backend WCS model.
6. **Image delivery path:** `image_uri` does not have a serving implementation. Deployment must make observation/cutout bytes reachable without exposing arbitrary local paths.
7. **Pagination and server-side discovery:** frontend requests only the first 100 candidate rows and performs cone filtering locally. Observation query filters exist in backend but are unused by frontend.
8. **Status vocabulary and confidence:** API status/category enums and frontend displays need an evidence-safe representation for preliminary or unverified workspace sources.
9. **Environment/deployment configuration:** frontend supports `API_URL`; deployment CORS must be set safely for actual frontend origins when deployed. No backend environment/config contract is currently declared.
10. **Tests and integration fixture:** the repositories have backend API/service tests, but the scientific workspace lacks substantive tests and no shared real-data integration fixture currently proves schema compatibility.

## Recommended integration workflow

1. Pin and record teammate repository revisions; continue treating those repositories as authoritative for public routes and frontend behavior. Do not fork their code into the science workspace or make uncoordinated contract changes.
2. Agree with backend/frontend owners on units, band mapping, WCS fidelity, image storage/URI strategy, candidate import mechanism, and how “preliminary/unverified” status should appear. Keep model/public route contracts fixed unless the owners explicitly revise them together.
3. Create an exporter/adapter in the scientific workspace that reads existing FITS/CSV inputs without altering them and writes versioned JSON products plus image previews into a new derived-data location. Include input filenames/checksums, processing version, units, uncertainties, and evidence status in a manifest.
4. Start with one observation and one small cutout centered on a known workspace coordinate. Confirm WCS round-trip, pixel scale/distortion treatment, selected HDUs, display stretch, PNG output, and backend schema validation before processing more epochs.
5. Load the generated observation and sources through `POST /api/v1/observations/ingest` only in an isolated backend instance. Use the agreed backend-side candidate loader for candidates; do not alter API routes or place real candidates into the synthetic seed set without clear separation and labels.
6. Test the actual frontend against that isolated instance using `API_URL`. Verify real thumbnails, coordinates, epochs, units, confidence labels, candidate details, and refresh/restart behavior.
7. After the test region passes review, scale to the three observations and then expand data coverage with versioned processing, persistence, storage, pagination, and operational monitoring.

## Recommended first scientific processing task

Implement a **single-observation, WCS-faithful FITS cutout and metadata exporter** for the May 2025 test observation, centered on the project's stated test region. Start here because the first user journey is coordinate-to-image discovery and epoch comparison, and because the backend's existing cutout route currently returns synthetic pixels. The exporter should preserve source FITS files, select and document the correct image/variance/flags/wavelength HDUs, retain full TAN-SIP/CD WCS in its sidecar metadata, generate one real PNG preview for the frontend, and record units and provenance. Do not generate or classify new candidate detections in this first task. Validate the serialized observation metadata against the existing `ObservationRecord` contract and explicitly document any information the current simplified WCS model cannot carry; use an agreed non-breaking import/storage path before wiring it to the backend.
