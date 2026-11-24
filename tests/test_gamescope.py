import os
import shutil
import subprocess
import tempfile
import unittest

from streamhdr import gamescope


class ParseTests(unittest.TestCase):
    def test_parses_plain_export_and_quoted_lines(self):
        env = gamescope.parse_environment(
            "# comment\nDISPLAY=:1\nexport XAUTHORITY='/tmp/auth file'\nWAYLAND_DISPLAY=\"gamescope-0\"\n\nnot a line\n"
        )
        self.assertEqual(env["DISPLAY"], ":1")
        self.assertEqual(env["XAUTHORITY"], "/tmp/auth file")
        self.assertEqual(env["WAYLAND_DISPLAY"], "gamescope-0")
        self.assertNotIn("not a line", env)

    def test_environment_file_path(self):
        self.assertEqual(gamescope.environment_file_for(1000), "/run/user/1000/gamescope-environment")
        self.assertEqual(gamescope.environment_file_for(1000, "/x"), "/x/gamescope-environment")


class XpropTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env_file = os.path.join(self.tmp, "gamescope-environment")
        with open(self.env_file, "w") as handle:
            handle.write("DISPLAY=:1\n")
        self.calls = []

    def runner(self, returncode=0, error=None):
        def run(args, **kwargs):
            self.calls.append((args, kwargs))
            if error:
                raise error
            return subprocess.CompletedProcess(args, returncode, "", "boom")
        return run

    def test_set_look_command_and_environment(self):
        gamescope.set_look("/luts/a.cube", self.env_file, self.runner())
        args, kwargs = self.calls[0]
        self.assertEqual(
            args,
            ["xprop", "-root", "-f", gamescope.ATOM, "8s", "-set", gamescope.ATOM, "/luts/a.cube"],
        )
        self.assertEqual(kwargs["env"]["DISPLAY"], ":1")

    def test_clear_look_command(self):
        gamescope.clear_look(self.env_file, self.runner())
        self.assertEqual(self.calls[0][0], ["xprop", "-root", "-remove", gamescope.ATOM])

    def test_get_look_reads_current_path(self):
        run = self.runner_with_stdout('GAMESCOPE_COLOR_LOOK_PQ(STRING) = "/luts/a.cube"\n')
        self.assertEqual(gamescope.get_look(self.env_file, run), "/luts/a.cube")
        self.assertEqual(self.calls[0][0], ["xprop", "-root", gamescope.ATOM])

    def test_get_look_when_not_set(self):
        run = self.runner_with_stdout("GAMESCOPE_COLOR_LOOK_PQ:  not found.\n")
        self.assertIsNone(gamescope.get_look(self.env_file, run))

    def runner_with_stdout(self, stdout):
        def run(args, **kwargs):
            self.calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0, stdout, "")
        return run

    def test_missing_environment_file(self):
        with self.assertRaises(gamescope.GamescopeError):
            gamescope.set_look("/x", os.path.join(self.tmp, "none"), self.runner())

    def test_environment_without_display(self):
        with open(self.env_file, "w") as handle:
            handle.write("FOO=bar\n")
        with self.assertRaises(gamescope.GamescopeError):
            gamescope.clear_look(self.env_file, self.runner())

    def test_missing_xprop_tool(self):
        with self.assertRaises(gamescope.GamescopeError) as raised:
            gamescope.clear_look(self.env_file, self.runner(error=FileNotFoundError()))
        self.assertIn("xprop", str(raised.exception))

    def test_failed_command(self):
        with self.assertRaises(gamescope.GamescopeError):
            gamescope.clear_look(self.env_file, self.runner(returncode=1))

    def test_timeout(self):
        with self.assertRaises(gamescope.GamescopeError):
            gamescope.clear_look(self.env_file, self.runner(error=subprocess.TimeoutExpired("xprop", 10)))


if __name__ == "__main__":
    unittest.main()
