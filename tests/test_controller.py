import json
import os
import unittest

from streamhdr import gamescope, saturation, wrapper
from streamhdr.controller import Controller
from streamhdr.settings import Settings

from .test_wrapper import ELF_V1, WrapperTestCase


class SettingsTests(WrapperTestCase):
    def path(self):
        return os.path.join(self.tmp, "settings", "settings.json")

    def test_defaults_when_file_is_missing(self):
        self.assertFalse(Settings(self.path()).get("hdr_enabled"))

    def test_values_persist(self):
        Settings(self.path()).set("hdr_enabled", True)
        self.assertTrue(Settings(self.path()).get("hdr_enabled"))

    def test_damaged_file_falls_back_to_defaults(self):
        os.makedirs(os.path.dirname(self.path()))
        with open(self.path(), "w") as handle:
            handle.write("{not json")
        self.assertFalse(Settings(self.path()).get("hdr_enabled"))

    def test_wrong_type_is_ignored(self):
        os.makedirs(os.path.dirname(self.path()))
        with open(self.path(), "w") as handle:
            json.dump({"hdr_enabled": "yes"}, handle)
        self.assertFalse(Settings(self.path()).get("hdr_enabled"))

    def test_unknown_key_is_rejected(self):
        with self.assertRaises(KeyError):
            Settings(self.path()).set("nope", 1)


class FakeGamescope:
    """Records calls instead of talking to gamescope."""

    def __init__(self):
        self.look = None
        self.calls = []
        self.fail = False

    def set_look(self, path, env_file):
        self.calls.append(("set", path))
        if self.fail:
            raise gamescope.GamescopeError("no gamescope")
        self.look = path

    def clear_look(self, env_file):
        self.calls.append(("clear", None))
        if self.fail:
            raise gamescope.GamescopeError("no gamescope")
        self.look = None

    def get_look(self, env_file):
        if self.fail:
            raise gamescope.GamescopeError("no gamescope")
        return self.look


class ControllerTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def test_enabling_installs_wrapper_and_sets_flag(self):
        controller = self.make()
        status = controller.set_hdr_enabled(True)
        self.assertTrue(status["hdr_enabled"])
        self.assertTrue(status["wrapper"]["wrapped"])
        self.assertTrue(status["wrapper"]["enabled"])
        self.assertIsNone(status["error"])

    def test_disabling_removes_flag_but_keeps_wrapper(self):
        controller = self.make()
        controller.set_hdr_enabled(True)
        status = controller.set_hdr_enabled(False)
        self.assertFalse(status["hdr_enabled"])
        self.assertFalse(status["wrapper"]["enabled"])
        self.assertTrue(status["wrapper"]["wrapped"])

    def test_start_applies_saved_setting(self):
        self.make().set_hdr_enabled(True)
        wrapper.restore(self.paths)
        wrapper.set_enabled(self.paths, False)
        controller = self.make()
        controller.start()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])
        self.assertTrue(controller.status()["wrapper"]["enabled"])

    def test_start_with_hdr_off_leaves_client_untouched(self):
        controller = self.make()
        controller.start()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])
        with open(self.paths.client, "rb") as handle:
            self.assertEqual(handle.read(), ELF_V1)

    def test_problem_is_reported_and_flag_cleared(self):
        os.remove(self.paths.client)
        controller = self.make()
        status = controller.set_hdr_enabled(True)
        self.assertIsNotNone(status["error"])
        self.assertFalse(status["wrapper"]["enabled"])

    def test_stop_restores_original(self):
        controller = self.make()
        controller.set_hdr_enabled(True)
        controller.stop()
        with open(self.paths.client, "rb") as handle:
            self.assertEqual(handle.read(), ELF_V1)

    def test_uninstall_cleans_up(self):
        controller = self.make()
        controller.set_hdr_enabled(True)
        controller.uninstall()
        self.assertFalse(os.path.exists(self.paths.shim))
        self.assertFalse(os.path.exists(self.paths.flag))


class SaturationTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def lut(self, percent):
        return os.path.join(self.paths.luts_dir, saturation.lut_filename(percent))

    def test_value_is_snapped_stored_and_lut_prepared(self):
        controller = self.make()
        status = controller.set_saturation(147)
        self.assertEqual(status["saturation"], 150)
        self.assertTrue(os.path.isfile(self.lut(150)))
        self.assertEqual(Settings(os.path.join(self.tmp, "settings", "settings.json")).get("saturation"), 150)

    def test_nothing_is_applied_while_not_streaming(self):
        controller = self.make()
        controller.set_saturation(150)
        self.assertEqual(self.gs.calls, [])

    def test_stream_start_applies_and_end_clears(self):
        controller = self.make()
        controller.set_saturation(150)
        controller.on_streaming_changed(True)
        self.assertEqual(self.gs.look, self.lut(150))
        controller.on_streaming_changed(False)
        self.assertIsNone(self.gs.look)

    def test_changing_value_during_stream_applies_immediately(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_saturation(130)
        self.assertEqual(self.gs.look, self.lut(130))
        controller.set_saturation(170)
        self.assertEqual(self.gs.look, self.lut(170))

    def test_default_value_clears_the_atom(self):
        controller = self.make()
        controller.set_saturation(150)
        controller.on_streaming_changed(True)
        controller.set_saturation(100)
        self.assertIsNone(self.gs.look)
        self.assertFalse(os.path.exists(self.lut(100)))

    def test_default_value_never_touches_gamescope_when_nothing_was_set(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.on_streaming_changed(False)
        self.assertEqual(self.gs.calls, [])

    def test_gamescope_problem_is_reported(self):
        controller = self.make()
        controller.set_saturation(150)
        self.gs.fail = True
        controller.on_streaming_changed(True)
        self.assertIsNotNone(controller.status()["saturation_error"])

    def test_stop_clears_the_atom(self):
        controller = self.make()
        controller.set_saturation(150)
        controller.on_streaming_changed(True)
        controller.stop()
        self.assertIsNone(self.gs.look)

    def test_start_clears_a_leftover_atom_from_this_plugin_only(self):
        controller = self.make()
        self.gs.look = self.lut(150)
        controller.start()
        self.assertIsNone(self.gs.look)
        controller = self.make()
        self.gs.look = "/home/user/own.cube"
        controller.start()
        self.assertEqual(self.gs.look, "/home/user/own.cube")

    def test_start_without_gamescope_is_fine(self):
        controller = self.make()
        self.gs.fail = True
        controller.start()


class MaintainTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def test_reinstalls_wrapper_after_steam_restores_original(self):
        controller = self.make()
        controller.set_hdr_enabled(True)
        self.write_client(b"\x7fELF-steam-update")
        controller.maintain()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])
        with open(self.paths.real, "rb") as handle:
            self.assertEqual(handle.read(), b"\x7fELF-steam-update")

    def test_does_nothing_when_hdr_is_off(self):
        controller = self.make()
        controller.maintain()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])

    def test_recovers_after_steam_was_not_yet_started(self):
        os.remove(self.paths.client)
        controller = self.make()
        controller.set_hdr_enabled(True)
        self.assertIsNotNone(controller.status()["error"])
        self.write_client(b"\x7fELF-late")
        controller.maintain()
        self.assertIsNone(controller.status()["error"])
        self.assertTrue(controller.status()["wrapper"]["enabled"])

    def test_reapplies_a_lost_color_table_while_streaming(self):
        controller = self.make()
        controller.set_saturation(150)
        controller.on_streaming_changed(True)
        self.gs.look = None  # for example gamescope restarted
        controller.maintain()
        self.assertEqual(self.gs.look, os.path.join(self.paths.luts_dir, saturation.lut_filename(150)))

    def test_leaves_a_correct_color_table_alone(self):
        controller = self.make()
        controller.set_saturation(150)
        controller.on_streaming_changed(True)
        self.gs.calls.clear()
        controller.maintain()
        self.assertEqual(self.gs.calls, [])


if __name__ == "__main__":
    unittest.main()
