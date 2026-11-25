"""Ties settings, the wrapper and gamescope together. main.py only forwards calls here."""
from __future__ import annotations

import logging
import os
import shutil
from typing import Any, Callable, Dict, List, Optional

from . import gamescope, look, paperwhite, wrapper
from .errors import info_for
from .paths import Paths
from .settings import Settings


# Settings that only apply when a stream starts, so they are left alone while one is running.
FROZEN_WHILE_STREAMING = ("hdr_enabled", "paper_white")


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
        self.look_error: Optional[Dict[str, Any]] = None
        self.paper_white_error: Optional[Dict[str, Any]] = None
        self.streaming = False
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._look_applied = False  # True while the color LUT atom is set by us

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        """Called when the plugin backend loads: make everything match the saved settings."""
        self._clear_stale_look()
        self.apply_paper_white()
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
            if os.path.exists(self.paths.paper_white):
                os.remove(self.paths.paper_white)
            try:
                os.rmdir(self.paths.data_dir)  # only removes the folder when nothing else is in it
            except OSError:
                pass
            self.log.info("Removed all plugin files")
        except OSError as exc:
            self.error = info_for("file_operation_failed", str(exc))
            self.log.error("Cleanup failed: %s", exc)

    def reset_settings(self) -> Dict[str, Any]:
        """The Reset All Settings button: every option back to its default.

        While a stream is running the options that only apply at the next connection stay as they are."""
        keep = {key: self.settings.get(key) for key in FROZEN_WHILE_STREAMING} if self.streaming else {}
        self.settings.reset(keep)
        self.look_error = None
        self.apply_paper_white()
        if not self.streaming:
            self.apply_hdr(self.settings.get("hdr_enabled"))
        if self.streaming:
            self.apply_look()  # takes the color table off when everything is back to unchanged
        return self.status()

    # -- HDR toggle ------------------------------------------------------

    def apply_hdr(self, enabled: bool) -> None:
        """Bring the wrapper and flag file in line with `enabled`, recording any problem."""
        self.error = None
        try:
            if enabled:
                self.apply_paper_white()  # the injected library reads it; it may have been removed
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

    # -- paper white -----------------------------------------------------

    def set_paper_white(self, nits: int) -> Dict[str, Any]:
        self.settings.set("paper_white", paperwhite.clamp_nits(int(nits)))
        self.apply_paper_white()
        if self.streaming:
            self.apply_look()  # contrast and gamma are centered on the paper white
        return self.status()

    def apply_paper_white(self) -> None:
        """Write the saved paper white where the injected library reads it."""
        self.paper_white_error = None
        try:
            paperwhite.write_file(self.paths.paper_white, self.settings.get("paper_white"))
        except OSError as exc:
            self.paper_white_error = info_for("file_operation_failed", str(exc))
            self.log.error("Could not save the paper white: %s", exc)

    # -- changes from outside ---------------------------------------------

    def add_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """`listener(status)` is called after something changed that the panel did not ask for."""
        self._listeners.append(listener)

    def _changed(self) -> None:
        status = self.status()
        for listener in self._listeners:
            try:
                listener(status)
            except Exception as exc:  # a broken listener must not break the controller
                self.log.error("Status listener failed: %s", exc)

    def maintain(self) -> None:
        """Called when a file the wrapper relies on changed: Steam may have restored its own client."""
        if self.settings.get("hdr_enabled") and wrapper.needs_attention(self.paths):
            previous = self.error
            self.apply_hdr(True)
            if self.error is None and previous is None:
                self.log.info("Reinstalled the streaming client wrapper")
        self._changed()

    # -- contrast, gamma and saturation ------------------------------------

    def _look(self) -> look.Look:
        return look.Look(
            self.settings.get("saturation"),
            self.settings.get("contrast"),
            self.settings.get("gamma"),
            self.settings.get("paper_white"),
        )

    def set_saturation(self, percent: int) -> Dict[str, Any]:
        return self._set_look_value("saturation", look.clamp_saturation(int(percent)))

    def set_contrast(self, percent: int) -> Dict[str, Any]:
        return self._set_look_value("contrast", look.clamp_contrast(int(percent)))

    def set_gamma(self, hundredths: int) -> Dict[str, Any]:
        return self._set_look_value("gamma", look.clamp_gamma(int(hundredths)))

    def _set_look_value(self, key: str, value: int) -> Dict[str, Any]:
        self.settings.set(key, value)
        self.look_error = None
        if self.streaming:
            self.apply_look()
        elif not self._look().is_neutral:
            try:
                path = look.ensure_lut(self.paths.luts_dir, self._look())  # build it now, not at connect time
                look.prune(self.paths.luts_dir, path)
            except OSError as exc:
                self.look_error = info_for("lut_failed", str(exc))
                self.log.error("Could not create the color table: %s", exc)
        return self.status()

    def on_streaming_changed(self, streaming: bool) -> None:
        """Called by the watcher when a stream starts or ends."""
        self.streaming = streaming
        self.log.info("Streaming %s", "started" if streaming else "ended")
        if streaming:
            self.apply_look()
        else:
            self._remove_look()
        self._changed()

    def apply_look(self) -> None:
        current = self._look()
        self.look_error = None
        try:
            if current.is_neutral:
                self._remove_look()
                return
            lut = look.ensure_lut(self.paths.luts_dir, current)
            self.gs.set_look(lut, self.paths.gamescope_env)
            self._look_applied = True
            look.prune(self.paths.luts_dir, lut)
        except gamescope.GamescopeError as exc:
            self.look_error = exc.info()
            self.log.error("Color adjustment problem: %s", exc)
        except OSError as exc:
            self.look_error = info_for("lut_failed", str(exc))
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
            "contrast": self.settings.get("contrast"),
            "gamma": self.settings.get("gamma"),
            "paper_white": self.settings.get("paper_white"),
            "streaming": self.streaming,
            "wrapper": wrapper_state,
            "error": self.error,
            "look_error": self.look_error,
            "paper_white_error": self.paper_white_error,
        }
