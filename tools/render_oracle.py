"""Render PCSX-Redux's raw RGB555/RGB24 screenshot buffers as PNG files."""
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
def chunk(kind, payload):
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))

for metadata in sorted((ROOT / 'local/oracle').glob('frame-*.json')):
    if not metadata.stat().st_size:
        continue
    doc = json.loads(metadata.read_text())
    width, height = doc['width'], doc['height']
    raw = metadata.with_suffix('.raw').read_bytes()
    if doc['bpp'] == 0:
        if len(raw) != width * height * 2:
            raise ValueError('RGB555 buffer size mismatch')
        rgb = bytearray()
        for (pixel,) in struct.iter_unpack('<H', raw):
            rgb.extend(((pixel & 31)*255//31, ((pixel >> 5)&31)*255//31, ((pixel >> 10)&31)*255//31))
    elif doc['bpp'] == 1:
        if len(raw) != width * height * 3:
            raise ValueError('RGB24 buffer size mismatch')
        rgb = raw
    else:
        raise ValueError('Unknown pixel format')
    rows = b''.join(b'\0' + rgb[y*width*3:(y+1)*width*3] for y in range(height))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')
    metadata.with_suffix('.png').write_bytes(png)
    print(metadata.with_suffix('.png').name)
