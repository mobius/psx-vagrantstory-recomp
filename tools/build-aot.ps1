param([int]$Jobs = 8)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/common.ps1"
Initialize-RecompEnvironment -RequireCompiler
Checked { .venv/Scripts/python.exe tools/test_prg_map.py }
Checked { .venv/Scripts/python.exe tools/extract_prg_overlays.py }
Checked { .venv/Scripts/python.exe psxrecomp/tools/compile_overlays.py --captures local/aot/prg-captures.json --game-toml game.toml --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe --runtime-include psxrecomp/runtime/include --out-dir build/runtime/cache --gcc $RecompGcc --cps --jobs $Jobs }
Checked { .venv/Scripts/python.exe psxrecomp/tools/aot_overlay_spike/extract_generic.py --only-bios-resident --bios $RecompBios --require-bios-resident --out local/aot/bios-resident.json }
Checked { .venv/Scripts/python.exe psxrecomp/tools/compile_overlays.py --captures local/aot/bios-resident.json --game-toml game.toml --recompiler psxrecomp/recompiler/build/psxrecomp-game.exe --runtime-include psxrecomp/runtime/include --out-dir build/runtime/cache --gcc $RecompGcc --cps --jobs $Jobs }
Checked { .venv/Scripts/python.exe tools/enrich_boot_seeds.py }
Checked { & ./tools/compile-interiors.ps1 -Jobs $Jobs }
Checked { .venv/Scripts/python.exe psxrecomp/psxrecomp_cli.py generate --project-root . --config game.toml --bios $RecompBios --no-toolchain-download }
Checked { cmake --build build/runtime --target psx-runtime -j $Jobs }
