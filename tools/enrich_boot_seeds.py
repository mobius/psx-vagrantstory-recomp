"""Recover boot-EXE callees from audited PRG code ranges, not raw data scans."""
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'local/aot/prg-captures.json').read_text())
seed_path = ROOT / 'seeds/ghidra_funcs.txt'
previous = {int(line, 16) for line in seed_path.read_text(encoding='utf-8-sig').splitlines() if line.startswith('0x')}
found = {}
annotations = {}
boot = ROOT / 'local/disc/SLUS_010.40'
if hashlib.sha1(boot.read_bytes()).hexdigest() != 'fababcfd4325d42f350d95b3472874affeb0e48c':
    raise ValueError('Boot image does not match the reference symbol map')
symbols = (ROOT / 'references/rood-reverse/config/SLUS_010.40/symbol_addrs.txt').read_text(encoding='utf-8')
for match in re.finditer(r'(\w+)\s*=\s*(0x[0-9A-Fa-f]+);\s*//[^\n]*type:func', symbols):
    address = int(match[2], 16)
    if 0x80010000 <= address < 0x80062000:
        annotations[address] = match[1]
for record in records:
    base = int(record['load_addr'], 16)
    data = base64.b64decode(record['bytes_b64'])
    name = f'{base & 0x1fffffff:08X}_{zlib.crc32(data):08X}.ranges'
    manifests = list((ROOT / 'build/runtime/cache/SLUS-01040/gcc').glob(f'*/cg10_f2c33ef6_gcc15c8ed0_f0/{name}'))
    if len(manifests) != 1:
        raise RuntimeError(f'Expected current audited primary manifest for {record["source_file"]}: {name}')
    for match in re.finditer(r'^R ([0-9A-Fa-f]+) ([0-9A-Fa-f]+)$', manifests[0].read_text(), re.M):
        start, length = (int(value, 16) for value in match.groups())
        offset = (start & 0x1fffffff) - (base & 0x1fffffff)
        if offset < 0 or offset+length > len(data) or length % 4:
            raise ValueError('Audited range outside its producer image')
        for delta in range(0, length, 4):
            (word,) = struct.unpack_from('<I', data, offset+delta)
            if word >> 26 != 3:
                continue
            target = 0x80000000 | ((word & 0x3ffffff) << 2)
            if 0x80010000 <= target < 0x80062000:
                found.setdefault(target, set()).add((record['source_file'], start+delta))
combined = previous | set(found) | set(annotations)
added = sorted(combined - previous)
seed_path.write_text('# Initial boot JAL roots plus audited PRG direct-call targets.\n' +
                    '\n'.join(f'0x{value:08X}' for value in sorted(combined)) + '\n', encoding='utf-8')
evidence = [{'target': f'0x{target:08X}', 'reference_function': annotations.get(target),
             'callsites': [{'file': p, 'pc': f'0x{pc:08X}'} for p, pc in sorted(found.get(target, set()))]}
            for target in sorted(set(found) | set(annotations))]
(ROOT / 'local/aot/boot-seed-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
print(json.dumps(dict(previous=len(previous), total=len(combined), added=len(added),
                      rcos=0x80040F24 in combined, rsin=0x80040F28 in combined)))
