import asyncio
import os
import shutil
import tempfile
import unittest

from streamhdr import watcher


def make_proc(root, pid, argv):
    os.makedirs(os.path.join(root, str(pid)))
    with open(os.path.join(root, str(pid), "cmdline"), "wb") as handle:
        handle.write(b"\0".join(part.encode() for part in argv) + b"\0")


class IsStreamingTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_no_processes(self):
        self.assertFalse(watcher.is_streaming(self.root))

    def test_unrelated_processes(self):
        make_proc(self.root, 10, ["/usr/bin/steam", "-gamepadui"])
        make_proc(self.root, 11, ["/bin/sh", "-c", "streaming_client.real in args only"])
        self.assertFalse(watcher.is_streaming(self.root))

    def test_original_binary_name(self):
        make_proc(self.root, 20, ["/home/u/.local/share/Steam/steamrt64/streaming_client", "--vulkan"])
        self.assertTrue(watcher.is_streaming(self.root))

    def test_wrapped_binary_name(self):
        make_proc(self.root, 21, ["/home/u/.local/share/Steam/steamrt64/streaming_client.real", "--vulkan"])
        self.assertTrue(watcher.is_streaming(self.root))

    def test_ignores_non_process_entries_and_missing_root(self):
        os.makedirs(os.path.join(self.root, "self"))
        self.assertFalse(watcher.is_streaming(self.root))
        self.assertFalse(watcher.is_streaming(os.path.join(self.root, "missing")))


class StreamWatcherTests(unittest.IsolatedAsyncioTestCase):
    async def test_reports_only_changes(self):
        states = iter([False, False, True, True, False])
        seen = []

        async def on_change(value):
            seen.append(value)

        stream_watcher = watcher.StreamWatcher(on_change, probe=lambda: next(states))
        for _ in range(5):
            await stream_watcher.poll_once()
        self.assertEqual(seen, [False, True, False])

    async def test_run_survives_probe_errors_and_can_be_cancelled(self):
        calls = []

        def probe():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("boom")
            return True

        seen = []

        async def on_change(value):
            seen.append(value)

        task = asyncio.create_task(watcher.StreamWatcher(on_change, interval=0.01, probe=probe).run())
        await asyncio.sleep(0.15)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(seen, [True])


if __name__ == "__main__":
    unittest.main()
