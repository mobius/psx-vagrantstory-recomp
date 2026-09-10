"""Bounded headless boot; logs and optional debug screenshot remain local."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--seconds', type=int, default=20)
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
exe = ROOT / 'build/runtime/Vagrant_Story_Recompiled.exe'
command = [str(exe), '--headless', '--game', str(ROOT / 'game.toml'), '--disc', str(ROOT / 'local/disc/Vagrant Story (USA).cue'), '--bios', str(ROOT / 'local/bios/SCPH1001.BIN'), '--memcard-dir', str(ROOT / 'local/smoke-saves'), '--debug-port', '18765']
environment = dict(os.environ, PYTHONUTF8='1', PSX_OVERLAY_CAPTURES=str(ROOT / 'local/overlay_captures.json'), PSX_OVERLAY_AUTOCOMPILE_OFF='1')
with (ROOT / 'local/smoke.log').open('wb') as log:
    process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    result = {'pid': process.pid}
    try:
        try:
            result['exit_code'] = process.wait(timeout=args.seconds)
        except subprocess.TimeoutExpired:
            result['alive_after_seconds'] = args.seconds
        if args.debug and process.poll() is None:
            responses = []
            result['debug_responses'] = responses
            for request in [{'id': 1, 'cmd': 'frame'}, {'id': 2, 'cmd': 'screenshot_file', 'path': str(ROOT / 'local/smoke.png')}]:
                with socket.create_connection(('127.0.0.1', 18765), timeout=5) as conn:
                    stream = conn.makefile('rwb')
                    stream.write((json.dumps(request) + '\n').encode())
                    stream.flush()
                    responses.append(stream.readline().decode(errors='replace').strip())
    except (OSError, TimeoutError) as error:
        result['debug_error'] = str(error)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        result['final_exit_code'] = process.returncode
(ROOT / 'local/smoke-result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
