#!/usr/bin/env bash
# build-jsm.sh — turnkey Linux build of the parent JoyShockMapper fork, encoding
# the recipe from findings/jsm_linux_port.md as an executable. clang for BOTH C
# and C++ is load-bearing (gcc-16 ICEs on SDL3's Wayland C sources); SDL3
# release-3.4.8 is fetched + built from source via CPM. Build dir is git-ignored.
#   usage: build-jsm.sh [BUILD_DIR]   (default: <repo-root>/build-linux)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"   # gamepad/tools -> gamepad -> repo root (the JSM fork)
BUILD="${1:-$ROOT/build-linux}"
test -f "$ROOT/JoyShockMapper/CMakeLists.txt" || { echo "ERR: $ROOT is not the JSM fork root"; exit 1; }
echo "== building JSM: $ROOT  ->  $BUILD =="
cmake -S "$ROOT" -B "$BUILD" -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build "$BUILD" -j
BIN="$BUILD/JoyShockMapper/JoyShockMapper"
if [ -x "$BIN" ]; then echo "OK: $BIN ($(du -h "$BIN" | cut -f1))"; else echo "FAIL: binary not produced"; exit 1; fi
