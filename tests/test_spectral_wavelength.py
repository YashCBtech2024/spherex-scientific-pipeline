from pathlib import Path

import pytest

from science.spectral_wavelength import wavelength_bandwidth_at_pixel, wavelength_bandwidth_at_sky


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EPOCH_FILES = (
    RAW / "level2_2025W17_4B_0043_1D1_spx_l2b-v20-2025-241.fits",
    RAW / "level2_2025W19_2B_0103_1D1_spx_l2b-v20-2025-247.fits",
    RAW / "level2_2026W22_1A_0214_2D1_spx_l2b-v25-2026-150.fits",
)


@pytest.mark.parametrize("fits_path", EPOCH_FILES)
def test_wcs_wave_returns_finite_positive_spectral_coordinates(fits_path):
    values = wavelength_bandwidth_at_sky(fits_path, 151.81441452, 2.82631029)
    assert 0.7 < values["wavelength_um_wcs_wave_approx"] < 1.2
    assert 0 < values["bandwidth_um_wcs_wave_approx"] < 0.1
    assert values["spectral_metadata_source"].startswith("WCS-WAVE")


def test_wcs_wave_pixel_bounds_are_checked():
    with pytest.raises(ValueError, match="outside"):
        wavelength_bandwidth_at_pixel(EPOCH_FILES[0], 1e6, 1e6)
