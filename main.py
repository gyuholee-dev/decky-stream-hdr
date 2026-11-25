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


MAINTAIN_INTERVAL_SECONDS = 20


class Plugin:
    controller: Controller
    watch_task: "asyncio.Task | None" = None
    maintain_task: "asyncio.Task | None" = None

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

        async def maintain_forever():
            # Steam restores its own streaming client on restart and update; put the wrapper back.
            while True:
                await asyncio.sleep(MAINTAIN_INTERVAL_SECONDS)
                try:
                    await loop.run_in_executor(None, self.controller.maintain)
                except Exception as exc:  # keep the loop alive whatever happens
                    decky.logger.error("Maintenance failed: %s", exc)

        self.maintain_task = loop.create_task(maintain_forever())

    async def _unload(self):
        decky.logger.info("StreamHDR backend unloading")
        for task in (self.watch_task, self.maintain_task):
            if task:
                task.cancel()
        self.watch_task = None
        self.maintain_task = None
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

    async def set_paper_white(self, nits: int):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_paper_white, nits)

    async def set_contrast(self, percent: int):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_contrast, percent)

    async def set_gamma(self, hundredths: int):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_gamma, hundredths)

    async def reset_settings(self):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.reset_settings)
