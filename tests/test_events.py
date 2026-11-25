import asyncio
import os
import shutil
import struct
import tempfile
import unittest

from streamhdr import events
from streamhdr.events import ANY_CHANGE, IN_CLOSE_WRITE, IN_CREATE, IN_DELETE, WRITTEN, Events, FileEvent
from streamhdr.paths import Paths


def make_proc(root, pid, argv):
    os.makedirs(os.path.join(root, str(pid)), exist_ok=True)
    with open(os.path.join(root, str(pid), "cmdline"), "wb") as handle:
        handle.write(b"\0".join(part.encode() for part in argv) + b"\0")


class ParseTests(unittest.TestCase):
    def test_parse_events_reads_every_record(self):
        def record(wd, mask, name):
            padded = name.encode() + b"\0"
            padded += b"\0" * (-len(padded) % 8)
            return struct.pack("iIII", wd, mask, 0, len(padded)) + padded

        data = record(1, IN_CLOSE_WRITE, "stream_event") + record(2, IN_DELETE, "enabled")
        self.assertEqual(events.parse_events(data), [(1, IN_CLOSE_WRITE, "stream_event"), (2, IN_DELETE, "enabled")])

    def test_parse_events_ignores_a_truncated_tail(self):
        self.assertEqual(events.parse_events(b"\x01\x00"), [])

    def test_parse_start_event(self):
        self.assertEqual(events.parse_start_event("start 1234\n"), 1234)
        self.assertIsNone(events.parse_start_event("start abc"))
        self.assertIsNone(events.parse_start_event("stop 12"))
        self.assertIsNone(events.parse_start_event(""))
        self.assertIsNone(events.parse_start_event("start 12 34"))


STEAM_CLIENT = "/h/.local/share/Steam/steamrt64/steam"


class FindTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_no_processes(self):
        self.assertIsNone(events.find_streaming_pid(self.root))

    def test_unrelated_processes(self):
        make_proc(self.root, 10, ["/usr/bin/steam", "-gamepadui"])
        make_proc(self.root, 11, ["/bin/sh", "-c", "streaming_client.real in args only"])
        self.assertIsNone(events.find_streaming_pid(self.root))

    def test_original_and_wrapped_names(self):
        make_proc(self.root, 20, ["/x/steamrt64/streaming_client", "--vulkan"])
        self.assertEqual(events.find_streaming_pid(self.root), 20)
        shutil.rmtree(os.path.join(self.root, "20"))
        make_proc(self.root, 21, ["/x/steamrt64/streaming_client.real", "--vulkan"])
        self.assertEqual(events.find_streaming_pid(self.root), 21)

    def test_ignores_non_process_entries_and_missing_root(self):
        os.makedirs(os.path.join(self.root, "self"))
        self.assertIsNone(events.find_streaming_pid(self.root))
        self.assertIsNone(events.find_streaming_pid(os.path.join(self.root, "missing")))


class FakeInotify:
    """Stands in for inotify, which only exists on Linux. `fire` plays an event."""

    def __init__(self, loop, callback):
        self.callback = callback
        self.watches = {}
        self.closed = False
        FakeInotify.last = self

    def watch(self, directory, mask):
        if not os.path.isdir(directory):
            return False
        self.watches[directory] = mask
        return True

    def fire(self, directory, name, mask):
        self.callback(FileEvent(directory, name, mask))

    def close(self):
        self.closed = True


class EventsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        home = os.path.join(self.tmp, "home")
        self.paths = Paths.for_user(home, os.path.join(self.tmp, "plugin"))
        os.makedirs(os.path.dirname(self.paths.client))
        self.proc = os.path.join(self.tmp, "proc")
        os.makedirs(self.proc)
        self.streaming = []
        self.files_changed = []
        self.steam_exits = []
        self.pipes = {}  # pid -> (read fd, write fd): the read end plays the pidfd, writing to it plays the exit
        self.addCleanup(self.close_pipes)
        self.loop = asyncio.get_running_loop()

    def pidfd_open(self, pid):
        if pid not in self.pipes:
            self.pipes[pid] = os.pipe()
        return os.dup(self.pipes[pid][0])  # Events closes its copy; the test keeps the original

    def close_pipes(self):
        for read_end, write_end in self.pipes.values():
            os.close(read_end)
            os.close(write_end)

    def end_process(self, pid):
        os.write(self.pipes[pid][1], b"x")
        shutil.rmtree(os.path.join(self.proc, str(pid)), ignore_errors=True)  # an ended process has no /proc entry

    def make_events(self, debounce=0.02):
        self.events = Events(
            self.paths,
            self.loop,
            on_streaming=self.streaming.append,
            on_files_changed=lambda: self.files_changed.append(1),
            on_steam_exit=lambda: self.steam_exits.append(1),
            inotify_factory=FakeInotify,
            pidfd_open=self.pidfd_open,
            proc_root=self.proc,
            debounce=debounce,
        )
        self.addCleanup(self.events.stop)
        return self.events

    def write_event(self, text):
        with open(self.paths.stream_event, "w") as handle:
            handle.write(text)
        FakeInotify.last.fire(self.paths.data_dir, "stream_event", IN_CLOSE_WRITE)

    async def settle(self, seconds=0.1):
        await asyncio.sleep(seconds)

    async def test_start_watches_both_folders_and_stays_quiet_without_a_stream(self):
        self.make_events().start()
        self.assertEqual(
            set(FakeInotify.last.watches),
            {self.paths.data_dir, os.path.dirname(self.paths.client)},
        )
        self.assertEqual(self.streaming, [])

    async def test_a_stream_that_is_already_running_is_found_once(self):
        make_proc(self.proc, 300, ["/x/streaming_client.real"])
        self.make_events().start()
        self.assertEqual(self.streaming, [True])

    async def test_start_event_then_exit(self):
        make_proc(self.proc, 400, ["/x/streaming_client.real"])
        self.make_events().start()
        self.write_event("start 400\n")
        self.assertEqual(self.streaming, [True])
        self.end_process(400)
        await self.settle()
        self.assertEqual(self.streaming, [True, False])

    async def test_an_event_for_another_process_is_ignored(self):
        make_proc(self.proc, 500, ["/usr/bin/steam"])
        self.make_events().start()
        self.write_event("start 500\n")
        self.write_event("start nonsense\n")
        self.write_event("start 99999\n")  # no such process
        self.assertEqual(self.streaming, [])

    async def test_a_new_client_replaces_the_old_one_without_a_gap(self):
        make_proc(self.proc, 600, ["/x/streaming_client.real"])
        make_proc(self.proc, 601, ["/x/streaming_client.real"])
        self.make_events().start()
        self.write_event("start 600\n")
        self.write_event("start 601\n")
        self.end_process(600)  # the old one ending must not end the stream
        await self.settle()
        self.assertEqual(self.streaming, [True])
        self.end_process(601)
        await self.settle()
        self.assertEqual(self.streaming, [True, False])

    async def test_file_events_for_the_wrapper_are_merged_into_one_call(self):
        make_proc(self.proc, 800, [STEAM_CLIENT])
        self.make_events().start()
        client_dir = os.path.dirname(self.paths.client)
        for name in ("streaming_client", "streaming_client.real", "streaming_client"):
            FakeInotify.last.fire(client_dir, name, IN_CREATE)
        FakeInotify.last.fire(self.paths.data_dir, "enabled", IN_DELETE)
        self.assertEqual(self.files_changed, [])
        await self.settle()
        self.assertEqual(self.files_changed, [1])

    async def test_a_new_event_starts_the_quiet_period_again(self):
        make_proc(self.proc, 800, [STEAM_CLIENT])
        self.make_events(debounce=0.15).start()
        client_dir = os.path.dirname(self.paths.client)
        FakeInotify.last.fire(client_dir, "streaming_client", IN_CREATE)
        await asyncio.sleep(0.1)
        FakeInotify.last.fire(client_dir, "streaming_client", IN_CREATE)
        await asyncio.sleep(0.1)
        self.assertEqual(self.files_changed, [])  # 0.2 s after the first event, but only 0.1 s after the last
        await asyncio.sleep(0.15)
        self.assertEqual(self.files_changed, [1])

    async def test_a_requested_check_waits_for_the_quiet_period(self):
        make_proc(self.proc, 800, [STEAM_CLIENT])
        self.make_events(debounce=0.05).start()
        self.events.request_check()
        self.assertEqual(self.files_changed, [])
        await asyncio.sleep(0.15)
        self.assertEqual(self.files_changed, [1])

    async def test_the_check_comes_again_while_steam_is_not_running(self):
        self.make_events(debounce=0.03).start()
        self.events.request_check()
        await asyncio.sleep(0.12)
        self.assertGreaterEqual(len(self.files_changed), 2)
        self.assertFalse(self.events.steam_running())

    async def test_the_check_stops_repeating_once_steam_is_up(self):
        self.make_events(debounce=0.03).start()
        self.events.request_check()
        await asyncio.sleep(0.05)
        make_proc(self.proc, 801, [STEAM_CLIENT])
        await asyncio.sleep(0.06)  # the next check finds Steam
        self.assertTrue(self.events.steam_running())
        count = len(self.files_changed)
        await asyncio.sleep(0.12)
        self.assertEqual(len(self.files_changed), count)

    async def test_a_steam_exit_is_reported(self):
        make_proc(self.proc, 802, [STEAM_CLIENT, "-gamepadui"])
        self.make_events().start()
        self.assertTrue(self.events.steam_running())
        self.end_process(802)
        await self.settle()
        self.assertEqual(self.steam_exits, [1])
        self.assertFalse(self.events.steam_running())

    async def test_only_the_steam_client_counts_as_steam(self):
        make_proc(self.proc, 803, ["/usr/bin/steam"])
        make_proc(self.proc, 804, ["/h/.local/share/Steam/steamrt64/steamwebhelper", "--type=zygote"])
        make_proc(self.proc, 805, ["/bin/sh", "-c", "steamrt64/steam"])
        self.make_events().start()
        self.assertFalse(self.events.steam_running())

    async def test_a_steam_started_later_is_found_at_the_next_check(self):
        make_proc(self.proc, 806, [STEAM_CLIENT])
        self.make_events(debounce=0.03).start()
        self.end_process(806)
        await self.settle()
        self.assertEqual(self.steam_exits, [1])
        make_proc(self.proc, 807, [STEAM_CLIENT])  # Steam restarted
        self.events.request_check()
        await asyncio.sleep(0.08)
        self.end_process(807)
        await self.settle()
        self.assertEqual(self.steam_exits, [1, 1])

    async def test_unrelated_files_are_ignored(self):
        self.make_events().start()
        FakeInotify.last.fire(os.path.dirname(self.paths.client), "steamwebhelper", IN_CREATE)
        FakeInotify.last.fire(self.paths.data_dir, "paper_white", IN_CLOSE_WRITE)
        await self.settle()
        self.assertEqual(self.files_changed, [])

    async def test_a_missing_steam_folder_is_not_fatal(self):
        shutil.rmtree(os.path.dirname(self.paths.client))
        self.make_events().start()
        self.assertEqual(set(FakeInotify.last.watches), {self.paths.data_dir})

    async def test_stop_closes_everything(self):
        make_proc(self.proc, 700, ["/x/streaming_client.real"])
        self.make_events().start()
        self.write_event("start 700\n")
        self.events.stop()
        self.assertTrue(FakeInotify.last.closed)


if __name__ == "__main__":
    unittest.main()
