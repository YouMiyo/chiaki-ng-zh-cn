#!/usr/bin/env bash
set -euo pipefail
if [[ "${ALLOW_LEGACY_SDK:-0}" != "1" ]]; then
    echo 'This legacy developer build may bundle different runtime libraries. Use zh-windows.yml for an official-runtime-aligned package.' >&2
    echo 'For intentional SDK experiments only, set ALLOW_LEGACY_SDK=1.' >&2
    exit 1
fi
cd "$(dirname "$0")/.."
prefix="${MINGW_PREFIX:-/ucrt64}"
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-2}"
python scripts/check-zh-translations.py
cmake -S . -B build-zh -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCHIAKI_ENABLE_CLI=OFF -DCHIAKI_ENABLE_TESTS=OFF \
    -DCHIAKI_ENABLE_STEAMDECK_NATIVE=OFF
cmake --build build-zh --target chiaki --parallel "$CMAKE_BUILD_PARALLEL_LEVEL"
scripts/deploy-windows-msys2.sh dist-zh build-zh/gui/chiaki.exe \
    "$PWD/build-zh/third-party/cpp-steam-tools" "$prefix" gui/src/qml
mkdir -p dist-zh/translations
cp "$prefix/share/qt6/translations/qtbase_zh_CN.qm" dist-zh/translations/
cp COPYING README.zh-CN.md dist-zh/
printf '[Paths]\nTranslations=translations\n' > dist-zh/qt.conf
printf 'Upstream: v1.10.1\nSource commit: %s\nBuild UTC: %s\n' \
    "$(git rev-parse HEAD)" "$(date -u +%FT%TZ)" > dist-zh/BUILD-INFO.txt
pacman -Q | grep -E '(qt6-|ffmpeg|libplacebo|gcc|sdl3|SDL2|openssl|curl)' >> dist-zh/BUILD-INFO.txt
printf '\nSDL3 and sdl2-compat are built using the versions pinned in scripts/build-sdl2-compat.sh.\n' >> dist-zh/BUILD-INFO.txt
