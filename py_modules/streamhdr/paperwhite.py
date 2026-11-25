"""Paper white of the HDR stream, in nits.

The injected library reads the value from a small file when Steam's streaming client creates its
renderer, so a new value applies from the next connection.
"""
from __future__ import annotations

import os

PAPER_WHITE_MIN = 80
PAPER_WHITE_MAX = 480
PAPER_WHITE_STEP = 10
PAPER_WHITE_DEFAULT = 200  # nits; 200-230 is recommended for a display with a 1000 nit peak


def clamp_nits(value: int) -> int:
    """Snap to the slider grid and keep inside the allowed range."""
    snapped = int(round(value / PAPER_WHITE_STEP)) * PAPER_WHITE_STEP
    return max(PAPER_WHITE_MIN, min(PAPER_WHITE_MAX, snapped))


def write_file(path: str, nits: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as handle:
        handle.write("%d\n" % nits)
    os.replace(tmp, path)
