"""The options the user can change, read from options.json.

options.json is the one place that says what each option is: its range, step and default, and whether it
only applies when a stream starts. The backend, the panel and the browser preview all read the same file.
(The injection library in backend/src has its own copy of the paper white numbers; a test keeps it in line.)

* min, max, step: the slider grid, in stored units
* default: the value for a new install and for Reset All Settings
* neutral: the value that leaves the picture unchanged (the color options)
* scale: stored value divided by scale is the number shown (gamma is stored in hundredths)
* frozenWhileStreaming: applies only at the next connection, so it cannot change during a stream
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

with open(os.path.join(os.path.dirname(__file__), "options.json"), "r", encoding="utf-8") as _handle:
    SPEC: Dict[str, Dict[str, Any]] = json.load(_handle)

DEFAULTS: Dict[str, Any] = {name: spec["default"] for name, spec in SPEC.items()}
FROZEN_WHILE_STREAMING: Tuple[str, ...] = tuple(name for name, spec in SPEC.items() if spec.get("frozenWhileStreaming"))
LOOK_OPTIONS: Tuple[str, ...] = tuple(name for name, spec in SPEC.items() if "neutral" in spec)


def snap(name: str, value: Any) -> Any:
    """The value a user's request becomes: on the grid and inside the range (a toggle becomes a bool)."""
    spec = SPEC[name]
    if isinstance(spec["default"], bool):
        return bool(value)
    step, low, high = spec["step"], spec["min"], spec["max"]
    snapped = int(round((int(value) - low) / step)) * step + low
    return max(low, min(high, snapped))


def is_valid(name: str, value: Any) -> bool:
    """True when a stored value has the right type for the option (bool is an int, so check it explicitly)."""
    default = SPEC[name]["default"]
    return isinstance(default, bool) == isinstance(value, bool) and isinstance(value, type(default))
