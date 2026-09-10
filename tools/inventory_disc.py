"""Inventory a local MODE2/2352 disc and check PRG hashes against rood-reverse."""
import hashlib
import json
import mmap
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory():
    results = []
    with (ROOT / 'local/disc/Vagrant Story (USA).bin').open('rb') as handle:
        with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as image:
            def read(lba, length):
                data = bytearray()
                while len(data) < length:
                    start = lba * 2352 + 24
                    sector = image[start:start + 2048]
                    if len(sector) != 2048:
                        raise ValueError('Truncated disc')
                    data.extend(sector)
                    lba += 1
                return bytes(data[:length])

            pvd = read(16, 2048)
            if pvd[1:6] != b'CD001':
                raise ValueError('Expected ISO9660 in MODE2/2352')
            visited = set()

            def walk(extent, size, prefix=''):
                if extent in visited:
                    raise ValueError('Repeated directory extent')
                visited.add(extent)
                directory = read(extent, size)
                pos = 0
                while pos < len(directory):
                    length = directory[pos]
                    if not length:
                        pos = (pos // 2048 + 1) * 2048
                        continue
                    record = directory[pos:pos + length]
                    if len(record) < 34:
                        raise ValueError('Invalid directory record')
                    pos += length
                    name = record[33:33 + record[32]]
                    if name in (b'\x00', b'\x01'):
                        continue
                    name = name.decode('ascii').split(';')[0]
                    path = prefix + name
                    lba, count = struct.unpack_from('<I', record, 2)[0], struct.unpack_from('<I', record, 10)[0]
                    if record[25] & 2:
                        walk(lba, count, path + '/')
                        continue
                    entry = dict(path=path, lba=lba, size=count)
                    config = ROOT / 'references/rood-reverse/config' / path / 'splat.yaml'
                    if config.is_file():
                        digest = hashlib.sha1(read(lba, count)).hexdigest()
                        expected = re.search(r'^sha1:\s*([0-9a-f]+)', config.read_text(), re.M)
                        entry.update(sha1=digest, reference_match=bool(expected and digest == expected[1]))
                    results.append(entry)

            walk(struct.unpack_from('<I', pvd, 158)[0], struct.unpack_from('<I', pvd, 166)[0])
    output = ROOT / 'local/disc_inventory.json'
    output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    checked = [item for item in results if 'reference_match' in item]
    print(json.dumps(dict(files=len(results), checked=len(checked), matched=sum(item['reference_match'] for item in checked))))
    if any(not item['reference_match'] for item in checked):
        raise SystemExit('Reference hash mismatch')


if __name__ == '__main__':
    inventory()
