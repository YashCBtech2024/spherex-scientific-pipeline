# SPHEREx Scientific Pipeline

Scientific processing contribution for the NASA SPHEREx challenge and its public-facing sky exploration application. This repository contains the reproducible science-side FITS/WCS workflow, three-epoch cutouts and alignment, preliminary source analysis, tests, and integration handoff materials. The teammate applications remain in their separate repositories; this repository does not bundle copies of their code.

## Scientific objective

Build reliable, reusable processing for SPHEREx Level 2 observations that supports coordinate-based exploration, multi-epoch comparison, source measurements, and later integration with the project application. The immediate field is centered at **RA 151.81441452°, Dec +2.82631029°**.

## Observations and data

The test set contains April 25, 2025; May 9, 2025; and May 26, 2026 D1-named observations. Three original FITS observations and historical project materials are included under `data/raw/` and `archive/historical_raw/`. These FITS files are each about 5–5.5 MB; the scientific handoff ZIP is about 13 MB, below GitHub's individual-file limit.

The historical source catalogue contains 51 preliminary detections. This is the number of catalogue entries, not the number of detections scientifically validated. Two close May 2025–May 2026 associations were reported historically; neither is a confirmed moving object. External Gaia/JPL/SkyBoT validation remains incomplete or has unresolved provenance.

## Methodology and current results

- FITS HDU inspection and science-image loading with Astropy.
- Full celestial WCS handling, including TAN-SIP distortion and anisotropic scales.
- Sky cutout extraction, robust background estimation/subtraction, PNG and metadata output.
- Three-epoch common-footprint evaluation and reprojection to a shared TAN grid.
- A strict all-epoch coverage mask: 2,259 of 3,720 grid pixels (60.73%) are common; pixels outside are NaN.
- Preliminary DAOStarFinder detection and circular-aperture photometry on masked aligned data, using identical settings per epoch.
- Provisional sky-coordinate associations and historical candidate reassessment.

The plotted epoch fluxes are per-detection measurements, not a light curve: row indices are not source identities, and the observations have not been matched to a common wavelength/bandpass. Each Level 2 image includes a `WCS-WAVE` alternate wavelength lookup, but it is not read by the photometry calculation. The project now exports approximate per-detection `WCS-WAVE` diagnostics; IRSA recommends its `CWAVE`/`CBAND` calibration maps for scientific analysis, and those maps are not present here. Do not interpret cross-epoch flux differences as variability.

Photometry is an uncorrected aperture measurement converted from MJy/sr using pixel solid angle. Empirical RMS errors assume independent pixels and omit covariance introduced by bilinear interpolation; they may be optimistic. No PSF/aperture correction, absolute photometric calibration, or Gaia-based astrometric refinement has been completed. Shared-grid alignment does not eliminate residual pointing error; do not interpret it as physical source motion.

## Repository layout

| Path | Purpose |
|---|---|
| `science/` | FITS pipeline, WCS alignment, common mask, source analysis and integration exporter |
| `data/raw/` | Original FITS observations |
| `data/processed/` | Individual cutouts, aligned products, masks, metadata and PNG comparisons |
| `data/catalogues/` | Preserved historical tables and new preliminary analysis catalogues |
| `data/integration/` | Integration CSV, provisional JSON examples and manifest |
| `data/external/` | External query artifacts; inspect status/provenance before use |
| `archive/historical_raw/` | Preserved historical materials |
| `tests/` | Automated processing, alignment, coverage, source-analysis and export tests |
| `docs/` | Vision, scientific records, environment, development log and teammate handoffs |
| `SPHEREx_Scientific_Handoff.zip` | Curated handoff bundle with its own inventory and checksum sidecar |

## Setup

Python 3.12 is used. In PowerShell:

```powershell
py -3.12 -m venv .venv312
.venv312\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

The development environment was verified; see [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for the recorded package versions. For this workspace, activate the existing `.venv312` rather than recreating it.

## Reproduce and test

See [docs/RECOVERED_COLAB_WORKFLOW.md](docs/RECOVERED_COLAB_WORKFLOW.md) for the May 2025 cutout command. Reprojection and source analysis entry points and configuration are in `science/alignment.py` and `science/source_analysis.py`; generated products are under `data/processed/aligned_validated/` and `data/catalogues/reprocessed/`.

Run the suite from the repository root:

```powershell
.venv312\Scripts\python.exe -m pytest tests -q
```

Latest recorded software test result: **7 automated tests passed**. These are software checks, not validation of 7 out of the 51 source detections. The 51 detections remain preliminary and have not all been scientifically validated. An earlier full-suite run timed out; the development log records a later completed run with 7 passing tests. See [docs/DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md).

## Application integration

The teammate applications are maintained separately: [backend](https://github.com/YashCBtech2024/Backend) and [frontend](https://github.com/YashCBtech2024/Frontend). This repository does not copy or modify them. Integration exports and exact schema limitations are described in [docs/INTEGRATION_REQUIREMENTS.md](docs/INTEGRATION_REQUIREMENTS.md) and [docs/TEAMMATE_INTEGRATION_HANDOFF.md](docs/TEAMMATE_INTEGRATION_HANDOFF.md).

The current backend requires non-null significance and classification fields that these preliminary outputs cannot scientifically provide. The provisional payload deliberately leaves those values null and is marked incompatible until teammates support preliminary records. Do not promote candidates to confirmed classifications based on these products.

## Limitations

This is a scientific prototype, not a validated all-sky pipeline or production web application. Detection completeness, uncertainties, calibration, external catalogue matches and candidate classifications need further validation. Preserve all original data and distinguish reproducible measurements from preliminary associations.
