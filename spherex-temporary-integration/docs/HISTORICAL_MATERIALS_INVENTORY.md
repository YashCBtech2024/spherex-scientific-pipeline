# Historical Project Materials Inventory

This document tracks all files provided from previous SPHEREx project work. Every incoming file is preserved in `archive/historical_raw/` with zero modification, and cataloged here before being copied or linked to the active project modules.

| # | Original Filename / Content | Size / Type | Epoch / Date | Description & Content | Detected Purpose | Target Organized Location | Status |
|---|---|---|---|---|---|---|---|
| 1 | `SpectralImages-curl.sh` | 1.95 KB, Shell Script | Nov 06, 2026 | IRSA SPHEREx download script using `curl`. Targets level-2 FITS: `level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits` (2025 Week 17 D1). | Observation download script | `archive/historical_raw/` & `data/raw/` | Preserved & cataloged |
| 2 | `SpectralImages-curl_-_Copy.sh` (Batch 1) | 1.95 KB, Shell Script | Nov 06, 2026 | Identical copy of `SpectralImages-curl.sh` (SHA-256 matched). | Duplicate copy of download script | `archive/historical_raw/` | Preserved (Duplicate) |
| 3 | `SpectralImages-wget.sh` | 1.97 KB, Shell Script | Nov 06, 2026 | IRSA SPHEREx download script using `wget`. Targets level-2 FITS: `level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits`. | Observation download script | `archive/historical_raw/` & `data/raw/` | Preserved & cataloged |
| 4 | `SpectralImages-wget_-_Copy.sh` | 1.97 KB, Shell Script | Nov 06, 2026 | Identical copy of `SpectralImages-wget.sh` (SHA-256 matched). | Duplicate copy of download script | `archive/historical_raw/` | Preserved (Duplicate) |
| 5 | Text snippet / URL (Batch 1) | Text / URL | Nov 06, 2026 | Direct IRSA download URL for SPHEREx level 2 observation: `2025W17_4B`. | Raw observation source link | `archive/historical_raw/` & inventory | Recorded |
| 6 | `SpectralImages-curl_-_Copy.sh` (Batch 2) | 1.95 KB, Shell Script | Nov 06, 2026 | Third identical duplicate of `SpectralImages-curl.sh` (SHA-256 matched: `7820206D...`). | Duplicate copy of download script | `archive/historical_raw/` | Preserved (Duplicate) |
| 7 | `level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits` | 5.11 MB, FITS Image | 2025 Week 17 (April 2025) | SPHEREx Level-2 D1 calibrated spectral image. | Primary science observation data (Epoch 1) | `archive/historical_raw/` & `data/raw/` | Preserved & organized |
| 8 | `level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits` | 5.11 MB, FITS Image | 2025 Week 19 (May 2025) | SPHEREx Level-2 D1 calibrated spectral image. | Primary science observation data (Epoch 2) | `archive/historical_raw/` & `data/raw/` | Preserved & organized |
| 9 | `source_detections_batch1.csv` | 839 B, CSV table | Detections across epochs 1 & 2 | 10 source detections with RA, Dec, center_flag, local variance (6 in May 2025, 4 in April 2025). | Source detection catalog subset | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 10 | `SpectralImages-url-2025W19_2B.txt` | 215 B, Text | Nov 06, 2026 | Direct IRSA download URL for SPHEREx observation: `2025W19_2B` (Week 19 D1). | Raw observation source link | `archive/historical_raw/` & inventory | Recorded |
| 11 | `spherex_irsa_query_results.vot` (uploaded as `spherex`) | 13.58 KB, VOTable XML | 2026 query | IRSA SIA/IBE VOTable metadata query containing links and S3 bucket keys to SPHEREx Level 2 observations including **May 2026** (`2026W22_1A`). | Observation metadata & cloud download registry | `archive/historical_raw/` & `data/external/` | Preserved & organized |
| 12 | `candidate_motion_associations.csv` | 370 B, CSV table | Multi-epoch matching | The preliminary candidate associations between April & May 2025 (shifts and separation). | Preliminary candidate table | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 13 | `photometry_snr_measurements.csv` | 647 B, CSV table | April & May epochs | Aperture photometry measurements (X, Y, Net_Flux, Flux_Uncertainty, SNR) for 4 April sources and 6 May sources. | Photometric verification catalog | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 14 | `SpectralImages-urls-batch3.txt` | 316 B, Text | Nov 06, 2026 | Download links for `2025W19_2B_0103_1D4` (Detector 4) and `2025W17_4B_0043_1D1`. | Raw observation source links | `archive/historical_raw/` & inventory | Recorded |
| 15 | `level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150.fits` | 5.11 MB, FITS Image | 2026 Week 22 (May 2026) | SPHEREx Level-2 D1 calibrated spectral image (2026 epoch). | Primary science observation data (Epoch 3) | `archive/historical_raw/` & `data/raw/` | Preserved & organized |
| 16 | `level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits` | 5.55 MB, FITS Image | 2026 Week 22 (May 2026) | SPHEREx Level-2 D1 calibrated spectral image with additional extension/header data (2026 epoch). | Primary science observation data (Epoch 3 variant) | `archive/historical_raw/` & `data/raw/` | Preserved & organized |
| 17 | `source_detections_51_catalogue.csv` | 4.9 KB, CSV table | April 2025, May 2025, May 2026 | **The Complete 51-Source Detection Catalogue** (3 April sources, 6 May 2025 sources, 42 May 2026 sources) with centroid, sharpness, roundness, peak, flux, magnitudes, RA, Dec. | Master Source Detection Catalogue | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 18 | `epoch_comparison_crossmatch.csv` | 1.1 KB, CSV table | Multi-epoch | Complete nearest-neighbor cross-match comparison table across all 3 epochs with 2-arcsecond matching threshold and interpretations. | Cross-Epoch Matching Table | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 19 | `may2025_may2026_candidate_associations.csv` | 550 B, CSV table | May 2025 vs May 2026 | **The Two Preliminary Close Source Associations**: (May 2025 #4 <-> May 2026 #23, sep 0.444") and (May 2025 #6 <-> May 2026 #29, sep 0.300") with baseline of 382.2 days and apparent motion rates. | Candidate Associations Table (Pending Calibration) | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |
| 20 | `daofind_detections_10_sources.csv` | 1.8 KB, CSV table | April 2025 & May 2025 | DAOPhot / DAOFind PSF fitting detection parameters for the 10 sources from the first two epochs. | PSF Fitting Photometry Table | `archive/historical_raw/` & `data/catalogues/` | Preserved & organized |

---

## Inventory Intake Summary
- **Total Unique Items / Data Products**: 20 cataloged records.
- **Raw Observations (FITS)**:
  1. `level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits` (April 2025)
  2. `level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits` (May 2025)
  3. `level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150.fits` (May 2026)
  4. `level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150(1).fits` (May 2026 extended)
- **Scientific Catalogues**:
  1. Full **51-source detection catalogue** (`source_detections_51_catalogue.csv`)
  2. Cross-epoch matching table (`epoch_comparison_crossmatch.csv`)
  3. The **2 candidate associations** between May 2025 and May 2026 (`may2025_may2026_candidate_associations.csv`)
  4. DAOFind PSF measurements (`daofind_detections_10_sources.csv`)
  5. Photometry and SNR measurements (`photometry_snr_measurements.csv`)
- **Archival Integrity**: Every single file is preserved unedited in `archive/historical_raw/`.

---

## Historical Inventory Verification (2026-11-07)

Targeted follow-up against the current workspace. No originals were modified, moved, or deleted. The workspace contains no scientific package ZIP, `.ipynb` notebook, or Excel workbook (`.xlsx`, `.xls`, `.xlsm`); therefore none could be opened or verified. These items are **missing from the current workspace** (their existence in earlier external records cannot be established from local files).

### Missing requested materials

| Requested item | Verification result |
|---|---|
| SPHEREx Scientific Data Package ZIP | Not found; cannot inspect archive contents. |
| Previous Jupyter notebooks | No `.ipynb` files found. `notebooks/` contains only `.gitkeep`. |
| Preliminary validation Excel workbook | No `.xlsx`, `.xls`, or `.xlsm` files found. |

### SHA-256 duplicate and copy comparison

Hash comparison covered archive and active FITS, CSV, VOTable, and script materials. For every archived/active counterpart listed below, SHA-256 matched exactly:

- **Four FITS observations:** all four `archive/historical_raw/` copies match the same-named files in `data/raw/` byte-for-byte.
- **Catalogue copies:** `source_detections_batch1.csv`, `source_detections_51_catalogue.csv`, `photometry_snr_measurements.csv`, `may2025_may2026_candidate_associations.csv`, `epoch_comparison_crossmatch.csv`, `daofind_detections_10_sources.csv`, and `candidate_motion_associations.csv` in the archive match their counterparts in `data/catalogues/` byte-for-byte.
- **IRSA VOTable:** `archive/historical_raw/spherex_irsa_query_results.vot` matches `data/external/spherex_irsa_query_results.vot` byte-for-byte.
- **Download scripts:** duplicate curl scripts have SHA-256 `7820206D32C9168EADD90D297F5AC40E11126EF9A0A8DBB8CCDF27CFA8DA3B21`; duplicate wget scripts also hash identically to each other. The inventory's claimed original copy counts cannot all be confirmed: only two curl filenames and one wget filename are currently present in the archive; `SpectralImages-wget_-_Copy.sh` is absent.

The hash scan also found repeated zero-byte `.gitkeep` placeholders; these are empty directory markers, not scientific data duplicates. No different-content variants with identical names were found among the archive/active pairs compared.

### Documentation and inventory corrections

- The earlier table's blanket statement that every historical file is archived is too broad: the ZIP, notebooks, and Excel workbook are absent locally, and the stated wget-copy file is missing.
- The archive contains `spherex_irsa_query_results.vot`; the original table correctly identifies it, while active copy is under `data/external/`.
- The inventory lists 20 catalogued records, but several are duplicate copies/URL snippets, not 20 unique scientific data products. Do not interpret that count as 20 distinct datasets.
- The two differently named May 2026 FITS files are distinct variants: each archive copy matches its same-named active copy, but filenames and sizes differ between variants. Neither was collapsed or treated as a duplicate of the other.
- Previous project conversation records mention expected ZIP/notebook/workbook materials, but no local copies or accessible source records were available to establish filenames, contents, or hashes. Request the missing originals if they are still needed.

### Verification scope and limits

SHA-256 was used for exact byte comparison, not scientific validity. ZIP/notebook/workbook open checks were not applicable because no such files were found. This targeted follow-up did not repeat scientific analyses or alter the earlier scientific records.

---

## Google Colab Historical Intake (2026-11-07)

Intake-only pass per user instruction. Files were copied from `C:\Users\yashc\Downloads` into `archive/historical_raw/`, retaining supplied names. No source file was opened for scientific-content review in this pass; no files in Downloads were modified or deleted.

- **28 supplied filenames accounted for:** 21 newly copied and SHA-256 verified; 6 already existed in the archive with matching SHA-256 and were left in place; 1 duplicate ZIP was not recopied.
- **Duplicate ZIP:** `SphereX_Data.zip` has the same SHA-256 as `SPHEREx_Scientific_Data_Package.zip`. One copy is archived as `SPHEREx_Scientific_Data_Package.zip`; the duplicate filename and identical hash are recorded by this entry.
- **Existing identical archive copies:** the three May 2025/2026 FITS files and `SpectralImages-curl.sh`, `SpectralImages-wget.sh`, and `SpectralImages-urllist.txt` were already archived and matched the Downloads copies by SHA-256.
- All other supplied files were copied under their original filenames. Each new destination's SHA-256 was computed and matched its Downloads source immediately after copying. Any same-name archive collision with differing content was routed into `archive/historical_raw/incoming_colab_20261107/` rather than overwritten.
- Intake includes the supplied two-epoch notebooks, three-epoch and first-pass detection CSVs, source photometry/motion/quality CSVs (including the `(1)` quality copy), validation workbook, scientific package ZIP, PDF, FITS files, VOTable files supplied without extensions, URL lists, and curl/wget scripts.

This entry records preservation and byte-integrity only. Scientific contents, workbook/notebook usability, relationship to active catalogue versions, and missing analysis stages remain for a separate review as requested.
