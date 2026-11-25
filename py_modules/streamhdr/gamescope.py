"""Talks to gamescope's X server to set or clear the HDR "look" LUT atom."""
from __future__ import annotations

import os
import re
import subprocess
from typing import Callable, Dict, Optional

from .errors import CodedError

ATOM = "GAMESCOPE_COLOR_LOOK_PQ"
ENVIRONMENT_FILE = "gamescope-environment"
# When nothing tells us where gamescope's X server is, use the display that gamescope sessions
# normally give it (other plugins that talk to gamescope rely on the same value).
FALLBACK_DISPLAY = ":1"


class GamescopeError(CodedError):
    """A problem the user can act on."""


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
        raise GamescopeError("env_missing", "gamescope's environment file was not found. Is gamescope running?")
    if "DISPLAY" not in env:
        raise GamescopeError("env_missing", "gamescope's environment file has no DISPLAY entry.")
    return env


def resolve_environment(path: str) -> "tuple[Dict[str, str], bool]":
    """Variables for reaching gamescope's X server, and whether they are only a best guess.

    The environment file that gamescope sessions write is preferred. Not every setup has it, so
    otherwise the DISPLAY we already have is used, and as a last resort the usual display.
    """
    try:
        return read_environment(path), False
    except GamescopeError:
        return {"DISPLAY": os.environ.get("DISPLAY") or FALLBACK_DISPLAY}, True


Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def _run_xprop(args: list, env_file: str, run: Runner) -> str:
    variables, guessed = resolve_environment(env_file)
    env = dict(os.environ)
    env.update(variables)
    env["LC_ALL"] = "C"  # xprop's output is parsed, so it must not be translated
    try:
        result = run(["xprop", "-root"] + args, env=env, capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        raise GamescopeError("xprop_missing", "The xprop tool is not installed, so saturation cannot be applied.")
    except subprocess.TimeoutExpired:
        raise GamescopeError("xprop_timeout", "xprop timed out while talking to gamescope.")
    if result.returncode != 0:
        detail = (result.stderr or "").strip()
        if guessed:
            # We could not find gamescope's display and the guess did not work either.
            raise GamescopeError("env_missing", "Could not reach gamescope's display (%s): %s" % (variables["DISPLAY"], detail), detail or None)
        raise GamescopeError("xprop_failed", "xprop failed: %s" % detail, detail or None)
    return result.stdout or ""


def set_look(lut_path: str, env_file: str, run: Runner = subprocess.run) -> None:
    _run_xprop(["-f", ATOM, "8s", "-set", ATOM, lut_path], env_file, run)


def clear_look(env_file: str, run: Runner = subprocess.run) -> None:
    _run_xprop(["-remove", ATOM], env_file, run)


def get_look(env_file: str, run: Runner = subprocess.run) -> Optional[str]:
    """Return the LUT path currently set on the atom, or None when it is not set."""
    output = _run_xprop([ATOM], env_file, run)
    match = re.search(r'=\s*"(.*)"', output)
    return match.group(1) if match else None
