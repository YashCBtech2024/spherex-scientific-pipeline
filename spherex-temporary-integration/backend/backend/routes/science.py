"""Endpoints exposing the copied scientific products without synthetic fallbacks."""
from fastapi import APIRouter, HTTPException

from backend.services.science_products import EPOCHS, science_products

router = APIRouter(prefix="/api/v1/science", tags=["Scientific products"])


@router.get("/summary")
def science_summary():
    metadata = science_products.common_metadata
    return {
        "project": "SPHEREx three-epoch test-field processing",
        "status": "preliminary measurements; scientific classifications and cross-epoch identities are unverified",
        "epochs": [
            {
                "epoch": e,
                "observation_id": science_products.epochs[e]["observation_id"],
                "timestamp_utc": science_products.epochs[e]["timestamp_utc"],
                "detection_count": len(science_products.epochs[e]["sources"]),
            }
            for e in EPOCHS
        ],
        "shape_yx": metadata["shape_yx"],
        "common_valid_pixel_count": metadata["common_valid_pixel_count"],
        "masked_pixel_count": metadata["masked_pixel_count"],
        "coverage_fraction": metadata["coverage_fraction"],
        "valid_sky_area_sqdeg": metadata["valid_sky_area_sqdeg"],
        "pixel_area_arcsec2": metadata["pixel_area_arcsec2"],
        "bunit": "MJy / sr",
        "photometry_unit": "Jy uncorrected aperture sum",
        "photometry_limitations": "No PSF/aperture correction or absolute calibration; empirical RMS errors omit reprojection covariance.",
        "astrometry_limitations": "Shared WCS grid is not independent astrometric registration; residual pointing differences are not motion evidence.",
    }


@router.get("/epochs/{observation_id}/image")
def epoch_image(observation_id: str):
    result = science_products.full_image_payload(observation_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No scientific image for observation {observation_id}")
    return result


@router.get("/provisional-associations")
def provisional_associations():
    return science_products.associations()
