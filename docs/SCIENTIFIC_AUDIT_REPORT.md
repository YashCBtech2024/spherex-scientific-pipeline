# SPHEREx Scientific Audit Report

**Status:** Partial; source measurements and external associations remain preliminary.
**Updated:** 2026-11-15

This report supersedes the earlier audit draft. Its Gaia source provenance was not verified, JPL Horizons and SkyBoT checks failed, and its claims of confirmed stars, WCS-caused offsets, flux constancy, and Solar System exclusion are not supported. Do not use those earlier claims as scientific conclusions.

## Current dataset and processing

- Three Level 2 observations were processed for April 25, 2025, May 9, 2025, and May 26, 2026.
- Their images were reprojected onto a shared celestial WCS grid with SIP-aware input coordinate transformations. A common mask marks 2,259 of 3,720 grid pixels (60.73%) as covered by all three inputs.
- Preliminary source detection and aperture photometry produced 5, 7, and 7 detections, respectively. The quoted photometric uncertainties omit covariance from image interpolation and may be too small.
- The alignment is WCS-based and does not include independent source-based astrometric refinement. Residual offsets must not be interpreted as motion.

## Candidate associations

The historical pairs #4→#23 and #6→#29 are unconfirmed positional associations. The table is now named `data/catalogues/candidate_associations_provisional.csv`; its classification fields say **“Unconfirmed; Gaia association unverified.”** Existing numeric entries were preserved and must be treated according to their preliminary provenance.

The saved Gaia rows have unverified query provenance and are not confirmed cross-matches. At most, the reported Gaia associations are consistent with stellar sources. They do not establish candidate identity or classification.

## Photometry and wavelength

The aperture measurements are preliminary and not absolutely calibrated. The three observations are not wavelength-matched; approximate `WCS-WAVE` diagnostics do not replace the recommended `CWAVE`/`CBAND` calibration maps. The plotted epoch measurements are not a source-matched light curve. Cross-epoch flux differences are not evidence of variability.

## Solar System checks

JPL Small-Body Identification queries returned HTTP 400 errors, and the SkyBoT requests failed SSL verification. Neither service supplied usable results. Solar System object identification **and exclusion were not completed**.

## Conclusions and remaining validation

- No candidate is confirmed as a star, variable source, or moving object.
- The two historical associations remain unverified; pointing/WCS residuals and source identity have not been independently resolved.
- External Gaia match provenance and the failed Solar System queries require reproducible follow-up before classifications can be made.
- Wavelength-matched photometry, calibrated fluxes, and realistic uncertainty propagation remain necessary before evaluating variability.

See `docs/EXTERNAL_DATA_VALIDATION_REPORT.md` for the external-query record and `docs/SCIENTIFIC_HANDOFF.md` for measurement limitations and output paths.
