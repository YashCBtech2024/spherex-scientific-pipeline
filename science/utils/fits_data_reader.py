"""Pure Python FITS image data reader (reads 2D float32 image arrays and int32 flag arrays)."""

from pathlib import Path
import struct
from typing import Tuple, List, Optional
from science.utils.fits_header_reader import read_fits_headers

def read_fits_image_2d(filepath: str | Path, hdu_index: int = 1) -> Tuple[List[List[float]], dict]:
    """Reads a 2D BITPIX=-32 or BITPIX=32 image from the specified HDU."""
    filepath = Path(filepath)
    headers = read_fits_headers(filepath)
    if hdu_index >= len(headers):
        raise IndexError(f"HDU {hdu_index} not found in {filepath} (total HDUs: {len(headers)})")
        
    hdr = headers[hdu_index]["cards"]
    bitpix = int(hdr.get("BITPIX", -32))
    naxis = int(hdr.get("NAXIS", 0))
    if naxis != 2:
        raise ValueError(f"HDU {hdu_index} is not a 2D image (NAXIS={naxis})")
        
    naxis1 = int(hdr.get("NAXIS1", 0))
    naxis2 = int(hdr.get("NAXIS2", 0))
    
    with open(filepath, "rb") as f:
        # Seek past all prior HDUs and current header
        # Re-parse offsets
        current_offset = 0
        for idx in range(hdu_index + 1):
            h = headers[idx]["cards"]
            # Header size: length of header in blocks
            # We count cards
            # Let's count blocks until END
            f.seek(current_offset)
            block_count = 0
            while True:
                block = f.read(2880)
                block_count += 1
                if b'END     ' in block:
                    break
            header_bytes = block_count * 2880
            data_bytes = 0
            h_bitpix = int(h.get("BITPIX", 8))
            h_naxis = int(h.get("NAXIS", 0))
            if h_naxis > 0:
                h_elems = 1
                for ax in range(1, h_naxis + 1):
                    h_elems *= int(h.get(f"NAXIS{ax}", 0))
                raw_bytes = (abs(h_bitpix) // 8) * h_elems
                pcount = int(h.get("PCOUNT", 0))
                gcount = int(h.get("GCOUNT", 1))
                if pcount > 0:
                    raw_bytes += pcount
                raw_bytes *= gcount
                rem = raw_bytes % 2880
                data_bytes = raw_bytes if rem == 0 else raw_bytes + (2880 - rem)
                
            if idx == hdu_index:
                # Seek to start of this HDU data
                data_start = current_offset + header_bytes
                f.seek(data_start)
                break
            else:
                current_offset += header_bytes + data_bytes
                
        # Now read naxis1 * naxis2 elements
        num_pixels = naxis1 * naxis2
        if bitpix == -32:
            raw_data = f.read(num_pixels * 4)
            # Big-endian float (>f)
            flat_pixels = struct.unpack(f">{num_pixels}f", raw_data)
        elif bitpix == 32:
            raw_data = f.read(num_pixels * 4)
            flat_pixels = struct.unpack(f">{num_pixels}i", raw_data)
        else:
            raise NotImplementedError(f"Unsupported BITPIX={bitpix}")
            
    # Reshape to 2D list: [row][col] where row is y (0 to naxis2-1), col is x (0 to naxis1-1)
    grid = []
    for y in range(naxis2):
        row = flat_pixels[y * naxis1 : (y + 1) * naxis1]
        grid.append(list(row))
        
    return grid, hdr
