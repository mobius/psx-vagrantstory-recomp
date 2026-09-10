"""Build static overlay recipes from hash-matched rood-reverse segment maps.

Disc bytes and generated recipes stay in local/. No runtime observation is
fabricated: static seeds retain separate provenance and executed_pcs is empty.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'psxrecomp/tools/aot_overlay_spike'))
import extract_generic as generic

CODE_TYPES = {'c', 'asm', 'hasm'}


def segment_map(document, file_size):
    segments = document['segments']
    code_segments = [s for s in segments if isinstance(s, dict) and s.get('type') == 'code']
    if len(code_segments) != 1:
        raise ValueError('Expected one positioned code segment')
    segment = code_segments[0]
    if segment.get('start') != 0:
        raise ValueError('Nonzero file start requires explicit mapping support')
    base = segment['vram']
    if not 0x80010000 <= base < 0x80200000 or base + file_size > 0x80200000:
        raise ValueError('Program outside PS1 RAM')
    rows = []
    for row in segment['subsegments']:
        start, kind = (row['start'], row['type']) if isinstance(row, dict) else row[:2]
        if not isinstance(start, int) or not 0 <= start <= file_size:
            raise ValueError('Invalid segment offset')
        if rows and start <= rows[-1][0]:
            raise ValueError('Segment offsets must strictly increase')
        rows.append((start, kind))
    spans, entries = [], []
    for index, (start, kind) in enumerate(rows):
        end = rows[index + 1][0] if index + 1 < len(rows) else file_size
        if kind not in CODE_TYPES:
            continue
        # Auto-linked C objects may end with byte-aligned data. A partial final
        # word cannot be an instruction; keep the bytes in the image, not roots.
        if index + 1 == len(rows):
            end &= ~3
        if start % 4 or end % 4 or end <= start:
            raise ValueError('Unaligned or empty code span')
        entries.append(base + start)
        if spans and spans[-1][1] == base + start:
            spans[-1] = (spans[-1][0], base + end)
        else:
            spans.append((base + start, base + end))
    if not spans:
        raise ValueError('No declared executable spans')
    return base, spans, entries


def recipe_for(path, data, document):
    digest = hashlib.sha1(data).hexdigest()
    if digest != document['sha1']:
        raise ValueError(f'{path}: disc does not match reference SHA1')
    base, spans, segment_entries = segment_map(document, len(data))
    def in_code(address):
        return address % 4 == 0 and any(lo <= address < hi for lo, hi in spans)
    roots = set(segment_entries)
    direct = set()
    for lo, hi in spans:
        block = data[lo - base:hi - base]
        roots.update(generic.prologues(block, lo))
        # Only calls originating in confirmed executable spans nominate roots.
        direct.update(generic.jal_targets(block))
    roots.update(address for address in direct if in_code(address))
    dispatch = {address for address in generic.pointer_table_targets(data, base) if in_code(address)}
    page, image = generic.page_aligned_region(base, data)
    record = generic.rec(page, image, sorted(roots), sorted(dispatch), producer_ranges=spans)
    record['source_file'] = path
    record['source_sha1'] = digest
    record['source_load_address'] = f'0x{base:08X}'
    record['strict_producer_ranges'] = True
    metadata = dict(path=path, sha1=digest, size=len(data), load_address=f'0x{base:08X}',
                    code_bytes=sum(hi-lo for lo, hi in spans), roots=len(roots),
                    dispatch_candidates=len(dispatch), code_spans=[list(s) for s in spans])
    return record, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='local/aot/prg-captures.json')
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'local/disc_inventory.json').read_text())
    programs = [f for f in inventory if f['path'].endswith('.PRG') and f['size']]
    records, metadata = [], []
    with (ROOT / 'local/disc/Vagrant Story (USA).bin').open('rb') as source:
        with mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as image:
            for entry in programs:
                data = b''.join(image[lba * 2352 + 24:lba * 2352 + 24 + 2048]
                                for lba in range(entry['lba'], entry['lba'] + (entry['size'] + 2047)//2048))[:entry['size']]
                if len(data) != entry['size']:
                    raise ValueError('Truncated disc')
                config = ROOT / 'references/rood-reverse/config' / entry['path'] / 'splat.yaml'
                record, info = recipe_for(entry['path'], data, yaml.safe_load(config.read_text()))
                records.append(record)
                metadata.append(info)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records), encoding='utf-8')
    output.with_name('prg-inventory.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(dict(programs=len(records), code_bytes=sum(m['code_bytes'] for m in metadata),
                          roots=sum(m['roots'] for m in metadata), output=str(output))))


if __name__ == '__main__':
    main()
