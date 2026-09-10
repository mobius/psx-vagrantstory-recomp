"""Bounded normal controller presses with screenshots for manual verification."""
import argparse
import json
from pathlib import Path
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument('--count', type=int, default=8)
parser.add_argument('--button', choices=['circle', 'cross', 'start'], default='cross')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
out = root / 'local/newgame-probe'
buttons = {'circle': 0xDFFF, 'cross': 0xBFFF, 'start': 0xFFF7}
def command(cmd, **kwargs):
    with socket.create_connection(('127.0.0.1', 18765), timeout=5) as connection:
        connection.sendall((json.dumps(dict(cmd=cmd, **kwargs))+'\n').encode())
        chunks = []
        while chunk := connection.recv(65536):
            chunks.append(chunk)
    return json.loads(b''.join(chunks))
result = []
for index in range(args.count):
    command('set_input', buttons=f'{buttons[args.button]:04X}')
    time.sleep(.25)
    command('clear_input')
    time.sleep(.75)
    frame = command('frame')['frame']
    result.append(command('screenshot_file', path=str(out / f'advance-{frame:07d}.png')))
command('clear_input')
print(json.dumps(result, indent=2))
