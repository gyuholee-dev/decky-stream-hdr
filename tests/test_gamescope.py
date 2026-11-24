import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

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

    def test_missing_environment_file_falls_back_to_the_current_display(self):
        with unittest.mock.patch.dict(os.environ, {"DISPLAY": ":7"}):
            gamescope.clear_look(os.path.join(self.tmp, "none"), self.runner())
        self.assertEqual(self.calls[0][1]["env"]["DISPLAY"], ":7")

    def test_without_any_display_the_usual_one_is_used(self):
        env = {key: value for key, value in os.environ.items() if key != "DISPLAY"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            gamescope.clear_look(os.path.join(self.tmp, "none"), self.runner())
        self.assertEqual(self.calls[0][1]["env"]["DISPLAY"], gamescope.FALLBACK_DISPLAY)

    def test_environment_without_display_entry_also_falls_back(self):
        with open(self.env_file, "w") as handle:
            handle.write("FOO=bar\n")
        with unittest.mock.patch.dict(os.environ, {"DISPLAY": ":3"}):
            gamescope.clear_look(self.env_file, self.runner())
        self.assertEqual(self.calls[0][1]["env"]["DISPLAY"], ":3")

    def test_failure_with_a_guessed_display_reports_it_cannot_reach_gamescope(self):
        with self.assertRaises(gamescope.GamescopeError) as raised:
            gamescope.clear_look(os.path.join(self.tmp, "none"), self.runner(returncode=1))
        self.assertEqual(raised.exception.code, "env_missing")

    def test_output_is_not_translated(self):
        gamescope.clear_look(self.env_file, self.runner())
        self.assertEqual(self.calls[0][1]["env"]["LC_ALL"], "C")

    def test_missing_xprop_tool(self):
        with self.assertRaises(gamescope.GamescopeError) as raised:
            gamescope.clear_look(self.env_file, self.runner(error=FileNotFoundError()))
        self.assertIn("xprop", str(raised.exception))
        self.assertEqual(raised.exception.code, "xprop_missing")

    def test_failed_command(self):
        with self.assertRaises(gamescope.GamescopeError) as raised:
            gamescope.clear_look(self.env_file, self.runner(returncode=1))
        self.assertEqual(raised.exception.info(), {"code": "xprop_failed", "detail": "boom"})

    def test_timeout(self):
        with self.assertRaises(gamescope.GamescopeError):
            gamescope.clear_look(self.env_file, self.runner(error=subprocess.TimeoutExpired("xprop", 10)))


if __name__ == "__main__":
    unittest.main()
