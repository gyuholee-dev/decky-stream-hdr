import os
import sys

import decky

# Backend modules live in py_modules/, which Decky adds to the import path.
# Keep them independent of the decky module so they can be unit tested anywhere.
sys.path.insert(0, os.path.join(decky.DECKY_PLUGIN_DIR, "py_modules"))

from streamhdr.controller import Controller  # noqa: E402
from streamhdr.paths import Paths  # noqa: E402
from streamhdr.settings import Settings  # noqa: E402


class Plugin:
    controller: Controller

    async def _main(self):
        paths = Paths.for_user(decky.DECKY_USER_HOME, decky.DECKY_PLUGIN_DIR)
        settings = Settings(os.path.join(decky.DECKY_PLUGIN_SETTINGS_DIR, "settings.json"))
        self.controller = Controller(paths, settings, decky.logger)
        decky.logger.info("StreamHDR backend loaded (user=%s)", decky.DECKY_USER)
        self.controller.start()

    async def _unload(self):
        decky.logger.info("StreamHDR backend unloading")
        self.controller.stop()

    async def _uninstall(self):
        decky.logger.info("StreamHDR uninstalling")
        self.controller.uninstall()

    async def get_status(self):
        return self.controller.status()

    async def set_hdr_enabled(self, enabled: bool):
        return self.controller.set_hdr_enabled(enabled)
