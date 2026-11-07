"""FITS file inspection and metadata utilities for SPHEREx level 2 observations."""

from pathlib import Path
from typing import Dict, Any, Optional
import json

def get_fits_summary(fits_path: str | Path) -> Dict[str, Any]:
    """Inspect basic FITS header information without relying on heavy external dependencies."""
    # We can inspect using astropy.io.fits once installed, or raw header reading if needed.
    fits_path = Path(fits_path)
    if not fits_path.exists():
        raise FileNotFoundError(f"FITS file not found: {fits_path}")
    
    return {
        "filename": fits_path.name,
        "size_bytes": fits_path.stat().st_size,
        "path": str(fits_path.resolve())
    }
