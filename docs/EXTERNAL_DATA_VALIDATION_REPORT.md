# Historical External Data-Query Review

## SPHEREx Preliminary Source-Association Checks

**Project:** SPHEREx Multi-Epoch Source Analysis — External Catalogue Review
**Report Date:** 2026-11-07  
**Author:** Automated Validation Pipeline  
**Status:** Partial

---

## 1. Executive Summary

This report records earlier exploratory Gaia DR3 and Solar System object query attempts for two preliminary SPHEREx source associations. The provenance linking the saved Gaia rows to the stated query results is unverified. JPL and SkyBoT queries failed, so the Solar System check was not completed.

**Current interpretation:** Gaia cross-match consistent with stars; Solar System check not completed. The Gaia associations are not confirmed identities, and neither candidate is classified. The reported SPHEREx positional offsets have not been independently separated into pointing error and astrophysical motion.

---

## 2. Observation Epochs

| Parameter | Epoch 1 | Epoch 2 |
|---|---|---|
| **Date (UTC)** | 2025-05-09 03:53:15 | 2026-05-26 08:40:11 |
| **MJD** | 60804.162 | 61186.361 |
| **Temporal baseline** | **382.20 days (1.046 years)** | |

---

## 3. Query Targets

| Candidate | SPHEREx RA (°) | SPHEREx Dec (°) |
|---|---|---|
| 1 | 151.786148 | +2.831860 |
| 2 | 151.762635 | +2.802392 |

---

## 4. Gaia DR3 Cross-Match Results

### 4.1 Methodology

The historical analysis record says Gaia DR3 was queried through the IRSA TAP service (`https://irsa.ipac.caltech.edu/TAP/sync`) using ADQL cone searches with a 5″ search radius and requesting astrometry and broadband photometry. The provenance of the saved rows and their linkage to these query parameters have not been independently verified. All Gaia values below are therefore historical, unverified values; they are not validated catalogue matches.

### 4.2 Candidate 1

| Parameter | Value |
|---|---|
| **Gaia source_id** | 3836535238583299072 |
| **Gaia RA** | 151.78611387644° |
| **Gaia Dec** | +2.83176933588° |
| **Separation from SPHEREx** | 0.3444″ |
| **G mag** | 13.3425 |
| **BP mag** | 13.7875 |
| **RP mag** | 12.7341 |
| **Parallax** | 0.7507 ± 0.0175 mas |
| **Distance (1/parallax)** | ≈ 1332 pc |
| **pmRA** | −4.610 ± 0.018 mas yr⁻¹ |
| **pmDec** | −1.938 ± 0.016 mas yr⁻¹ |
| **Total proper motion** | 5.00 mas yr⁻¹ (0.005″ yr⁻¹) |
| **RUWE** | 1.024 |

**Astrometric Displacement Analysis:**

- Expected displacement over 382.2 days (1.046 yr) from Gaia proper motion: **5.23 mas (0.005″)**
- SPHEREx observed displacement between epochs: **444 mas (0.444″)**
- Ratio (observed / expected): **≈ 85×**

**Interpretation (conditional and unverified):** If the reported Gaia row is the correct counterpart, its tabulated proper motion is smaller than the historical SPHEREx offset. This comparison does not establish the source identity or determine the cause of the SPHEREx offset. The reported RUWE is a Gaia catalogue statistic and does not confirm the cross-match or rule out all source complexity. The source is not confirmed as a star by this project.

---

### 4.3 Candidate 2

| Parameter | Value |
|---|---|
| **Gaia source_id** | 3836535096848994688 |
| **Gaia RA** | 151.76259626447° |
| **Gaia Dec** | +2.80232692564° |
| **Separation from SPHEREx** | 0.2721″ |
| **G mag** | 13.585 |
| **BP mag** | 13.9468 |
| **RP mag** | 13.0579 |
| **Parallax** | 2.2257 ± 0.0192 mas |
| **Distance (1/parallax)** | ≈ 449 pc |
| **pmRA** | +11.443 ± 0.020 mas yr⁻¹ |
| **pmDec** | −12.185 ± 0.017 mas yr⁻¹ |
| **Total proper motion** | 16.72 mas yr⁻¹ (0.0167″ yr⁻¹) |
| **RUWE** | 1.105 |

**Astrometric Displacement Analysis:**

- Expected displacement over 382.2 days (1.046 yr) from Gaia proper motion: **17.50 mas (0.0175″)**
- SPHEREx observed displacement between epochs: **300 mas (0.300″)**
- Ratio (observed / expected): **≈ 17×**

**Interpretation (conditional and unverified):** If the reported Gaia row is the correct counterpart, its tabulated proper motion is smaller than the historical SPHEREx offset. The fraction attributed to WCS systematics cannot be established without validated source identity and independent astrometric calibration. The reported RUWE and distance do not confirm this candidate's identity or classification.

---

## 5. Historical Cross-Match Summary (Unverified Values)

| Property | Candidate 1 | Candidate 2 |
|---|---|---|
| **Gaia source_id** | 3836535238583299072 | 3836535096848994688 |
| **Separation** | 0.344″ | 0.272″ |
| **G mag** | 13.34 | 13.59 |
| **Distance** | ≈ 1332 pc | ≈ 449 pc |
| **Total μ** | 5.00 mas yr⁻¹ | 16.72 mas yr⁻¹ |
| **RUWE** | 1.024 | 1.105 |
| **Expected Δ (382d)** | 5.23 mas | 17.50 mas |
| **Observed Δ (SPHEREx)** | 444 mas | 300 mas |
| **Ratio (obs/exp)** | 85× | 17× |
| **Previously claimed WCS attribution** | > 99% (unverified) | ≈ 94% (unverified) |
| **Classification** | Unconfirmed; reported Gaia association has unverified provenance | Unconfirmed; reported Gaia association has unverified provenance |

---

## 6. Solar System Object Search

### 6.1 JPL Small-Body Identification (sb_ident)

**Endpoint:** `https://ssd.jpl.nasa.gov/api/sb_ident.api`  
**Method:** Queries submitted for both candidates at both epochs using sexagesimal coordinates, MPC observatory code 500 (geocentric), and FOV half-widths of 0.1°.

**Result:** All 4 queries returned **HTTP 400 Bad Request** errors. The API did not process our requests.

**Status:** ❌ FAILED

### 6.2 IMCCE SkyBoT

**Endpoint:** `https://vo.imcce.fr/webservices/skybot/`  
**Method:** Cone search queries for both candidates at both epochs.

**Result:** All 4 queries failed with SSL certificate verification error:
```
[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate
```
The Python 3.12.0 runtime on Windows lacked the root CA certificate for `vo.imcce.fr`.

**Status:** ❌ FAILED (SSL verification error; no usable result)

### 6.3 Solar System Status

The earlier claim that Solar System objects were excluded is withdrawn. Failed JPL and SkyBoT requests provided no usable ephemeris matches or non-matches. Because the Gaia match provenance is unverified, the saved Gaia rows cannot substitute for a Solar System search. The Solar System check remains incomplete; no conclusion about Solar System identity is supported by this report.

---

## 7. Data Products

The following files were saved during the validation process:

| File | Description |
|---|---|
| `data/external/gaia_dr3_raw_candidates.csv` | Saved Gaia rows; query-response provenance is unverified |
| `data/external/gaia_dr3_crossmatch_table.csv` | Historical candidate associations; numeric entries retained, classification labels corrected to unconfirmed because query provenance is unverified |
| `data/external/jpl_sb_ident_raw_candidates.json` | JPL sb_ident API error log |
| `data/external/skybot_solar_system_matches.json` | IMCCE SkyBoT error log |

---

## 8. Limitations

1. **JPL sb_ident API failure:** The Small-Body Identification service returned HTTP 400 for all recorded queries. No usable result was obtained; this does not rule objects in or out.

2. **IMCCE SkyBoT SSL failure:** The SkyBoT service could not be contacted because of an SSL certificate verification error. No usable result was obtained; the Solar System check remains incomplete.

3. **Gaia DR3 match provenance:** The saved Gaia rows have not been verified against the original TAP responses. Source IDs, separations, astrometry, photometry, and derived distances in this report are not validated matches and must not be used as confirmed classifications.

4. **SPHEREx astrometry:** No independent astrometric calibration or uncertainty model establishes whether the reported offsets arise from pointing, source matching, or physical motion. Do not infer motion from these offsets.

---

## 9. Conclusions

1. Historical Gaia rows were reported near both candidate positions and are, at most, consistent with stellar sources. Their provenance is unverified, so neither candidate is a confirmed Gaia match or confirmed star.

2. Historical SPHEREx offsets are preliminary and have not been separated into pointing effects and astrophysical motion with independent astrometry. They are not evidence of confirmed motion.

3. The JPL and SkyBoT queries failed. Solar System object identification or exclusion was not completed.

4. Candidate classifications remain unverified. Reproducible Gaia query provenance, astrometric validation, and successful Solar System queries are required before stronger conclusions.

---

*End of External Data Validation Report*
