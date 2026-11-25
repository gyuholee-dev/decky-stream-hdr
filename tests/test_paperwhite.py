import os
import unittest

from streamhdr import paperwhite
from streamhdr.controller import Controller
from streamhdr.settings import Settings

from .test_controller import FakeGamescope
from .test_wrapper import WrapperTestCase


class ClampTests(unittest.TestCase):
    def test_snaps_to_the_grid_and_limits(self):
        self.assertEqual(paperwhite.clamp_nits(200), 200)
        self.assertEqual(paperwhite.clamp_nits(204), 200)
        self.assertEqual(paperwhite.clamp_nits(206), 210)
        self.assertEqual(paperwhite.clamp_nits(10), 80)
        self.assertEqual(paperwhite.clamp_nits(9999), 480)


class ControllerPaperWhiteTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        return Controller(self.paths, settings, gamescope_api=FakeGamescope())

    def read_file(self):
        with open(self.paths.paper_white) as handle:
            return handle.read().strip()

    def test_default_is_written_at_start(self):
        controller = self.make()
        controller.start()
        self.assertEqual(self.read_file(), "200")
        self.assertEqual(controller.status()["paper_white"], 200)

    def test_new_value_is_snapped_saved_and_written(self):
        controller = self.make()
        status = controller.set_paper_white(226)
        self.assertEqual(status["paper_white"], 230)
        self.assertEqual(self.read_file(), "230")
        self.assertEqual(Settings(os.path.join(self.tmp, "settings", "settings.json")).get("paper_white"), 230)

    def test_uninstall_removes_the_file(self):
        controller = self.make()
        controller.set_paper_white(250)
        controller.uninstall()
        self.assertFalse(os.path.exists(self.paths.paper_white))


if __name__ == "__main__":
    unittest.main()
