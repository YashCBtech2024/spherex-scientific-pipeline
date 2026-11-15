# Required Datasets, Scripts, and Dependencies

## 1. Datasets Needed from User / Mission Archives

### A. SPHEREx Observations (FITS files / Spectral cubes)
- **Epoch 1**: April 2025 SPHEREx D1 observation(s)
  - Raw / calibrated level-2 or level-3 FITS images with headers (WCS, exposure time, filter/band index, epoch timestamp).
- **Epoch 2**: May 2025 SPHEREx D1 observation(s)
  - FITS images / spectral data corresponding to the matched region.
- **Epoch 3**: May 2026 SPHEREx D1 observation(s)
  - FITS images / spectral data corresponding to the matched region.

### B. Previous Catalogues & Tables
- **Source Detection Catalogue**: The table containing the **51 detections** (CSV, VOTable, FITS table, or ASCII format).
- **Candidate Association Records**: The preliminary matching records identifying the **2 candidate associations** between May 2025 and May 2026 (coordinates, pixel positions, flux, separation, positional offsets).

### C. Reference Catalogs & External Data (to be fetched via APIs/astroquery)
- **Gaia DR3**: Astrometric reference frame for local WCS solution checks and stellar proper motion filtering.
- **2MASS / AllWISE**: Near-infrared reference photometry and background star identification.
- **Minor Planet Center (MPC) / JPL Horizons / SkyBoT**: Ephemerides for known solar system objects in the target field at the exact SPHEREx observation epochs.

---

## 2. Scientific & Pipeline Scripts

Implemented modules are listed in the repository README and scientific handoff. The following capabilities remain unfinished and must not be treated as completed modules:

1. Independent Gaia-based astrometric refinement and uncertainty estimation.
2. A one-to-one, uncertainty-aware cross-epoch association pipeline.
3. Solar System object identification using successful, reproducible ephemeris queries.

Exploratory scripts from earlier query and audit attempts are preserved under `archive/science_validation/`. They are historical records, not supported pipeline modules or automated tests.

---

## 3. Software Dependencies
- **Python**: 3.10+ (current system environment: Python 3.14).
- **Astropy Ecosystem**:
  - `astropy`: Core astronomy, FITS I/O, coordinates, WCS, units.
  - `photutils`: Source detection (DAOPhot, SourceExtractor algorithms), aperture & PSF photometry.
  - `astroquery`: Automated queries to Gaia, VizieR, JPL Horizons, SkyBoT.
  - `reproject`: Image reprojection and alignment between different observation epochs.
- **Scientific Computing & Plotting**:
  - `numpy`, `scipy`, `pandas`, `matplotlib`.
- **Backend & Web**:
  - `fastapi`, `uvicorn`, `pydantic`: High-performance REST API for serving cutouts, catalog data, and candidate review endpoints.
