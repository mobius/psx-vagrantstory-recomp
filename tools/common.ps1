function Initialize-RecompEnvironment {
    param([switch]$RequireCompiler)
    $script:RecompRoot = Split-Path $PSScriptRoot -Parent
    Set-Location $script:RecompRoot
    $env:PYTHONUTF8 = '1'
    $env:UV_CACHE_DIR = Join-Path $script:RecompRoot 'local/uv-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $script:RecompRoot 'local/uv-python'
    $env:CCACHE_DIR = Join-Path $script:RecompRoot 'local/ccache'
    $env:Path = "$(Join-Path $script:RecompRoot '.venv/Scripts');$env:Path"
    $script:RecompBios = Join-Path $script:RecompRoot 'local/bios/SCPH1001.BIN'
    if ($RequireCompiler -or $env:PSXRECOMP_GCC) {
        $vsCompiler = if ($env:PSXRECOMP_GCC) { Get-Command $env:PSXRECOMP_GCC -ErrorAction Stop } else { Get-Command gcc -ErrorAction Stop }
        $script:RecompGcc = $vsCompiler.Source
        $env:Path = "$(Split-Path $script:RecompGcc -Parent);$env:Path"
    }
}

function Checked {
    param([scriptblock]$Command)
    $global:LASTEXITCODE = 0
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" }
}
