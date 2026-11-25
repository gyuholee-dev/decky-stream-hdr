import asyncio
import os
import pwd
import sys

import decky

# Backend modules live in py_modules/, which Decky adds to the import path.
# Keep them independent of the decky module so they can be unit tested anywhere.
sys.path.insert(0, os.path.join(decky.DECKY_PLUGIN_DIR, "py_modules"))

from streamhdr.controller import Controller  # noqa: E402
from streamhdr.events import Events  # noqa: E402
from streamhdr.paths import Paths  # noqa: E402
from streamhdr.settings import Settings  # noqa: E402


class Plugin:
    controller: Controller
    events: "Events | None" = None

    async def _main(self):
        uid = pwd.getpwnam(decky.DECKY_USER).pw_uid
        paths = Paths.for_user(decky.DECKY_USER_HOME, decky.DECKY_PLUGIN_DIR, uid)
        settings = Settings(os.path.join(decky.DECKY_PLUGIN_SETTINGS_DIR, "settings.json"))
        self.controller = Controller(paths, settings, decky.logger)
        decky.logger.info("StreamHDR backend loaded (user=%s)", decky.DECKY_USER)

        loop = asyncio.get_running_loop()

        # The controller reports changes from worker threads; the panel hears about them as an event.
        def publish(status):
            asyncio.run_coroutine_threadsafe(decky.emit("status", status), loop)

        self.controller.add_listener(publish)
        await loop.run_in_executor(None, self.controller.start)

        # File and process work is blocking, so every reaction runs off the event loop.
        def react(function, *args):
            async def run():
                try:
                    await loop.run_in_executor(None, function, *args)
                except Exception as exc:  # keep reacting to later events whatever happens
                    decky.logger.error("Handling an event failed: %s", exc)

            loop.create_task(run())

        self.events = Events(
            paths,
            loop,
            on_streaming=lambda streaming: react(self.controller.on_streaming_changed, streaming),
            on_files_changed=lambda: react(self.controller.maintain),
            on_steam_exit=lambda: react(self.controller.on_steam_exited),
            delay=self.controller.settle_seconds,
            logger=decky.logger,
        )
        self.controller.steam_running = self.events.steam_running
        self.events.start()
        # The wrapper is installed by the first check, once the files have been quiet for a while.
        self.events.request_check()

    async def _unload(self):
        decky.logger.info("StreamHDR backend unloading")
        if self.events:
            self.events.stop()
            self.events = None
        await asyncio.get_running_loop().run_in_executor(None, self.controller.stop)

    async def _uninstall(self):
        decky.logger.info("StreamHDR uninstalling")
        await asyncio.get_running_loop().run_in_executor(None, self.controller.uninstall)

    async def get_status(self):
        return self.controller.status()

    async def set_option(self, name: str, value):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.set_option, name, value)

    async def reset_settings(self):
        return await asyncio.get_running_loop().run_in_executor(None, self.controller.reset_settings)
