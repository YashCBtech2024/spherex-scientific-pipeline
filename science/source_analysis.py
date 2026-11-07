"""Consistent masked source detection, aperture photometry and sky matching."""
from pathlib import Path
import csv,json
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.stats import SigmaClip
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture, aperture_photometry

EPOCHS=('2025-04-25','2025-05-09','2026-05-26')
SETTINGS={'fwhm_px':2.5,'threshold_sigma':5.0,'aperture_radius_px':3.0,'matching_radius_arcsec':2.0}

def detect_photometer(path: Path, mask: np.ndarray) -> list[dict]:
    with fits.open(path) as h:
        image=np.asarray(h[0].data,float); w=WCS(h[0].header,relax=True); unit=h[0].header.get('BUNIT','')
    valid=np.asarray(mask,bool)&np.isfinite(image)
    sample=image[valid]
    clipped=SigmaClip(sigma=3,maxiters=5)(sample,masked=True).compressed()
    med=float(np.median(clipped)); rms=float(1.4826*np.median(np.abs(clipped-med)))
    if not np.isfinite(rms) or rms<=0: raise ValueError(f'Invalid background RMS for {path}')
    work=np.where(valid,image,0.0)
    finder=DAOStarFinder(fwhm=SETTINGS['fwhm_px'],threshold=SETTINGS['threshold_sigma']*rms)
    tbl=finder(work,mask=~valid)
    if tbl is None:return []
    xcol='x_centroid' if 'x_centroid' in tbl.colnames else 'xcentroid'; ycol='y_centroid' if 'y_centroid' in tbl.colnames else 'ycentroid'
    xy=np.column_stack([np.asarray(tbl[xcol],float),np.asarray(tbl[ycol],float)])
    aps=CircularAperture(xy,r=SETTINGS['aperture_radius_px'])
    phot=aperture_photometry(work,aps,error=np.full(image.shape,rms),mask=~valid)
    area_sr=abs(np.linalg.det(w.pixel_scale_matrix))*(np.pi/180)**2
    rows=[]
    for i,(x,y) in enumerate(xy):
        sky=w.pixel_to_world(x,y)
        summed=float(phot['aperture_sum'][i]); err=float(phot['aperture_sum_err'][i])
        # MJy/sr * pixel solid angle -> Jy; no color/PSF/aperture correction applied.
        flux_jy=summed*area_sr*1e6; err_jy=err*area_sr*1e6
        rows.append({'x_pixel':float(x),'y_pixel':float(y),'ra_deg':float(sky.ra.deg),'dec_deg':float(sky.dec.deg),
            'peak_MJy_sr':float(tbl['peak'][i]),'aperture_sum_MJy_sr_pixel':summed,
            'aperture_sum_unc_MJy_sr_pixel':err,'flux_Jy_uncorrected':flux_jy,'flux_unc_Jy_empirical':err_jy,
            'snr_aperture':summed/err if err>0 else None,'background_rms_MJy_sr':rms,
            'unit_input':unit,'quality':'preliminary; no PSF/aperture correction; interpolation covariance omitted'})
    return rows

def run_catalogues(aligned_dir:Path, mask_path:Path, outdir:Path, radius_arcsec:float=2.0):
    mask=fits.getdata(mask_path).astype(bool); outdir.mkdir(parents=True,exist_ok=True)
    catalogues={}
    for epoch in EPOCHS:
        p=aligned_dir/f'{epoch}_common_aligned.fits'; rows=detect_photometer(p,mask); catalogues[epoch]=rows
        with (outdir/f'{epoch}_detections_photometry.csv').open('w',newline='',encoding='utf-8') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['x_pixel','y_pixel','ra_deg','dec_deg']);wr.writeheader();wr.writerows(rows)
    master=[]; ref=[]; mid='2025-05-09'
    for epoch,rows in catalogues.items():
        for i,row in enumerate(rows):
            matches=[]
            for other,ors in catalogues.items():
                if other==epoch: continue
                if ors:
                    a=SkyCoord(row['ra_deg']*u.deg,row['dec_deg']*u.deg);b=SkyCoord([x['ra_deg'] for x in ors]*u.deg,[x['dec_deg'] for x in ors]*u.deg)
                    j=int(np.argmin(a.separation(b).arcsec));sep=float(a.separation(b[j]).arcsec)
                    matches.append({'epoch':other,'index':j,'separation_arcsec':sep if sep<=radius_arcsec else None})
            master.append({'epoch':epoch,'detection_index':i,**row,'cross_epoch_matches':matches,
                           'association_status':'provisional coordinate association; WCS residuals not independently calibrated'})
    with (outdir/'three_epoch_master_associations.json').open('w',encoding='utf-8') as f:json.dump({'settings':SETTINGS,'items':master},f,indent=2)
    with (outdir/'three_epoch_master_associations.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=['epoch','detection_index','ra_deg','dec_deg','flux_Jy_uncorrected','flux_unc_Jy_empirical','snr_aperture','association_status']);wr.writeheader()
        for item in master:wr.writerow({k:item.get(k) for k in wr.fieldnames})
    # Assess historical positions against detections; outcomes remain positional only.
    hist=[]; hp=Path('data/catalogues/may2025_may2026_candidate_associations.csv')
    if hp.exists():
        with hp.open(encoding='utf-8-sig',newline='') as f:
            for old in csv.DictReader(f):
                record={'historical_2025_id':old['May2025_source_ID'],'historical_2026_id':old['May2026_source_ID'],'historical_separation_arcsec':float(old['Separation_arcsec'])}
                for epoch,keyra,keydec in [('2025-05-09','May2025_RA_deg','May2025_Dec_deg'),('2026-05-26','May2026_RA_deg','May2026_Dec_deg')]:
                    rows=catalogues[epoch]; target=SkyCoord(float(old[keyra])*u.deg,float(old[keydec])*u.deg); best=None
                    if rows:
                        coords=SkyCoord([r['ra_deg'] for r in rows]*u.deg,[r['dec_deg'] for r in rows]*u.deg); sep=target.separation(coords).arcsec;j=int(np.argmin(sep));best={'detection_index':j,'separation_arcsec':float(sep[j]),'within_2arcsec':bool(sep[j]<=2)}
                    record[epoch]=best
                record['status']='historical pair; re-identification is uncertain because catalogue centroids/WCS solutions differ; not a motion classification'
                hist.append(record)
        (outdir/'historical_candidate_reassessment.json').write_text(json.dumps(hist,indent=2),encoding='utf-8')
    # Overlay maps use identical grid and mask; epoch panels kept separate.
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,3,figsize=(12,4))
    for ax,epoch in zip(axs,EPOCHS):
        arr=fits.getdata(aligned_dir/f'{epoch}_common_aligned.fits'); rows=catalogues[epoch]
        ax.imshow(arr,origin='lower',cmap='gray',vmin=np.nanpercentile(arr,2),vmax=np.nanpercentile(arr,99.5))
        if rows:ax.scatter([r['x_pixel'] for r in rows],[r['y_pixel'] for r in rows],s=35,facecolors='none',edgecolors='cyan')
        ax.set_title(epoch)
    fig.tight_layout();fig.savefig(outdir/'three_epoch_source_overlays.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    for epoch,rows in catalogues.items():ax.scatter([i+1 for i,_ in enumerate(rows)],[r['flux_Jy_uncorrected'] for r in rows],label=epoch)
    ax.set(xlabel='Detection index (not cross-epoch ID)',ylabel='Aperture flux (Jy; uncorrected)',title='Per-epoch detected-source fluxes');ax.legend();fig.tight_layout();fig.savefig(outdir/'per_epoch_photometry.png');plt.close(fig)
    return catalogues,master
