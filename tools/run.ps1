param(
    [switch]$Headless,
    [string]$MemcardDir = 'local/saves',
    [ValidateRange(1,65535)][int]$DebugPort = 18765
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment
$program = Join-Path $PWD 'build/runtime/Vagrant_Story_Recompiled.exe'
if (-not (Test-Path $program)) { throw '请先运行 tools/build.ps1 完成构建。' }
$env:PSX_OVERLAY_CAPTURES = "$PWD/local/overlay_captures.json"
$vsSavePath = if ([IO.Path]::IsPathRooted($MemcardDir)) { $MemcardDir } else { Join-Path $RecompRoot $MemcardDir }
$options = @('--game', "$PWD/game.toml", '--disc', "$PWD/local/disc/Vagrant Story (USA).cue", '--bios', $RecompBios, '--no-launcher', '--memcard-dir', $vsSavePath, '--debug-port', "$DebugPort")
if ($Headless) { $options += '--headless' }
& $program @options
exit $LASTEXITCODE
