import os
import shutil
import subprocess
import tempfile
import unittest

from streamhdr import wrapper
from streamhdr.paths import Paths

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELF_V1 = b"\x7fELF-original-v1"
ELF_V2 = b"\x7fELF-steam-update-v2"


class WrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = os.path.join(self.tmp, "home")
        plugin_dir = os.path.join(self.tmp, "plugin")
        os.makedirs(os.path.join(plugin_dir, "bin"))
        os.makedirs(os.path.join(plugin_dir, "py_modules", "streamhdr"))
        shutil.copy(
            os.path.join(REPO, "py_modules", "streamhdr", "streaming_client.sh.tmpl"),
            os.path.join(plugin_dir, "py_modules", "streamhdr"),
        )
        with open(os.path.join(plugin_dir, "bin", "sdl_hdr_shim.so"), "wb") as handle:
            handle.write(b"\x7fELF-shim")
        self.paths = Paths.for_user(home, plugin_dir)
        os.makedirs(os.path.dirname(self.paths.client))
        self.write_client(ELF_V1)

    def write_client(self, data):
        with open(self.paths.client, "wb") as handle:
            handle.write(data)
        os.chmod(self.paths.client, 0o755)

    def read(self, path):
        with open(path, "rb") as handle:
            return handle.read()


class InstallTests(WrapperTestCase):
    def test_install_wraps_original_binary(self):
        self.assertEqual(wrapper.install(self.paths), "installed")
        self.assertTrue(wrapper.is_wrapper(self.paths.client))
        self.assertEqual(self.read(self.paths.real), ELF_V1)
        self.assertTrue(os.access(self.paths.client, os.X_OK))
        script = self.read(self.paths.client).decode()
        self.assertIn(self.paths.shim, script)
        self.assertIn(self.paths.flag, script)
        self.assertNotIn("__SHIM__", script)
        self.assertTrue(os.path.isfile(self.paths.shim))

    def test_original_inode_is_kept_and_client_path_is_never_empty(self):
        before = os.stat(self.paths.client).st_ino
        wrapper.install(self.paths)
        self.assertEqual(os.stat(self.paths.real).st_ino, before)
        self.assertFalse(os.path.exists(self.paths.real + ".streamhdr-tmp"))

    def test_needs_attention_tracks_missing_pieces(self):
        self.assertTrue(wrapper.needs_attention(self.paths))
        wrapper.install(self.paths)
        wrapper.set_enabled(self.paths, True)
        self.assertFalse(wrapper.needs_attention(self.paths))
        os.remove(self.paths.shim)
        self.assertTrue(wrapper.needs_attention(self.paths))

    def test_install_is_idempotent(self):
        wrapper.install(self.paths)
        self.assertEqual(wrapper.install(self.paths), "ok")
        self.assertEqual(self.read(self.paths.real), ELF_V1)

    def test_reinstall_after_steam_restores_original(self):
        wrapper.install(self.paths)
        self.write_client(ELF_V2)
        self.assertEqual(wrapper.install(self.paths), "installed")
        self.assertEqual(self.read(self.paths.real), ELF_V2)
        self.assertTrue(wrapper.is_wrapper(self.paths.client))

    def test_outdated_wrapper_is_rewritten(self):
        wrapper.install(self.paths)
        with open(self.paths.client, "a") as handle:
            handle.write("# stale\n")
        self.assertEqual(wrapper.install(self.paths), "updated")
        self.assertNotIn("# stale", self.read(self.paths.client).decode())

    def test_missing_client_raises(self):
        os.remove(self.paths.client)
        with self.assertRaises(wrapper.WrapperError):
            wrapper.install(self.paths)

    def test_wrapper_without_saved_original_raises(self):
        wrapper.install(self.paths)
        os.remove(self.paths.real)
        with self.assertRaises(wrapper.WrapperError):
            wrapper.install(self.paths)

    def test_unknown_format_is_left_untouched(self):
        self.write_client(b"not an elf file")
        with self.assertRaises(wrapper.WrapperError):
            wrapper.install(self.paths)
        self.assertEqual(self.read(self.paths.client), b"not an elf file")

    def test_missing_bundled_shim_raises(self):
        os.remove(self.paths.shim_src)
        with self.assertRaises(wrapper.WrapperError):
            wrapper.install(self.paths)
        self.assertEqual(self.read(self.paths.client), ELF_V1)

    def test_changed_bundled_shim_is_copied_again(self):
        wrapper.install(self.paths)
        with open(self.paths.shim_src, "wb") as handle:
            handle.write(b"\x7fELF-shim-new")
        wrapper.install(self.paths)
        self.assertEqual(self.read(self.paths.shim), b"\x7fELF-shim-new")


class RestoreTests(WrapperTestCase):
    def test_restore_puts_original_back(self):
        wrapper.install(self.paths)
        self.assertTrue(wrapper.restore(self.paths))
        self.assertEqual(self.read(self.paths.client), ELF_V1)
        self.assertFalse(os.path.exists(self.paths.real))

    def test_restore_when_not_installed_does_nothing(self):
        self.assertFalse(wrapper.restore(self.paths))
        self.assertEqual(self.read(self.paths.client), ELF_V1)

    def test_restore_drops_stale_copy_after_steam_restored_original(self):
        wrapper.install(self.paths)
        self.write_client(ELF_V2)
        self.assertTrue(wrapper.restore(self.paths))
        self.assertEqual(self.read(self.paths.client), ELF_V2)
        self.assertFalse(os.path.exists(self.paths.real))

    def test_uninstall_removes_plugin_files(self):
        wrapper.install(self.paths)
        wrapper.set_enabled(self.paths, True)
        wrapper.uninstall(self.paths)
        self.assertEqual(self.read(self.paths.client), ELF_V1)
        self.assertFalse(os.path.exists(self.paths.shim))
        self.assertFalse(os.path.exists(self.paths.flag))


class FlagTests(WrapperTestCase):
    def test_enable_and_disable(self):
        self.assertFalse(wrapper.is_enabled(self.paths))
        wrapper.set_enabled(self.paths, True)
        self.assertTrue(wrapper.is_enabled(self.paths))
        wrapper.set_enabled(self.paths, False)
        self.assertFalse(wrapper.is_enabled(self.paths))

    def test_disable_without_flag_is_fine(self):
        wrapper.set_enabled(self.paths, False)

    def test_status_reports_state(self):
        wrapper.install(self.paths)
        wrapper.set_enabled(self.paths, True)
        self.assertEqual(
            wrapper.status(self.paths),
            {
                "client_found": True,
                "wrapped": True,
                "original_saved": True,
                "shim_installed": True,
                "enabled": True,
            },
        )


class WrapperScriptTests(WrapperTestCase):
    """Runs the generated script with a stand-in for the real client."""

    def run_wrapper(self, preload=None):
        wrapper.install(self.paths)
        with open(self.paths.real, "w") as handle:
            handle.write('#!/bin/sh\necho "PRELOAD=$LD_PRELOAD ARGS=$*"\n')
        os.chmod(self.paths.real, 0o755)
        env = dict(os.environ)
        env.pop("LD_PRELOAD", None)
        if preload:
            env["LD_PRELOAD"] = preload
        result = subprocess.run([self.paths.client, "--a", "b"], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_flag_missing_runs_without_preload(self):
        self.assertEqual(self.run_wrapper(), "PRELOAD= ARGS=--a b")

    def test_flag_present_sets_preload(self):
        wrapper.set_enabled(self.paths, True)
        self.assertEqual(self.run_wrapper(), "PRELOAD=%s ARGS=--a b" % self.paths.shim)

    def test_existing_preload_is_kept(self):
        wrapper.set_enabled(self.paths, True)
        self.assertEqual(self.run_wrapper("/other.so"), "PRELOAD=%s:/other.so ARGS=--a b" % self.paths.shim)

    def test_missing_shim_file_skips_preload(self):
        wrapper.set_enabled(self.paths, True)
        out = self.run_wrapper()
        os.remove(self.paths.shim)
        result = subprocess.run([self.paths.client], capture_output=True, text=True)
        self.assertIn("PRELOAD= ", result.stdout)
        self.assertIn("PRELOAD=", out)


if __name__ == "__main__":
    unittest.main()
