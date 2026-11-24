"""Detects whether Steam's streaming client is running."""
from __future__ import annotations

import asyncio
import os
from typing import Awaitable, Callable, Optional

CLIENT_NAMES = ("streaming_client", "streaming_client.real")


def is_streaming(proc_root: str = "/proc") -> bool:
    """True when a process whose executable name is the streaming client exists."""
    try:
        entries = os.listdir(proc_root)
    except OSError:
        return False
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            with open(os.path.join(proc_root, entry, "cmdline"), "rb") as handle:
                first = handle.read(4096).split(b"\0", 1)[0]
        except OSError:
            continue  # the process ended while we were looking
        if os.path.basename(first.decode("utf-8", "replace")) in CLIENT_NAMES:
            return True
    return False


class StreamWatcher:
    """Polls for the streaming client and reports changes through `on_change`."""

    def __init__(
        self,
        on_change: Callable[[bool], Awaitable[None]],
        interval: float = 2.0,
        probe: Callable[[], bool] = is_streaming,
    ):
        self._on_change = on_change
        self._interval = interval
        self._probe = probe
        self._state: Optional[bool] = None

    async def poll_once(self) -> None:
        # The probe reads /proc, so keep it off the event loop.
        current = await asyncio.get_running_loop().run_in_executor(None, self._probe)
        if current != self._state:
            self._state = current
            await self._on_change(current)

    async def run(self) -> None:
        while True:
            try:
                await self.poll_once()
            except asyncio.CancelledError:
                raise
            except Exception:  # keep watching even if one cycle fails
                pass
            await asyncio.sleep(self._interval)
