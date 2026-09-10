cmake_minimum_required(VERSION 3.20)
project(VagrantStoryRecomp LANGUAGES C CXX)

set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH "PSXRecomp checkout")
if(NOT EXISTS "${PSXRECOMP_ROOT}/runtime/runtime.cmake")
    message(FATAL_ERROR "Missing PSXRecomp. Run: git submodule update --init")
endif()

option(PSX_RECOMP_UI "Build optional launcher" OFF)
option(PSX_NETPLAY "Build optional netplay" OFF)
option(PSX_REWIND "Build optional rewind" OFF)
option(PSX_ENABLE_VULKAN "Build Vulkan backend" OFF)
option(PSX_DEBUG_TOOLS "Enable loopback development diagnostics" ON)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

psxrecomp_add_game_runtime(psx-runtime
    PRELOADED_MODS_DIR "NONE"
    WINDOW_TITLE "Vagrant Story Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 1
    GEN_MARKER "generated/SLUS_010.40_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_010.40_full_*.c"
)

add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_CURRENT_SOURCE_DIR}/game.toml"
        "$<TARGET_FILE_DIR:psx-runtime>/game.toml"
    COMMENT "Staging game.toml"
    VERBATIM)
