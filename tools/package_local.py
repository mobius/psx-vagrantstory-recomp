"""Catalog and package local build artifacts; never stages or uploads anything."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            sha.update(block)
    return sha.hexdigest()

def main():
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output = ROOT/'local/artifacts'/stamp
    runtime = output/'runtime'
    runtime.mkdir(parents=True)
    source = ROOT/'build/runtime'
    executable = 'Vagrant_Story_Recompiled.exe'
    if not (source/executable).is_file():
        raise SystemExit('Build the runtime before packaging')
    shutil.copy2(source/executable, runtime/executable)
    for directory in ('assets', 'bios', 'cache', 'mods'):
        if (source/directory).is_dir():
            shutil.copytree(source/directory, runtime/directory)
    # Inputs and saves are referenced from the project, never duplicated here.
    (runtime/'run-local.ps1').write_text('''param([string]$ProjectRoot = (Resolve-Path "$PSScriptRoot/../../../..").Path)
$ErrorActionPreference = 'Stop'
$env:PSX_OVERLAY_AUTOCOMPILE_OFF = '1'
Set-Location $ProjectRoot
& "$PSScriptRoot/Vagrant_Story_Recompiled.exe" --game "$ProjectRoot/game.toml" --disc "$ProjectRoot/local/disc/Vagrant Story (USA).cue" --bios "$ProjectRoot/local/bios/SCPH1001.BIN" --memcard-dir "$ProjectRoot/local/newgame-probe/saves" --no-launcher --debug-port 18765
exit $LASTEXITCODE
''', encoding='utf-8')
    files = [dict(path=p.relative_to(runtime).as_posix(), bytes=p.stat().st_size, sha256=digest(p))
             for p in sorted(runtime.rglob('*')) if p.is_file()]
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), source_revision=revision,
                    classification='private local development build; not a public release',
                    status='experimental; see STATUS.md', files=files,
                    game_input='local/disc/Vagrant Story (USA).cue', bios_input='local/bios/SCPH1001.BIN',
                    checkpoint='local/newgame-probe/saves/scph1001/state_8001F544_slot07.pst',
                    evidence=['local/newgame-probe/gameplay-hud.png','local/newgame-probe/workers-room.png',
                              'local/newgame-probe/card-result.png','local/handoff-screen.png'])
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (output/'README.txt').write_text('Local development handoff only. Not staged or uploaded.\n'
        'Run runtime/run-local.ps1 from this location; it uses the project\'s existing private disc, BIOS and test saves.\n'
        'If moved elsewhere, pass -ProjectRoot explicitly. Background compilation is disabled for this snapshot.\n'
        'The ZIP intentionally omits disc images, the retail BIOS input, and saves; the executable still contains locally generated code.\n',encoding='utf-8')
    archive=output/'local-build.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for path in sorted(runtime.rglob('*')):
            if path.is_file(): target.write(path,path.relative_to(output))
        target.write(output/'manifest.json','manifest.json')
        target.write(output/'README.txt','README.txt')
    with zipfile.ZipFile(archive) as target:
        if target.testzip() is not None: raise RuntimeError('Archive integrity check failed')
    summary=dict(directory=output.relative_to(ROOT).as_posix(), zip_bytes=archive.stat().st_size,
                 zip_sha256=digest(archive), runtime_files=len(files),
                 dll_count=sum(row['path'].endswith('.dll') for row in files))
    (ROOT/'local/artifacts/latest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
