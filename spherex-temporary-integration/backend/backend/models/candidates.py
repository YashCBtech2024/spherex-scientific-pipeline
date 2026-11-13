"""
Candidate and Source Models for Frontend Presentation and Scientific Validation.

Maps all 9 frontend requirements:
1. Object or candidate ID
2. Sky coordinates
3. Observation dates / timestamps
4. Wavelength or spectral channel
5. Measured displacement or brightness change
6. Measurement uncertainty
7. Data-quality indicators
8. Scientific interpretation
9. Validation status
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.models.spherex import SPHERExBand


class ValidationStatus(str, Enum):
    """Validation workflow statuses for triage and review."""
    PLAUSIBLE_CANDIDATE = "Plausible Candidate"
    CONFIRMED = "Confirmed"
    INCONCLUSIVE = "Inconclusive"
    LIKELY_ARTIFACT = "Likely Artifact"
    PRELIMINARY = "Preliminary / Unverified"


class ScientificCategory(str, Enum):
    """Scientific classifications derived from multi-epoch astrometry, variability, and spectroscopy."""
    HIGH_PROPER_MOTION = "High Proper Motion Star"
    PHOTOMETRIC_TRANSIENT = "Photometric Transient / Variable Star"
    WATER_ICE_ABSORPTION = "Interstellar H2O Ice Feature"
    CO2_ICE_ABSORPTION = "Circumstellar CO2 Ice Feature"
    CO_ICE_ABSORPTION = "Dense Core CO Ice Feature"
    STATIONARY_GALAXY = "Quiescent Galaxy SED"
    SUSPECTED_ARTIFACT = "Detector Artifact / Spike"


class IceAbsorptionFeature(BaseModel):
    """Specific molecular ice absorption detection result."""
    molecule: str = Field(..., description="Molecular formula: H2O, CO2, or CO")
    central_wavelength_um: float = Field(..., description="Expected line center in microns (3.0, 4.27, or 4.67)")
    equivalent_width_um: float = Field(..., description="Integrated equivalent width in microns")
    equivalent_width_uncertainty_um: float = Field(..., description="1-sigma uncertainty")
    detection_significance_sigma: float = Field(..., description="Significance ratio W / sigma_W")
    band: SPHERExBand
    is_detected: bool = Field(..., description="True if detection significance >= 3.0 sigma")


class SpectralPoint(BaseModel):
    """A calibrated photometric measurement in the candidate's spectrum."""
    wavelength_um: float = Field(..., description="Wavelength in microns")
    flux_density_mjy: float = Field(..., description="Monochromatic flux density in milliJanskys")
    flux_error_mjy: float = Field(..., description="1-sigma measurement uncertainty")
    band: SPHERExBand
    resolving_power: int


class CandidateSummary(BaseModel):
    """
    Summary view designed specifically for frontend data tables and candidate feeds.
    Satisfies all 9 frontend requirements.
    """
    candidate_id: str = Field(..., description="Unique source or candidate identifier")
    ra: float = Field(..., description="Right Ascension in degrees (J2000)")
    dec: float = Field(..., description="Declination in degrees (J2000)")
    observation_dates: List[datetime] = Field(default_factory=list, description="Observed timestamps for this detection record")
    bands_observed: List[SPHERExBand] = Field(default_factory=list, description="Empty when band mapping is unavailable")
    
    # Measured displacement & uncertainty
    displacement_arcsec: Optional[float] = Field(default=None, description="Null unless a validated cross-epoch identity and displacement measurement exist")
    displacement_uncertainty_arcsec: Optional[float] = Field(default=None, description="Null when no defensible uncertainty is available")
    displacement_significance_sigma: Optional[float] = Field(default=None, description="Null unless measured from validated astrometric errors")
    
    # Measured brightness change & uncertainty
    delta_brightness_mag: Optional[float] = Field(default=None, description="Null unless a validated multi-epoch photometric comparison exists")
    delta_brightness_uncertainty_mag: Optional[float] = Field(default=None, description="Null when unavailable")
    delta_brightness_significance_sigma: Optional[float] = Field(default=None, description="Null when unavailable")

    # Actual measured single-epoch values are stored separately from conclusions.
    peak_MJy_sr: Optional[float] = None
    aperture_sum_MJy_sr_pixel: Optional[float] = None
    aperture_sum_unc_MJy_sr_pixel: Optional[float] = None
    flux_Jy_uncorrected: Optional[float] = None
    flux_unc_Jy_empirical: Optional[float] = None
    snr_aperture: Optional[float] = None
    measurement_unit: Optional[str] = None
    measurement_method: Optional[str] = None
    measurement_status: str = "preliminary"
    
    # Data quality
    quality_indicators: List[str] = Field(..., description="Data quality tags (e.g. ['nominal', 'clean'])")
    has_quality_warnings: bool = Field(default=False, description="True if unflagged artifacts or edge issues exist")
    
    # Scientific interpretation & Validation
    scientific_interpretation: Optional[ScientificCategory] = Field(default=None, description="Null when no scientifically validated class is available")
    scientific_summary: str = Field(..., description="Human-readable explanation of the scientific evidence")
    validation_status: ValidationStatus = Field(..., description="Current triage / validation state")


class EpochMeasurement(BaseModel):
    """Detailed observation snapshot for a single epoch."""
    epoch_index: int
    observation_id: str
    timestamp_utc: datetime
    timestamp_mjd: float
    band: Optional[SPHERExBand] = None
    ra: float
    dec: float
    flux_density_mjy: Optional[float] = None
    flux_density_err_mjy: Optional[float] = None
    magnitude: Optional[float] = None
    magnitude_err: Optional[float] = None
    quality_flags: List[str] = Field(default_factory=list)
    pixel_x: Optional[float] = None
    pixel_y: Optional[float] = None
    peak_MJy_sr: Optional[float] = None
    aperture_sum_MJy_sr_pixel: Optional[float] = None
    aperture_sum_unc_MJy_sr_pixel: Optional[float] = None
    flux_Jy_uncorrected: Optional[float] = None
    flux_unc_Jy_empirical: Optional[float] = None
    snr_aperture: Optional[float] = None
    unit_input: Optional[str] = None
    quality_note: Optional[str] = None
    association_status: Optional[str] = None
    cross_epoch_matches: List[Dict[str, Any]] = Field(default_factory=list)


class CandidateDetail(CandidateSummary):
    """
    Full detail view for deep candidate inspection and interactive triage.
    Includes full 6-band spectrum, multi-epoch history, and ice feature measurements.
    """
    epochs: List[EpochMeasurement] = Field(default_factory=list, description="Per-epoch measurements")
    spectrum: List[SpectralPoint] = Field(default_factory=list, description="Extracted 6-band spectrum")
    ice_features: List[IceAbsorptionFeature] = Field(default_factory=list, description="Fitted molecular ice bands")
    cutout_thumbnails: Dict[str, str] = Field(
        default_factory=dict, 
        description="Base64 or URL thumbnail map: e.g. {'epoch_0': 'data:image/png;base64,...'}"
    )
    measurement_provenance: Dict[str, Any] = Field(default_factory=dict)
    is_cross_epoch_identity_validated: bool = False
    user_notes: str = Field(default="", description="Scientist verification notes and comments")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationUpdateRequest(BaseModel):
    """Payload sent by the frontend to update a candidate's triage state."""
    validation_status: ValidationStatus
    user_notes: Optional[str] = None
