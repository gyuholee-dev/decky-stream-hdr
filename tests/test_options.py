import os
import re
import unittest

from streamhdr import options
from streamhdr.controller import Controller
from streamhdr.settings import Settings

from .test_controller import FakeGamescope
from .test_wrapper import WrapperTestCase


class SpecTests(unittest.TestCase):
    def test_every_option_is_complete_and_its_default_is_on_the_grid(self):
        for name, spec in options.SPEC.items():
            if isinstance(spec["default"], bool):
                continue
            self.assertLessEqual(spec["min"], spec["default"], name)
            self.assertLessEqual(spec["default"], spec["max"], name)
            self.assertEqual((spec["default"] - spec["min"]) % spec["step"], 0, name)
            self.assertEqual(options.snap(name, spec["default"]), spec["default"], name)

    def test_the_color_options_start_neutral(self):
        for name in options.LOOK_OPTIONS:
            self.assertEqual(options.SPEC[name]["default"], options.SPEC[name]["neutral"], name)

    def test_which_options_are_frozen_during_a_stream(self):
        self.assertEqual(set(options.FROZEN_WHILE_STREAMING), {"hdr_enabled", "paper_white"})
        self.assertEqual(set(options.LOOK_OPTIONS), {"contrast", "gamma", "saturation"})

    def test_snap_puts_values_on_the_grid_and_inside_the_range(self):
        self.assertEqual(options.snap("paper_white", 204), 200)
        self.assertEqual(options.snap("paper_white", 206), 210)
        self.assertEqual(options.snap("paper_white", 10), 80)
        self.assertEqual(options.snap("paper_white", 9999), 480)
        self.assertEqual(options.snap("saturation", 148), 150)
        self.assertEqual(options.snap("saturation", 999), 200)
        self.assertEqual(options.snap("contrast", -5), 0)
        self.assertEqual(options.snap("contrast", 102), 100)
        self.assertEqual(options.snap("gamma", 102), 100)
        self.assertEqual(options.snap("gamma", 103), 105)
        self.assertEqual(options.snap("gamma", 30), 50)
        self.assertEqual(options.snap("gamma", 999), 200)

    def test_a_toggle_becomes_a_bool(self):
        self.assertIs(options.snap("hdr_enabled", 1), True)
        self.assertIs(options.snap("hdr_enabled", 0), False)

    def test_is_valid_checks_the_type(self):
        self.assertTrue(options.is_valid("hdr_enabled", False))
        self.assertFalse(options.is_valid("hdr_enabled", 1))
        self.assertTrue(options.is_valid("saturation", 100))
        self.assertFalse(options.is_valid("saturation", True))
        self.assertFalse(options.is_valid("saturation", "100"))


class ShimTests(unittest.TestCase):
    """The injection library cannot read options.json, so its copy of the paper white numbers must match."""

    def number(self, name):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "src", "sdl_hdr_shim.c")
        with open(path, encoding="utf-8") as handle:
            match = re.search(r"#define %s ([0-9.]+)f" % name, handle.read())
        self.assertIsNotNone(match, name)
        return float(match.group(1))

    def test_paper_white_numbers_match_the_options(self):
        spec = options.SPEC["paper_white"]
        self.assertEqual(self.number("PAPER_WHITE_DEFAULT_NITS"), spec["default"])
        self.assertEqual(self.number("PAPER_WHITE_MIN_NITS"), spec["min"])
        self.assertEqual(self.number("PAPER_WHITE_MAX_NITS"), spec["max"])


class OptionTests(WrapperTestCase):
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
        status = controller.set_option("paper_white", 226)
        self.assertEqual(status["paper_white"], 230)
        self.assertEqual(self.read_file(), "230")
        self.assertEqual(Settings(os.path.join(self.tmp, "settings", "settings.json")).get("paper_white"), 230)

    def test_contrast_and_gamma_are_snapped_and_saved(self):
        controller = self.make()
        self.assertEqual(controller.set_option("contrast", 103)["contrast"], 105)
        self.assertEqual(controller.set_option("gamma", 147)["gamma"], 145)
        self.assertEqual(controller.set_option("gamma", 10)["gamma"], 50)

    def test_changes_while_streaming_use_a_new_look_file_and_drop_the_old_one(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_option("contrast", 120)
        first = controller.gs.look
        controller.set_option("gamma", 80)
        second = controller.gs.look
        self.assertNotEqual(first, second)
        self.assertFalse(os.path.exists(first))
        self.assertTrue(os.path.exists(second))

    def test_options_that_apply_at_connect_are_ignored_during_a_stream(self):
        controller = self.make()
        controller.start()
        controller.set_option("paper_white", 250)
        controller.on_streaming_changed(True)
        status = controller.set_option("paper_white", 300)
        self.assertEqual(status["paper_white"], 250)
        self.assertEqual(self.read_file(), "250")
        status = controller.set_option("hdr_enabled", False)
        self.assertTrue(status["hdr_enabled"])
        self.assertTrue(status["wrapper"]["enabled"])

    def test_color_options_still_change_during_a_stream(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        self.assertEqual(controller.set_option("contrast", 120)["contrast"], 120)
        self.assertIsNotNone(controller.gs.look)

    def test_a_new_paper_white_gets_a_matching_color_table_ready(self):
        controller = self.make()
        controller.set_option("contrast", 120)
        controller.set_option("paper_white", 250)
        files = os.listdir(self.paths.luts_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("_p250.cube"))

    def test_unknown_options_are_ignored(self):
        controller = self.make()
        before = controller.status()
        self.assertEqual(controller.set_option("nonsense", 5), before)

    def test_all_neutral_removes_the_look(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_option("gamma", 80)
        self.assertIsNotNone(controller.gs.look)
        controller.set_option("gamma", 100)
        self.assertIsNone(controller.gs.look)

    def test_reset_settings_restores_every_default(self):
        controller = self.make()
        controller.set_option("hdr_enabled", False)
        controller.set_option("paper_white", 250)
        controller.set_option("contrast", 120)
        controller.set_option("gamma", 80)
        controller.set_option("saturation", 150)
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
        controller.set_option("gamma", 80)
        self.assertIsNotNone(controller.gs.look)
        controller.reset_settings()
        self.assertIsNone(controller.gs.look)

    def test_reset_while_streaming_keeps_the_frozen_options(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        controller.set_option("paper_white", 250)
        controller.on_streaming_changed(True)
        controller.set_option("contrast", 120)
        controller.set_option("saturation", 150)
        status = controller.reset_settings()
        self.assertTrue(status["hdr_enabled"])
        self.assertEqual(status["paper_white"], 250)
        self.assertEqual((status["contrast"], status["gamma"], status["saturation"]), (100, 100, 100))
        self.assertEqual(self.read_file(), "250")
        self.assertTrue(status["wrapper"]["enabled"])

    def test_uninstall_removes_the_file(self):
        controller = self.make()
        controller.set_option("paper_white", 250)
        controller.uninstall()
        self.assertFalse(os.path.exists(self.paths.paper_white))


if __name__ == "__main__":
    unittest.main()
