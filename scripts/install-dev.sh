#!/bin/sh
# Builds the injection library on this machine and installs the plugin into Decky Loader.
# Run it on the Linux client from a copy of this repository that already contains dist/
# (build the frontend on your development machine with 'pnpm run build' and copy the repo over).
#
#   scripts/install-dev.sh [plugins-dir]     default plugins dir: ~/homebrew/plugins
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugins_dir=${1:-"$HOME/homebrew/plugins"}

make -C "$root/backend"
sh "$root/scripts/package.sh"

echo "Installing into $plugins_dir/decky-stream-hdr (sudo may ask for your password)"
sudo rm -rf "$plugins_dir/decky-stream-hdr"
sudo cp -R "$root/release/stage/decky-stream-hdr" "$plugins_dir/decky-stream-hdr"
sudo systemctl restart plugin_loader
echo "Done. Open the Decky menu and look for StreamHDR."
