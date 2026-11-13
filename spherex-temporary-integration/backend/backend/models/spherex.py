"""
SPHEREx Spectral Band Constants and Observation Data Models.

Defines the 6 spectral channels of the SPHEREx mission, resolving power specifications,
data-quality bitmasks, and raw/calibrated observation records.
"""

from datetime import datetime
from enum import Enum, IntFlag
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SPHERExBand(str, Enum):
    """The six discrete spectral channels of the SPHEREx all-sky survey."""
    BAND_1 = "BAND_1"  # 0.75 - 1.11 um (R = 39)
    BAND_2 = "BAND_2"  # 1.11 - 1.64 um (R = 41)
    BAND_3 = "BAND_3"  # 1.64 - 2.42 um (R = 41)
    BAND_4 = "BAND_4"  # 2.42 - 3.82 um (R = 35) - H2O Ice absorption at ~3.0 um
    BAND_5 = "BAND_5"  # 3.82 - 4.42 um (R = 112) - CO2 Ice absorption at ~4.27 um
    BAND_6 = "BAND_6"  # 4.42 - 5.00 um (R = 128) - CO Ice absorption at ~4.67 um


class BandConfig(BaseModel):
    """Detailed specifications for each SPHEREx band."""
    band: SPHERExBand
    wavelength_min_um: float
    wavelength_max_um: float
    wavelength_center_um: float
    resolving_power: int
    primary_diagnostic: str


SPHEREX_BANDS_METADATA: Dict[SPHERExBand, BandConfig] = {
    SPHERExBand.BAND_1: BandConfig(
        band=SPHERExBand.BAND_1,
        wavelength_min_um=0.75,
        wavelength_max_um=1.11,
        wavelength_center_um=0.93,
        resolving_power=39,
        primary_diagnostic="Visible & NIR stellar and galaxy light; redshifted rest-frame visible emission",
    ),
    SPHERExBand.BAND_2: BandConfig(
        band=SPHERExBand.BAND_2,
        wavelength_min_um=1.11,
        wavelength_max_um=1.64,
        wavelength_center_um=1.375,
        resolving_power=41,
        primary_diagnostic="Stellar SED continuum characterization and Milky Way galactic structure",
    ),
    SPHERExBand.BAND_3: BandConfig(
        band=SPHERExBand.BAND_3,
        wavelength_min_um=1.64,
        wavelength_max_um=2.42,
        wavelength_center_um=2.03,
        resolving_power=41,
        primary_diagnostic="Cosmic Infrared Background (CIB) fluctuations and galaxy photometric redshifts",
    ),
    SPHERExBand.BAND_4: BandConfig(
        band=SPHERExBand.BAND_4,
        wavelength_min_um=2.42,
        wavelength_max_um=3.82,
        wavelength_center_um=3.12,
        resolving_power=35,
        primary_diagnostic="Molecular and interstellar water-ice (H2O) broad absorption feature near 3.0 um",
    ),
    SPHERExBand.BAND_5: BandConfig(
        band=SPHERExBand.BAND_5,
        wavelength_min_um=3.82,
        wavelength_max_um=4.42,
        wavelength_center_um=4.12,
        resolving_power=112,
        primary_diagnostic="High-detail carbon dioxide (CO2) ice absorption feature near 4.27 um",
    ),
    SPHERExBand.BAND_6: BandConfig(
        band=SPHERExBand.BAND_6,
        wavelength_min_um=4.42,
        wavelength_max_um=5.00,
        wavelength_center_um=4.71,
        resolving_power=128,
        primary_diagnostic="Maximum resolution carbon monoxide (CO) ice absorption feature near 4.67 um",
    ),
}


class QualityFlagBitmask(IntFlag):
    """Bitmask for detector and observation quality indicators."""
    CLEAN = 0
    BAD_PIXEL = 1 << 0          # Bit 0: Dead or hot detector pixel
    COSMIC_RAY = 1 << 1         # Bit 1: Cosmic ray hit detected
    SATURATED = 1 << 2          # Bit 2: Saturated pixel within PSF core
    EDGE_PROXIMITY = 1 << 3     # Bit 3: Source < 15px from detector boundary
    HIGH_JITTER = 1 << 4        # Bit 4: Spacecraft pointing jitter exceeded tolerance
    STRAY_LIGHT = 1 << 5        # Bit 5: Earth limb or solar stray light contamination


def decode_quality_flags(flags: int) -> List[str]:
    """Converts a bitmask integer into human-readable indicator strings."""
    if flags == 0:
        return ["nominal", "clean"]
    indicators = []
    if flags & QualityFlagBitmask.BAD_PIXEL:
        indicators.append("bad_pixel")
    if flags & QualityFlagBitmask.COSMIC_RAY:
        indicators.append("cosmic_ray")
    if flags & QualityFlagBitmask.SATURATED:
        indicators.append("saturated")
    if flags & QualityFlagBitmask.EDGE_PROXIMITY:
        indicators.append("edge_proximity")
    if flags & QualityFlagBitmask.HIGH_JITTER:
        indicators.append("high_jitter")
    if flags & QualityFlagBitmask.STRAY_LIGHT:
        indicators.append("stray_light")
    return indicators


class WCSMetadata(BaseModel):
    """Complete celestial WCS summary; the full header preserves matrix/distortion terms."""
    crval1: Optional[float] = Field(default=None, description="Reference longitude in degrees")
    crval2: Optional[float] = Field(default=None, description="Reference latitude in degrees")
    crpix1: Optional[float] = Field(default=None, description="Reference pixel X index")
    crpix2: Optional[float] = Field(default=None, description="Reference pixel Y index")
    cdelt1: Optional[float] = Field(default=None, description="Not populated when the full matrix is used")
    cdelt2: Optional[float] = Field(default=None, description="Not populated when the full matrix is used")
    ctype1: str = Field(default="RA---TAN", description="Coordinate projection type RA")
    ctype2: str = Field(default="DEC--TAN", description="Coordinate projection type Dec")
    radesys: Optional[str] = None
    pixel_scale_matrix_deg_per_pixel: List[List[float]] = Field(default_factory=list)
    full_header: Dict[str, Any] = Field(default_factory=dict, description="Complete serialized celestial WCS, including SIP when present")


class SourceMeasurement(BaseModel):
    """A single source detection within an observation."""
    source_id: str
    pixel_x: float
    pixel_y: float
    ra_deg: float
    dec_deg: float
    positional_uncertainty_arcsec: Optional[float] = None
    flux_density_mjy: Optional[float] = None
    flux_uncertainty_mjy: Optional[float] = None
    snr: Optional[float] = None
    peak_MJy_sr: Optional[float] = None
    aperture_sum_MJy_sr_pixel: Optional[float] = None
    aperture_sum_unc_MJy_sr_pixel: Optional[float] = None
    flux_Jy_uncorrected: Optional[float] = None
    flux_unc_Jy_empirical: Optional[float] = None
    snr_aperture: Optional[float] = None
    input_unit: Optional[str] = None
    measurement_method: Optional[str] = None
    quality_note: Optional[str] = None
    quality_flags: int = 0


class ObservationRecord(BaseModel):
    """
    Complete observation record conforming to SPHEREx backend requirements:
    - Observation image reference
    - Observation timestamp (UTC & MJD)
    - WCS metadata
    - Wavelength information (band, central wavelength)
    - Source coordinates & uncertainties
    - Data quality flags
    - Calibration & metadata
    """
    observation_id: str = Field(..., description="Unique frame exposure identifier")
    timestamp_utc: datetime = Field(..., description="UTC timestamp of the observation")
    timestamp_mjd: float = Field(..., description="Modified Julian Date (JD - 2400000.5)")
    band: Optional[SPHERExBand] = Field(default=None, description="Null when the provided metadata does not establish a band mapping")
    wavelength_center_um: Optional[float] = Field(default=None, description="Unavailable until a validated band mapping exists")
    exposure_time_sec: Optional[float] = Field(default=None, description="Unavailable in the copied cutout metadata")
    wcs: WCSMetadata = Field(..., description="World Coordinate System metadata")
    quality_flags: int = Field(default=0, description="Observation-level quality flag bitmask")
    zeropoint_mag: Optional[float] = Field(default=None, description="Unavailable; no absolute calibration is claimed")
    background_rms: Optional[float] = Field(default=None, description="Empirical pre-alignment cutout background RMS")
    background_rms_unit: Optional[str] = None
    background_rms_scope: Optional[str] = None
    detector_label: Optional[str] = None
    source_fits_original: Optional[str] = None
    processed_fits: Optional[str] = None
    bunit: Optional[str] = None
    coverage_fraction: Optional[float] = None
    valid_pixel_count: Optional[int] = None
    valid_sky_area_sqdeg: Optional[float] = None
    pixel_scale_matrix_deg_per_pixel: List[List[float]] = Field(default_factory=list)
    provenance_status: str = "provisional"
    sources: List[SourceMeasurement] = Field(default_factory=list, description="Extracted sources in frame")
    image_uri: Optional[str] = Field(default=None, description="Path or URI to observation image array")
