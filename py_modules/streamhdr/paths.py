"""Filesystem locations used by the plugin. No dependency on the decky module."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

DATA_DIR_NAME = "decky-stream-hdr"
SHIM_NAME = "sdl_hdr_shim.so"
FLAG_NAME = "enabled"
TEMPLATE_NAME = "streaming_client.sh.tmpl"


@dataclass(frozen=True)
class Paths:
    # Steam's streaming client and the copy of the original binary.
    client: str
    real: str
    # Plugin-owned files that must be visible inside the Steam runtime container,
    # so they live under the user's home instead of the plugin directory.
    data_dir: str
    shim: str
    flag: str
    luts_dir: str
    # gamescope's environment file, which tells us how to reach its X server.
    gamescope_env: str
    # Files shipped inside the plugin package.
    shim_src: str
    template: str

    @staticmethod
    def for_user(home: str, plugin_dir: str, uid: Optional[int] = None) -> "Paths":
        client = os.path.join(home, ".local", "share", "Steam", "steamrt64", "streaming_client")
        data_dir = os.path.join(home, ".local", "share", DATA_DIR_NAME)
        uid = os.getuid() if uid is None else uid
        return Paths(
            client=client,
            real=client + ".real",
            data_dir=data_dir,
            shim=os.path.join(data_dir, SHIM_NAME),
            flag=os.path.join(data_dir, FLAG_NAME),
            luts_dir=os.path.join(data_dir, "luts"),
            gamescope_env="/run/user/%d/gamescope-environment" % uid,
            shim_src=os.path.join(plugin_dir, "bin", SHIM_NAME),
            template=os.path.join(plugin_dir, "py_modules", "streamhdr", TEMPLATE_NAME),
        )
