import os
import sys

import decky

# Backend modules live in py_modules/, which Decky adds to the import path.
# Keep them independent of the decky module so they can be unit tested anywhere.
sys.path.insert(0, os.path.join(decky.DECKY_PLUGIN_DIR, "py_modules"))


class Plugin:
    async def _main(self):
        decky.logger.info("StreamHDR backend loaded (user=%s)", decky.DECKY_USER)

    async def _unload(self):
        decky.logger.info("StreamHDR backend unloading")

    async def _uninstall(self):
        decky.logger.info("StreamHDR uninstalling")

    async def ping(self) -> str:
        return "pong"
