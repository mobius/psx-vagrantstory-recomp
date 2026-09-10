param([switch]$SkipSubmodules)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment -RequireCompiler
Get-Command uv, git -ErrorAction Stop | Out-Null
if (-not $SkipSubmodules) {
    # Optional nested launcher/netplay dependencies are not needed for this build.
    Checked { git submodule update --init }
}
Checked { uv venv --python 3.13 .venv }
Checked { uv pip install --python .venv/Scripts/python.exe -r requirements-tools.txt }
Write-Host 'Local tool environment is ready. Stage your own inputs with tools/prepare-inputs.ps1.'
