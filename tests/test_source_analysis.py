from pathlib import Path
import numpy as np
from astropy.io import fits
from science.source_analysis import detect_photometer, EPOCHS

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/aligned_validated'

def test_masked_detection_photometry_all_epochs():
    mask=fits.getdata(DATA/'three_epoch_common_coverage_mask.fits').astype(bool)
    for epoch in EPOCHS:
        rows=detect_photometer(DATA/f'{epoch}_common_aligned.fits',mask)
        assert rows
        for r in rows:
            x,y=round(r['x_pixel']),round(r['y_pixel'])
            assert mask[y,x]
            assert np.isfinite(r['flux_Jy_uncorrected'])
            assert r['flux_unc_Jy_empirical']>0
            assert r['snr_aperture']>0
