"""Reusable, WCS-preserving FITS processing for SPHEREx Level 2 images."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.stats import SigmaClip
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import astropy.units as u
from matplotlib import pyplot as plt
from matplotlib.colors import AsinhNorm


def inspect_fits(path: str | Path) -> list[dict[str, Any]]:
    with fits.open(path, memmap=True) as hdus:
        return [{"index": i, "name": h.name, "shape": list(h.data.shape) if h.data is not None else None,
                 "bitpix": h.header.get("BITPIX"), "bunit": h.header.get("BUNIT")} for i, h in enumerate(hdus)]


def load_image(path: str | Path, ext: int | str = "IMAGE"):
    with fits.open(path, memmap=True) as hdus:
        hdu = hdus[ext]
        data = np.asarray(hdu.data, dtype=float).copy()
        header = hdu.header.copy()
    if data.ndim != 2:
        raise ValueError(f"Expected 2D image extension; got shape {data.shape}")
    wcs = WCS(header, relax=True)
    if not wcs.has_celestial:
        raise ValueError("Image extension has no celestial WCS")
    return data, header, wcs


def validate_wcs(wcs: WCS, shape: tuple[int, int]) -> dict[str, Any]:
    if not wcs.has_celestial:
        raise ValueError("WCS has no celestial axes")
    h, w = shape
    cx, cy = (w - 1) / 2, (h - 1) / 2
    world = wcs.pixel_to_world(cx, cy)
    bx, by = wcs.world_to_pixel(world)
    err = float(np.hypot(float(bx)-cx, float(by)-cy))
    if not np.isfinite(err) or err > 1e-4:
        raise ValueError(f"WCS round-trip failed ({err} pixel)")
    # Axis scales are the row norms of the full linear transform: retain anisotropy.
    scales = np.linalg.norm(wcs.pixel_scale_matrix, axis=1) * 3600.0
    return {"roundtrip_error_pixel": err, "center_ra_deg": float(world.ra.deg),
            "center_dec_deg": float(world.dec.deg), "pixel_scales_arcsec": [float(x) for x in scales],
            "has_sip": wcs.sip is not None}


def extract_sky_cutout(data: np.ndarray, wcs: WCS, ra_deg: float, dec_deg: float,
                       size: int | tuple[int, int] = 32) -> Cutout2D:
    if isinstance(size, int):
        size = (size, size)
    coord = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame="icrs")
    return Cutout2D(data, coord, size=size, wcs=wcs, mode="partial", fill_value=np.nan,
                    copy=True, limit_rounding_method=np.ceil)


def estimate_background(data: np.ndarray, mask: np.ndarray | None = None) -> tuple[float, float]:
    values = np.asarray(data, dtype=float)
    valid = np.isfinite(values)
    if mask is not None:
        valid &= ~np.asarray(mask, dtype=bool)
    sample = values[valid]
    if sample.size == 0:
        raise ValueError("No unmasked finite pixels available for background estimate")
    clipped = SigmaClip(sigma=3.0, maxiters=5)(sample, masked=True).compressed()
    med = float(np.median(clipped))
    mad = float(1.4826 * np.median(np.abs(clipped-med)))
    return med, mad


def write_png(data: np.ndarray, path: str | Path, background: float, noise: float,
              unit: str = "image units") -> dict[str, Any]:
    arr = np.asarray(data, dtype=float)
    finite = arr[np.isfinite(arr)]
    if not finite.size:
        raise ValueError("Cannot render image with no finite pixels")
    lo, hi = np.nanpercentile(arr, [1, 99.5])
    if hi <= lo:
        hi = lo + 1
    fig, ax = plt.subplots(figsize=(6, 6), dpi=120)
    ax.imshow(arr, origin="lower", cmap="inferno", interpolation="nearest",
              norm=AsinhNorm(linear_width=max(noise, np.finfo(float).eps), vmin=lo, vmax=hi))
    ax.set_title("SPHEREx Level 2 cutout — background subtracted")
    ax.set_xlabel("Cutout pixel X"); ax.set_ylabel("Cutout pixel Y")
    fig.colorbar(ax.images[0], ax=ax, label=unit)
    fig.tight_layout(); fig.savefig(path, format="png", dpi=120); plt.close(fig)
    return {"stretch": "asinh", "percentile_limits": [1.0, 99.5], "colorbar_label": unit,
            "data_min": float(np.nanmin(arr)), "data_max": float(np.nanmax(arr)), "unit": unit}


def process_observation(fits_path: str | Path, ra_deg: float, dec_deg: float,
                        size_px: int, output_dir: str | Path, observation_id: str) -> dict[str, Any]:
    fits_path, out = Path(fits_path), Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    data, header, wcs = load_image(fits_path)
    wcs_check = validate_wcs(wcs, data.shape)
    cutout = extract_sky_cutout(data, wcs, ra_deg, dec_deg, size_px)
    bkg, rms = estimate_background(cutout.data)
    subtracted = cutout.data - bkg
    stem = observation_id
    cut_fits = out / f"{stem}_cutout.fits"
    png = out / f"{stem}_cutout.png"
    meta = out / f"{stem}_metadata.json"
    if all(p.exists() for p in (cut_fits, png, meta)):
        try:
            prior = json.loads(meta.read_text(encoding="utf-8"))
            with fits.open(cut_fits, memmap=True) as check:
                fits_ok = check[0].data.shape == (size_px, size_px) and WCS(check[0].header).has_celestial
            from PIL import Image
            with Image.open(png) as image:
                png_ok = image.format == "PNG"
            if (prior.get("source_fits") == str(fits_path) and prior.get("cutout_center_requested_deg") == {"ra": ra_deg, "dec": dec_deg}
                    and prior.get("size_pixels_yx") == [size_px, size_px] and fits_ok and png_ok):
                if (prior.get("visualization", {}).get("stretch") == "asinh"
                        and prior.get("visualization", {}).get("colorbar_label") == prior.get("bunit")
                        and prior.get("metadata")):
                    return prior
        except Exception:
            pass
        index = 2
        while any((out / f"{observation_id}_v{index}_{suffix}").exists() for suffix in ("cutout.fits", "cutout.png", "metadata.json")):
            index += 1
        stem = f"{observation_id}_v{index}"
        cut_fits = out / f"{stem}_cutout.fits"; png = out / f"{stem}_cutout.png"; meta = out / f"{stem}_metadata.json"
    # Preserve full original header including SIP terms; Cutout2D updates CRPIX correctly.
    out_header = header.copy(); out_header.update(cutout.wcs.to_header(relax=True))
    out_header["BKG_MED"] = (bkg, "Median clipped background in image units")
    fits.PrimaryHDU(data=subtracted.astype(np.float32), header=out_header).writeto(cut_fits, overwrite=False)
    visualization = write_png(subtracted, png, bkg, rms, header.get("BUNIT", "image units"))
    center_world = cutout.wcs.pixel_to_world((cutout.data.shape[1]-1)/2, (cutout.data.shape[0]-1)/2)
    result = {"observation_id": observation_id, "source_fits": str(fits_path), "image_extension": "IMAGE",
              "timestamp_utc": header.get("DATE-OBS"), "bunit": header.get("BUNIT"),
              "cutout_center_requested_deg": {"ra": ra_deg, "dec": dec_deg},
              "cutout_center_actual_deg": {"ra": float(center_world.ra.deg), "dec": float(center_world.dec.deg)},
              "size_pixels_yx": list(cutout.data.shape), "background_median": bkg, "background_rms_robust": rms,
              "wcs_validation": wcs_check, "original_wcs_header_preserved": True,
              "visualization": visualization,
              "cutout_fits": str(cut_fits), "png": str(png), "metadata": str(meta),
              "background_subtracted": True}
    meta.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
