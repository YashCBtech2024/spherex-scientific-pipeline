# SPHEREx Sky Explorer: Project Vision and Roadmap

## Purpose

This project is part of a NASA SPHEREx challenge. Its goal is a public-facing web application that makes the mission's observations accessible and easy to explore. SPHEREx maps the entire sky every six months in 102 bands of near-infrared light. Repeated observations can reveal sources that change position or brightness, including asteroids, comets, stars, brown dwarfs, and potentially previously unidentified objects.

The product is an interactive sky exploration application. Scientific processing and candidate analysis provide the trustworthy data and context behind that experience; they are not the end product by themselves.

## Intended user experience

Users should eventually be able to:

1. Explore SPHEREx sky images interactively.
2. Select a sky region using celestial coordinates: right ascension (RA) and declination (Dec).
3. See which observations of that region are available across dates.
4. Switch between epochs and blink images to reveal possible changes.
5. Compare brightness and investigate variable sources.
6. Display detected sources over the image.
7. Investigate possible moving objects.
8. Inspect a source's coordinates, brightness, observation history, and possible catalogue matches.
9. Read candidate classifications with scientifically appropriate confidence and uncertainty.
10. Expand from the initial test region to all available SPHEREx observations.

The interface should work for non-astronomers without obscuring how measurements and classifications were obtained.

## Current scientific test case

- **Observation epochs:** April 25, 2025; May 9, 2025; and approximately May 26, 2026.
- **Detector:** D1 in the existing analyzed observation set.
- **Initial region center:** RA = **151.81441452°**, Dec = **+2.82631029°**.
- **Existing catalogue:** 51 preliminary source detections across the three epochs.
- **Existing associations:** Two close May 2025 to May 2026 associations.

Those associations are **not confirmed moving objects**. Existing reports interpret their small apparent offsets as consistent with astrometric systematics and/or ordinary stellar motion, but the scientific analysis still needs validation, especially for astrometry, photometry, Gaia DR3 matching, and Solar System object cross-matching. Reports and saved files may contain claims or data whose provenance and query outcome need independent checking. Preserve this distinction in code, documentation, and the public interface: a candidate is not a confirmed classification.

## Expected architecture

### Scientific processing

Use Python and appropriate astronomy libraries such as Astropy and Photutils to read FITS data, interpret WCS, detect and measure sources, calibrate astrometry, align observations, associate detections across epochs, and estimate uncertainties. Processing should be modular, reproducible, and explicit about assumptions and provenance.

### Backend

Use FastAPI or another suitable service to provide observation discovery, metadata, source catalogues, image cutouts, and candidate investigation data to the viewer. API choices should support incremental growth from a small validated dataset to a much larger observation collection.

### Frontend and visualization

Build a modern, responsive interactive sky viewer with coordinate-based region selection, observation and epoch controls, image comparison/blinking, source overlays, source details, brightness comparisons, and lightcurves where the data supports them.

### Data storage

Keep original FITS observations intact. Store processed images, catalogues, external reference results, and metadata in clearly separated, documented locations. Record where data came from and how derived products were generated.

## Development principles

- Scientific accuracy comes before visual polish.
- Preserve original astronomical data.
- Never invent detections, catalogue matches, or uncertainties.
- Label verified measurements, preliminary candidates, and unknowns distinctly.
- Make analysis and application components modular and reproducible.
- Plan for the full observation collection, while validating on the current small test set.
- Keep the public interface understandable and accessible to non-astronomers.
- Document scientific methods, software decisions, data provenance, and limitations.

## Current implementation boundary

The workspace currently provides historical FITS and catalogue data, project documentation, standalone validation scripts, and a small set of FITS inspection utilities. The FITS header reader has been exercised on one local observation. The main scientific pipeline, backend service, and interactive frontend are not implemented yet, and there are no substantive automated tests. Required packages are missing from the existing Python 3.12 virtual environment.

The saved Gaia CSV contains two results, but the saved raw JSON is an IRSA query error and a script writes hard-coded rows into files named as raw results. Treat Gaia matches as reported but with unverified saved-query provenance until re-queried. JPL `sb_ident` artifacts contain HTTP 400 errors; SkyBoT artifacts contain TLS certificate failures. A small Horizons test script is not equivalent to a candidate-centered Solar System object search. Do not describe those cross-matches as completed.

## Phased development roadmap

### Phase 1 — Establish a trustworthy baseline

- Inventory observations, headers, catalogues, derived products, and external-query artifacts without altering originals.
- Reconcile documentation against the actual saved data and clarify provenance, units, epoch definitions, and uncertainty assumptions.
- Revalidate the 51-source catalogue and two associations with reproducible scripts.
- Complete and record reliable Gaia DR3, astrometric, photometric, and Solar System cross-match checks.
- Define data schemas and a minimal repeatable workflow for the three test epochs.

**Exit condition:** Results can be regenerated from preserved inputs, and every claim has a traceable method, source, and uncertainty or an explicit “not verified” status.

### Phase 2 — Build the minimum usable science pipeline

- Implement FITS reading and WCS-aware cutouts using established libraries.
- Add repeatable source detection and photometry, retaining measurement uncertainties and provenance.
- Calibrate/check astrometry against a reference catalogue and quantify epoch-to-epoch registration error.
- Match sources across epochs with configurable thresholds and uncertainty-aware candidate status.
- Validate pipeline outputs against the historical catalogue without silently replacing it.

**Exit condition:** The three-epoch test case runs through documented, reproducible steps and emits versioned machine-readable products.

### Phase 3 — Serve a small validated dataset

- Define observation, image, source, measurement, and candidate schemas.
- Implement backend endpoints for observation discovery, metadata, coordinate-based cutouts, catalogues, and source history.
- Add basic operational checks and automated tests around data parsing and API behavior.

**Exit condition:** A client can request the test region and receive consistent observations and source data through a documented API.

### Phase 4 — Deliver the public sky viewer

- Implement coordinate search and a responsive image viewer.
- Add observation/date selection, epoch blinking, source overlays, and source-detail panels.
- Add brightness comparison and lightcurves only where measurements support them.
- Present candidate labels, match provenance, and uncertainty in accessible language.

**Exit condition:** A non-astronomer can explore the test field and understand both the observations and the limits of candidate claims.

### Phase 5 — Scale observation coverage

- Add scalable observation discovery and ingestion across available SPHEREx data.
- Store and serve derived products efficiently, while keeping original data preserved.
- Monitor data quality, processing versions, coverage gaps, and external catalogue refreshes.
- Validate performance and scientific behavior across more fields, epochs, and relevant bands.

**Exit condition:** The application can grow beyond the initial region without changing the meaning or provenance of existing scientific products.

## Continuity rule

Use this document as the durable statement of project purpose and intended direction. When implementation details or preliminary scientific reports conflict with it, preserve the scientific records but clearly mark uncertainty and update the records through traceable corrections. Do not silently convert a preliminary association or failed external query into a confirmed result.
