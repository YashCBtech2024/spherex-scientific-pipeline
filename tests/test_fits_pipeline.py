import json
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from PIL import Image

from science.fits_pipeline import inspect_fits, load_image, validate_wcs, extract_sky_cutout, process_observation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits"
RA, DEC = 151.81441452, 2.82631029


def test_load_and_extension_inspection():
    entries = inspect_fits(SOURCE)
    assert entries[1]["name"] == "IMAGE"
    data, header, wcs = load_image(SOURCE)
    assert data.shape == (59, 58)
    assert header["BUNIT"] == "MJy / sr"
    assert wcs.sip is not None


def test_wcs_round_trip_and_cutout_center():
    data, _, wcs = load_image(SOURCE)
    result = validate_wcs(wcs, data.shape)
    assert result["roundtrip_error_pixel"] < 1e-6
    assert result["has_sip"]
    assert abs(result["pixel_scales_arcsec"][0] - result["pixel_scales_arcsec"][1]) > 0.1
    cut = extract_sky_cutout(data, wcs, RA, DEC, 32)
    assert cut.data.shape == (32, 32)
    world = cut.wcs.pixel_to_world(*cut.input_position_cutout)
    from astropy.coordinates import SkyCoord
    assert world.separation(SkyCoord(RA, DEC, unit='deg')).arcsec < 1e-5


def test_outputs_metadata_and_png(tmp_path):
    result = process_observation(SOURCE, RA, DEC, 32, tmp_path, "test")
    fits_path, png_path, meta_path = (Path(result[k]) for k in ("cutout_fits", "png", "metadata"))
    with fits.open(fits_path) as h:
        assert h[0].data.shape == (32, 32)
        assert WCS(h[0].header).sip is not None
        assert h[0].header["BUNIT"] == "MJy / sr"
    with Image.open(png_path) as im:
        assert im.format == "PNG" and im.width > 0 and im.height > 0
    meta = json.loads(meta_path.read_text())
    assert meta["size_pixels_yx"] == [32, 32]
    assert meta["bunit"] == "MJy / sr" and meta["wcs_validation"]["has_sip"]
    assert np.isfinite(meta["background_median"])
    # A second run must reuse validated outputs without overwriting them.
    assert process_observation(SOURCE, RA, DEC, 32, tmp_path, "test") == meta
