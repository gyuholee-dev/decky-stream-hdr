"""Small JSON settings store that tolerates a missing or damaged file."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "hdr_enabled": False,
    "saturation": 100,  # percent; 100 means no change
    "paper_white": 200,  # nits
    "contrast": 100,  # percent; 100 means no change
    "gamma": 100,  # hundredths; 100 means 1.00 (no change)
}


class Settings:
    def __init__(self, path: str):
        self._path = path
        self._values: Dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                stored = json.load(handle)
        except (OSError, ValueError):
            return
        if not isinstance(stored, dict):
            return
        for key, default in DEFAULTS.items():
            value = stored.get(key, default)
            # Ignore values of the wrong type (bool is an int subclass, so check it explicitly).
            if isinstance(default, bool) != isinstance(value, bool) or not isinstance(value, type(default)):
                continue
            self._values[key] = value

    def get(self, key: str) -> Any:
        return self._values[key]

    def set(self, key: str, value: Any) -> None:
        if key not in DEFAULTS:
            raise KeyError(key)
        self._values[key] = value
        self._save()

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(self._values, handle, indent=2)
        os.replace(tmp, self._path)
