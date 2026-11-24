"""Builds 3D LUTs (.cube) that change the saturation of PQ-encoded BT.2020 HDR output.

gamescope applies GAMESCOPE_COLOR_LOOK_PQ to HDR output, with input and output both
PQ encoded BT.2020. Each LUT cell is decoded to linear nits, saturation is scaled
around the BT.2020 luminance (so brightness is kept), and the result is PQ encoded again.
"""
from __future__ import annotations

import os
from typing import List, Sequence

LUT_SIZE = 17  # gamescope's internal 3D LUT size

SATURATION_MIN = 0
SATURATION_MAX = 200
SATURATION_STEP = 10
SATURATION_DEFAULT = 100  # percent; 100 means "no change"

PQ_M1 = 2610 / 16384
PQ_M2 = 2523 / 4096 * 128
PQ_C1 = 3424 / 4096
PQ_C2 = 2413 / 4096 * 32
PQ_C3 = 2392 / 4096 * 32
PQ_PEAK_NITS = 10000.0
BT2020_LUMA = (0.2627, 0.6780, 0.0593)


def clamp_percent(value: int) -> int:
    """Snap to the slider grid and keep inside the allowed range."""
    snapped = int(round(value / SATURATION_STEP)) * SATURATION_STEP
    return max(SATURATION_MIN, min(SATURATION_MAX, snapped))


def percent_to_factor(percent: int) -> float:
    return percent / 100.0


def decode_pq(encoded: float) -> float:
    powered = encoded ** (1 / PQ_M2)
    numerator = max(powered - PQ_C1, 0.0)
    denominator = PQ_C2 - PQ_C3 * powered
    return PQ_PEAK_NITS * (numerator / denominator) ** (1 / PQ_M1)


def encode_pq(nits: float) -> float:
    normalized = min(max(nits / PQ_PEAK_NITS, 0.0), 1.0)
    powered = normalized ** PQ_M1
    return ((PQ_C1 + PQ_C2 * powered) / (1 + PQ_C3 * powered)) ** PQ_M2


def scale_saturation(linear_rgb: Sequence[float], factor: float) -> List[float]:
    luma = sum(weight * channel for weight, channel in zip(BT2020_LUMA, linear_rgb))
    return [max(luma + factor * (channel - luma), 0.0) for channel in linear_rgb]


def lut_text(factor: float, size: int = LUT_SIZE) -> str:
    lines = ['TITLE "StreamHDR PQ BT.2020 saturation %.2f"' % factor, "LUT_3D_SIZE %d" % size]
    decoded = [decode_pq(index / (size - 1)) for index in range(size)]  # reused for every axis
    for blue in range(size):
        for green in range(size):
            for red in range(size):  # .cube order: red changes fastest
                adjusted = scale_saturation((decoded[red], decoded[green], decoded[blue]), factor)
                lines.append(" ".join("%.6f" % encode_pq(value) for value in adjusted))
    return "\n".join(lines) + "\n"


def lut_filename(percent: int) -> str:
    # One file per value: gamescope re-reads the LUT when the atom value changes,
    # so a new value always points at a different path.
    return "look_pq_sat%03d.cube" % percent


def ensure_lut(luts_dir: str, percent: int) -> str:
    """Create the LUT file for `percent` if missing and return its path."""
    path = os.path.join(luts_dir, lut_filename(percent))
    if os.path.isfile(path):
        return path
    os.makedirs(luts_dir, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as handle:
        handle.write(lut_text(percent_to_factor(percent)))
    os.replace(tmp, path)
    return path
