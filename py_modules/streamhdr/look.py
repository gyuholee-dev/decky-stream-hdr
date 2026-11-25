"""Builds 3D LUTs (.cube) that change contrast, gamma and saturation of PQ-encoded BT.2020 HDR output.

gamescope applies GAMESCOPE_COLOR_LOOK_PQ to HDR output, with input and output both PQ encoded
BT.2020. Each LUT cell is decoded to linear nits, adjusted and PQ encoded again:

* gamma bends the tones below the pivot (paper white) and fades out above it, so highlights stay;
* contrast stretches the PQ signal around the pivot, so paper white itself does not move;
* both act on luminance only (colors keep their hue), then saturation is scaled around that luminance.
"""
from __future__ import annotations

import glob
import math
import os
from typing import List, NamedTuple, Sequence

LUT_SIZE = 17  # gamescope's internal 3D LUT size

SATURATION_MIN, SATURATION_MAX, SATURATION_STEP, SATURATION_DEFAULT = 0, 200, 5, 100  # percent
CONTRAST_MIN, CONTRAST_MAX, CONTRAST_STEP, CONTRAST_DEFAULT = 0, 200, 5, 100  # percent
GAMMA_MIN, GAMMA_MAX, GAMMA_STEP, GAMMA_DEFAULT = 50, 200, 10, 100  # hundredths: 100 means 1.00

# Gamma fades out between the pivot and this many times the pivot.
GAMMA_FADE_RATIO = 4.0

PQ_M1 = 2610 / 16384
PQ_M2 = 2523 / 4096 * 128
PQ_C1 = 3424 / 4096
PQ_C2 = 2413 / 4096 * 32
PQ_C3 = 2392 / 4096 * 32
PQ_PEAK_NITS = 10000.0
BT2020_LUMA = (0.2627, 0.6780, 0.0593)


class Look(NamedTuple):
    saturation: int  # percent
    contrast: int  # percent
    gamma: int  # hundredths
    pivot: int  # nits; the paper white the stream is drawn with

    @property
    def is_neutral(self) -> bool:
        return (
            self.saturation == SATURATION_DEFAULT
            and self.contrast == CONTRAST_DEFAULT
            and self.gamma == GAMMA_DEFAULT
        )


def snap(value: int, minimum: int, maximum: int, step: int) -> int:
    """Snap to the slider grid and keep inside the allowed range."""
    snapped = int(round(value / step)) * step
    return max(minimum, min(maximum, snapped))


def clamp_saturation(value: int) -> int:
    return snap(value, SATURATION_MIN, SATURATION_MAX, SATURATION_STEP)


def clamp_contrast(value: int) -> int:
    return snap(value, CONTRAST_MIN, CONTRAST_MAX, CONTRAST_STEP)


def clamp_gamma(value: int) -> int:
    return snap(value, GAMMA_MIN, GAMMA_MAX, GAMMA_STEP)


def decode_pq(encoded: float) -> float:
    powered = encoded ** (1 / PQ_M2)
    numerator = max(powered - PQ_C1, 0.0)
    denominator = PQ_C2 - PQ_C3 * powered
    return PQ_PEAK_NITS * (numerator / denominator) ** (1 / PQ_M1)


def encode_pq(nits: float) -> float:
    normalized = min(max(nits / PQ_PEAK_NITS, 0.0), 1.0)
    powered = normalized ** PQ_M1
    return ((PQ_C1 + PQ_C2 * powered) / (1 + PQ_C3 * powered)) ** PQ_M2


def luminance(linear_rgb: Sequence[float]) -> float:
    return sum(weight * channel for weight, channel in zip(BT2020_LUMA, linear_rgb))


def scale_saturation(linear_rgb: Sequence[float], factor: float) -> List[float]:
    luma = luminance(linear_rgb)
    return [max(luma + factor * (channel - luma), 0.0) for channel in linear_rgb]


def _gamma_weight(nits: float, pivot: float) -> float:
    """1 up to the pivot, easing to 0 at GAMMA_FADE_RATIO times the pivot."""
    if nits <= pivot:
        return 1.0
    t = min(math.log(nits / pivot) / math.log(GAMMA_FADE_RATIO), 1.0)
    return 1.0 - t * t * (3.0 - 2.0 * t)


def tone(nits: float, contrast: float, gamma: float, pivot: float) -> float:
    """New luminance for `nits`. gamma above 1 darkens, below 1 brightens (like a display gamma)."""
    if nits <= 0.0:
        return 0.0
    if gamma != 1.0:
        nits = nits * (nits / pivot) ** ((gamma - 1.0) * _gamma_weight(nits, pivot))
    if contrast != 1.0:
        center = encode_pq(pivot)
        nits = decode_pq(min(max(center + contrast * (encode_pq(nits) - center), 0.0), 1.0))
    return nits


def lut_text(
    saturation: float,
    size: int = LUT_SIZE,
    contrast: float = 1.0,
    gamma: float = 1.0,
    pivot: float = 200.0,
) -> str:
    title = "StreamHDR PQ BT.2020 saturation %.2f contrast %.2f gamma %.2f pivot %.0f" % (saturation, contrast, gamma, pivot)
    lines = ['TITLE "%s"' % title, "LUT_3D_SIZE %d" % size]
    decoded = [decode_pq(index / (size - 1)) for index in range(size)]  # reused for every axis
    adjust_tone = contrast != 1.0 or gamma != 1.0
    for blue in range(size):
        for green in range(size):
            for red in range(size):  # .cube order: red changes fastest
                rgb = [decoded[red], decoded[green], decoded[blue]]
                if adjust_tone:
                    luma = luminance(rgb)
                    if luma > 0.0:
                        factor = tone(luma, contrast, gamma, pivot) / luma
                        rgb = [channel * factor for channel in rgb]
                rgb = scale_saturation(rgb, saturation)
                lines.append(" ".join("%.6f" % encode_pq(value) for value in rgb))
    return "\n".join(lines) + "\n"


def lut_filename(look: Look) -> str:
    # One file per setting: gamescope re-reads the LUT when the atom value changes,
    # so a new setting always points at a different path.
    return "look_pq_s%03d_c%03d_g%03d_p%03d.cube" % look[:4]


def lut_text_for(look: Look) -> str:
    return lut_text(look.saturation / 100.0, contrast=look.contrast / 100.0, gamma=look.gamma / 100.0, pivot=float(look.pivot))


def ensure_lut(luts_dir: str, look: Look) -> str:
    """Create the LUT file for `look` if missing and return its path."""
    path = os.path.join(luts_dir, lut_filename(look))
    if os.path.isfile(path):
        return path
    os.makedirs(luts_dir, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as handle:
        handle.write(lut_text_for(look))
    os.replace(tmp, path)
    return path


def prune(luts_dir: str, keep: str) -> None:
    """Delete LUT files other than `keep`, so dragging a slider does not fill the disk."""
    for path in glob.glob(os.path.join(luts_dir, "look_pq_*")):
        if path != keep:
            try:
                os.remove(path)
            except OSError:
                pass
