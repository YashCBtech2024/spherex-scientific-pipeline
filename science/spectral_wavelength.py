"""Read approximate per-pixel spectral coordinates from SPHEREx WCS-WAVE.

IRSA recommends the CWAVE/CBAND calibration maps for scientific analysis.
This module reads the WCS-WAVE lookup attached to Level 2 images only as a
diagnostic; callers must retain that provenance and must not treat it as a
calibrated bandpass match.
"""
from pathlib import Path
import re

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS


def _spectral_wcs(header, hdus):
    # SIP A/B terms describe the celestial tangent-plane correction. The
    # alternate spectral WCS uses its own auxiliary detector-pixel WCS; carrying
    # unsuffixed SIP terms into it makes Astropy apply the wrong distortion.
    spectral_header = header.copy()
    sip_key = re.compile(r"^(?:A|B|AP|BP)_(?:ORDER|DMAX|\d+_\d+)$")
    for key in list(spectral_header):
        if sip_key.match(key):
            del spectral_header[key]
    return WCS(spectral_header, fobj=hdus, key="W", relax=True)


def wavelength_bandwidth_at_pixel(fits_path: Path, x_pixel: float, y_pixel: float) -> dict:
    """Return the image's WCS-WAVE wavelength and bandwidth at zero-based x,y.

    The WCS-WAVE extension is a lookup table, not a dense per-pixel array.
    Astropy evaluates its tabular WCS at the requested image coordinate. SIP
    terms in these files belong to the celestial WCS and are not applied to
    the separate spectral alternate WCS.
    """
    fits_path = Path(fits_path)
    with fits.open(fits_path, memmap=True) as hdus:
        if "IMAGE" not in hdus or "WCS-WAVE" not in hdus:
            raise ValueError(f"{fits_path} must contain IMAGE and WCS-WAVE HDUs")
        image = hdus["IMAGE"].data
        if image is None or not (0 <= x_pixel < image.shape[1] and 0 <= y_pixel < image.shape[0]):
            raise ValueError("Image pixel coordinate is outside the IMAGE array")
        spectral_wcs = _spectral_wcs(hdus["IMAGE"].header, hdus)
        values = spectral_wcs.pixel_to_world_values(float(x_pixel), float(y_pixel))
        wavelength_um, bandwidth_um = (float(np.asarray(value)) for value in values)
    if not np.isfinite(wavelength_um) or wavelength_um <= 0:
        raise ValueError("WCS-WAVE returned an invalid wavelength")
    if not np.isfinite(bandwidth_um) or bandwidth_um <= 0:
        raise ValueError("WCS-WAVE returned an invalid bandwidth")
    return {
        "wavelength_um_wcs_wave_approx": wavelength_um,
        "bandwidth_um_wcs_wave_approx": bandwidth_um,
        "spectral_metadata_source": "WCS-WAVE approximate lookup; diagnostic only",
    }


def wavelength_bandwidth_at_sky(fits_path: Path, ra_deg: float, dec_deg: float) -> dict:
    """Map an ICRS sky coordinate through the input celestial WCS to WCS-WAVE."""
    fits_path = Path(fits_path)
    with fits.open(fits_path, memmap=True) as hdus:
        if "IMAGE" not in hdus or "WCS-WAVE" not in hdus:
            raise ValueError(f"{fits_path} must contain IMAGE and WCS-WAVE HDUs")
        image = hdus["IMAGE"].data
        celestial_wcs = WCS(hdus["IMAGE"].header, relax=True).celestial
        x_pixel, y_pixel = celestial_wcs.world_to_pixel_values(float(ra_deg), float(dec_deg))
        if not np.isfinite(x_pixel) or not np.isfinite(y_pixel):
            raise ValueError("Celestial WCS returned a non-finite image coordinate")
        if not (0 <= x_pixel < image.shape[1] and 0 <= y_pixel < image.shape[0]):
            raise ValueError("Sky coordinate falls outside the IMAGE array")
        spectral_wcs = _spectral_wcs(hdus["IMAGE"].header, hdus)
        wavelength_um, bandwidth_um = spectral_wcs.pixel_to_world_values(float(x_pixel), float(y_pixel))
        wavelength_um, bandwidth_um = float(np.asarray(wavelength_um)), float(np.asarray(bandwidth_um))
    if not np.isfinite(wavelength_um) or wavelength_um <= 0:
        raise ValueError("WCS-WAVE returned an invalid wavelength")
    if not np.isfinite(bandwidth_um) or bandwidth_um <= 0:
        raise ValueError("WCS-WAVE returned an invalid bandwidth")
    return {
        "x_input_pixel": float(x_pixel),
        "y_input_pixel": float(y_pixel),
        "wavelength_um_wcs_wave_approx": wavelength_um,
        "bandwidth_um_wcs_wave_approx": bandwidth_um,
        "spectral_metadata_source": "WCS-WAVE approximate lookup; diagnostic only",
    }
