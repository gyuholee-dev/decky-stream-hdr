import json
import os
import unittest

from streamhdr import gamescope, look, options, wrapper
from streamhdr.controller import Controller
from streamhdr.settings import Settings

from .test_wrapper import ELF_V1, WrapperTestCase


class SettingsTests(WrapperTestCase):
    def path(self):
        return os.path.join(self.tmp, "settings", "settings.json")

    def test_defaults_when_file_is_missing(self):
        self.assertTrue(Settings(self.path()).get("hdr_enabled"))

    def test_values_persist(self):
        Settings(self.path()).set("hdr_enabled", False)
        self.assertFalse(Settings(self.path()).get("hdr_enabled"))

    def test_damaged_file_falls_back_to_defaults(self):
        os.makedirs(os.path.dirname(self.path()))
        with open(self.path(), "w") as handle:
            handle.write("{not json")
        self.assertTrue(Settings(self.path()).get("hdr_enabled"))

    def test_wrong_type_is_ignored(self):
        os.makedirs(os.path.dirname(self.path()))
        with open(self.path(), "w") as handle:
            json.dump({"hdr_enabled": "yes"}, handle)
        self.assertTrue(Settings(self.path()).get("hdr_enabled"))

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
            raise gamescope.GamescopeError("env_missing", "no gamescope")
        self.look = path

    def clear_look(self, env_file):
        self.calls.append(("clear", None))
        if self.fail:
            raise gamescope.GamescopeError("env_missing", "no gamescope")
        self.look = None

    def get_look(self, env_file):
        if self.fail:
            raise gamescope.GamescopeError("env_missing", "no gamescope")
        return self.look


class ControllerTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def test_enabling_installs_wrapper_and_sets_flag(self):
        controller = self.make()
        status = controller.set_option("hdr_enabled", True)
        self.assertTrue(status["hdr_enabled"])
        self.assertTrue(status["wrapper"]["wrapped"])
        self.assertTrue(status["wrapper"]["enabled"])
        self.assertIsNone(status["error"])

    def test_disabling_removes_flag_but_keeps_wrapper(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        status = controller.set_option("hdr_enabled", False)
        self.assertFalse(status["hdr_enabled"])
        self.assertFalse(status["wrapper"]["enabled"])
        self.assertTrue(status["wrapper"]["wrapped"])

    def test_start_applies_saved_setting(self):
        self.make().set_option("hdr_enabled", True)
        wrapper.restore(self.paths)
        wrapper.set_enabled(self.paths, False)
        controller = self.make()
        controller.start()
        controller.maintain()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])
        self.assertTrue(controller.status()["wrapper"]["enabled"])

    def test_start_does_not_touch_the_streaming_client(self):
        wrapper.restore(self.paths)
        controller = self.make()
        controller.start()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])
        self.assertTrue(wrapper.is_enabled(self.paths))  # only the flag is brought in line
        self.assertIsNone(controller.status()["error"])

    def test_start_with_default_settings_installs_the_wrapper_at_the_first_check(self):
        controller = self.make()
        controller.start()
        controller.maintain()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])

    def test_start_with_hdr_off_still_installs_the_wrapper_but_without_the_flag(self):
        controller = self.make()
        controller.settings.set("hdr_enabled", False)
        controller.start()
        controller.maintain()
        status = controller.status()
        self.assertTrue(status["wrapper"]["wrapped"])
        self.assertFalse(status["wrapper"]["enabled"])
        self.assertFalse(os.path.exists(self.paths.flag))

    def test_problem_is_reported_and_flag_cleared(self):
        os.remove(self.paths.client)
        controller = self.make()
        status = controller.set_option("hdr_enabled", True)
        self.assertEqual(status["error"], {"code": "client_not_found", "detail": None})
        self.assertFalse(status["wrapper"]["enabled"])

    def test_stop_restores_original(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        controller.stop()
        with open(self.paths.client, "rb") as handle:
            self.assertEqual(handle.read(), ELF_V1)

    def test_uninstall_cleans_up(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        controller.set_option("saturation", 150)
        controller.uninstall()
        self.assertFalse(os.path.exists(self.paths.shim))
        self.assertFalse(os.path.exists(self.paths.flag))
        self.assertFalse(os.path.exists(self.paths.data_dir))


class SaturationTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def lut(self, percent):
        return os.path.join(self.paths.luts_dir, look.lut_filename(look.Look(percent, 100, 100, options.DEFAULTS["paper_white"])))

    def test_value_is_snapped_stored_and_lut_prepared(self):
        controller = self.make()
        status = controller.set_option("saturation", 148)
        self.assertEqual(status["saturation"], 150)
        self.assertTrue(os.path.isfile(self.lut(150)))
        self.assertEqual(Settings(os.path.join(self.tmp, "settings", "settings.json")).get("saturation"), 150)

    def test_nothing_is_applied_while_not_streaming(self):
        controller = self.make()
        controller.set_option("saturation", 150)
        self.assertEqual(self.gs.calls, [])

    def test_stream_start_applies_and_end_clears(self):
        controller = self.make()
        controller.set_option("saturation", 150)
        controller.on_streaming_changed(True)
        self.assertEqual(self.gs.look, self.lut(150))
        controller.on_streaming_changed(False)
        self.assertIsNone(self.gs.look)

    def test_changing_value_during_stream_applies_immediately(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.set_option("saturation", 135)
        self.assertEqual(self.gs.look, self.lut(135))
        controller.set_option("saturation", 175)
        self.assertEqual(self.gs.look, self.lut(175))

    def test_default_value_clears_the_atom(self):
        controller = self.make()
        controller.set_option("saturation", 150)
        controller.on_streaming_changed(True)
        controller.set_option("saturation", 100)
        self.assertIsNone(self.gs.look)
        self.assertFalse(os.path.exists(self.lut(100)))

    def test_default_value_never_touches_gamescope_when_nothing_was_set(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        controller.on_streaming_changed(False)
        self.assertEqual(self.gs.calls, [])

    def test_gamescope_problem_is_reported(self):
        controller = self.make()
        controller.set_option("saturation", 150)
        self.gs.fail = True
        controller.on_streaming_changed(True)
        self.assertEqual(controller.status()["look_error"], {"code": "env_missing", "detail": None})

    def test_stop_clears_the_atom(self):
        controller = self.make()
        controller.set_option("saturation", 150)
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


class HdrActiveTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        return Controller(self.paths, settings, gamescope_api=FakeGamescope())

    def test_not_active_without_a_stream(self):
        controller = self.make()
        self.assertFalse(controller.set_option("hdr_enabled", True)["hdr_active"])

    def test_active_while_streaming_with_hdr_on(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        controller.on_streaming_changed(True)
        self.assertTrue(controller.status()["hdr_active"])
        controller.on_streaming_changed(False)
        self.assertFalse(controller.status()["hdr_active"])

    def test_not_active_while_streaming_with_hdr_off(self):
        controller = self.make()
        controller.on_streaming_changed(True)
        self.assertFalse(controller.status()["hdr_active"])
        self.assertTrue(controller.status()["streaming"])

    def test_not_active_when_the_wrapper_could_not_be_installed(self):
        os.remove(self.paths.client)
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        controller.on_streaming_changed(True)
        self.assertFalse(controller.status()["hdr_active"])


class MaintainTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs)

    def test_reinstalls_wrapper_after_steam_restores_original(self):
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        self.write_client(b"\x7fELF-steam-update")
        controller.maintain()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])
        with open(self.paths.real, "rb") as handle:
            self.assertEqual(handle.read(), b"\x7fELF-steam-update")

    def test_repairs_the_wrapper_even_when_hdr_is_off(self):
        controller = self.make()
        controller.settings.set("hdr_enabled", False)
        controller.maintain()
        status = controller.status()
        self.assertTrue(status["wrapper"]["wrapped"])
        self.assertFalse(status["wrapper"]["enabled"])

    def test_recovers_after_steam_was_not_yet_started(self):
        os.remove(self.paths.client)
        controller = self.make()
        controller.set_option("hdr_enabled", True)
        self.assertIsNotNone(controller.status()["error"])
        self.write_client(b"\x7fELF-late")
        controller.maintain()
        self.assertIsNone(controller.status()["error"])
        self.assertTrue(controller.status()["wrapper"]["enabled"])

    def make_with_clock(self):
        self.now = 1000.0
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        self.gs = FakeGamescope()
        return Controller(self.paths, settings, gamescope_api=self.gs, clock=lambda: self.now)

    def steam_restores(self, controller):
        """Steam puts its original client back and the files then go quiet: the plugin checks."""
        self.write_client(b"\x7fELF-steam-update")
        controller.maintain()

    def test_stops_reinstalling_when_steam_keeps_restoring_the_client(self):
        controller = self.make_with_clock()
        controller.set_option("hdr_enabled", True)
        for _ in range(2):
            self.steam_restores(controller)
            self.assertTrue(controller.status()["wrapper"]["wrapped"])
            self.now += 25
        self.steam_restores(controller)  # the third time within ten minutes
        status = controller.status()
        self.assertFalse(status["wrapper"]["wrapped"])
        self.assertEqual(status["error"]["code"], "wrapper_unstable")
        # Later checks leave it alone instead of fighting on.
        self.now += 25
        controller.maintain()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])

    def test_restores_far_apart_are_not_a_fight(self):
        controller = self.make_with_clock()
        controller.set_option("hdr_enabled", True)
        for _ in range(5):
            self.steam_restores(controller)
            self.assertTrue(controller.status()["wrapper"]["wrapped"])
            self.assertIsNone(controller.status()["error"])
            self.now += 700  # Steam updates now and then; that is normal

    def test_switching_hdr_streaming_tries_again_after_giving_up(self):
        controller = self.make_with_clock()
        controller.set_option("hdr_enabled", True)
        for _ in range(3):
            self.steam_restores(controller)
            self.now += 25
        self.assertEqual(controller.status()["error"]["code"], "wrapper_unstable")
        controller.set_option("hdr_enabled", False)
        controller.set_option("hdr_enabled", True)
        status = controller.status()
        self.assertIsNone(status["error"])
        self.assertTrue(status["wrapper"]["wrapped"])

    def test_the_first_install_after_start_does_not_count_as_a_restore(self):
        controller = self.make_with_clock()
        wrapper.restore(self.paths)
        controller.start()
        for _ in range(2):
            controller.maintain()
            self.write_client(b"\x7fELF-steam-update")
            self.now += 25
        controller.maintain()
        self.assertIsNone(controller.status()["error"])
        self.assertTrue(controller.status()["wrapper"]["wrapped"])

    def test_steam_ending_puts_the_original_back_and_the_next_install_is_not_a_restore(self):
        controller = self.make_with_clock()
        controller.set_option("hdr_enabled", True)
        self.assertTrue(controller.status()["wrapper"]["wrapped"])
        controller.on_steam_exited()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])
        self.assertTrue(wrapper.is_elf(self.paths.client))
        for _ in range(4):  # Steam restarts again and again, but the plugin keeps clear of its repairs
            controller.maintain()
            self.assertTrue(controller.status()["wrapper"]["wrapped"])
            controller.on_steam_exited()
            self.now += 25
        self.assertIsNone(controller.status()["error"])

    def test_the_wrapper_waits_for_steam_to_run(self):
        controller = self.make_with_clock()
        controller.steam_running = lambda: False
        controller.start()
        controller.maintain()
        self.assertFalse(controller.status()["wrapper"]["wrapped"])
        controller.steam_running = lambda: True
        controller.maintain()
        self.assertTrue(controller.status()["wrapper"]["wrapped"])

    def test_leaves_a_correct_color_table_alone(self):
        controller = self.make()
        controller.set_option("saturation", 150)
        controller.on_streaming_changed(True)
        self.gs.calls.clear()
        controller.maintain()
        self.assertEqual(self.gs.calls, [])


if __name__ == "__main__":
    unittest.main()
