#!/bin/sh
# Builds everything on this machine and installs the plugin into Decky Loader.
# Run it on the Linux client from a clone of this repository:
#
#   git pull && sh scripts/install-dev.sh [plugins-dir]     default plugins dir: ~/homebrew/plugins
#
# Needs: git, node, yarn, a C compiler (gcc or cc), python3 and sudo. make is optional.
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugins_dir=${1:-"$HOME/homebrew/plugins"}

missing=""
for tool in node yarn python3 sudo; do
    command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
done
compiler=""
for candidate in gcc cc; do
    if command -v "$candidate" >/dev/null 2>&1; then compiler=$candidate; break; fi
done
[ -n "$compiler" ] || missing="$missing gcc"
if [ -n "$missing" ]; then
    echo "Missing tools:$missing" >&2
    echo "Install them with your package manager first (on Arch-based systems such as CachyOS: sudo pacman -S nodejs yarn gcc python)." >&2
    exit 1
fi

if [ ! -d "$plugins_dir" ]; then
    echo "The plugins folder '$plugins_dir' does not exist. Is Decky Loader installed?" >&2
    echo "If it lives somewhere else, pass the folder: sh scripts/install-dev.sh <plugins folder>" >&2
    exit 1
fi

echo "Building the frontend"
(cd "$root" && yarn install --frozen-lockfile && yarn build)

echo "Building the injection library"
if command -v make >/dev/null 2>&1; then
    make -C "$root/backend"
else
    # Same command as backend/Makefile, for machines without make.
    mkdir -p "$root/backend/out"
    "$compiler" -shared -fPIC -O2 -o "$root/backend/out/sdl_hdr_shim.so" "$root/backend/src/sdl_hdr_shim.c" -ldl
fi

echo "Packaging"
sh "$root/scripts/package.sh"

echo "Installing into $plugins_dir/decky-stream-hdr (sudo may ask for your password)"
sudo rm -rf "$plugins_dir/decky-stream-hdr"
sudo cp -R "$root/release/stage/decky-stream-hdr" "$plugins_dir/decky-stream-hdr"
sudo systemctl restart plugin_loader
echo "Done. Open the Decky menu and look for StreamHDR."
