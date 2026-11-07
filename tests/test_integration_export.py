import json
from pathlib import Path
from science.integration_export import export_integration

ROOT=Path(__file__).resolve().parents[1]

def test_exported_payload_keeps_unmeasured_values_null(tmp_path):
    export_integration(ROOT/'data/catalogues/reprocessed',tmp_path)
    data=json.loads((tmp_path/'candidate_payloads_provisional.json').read_text())
    assert data['records']
    for r in data['records']:
        assert r['displacement_significance_sigma'] is None
        assert r['delta_brightness_significance_sigma'] is None
        assert r['scientific_interpretation'] is None
        assert r['validation_status']=='Inconclusive'
        assert not r['api_compatible_without_backend_changes']
    manifest=json.loads((tmp_path/'integration_manifest.json').read_text())
    assert any('source_measurements_for_import.csv' in f['path'] for f in manifest['files'])
