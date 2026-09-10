param([int]$Jobs = 8)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment -RequireCompiler
Checked { cmake -S psxrecomp/recompiler -B psxrecomp/recompiler/build -G Ninja "-DCMAKE_MAKE_PROGRAM=$PWD/.venv/Scripts/ninja.exe" -DCMAKE_BUILD_TYPE=Release -DPSXRECOMP_ENABLE_CHD=OFF }
Checked { cmake --build psxrecomp/recompiler/build --target psxrecomp-game psxrecomp-bios -j $Jobs }
Checked { .venv/Scripts/python.exe psxrecomp/psxrecomp_cli.py generate --project-root . --config game.toml --bios $RecompBios --no-toolchain-download }
Checked { cmake -S . -B build/runtime -G Ninja "-DCMAKE_MAKE_PROGRAM=$PWD/.venv/Scripts/ninja.exe" -DCMAKE_BUILD_TYPE=Release -DPSX_RECOMP_UI=OFF -DPSX_NETPLAY=OFF -DPSX_ENABLE_VULKAN=OFF -DPSX_REWIND=OFF -DPSX_DEBUG_TOOLS=ON }
Checked { cmake --build build/runtime --target psx-runtime -j $Jobs }
