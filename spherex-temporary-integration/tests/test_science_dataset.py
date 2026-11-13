from pathlib import Path
import sys

import numpy as np
from astropy.io import fits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from backend.services.science_products import science_products


def load_products():
    return science_products


def test_real_three_epoch_products_and_common_mask():
    products = load_products()
    assert list(products.epochs) == ["2025-04-25", "2025-05-09", "2026-05-26"]
    assert [len(row["sources"]) for row in products.epochs.values()] == [5, 7, 7]
    reference_header = None
    for epoch, record in products.epochs.items():
        assert record["image"].shape == (60, 62)
        assert np.array_equal(np.isfinite(record["image"]), products.mask)
        assert record["finite_pixel_count"] == int(products.mask.sum()) == 2259
        assert record["coverage_fraction"] == 2259 / 3720
        assert record["bunit"] == "MJy / sr"
        if reference_header is None:
            reference_header = record["wcs_header"]
        else:
            assert record["wcs_header"] == reference_header
        for source in record["sources"]:
            assert source["inside_common_coverage"]
            assert source["wcs_roundtrip_residual_px"] < 1e-3
            assert source["flux_Jy_uncorrected"] is not None
            assert source["flux_unc_Jy_empirical"] > 0
            assert source["association_status"].startswith("provisional")


def test_mjd_is_derived_from_source_timestamp_and_band_is_unknown():
    products = load_products()
    record = products.list_observations()[0]
    assert abs(record["timestamp_mjd"] - 60790.029831168984) < 1e-8
    assert record["band"] is None
    assert record["wavelength_center_um"] is None


def test_original_cutout_and_aligned_files_exist_in_temporary_copy():
    products = load_products()
    for record in products.epochs.values():
        assert (products.root / record["processed_fits"]).is_file()
        original_name = Path(record["source_fits_original"].replace("\\", "/")).name
        assert (products.data / "raw" / original_name).is_file()
    mask = fits.getdata(products.data / "processed" / "aligned_validated" / "three_epoch_common_coverage_mask.fits").astype(bool)
    assert mask.sum() == 2259
