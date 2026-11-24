import asyncio
import os
import pwd
import sys

import decky

# Backend modules live in py_modules/, which Decky adds to the import path.
# Keep them independent of the decky module so they can be unit tested anywhere.
sys.path.insert(0, os.path.join(decky.DECKY_PLUGIN_DIR, "py_modules"))

from streamhdr.controller import Controller  # noqa: E402
from streamhdr.paths import Paths  # noqa: E402
from streamhdr.settings import Settings  # noqa: E402
from streamhdr.watcher import StreamWatcher  # noqa: E402


class Plugin:
    controller: Controller
    watch_task: "asyncio.Task | None" = None

    async def _main(self):
        uid = pwd.getpwnam(decky.DECKY_USER).pw_uid
        paths = Paths.for_user(decky.DECKY_USER_HOME, decky.DECKY_PLUGIN_DIR, uid)
        settings = Settings(os.path.join(decky.DECKY_PLUGIN_SETTINGS_DIR, "settings.json"))
        self.controller = Controller(paths, settings, decky.logger)
        decky.logger.info("StreamHDR backend loaded (user=%s)", decky.DECKY_USER)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.controller.start)

        async def on_change(streaming: bool):
            # File and process work is blocking, so keep it off the event loop.
            await loop.run_in_executor(None, self.controller.on_streaming_changed, streaming)

        self.watch_task = loop.create_task(StreamWatcher(on_change).run())

    async def _unload(self):
        decky.logger.info("StreamHDR backend unloading")
        if self.watch_task:
            self.watch_task.cancel()
            self.watch_task = None
        await asyncio.get_running_loop().run_in_executor(None, self.controller.stop)

    async def _uninstall(self):
        decky.logger.info("StreamHDR uninstalling")
        await asyncio.get_running_loop().run_in_executor(None, self.controller.uninstall)

    async def get_status(self):
        return self.controller.status()

    async def set_hdr_enabled(self, enabled: bool):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_hdr_enabled, enabled)

    async def set_saturation(self, percent: int):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_saturation, percent)
