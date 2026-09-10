"""Apply bounded controller input and capture before/after game screenshots."""
import argparse
import json
from pathlib import Path
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument('buttons', nargs='+', choices=['up','right','down','left','triangle','circle','cross','square','start','select','l1','r1','l2','r2'])
parser.add_argument('--seconds', type=float, default=.25)
parser.add_argument('--name', default='input')
parser.add_argument('--repeat', type=int, default=1)
args = parser.parse_args()
if not 0 < args.seconds <= 3 or not 1 <= args.repeat <= 20 or not args.name.replace('-','').replace('_','').isalnum():
    parser.error('Use 0 < seconds <= 3 and an alphanumeric output name')
bits = dict(select=0,start=3,up=4,right=5,down=6,left=7,l2=8,r2=9,l1=10,r1=11,triangle=12,circle=13,cross=14,square=15)
word = 0xffff
for key in args.buttons:
    word &= ~(1 << bits[key])
out = Path(__file__).resolve().parents[1]/'local/newgame-probe'
def command(cmd, **fields):
    with socket.create_connection(('127.0.0.1',18765),timeout=5) as conn:
        conn.sendall((json.dumps(dict(cmd=cmd,**fields))+'\n').encode())
        data=bytearray()
        while chunk:=conn.recv(65536): data.extend(chunk)
    return json.loads(data)
result = {'before':command('screenshot_file',path=str(out/f'{args.name}-before.png'))}
try:
    for index in range(args.repeat):
        result['input'] = command('set_input',buttons=f'{word:04X}')
        time.sleep(args.seconds)
        command('clear_input')
        if index+1 < args.repeat:
            time.sleep(.15)
finally:
    command('clear_input')
time.sleep(.6)
result['after'] = command('screenshot_file',path=str(out/f'{args.name}-after.png'))
(out/f'{args.name}.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
