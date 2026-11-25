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
        self.assertEqual(self.read_file(), "230")
        self.assertEqual(controller.status()["paper_white"], 230)

    def test_new_value_is_snapped_saved_and_written(self):
        controller = self.make()
        status = controller.set_paper_white(226)
        self.assertEqual(status["paper_white"], 230)
        self.assertEqual(self.read_file(), "230")
        self.assertEqual(Settings(os.path.join(self.tmp, "settings", "settings.json")).get("paper_white"), 230)

    def test_contrast_and_gamma_are_snapped_and_saved(self):
        controller = self.make()
        self.assertEqual(controller.set_contrast(103)["contrast"], 105)
        self.assertEqual(controller.set_gamma(147)["gamma"], 145)
        self.assertEqual(controller.set_gamma(10)["gamma"], 50)

    def test_changes_while_streaming_use_a_new_look_file_and_drop_the_old_one(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_contrast(120)
        first = controller.gs.look
        controller.set_gamma(80)
        second = controller.gs.look
        self.assertNotEqual(first, second)
        self.assertFalse(os.path.exists(first))
        self.assertTrue(os.path.exists(second))

    def test_paper_white_change_rebuilds_the_look_while_streaming(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_contrast(120)
        first = controller.gs.look
        controller.set_paper_white(250)
        self.assertNotEqual(controller.gs.look, first)

    def test_all_neutral_removes_the_look(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_gamma(80)
        self.assertIsNotNone(controller.gs.look)
        controller.set_gamma(100)
        self.assertIsNone(controller.gs.look)

    def test_reset_settings_restores_every_default(self):
        controller = self.make()
        controller.set_hdr_enabled(False)
        controller.set_paper_white(250)
        controller.set_contrast(120)
        controller.set_gamma(80)
        controller.set_saturation(150)
        status = controller.reset_settings()
        self.assertEqual(
            (status["hdr_enabled"], status["paper_white"], status["contrast"], status["gamma"], status["saturation"]),
            (True, 230, 100, 100, 100),
        )
        self.assertEqual(self.read_file(), "230")
        self.assertTrue(status["wrapper"]["enabled"])

    def test_reset_while_streaming_takes_the_look_off(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_gamma(80)
        self.assertIsNotNone(controller.gs.look)
        controller.reset_settings()
        self.assertIsNone(controller.gs.look)

    def test_reset_while_streaming_keeps_the_frozen_options(self):
        controller = self.make()
        controller.set_hdr_enabled(True)
        controller.set_paper_white(250)
        controller.on_streaming_changed(True)
        controller.set_contrast(120)
        controller.set_saturation(150)
        status = controller.reset_settings()
        self.assertTrue(status["hdr_enabled"])
        self.assertEqual(status["paper_white"], 250)
        self.assertEqual((status["contrast"], status["gamma"], status["saturation"]), (100, 100, 100))
        self.assertEqual(self.read_file(), "250")
        self.assertTrue(status["wrapper"]["enabled"])

    def test_uninstall_removes_the_file(self):
        controller = self.make()
        controller.set_paper_white(250)
        controller.uninstall()
        self.assertFalse(os.path.exists(self.paths.paper_white))


if __name__ == "__main__":
    unittest.main()
