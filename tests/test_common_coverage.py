import json
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, SkyOffsetFrame
import astropy.units as u
from shapely.geometry import Polygon
from science.alignment import footprint_polygon

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/aligned_validated'
CUT=ROOT/'data/processed/multi_epoch'
EPOCHS=('2025-04-25','2025-05-09','2026-05-26')

def test_valid_footprints_and_real_intersection():
    c=SkyCoord(151.81441452*u.deg,2.82631029*u.deg)
    polygons=[]
    for e in EPOCHS:
        with fits.open(CUT/f'spherex_{e}_cutout.fits') as h:
            poly=Polygon(footprint_polygon(WCS(h[0].header,relax=True),h[0].data.shape,c))
        assert poly.is_valid and poly.area>0
        polygons.append(poly)
    common=polygons[0].intersection(polygons[1]).intersection(polygons[2])
    assert common.is_valid and common.area>0.006

def test_final_common_mask_wcs_dimensions_and_coverage():
    meta=json.loads((OUT/'three_epoch_common_metadata.json').read_text())
    mask=fits.getdata(OUT/'three_epoch_common_coverage_mask.fits').astype(bool)
    assert int(mask.sum())==meta['common_valid_pixel_count']==2259
    grids=[]
    for e in EPOCHS:
        p=OUT/f'{e}_common_aligned.fits'
        with fits.open(p) as h:
            a=h[0].data; w=WCS(h[0].header,relax=True); grids.append((a,w))
            assert a.shape==tuple(meta['shape_yx'])
            assert np.array_equal(np.isfinite(a),mask)
    assert all(a.shape==grids[0][0].shape for a,w in grids)
    assert all(w.wcs.compare(grids[0][1].wcs) for a,w in grids[1:])
    for a,w in grids:
        sky=w.pixel_to_world((a.shape[1]-1)/2,(a.shape[0]-1)/2)
        assert sky.separation(SkyCoord(151.81441452*u.deg,2.82631029*u.deg)).arcsec<1e-3
    assert meta['masked_pixel_count']==mask.size-mask.sum()
    assert meta['coverage_fraction']==mask.mean()
