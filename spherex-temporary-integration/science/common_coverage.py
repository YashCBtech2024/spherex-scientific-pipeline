"""Create final three-epoch aligned products masked to exact shared coverage."""
from pathlib import Path
import json
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
from matplotlib import pyplot as plt

EPOCHS = ("2025-04-25", "2025-05-09", "2026-05-26")

def build_common_products(cutout_dir: Path, preliminary_dir: Path, output_dir: Path) -> dict:
    preliminary = [preliminary_dir / f"{e}_aligned.fits" for e in EPOCHS]
    with fits.open(preliminary[0]) as hdus:
        target_wcs = WCS(hdus[0].header, relax=True)
        shape = hdus[0].data.shape
    if any((fits.getdata(p).shape != shape or not WCS(fits.getheader(p), relax=True).wcs.compare(target_wcs.wcs)) for p in preliminary[1:]):
        raise ValueError("Preliminary products do not share one grid")
    projected, coverage = [], []
    for epoch in EPOCHS:
        src = cutout_dir / f"spherex_{epoch}_cutout.fits"
        with fits.open(src) as hdus:
            data = np.asarray(hdus[0].data, float)
            src_wcs = WCS(hdus[0].header, relax=True)
            bunit = hdus[0].header.get("BUNIT", "")
        arr, footprint = reproject_interp((data, src_wcs), target_wcs, shape_out=shape,
                                          order="bilinear", return_footprint=True)
        valid = np.isfinite(arr) & np.isfinite(footprint) & (footprint >= 1.0 - 1e-6)
        projected.append((epoch, arr, bunit)); coverage.append(valid)
    common = np.logical_and.reduce(coverage)
    nvalid = int(common.sum()); total = int(common.size)
    if nvalid == 0:
        raise ValueError("No pixels are fully covered by all three epochs")
    output_dir.mkdir(parents=True, exist_ok=True)
    mask_h = target_wcs.to_header(relax=True); mask_h["BUNIT"] = "1"
    mask_path = output_dir / "three_epoch_common_coverage_mask.fits"
    fits.PrimaryHDU(common.astype(np.uint8), header=mask_h).writeto(mask_path, overwrite=False)
    outrecords=[]
    for epoch, arr, bunit in projected:
        masked=np.where(common, arr, np.nan).astype(np.float32)
        h=target_wcs.to_header(relax=True); h["BUNIT"]=bunit; h["COVMASK"]=mask_path.name
        h["NVALID"]=nvalid; h["INTERP"]="bilinear"
        dst=output_dir/f"{epoch}_common_aligned.fits"
        fits.PrimaryHDU(masked,header=h).writeto(dst,overwrite=False)
        outrecords.append({"epoch":epoch,"fits":str(dst),"shape_yx":list(shape),"bunit":bunit,
                           "finite_pixel_count":int(np.isfinite(masked).sum())})
    # tangent-plane area approximation from shared grid's local pixel area
    matrix=target_wcs.pixel_scale_matrix
    pixel_area=float(abs(np.linalg.det(matrix))*3600**2)
    meta={"epochs":outrecords,"shape_yx":list(shape),"shared_wcs":target_wcs.to_header(relax=True).tostring(),
          "coverage_mask":str(mask_path),"common_valid_pixel_count":nvalid,"masked_pixel_count":total-nvalid,
          "total_grid_pixel_count":total,"coverage_fraction":nvalid/total,
          "valid_sky_area_sqdeg":nvalid*abs(np.linalg.det(matrix)),"pixel_area_arcsec2":pixel_area,
          "pixel_scale_matrix_deg_per_pixel":matrix.tolist(),"coverage_threshold":">= 1 - 1e-6 reproject footprint",
          "method":"Each original cutout reprojected through its full WCS (including SIP) to preliminary shared TAN WCS; bilinear interpolation.",
          "limitations":"Reprojection interpolates and correlates pixels. Finite pixels are covered in every input, but are not source-registered; remaining pointing/WCS offsets are not object motion."}
    (output_dir/"three_epoch_common_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    fig,axs=plt.subplots(1,3,figsize=(12,4))
    for ax,(epoch,arr,unit) in zip(axs,projected):
        a=np.where(common,arr,np.nan); lo,hi=np.nanpercentile(a,[1,99.5]); im=ax.imshow(a,origin="lower",cmap="inferno",vmin=lo,vmax=hi); ax.set_title(epoch);fig.colorbar(im,ax=ax,label=unit)
    fig.suptitle(f"Three epochs — common coverage only ({nvalid}/{total} pixels)");fig.tight_layout()
    fig.savefig(output_dir/"three_epoch_common_comparison.png");plt.close(fig)
    return meta
