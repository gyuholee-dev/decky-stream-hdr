"""Small JSON settings store that tolerates a missing or damaged file."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .options import DEFAULTS, is_valid

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
            if is_valid(key, value):  # a value of the wrong type is ignored
                self._values[key] = value

    def get(self, key: str) -> Any:
        return self._values[key]

    def set(self, key: str, value: Any) -> None:
        if key not in DEFAULTS:
            raise KeyError(key)
        self._values[key] = value
        self._save()

    def reset(self, keep: Optional[Dict[str, Any]] = None) -> None:
        """Back to the defaults, except for the values in `keep`."""
        self._values = dict(DEFAULTS)
        self._values.update(keep or {})
        self._save()

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(self._values, handle, indent=2)
        os.replace(tmp, self._path)
