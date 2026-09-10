param([int]$Jobs = 8)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment -RequireCompiler
& .venv/Scripts/python.exe -c 'import json; from pathlib import Path; records=json.loads(Path("local/aot/prg-captures.json").read_text()); Path("local/aot/battle-capture.json").write_text(json.dumps([next(x for x in records if x["source_file"]=="BATTLE/BATTLE.PRG")]))'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$vsArgs = @('psxrecomp/tools/compile_overlays.py','--captures','local/aot/battle-capture.json','--game-toml','game.toml','--recompiler','psxrecomp/recompiler/build/psxrecomp-game.exe','--runtime-include','psxrecomp/runtime/include','--out-dir','build/runtime/cache','--gcc',$RecompGcc,'--cps','--jobs',"$Jobs",'--force-interior','0x800988BC','--force-interior','0x800B16F4')
if (Test-Path seeds/battle-interiors.json) {
    foreach ($vsEntry in (Get-Content seeds/battle-interiors.json -Raw | ConvertFrom-Json)) {
        if ($vsEntry.pc -notmatch '^0x8[0-9A-Fa-f]{7}$') { throw 'Invalid observed PC' }
        $vsArgs += @('--force-interior', $vsEntry.pc)
    }
}
& .venv/Scripts/python.exe @vsArgs
exit $LASTEXITCODE
