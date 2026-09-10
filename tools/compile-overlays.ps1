param([int]$Jobs = 8)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment -RequireCompiler
$vsCaptures = if ($env:PSX_OVERLAY_CAPTURES) { $env:PSX_OVERLAY_CAPTURES } else { 'local/overlay_captures.json' }
& .venv/Scripts/python.exe psxrecomp/tools/compile_overlays.py --captures $vsCaptures --game-toml game.toml --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe --runtime-include psxrecomp/runtime/include --out-dir build/runtime/cache --gcc $RecompGcc --cps --jobs $Jobs
exit $LASTEXITCODE
