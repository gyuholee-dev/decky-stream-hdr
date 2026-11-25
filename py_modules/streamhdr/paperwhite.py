"""Paper white of the HDR stream, in nits.

The injected library reads the value from a small file when Steam's streaming client creates its
renderer, so a new value applies from the next connection. The range and default are in options.json.
"""
from __future__ import annotations

import os


def write_file(path: str, nits: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as handle:
        handle.write("%d\n" % nits)
    os.replace(tmp, path)
