"""Filesystem locations used by the plugin. No dependency on the decky module."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

DATA_DIR_NAME = "decky-stream-hdr"
SHIM_NAME = "sdl_hdr_shim.so"
FLAG_NAME = "enabled"
PAPER_WHITE_NAME = "paper_white"
STREAM_EVENT_NAME = "stream_event"
TEMPLATE_NAME = "streaming_client.sh.tmpl"

# Where Steam keeps its files, in the order they are tried. The first is the usual place (SteamOS and
# most distributions); the others are links or older locations that point at the same folder.
STEAM_ROOT_CANDIDATES = (
    os.path.join(".local", "share", "Steam"),
    os.path.join(".steam", "steam"),
    os.path.join(".steam", "root"),
)


def find_streaming_client(home: str) -> str:
    """Path of Steam's streaming client: the first place it exists, else the usual place."""
    paths = [os.path.join(home, root, "steamrt64", "streaming_client") for root in STEAM_ROOT_CANDIDATES]
    return next((path for path in paths if os.path.isfile(path)), paths[0])


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
    paper_white: str
    stream_event: str
    luts_dir: str
    # gamescope's environment file, which tells us how to reach its X server.
    gamescope_env: str
    # Files shipped inside the plugin package.
    shim_src: str
    template: str

    @staticmethod
    def for_user(home: str, plugin_dir: str, uid: Optional[int] = None) -> "Paths":
        client = find_streaming_client(home)
        data_dir = os.path.join(home, ".local", "share", DATA_DIR_NAME)
        uid = os.getuid() if uid is None else uid
        return Paths(
            client=client,
            real=client + ".real",
            data_dir=data_dir,
            shim=os.path.join(data_dir, SHIM_NAME),
            flag=os.path.join(data_dir, FLAG_NAME),
            paper_white=os.path.join(data_dir, PAPER_WHITE_NAME),
            stream_event=os.path.join(data_dir, STREAM_EVENT_NAME),
            luts_dir=os.path.join(data_dir, "luts"),
            gamescope_env="/run/user/%d/gamescope-environment" % uid,
            shim_src=os.path.join(plugin_dir, "bin", SHIM_NAME),
            template=os.path.join(plugin_dir, "py_modules", "streamhdr", TEMPLATE_NAME),
        )
