# Verified Python Environment

**Environment:** existing `.venv312` (Python 3.12.0, Windows, 64-bit)  
**Requirements source:** repository `requirements.txt`  
**Verification:** 2026-11-07

All required package imports passed in one Python process. `python -m pip check` returned `No broken requirements found.` No environment recreation was performed. Previously working NumPy, Astropy, Matplotlib, and Pillow were retained. The interrupted requirements installation was resumed; missing dependencies were installed into this environment.

## Direct requirements and verified versions

| Requirement | Installed version |
|---|---:|
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| astropy | 8.0.2 |
| photutils | 3.1.1 |
| astroquery | 0.4.11 |
| matplotlib | 3.11.2 |
| pandas | 3.1.1 |
| reproject | 0.21.0 |
| scikit-image | 0.26.0 |
| pillow | 13.0.0 |
| fastapi | 0.162.0 |
| uvicorn | 0.54.0 |
| pydantic | 2.14.3 |
| python-multipart | 0.0.33 |
| pytest | 9.2.0 |
| pytest-asyncio | 1.4.1.post1 |

## Import verification

The following imports completed successfully: `numpy`, `scipy`, `astropy`, `photutils`, `astroquery`, `matplotlib`, `pandas`, `reproject`, `skimage`, `PIL`, `fastapi`, `uvicorn`, `pydantic`, `multipart`, `pytest`, and `pytest_asyncio`.

## Full installed package lock snapshot

```text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.16.0
astropy==8.0.2
astropy_healpix==2.0.1
astropy-iers-data==0.2026.11.2.0.34.55
astroquery==0.4.11
beautifulsoup4==4.15.0
certifi==2026.10.23
charset-normalizer==3.5.2
click==8.5.1
cloudpickle==3.1.2
colorama==0.4.6
contourpy==1.4.0
cycler==0.12.1
dask==2026.8.0
dask-image==2026.5.0
donfig==0.8.1.post1
fastapi==0.162.0
fonttools==4.68.0
fsspec==2026.9.0
google-crc32c==1.9.0
h11==0.16.0
html5lib==1.1
httptools==0.9.0
idna==3.20
ImageIO==2.38.1
iniconfig==2.3.1
jaraco.classes==3.4.0
jaraco.context==6.1.2
jaraco.functools==4.6.0
keyring==25.7.0
kiwisolver==1.5.1
lazy-loader==0.6
locket==1.0.0
matplotlib==3.11.2
more-itertools==11.2.1
msgspec==0.22.0
networkx==3.7
numcodecs==0.17.1
numpy==2.5.4
opentelemetry-api==1.45.2
packaging==26.3
pandas==3.1.1
partd==1.4.2
pillow==13.0.0
PIMS==0.7
pip==23.2.1
pluggy==1.7.0
PyAVM==0.9.9
pydantic==2.14.3
pydantic_core==2.50.4
pyerfa==2.0.1.5
Pygments==2.21.0
pyparsing==3.3.3
pytest==9.2.0
pytest-asyncio==1.4.1.post1
python-dateutil==4.0.0
python-dotenv==1.2.4
python-multipart==0.0.33
pyvo==1.10.0
pywin32-ctypes==0.2.3
PyYAML==6.0.3
reproject==0.21.0
requests==2.34.2
scikit-image==0.26.0
scipy==1.18.1
six==1.17.0
slicerator==1.1.0
soupsieve==4.0.1
starlette==1.10.0
tifffile==2026.10.15
toolz==1.2.0
typing_extensions==4.16.0
typing-inspection==0.4.5
tzdata==2026.6
urllib3==2.8.0
uvicorn==0.54.0
watchfiles==1.3.0
webencodings==0.6.1
websockets==17.4
zarr==3.4.2
```
