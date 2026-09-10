param(
    [Parameter(Mandatory = $true)][string]$Disc,
    [Parameter(Mandatory = $true)][string]$Bios
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment
$vsCue = (Resolve-Path -LiteralPath $Disc).Path
$vsBios = (Resolve-Path -LiteralPath $Bios).Path
$vsCueText = Get-Content -LiteralPath $vsCue -Raw
$vsFiles = [regex]::Matches($vsCueText, '(?im)^\s*FILE\s+"([^"]+)"\s+BINARY\s*$')
if ($vsFiles.Count -ne 1 -or ([regex]::Matches($vsCueText, '(?im)^\s*TRACK\s+')).Count -ne 1 -or $vsCueText -notmatch '(?im)^\s*TRACK\s+01\s+MODE2/2352\s*$' -or $vsCueText -notmatch '(?im)^\s*INDEX\s+01\s+00:00:00\s*$') {
    throw 'Only the verified single-track USA MODE2/2352 dump is supported.'
}
$vsCueDir = Split-Path $vsCue -Parent
$vsBin = [IO.Path]::GetFullPath((Join-Path $vsCueDir $vsFiles[0].Groups[1].Value))
$vsPrefix = $vsCueDir.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
if (-not $vsBin.StartsWith($vsPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The BIN reference must remain inside the CUE directory.'
}
if ((Get-FileHash -LiteralPath $vsBin -Algorithm SHA1).Hash -ne '38C63DB6C49A06B91D87CD5A4E31B1EC68FE212C') { throw 'Disc SHA1 mismatch.' }
if ((Get-FileHash -LiteralPath $vsBios -Algorithm SHA256).Hash -ne '71AF94D1E47A68C11E8FDB9F8368040601514A42A5A399CDA48C7D3BFF1E99D3') { throw 'SCPH1001 BIOS SHA256 mismatch.' }
New-Item -ItemType Directory local/disc, local/bios -Force | Out-Null
$vsTargetBin = Join-Path $RecompRoot 'local/disc/Vagrant Story (USA).bin'
if ($vsBin -ne $vsTargetBin) { Copy-Item -LiteralPath $vsBin -Destination $vsTargetBin }
if ($vsBios -ne $RecompBios) { Copy-Item -LiteralPath $vsBios -Destination $RecompBios }
Set-Content -Encoding ascii 'local/disc/Vagrant Story (USA).cue' @'
FILE "Vagrant Story (USA).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
'@
Checked { .venv/Scripts/python.exe psxrecomp/tools/new_project_layout/probe_disc.py 'local/disc/Vagrant Story (USA).cue' --write-boot-exe local/disc --json-out local/disc_probe.json }
Checked { .venv/Scripts/python.exe tools/inventory_disc.py }
Write-Host 'Verified local inputs staged. Existing curated game.toml and seeds were preserved.'
