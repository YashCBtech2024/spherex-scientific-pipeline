# SPHEREx Scientific Context & Empirical Findings

## 1. Mission & Instrument Context
NASA's SPHEREx (Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer) maps the sky in 102 near-infrared spectral channels (0.75 – 5.0 µm) using 6 detector arrays with Linear Variable Filters (LVF).
- **Detector 1 (`D1`)**: Covers Band 1 (~0.75 – 1.15 µm).
- **Pixel Scale**: $\approx 6.24$ arcseconds/pixel (derived from header PC matrix: $\sqrt{PC_{1,1}^2 + PC_{1,2}^2} \times 3600''/\text{deg}$).

---

## 2. Verified Observations Analyzed

| Epoch | FITS File | Observation UTC | MJD | WCS Center (RA, Dec) | Dimensions | Detector |
|---|---|---|---|---|---|---|
| **Epoch 1 (April 2025)** | `level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits` | 2025-04-25 00:42:57 | 60790.030 | (151.8132°, +2.8250°) | 58 × 59 px | Band 1 (D1) |
| **Epoch 2 (May 2025)** | `level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits` | 2025-05-09 03:53:15 | 60804.162 | (151.8154°, +2.8243°) | 58 × 59 px | Band 1 (D1) |
| **Epoch 3 (May 2026)** | `level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits` | 2026-05-26 08:40:11 | 61186.361 | (151.9666°, +2.6617°) | 175 × 176 px | Band 1 (D1) |

- **Baseline Epoch 1 → Epoch 2**: 14.132 days (0.0387 years).
- **Baseline Epoch 2 → Epoch 3**: 382.199 days (1.0464 years).

---

## 3. Master 51-Source Detection Catalogue Breakdown
The historical detection catalogue (`source_detections_51_catalogue.csv`) contains **51 sources** identified using DAOFind PSF fitting across the three observation epochs:
- **April 2025**: 3 detections (IDs 1 to 3)
- **May 2025**: 6 detections (IDs 1 to 6)
- **May 2026**: 42 detections (IDs 1 to 42, detected across the wider 175 × 176 cutout)

---

## 4. Scientific Audit of the Two Candidate Associations

The two preliminary candidate associations between May 2025 and May 2026 (`may2025_may2026_candidate_associations.csv`) have been evaluated:

### Candidate Association 1: May 2025 Source #4 $\rightarrow$ May 2026 Source #23
- **Coordinates (May 2025)**: $\text{RA} = 151.786148^\circ$, $\text{Dec} = +2.831860^\circ$
- **Coordinates (May 2026)**: $\text{RA} = 151.786030^\circ$, $\text{Dec} = +2.831894^\circ$
- **Positional Separation**: $0.4440''$ (444.0 milliarcseconds)
- **Baseline**: 382.20 days
- **Apparent Motion Rate**: $0.001162''/\text{day}$ ($\approx 424.3\text{ mas/year}$)
- **Photometry**:
  - May 2025 Flux: **26.125** MJy/sr (Peak: 10.317, Mag: -3.543)
  - May 2026 Flux: **26.172** MJy/sr (Peak: 8.521, Mag: -3.545)
  - Flux Ratio (2026/2025): **1.0018** (matches within 0.18%)

### Candidate Association 2: May 2025 Source #6 $\rightarrow$ May 2026 Source #29
- **Coordinates (May 2025)**: $\text{RA} = 151.762635^\circ$, $\text{Dec} = +2.802392^\circ$
- **Coordinates (May 2026)**: $\text{RA} = 151.762552^\circ$, $\text{Dec} = +2.802395^\circ$
- **Positional Separation**: $0.2996''$ (299.6 milliarcseconds)
- **Baseline**: 382.20 days
- **Apparent Motion Rate**: $0.000784''/\text{day}$ ($\approx 286.3\text{ mas/year}$)
- **Photometry**:
  - May 2025 Flux: **18.924** MJy/sr (Peak: 7.785, Mag: -3.193)
  - May 2026 Flux: **19.505** MJy/sr (Peak: 5.558, Mag: -3.225)
  - Flux Ratio (2026/2025): **1.0307** (matches within 3.07%)

---

## 5. Astrometric & Physical Interpretation
1. **Not Solar System Moving Objects**:
   - Small Solar System bodies (Main-Belt Asteroids, Near-Earth Objects, Centaurs) travel at rates of tens to hundreds of arcseconds *per day*. Over a 382-day baseline, any asteroid would have moved thousands of arcseconds across the sky.
   - The measured motion rate ($<0.0012''/\text{day}$) rules out any Solar System body.
2. **Sub-Pixel Centroid Offsets**:
   - The spatial pixel scale of SPHEREx is $\approx 6.24''/\text{pixel}$.
   - The measured separations of $0.444''$ and $0.300''$ correspond to **$0.071$ pixels** and **$0.048$ pixels** respectively.
   - Centroid shifts below $0.1$ pixels are well within expected single-frame astrometric jitter, pointing re-acquisition uncertainties, and Level 2 pipeline WCS distortion differences between 2025 and 2026 data releases.
3. **Alternative Physical Hypothesis: Stellar Proper Motion**:
   - If the shift is real and astrometrically calibrated against Gaia DR3, proper motions of $286$ to $424\text{ mas/yr}$ correspond to moderate proper motion Galactic dwarf stars.
   - Both sources are bright, steady point sources with flux constancy $>97\%$.
