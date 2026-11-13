import base64
from io import BytesIO

from PIL import Image
import requests


def test_health_root_and_real_catalogue(api_base_url):
    health = requests.get(api_base_url + "/api/v1/health", timeout=15)
    assert health.status_code == 200 and health.json()["status"] == "healthy"
    root = requests.get(api_base_url + "/", timeout=15).json()
    assert root["status"] == "preliminary_science_integration_test"
    assert root["synthetic_seed_data_loaded"] is False
    assert root["indexed_candidates_count"] == 19
    assert root["indexed_observations_count"] == 3
    assert root["bands_count"] is None


def test_observation_epochs_and_metadata(api_base_url):
    observations = requests.get(api_base_url + "/api/v1/observations", timeout=15).json()
    assert [row["timestamp_utc"][:10] for row in observations] == ["2025-04-25", "2025-05-09", "2026-05-26"]
    assert [len(row["sources"]) for row in observations] == [5, 7, 7]
    for record in observations:
        assert record["band"] is None
        assert record["wavelength_center_um"] is None
        assert record["bunit"] == "MJy / sr"
        assert record["coverage_fraction"] == 2259 / 3720
        assert record["wcs"]["full_header"]["CTYPE1"] == "RA---TAN"
        assert record["wcs"]["pixel_scale_matrix_deg_per_pixel"]
        assert all(source["flux_density_mjy"] is None for source in record["sources"])
        assert all(source["flux_Jy_uncorrected"] is not None for source in record["sources"])


def test_candidates_keep_measurements_separate_from_conclusions(api_base_url):
    response = requests.get(api_base_url + "/api/v1/candidates", params={"page": 1, "page_size": 100}, timeout=15)
    payload = response.json()
    assert response.status_code == 200 and payload["total"] == 19
    first = payload["items"][0]
    assert first["displacement_arcsec"] is None
    assert first["displacement_significance_sigma"] is None
    assert first["delta_brightness_mag"] is None
    assert first["scientific_interpretation"] is None
    assert first["validation_status"] == "Inconclusive"
    assert first["measurement_status"] == "Preliminary; not absolutely calibrated"
    assert first["flux_Jy_uncorrected"] is not None
    assert first["flux_unc_Jy_empirical"] is not None
    detail = requests.get(api_base_url + "/api/v1/candidates/" + first["candidate_id"], timeout=15).json()
    assert detail["is_cross_epoch_identity_validated"] is False
    assert detail["epochs"][0]["flux_density_mjy"] is None
    assert detail["epochs"][0]["flux_Jy_uncorrected"] == first["flux_Jy_uncorrected"]
    assert detail["measurement_provenance"]["external_catalogue_validation"] == "incomplete"


def test_real_common_grid_images_and_coverage(api_base_url):
    images = []
    for epoch in ("spherex_2025-04-25", "spherex_2025-05-09", "spherex_2026-05-26"):
        response = requests.get(api_base_url + f"/api/v1/science/epochs/{epoch}/image", timeout=15)
        assert response.status_code == 200
        image = response.json()
        assert image["shape_yx"] == [60, 62]
        assert image["valid_pixel_count"] == 2259
        assert image["masked_pixel_count"] == 1461
        assert image["coverage_fraction"] == 2259 / 3720
        assert image["bunit"] == "MJy / sr"
        assert image["wcs_header"]["RADESYS"] == "ICRS"
        assert image["wcs_header"]["CTYPE1"] == "RA---TAN"
        assert image["pixels"][0][0] is None
        assert any(value is not None for row in image["pixels"] for value in row)
        assert sum(map(sum, image["coverage_mask"])) == 2259
        images.append(image)
    assert images[0]["wcs_header"] == images[1]["wcs_header"] == images[2]["wcs_header"]
    assert images[0]["display_limits"] == images[1]["display_limits"] == images[2]["display_limits"]


def test_cutout_png_is_actual_and_mask_metadata_is_present(api_base_url):
    response = requests.get(
        api_base_url + "/api/v1/observations/spherex_2025-05-09/cutout",
        params={"ra": 151.81441452, "dec": 2.82631029, "size_px": 48}, timeout=30,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["bunit"] == "MJy / sr"
    assert result["coverage_fraction"] > 0
    assert result["data_width_px"] == result["data_height_px"] == result["size_pixels"] == 48
    assert "asinh" in result["display_stretch"]
    png = base64.b64decode(result["data_uri"].split(",", 1)[1], validate=True)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(BytesIO(png)) as image:
        assert image.format == "PNG"
        assert image.size == (48, 48)


def test_associations_remain_provisional_and_unknown_ids_fail(api_base_url):
    result = requests.get(api_base_url + "/api/v1/science/provisional-associations", timeout=15).json()
    assert len(result["items"]) == 19
    assert "not confirmed identities" in result["interpretation"]
    reassessments = result["historical_candidate_reassessment"]
    assert len(reassessments) == 2
    assert all("not a motion classification" in row["status"] for row in reassessments)
    assert requests.get(api_base_url + "/api/v1/candidates/unknown", timeout=15).status_code == 404
    assert requests.get(api_base_url + "/api/v1/science/epochs/unknown/image", timeout=15).status_code == 404


def test_remaining_read_routes_filters_and_write_validation(api_base_url):
    bands = requests.get(api_base_url + "/api/v1/spectral/bands", timeout=15)
    assert bands.status_code == 200 and len(bands.json()) == 6
    ice = requests.get(api_base_url + "/api/v1/spectral/ice-diagnostics", timeout=15)
    assert ice.status_code == 200 and {row["molecule"] for row in ice.json()} == {"H2O", "CO2", "CO"}

    obs = requests.get(api_base_url + "/api/v1/observations/spherex_2025-04-25", timeout=15)
    assert obs.status_code == 200 and obs.json()["timestamp_utc"].startswith("2025-04-25")
    filtered = requests.get(
        api_base_url + "/api/v1/observations",
        params={"min_date": "2025-05-01T00:00:00Z"}, timeout=15,
    )
    assert filtered.status_code == 200
    assert [row["timestamp_utc"][:10] for row in filtered.json()] == ["2025-05-09", "2026-05-26"]
    cone = requests.get(
        api_base_url + "/api/v1/candidates",
        params={"ra": 151.81441452, "dec": 2.82631029, "radius_arcmin": 5, "page_size": 100}, timeout=15,
    )
    assert cone.status_code == 200 and cone.json()["total"] > 0

    summary = requests.get(api_base_url + "/api/v1/science/summary", timeout=15)
    assert summary.status_code == 200 and len(summary.json()["epochs"]) == 3
    # Exercise write-route request validation without creating fake scientific records or changing triage state.
    candidate_id = requests.get(api_base_url + "/api/v1/candidates", params={"page_size": 1}, timeout=15).json()["items"][0]["candidate_id"]
    invalid_validation = requests.post(api_base_url + f"/api/v1/candidates/{candidate_id}/validate", json={}, timeout=15)
    invalid_ingest = requests.post(api_base_url + "/api/v1/observations/ingest", json={}, timeout=15)
    assert invalid_validation.status_code == 422
    assert invalid_ingest.status_code == 422
