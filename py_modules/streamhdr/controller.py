"""Ties settings, the wrapper and gamescope together. main.py only forwards calls here."""
from __future__ import annotations

import logging
import os
import shutil
import time
from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional

from . import gamescope, look, options, paperwhite, wrapper
from .errors import info_for
from .paths import Paths
from .settings import Settings

# Steam repairs the streaming client whenever it starts and finds the wrapper. If it has had to restore the
# original this many times within this many seconds, we stop putting the wrapper back: that is a fight with
# Steam, and Steam's repair also restarts the whole client.
MAX_RESTORES = 3
RESTORE_WINDOW_SECONDS = 600.0

# How long the wrapper's files must stay quiet, and how old Steam must be, before the wrapper goes in.
# When we know the original client was in place as Steam started, Steam's startup check has passed, so a
# short wait is enough. When the wrapper may have been there at Steam's start (it was left behind by a power
# cut, say), Steam repairs the client and restarts itself about 25 seconds later, so the wait is longer.
SETTLE_CLEAN_SECONDS = 5.0
SETTLE_UNSURE_SECONDS = 30.0


class Controller:
    def __init__(
        self,
        paths: Paths,
        settings: Settings,
        logger: Optional[logging.Logger] = None,
        gamescope_api: Any = gamescope,
        clock: Callable[[], float] = time.monotonic,
        steam_running: Callable[[], bool] = lambda: True,
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
        self._clock = clock
        self.steam_running = steam_running  # the wrapper only goes in while Steam is up (see maintain)
        self._wrapped_before = False  # we have put the wrapper in place at least once in this run
        self._restores: Deque[float] = deque()  # when Steam put the original back after we had wrapped it
        self._gave_up = False
        self._clean = False  # the original client was in place when the current Steam started

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        """Called when the plugin backend loads: make everything match the saved settings.

        The wrapper itself is not installed here. The plugin usually loads while Steam is still starting, and
        Steam repairs a modified streaming client at startup, so the first install waits until the files have
        been quiet for a while (the caller asks for that check once its event watching is running)."""
        self._clear_stale_look()
        self.apply_paper_white()
        wrapper.set_enabled(self.paths, bool(self.settings.get("hdr_enabled")))
        self._clean = wrapper.is_elf(self.paths.client)

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
        keep = {name: self.settings.get(name) for name in options.FROZEN_WHILE_STREAMING} if self.streaming else {}
        self.settings.reset(keep)
        self.apply_paper_white()
        if not self.streaming:
            self._retry_wrapper()
            self.apply_hdr(self.settings.get("hdr_enabled"))
        self._apply_look_setting()
        return self.status()

    # -- changing an option ------------------------------------------------

    def set_option(self, name: str, value: Any) -> Dict[str, Any]:
        """Applies one change from the panel. Unknown options and options that are frozen during a stream
        are ignored; the reply shows the state as it is, so the panel can show that nothing changed."""
        if name not in options.SPEC or (self.streaming and name in options.FROZEN_WHILE_STREAMING):
            return self.status()
        self.settings.set(name, options.snap(name, value))
        if name == "hdr_enabled":
            self._retry_wrapper()  # the user asked again, so a give-up no longer applies
            self.apply_hdr(self.settings.get(name))
        elif name == "paper_white":
            self.apply_paper_white()
            self._apply_look_setting()  # contrast and gamma are centered on the paper white
        else:
            self._apply_look_setting()
        return self.status()

    # -- HDR toggle ------------------------------------------------------

    def apply_hdr(self, enabled: bool) -> None:
        """Bring the wrapper and the flag file in line with `enabled`, recording any problem.

        The wrapper is installed whether or not HDR is wanted: it tells the plugin when a stream starts, which
        the panel needs to lock the options and show the badge. Only the flag decides if it injects HDR."""
        self.error = None
        try:
            self.apply_paper_white()  # the injected library reads it; it may have been removed
            result = wrapper.install(self.paths)
            self._wrapped_before = True
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

    # -- paper white -----------------------------------------------------

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
        """Called when the files the wrapper relies on changed and stayed quiet: Steam may have restored its
        own client. Puts the wrapper back, unless Steam keeps undoing it."""
        enabled = self.settings.get("hdr_enabled")
        if not self._gave_up and self.steam_running() and wrapper.needs_attention(self.paths, enabled):
            if self._steam_restored_original() and self._too_many_restores():
                self._give_up()
            else:
                previous = self.error
                self.apply_hdr(enabled)
                if self.error is None and previous is None:
                    self.log.info("Reinstalled the streaming client wrapper")
        self._changed()

    def on_steam_exited(self) -> None:
        """A Steam client process ended (Steam is restarting or shutting down): put the original client back,
        so that Steam's size check at its next start passes and it does not repair the file and restart."""
        try:
            if wrapper.restore(self.paths):
                self.log.info("Steam ended; restored the original streaming client")
        except OSError as exc:
            self.log.error("Could not restore the streaming client: %s", exc)
        self._wrapped_before = False  # our own restore is not Steam repairing the file
        self._clean = wrapper.is_elf(self.paths.client)  # the next Steam starts with the original in place
        self._changed()

    def settle_seconds(self) -> float:
        """How long to wait before putting the wrapper in (see SETTLE_CLEAN_SECONDS)."""
        return SETTLE_CLEAN_SECONDS if self._clean else SETTLE_UNSURE_SECONDS

    def _steam_restored_original(self) -> bool:
        """True when the original client is back after we had wrapped it: Steam repaired it. Counts it."""
        if not (self._wrapped_before and wrapper.is_elf(self.paths.client)):
            return False
        now = self._clock()
        self._restores.append(now)
        while self._restores and now - self._restores[0] > RESTORE_WINDOW_SECONDS:
            self._restores.popleft()
        return True

    def _too_many_restores(self) -> bool:
        return len(self._restores) >= MAX_RESTORES

    def _give_up(self) -> None:
        self._gave_up = True
        self.error = info_for("wrapper_unstable")
        self.log.error(
            "Steam restored its streaming client %d times within %d seconds; not installing the wrapper again "
            "until HDR Streaming is switched or the plugin is reloaded",
            len(self._restores),
            int(RESTORE_WINDOW_SECONDS),
        )

    def _retry_wrapper(self) -> None:
        self._gave_up = False
        self._restores.clear()

    # -- the color table (contrast, gamma, saturation) ----------------------

    def _look(self) -> look.Look:
        return look.Look(
            self.settings.get("saturation"),
            self.settings.get("contrast"),
            self.settings.get("gamma"),
            self.settings.get("paper_white"),
        )

    def _apply_look_setting(self) -> None:
        """A color option (or the paper white they are centered on) changed: use it now, or get it ready."""
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

    def on_streaming_changed(self, streaming: bool) -> None:
        """Called when a stream starts or ends."""
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
