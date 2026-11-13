"""In-memory API facade over the copied, real SPHEREx science products."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from backend.models.candidates import (
    CandidateDetail, CandidateSummary, EpochMeasurement, ValidationStatus,
    ScientificCategory,
)
from backend.models.spherex import (
    ObservationRecord, SourceMeasurement, WCSMetadata,
)
from backend.services.differencing import compute_angular_separation_arcsec
from backend.services.science_products import EPOCHS, science_products


def _as_utc(value: str | datetime) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


class SPHERExRepository:
    """Serves measured detections as provisional records; never seeds synthetic sources."""

    def __init__(self):
        self._observations: Dict[str, ObservationRecord] = {
            item["observation_id"]: self._make_observation(epoch)
            for epoch, item in science_products.epochs.items()
        }
        self._candidates: Dict[str, CandidateDetail] = {}
        self._detection_to_epoch: Dict[str, str] = {}
        for epoch in EPOCHS:
            for source in science_products.epochs[epoch]["sources"]:
                record = self._make_detection(epoch, source)
                self._candidates[record.candidate_id] = record
                self._detection_to_epoch[record.candidate_id] = epoch

    @staticmethod
    def _make_observation(epoch: str) -> ObservationRecord:
        item = science_products.epochs[epoch]
        w = item["wcs"]
        wcs = WCSMetadata(
            crval1=float(w.wcs.crval[0]), crval2=float(w.wcs.crval[1]),
            crpix1=float(w.wcs.crpix[0]), crpix2=float(w.wcs.crpix[1]),
            ctype1=str(w.wcs.ctype[0]), ctype2=str(w.wcs.ctype[1]),
            radesys=str(w.wcs.radesys or "ICRS"),
            pixel_scale_matrix_deg_per_pixel=w.pixel_scale_matrix.tolist(),
            full_header=item["wcs_header"],
        )
        sources = [SourceMeasurement(
            source_id=s["source_id"], pixel_x=s["pixel_x"], pixel_y=s["pixel_y"],
            ra_deg=s["ra_deg"], dec_deg=s["dec_deg"], positional_uncertainty_arcsec=None,
            flux_density_mjy=None, flux_uncertainty_mjy=None, snr=None,
            peak_MJy_sr=s["peak_MJy_sr"],
            aperture_sum_MJy_sr_pixel=s["aperture_sum_MJy_sr_pixel"],
            aperture_sum_unc_MJy_sr_pixel=s["aperture_sum_unc_MJy_sr_pixel"],
            flux_Jy_uncorrected=s["flux_Jy_uncorrected"],
            flux_unc_Jy_empirical=s["flux_unc_Jy_empirical"],
            snr_aperture=s["snr_aperture"], input_unit=s["unit_input"],
            measurement_method="3-pixel-radius aperture sum; empirical image RMS error",
            quality_note=s["quality"],
        ) for s in item["sources"]]
        return ObservationRecord(
            observation_id=item["observation_id"],
            timestamp_utc=_as_utc(item["timestamp_utc"]), timestamp_mjd=item["timestamp_mjd"],
            band=None, wavelength_center_um=None, exposure_time_sec=None, wcs=wcs,
            quality_flags=0, zeropoint_mag=None,
            background_rms=item["background_rms_MJy_sr"], background_rms_unit="MJy / sr",
            background_rms_scope=item["background_rms_scope"], detector_label=item["detector_label"],
            source_fits_original=item["source_fits_original"], processed_fits=item["processed_fits"],
            bunit=item["bunit"], coverage_fraction=item["coverage_fraction"],
            valid_pixel_count=item["finite_pixel_count"], valid_sky_area_sqdeg=item["valid_sky_area_sqdeg"],
            pixel_scale_matrix_deg_per_pixel=item["pixel_scale_matrix_deg_per_pixel"],
            provenance_status="validated common-grid product; photometry remains preliminary",
            sources=sources,
            image_uri=f"/api/v1/science/epochs/{item['observation_id']}/image",
        )

    @staticmethod
    def _make_detection(epoch: str, source: dict[str, Any]) -> CandidateDetail:
        item = science_products.epochs[epoch]
        timestamp = _as_utc(item["timestamp_utc"])
        epoch_record = EpochMeasurement(
            epoch_index=0, observation_id=item["observation_id"],
            timestamp_utc=timestamp, timestamp_mjd=item["timestamp_mjd"], band=None,
            ra=source["ra_deg"], dec=source["dec_deg"],
            flux_density_mjy=None, flux_density_err_mjy=None, magnitude=None, magnitude_err=None,
            quality_flags=["preliminary_aperture_photometry", "common_coverage", "reprojected"],
            pixel_x=source["pixel_x"], pixel_y=source["pixel_y"],
            peak_MJy_sr=source["peak_MJy_sr"],
            aperture_sum_MJy_sr_pixel=source["aperture_sum_MJy_sr_pixel"],
            aperture_sum_unc_MJy_sr_pixel=source["aperture_sum_unc_MJy_sr_pixel"],
            flux_Jy_uncorrected=source["flux_Jy_uncorrected"],
            flux_unc_Jy_empirical=source["flux_unc_Jy_empirical"],
            snr_aperture=source["snr_aperture"], unit_input=source["unit_input"],
            quality_note=source["quality"], association_status=source["association_status"],
            cross_epoch_matches=source["cross_epoch_matches"],
        )
        source_id = source["source_id"]
        return CandidateDetail(
            candidate_id=source_id, ra=source["ra_deg"], dec=source["dec_deg"],
            observation_dates=[timestamp], bands_observed=[],
            displacement_arcsec=None, displacement_uncertainty_arcsec=None,
            displacement_significance_sigma=None, delta_brightness_mag=None,
            delta_brightness_uncertainty_mag=None, delta_brightness_significance_sigma=None,
            peak_MJy_sr=source["peak_MJy_sr"],
            aperture_sum_MJy_sr_pixel=source["aperture_sum_MJy_sr_pixel"],
            aperture_sum_unc_MJy_sr_pixel=source["aperture_sum_unc_MJy_sr_pixel"],
            flux_Jy_uncorrected=source["flux_Jy_uncorrected"],
            flux_unc_Jy_empirical=source["flux_unc_Jy_empirical"],
            snr_aperture=source["snr_aperture"], measurement_unit="Jy (uncorrected aperture sum)",
            measurement_method="DAOStarFinder detection; circular aperture r=3 px; empirical RMS uncertainty",
            measurement_status="Preliminary; not absolutely calibrated",
            quality_indicators=["common_coverage", "reprojected", "preliminary_aperture_photometry"],
            has_quality_warnings=True, scientific_interpretation=None,
            scientific_summary="Single-epoch source detection. Cross-epoch identity and scientific classification are not validated.",
            validation_status=ValidationStatus.INCONCLUSIVE,
            epochs=[epoch_record], spectrum=[], ice_features=[], cutout_thumbnails={},
            measurement_provenance={
                "epoch": epoch, "observation_id": item["observation_id"],
                "source_fits": item["source_fits_original"], "processed_fits": item["processed_fits"],
                "input_image_unit": source["unit_input"], "reported_flux_unit": "Jy, uncorrected aperture sum",
                "uncertainty": source["quality"], "wcs_frame": "ICRS",
                "association_status": source["association_status"],
                "classification": "not assessed", "external_catalogue_validation": "incomplete",
            },
            is_cross_epoch_identity_validated=False,
        )

    def list_candidates(
        self, min_displacement_sigma: Optional[float] = None, min_delta_mag: Optional[float] = None,
        ice_molecule: Optional[str] = None, validation_status: Optional[ValidationStatus] = None,
        category: Optional[ScientificCategory] = None, ra_deg: Optional[float] = None,
        dec_deg: Optional[float] = None, radius_arcmin: Optional[float] = None,
        page: int = 1, page_size: int = 20,
    ) -> Tuple[List[CandidateSummary], int]:
        results = list(self._candidates.values())
        if min_displacement_sigma is not None:
            results = [c for c in results if c.displacement_significance_sigma is not None and c.displacement_significance_sigma >= min_displacement_sigma]
        if min_delta_mag is not None:
            results = [c for c in results if c.delta_brightness_mag is not None and abs(c.delta_brightness_mag) >= min_delta_mag]
        if ice_molecule:
            results = []  # No validated spectral/ice measurements are available in this test field export.
        if validation_status is not None:
            results = [c for c in results if c.validation_status == validation_status]
        if category is not None:
            results = [c for c in results if c.scientific_interpretation == category]
        if ra_deg is not None and dec_deg is not None and radius_arcmin is not None:
            max_sep = radius_arcmin * 60.0
            results = [c for c in results if compute_angular_separation_arcsec(ra_deg, dec_deg, c.ra, c.dec) <= max_sep]
        total = len(results)
        start = (page - 1) * page_size
        return [CandidateSummary.model_validate(c.model_dump()) for c in results[start:start + page_size]], total

    def get_candidate(self, candidate_id: str) -> Optional[CandidateDetail]:
        return self._candidates.get(candidate_id)

    def update_validation(self, candidate_id: str, new_status: ValidationStatus, notes: Optional[str] = None) -> Optional[CandidateDetail]:
        record = self._candidates.get(candidate_id)
        if record is None:
            return None
        record.validation_status = new_status
        if notes is not None:
            record.user_notes = notes
        record.updated_at = datetime.now(timezone.utc)
        return record

    def list_observations(self, band=None, min_timestamp=None, max_timestamp=None) -> List[ObservationRecord]:
        records = list(self._observations.values())
        if band is not None:
            records = [o for o in records if o.band == band]
        if min_timestamp is not None:
            edge = min_timestamp.replace(tzinfo=timezone.utc) if min_timestamp.tzinfo is None else min_timestamp.astimezone(timezone.utc)
            records = [o for o in records if o.timestamp_utc >= edge]
        if max_timestamp is not None:
            edge = max_timestamp.replace(tzinfo=timezone.utc) if max_timestamp.tzinfo is None else max_timestamp.astimezone(timezone.utc)
            records = [o for o in records if o.timestamp_utc <= edge]
        return records

    def get_observation(self, observation_id: str) -> Optional[ObservationRecord]:
        return self._observations.get(observation_id)

    def add_observation(self, observation: ObservationRecord):
        self._observations[observation.observation_id] = observation


repo = SPHERExRepository()
