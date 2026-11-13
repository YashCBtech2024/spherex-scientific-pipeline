"""Read-only loader for the copied, validated SPHEREx test-field products.

This module serves existing products; it does not rerun detection, photometry,
registration, or external catalogue queries.
"""
from __future__ import annotations

import base64
import csv
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.time import Time
from astropy.wcs import WCS
import astropy.units as u


EPOCHS = ("2025-04-25", "2025-05-09", "2026-05-26")
OBSERVATION_IDS = {epoch: f"spherex_{epoch}" for epoch in EPOCHS}
ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"


def _header_json(header: fits.Header) -> dict[str, Any]:
    """Return a JSON-safe full celestial WCS header, including all matrix terms."""
    wcs_header = WCS(header, relax=True).celestial.to_header(relax=True)
    return {str(key): value.item() if isinstance(value, np.generic) else value
            for key, value in wcs_header.items()}


class ScienceProducts:
    """Loads the three immutable common-grid observations and their catalogues."""

    def __init__(self, root: Path = ROOT):
        self.root = Path(root)
        self.data = self.root / "data"
        aligned = self.data / "processed" / "aligned_validated"
        catalogues = self.data / "catalogues" / "reprocessed"
        self.common_metadata = json.loads((aligned / "three_epoch_common_metadata.json").read_text(encoding="utf-8"))
        self.mask = np.asarray(fits.getdata(aligned / "three_epoch_common_coverage_mask.fits"), dtype=bool)
        self.master = json.loads((catalogues / "three_epoch_master_associations.json").read_text(encoding="utf-8"))
        self.historical = json.loads((catalogues / "historical_candidate_reassessment.json").read_text(encoding="utf-8"))
        master_by_key = {(item["epoch"], int(item["detection_index"])): item for item in self.master["items"]}
        self.epochs: dict[str, dict[str, Any]] = {}
        all_pixels: list[np.ndarray] = []
        shared_wcs_header: dict[str, Any] | None = None

        for epoch in EPOCHS:
            fits_path = aligned / f"{epoch}_common_aligned.fits"
            meta_path = self.data / "processed" / "multi_epoch" / f"spherex_{epoch}_metadata.json"
            csv_path = catalogues / f"{epoch}_detections_photometry.csv"
            original_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            with fits.open(fits_path, memmap=False) as hdus:
                image = np.asarray(hdus[0].data, dtype=float).copy()
                header = hdus[0].header.copy()
            wcs = WCS(header, relax=True).celestial
            if image.shape != self.mask.shape:
                raise ValueError(f"Image/mask shape mismatch for {epoch}: {image.shape} vs {self.mask.shape}")
            if not np.array_equal(np.isfinite(image), self.mask):
                raise ValueError(f"Finite-pixel support in {epoch} does not exactly equal the saved common-coverage mask")
            current_wcs_header = _header_json(header)
            if shared_wcs_header is None:
                shared_wcs_header = current_wcs_header
            elif current_wcs_header != shared_wcs_header:
                raise ValueError(f"The aligned WCS for {epoch} differs from the shared reference grid")
            valid = self.mask & np.isfinite(image)
            image[~valid] = np.nan
            with csv_path.open(encoding="utf-8-sig", newline="") as stream:
                raw_rows = list(csv.DictReader(stream))
            sources = []
            for index, raw in enumerate(raw_rows):
                ra = float(raw["ra_deg"])
                dec = float(raw["dec_deg"])
                x_wcs, y_wcs = wcs.world_to_pixel(SkyCoord(ra * u.deg, dec * u.deg, frame="icrs"))
                x_file, y_file = float(raw["x_pixel"]), float(raw["y_pixel"])
                residual_px = float(np.hypot(float(x_wcs) - x_file, float(y_wcs) - y_file))
                if residual_px > 1e-3:
                    raise ValueError(f"Catalogue coordinate/WCS round-trip differs by {residual_px:.6g} px for {epoch}/{index}")
                xi, yi = int(round(float(x_wcs))), int(round(float(y_wcs)))
                in_bounds = 0 <= xi < image.shape[1] and 0 <= yi < image.shape[0]
                on_common_footprint = bool(in_bounds and valid[yi, xi])
                if not on_common_footprint:
                    raise ValueError(f"Detection {epoch}/{index} falls outside the common valid footprint")
                linked = master_by_key.get((epoch, index), {})
                sources.append({
                    "source_id": f"DET-{epoch}-{index:03d}",
                    "detection_index": index,
                    "pixel_x": float(x_wcs),
                    "pixel_y": float(y_wcs),
                    "catalogue_pixel_x": x_file,
                    "catalogue_pixel_y": y_file,
                    "wcs_roundtrip_residual_px": residual_px,
                    "ra_deg": ra,
                    "dec_deg": dec,
                    "peak_MJy_sr": float(raw["peak_MJy_sr"]),
                    "aperture_sum_MJy_sr_pixel": float(raw["aperture_sum_MJy_sr_pixel"]),
                    "aperture_sum_unc_MJy_sr_pixel": float(raw["aperture_sum_unc_MJy_sr_pixel"]),
                    "flux_Jy_uncorrected": float(raw["flux_Jy_uncorrected"]),
                    "flux_unc_Jy_empirical": float(raw["flux_unc_Jy_empirical"]),
                    "snr_aperture": float(raw["snr_aperture"]),
                    "background_rms_MJy_sr": float(raw["background_rms_MJy_sr"]),
                    "unit_input": raw["unit_input"],
                    "quality": raw["quality"],
                    "association_status": linked.get("association_status", "No validated cross-epoch identity"),
                    "cross_epoch_matches": linked.get("cross_epoch_matches", []),
                    "inside_common_coverage": on_common_footprint,
                })
            valid_pixels = image[valid]
            all_pixels.append(valid_pixels)
            timestamp = original_meta["timestamp_utc"]
            timestamp_mjd = float(Time(timestamp, format="isot", scale="utc").mjd)
            self.epochs[epoch] = {
                "observation_id": OBSERVATION_IDS[epoch],
                "epoch": epoch,
                "timestamp_utc": timestamp,
                "timestamp_mjd": timestamp_mjd,
                "detector_label": "D1 (project observation label)",
                "band": None,
                "wavelength_center_um": None,
                "exposure_time_sec": None,
                "zeropoint_mag": None,
                "bunit": header.get("BUNIT", "unknown"),
                "source_fits_original": str(original_meta["source_fits"]),
                "processed_fits": str(fits_path.relative_to(self.root)),
                "original_cutout_metadata": original_meta,
                "image": image,
                "valid_mask": valid,
                "wcs": wcs,
                "wcs_header": _header_json(header),
                "header": header,
                "sources": sources,
                "shape_yx": list(image.shape),
                "finite_pixel_count": int(np.count_nonzero(valid)),
                "coverage_fraction": float(np.count_nonzero(valid) / valid.size),
                "valid_sky_area_sqdeg": float(self.common_metadata["valid_sky_area_sqdeg"]),
                "pixel_area_arcsec2": float(self.common_metadata["pixel_area_arcsec2"]),
                "pixel_scale_matrix_deg_per_pixel": wcs.pixel_scale_matrix.tolist(),
                "background_rms_MJy_sr": float(original_meta["background_rms_robust"]),
                "background_rms_scope": "original 48x48 cutout before common-grid reprojection",
            }
        pooled = np.concatenate(all_pixels)
        self.display_limits = [float(np.percentile(pooled, 2)), float(np.percentile(pooled, 99.5))]

    def list_observations(self) -> list[dict[str, Any]]:
        return [self.observation_record(e) for e in EPOCHS]

    def observation_record(self, epoch: str) -> dict[str, Any]:
        item = self.epochs[epoch]
        return {key: value for key, value in item.items() if key not in {"image", "valid_mask", "wcs", "header"}}

    def get_epoch(self, observation_id: str) -> dict[str, Any] | None:
        return next((value for value in self.epochs.values() if value["observation_id"] == observation_id), None)

    def full_image_payload(self, observation_id: str) -> dict[str, Any] | None:
        item = self.get_epoch(observation_id)
        if item is None:
            return None
        pixels = [[float(v) if np.isfinite(v) else None for v in row] for row in item["image"]]
        return {
            "observation_id": observation_id,
            "epoch": item["epoch"],
            "timestamp_utc": item["timestamp_utc"],
            "shape_yx": item["shape_yx"],
            "pixels": pixels,
            "coverage_mask": item["valid_mask"].tolist(),
            "coverage_fraction": item["coverage_fraction"],
            "valid_pixel_count": item["finite_pixel_count"],
            "masked_pixel_count": int(item["valid_mask"].size - item["finite_pixel_count"]),
            "valid_sky_area_sqdeg": item["valid_sky_area_sqdeg"],
            "bunit": item["bunit"],
            "display_limits": self.display_limits,
            "wcs_header": item["wcs_header"],
            "pixel_scale_matrix_deg_per_pixel": item["pixel_scale_matrix_deg_per_pixel"],
            "sources": item["sources"],
            "image_origin": "lower",
            "interpolation_note": "These are common-grid products already reprojected with bilinear interpolation; masked pixels are null and are not measurements.",
        }

    def render_png(self, item: dict[str, Any], ra: float, dec: float, size_px: int) -> dict[str, Any]:
        """Return an actual-pixel WCS cutout for the requested sky position."""
        center = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
        center_x, center_y = item["wcs"].world_to_pixel(center)
        center_x, center_y = float(center_x), float(center_y)
        center_ix, center_iy = int(round(center_x)), int(round(center_y))
        if not (0 <= center_ix < item["image"].shape[1] and 0 <= center_iy < item["image"].shape[0]):
            raise ValueError("Requested sky coordinate is outside this observation's common-grid image")
        if not item["valid_mask"][center_iy, center_ix]:
            raise ValueError("Requested sky coordinate falls in a pixel without common three-observation coverage")
        cut = Cutout2D(item["image"], center, (size_px, size_px), wcs=item["wcs"], mode="partial", fill_value=np.nan)
        mask_cut = Cutout2D(item["valid_mask"].astype(np.uint8), center, (size_px, size_px), wcs=item["wcs"], mode="partial", fill_value=0)
        cut_data = np.asarray(cut.data, dtype=float)
        cut_mask = mask_cut.data.astype(bool) & np.isfinite(cut_data)
        cut_data[~cut_mask] = np.nan
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib import colormaps
        from astropy.visualization import ImageNormalize, AsinhStretch
        from PIL import Image
        norm = ImageNormalize(vmin=self.display_limits[0], vmax=self.display_limits[1], stretch=AsinhStretch(), clip=True)
        normalized = np.ma.filled(norm(np.ma.array(cut_data, mask=~cut_mask)), 0.0)
        rgba = np.asarray(np.clip(colormaps["magma"](normalized) * 255, 0, 255), dtype=np.uint8)
        rgba[~cut_mask, 0:3] = 0
        rgba[~cut_mask, 3] = 0
        output = io.BytesIO()
        Image.fromarray(rgba, mode="RGBA").save(output, format="PNG", optimize=False)
        return {
            "observation_id": item["observation_id"], "ra": ra, "dec": dec,
            "size_pixels": size_px,
            "data_uri": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii"),
            "data_width_px": int(cut_data.shape[1]), "data_height_px": int(cut_data.shape[0]),
            "display_stretch": "asinh with pooled 3-epoch 2nd–99.5th percentile limits",
            "bunit": item["bunit"], "wcs_header": _header_json(cut.wcs.to_header(relax=True)),
            "coverage_fraction": float(np.count_nonzero(cut_mask) / cut_mask.size),
            "valid_pixel_count": int(np.count_nonzero(cut_mask)),
            "masked_pixel_count": int(cut_mask.size - np.count_nonzero(cut_mask)),
            "interpolation_note": "Cutout is a view of the already reprojected common-grid pixels; no new interpolation was performed for this crop.",
        }

    def associations(self) -> dict[str, Any]:
        return {
            "settings": self.master.get("settings", {}),
            "items": self.master.get("items", []),
            "interpretation": "Nearest-coordinate links within the configured search radius are provisional only. WCS residuals are not independently calibrated; links are not confirmed identities or motion detections.",
            "historical_candidate_reassessment": self.historical,
        }


science_products = ScienceProducts()
