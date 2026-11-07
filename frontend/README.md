# SPHEREx Observation Viewer Frontend

## Architecture Overview
The frontend will provide a web interface designed for both researchers and citizen scientists to:
1. **Explore SPHEREx Observations**: Browse sky fields observed across multiple epochs (e.g. April 2025, May 2025, May 2026).
2. **Interactive Blink Comparator**: Toggle or animate between epochs to spot positional shifts (proper motion / asteroid orbits) and brightness variations (flaring, pulsators).
3. **Candidate Verification Table**: Review candidate detections (starting with the 51 cataloged sources and 2 candidate associations), inspect cutouts, SNR, lightcurves, and report flags.
4. **Aladin / HiPS Integration**: Overlay reference surveys (DSS, 2MASS, Pan-STARRS, Gaia) for instant context.

## Stack
- Framework: React / Next.js or Vite + React
- Astronomical FITS / Canvas Viewers: Aladin Lite / custom WebGL FITS viewer / Canvas cutout player
- Styling: Tailwind CSS
