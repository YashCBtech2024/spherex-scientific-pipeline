"""WCS-aware common-footprint validation and multi-epoch reprojection."""
from pathlib import Path
import json
import numpy as np
from shapely.geometry import Polygon
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, SkyOffsetFrame
import astropy.units as u
from reproject import reproject_interp
from matplotlib import pyplot as plt


def footprint_polygon(wcs: WCS, shape: tuple[int, int], center: SkyCoord) -> np.ndarray:
    ny, nx = shape
    # Dense sampling of true pixel-edge coordinates captures SIP curvature.
    edge = 257
    xb = np.linspace(-0.5, nx-0.5, edge)
    yr = np.linspace(-0.5, ny-0.5, edge)
    x = np.r_[xb, np.full(edge-1,nx-.5), xb[-2::-1], np.full(edge-2,-.5)]
    y = np.r_[np.full(edge,-.5), yr[1:], np.full(edge-1,ny-.5), yr[-2:0:-1]]
    sky = wcs.pixel_to_world(x, y)
    off = sky.transform_to(SkyOffsetFrame(origin=center))
    poly=np.column_stack([off.lon.to_value(u.deg), off.lat.to_value(u.deg)])
    if not np.all(np.isfinite(poly)):
        raise ValueError("Non-finite coordinates on WCS footprint boundary")
    # Remove adjacent numerical duplicates, retaining the sampled boundary order.
    keep=np.r_[True,np.any(np.abs(np.diff(poly,axis=0))>1e-13,axis=1)]
    return poly[keep]


def _clip(subject: np.ndarray, clipper: np.ndarray) -> np.ndarray:
    # Convex polygon clipping in a local tangent plane.
    out = subject
    area = np.sum(clipper[:,0]*np.roll(clipper[:,1],-1)-clipper[:,1]*np.roll(clipper[:,0],-1))
    sign = 1 if area >= 0 else -1
    def cross2(x, y): return x[0]*y[1]-x[1]*y[0]
    for a,b in zip(clipper, np.roll(clipper,-1,axis=0)):
        inp, out = out, []
        if len(inp)==0: break
        def inside(p): return sign*cross2(b-a,p-a) >= -1e-12
        def intersect(p,q):
            d=q-p; e=b-a; den=cross2(d,e)
            if abs(den)<1e-15: return q
            return p+d*(cross2(a-p,e)/den)
        s=inp[-1]
        for e in inp:
            if inside(e):
                if not inside(s): out.append(intersect(s,e))
                out.append(e)
            elif inside(s): out.append(intersect(s,e))
            s=e
        out=np.asarray(out)
    return np.asarray(out)


def align_epochs(inputs: list[tuple[str, Path]], outdir: Path, center_ra: float, center_dec: float,
                 pixel_scale_arcsec: float = 6.15) -> dict:
    center=SkyCoord(center_ra*u.deg,center_dec*u.deg,frame='icrs')
    images=[]; polys=[]
    for epoch,path in inputs:
        with fits.open(path) as hdus:
            data=np.asarray(hdus[0].data,dtype=float); hdr=hdus[0].header.copy(); w=WCS(hdr,relax=True)
        images.append((epoch,path,data,hdr,w)); polys.append(footprint_polygon(w,data.shape,center))
    common=Polygon(polys[0])
    for poly in polys[1:]: common=common.intersection(Polygon(poly))
    if common.is_empty or common.geom_type != 'Polygon': raise ValueError('No common sky footprint across all epochs')
    intersection=np.asarray(common.exterior.coords[:-1])
    # Inscribed centered rectangle represented by conservative symmetric bounds.
    halfx=min(abs(intersection[:,0].min()),abs(intersection[:,0].max()))
    halfy=min(abs(intersection[:,1].min()),abs(intersection[:,1].max()))
    scale=pixel_scale_arcsec/3600
    nx=int(np.floor(2*halfx/scale)); ny=int(np.floor(2*halfy/scale))
    if min(nx,ny)<8: raise ValueError(f'Common intersection too small: {nx}x{ny} pixels')
    wout=WCS(naxis=2); wout.wcs.crpix=[(nx+1)/2,(ny+1)/2]; wout.wcs.crval=[center_ra,center_dec]
    wout.wcs.cd=np.array([[-scale,0],[0,scale]]); wout.wcs.ctype=['RA---TAN','DEC--TAN']; wout.wcs.cunit=['deg','deg']
    outdir.mkdir(parents=True,exist_ok=True); outputs=[]
    for epoch,path,data,hdr,win in images:
        arr,foot=reproject_interp((data,win),wout,shape_out=(ny,nx),order='bilinear',return_footprint=True)
        out=outdir/f'{epoch}_aligned.fits'; png=outdir/f'{epoch}_aligned.png'
        h=wout.to_header(); h['BUNIT']=hdr.get('BUNIT',''); h['SRCFILE']=path.name; h['INTERP']='bilinear'
        fits.PrimaryHDU(np.asarray(arr,dtype=np.float32),header=h).writeto(out,overwrite=True)
        valid=np.isfinite(arr); lo,hi=np.nanpercentile(arr[valid],[1,99.5]);
        fig,ax=plt.subplots(figsize=(4,4),dpi=120); im=ax.imshow(arr,origin='lower',cmap='inferno',vmin=lo,vmax=hi);ax.set_title(epoch);fig.colorbar(im,ax=ax,label=hdr.get('BUNIT',''));fig.tight_layout();fig.savefig(png);plt.close(fig)
        outputs.append({'epoch':epoch,'source':str(path),'fits':str(out),'png':str(png),'shape_yx':[ny,nx],
                        'valid_fraction':float(np.mean(foot>0)),'interpolation':'bilinear'})
    metadata={'center_icrs_deg':[center_ra,center_dec],'common_footprint_tangent_polygon_deg':intersection.tolist(),
              'common_grid_shape_yx':[ny,nx],'pixel_scale_arcsec':pixel_scale_arcsec,'projection':'TAN common grid',
              'input_wcs_sip_used':True,'reprojection':'reproject_interp bilinear; SIP distortion evaluated through input WCS',
              'limitations':'Interpolation correlates neighboring pixels and smooths the PSF; no photometric or astrometric registration beyond each input WCS was applied.',
              'epochs':outputs}
    (outdir/'alignment_metadata.json').write_text(json.dumps(metadata,indent=2))
    fig,axs=plt.subplots(1,3,figsize=(12,4))
    for ax,item in zip(axs,outputs):
        a=fits.getdata(item['fits']); ax.imshow(a,origin='lower',cmap='inferno',vmin=np.nanpercentile(a,1),vmax=np.nanpercentile(a,99.5));ax.set_title(item['epoch'])
    fig.suptitle('Same sky grid — WCS reprojected (not registered by source motion)');fig.tight_layout();fig.savefig(outdir/'three_epoch_comparison.png');plt.close(fig)
    return metadata
