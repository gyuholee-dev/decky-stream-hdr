"""Ties settings and the wrapper together. main.py only forwards calls here."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from . import wrapper
from .paths import Paths
from .settings import Settings


class Controller:
    def __init__(self, paths: Paths, settings: Settings, logger: Optional[logging.Logger] = None):
        self.paths = paths
        self.settings = settings
        self.log = logger or logging.getLogger("streamhdr")
        self.error: Optional[str] = None

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        """Called when the plugin backend loads: make the files match the saved settings."""
        self.apply_hdr(self.settings.get("hdr_enabled"))

    def stop(self) -> None:
        """Called when the plugin unloads: put Steam's original client back."""
        try:
            if wrapper.restore(self.paths):
                self.log.info("Restored the original streaming client")
        except OSError as exc:
            self.log.error("Could not restore the streaming client: %s", exc)

    def uninstall(self) -> None:
        try:
            wrapper.uninstall(self.paths)
            self.log.info("Removed all plugin files")
        except OSError as exc:
            self.log.error("Cleanup failed: %s", exc)

    # -- HDR toggle ------------------------------------------------------

    def apply_hdr(self, enabled: bool) -> None:
        """Bring the wrapper and flag file in line with `enabled`, recording any problem."""
        self.error = None
        try:
            if enabled:
                result = wrapper.install(self.paths)
                if result != "ok":
                    self.log.info("Streaming client wrapper %s", result)
            wrapper.set_enabled(self.paths, enabled)
        except wrapper.WrapperError as exc:
            self.error = str(exc)
            self.log.error("Wrapper problem: %s", exc)
            wrapper.set_enabled(self.paths, False)
        except OSError as exc:
            self.error = "File operation failed: %s" % exc
            self.log.error("%s", self.error)

    def set_hdr_enabled(self, enabled: bool) -> Dict[str, Any]:
        self.settings.set("hdr_enabled", bool(enabled))
        self.apply_hdr(bool(enabled))
        return self.status()

    # -- status ----------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "hdr_enabled": bool(self.settings.get("hdr_enabled")),
            "wrapper": wrapper.status(self.paths),
            "error": self.error,
        }
