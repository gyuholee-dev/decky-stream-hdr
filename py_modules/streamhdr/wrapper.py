"""Installs, checks and removes the streaming_client wrapper script.

Steam restores a pristine streaming_client binary every time it starts or updates,
so every function here is idempotent and safe to call repeatedly.
"""
from __future__ import annotations

import filecmp
import os
import shutil
from typing import Optional, Tuple

from .paths import Paths

MARKER = "# streamhdr-wrapper v1"
ELF_MAGIC = b"\x7fELF"

Owner = Optional[Tuple[int, int]]


class WrapperError(Exception):
    """A problem the user can act on; the message is shown as-is."""


def _head(path: str, size: int = 512) -> bytes:
    with open(path, "rb") as handle:
        return handle.read(size)


def is_wrapper(path: str) -> bool:
    """True when `path` is a script installed by this plugin."""
    try:
        head = _head(path)
    except OSError:
        return False
    return head.startswith(b"#!") and MARKER.encode() in head


def is_elf(path: str) -> bool:
    try:
        return _head(path, 4) == ELF_MAGIC
    except OSError:
        return False


def render_wrapper(template_text: str, paths: Paths) -> str:
    return template_text.replace("__SHIM__", paths.shim).replace("__FLAG__", paths.flag)


def _owner_of(path: str) -> Owner:
    """Ownership to apply to created files, only needed when running as root."""
    if os.geteuid() != 0:
        return None
    stat = os.stat(path)
    return stat.st_uid, stat.st_gid


def _chown(path: str, owner: Owner) -> None:
    if owner is not None:
        os.chown(path, owner[0], owner[1])


def _ensure_dir(path: str, owner: Owner) -> None:
    missing = []
    current = path
    while not os.path.isdir(current):
        missing.append(current)
        current = os.path.dirname(current)
    os.makedirs(path, exist_ok=True)
    for created in missing:
        _chown(created, owner)


def _atomic_write(path: str, data: str, mode: int, owner: Owner) -> None:
    tmp = path + ".streamhdr-tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(data)
    os.chmod(tmp, mode)
    _chown(tmp, owner)
    os.replace(tmp, path)


def _install_shim(paths: Paths, owner: Owner) -> None:
    if not os.path.isfile(paths.shim_src):
        raise WrapperError("The bundled injection library is missing from the plugin package.")
    _ensure_dir(paths.data_dir, owner)
    if os.path.isfile(paths.shim) and filecmp.cmp(paths.shim_src, paths.shim, shallow=False):
        return
    tmp = paths.shim + ".streamhdr-tmp"
    shutil.copyfile(paths.shim_src, tmp)
    os.chmod(tmp, 0o755)
    _chown(tmp, owner)
    os.replace(tmp, paths.shim)


def _keep_original(paths: Paths) -> None:
    tmp = paths.real + ".streamhdr-tmp"
    if os.path.lexists(tmp):
        os.remove(tmp)
    try:
        os.link(paths.client, tmp)
    except OSError:
        shutil.copy2(paths.client, tmp)  # file systems without hard links
    os.replace(tmp, paths.real)


def needs_attention(paths: Paths) -> bool:
    """Cheap check for the periodic maintenance: has anything the wrapper relies on gone missing?"""
    return not (
        is_wrapper(paths.client)
        and os.path.isfile(paths.real)
        and os.path.isfile(paths.shim)
        and os.path.isfile(paths.flag)
    )


def install(paths: Paths) -> str:
    """Make sure the wrapper is in place. Returns what was done: 'installed', 'updated' or 'ok'."""
    if not os.path.isfile(paths.client):
        raise WrapperError("Steam's streaming client was not found. Start Steam once and try again.")
    owner = _owner_of(os.path.dirname(paths.client))
    _install_shim(paths, owner)

    with open(paths.template, "r", encoding="utf-8") as handle:
        wanted = render_wrapper(handle.read(), paths)

    if is_wrapper(paths.client):
        if not os.path.isfile(paths.real):
            raise WrapperError(
                "The wrapper is installed but the original streaming client copy is missing. "
                "Restart Steam to restore the original, then reload the plugin."
            )
        with open(paths.client, "r", encoding="utf-8") as handle:
            if handle.read() == wanted:
                return "ok"
        _atomic_write(paths.client, wanted, 0o755, owner)
        return "updated"

    if not is_elf(paths.client):
        raise WrapperError("Steam's streaming client has an unexpected format; leaving it untouched.")

    # The original binary is back (first run, Steam restart, or a Steam update).
    # Keep it as streaming_client.real through a hard link and then swap the script in with a
    # single rename, so the client path never disappears while a stream could be starting.
    _keep_original(paths)
    _atomic_write(paths.client, wanted, 0o755, owner)
    return "installed"


def restore(paths: Paths) -> bool:
    """Put the original streaming client back. Returns True when something changed."""
    if is_wrapper(paths.client) and os.path.isfile(paths.real):
        os.replace(paths.real, paths.client)
        return True
    if is_elf(paths.client) and os.path.isfile(paths.real):
        # Steam already restored the original; the saved copy is stale.
        os.remove(paths.real)
        return True
    return False


def set_enabled(paths: Paths, enabled: bool) -> None:
    if enabled:
        owner = _owner_of(os.path.dirname(paths.client)) if os.path.isdir(os.path.dirname(paths.client)) else None
        _ensure_dir(paths.data_dir, owner)
        with open(paths.flag, "w", encoding="utf-8") as handle:
            handle.write("1\n")
        _chown(paths.flag, owner)
    elif os.path.exists(paths.flag):
        os.remove(paths.flag)


def is_enabled(paths: Paths) -> bool:
    return os.path.isfile(paths.flag)


def uninstall(paths: Paths) -> None:
    """Remove everything this module created."""
    restore(paths)
    for path in (paths.flag, paths.shim):
        if os.path.exists(path):
            os.remove(path)


def status(paths: Paths) -> dict:
    return {
        "client_found": os.path.isfile(paths.client),
        "wrapped": is_wrapper(paths.client),
        "original_saved": os.path.isfile(paths.real),
        "shim_installed": os.path.isfile(paths.shim),
        "enabled": is_enabled(paths),
    }
