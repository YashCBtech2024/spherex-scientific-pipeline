import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests


BACKEND_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def api_base_url():
    """Start a temporary loopback Uvicorn process for real HTTP integration tests."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=BACKEND_ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    try:
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Temporary API process exited early with code {process.returncode}")
            try:
                if requests.get(base + "/api/v1/health", timeout=1).ok:
                    break
            except requests.RequestException:
                time.sleep(0.25)
        else:
            raise RuntimeError("Temporary API did not become healthy within 90 seconds")
        yield base
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
