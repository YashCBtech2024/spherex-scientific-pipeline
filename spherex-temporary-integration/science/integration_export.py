"""Export scientifically honest integration payloads and manifest."""
from pathlib import Path
import csv,json
from datetime import datetime,timezone

EPOCH_META={
 '2025-04-25':('2025-04-25T00:42:57.413',60790.030),
 '2025-05-09':('2025-05-09T03:53:15.489',60804.162),
 '2026-05-26':('2026-05-26T08:40:11.829',61186.361)}

def export_integration(source_dir:Path,outdir:Path)->dict:
    outdir.mkdir(parents=True,exist_ok=True)
    payload=[]
    for epoch,(iso,mjd) in EPOCH_META.items():
        p=source_dir/f'{epoch}_detections_photometry.csv'
        with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        for i,r in enumerate(rows):
            # Contract-shaped provisional record. Unmeasured required values remain null.
            payload.append({'candidate_id':f'SPHX-{epoch}-{i+1:03d}','ra':float(r['ra_deg']),'dec':float(r['dec_deg']),
              'observation_dates':[iso+'Z'],'bands_observed':[], 'displacement_arcsec':None,
              'displacement_uncertainty_arcsec':None,'displacement_significance_sigma':None,
              'delta_brightness_mag':None,'delta_brightness_uncertainty_mag':None,
              'delta_brightness_significance_sigma':None,
              'quality_indicators':['common_coverage','reprojected','preliminary_aperture_photometry'],
              'has_quality_warnings':True,'scientific_interpretation':None,
              'scientific_summary':'Preliminary single-epoch detection; no validated cross-epoch identity or classification.',
              'validation_status':'Inconclusive','provenance':{'epoch':epoch,'source_detection_index':i,
              'flux_Jy_uncorrected':float(r['flux_Jy_uncorrected']),'flux_unc_Jy_empirical':float(r['flux_unc_Jy_empirical']),
              'snr_aperture':float(r['snr_aperture']),'photometry_unit':'Jy, uncorrected aperture sum',
              'uncertainty_note':'Empirical RMS; interpolation covariance omitted.'},
              'api_compatible_without_backend_changes':False})
    payload_path=outdir/'candidate_payloads_provisional.json'
    payload_path.write_text(json.dumps({'records':payload,'required_backend_changes':['allow null scientific metrics and interpretation','accept provenance extension','frontend must render unavailable values safely']},indent=2),encoding='utf-8')
    # Flat CSV suitable for import/mapping; preserve source-specific quantities.
    rows=[]
    for epoch in EPOCH_META:
        with (source_dir/f'{epoch}_detections_photometry.csv').open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f): rows.append({'epoch':epoch,**r})
    csv_path=outdir/'source_measurements_for_import.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['epoch']);wr.writeheader();wr.writerows(rows)
    products=[*source_dir.glob('*'),*Path('data/processed/aligned_validated').glob('*'),csv_path,payload_path]
    def describe(p):
        n=p.name
        purpose=('Per-epoch detections and aperture photometry' if 'detections_photometry' in n else
          'Provisional master coordinate associations' if 'master_associations' in n else
          'Historical candidate positional reassessment' if 'reassessment' in n else
          'Source overlay visualization' if 'overlays' in n else
          'Per-epoch aperture flux visualization' if 'photometry' in n else
          'Common-coverage mask' if 'coverage_mask' in n else
          'Three-epoch aligned image on shared TAN grid' if n.endswith('.fits') else
          'Three-epoch image comparison' if n.endswith('.png') else 'Integration export/metadata')
        units='RA/Dec degrees; flux Jy uncorrected aperture; flux error Jy empirical; separation arcsec' if p.suffix=='.csv' or 'json' in n else ('MJy/sr' if p.suffix=='.fits' else 'image pixels')
        usage='Review or science-side import; not a final classification' if ('candidate' in n or 'association' in n) else 'Data/preview artifact'
        return {'path':str(p),'purpose':purpose,'units':units,'api_usage':usage}
    manifest={'files':[describe(p) for p in sorted(set(products)) if p.is_file()],
      'backend_contract_note':'Current Pydantic CandidateSummary requires non-null float significance/displacement/photometry fields and non-null ScientificCategory. Honest nulls therefore cannot be accepted without model changes.',
      'frontend_note':'Current detail/overview formats significance and magnitude as numeric values; frontend must guard null values.'}
    (outdir/'integration_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest
