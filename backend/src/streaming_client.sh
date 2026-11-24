#!/bin/sh
# streamhdr-wrapper v1
# Installed by the StreamHDR Decky plugin in place of Steam's streaming_client.
# The original binary is kept next to this file as streaming_client.real.
# The __SHIM__ and __FLAG__ placeholders are replaced with absolute paths at install time.
SHIM="__SHIM__"
FLAG="__FLAG__"
if [ -f "$FLAG" ] && [ -f "$SHIM" ]; then
    export LD_PRELOAD="$SHIM${LD_PRELOAD:+:$LD_PRELOAD}"
fi
exec "$(dirname "$0")/streaming_client.real" "$@"
