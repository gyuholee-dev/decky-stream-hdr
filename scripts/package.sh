#!/bin/sh
# Assembles the plugin release zip: release/decky-stream-hdr-<version>.zip
#
#   scripts/package.sh            needs dist/ (yarn build) and backend/out/sdl_hdr_shim.so (make -C backend)
#   scripts/package.sh --no-shim  skips the injection library, only useful to check the zip layout
#
# The staged plugin folder is left in release/stage/decky-stream-hdr for scripts/install-dev.sh.
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

no_shim=0
[ "${1:-}" = "--no-shim" ] && no_shim=1

version=$(sed -n 's/^ *"version": *"\([^"]*\)".*/\1/p' package.json | head -1)

if [ ! -f dist/index.js ]; then
    echo "dist/index.js is missing. Run 'yarn build' first." >&2
    exit 1
fi
if [ "$no_shim" = 0 ] && [ ! -f backend/out/sdl_hdr_shim.so ]; then
    echo "backend/out/sdl_hdr_shim.so is missing. Run 'make -C backend' on a Linux machine first." >&2
    exit 1
fi

stage=release/stage/decky-stream-hdr
rm -rf release/stage
mkdir -p "$stage/bin"
cp -R dist py_modules "$stage/"
find "$stage" -name __pycache__ -type d -prune -exec rm -rf {} +
cp main.py plugin.json package.json LICENSE README.md "$stage/"
if [ "$no_shim" = 0 ]; then
    cp backend/out/sdl_hdr_shim.so "$stage/bin/"
fi

zip_path="release/decky-stream-hdr-$version.zip"
rm -f "$zip_path"
(cd release/stage && python3 -m zipfile -c "../decky-stream-hdr-$version.zip" decky-stream-hdr)
echo "Created $zip_path"
