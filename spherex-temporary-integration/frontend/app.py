"""Temporary integrated viewer; starts its local API when one is not configured."""

import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import streamlit as st

from common import API_URL


@st.cache_resource
def _ensure_backend(api_url: str):
    """Run the copied FastAPI service in-process for a self-contained demo.

    A separately configured API_URL remains supported. When the default loopback
    URL is used (as on Streamlit Community Cloud), start the local read-only API
    against the bundled products. This does not change any scientific files.
    """
    parsed = urlparse(api_url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return None
    health_url = f"{api_url.rstrip('/')}/api/v1/health"
    try:
        if requests.get(health_url, timeout=2).ok:
            return None
    except requests.RequestException:
        pass

    app_root = Path(__file__).resolve().parents[1]
    backend_root = app_root / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    import uvicorn

    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8000
    config = uvicorn.Config(
        "backend.main:app", host=host, port=port, log_level="warning", access_log=False
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="spherex-api", daemon=True)
    thread.start()
    for _ in range(100):
        if not thread.is_alive():
            raise RuntimeError("The bundled SPHEREx API server stopped during startup.")
        try:
            if requests.get(health_url, timeout=1).ok:
                return server
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError("Timed out waiting for the bundled SPHEREx API to become ready.")

st.set_page_config(page_title="SPHEREx Scientific Integration Test", page_icon="🌌", layout="wide")
try:
    _ensure_backend(API_URL)
except Exception as exc:
    st.error(f"Could not start the bundled scientific API: {exc}")
st.title("SPHEREx · Three-epoch test field")
st.caption("Temporary integration build using the project's real aligned FITS products and preliminary source catalogues.")

navigation = st.navigation([
    st.Page("pages/science_viewer.py", title="Sky viewer", default=True),
    st.Page("pages/source_detail.py", title="Source detections", url_path="detections"),
])
navigation.run()
