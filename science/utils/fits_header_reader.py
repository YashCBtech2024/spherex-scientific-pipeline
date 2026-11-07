"""Pure Python FITS header reader (zero external dependencies).
Reads primary and extension HDU headers from FITS files.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional

def read_fits_headers(filepath: str | Path) -> List[Dict[str, Any]]:
    """Reads all header blocks from a FITS file and returns a list of dictionaries per HDU."""
    filepath = Path(filepath)
    hdus = []
    
    with open(filepath, 'rb') as f:
        hdu_idx = 0
        while True:
            header_cards = {}
            cards_list = []
            block_bytes_read = 0
            found_end = False
            
            while not found_end:
                block = f.read(2880)
                if not block or len(block) < 2880:
                    break
                block_bytes_read += 2880
                
                # Each block has 36 cards of 80 characters
                for i in range(0, 2880, 80):
                    card = block[i:i+80].decode('ascii', errors='replace')
                    key = card[:8].strip()
                    if key == 'END':
                        found_end = True
                        break
                    if key:
                        val_comment = card[8:].strip()
                        if val_comment.startswith('='):
                            val_comment = val_comment[1:].strip()
                            if '/' in val_comment:
                                val_part, comment_part = val_comment.split('/', 1)
                                val = val_part.strip().strip("'").strip()
                                comment = comment_part.strip()
                            else:
                                val = val_comment.strip("'").strip()
                                comment = ""
                        else:
                            val = ""
                            comment = val_comment
                        header_cards[key] = val
                        cards_list.append((key, val, comment))
            
            if not cards_list and not header_cards:
                break
                
            hdus.append({
                "hdu_index": hdu_idx,
                "cards": header_cards,
                "cards_list": cards_list
            })
            hdu_idx += 1
            
            # Skip data block to reach next HDU
            bitpix = int(header_cards.get('BITPIX', 8))
            naxis = int(header_cards.get('NAXIS', 0))
            data_size = 0
            if naxis > 0:
                num_elements = 1
                for ax in range(1, naxis + 1):
                    num_elements *= int(header_cards.get(f'NAXIS{ax}', 0))
                data_size = abs(bitpix) // 8 * num_elements
                # PCOUNT and GCOUNT for table/extension data
                pcount = int(header_cards.get('PCOUNT', 0))
                gcount = int(header_cards.get('GCOUNT', 1))
                if pcount > 0:
                    data_size += pcount
                data_size *= gcount
                
                # FITS data blocks are padded to multiples of 2880 bytes
                remainder = data_size % 2880
                if remainder != 0:
                    data_size += (2880 - remainder)
                    
                f.seek(data_size, 1) # Seek relative to current position
                
    return hdus

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        headers = read_fits_headers(sys.argv[1])
        for h in headers:
            print(f"HDU {h['hdu_index']}:")
            for k in ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'CTYPE1', 'CTYPE2', 'CRVAL1', 'CRVAL2', 'DATE-OBS', 'TELESCOP', 'INSTRUME']:
                if k in h['cards']:
                    print(f"  {k} = {h['cards'][k]}")
