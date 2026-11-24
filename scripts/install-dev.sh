#!/bin/sh
# Builds everything on this machine and installs the plugin into Decky Loader.
# Run it on the Linux client from a clone of this repository:
#
#   git pull && sh scripts/install-dev.sh [plugins-dir]     default plugins dir: ~/homebrew/plugins
#
# Needs: git, node, yarn, gcc, make, python3 and sudo.
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugins_dir=${1:-"$HOME/homebrew/plugins"}

for tool in node yarn gcc make python3 sudo; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "'$tool' is not installed. Install it first (on CachyOS: sudo pacman -S nodejs yarn gcc make python)." >&2
        exit 1
    fi
done

echo "Building the frontend"
(cd "$root" && yarn install --frozen-lockfile && yarn build)

echo "Building the injection library"
make -C "$root/backend"

echo "Packaging"
sh "$root/scripts/package.sh"

echo "Installing into $plugins_dir/decky-stream-hdr (sudo may ask for your password)"
sudo rm -rf "$plugins_dir/decky-stream-hdr"
sudo cp -R "$root/release/stage/decky-stream-hdr" "$plugins_dir/decky-stream-hdr"
sudo systemctl restart plugin_loader
echo "Done. Open the Decky menu and look for StreamHDR."
