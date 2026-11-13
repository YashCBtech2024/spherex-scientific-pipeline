# SPHEREx Three-Epoch Demo

Temporary public integration build using the project's real SPHEREx aligned FITS products and preliminary source catalogues. It is an exploration demo, not a scientifically validated classification service.

## Run locally

From the root of the main repository:

```powershell
.\.venv312\Scripts\python.exe -m streamlit run spherex-temporary-integration/frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

The app starts its copied FastAPI service automatically when `API_URL` is unset or points to loopback. To use a separately started API, set `API_URL` before launching Streamlit.

## Deploy on Streamlit Community Cloud

Choose the public GitHub repository `YashCBtech2024/spherex-scientific-pipeline`, branch `main`, and entrypoint `spherex-temporary-integration/frontend/app.py`. Select Python 3.12. The app and its read-only API run in the same Streamlit service; no API keys are required. The repository-root `requirements.txt` declares the dependencies.

## Included content

- `backend/`, `frontend/`: isolated copies of the teammate apps with temporary integration changes; originals remain untouched.
- `data/raw/`: copies of four source FITS observations.
- `data/processed/`: three-epoch cutouts and validated common-grid FITS/PNG/metadata products.
- `data/catalogues/`: preliminary per-epoch source measurements and provisional association outputs.
- `science/`, `tests/`, `docs/`: copied processing code, tests, and scientific notes.

The interface serves 19 single-epoch detections (5, 7, and 7 for 25 April 2025, 9 May 2025, and 26 May 2026). Flux calibration, band mapping, cross-epoch source identities, Gaia/JPL validation, significance, and classifications are unavailable or incomplete and remain null/unverified. Small positional differences are not evidence of motion. See [`TESTING_REPORT.md`](TESTING_REPORT.md).

The reference repositories are only source material; this directory has no remote and deployment must use the main project repository. No teammate repository is modified by this demo.
