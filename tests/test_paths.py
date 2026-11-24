import os
import shutil
import tempfile
import unittest

from streamhdr import paths


class StreamingClientLocationTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)

    def make_client(self, *relative):
        folder = os.path.join(self.home, *relative, "steamrt64")
        os.makedirs(folder)
        path = os.path.join(folder, "streaming_client")
        with open(path, "wb") as handle:
            handle.write(b"\x7fELF")
        return path

    def test_usual_place_is_preferred(self):
        usual = self.make_client(".local", "share", "Steam")
        self.make_client(".steam", "steam")
        self.assertEqual(paths.find_streaming_client(self.home), usual)

    def test_other_places_are_tried(self):
        other = self.make_client(".steam", "steam")
        self.assertEqual(paths.find_streaming_client(self.home), other)

    def test_when_nothing_exists_the_usual_place_is_returned(self):
        expected = os.path.join(self.home, ".local", "share", "Steam", "steamrt64", "streaming_client")
        self.assertEqual(paths.find_streaming_client(self.home), expected)

    def test_paths_use_the_found_client(self):
        other = self.make_client(".steam", "root")
        result = paths.Paths.for_user(self.home, "/plugin", 1000)
        self.assertEqual(result.client, other)
        self.assertEqual(result.real, other + ".real")


if __name__ == "__main__":
    unittest.main()
