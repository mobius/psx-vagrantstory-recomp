"""Record observed dispatch entries whose live BATTLE bytes match the disc."""
import base64
import hashlib
import json
from pathlib import Path
import re
import socket

ROOT = Path(__file__).resolve().parents[1]
def command(cmd, **fields):
    with socket.create_connection(('127.0.0.1', 18765), timeout=5) as conn:
        conn.sendall((json.dumps(dict(cmd=cmd, **fields))+'\n').encode())
        data = bytearray()
        while chunk := conn.recv(65536):
            data.extend(chunk)
    return json.loads(data)

battle = next(x for x in json.loads((ROOT/'local/aot/prg-captures.json').read_text())
              if x['source_file'] == 'BATTLE/BATTLE.PRG')
base = int(battle['load_addr'], 16)
image = base64.b64decode(battle['bytes_b64'])
spans = [(int(x['start'], 16), int(x['end'], 16)) for x in battle['producer_ranges']]
served = set()
for path in (ROOT/'build/runtime/cache/SLUS-01040/gcc').rglob('*.ranges'):
    served.update(int(x,16) | 0x80000000 for x in re.findall(r'^F ([0-9A-Fa-f]+)', path.read_text(), re.M))
stats = command('dirty_ram_stats')
(ROOT/'local/newgame-probe/dirty-current.json').write_text(json.dumps(stats))
frame = command('frame')['frame']
path = ROOT/'seeds/battle-interiors.json'
evidence = json.loads(path.read_text()) if path.exists() else []
known = {int(row['pc'],16) for row in evidence}
added = []
for item in sorted(stats['per_pc'], key=lambda x:x['insns'], reverse=True):
    pc = int(item['pc'],16) | 0x80000000
    if not item.get('entries') or item['insns'] < 10000 or pc in served or pc in known:
        continue
    if not any(lo <= pc and pc+64 <= hi for lo,hi in spans):
        continue
    live = bytes.fromhex(command('read_ram', addr=f'{pc:08X}', len=64)['hex'])
    if live != image[pc-base:pc-base+64]:
        continue
    row = dict(pc=f'0x{pc:08X}', source='BATTLE/BATTLE.PRG',
               source_sha1=battle['source_sha1'], observed_frame=frame,
               dispatch_entries=item['entries'], matching_prefix_sha256=hashlib.sha256(live).hexdigest())
    evidence.append(row)
    added.append(row['pc'])
    if len(added) >= 16:
        break
path.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print(json.dumps(dict(added=added,total=len(evidence))))
