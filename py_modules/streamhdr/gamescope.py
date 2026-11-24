"""Talks to gamescope's X server to set or clear the HDR "look" LUT atom."""
from __future__ import annotations

import os
import subprocess
from typing import Callable, Dict, Optional

ATOM = "GAMESCOPE_COLOR_LOOK_PQ"
ENVIRONMENT_FILE = "gamescope-environment"


class GamescopeError(Exception):
    """A problem the user can act on; the message is shown as-is."""


def environment_file_for(uid: int, runtime_dir: Optional[str] = None) -> str:
    return os.path.join(runtime_dir or "/run/user/%d" % uid, ENVIRONMENT_FILE)


def parse_environment(text: str) -> Dict[str, str]:
    """Parse the KEY=VALUE lines of gamescope's environment file (it is sourced by a shell)."""
    result: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, separator, value = line.partition("=")
        if not separator or not key.isidentifier():
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        result[key] = value
    return result


def read_environment(path: str) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            env = parse_environment(handle.read())
    except OSError:
        raise GamescopeError("gamescope's environment file was not found. Is gamescope running?")
    if "DISPLAY" not in env:
        raise GamescopeError("gamescope's environment file has no DISPLAY entry.")
    return env


Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def _run_xprop(args: list, env_file: str, run: Runner) -> None:
    env = dict(os.environ)
    env.update(read_environment(env_file))
    try:
        result = run(["xprop", "-root"] + args, env=env, capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        raise GamescopeError("The xprop tool is not installed, so saturation cannot be applied.")
    except subprocess.TimeoutExpired:
        raise GamescopeError("xprop timed out while talking to gamescope.")
    if result.returncode != 0:
        raise GamescopeError("xprop failed: %s" % (result.stderr or "").strip())


def set_look(lut_path: str, env_file: str, run: Runner = subprocess.run) -> None:
    _run_xprop(["-f", ATOM, "8s", "-set", ATOM, lut_path], env_file, run)


def clear_look(env_file: str, run: Runner = subprocess.run) -> None:
    _run_xprop(["-remove", ATOM], env_file, run)
