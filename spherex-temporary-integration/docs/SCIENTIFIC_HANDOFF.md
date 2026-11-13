# Scientific Handoff — Three-Epoch SPHEREx Test Field

## Processing products

- Validated inputs: three common-grid FITS files in `data/processed/aligned_validated/`, with shared mask `three_epoch_common_coverage_mask.fits`.
- Common coverage: 2,259 / 3,720 pixels (60.73%); masked values are NaN. Only this area is suitable for direct pixel-grid comparison.
- Detection/photometry implementation: `science/source_analysis.py`; fixed settings: DAOStarFinder FWHM 2.5 px, threshold 5 robust background sigma, circular aperture radius 3 px.
- New per-epoch CSVs and master JSON/CSV are under `data/catalogues/reprocessed/`. Product counts: 5 detections (Apr 2025), 7 (May 2025), 7 (May 2026).
- Overlays and per-epoch photometry plot are in the same directory.

## Measurement interpretation and limits

Images are background-subtracted MJy/sr. Aperture sums are converted to Jy by multiplying by the common-grid pixel solid angle and 1e6; these are uncorrected aperture fluxes, not calibrated total source fluxes. Error estimates use robust empirical image RMS propagated as independent-pixel aperture errors. Bilinear reprojection correlates adjacent pixels, so these errors are likely optimistic; no covariance correction, PSF fit, aperture correction, or absolute photometric calibration was applied. SNR is therefore a preliminary diagnostic.

Astrometry uses each FITS WCS, including SIP at reprojection time, but there is no independent Gaia-based registration/refinement. A shared WCS grid is not evidence that residual pointing errors are zero. Do not infer source motion from small epoch offsets without registration uncertainty.

Historical pair #4→#23 re-evaluation finds nearest new detections at about 0.20 arcsec (May 2025) and 1.01 arcsec (May 2026) from the respective historical positions. Pair #6→#29 has no new detections within 2 arcsec of either recorded historical position (nearest about 135 arcsec). Treat these as uncertain catalogue re-identifications, not classifications or moving-object detections. Historical CSVs are preserved unchanged.

Gaia raw JSON/VOTable artifacts record query errors; saved Gaia CSV rows have unverified provenance. JPL sb_ident artifacts contain HTTP 400 errors and SkyBoT artifacts TLS errors. No new external response was fabricated; external validation remains incomplete.

## Backend integration

Generated measurements provide celestial coordinates, epochs, common-grid source IDs by row, aperture flux/error, SNR and quality caveats. They are **not yet directly serializable** as the teammate `CandidateSummary` contract: that model requires astrometric/photometric displacement uncertainties, significance, enum classification and validation status, and the workspace has not established evidence-backed values for those fields. Do not assign `Confirmed`. The CSV/JSON products can be consumed by a science-side adapter after calibration and cross-epoch identity review. See `INTEGRATION_REQUIREMENTS.md` for API schemas.
