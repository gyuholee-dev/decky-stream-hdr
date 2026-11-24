"""Ties settings, the wrapper and gamescope together. main.py only forwards calls here."""
from __future__ import annotations

import logging
import os
import shutil
from typing import Any, Dict, Optional

from . import gamescope, saturation, wrapper
from .errors import info_for
from .paths import Paths
from .settings import Settings


class Controller:
    def __init__(
        self,
        paths: Paths,
        settings: Settings,
        logger: Optional[logging.Logger] = None,
        gamescope_api: Any = gamescope,
    ):
        self.paths = paths
        self.settings = settings
        self.log = logger or logging.getLogger("streamhdr")
        self.gs = gamescope_api
        self.error: Optional[Dict[str, Any]] = None
        self.saturation_error: Optional[Dict[str, Any]] = None
        self.streaming = False
        self._look_applied = False  # True while the saturation LUT atom is set by us

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        """Called when the plugin backend loads: make everything match the saved settings."""
        self._clear_stale_look()
        self.apply_hdr(self.settings.get("hdr_enabled"))

    def stop(self) -> None:
        """Called when the plugin unloads: put Steam's original client and the display back."""
        self._remove_look()
        try:
            if wrapper.restore(self.paths):
                self.log.info("Restored the original streaming client")
        except OSError as exc:
            self.log.error("Could not restore the streaming client: %s", exc)

    def uninstall(self) -> None:
        self._remove_look()
        try:
            wrapper.uninstall(self.paths)
            shutil.rmtree(self.paths.luts_dir, ignore_errors=True)
            try:
                os.rmdir(self.paths.data_dir)  # only removes the folder when nothing else is in it
            except OSError:
                pass
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
            self.error = exc.info()
            self.log.error("Wrapper problem: %s", exc)
            wrapper.set_enabled(self.paths, False)
        except OSError as exc:
            self.error = info_for("file_operation_failed", str(exc))
            self.log.error("File operation failed: %s", exc)

    def set_hdr_enabled(self, enabled: bool) -> Dict[str, Any]:
        self.settings.set("hdr_enabled", bool(enabled))
        self.apply_hdr(bool(enabled))
        return self.status()

    # -- periodic maintenance --------------------------------------------

    def maintain(self) -> None:
        """Called every few seconds: repair what Steam or gamescope may have undone."""
        if self.settings.get("hdr_enabled") and wrapper.needs_attention(self.paths):
            previous = self.error
            self.apply_hdr(True)
            if self.error is None and previous is None:
                self.log.info("Reinstalled the streaming client wrapper")
        if self.streaming and self.settings.get("saturation") != saturation.SATURATION_DEFAULT:
            self._reapply_look_if_lost()

    def _reapply_look_if_lost(self) -> None:
        expected = os.path.join(self.paths.luts_dir, saturation.lut_filename(self.settings.get("saturation")))
        try:
            current = self.gs.get_look(self.paths.gamescope_env)
        except gamescope.GamescopeError:
            return
        if current != expected:
            self.log.info("The color table was reset; applying it again")
            self.apply_saturation()

    # -- saturation ------------------------------------------------------

    def set_saturation(self, percent: int) -> Dict[str, Any]:
        percent = saturation.clamp_percent(int(percent))
        self.settings.set("saturation", percent)
        self.saturation_error = None
        if percent != saturation.SATURATION_DEFAULT:
            try:
                saturation.ensure_lut(self.paths.luts_dir, percent)  # build it now, not at connect time
            except OSError as exc:
                self.saturation_error = info_for("lut_failed", str(exc))
                self.log.error("Could not create the color table: %s", exc)
        if self.streaming:
            self.apply_saturation()
        return self.status()

    def on_streaming_changed(self, streaming: bool) -> None:
        """Called by the watcher when a stream starts or ends."""
        self.streaming = streaming
        self.log.info("Streaming %s", "started" if streaming else "ended")
        if streaming:
            self.apply_saturation()
        else:
            self._remove_look()

    def apply_saturation(self) -> None:
        percent = self.settings.get("saturation")
        self.saturation_error = None
        try:
            if percent == saturation.SATURATION_DEFAULT:
                self._remove_look()
                return
            lut = saturation.ensure_lut(self.paths.luts_dir, percent)
            self.gs.set_look(lut, self.paths.gamescope_env)
            self._look_applied = True
        except gamescope.GamescopeError as exc:
            self.saturation_error = exc.info()
            self.log.error("Saturation problem: %s", exc)
        except OSError as exc:
            self.saturation_error = info_for("lut_failed", str(exc))
            self.log.error("Could not create the color table: %s", exc)

    def _remove_look(self) -> None:
        if not self._look_applied:
            return
        try:
            self.gs.clear_look(self.paths.gamescope_env)
        except gamescope.GamescopeError as exc:
            self.log.error("Could not clear the color table: %s", exc)
        self._look_applied = False

    def _clear_stale_look(self) -> None:
        """Remove a LUT left behind by a previous run of this plugin (for example after a crash)."""
        try:
            current = self.gs.get_look(self.paths.gamescope_env)
        except gamescope.GamescopeError:
            return  # gamescope is not reachable, so there is nothing to clean
        if current and current.startswith(self.paths.luts_dir):
            try:
                self.gs.clear_look(self.paths.gamescope_env)
                self.log.info("Cleared a color table left by a previous run")
            except gamescope.GamescopeError as exc:
                self.log.error("Could not clear the old color table: %s", exc)

    # -- status ----------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        wrapper_state = wrapper.status(self.paths)
        hdr_enabled = bool(self.settings.get("hdr_enabled"))
        # HDR is being requested right now: a stream is running and everything needed for the
        # request is in place. (The host can still decide to send SDR, for example because of its settings.)
        hdr_active = (
            self.streaming
            and hdr_enabled
            and self.error is None
            and wrapper_state["wrapped"]
            and wrapper_state["enabled"]
            and wrapper_state["shim_installed"]
        )
        return {
            "hdr_enabled": hdr_enabled,
            "hdr_active": hdr_active,
            "saturation": self.settings.get("saturation"),
            "streaming": self.streaming,
            "wrapper": wrapper_state,
            "error": self.error,
            "saturation_error": self.saturation_error,
        }
