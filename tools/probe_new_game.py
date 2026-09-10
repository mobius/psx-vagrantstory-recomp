"""Drive real Start input before the accelerated title's inactivity timeout."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--keep', action='store_true')
parser.add_argument('--seconds', type=int, default=60)
args = parser.parse_args()
out = ROOT / 'local/newgame-probe'
out.mkdir(parents=True, exist_ok=True)

def command(cmd, **fields):
    with socket.create_connection(('127.0.0.1', 18765), timeout=5) as conn:
        conn.sendall((json.dumps(dict(cmd=cmd, **fields)) + '\n').encode())
        data = bytearray()
        while chunk := conn.recv(65536):
            data.extend(chunk)
    return json.loads(data)

environment = dict(os.environ, PYTHONUTF8='1', PSX_OVERLAY_AUTOCOMPILE_OFF='1',
                   PSX_OVERLAY_CAPTURES=str(out / 'overlay_captures.json'))
environment['PATH'] = str(ROOT / '.venv/Scripts') + ';' + environment['PATH']
options = [str(ROOT / 'build/runtime/Vagrant_Story_Recompiled.exe'), '--headless',
           '--game', str(ROOT / 'game.toml'), '--bios', str(ROOT / 'local/bios/SCPH1001.BIN'),
           '--memcard-dir', str(out / 'saves'), '--debug-port', '18765']
result = {'new_game_confirmed': False, 'samples': []}
with (out / 'runtime.log').open('wb') as log:
    process = subprocess.Popen(options, cwd=out, env=environment, stdout=log,
                               stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    (out / 'pid.txt').write_text(str(process.pid))
    result['pid'] = process.pid
    start = time.monotonic()
    try:
        while True:
            if process.poll() is not None:
                raise RuntimeError(f'Runtime exited: {process.returncode}')
            try:
                command('ping')
                break
            except (OSError, ValueError):
                if time.monotonic() - start > 20:
                    raise RuntimeError('Debug interface not ready')
                time.sleep(.1)
        command('set_input', buttons='FFF7')
        confirmed_at = None
        while time.monotonic() - start < args.seconds:
            frame = command('frame')['frame']
            scene = bytes.fromhex(command('read_ram', addr='80061068', len=16)['hex'])
            flags = bytes.fromhex(command('read_ram', addr='80061598', len=16)['hex'])
            result['samples'].append(dict(frame=frame, scene=scene[:2].hex(), flags=flags[12:15].hex()))
            if scene[:2] == b'\x01\x00' and flags[13] == 0 and not result['new_game_confirmed']:
                result['new_game_confirmed'] = True
                result['confirmed_frame'] = frame
                command('clear_input')
                confirmed_at = time.monotonic()
            if confirmed_at and time.monotonic() - confirmed_at >= 12:
                break
            time.sleep(.4)
        command('clear_input')
        result['screenshot'] = command('screenshot_file', path=str(out / 'screen.png'))
        result['capture'] = command('overlay_capture_dump')
        (out / 'native-status.json').write_text(json.dumps(command('overlay_loader_status'), indent=2))
    except Exception as error:
        result['error'] = str(error)
    finally:
        if not args.keep and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        result['running'] = process.poll() is None
(out / 'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps({key: value for key, value in result.items() if key != 'samples'}, indent=2))
