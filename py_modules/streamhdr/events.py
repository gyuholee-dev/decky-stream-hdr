"""Event sources that replace polling.

* inotify tells us when a file we care about changes: the stream event file the wrapper writes, and the
  files the wrapper relies on (so a Steam restart that restores the original client is noticed at once).
* pidfd tells us when the streaming client process ends.

Nothing here wakes up on a timer, except one quiet period that merges a burst of file events into one call.
The call only comes after the files have been quiet for QUIET_SECONDS: Steam checks the streaming client's size
every time it starts and restarts itself to repair it, so putting the wrapper back the moment Steam restores the
original makes Steam repair it again, over and over. Waiting until Steam is done breaks that loop.
"""
from __future__ import annotations

import asyncio
import ctypes
import ctypes.util
import logging
import os
import struct
from typing import Callable, Dict, List, NamedTuple, Optional, Set

from .paths import Paths

CLIENT_NAMES = ("streaming_client", "streaming_client.real")
STEAM_NAME = "steam"  # the Steam client process: .../steamrt64/steam
STEAM_DIR = "steamrt64"

# How long the wrapper's files must stay unchanged before the plugin checks them. Steam restarts itself about
# 25 seconds after it repairs the client, so this must not be shorter than that. The plugin also puts the
# original client back whenever Steam ends, so this wait is only a second line of defence.
QUIET_SECONDS = 30.0

IN_ATTRIB = 0x4
IN_CLOSE_WRITE = 0x8
IN_MOVED_FROM = 0x40
IN_MOVED_TO = 0x80
IN_CREATE = 0x100
IN_DELETE = 0x200

# What it takes for a file to appear, change or disappear.
WRITTEN = IN_CLOSE_WRITE | IN_MOVED_TO | IN_CREATE
REMOVED = IN_DELETE | IN_MOVED_FROM
ANY_CHANGE = WRITTEN | REMOVED | IN_ATTRIB

_HEADER = struct.Struct("iIII")  # wd, mask, cookie, name length


class FileEvent(NamedTuple):
    directory: str
    name: str
    mask: int


def parse_events(data: bytes) -> List[tuple]:
    """Splits what read() returned from an inotify descriptor into (watch id, mask, name)."""
    events = []
    offset = 0
    while offset + _HEADER.size <= len(data):
        wd, mask, _cookie, length = _HEADER.unpack_from(data, offset)
        offset += _HEADER.size
        name = data[offset : offset + length].split(b"\0", 1)[0].decode("utf-8", "replace")
        offset += length
        events.append((wd, mask, name))
    return events


class Inotify:
    """A thin inotify wrapper that reports events from the asyncio loop."""

    def __init__(self, loop: asyncio.AbstractEventLoop, callback: Callable[[FileEvent], None]):
        self._loop = loop
        self._callback = callback
        self._libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
        self._fd = self._libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self._fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1 failed")
        self._directories: Dict[int, str] = {}
        loop.add_reader(self._fd, self._readable)

    def watch(self, directory: str, mask: int) -> bool:
        """Starts watching a folder. False when that is not possible, for example it does not exist yet."""
        wd = self._libc.inotify_add_watch(self._fd, directory.encode(), mask)
        if wd < 0:
            return False
        self._directories[wd] = directory
        return True

    def _readable(self) -> None:
        try:
            data = os.read(self._fd, 65536)
        except (BlockingIOError, InterruptedError):
            return
        for wd, mask, name in parse_events(data):
            directory = self._directories.get(wd)
            if directory is not None and name:
                self._callback(FileEvent(directory, name, mask))

    def close(self) -> None:
        if self._fd >= 0:
            self._loop.remove_reader(self._fd)
            os.close(self._fd)
            self._fd = -1


def find_streaming_pid(proc_root: str = "/proc") -> Optional[int]:
    """The pid of the running streaming client, if there is one. Used once at start, not repeatedly."""
    try:
        entries = os.listdir(proc_root)
    except OSError:
        return None
    for entry in entries:
        if entry.isdigit() and is_streaming_client(int(entry), proc_root):
            return int(entry)
    return None


def is_streaming_client(pid: int, proc_root: str = "/proc") -> bool:
    try:
        with open(os.path.join(proc_root, str(pid), "cmdline"), "rb") as handle:
            first = handle.read(4096).split(b"\0", 1)[0]
    except OSError:
        return False
    return os.path.basename(first.decode("utf-8", "replace")) in CLIENT_NAMES


def is_steam_client(pid: int, proc_root: str = "/proc") -> bool:
    """True for the Steam client itself (.../steamrt64/steam), not for its helpers or scripts."""
    try:
        with open(os.path.join(proc_root, str(pid), "cmdline"), "rb") as handle:
            first = handle.read(4096).split(b"\0", 1)[0].decode("utf-8", "replace")
    except OSError:
        return False
    return os.path.basename(first) == STEAM_NAME and os.path.basename(os.path.dirname(first)) == STEAM_DIR


def find_steam_pids(proc_root: str = "/proc") -> List[int]:
    try:
        entries = os.listdir(proc_root)
    except OSError:
        return []
    return [int(entry) for entry in entries if entry.isdigit() and is_steam_client(int(entry), proc_root)]


def process_age(pid: int, proc_root: str = "/proc") -> Optional[float]:
    """Seconds since the process started, or None when that cannot be read."""
    try:
        with open(os.path.join(proc_root, str(pid), "stat"), "rb") as handle:
            data = handle.read(4096).decode("utf-8", "replace")
        # The command name sits in parentheses and may hold spaces: the fields continue after the last ")".
        fields = data.rsplit(")", 1)[1].split()
        start_ticks = int(fields[19])  # field 22 of the stat line: start time in clock ticks since boot
        with open(os.path.join(proc_root, "uptime"), "r", encoding="ascii") as handle:
            uptime = float(handle.read().split()[0])
        return uptime - start_ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError):
        return None


def parse_start_event(text: str) -> Optional[int]:
    """The pid in a line like "start 1234" written by the wrapper, or None."""
    parts = text.split()
    if len(parts) == 2 and parts[0] == "start" and parts[1].isdigit():
        return int(parts[1])
    return None


class Events:
    """Turns file and process events into two callbacks.

    on_streaming(True/False) is called when a stream starts or ends.
    on_files_changed() is called once the files the wrapper relies on were created, changed or removed and
    then stayed quiet for `debounce` seconds (every new change starts the wait again). While Steam is not
    running it is called again after every quiet period, so the wrapper goes in once Steam is up.
    The check also waits until the youngest Steam client process is `debounce` seconds old: Steam checks the
    streaming client when it starts, so the wrapper must not go in before that and its restart are over.
    on_steam_exit() is called when a Steam client process ends: Steam checks the streaming client's size
    every time it starts, so the original has to be back in place before the next start.
    """

    def __init__(
        self,
        paths: Paths,
        loop: asyncio.AbstractEventLoop,
        on_streaming: Callable[[bool], None],
        on_files_changed: Callable[[], None],
        on_steam_exit: Optional[Callable[[], None]] = None,
        logger: Optional[logging.Logger] = None,
        inotify_factory: Callable[..., Inotify] = Inotify,
        pidfd_open: Optional[Callable[[int], int]] = None,
        proc_root: str = "/proc",
        debounce: float = QUIET_SECONDS,
        age_of: Optional[Callable[[int], Optional[float]]] = None,
    ):
        self._paths = paths
        self._loop = loop
        self._on_streaming = on_streaming
        self._on_files_changed = on_files_changed
        self._on_steam_exit = on_steam_exit
        self._log = logger or logging.getLogger("streamhdr")
        self._inotify_factory = inotify_factory
        self._pidfd_open = pidfd_open or getattr(os, "pidfd_open", None)
        self._proc_root = proc_root
        self._debounce = debounce
        self._age_of = age_of or (lambda pid: process_age(pid, proc_root))
        self._inotify: Optional[Inotify] = None
        self._tracked_pid: Optional[int] = None
        self._tracked_fd: Optional[int] = None
        self._steam_fds: Dict[int, int] = {}  # pid -> pidfd of every Steam client process we know about
        self._streaming = False
        self._timer: Optional[asyncio.TimerHandle] = None
        self._client_dir = os.path.dirname(paths.client)
        self._event_name = os.path.basename(paths.stream_event)
        self._client_names: Set[str] = {os.path.basename(paths.client), os.path.basename(paths.real)}
        self._data_names: Set[str] = {os.path.basename(paths.shim), os.path.basename(paths.flag)}

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        os.makedirs(self._paths.data_dir, exist_ok=True)
        try:
            self._inotify = self._inotify_factory(self._loop, self._on_file_event)
        except OSError as exc:
            self._log.error("Cannot watch files (%s); stream and wrapper changes will not be noticed", exc)
            return
        if not self._inotify.watch(self._paths.data_dir, WRITTEN | REMOVED):
            self._log.error("Cannot watch %s", self._paths.data_dir)
        if not self._inotify.watch(self._client_dir, ANY_CHANGE):
            self._log.warning("Cannot watch %s yet; start Steam once and reload the plugin", self._client_dir)
        # A stream may already be running when the plugin starts: look once.
        pid = find_streaming_pid(self._proc_root)
        if pid is not None:
            self._track(pid)
        self._track_steam()

    def stop(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._untrack()
        for pid in list(self._steam_fds):
            self._forget_steam(pid)
        if self._inotify is not None:
            self._inotify.close()
            self._inotify = None

    # -- file events -----------------------------------------------------

    def _on_file_event(self, event: FileEvent) -> None:
        if event.directory == self._paths.data_dir:
            if event.name == self._event_name and event.mask & WRITTEN:
                self._read_stream_event()
            elif event.name in self._data_names:
                self._schedule_files_changed()
        elif event.directory == self._client_dir and event.name in self._client_names:
            self._schedule_files_changed()

    def _read_stream_event(self) -> None:
        try:
            with open(self._paths.stream_event, "r", encoding="utf-8") as handle:
                pid = parse_start_event(handle.read(256))
        except OSError:
            return
        if pid is not None:
            self._track(pid)

    def request_check(self) -> None:
        """Ask for a check once things have been quiet for a while (used right after the plugin starts)."""
        self._schedule_files_changed()

    def _schedule_files_changed(self) -> None:
        """Waits for the files to stay quiet: each new event starts the wait again."""
        if self._timer is not None:
            self._timer.cancel()
        self._timer = self._loop.call_later(self._debounce, self._fire_files_changed)

    def _fire_files_changed(self) -> None:
        self._timer = None
        self._track_steam()  # a Steam that started since we last looked
        remaining = self._steam_wait()
        if remaining > 0:  # Steam is still young: wait until it has been up long enough
            self._timer = self._loop.call_later(remaining + 0.01, self._fire_files_changed)
            return
        self._on_files_changed()
        if not self._steam_fds:
            self._schedule_files_changed()  # nothing to repair yet: look again once Steam may be up

    def _steam_wait(self) -> float:
        """Seconds until the youngest Steam client process is old enough; 0 when there is none or its age is unknown."""
        ages = [age for age in (self._age_of(pid) for pid in self._steam_fds) if age is not None]
        if not ages:
            return 0.0
        return max(0.0, self._debounce - min(ages))

    # -- the Steam client process ----------------------------------------------

    def steam_running(self) -> bool:
        return bool(self._steam_fds)

    def _track_steam(self) -> None:
        if self._pidfd_open is None:
            return
        for pid in find_steam_pids(self._proc_root):
            if pid in self._steam_fds:
                continue
            try:
                fd = self._pidfd_open(pid)
            except OSError:
                continue  # already gone
            self._steam_fds[pid] = fd
            self._loop.add_reader(fd, self._steam_ended, pid)

    def _forget_steam(self, pid: int) -> None:
        fd = self._steam_fds.pop(pid, None)
        if fd is None:
            return
        self._loop.remove_reader(fd)
        try:
            os.close(fd)
        except OSError:
            pass

    def _steam_ended(self, pid: int) -> None:
        self._forget_steam(pid)
        self._log.info("Steam client process %d ended", pid)
        if self._on_steam_exit is not None:
            self._on_steam_exit()
        self._track_steam()

    # -- the streaming client process --------------------------------------

    def _track(self, pid: int) -> None:
        if pid == self._tracked_pid:
            return
        if not is_streaming_client(pid, self._proc_root) or self._pidfd_open is None:
            if self._pidfd_open is None:
                self._log.error("This Python cannot wait for a process to end (no pidfd_open)")
            return
        try:
            fd = self._pidfd_open(pid)
        except OSError:
            return  # the process is already gone
        self._untrack()
        self._tracked_pid, self._tracked_fd = pid, fd
        self._loop.add_reader(fd, self._ended, pid)
        self._set_streaming(True)

    def _ended(self, pid: int) -> None:
        if pid != self._tracked_pid:
            return
        self._untrack()
        self._set_streaming(False)

    def _untrack(self) -> None:
        if self._tracked_fd is not None:
            self._loop.remove_reader(self._tracked_fd)
            try:
                os.close(self._tracked_fd)
            except OSError:
                pass
        self._tracked_pid = self._tracked_fd = None

    def _set_streaming(self, streaming: bool) -> None:
        if streaming != self._streaming:
            self._streaming = streaming
            self._on_streaming(streaming)
