import json
import os
import unittest

from streamhdr import wrapper
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


class ControllerTests(WrapperTestCase):
    def make(self):
        settings = Settings(os.path.join(self.tmp, "settings", "settings.json"))
        return Controller(self.paths, settings)

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


if __name__ == "__main__":
    unittest.main()
